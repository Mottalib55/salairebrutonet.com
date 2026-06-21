#!/usr/bin/env python3
"""Génère admin/index.html – Dashboard SEO privé."""
import os, re, json

BASE = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "salairebrutonet.com"
SITE_NAME = "SalaireBrutNet"
PASSWORD = "sofia"

# ── Collecter les données SEO ───────────────────────────────────────────────
pages = []
for root, dirs, files in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in ('node_modules','__pycache__','.git','admin')]
    for f in files:
        if f == 'index.html':
            path = os.path.join(root, f)
            rel = os.path.relpath(root, BASE)
            url_path = '/' if rel == '.' else '/' + rel + '/'
            with open(path, 'r', encoding='utf-8') as fh:
                html = fh.read()
            tm = re.search(r'<title>(.*?)</title>', html)
            title = tm.group(1) if tm else ''
            dm = re.search(r'<meta name="description" content="(.*?)"', html)
            desc = dm.group(1) if dm else ''
            if 'brut-en-net' in url_path:
                cat = 'brut-net'
            elif 'net-en-brut' in url_path:
                cat = 'net-brut'
            else:
                cat = 'special'
            pages.append({'path': url_path, 'title': title, 'desc': desc, 'cat': cat})

pages.sort(key=lambda p: p['path'])

# Stats
total = len(pages)
n_brut = sum(1 for p in pages if p['cat'] == 'brut-net')
n_net = sum(1 for p in pages if p['cat'] == 'net-brut')
n_special = sum(1 for p in pages if p['cat'] == 'special')

# JS data
js_lines = []
for p in pages:
    t = p['title'].replace("\\","\\\\").replace("'","\\'")
    d = p['desc'].replace("\\","\\\\").replace("'","\\'")
    js_lines.append(f"  {{path:'{p['path']}',title:'{t}',desc:'{d}',cat:'{p['cat']}'}}")
js_data = "const seoPages = [\n" + ",\n".join(js_lines) + "\n];"

# ── HTML ─────────────────────────────────────────────────────────────────────
html_out = f'''<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<meta name="googlebot" content="noindex, nofollow">
<title>Admin Dashboard – {SITE_NAME}</title>
<link rel="icon" type="image/svg+xml" href="/img/logo.svg">
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://code.iconify.design/iconify-icon/1.0.7/iconify-icon.min.js"></script>
<style>
body {{ font-family: 'Inter', system-ui, -apple-system, sans-serif; }}
.card {{ transition: all 0.2s; }}
.card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 40px rgba(0,0,0,0.15); }}
.ring-highlight {{ animation: pulseRing 2s ease-out; }}
@keyframes pulseRing {{ 0% {{ box-shadow: 0 0 0 4px rgba(99,102,241,0.6); }} 100% {{ box-shadow: 0 0 0 0 rgba(99,102,241,0); }} }}
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: #1e293b; }}
::-webkit-scrollbar-thumb {{ background: #475569; border-radius: 3px; }}
</style>
</head>
<body class="bg-slate-900 text-slate-300 antialiased min-h-screen">

<!-- ═══ LOCK SCREEN ═══ -->
<div id="lockscreen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900">
  <div class="text-center p-8">
    <div class="mx-auto mb-6 w-16 h-16 rounded-2xl bg-indigo-600 flex items-center justify-center">
      <span class="text-white text-2xl font-bold">BN</span>
    </div>
    <h1 class="text-2xl font-bold text-white mb-2">Admin Dashboard</h1>
    <p class="text-slate-400 mb-6">Entrez le code d&rsquo;acc&egrave;s</p>
    <input id="passInput" type="password" placeholder="Code d'acc&egrave;s"
      class="w-64 px-4 py-3 rounded-xl bg-slate-800 border border-slate-600 text-white text-center focus:border-indigo-500 focus:outline-none mb-3"
      onkeydown="if(event.key==='Enter')checkAccess()">
    <br>
    <button onclick="checkAccess()" class="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium transition-colors">Acc&eacute;der</button>
    <p id="passError" class="text-red-400 text-sm mt-3 hidden">Code incorrect</p>
  </div>
</div>

<!-- ═══ HEADER ═══ -->
<header class="bg-slate-800 border-b border-slate-700 sticky top-0 z-40">
  <div class="mx-auto max-w-7xl flex items-center justify-between px-4 sm:px-6 lg:px-8 h-16">
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center">
        <span class="text-white text-sm font-bold">BN</span>
      </div>
      <div>
        <span class="text-white font-semibold">{SITE_NAME}</span>
        <span class="text-slate-500 text-sm ml-2">Dashboard priv&eacute;</span>
      </div>
    </div>
    <a href="/" target="_blank" class="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors">
      Voir le site <iconify-icon icon="lucide:external-link" width="16"></iconify-icon>
    </a>
  </div>
</header>

<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 space-y-8">

  <!-- ═══ QUICK STATS ═══ -->
  <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
    <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
      <p class="text-slate-400 text-sm">Total Pages</p>
      <p class="text-2xl font-bold text-white">{total}</p>
    </div>
    <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
      <p class="text-slate-400 text-sm">Brut &rarr; Net</p>
      <p class="text-2xl font-bold text-emerald-400">{n_brut}</p>
    </div>
    <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
      <p class="text-slate-400 text-sm">Net &rarr; Brut</p>
      <p class="text-2xl font-bold text-purple-400">{n_net}</p>
    </div>
    <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
      <p class="text-slate-400 text-sm">Pages sp&eacute;ciales</p>
      <p class="text-2xl font-bold text-amber-400">{n_special}</p>
    </div>
    <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
      <p class="text-slate-400 text-sm">SEO OK</p>
      <p class="text-2xl font-bold text-emerald-400" id="statOk">–</p>
    </div>
  </div>

  <!-- ═══ LIENS RAPIDES ═══ -->
  <div>
    <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
      <iconify-icon icon="lucide:link" width="20" class="text-indigo-400"></iconify-icon> Liens Rapides
    </h2>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <a href="https://analytics.google.com/" target="_blank" class="card bg-slate-800 rounded-xl p-4 border border-slate-700 hover:border-indigo-500 group">
        <div class="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center mb-3">
          <iconify-icon icon="logos:google-analytics" width="22"></iconify-icon>
        </div>
        <p class="text-white font-medium">Google Analytics</p>
        <p class="text-slate-500 text-sm">Trafic &amp; audiences</p>
      </a>
      <a href="https://search.google.com/search-console?resource_id=https://{DOMAIN}/" target="_blank" class="card bg-slate-800 rounded-xl p-4 border border-slate-700 hover:border-indigo-500 group">
        <div class="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center mb-3">
          <iconify-icon icon="logos:google-icon" width="22"></iconify-icon>
        </div>
        <p class="text-white font-medium">Search Console</p>
        <p class="text-slate-500 text-sm">Indexation &amp; requ&ecirc;tes</p>
      </a>
      <a href="https://github.com/motta/simulateur" target="_blank" class="card bg-slate-800 rounded-xl p-4 border border-slate-700 hover:border-indigo-500 group">
        <div class="w-10 h-10 rounded-lg bg-slate-500/20 flex items-center justify-center mb-3">
          <iconify-icon icon="mdi:github" width="24" class="text-white"></iconify-icon>
        </div>
        <p class="text-white font-medium">GitHub Repo</p>
        <p class="text-slate-500 text-sm">Code source</p>
      </a>
      <a href="https://pagespeed.web.dev/analysis?url=https://{DOMAIN}/" target="_blank" class="card bg-slate-800 rounded-xl p-4 border border-slate-700 hover:border-indigo-500 group">
        <div class="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center mb-3">
          <iconify-icon icon="lucide:zap" width="22" class="text-green-400"></iconify-icon>
        </div>
        <p class="text-white font-medium">PageSpeed</p>
        <p class="text-slate-500 text-sm">Performance</p>
      </a>
    </div>
  </div>

  <!-- ═══ SEO DASHBOARD ═══ -->
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
      <div>
        <h2 class="text-lg font-semibold text-white flex items-center gap-2">
          <iconify-icon icon="lucide:search-check" width="20" class="text-indigo-400"></iconify-icon> SEO Snippet Dashboard
        </h2>
        <p id="seoSummaryText" class="text-sm text-slate-400 mt-1">Chargement...</p>
      </div>
      <!-- Category Switcher -->
      <div class="flex bg-slate-800 p-1 rounded-xl border border-slate-700">
        <button onclick="switchCat('all')" id="pill-all" class="px-4 py-2 rounded-lg text-sm font-medium transition-colors bg-indigo-600 text-white">Toutes</button>
        <button onclick="switchCat('brut-net')" id="pill-brut-net" class="px-4 py-2 rounded-lg text-sm font-medium transition-colors text-slate-400 hover:text-white">Brut&rarr;Net</button>
        <button onclick="switchCat('net-brut')" id="pill-net-brut" class="px-4 py-2 rounded-lg text-sm font-medium transition-colors text-slate-400 hover:text-white">Net&rarr;Brut</button>
        <button onclick="switchCat('special')" id="pill-special" class="px-4 py-2 rounded-lg text-sm font-medium transition-colors text-slate-400 hover:text-white">Sp&eacute;ciales</button>
      </div>
    </div>

    <!-- SEO Quick Tools -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
      <a href="https://www.google.com/search?q=site:{DOMAIN}" target="_blank" class="flex items-center gap-2 text-sm text-slate-400 hover:text-indigo-400 bg-slate-800/50 rounded-lg px-3 py-2 border border-slate-700/50">
        <iconify-icon icon="lucide:search" width="14"></iconify-icon> Pages index&eacute;es
      </a>
      <a href="https://search.google.com/test/rich-results?url=https://{DOMAIN}/" target="_blank" class="flex items-center gap-2 text-sm text-slate-400 hover:text-indigo-400 bg-slate-800/50 rounded-lg px-3 py-2 border border-slate-700/50">
        <iconify-icon icon="lucide:sparkles" width="14"></iconify-icon> Rich Results
      </a>
      <a href="https://pagespeed.web.dev/analysis?url=https://{DOMAIN}/" target="_blank" class="flex items-center gap-2 text-sm text-slate-400 hover:text-indigo-400 bg-slate-800/50 rounded-lg px-3 py-2 border border-slate-700/50">
        <iconify-icon icon="lucide:gauge" width="14"></iconify-icon> PageSpeed
      </a>
      <a href="https://validator.w3.org/nu/?doc=https://{DOMAIN}/" target="_blank" class="flex items-center gap-2 text-sm text-slate-400 hover:text-indigo-400 bg-slate-800/50 rounded-lg px-3 py-2 border border-slate-700/50">
        <iconify-icon icon="lucide:file-check" width="14"></iconify-icon> HTML Validator
      </a>
    </div>
  </div>

  <!-- ═══ SUMMARY TABLE ═══ -->
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-white flex items-center gap-2">
        <iconify-icon icon="lucide:table" width="20" class="text-indigo-400"></iconify-icon> R&eacute;capitulatif toutes pages
      </h2>
      <span id="googleIndexBadge" class="text-xs text-slate-500 bg-slate-800 px-3 py-1 rounded-full border border-slate-700"></span>
    </div>
    <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
      <div class="max-h-[500px] overflow-y-auto">
        <table class="w-full text-sm">
          <thead class="sticky top-0 bg-slate-800 border-b border-slate-700 z-10">
            <tr class="text-slate-400 text-xs uppercase">
              <th class="text-left px-4 py-3 font-medium">Page</th>
              <th class="text-left px-3 py-3 font-medium">Cat.</th>
              <th class="text-left px-3 py-3 font-medium hidden lg:table-cell">URL</th>
              <th class="text-left px-3 py-3 font-medium hidden md:table-cell">Title</th>
              <th class="text-center px-2 py-3 font-medium">T.Len</th>
              <th class="text-center px-2 py-3 font-medium">D.Len</th>
              <th class="text-center px-2 py-3 font-medium">Status</th>
              <th class="text-center px-2 py-3 font-medium">Google</th>
              <th class="text-center px-3 py-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody id="summaryTableBody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ═══ SNIPPET CARDS ═══ -->
  <div>
    <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
      <iconify-icon icon="lucide:file-search" width="20" class="text-indigo-400"></iconify-icon> D&eacute;tail des Snippets
    </h2>
    <div id="snippetCards" class="space-y-4"></div>
  </div>

  <!-- ═══ EXPORT ═══ -->
  <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-lg font-semibold text-white flex items-center gap-2">
          <iconify-icon icon="lucide:download" width="20" class="text-indigo-400"></iconify-icon> Export
        </h2>
        <p id="exportCount" class="text-sm text-slate-400 mt-1">0 modification(s) non export&eacute;e(s)</p>
      </div>
      <button onclick="exportChanges()" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
        <iconify-icon icon="lucide:download" width="16"></iconify-icon> Exporter
      </button>
    </div>
    <div id="exportArea" class="hidden">
      <textarea id="exportJson" class="w-full h-48 bg-slate-900 border border-slate-700 rounded-lg p-4 text-sm text-slate-300 font-mono" readonly></textarea>
      <button onclick="navigator.clipboard.writeText(document.getElementById('exportJson').value)" class="mt-3 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
        <iconify-icon icon="lucide:copy" width="16"></iconify-icon> Copier
      </button>
    </div>
  </div>

  <!-- ═══ NOTES ═══ -->
  <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
    <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
      <iconify-icon icon="lucide:sticky-note" width="20" class="text-indigo-400"></iconify-icon> Notes &amp; Todo
    </h2>
    <textarea id="notesArea" class="w-full h-40 bg-slate-900 border border-slate-700 rounded-lg p-4 text-sm text-slate-300 resize-y focus:border-indigo-500 focus:outline-none"
      placeholder="Vos notes ici..." oninput="localStorage.setItem('sbn_admin_notes',this.value)"></textarea>
    <p class="text-xs text-slate-600 mt-2">Les notes sont sauvegard&eacute;es dans le localStorage de ton navigateur.</p>
  </div>

</div>

<!-- ═══ FOOTER ═══ -->
<footer class="border-t border-slate-800 py-6 text-center text-sm text-slate-600">
  {SITE_NAME} Admin &mdash; Page priv&eacute;e non index&eacute;e
</footer>

<script>
// ── DATA ────────────────────────────────────────────────────────────────────
{js_data}

let googleIndex = {{}};
const googleIndexCheckedAt = "";

let currentCat = 'all';
let seoChanges = JSON.parse(localStorage.getItem('sbn_seoChanges') || '{{}}');
let editingPath = null;
const DOMAIN = '{DOMAIN}';

// ── AUTH ─────────────────────────────────────────────────────────────────────
function isAuthenticated() {{
  try {{
    const a = JSON.parse(localStorage.getItem('sbn_admin_auth'));
    return a && a.granted && a.expiry > Date.now();
  }} catch {{ return false; }}
}}
function checkAccess() {{
  const v = document.getElementById('passInput').value;
  if (v === '{PASSWORD}') {{
    localStorage.setItem('sbn_admin_auth', JSON.stringify({{ granted: true, expiry: Date.now() + 86400000 }}));
    document.getElementById('lockscreen').classList.add('hidden');
  }} else {{
    document.getElementById('passError').classList.remove('hidden');
    document.getElementById('passInput').value = '';
    document.getElementById('passInput').focus();
  }}
}}
if (isAuthenticated()) document.getElementById('lockscreen').classList.add('hidden');

// ── HELPERS ──────────────────────────────────────────────────────────────────
function esc(s) {{ const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}
function getTitle(p) {{ return seoChanges[p.path]?.title ?? p.title; }}
function getDesc(p) {{ return seoChanges[p.path]?.desc ?? p.desc; }}

function lenColor(len, min, max) {{
  if (len >= min && len <= max) return 'text-emerald-400';
  if (len < min - 10 || len > max + 10) return 'text-red-400';
  return 'text-amber-400';
}}

function statusBadge(tLen, dLen) {{
  const ok = tLen >= 50 && tLen <= 60 && dLen >= 150 && dLen <= 160;
  return ok
    ? '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400">OK</span>'
    : '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400">!</span>';
}}

function catLabel(cat) {{
  if (cat === 'brut-net') return 'Brut\\u2192Net';
  if (cat === 'net-brut') return 'Net\\u2192Brut';
  return 'Sp\\u00e9ciale';
}}

function catColor(cat) {{
  if (cat === 'brut-net') return 'text-emerald-400';
  if (cat === 'net-brut') return 'text-purple-400';
  return 'text-amber-400';
}}

function pageName(p) {{
  if (p.path === '/') return 'Accueil';
  return p.path.replace(/^\\//,'').replace(/\\/$/,'').replace(/-/g,' ').replace(/\\b\\w/g, c => c.toUpperCase());
}}

function googleIcon(path) {{
  const st = googleIndex[path];
  if (st === true) return '<div class="w-6 h-6 rounded-full bg-emerald-500/10 flex items-center justify-center"><iconify-icon icon="lucide:check-circle" width="14" class="text-emerald-400"></iconify-icon></div>';
  if (st === false) return '<div class="w-6 h-6 rounded-full bg-red-500/10 flex items-center justify-center"><iconify-icon icon="lucide:x-circle" width="14" class="text-red-400"></iconify-icon></div>';
  return '<div class="w-6 h-6 rounded-full bg-slate-500/10 flex items-center justify-center"><iconify-icon icon="lucide:help-circle" width="14" class="text-slate-500"></iconify-icon></div>';
}}

// ── CATEGORY SWITCHER ────────────────────────────────────────────────────────
function switchCat(cat) {{
  currentCat = cat;
  ['all','brut-net','net-brut','special'].forEach(c => {{
    const el = document.getElementById('pill-' + c);
    if (c === cat) {{
      el.className = 'px-4 py-2 rounded-lg text-sm font-medium transition-colors bg-indigo-600 text-white';
    }} else {{
      el.className = 'px-4 py-2 rounded-lg text-sm font-medium transition-colors text-slate-400 hover:text-white';
    }}
  }});
  renderCards();
}}

// ── SUMMARY TABLE ────────────────────────────────────────────────────────────
function renderSummaryTable() {{
  const tbody = document.getElementById('summaryTableBody');
  let html = '';
  seoPages.forEach((p, i) => {{
    const t = getTitle(p), d = getDesc(p);
    const tl = t.length, dl = d.length;
    const hasChange = seoChanges[p.path];
    html += `<tr class="border-b border-slate-700/50 hover:bg-slate-700/30 ${{hasChange ? 'bg-amber-500/5' : ''}}">
      <td class="px-4 py-2 text-white font-medium text-xs">${{esc(pageName(p))}}</td>
      <td class="px-3 py-2"><span class="text-xs ${{catColor(p.cat)}}">${{catLabel(p.cat)}}</span></td>
      <td class="px-3 py-2 hidden lg:table-cell"><code class="text-xs text-slate-500 truncate max-w-[200px] block">${{esc(p.path)}}</code></td>
      <td class="px-3 py-2 hidden md:table-cell"><span class="text-xs text-slate-400 truncate max-w-[200px] block">${{esc(t)}}</span></td>
      <td class="px-2 py-2 text-center"><span class="text-xs font-mono ${{lenColor(tl,50,60)}}">${{tl}}</span></td>
      <td class="px-2 py-2 text-center"><span class="text-xs font-mono ${{lenColor(dl,150,160)}}">${{dl}}</span></td>
      <td class="px-2 py-2 text-center">${{statusBadge(tl, dl)}}</td>
      <td class="px-2 py-2 text-center">${{googleIcon(p.path)}}</td>
      <td class="px-3 py-2 text-center">
        <div class="flex items-center justify-center gap-1">
          <button onclick="scrollToSnippet('${{p.path}}','${{p.cat}}')" class="w-7 h-7 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 flex items-center justify-center" title="Voir snippet">
            <iconify-icon icon="lucide:hash" width="14" class="text-indigo-400"></iconify-icon>
          </button>
          <a href="https://${{DOMAIN}}${{p.path}}" target="_blank" class="w-7 h-7 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 flex items-center justify-center" title="Ouvrir la page">
            <iconify-icon icon="lucide:external-link" width="14" class="text-emerald-400"></iconify-icon>
          </a>
          <a href="https://www.google.com/search?q=site:${{DOMAIN}}${{p.path}}" target="_blank" class="w-7 h-7 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 flex items-center justify-center" title="V\\u00e9rifier Google">
            <iconify-icon icon="lucide:search" width="14" class="text-amber-400"></iconify-icon>
          </a>
        </div>
      </td>
    </tr>`;
  }});
  tbody.innerHTML = html;
}}

// ── SNIPPET CARDS ────────────────────────────────────────────────────────────
function renderCards() {{
  const container = document.getElementById('snippetCards');
  const filtered = currentCat === 'all' ? seoPages : seoPages.filter(p => p.cat === currentCat);
  let html = '';
  filtered.forEach(p => {{
    const t = getTitle(p), d = getDesc(p);
    const tl = t.length, dl = d.length;
    const hasChange = seoChanges[p.path];
    const isEditing = editingPath === p.path;
    const borderClass = hasChange ? 'border-amber-500/50' : 'border-slate-700';
    const cardId = 'card-' + p.path.replace(/[^a-z0-9]/g, '-');

    if (isEditing) {{
      html += `<div id="${{cardId}}" class="bg-slate-800 rounded-xl border ${{borderClass}} p-5">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <iconify-icon icon="lucide:globe" width="18" class="text-slate-500"></iconify-icon>
            <span class="text-white font-semibold">${{esc(pageName(p))}}</span>
            <code class="text-xs text-slate-500">${{esc(p.path)}}</code>
          </div>
        </div>
        <div class="space-y-4">
          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="text-sm text-slate-400">Title</label>
              <span id="editTitleCount" class="text-xs font-mono"></span>
            </div>
            <input id="editTitleInput" type="text" value="${{esc(t)}}" oninput="updateEditCounts()"
              class="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white text-sm focus:border-indigo-500 focus:outline-none">
          </div>
          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="text-sm text-slate-400">Description</label>
              <span id="editDescCount" class="text-xs font-mono"></span>
            </div>
            <textarea id="editDescInput" rows="3" oninput="updateEditCounts()"
              class="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white text-sm focus:border-indigo-500 focus:outline-none resize-none">${{esc(d)}}</textarea>
          </div>
          <div class="bg-white rounded-xl p-4">
            <p class="text-xs text-[#202124] mb-1">https://${{DOMAIN}}${{esc(p.path)}}</p>
            <p id="editPreviewTitle" class="text-lg text-[#1a0dab] font-medium truncate">${{esc(t)}}</p>
            <p id="editPreviewDesc" class="text-sm text-[#4d5156] line-clamp-2">${{esc(d)}}</p>
          </div>
          <div class="flex gap-3">
            <button onclick="cancelEdit()" class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors">Annuler</button>
            <button onclick="saveEdit('${{p.path}}','${{esc(p.title).replace(/'/g,"\\\\'")}}',' ${{esc(p.desc).replace(/'/g,"\\\\'")}}')" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors">Enregistrer</button>
          </div>
        </div>
      </div>`;
    }} else {{
      html += `<div id="${{cardId}}" class="bg-slate-800 rounded-xl border ${{borderClass}} p-5">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <iconify-icon icon="lucide:globe" width="18" class="text-slate-500"></iconify-icon>
            <span class="text-white font-semibold">${{esc(pageName(p))}}</span>
            <code class="text-xs text-slate-500">${{esc(p.path)}}</code>
          </div>
          <button onclick="startEdit('${{p.path}}')" class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition-colors">Modifier</button>
        </div>
        <div class="bg-white rounded-xl p-4 mb-4">
          <p class="text-xs text-[#202124] mb-1">https://${{DOMAIN}}${{esc(p.path)}}</p>
          <p class="text-lg text-[#1a0dab] font-medium truncate">${{esc(t)}}</p>
          <p class="text-sm text-[#4d5156] line-clamp-2">${{esc(d)}}</p>
        </div>
        <div class="flex items-center gap-4 text-xs">
          <span>Title: <span class="font-mono ${{lenColor(tl,50,60)}}">${{tl}}/60</span></span>
          <span>Desc: <span class="font-mono ${{lenColor(dl,150,160)}}">${{dl}}/160</span></span>
          ${{hasChange ? '<span class="text-amber-400">[modifi\\u00e9]</span>' : ''}}
        </div>
      </div>`;
    }}
  }});
  container.innerHTML = html;
  updateSummary();
  renderSummaryTable();
  if (editingPath) setTimeout(updateEditCounts, 50);
}}

// ── EDIT ─────────────────────────────────────────────────────────────────────
function startEdit(path) {{
  editingPath = path;
  renderCards();
}}
function cancelEdit() {{
  editingPath = null;
  renderCards();
}}
function saveEdit(path, origTitle, origDesc) {{
  const newT = document.getElementById('editTitleInput').value;
  const newD = document.getElementById('editDescInput').value;
  const page = seoPages.find(p => p.path === path);
  if (newT !== page.title || newD !== page.desc) {{
    seoChanges[path] = {{ title: newT, desc: newD }};
  }} else {{
    delete seoChanges[path];
  }}
  localStorage.setItem('sbn_seoChanges', JSON.stringify(seoChanges));
  editingPath = null;
  renderCards();
}}
function updateEditCounts() {{
  const ti = document.getElementById('editTitleInput');
  const di = document.getElementById('editDescInput');
  if (!ti || !di) return;
  const tl = ti.value.length, dl = di.value.length;
  document.getElementById('editTitleCount').innerHTML = `<span class="${{lenColor(tl,50,60)}}">${{tl}} / 60</span>`;
  document.getElementById('editDescCount').innerHTML = `<span class="${{lenColor(dl,150,160)}}">${{dl}} / 160</span>`;
  document.getElementById('editPreviewTitle').textContent = ti.value;
  document.getElementById('editPreviewDesc').textContent = di.value;
}}

// ── SCROLL TO SNIPPET ────────────────────────────────────────────────────────
function scrollToSnippet(path, cat) {{
  if (currentCat !== 'all' && currentCat !== cat) switchCat(cat);
  const cardId = 'card-' + path.replace(/[^a-z0-9]/g, '-');
  setTimeout(() => {{
    const el = document.getElementById(cardId);
    if (el) {{
      el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      el.classList.add('ring-highlight', 'ring-2', 'ring-indigo-500');
      setTimeout(() => el.classList.remove('ring-highlight', 'ring-2', 'ring-indigo-500'), 2000);
    }}
  }}, 100);
}}

// ── SUMMARY ──────────────────────────────────────────────────────────────────
function updateSummary() {{
  let ok = 0;
  seoPages.forEach(p => {{
    const tl = getTitle(p).length, dl = getDesc(p).length;
    if (tl >= 50 && tl <= 60 && dl >= 150 && dl <= 160) ok++;
  }});
  const total = seoPages.length;
  const color = ok === total ? 'text-emerald-400' : 'text-amber-400';
  document.getElementById('seoSummaryText').innerHTML = `<span class="${{color}}">${{ok}} / ${{total}} OK</span> &mdash; ${{Object.keys(seoChanges).length}} modification(s) en cours`;
  document.getElementById('statOk').textContent = ok + '/' + total;
  document.getElementById('statOk').className = 'text-2xl font-bold ' + (ok === total ? 'text-emerald-400' : 'text-amber-400');
  document.getElementById('exportCount').textContent = Object.keys(seoChanges).length + ' modification(s) non export\\u00e9e(s)';
}}

// ── EXPORT ───────────────────────────────────────────────────────────────────
function exportChanges() {{
  const area = document.getElementById('exportArea');
  area.classList.toggle('hidden');
  document.getElementById('exportJson').value = JSON.stringify(seoChanges, null, 2);
}}

// ── GOOGLE INDEX BADGE ───────────────────────────────────────────────────────
function updateGoogleBadge() {{
  const keys = Object.keys(googleIndex);
  const indexed = Object.values(googleIndex).filter(v => v === true).length;
  const missing = Object.values(googleIndex).filter(v => v === false).length;
  const unknown = seoPages.length - keys.length;
  const badge = document.getElementById('googleIndexBadge');
  if (googleIndexCheckedAt) {{
    badge.textContent = `${{indexed}} index\\u00e9es / ${{missing}} absentes / ${{unknown}} non v\\u00e9rifi\\u00e9es (${{googleIndexCheckedAt}})`;
  }} else {{
    badge.textContent = 'Indexation Google non v\\u00e9rifi\\u00e9e';
  }}
}}

// ── INIT ─────────────────────────────────────────────────────────────────────
document.getElementById('notesArea').value = localStorage.getItem('sbn_admin_notes') || '';
updateGoogleBadge();
renderCards();
</script>
</body></html>'''

# ── Write ────────────────────────────────────────────────────────────────────
os.makedirs(os.path.join(BASE, 'admin'), exist_ok=True)
out_path = os.path.join(BASE, 'admin', 'index.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html_out)
print(f"✓ admin/index.html généré ({len(html_out):,} octets, {total} pages SEO)")
