#!/usr/bin/env python3
"""
Génère les pages thématiques indexables (SMIC, apprentissage, stage, cadre...).

Usage : python3 generate-thematiques.py

Ce script ne touche qu'aux dossiers listés dans PAGES et REDIRECTIONS, et ajoute
leurs adresses au sitemap.xml sans retirer celles qui y sont déjà. Il ne régénère
ni les pages de montants (qui restent des redirections), ni les autres pages.

Kit de confiance (RECETTE §8.4) : date de mise à jour tirée de git (dernier commit
de ce script et de calcul.py, jamais la date du jour), éditeur, liens vers la
méthodologie et la confidentialité, sources officielles citées sur chaque page.
L'en-tête du site (menu) et le marquage GA4/Clarity sont repris de la page servie
/prime-brut-en-net/, pour rester identiques au reste du site.

Les chiffres officiels 2026 ont été relevés le 2026-10-26 sur service-public.gouv.fr,
urssaf.fr, insee.fr et retraitesdeletat.gouv.fr : voir les constantes ci-dessous.
"""

import html
import json
import math
import os
import re
import subprocess

from calcul import (
    HEURES_MENSUELLES, PSS_HORAIRE, PSS_MENSUEL, SMIC_HORAIRE, SMIC_HORAIRE_JANVIER,
    SMIC_MENSUEL_BRUT, SMIC_MENSUEL_JANVIER, arrondi, calculer_brut_vers_net, fmt, fmt2,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://salairebrutonet.com"
SCRIPT = os.path.basename(__file__)
MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
           "août", "septembre", "octobre", "novembre", "décembre"]

# ── Chiffres officiels 2026 (relevés le 2026-10-26) ───────────────────────────
# SMIC : service-public.gouv.fr F2300 (vérifié le 1er juin 2026), arrêté du 22 mai 2026
SMIC_NET_HORAIRE_SP = 9.74
SMIC_NET_MENSUEL_SP = 1477.93
SMIC_BRUT_ANNUEL_SP = 22404.20
SMIC_NET_ANNUEL_SP = 17735.19
SMIC_MAYOTTE_HORAIRE = 9.56
SMIC_MAYOTTE_MENSUEL = 1449.93
# Apprentis : service-public.gouv.fr F2918 (vérifié le 8 septembre 2026)
APPRENTI_GRILLE = {  # âge -> pourcentages du SMIC en 1re, 2e, 3e année
    "16-17 ans": (27, 39, 55),
    "18-20 ans": (43, 51, 67),
    "21-25 ans": (53, 61, 78),
    "26 ans et plus": (100, 100, 100),
}
APPRENTI_SEUIL_EXO = 933.51
# Service-public calcule les pourcentages sur le SMIC non arrondi : 12,31 € × 35 h × 52 / 12
SMIC_EXACT = SMIC_HORAIRE * 35 * 52 / 12  # 50 % du SMIC, contrats conclus depuis le 1er mars 2025
# Stage : service-public.gouv.fr F32131 et urssaf.fr (montants au 1er janvier 2026)
GRATIFICATION_HORAIRE = 4.50  # 15 % du plafond horaire de la Sécurité sociale (30 €)
# Salaires du privé en 2024 : Insee Première n° 2079 (23 octobre 2025)
INSEE = {
    "moyen_net": 2733, "moyen_brut": 3602, "median_net": 2190, "d1": 1492, "d9": 4334,
    "cadres": 4629, "prof_inter": 2633, "employes": 1941, "ouvriers": 2051, "ecart_fh": "13,0",
}
# Fonction publique : service-public.gouv.fr F461 (vérifié le 1er juin 2026),
# retraitesdeletat.gouv.fr (retenue pour pension), cor-retraites.fr (RAFP)
POINT_ANNUEL_IM100 = 5907.34
TAUX_PENSION_CIVILE = 0.111
TAUX_RAFP = 0.05
# Heures supplémentaires : urssaf.fr et service-public.gouv.fr F2391
TAUX_REDUCTION_HS = 0.1131
PLAFOND_IR_HS = 7500

# Taux salarial « tranche 1 » utilisé dans les explications : vieillesse 7,30 %,
# Agirc-Arrco 3,15 %, CEG 0,86 %, CSG-CRDS 9,70 % sur 98,25 % du brut (URSSAF 2026).
TAUX_RETRAITE_T1 = 0.069 + 0.004 + 0.0315 + 0.0086
TAUX_CSG_CRDS = 0.097 * 0.9825


# ── Outils ────────────────────────────────────────────────────────────────────

def date_maj(*fichiers):
    """Date du dernier commit touchant l'un des fichiers (§8.4), jamais la date du jour."""
    dates = []
    for f in fichiers:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", f],
                             cwd=BASE_DIR, capture_output=True, text=True).stdout.strip()
        if out:
            dates.append(out)
    if not dates:
        return "", ""
    iso = max(dates)
    a, m, j = iso.split("-")
    return iso, f"{int(j)} {MOIS_FR[int(m) - 1]} {a}"


def e(val):
    """Montant arrondi à l'euro : « 1 868 € »."""
    return f"{fmt(val)} €"


def e2(val):
    """Montant au centime : « 1 867,02 € »."""
    return f"{fmt2(val)} €"


def pct(val, dec=1):
    s = f"{val:.{dec}f}".replace(".", ",")
    return f"{s} %"


def net(brut, statut="non-cadre", **kw):
    return calculer_brut_vers_net(brut, statut, **kw)["net_avant_impot"]


def table(entetes, lignes, total=None):
    th = "".join(f"<th>{h}</th>" for h in entetes)
    corps = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>" for l in lignes)
    if total:
        corps += '<tr class="tp-total">' + "".join(f"<td>{c}</td>" for c in total) + "</tr>"
    return f'<div class="tp-wrap"><table class="tp-table"><thead><tr>{th}</tr></thead><tbody>{corps}</tbody></table></div>'


def note(texte):
    return f'<p class="tp-note">{texte}</p>'


def nbsp_texte(m):
    """Espaces insécables dans un texte (RECETTE §10.3) : milliers, unités, ponctuation double."""
    m = re.sub(r"(\d) (?=\d{3}(?!\d))", "\\1\u00a0", m)
    m = re.sub(r"(\d) (?=\d{3}(?!\d))", "\\1\u00a0", m)
    m = re.sub(r"(\d) (?=(?:%|€|\$|CHF|Fr\.|h\b|ans\b|mois\b|heures\b|jours\b|salariés\b))", "\\1\u00a0", m)
    m = re.sub(r" (?=[:;?!»])", "\u00a0", m)
    return m.replace("« ", "«\u00a0")


def nbsp(doc):
    """Applique nbsp_texte au texte affiché et aux chaînes des blocs JSON-LD, comme scripts/typo-nbsp.mjs
    de la trame : la réponse déclarée à Google reste ainsi identique à la réponse affichée."""
    morceaux = re.split(r"(<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)", doc, flags=re.S)
    for i, m in enumerate(morceaux):
        if not m:
            continue
        if m.startswith('<script type="application/ld+json">'):
            morceaux[i] = re.sub(r'"(?:[^"\\]|\\.)*"', lambda c: c.group(0) if re.match(r"\s*:", c.string[c.end():])
                                 else nbsp_texte(c.group(0)), m)
        elif not m.startswith("<"):
            morceaux[i] = nbsp_texte(m)
    return "".join(morceaux)


def compter_mots(texte):
    return len(re.findall(r"[\wÀ-ÿ'’,.%€-]+", texte))


# ── Gabarit commun ────────────────────────────────────────────────────────────

def extraire_gabarit():
    """Reprend de /prime-brut-en-net/ le marquage d'audience, l'en-tête et le script du menu."""
    with open(os.path.join(BASE_DIR, "prime-brut-en-net", "index.html"), encoding="utf-8") as f:
        src = f.read()
    mesure = re.search(r"\s*<!-- GA4.*?clarity\.ms/tag/[^<]*</script>", src, re.S)
    entete = re.search(r"(<a href=\"#main-content\".*?</header>)", src, re.S)
    menu = re.search(r"</footer>\s*(<script>.*?</script>)", src, re.S)
    if not (mesure and entete and menu):
        raise SystemExit("Gabarit introuvable dans prime-brut-en-net/index.html : arrêt sans rien écrire.")
    return mesure.group(0).strip(), entete.group(1), menu.group(1)


def jsonld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + "\n</script>"


def rendre(p, gabarit, maj_iso, maj_lisible, titres):
    mesure, entete, menu = gabarit
    url = f"{BASE_URL}/{p['slug']}/"
    t, d = html.escape(p["title"]), html.escape(p["desc"])

    faq_html = "".join(
        f'<details class="tp-faq" open><summary>{html.escape(q)}</summary><p>{html.escape(r)}</p></details>'
        for q, r in p["faq"])
    faq_ld = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}}
                       for q, r in p["faq"]],
    }
    page_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Calculateur salaire brut net", "item": f"{BASE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": p["crumb"], "item": url}]},
            {"@type": "WebPage", "@id": url, "url": url, "name": p["title"], "description": p["desc"],
             "inLanguage": "fr-FR", **({"dateModified": maj_iso} if maj_iso else {}),
             "isPartOf": {"@type": "WebSite", "name": "Salaire Bruto Net", "url": f"{BASE_URL}/"},
             "publisher": {"@type": "Organization", "name": "Radif Partners", "url": f"{BASE_URL}/a-propos/"}},
            {"@type": "Organization", "name": "Salaire Bruto Net", "url": BASE_URL,
             "logo": f"{BASE_URL}/img/logo.svg", "foundingDate": "2025-01-01",
             "publishingPrinciples": f"{BASE_URL}/methodologie/",
             "parentOrganization": {"@type": "Organization", "name": "Radif Partners", "url": f"{BASE_URL}/a-propos/"}},
        ],
    }
    sources_li = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{html.escape(l)}</a></li>'
                         for l, u in p["sources"])
    sources_pied = " &middot; ".join(
        f'<a class="underline" href="{u}" rel="noopener" target="_blank">{html.escape(l.split(",")[0])}</a>'
        for l, u in p["sources"][:4])
    connexes = "".join(
        f'<a href="/{s}/" class="block rounded-xl border border-slate-200 bg-white p-3 text-center hover:shadow-sm transition-all">'
        f'<span class="block text-sm font-medium text-slate-900">{titres[s]}</span></a>'
        for s in p["related"])
    date_haut = (f'<p class="maj-haut text-xs text-slate-500 mb-4">Mise à jour le <time datetime="{maj_iso}">{maj_lisible}</time> · '
                 f'<a href="/a-propos/" class="text-brand-600">Radif Partners</a> · <a href="/methodologie/" class="text-brand-600">Méthodologie</a></p>'
                 if maj_iso else "")
    date_bas = (f' · Mise à jour le <time datetime="{maj_iso}">{maj_lisible}</time>' if maj_iso else "")

    doc = f"""<!DOCTYPE html>
<html lang="fr" class="scroll-smooth"><head>
    <meta name="msvalidate.01" content="15b1d26333aa4cd7a1cdba8e813bfc7f" />
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t}</title>
    <meta name="description" content="{d}">
    <link rel="canonical" href="{url}">
    <link rel="icon" type="image/svg+xml" href="/img/logo.svg">
    <link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png">
    <link rel="apple-touch-icon" sizes="192x192" href="/img/favicon-192.png">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="{t}">
    <meta property="og:description" content="{d}">
    <meta property="og:locale" content="fr_FR">
    <meta property="og:site_name" content="Salaire Bruto Net">
    <meta property="og:image" content="{BASE_URL}/img/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{t}">
    <meta name="twitter:description" content="{d}">
    <meta name="twitter:image" content="{BASE_URL}/img/og-image.png">
    <meta name="robots" content="index, follow">
    <meta name="author" content="Radif Partners">
    <link rel="manifest" href="/manifest.webmanifest">
    <link rel="stylesheet" href="/css/fonts.css">
    <link rel="stylesheet" href="/css/style.css">
    {jsonld(page_ld)}
    {jsonld(faq_ld)}
    {mesure}
</head>
<body data-clarity-mask="true" class="bg-slate-50 text-slate-600 antialiased selection:bg-brand-100 selection:text-brand-900 flex flex-col min-h-screen">
    {entete}
    <main id="main-content" class="flex-grow" role="main">
        <nav class="mx-auto max-w-5xl px-4 pt-4" aria-label="Fil d'Ariane">
            <ol class="flex items-center gap-2 text-sm text-slate-500">
                <li><a href="/" class="hover:text-brand-600 transition-colors">Accueil</a></li>
                <li aria-hidden="true">›</li>
                <li class="text-slate-900 font-medium">{p['crumb']}</li>
            </ol>
        </nav>
        <section class="px-4 pt-4">
            <div class="mx-auto max-w-5xl">
                <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 mb-2">{p['h1']}</h1>
                {date_haut}
            </div>
        </section>
        <section class="px-4 pb-6">
            <div class="mx-auto max-w-5xl rounded-2xl border border-slate-200 bg-white p-5 shadow-sm" data-outil>
                <h2 class="text-lg font-semibold text-slate-900 mb-4">{p['widget_titre']}</h2>
                {p['widget']}
            </div>
        </section>
        <section class="bg-white border-t border-slate-200 py-8 px-4">
            <div class="mx-auto max-w-5xl">
                <!-- §21 : le paragraphe qui tient seul une fois extrait de la page. -->
                <p class="bloc-citable text-slate-700 leading-relaxed">{p['citable']}</p>
            </div>
        </section>
        <section class="py-10 px-4">
            <div class="mx-auto max-w-5xl tp-prose">
                {p['corps']}
                <div class="tp-sources mt-8 rounded-xl border border-slate-200 bg-white p-5">
                    <p class="text-sm font-semibold text-slate-700 mb-2">Sources officielles</p>
                    <ul class="space-y-1 text-sm text-slate-600">{sources_li}</ul>
                    <p class="tp-note mt-3">Chiffres relevés sur ces sites le 26 octobre 2026. Les montants nets sont des estimations du régime général : la mutuelle et la prévoyance d'entreprise, propres à chaque contrat, n'y sont pas déduites. <a href="/methodologie/">Méthode de calcul</a>.</p>
                </div>
            </div>
        </section>
        <section class="bg-white border-t border-slate-200 py-10 px-4">
            <div class="mx-auto max-w-5xl">
                <h2 class="text-xl font-bold text-slate-900 mb-6">Questions fréquentes</h2>
                <div class="space-y-3">{faq_html}</div>
            </div>
        </section>
        <section class="border-t border-slate-200 py-10 px-4">
            <div class="mx-auto max-w-5xl">
                <h2 class="text-lg font-bold text-slate-900 mb-4">Pages connexes</h2>
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">{connexes}</div>
            </div>
        </section>
    </main>

    <footer class="bg-white border-t border-slate-200 py-10">
        <div class="mx-auto max-w-7xl px-4 flex flex-col md:flex-row justify-between items-center gap-6">
            <a href="/" class="flex items-center gap-2">
                <img src="/img/logo.svg" alt="Salaire Bruto Net" class="h-6 w-6">
                <span class="text-sm font-semibold text-slate-900">Salaire Bruto Net</span>
            </a>
            <p class="text-xs text-slate-500">© 2026 Salaire Bruto Net · Estimation indicative</p>
            <div class="flex flex-wrap gap-4 justify-center">
                <a href="/" class="text-xs text-slate-500 hover:text-slate-900">Calculateur</a>
                <a href="/simulateur-impot-sur-le-revenu/" class="text-xs text-slate-500 hover:text-slate-900">Simulateur Impôts</a>
                <a href="/cadre-vs-non-cadre/" class="text-xs text-slate-500 hover:text-slate-900">Cadre vs Non-cadre</a>
                <a href="/confidentialite/" class="text-xs text-slate-500 hover:text-slate-900">Confidentialité</a>
                <a href="/methodologie/" class="text-xs text-slate-500 hover:text-slate-900">Méthodologie</a>
                <a href="/mentions-legales/" class="text-xs text-slate-500 hover:text-slate-900">Mentions légales</a>
                <a href="/a-propos/" class="text-xs text-slate-500 hover:text-slate-900">À propos</a>
                <a href="/mission/" class="text-xs text-slate-500 hover:text-slate-900">Notre Mission</a>
            </div>
            <p class="text-xs text-slate-500 w-full text-center" data-author="Radif Partners">
                Édité par Radif Partners{date_bas}
            </p>
            <p class="text-xs text-slate-500 w-full text-center">
                Sources : {sources_pied}
            </p>
        </div>
    </footer>
    <script src="/js/brut-net.js"></script>
    <script>
    (function() {{
        function v(id) {{ var x = document.getElementById(id); return parseFloat(String(x.value).replace(/\\s/g, '').replace(',', '.')) || 0; }}
        function out(id, txt) {{ document.getElementById(id).textContent = txt; }}
        function euros(x) {{ return formatMoney(x); }}
        function centimes(x) {{ return formatMoneyPrecis(x); }}
        function calc() {{
{p['js']}
        }}
        document.querySelectorAll('.tp-champ').forEach(function(c) {{ c.addEventListener('input', calc); c.addEventListener('change', calc); }});
        calc();
    }})();
    </script>
    {menu}
</body></html>
"""
    return nbsp(doc)


# ── Champs du calculateur ─────────────────────────────────────────────────────

def champ(id_, label, valeur, inputmode="decimal"):
    return (f'<div><label for="{id_}" class="block text-sm font-medium text-slate-700 mb-1">{label}</label>'
            f'<input type="text" inputmode="{inputmode}" id="{id_}" value="{valeur}" class="tp-champ text-lg font-bold"></div>')


def choix(id_, label, options, defaut=None):
    opts = "".join(f'<option value="{v}"{" selected" if v == defaut else ""}>{l}</option>' for v, l in options)
    return (f'<div><label for="{id_}" class="block text-sm font-medium text-slate-700 mb-1">{label}</label>'
            f'<select id="{id_}" class="tp-champ text-sm">{opts}</select></div>')


def resultats(items):
    cases = "".join(f'<div><span>{l}</span><strong id="{i}">–</strong></div>' for i, l in items)
    return f'<div class="tp-resultat mt-4" data-resultat aria-live="polite">{cases}</div>'


def widget(champs, items, remarque=""):
    n = len(champs)
    cols = "sm:grid-cols-3" if n >= 3 else ("sm:grid-cols-2" if n == 2 else "")
    r = f'<p class="tp-note mt-3 mb-0">{remarque}</p>' if remarque else ""
    return f'<div class="grid grid-cols-1 {cols} gap-4">{"".join(champs)}</div>{resultats(items)}{r}'


STATUT = [("non-cadre", "Non-cadre"), ("cadre", "Cadre")]

# ── Sources ───────────────────────────────────────────────────────────────────

SRC_SMIC = ("Service-Public.fr, montant du Smic", "https://www.service-public.gouv.fr/particuliers/vosdroits/F2300")
SRC_TAUX = ("Urssaf, taux de cotisations 2026 du secteur privé", "https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-secteur-prive.html")
SRC_PSS = ("Urssaf, plafonds de la Sécurité sociale 2026", "https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/plafonds-securite-sociale.html")
SRC_APPRENTI = ("Service-Public.fr, rémunération de l'apprenti", "https://www.service-public.gouv.fr/particuliers/vosdroits/F2918")
SRC_APPRENTI_URSSAF = ("Urssaf, contrat d'apprentissage et exonérations", "https://www.urssaf.fr/accueil/employeur/embaucher-gerer-salaries/embaucher/contrat-apprentissage.html")
SRC_STAGE = ("Service-Public.fr, gratification de stage", "https://www.service-public.gouv.fr/particuliers/vosdroits/F32131")
SRC_STAGE_URSSAF = ("Urssaf, accueillir un stagiaire étudiant", "https://www.urssaf.fr/accueil/employeur/embaucher-gerer-salaries/embaucher/stagiaire-etudiant.html")
SRC_INSEE = ("Insee Première n° 2079, les salaires dans le secteur privé en 2024", "https://www.insee.fr/fr/statistiques/8657156")
SRC_HS_SP = ("Service-Public.fr, heures supplémentaires", "https://www.service-public.gouv.fr/particuliers/vosdroits/F2391")
SRC_HS_URSSAF = ("Urssaf, réduction de cotisations salariales sur les heures supplémentaires", "https://www.urssaf.fr/accueil/employeur/beneficier-exonerations/exonerations-heures/reduction-cotisations-salariales.html")
SRC_HS_PATRONAL = ("Urssaf, déduction forfaitaire patronale", "https://www.urssaf.fr/accueil/employeur/beneficier-exonerations/exonerations-heures/deduction-forfaitaire-patronale.html")
SRC_RGDU = ("Urssaf, réduction générale dégressive unique 2026", "https://www.urssaf.fr/accueil/employeur/beneficier-exonerations/reduction-generale-cotisation.html")
SRC_FP = ("Service-Public.fr, traitement indiciaire du fonctionnaire", "https://www.service-public.gouv.fr/particuliers/vosdroits/F461")
SRC_PENSION = ("Retraites de l'État, taux de la retenue pour pension", "https://retraitesdeletat.gouv.fr/actif/ma-carriere/mes-cotisations")
SRC_RAFP = ("Conseil d'orientation des retraites, fiche RAFP", "https://www.cor-retraites.fr/sites/default/files/2024-07/Fiche_RAFP_vf.pdf")


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_smic():
    n35 = net(SMIC_MENSUEL_BRUT)
    lignes = []
    for h in (35, 32, 30, 28, 24, 20, 17.5):
        brut = arrondi(SMIC_HORAIRE * h * 52 / 12, 2)
        lignes.append([f"{str(h).replace('.', ',')} h", e2(brut), e2(net(brut))])
    hs = arrondi(SMIC_HORAIRE * 1.25 * 4 * 52 / 12, 2)
    brut39 = SMIC_MENSUEL_BRUT + hs
    net39 = net(brut39) + hs * TAUX_REDUCTION_HS
    lignes.append(["39 h (4 h sup. à 25 %)", e2(brut39), e2(net39)])
    brut24 = arrondi(SMIC_HORAIRE * 24 * 52 / 12, 2)
    net_janv = net(SMIC_MENSUEL_JANVIER)
    corps = f"""
<h2>Le SMIC 2026 en chiffres officiels</h2>
{table(["Montant", "Brut", "Net (indicatif)"], [
    ["Horaire", e2(SMIC_HORAIRE), e2(SMIC_NET_HORAIRE_SP)],
    ["Mensuel (35 h par semaine)", e2(SMIC_MENSUEL_BRUT), e2(SMIC_NET_MENSUEL_SP)],
    ["Annuel", e2(SMIC_BRUT_ANNUEL_SP), e2(SMIC_NET_ANNUEL_SP)],
])}
{note("Montants en vigueur depuis le 1er juin 2026 en métropole et dans les DROM hors Mayotte, publiés par service-public.gouv.fr. Le net est donné à titre indicatif par l'administration ; notre moteur de calcul retrouve exactement le même net mensuel, " + e2(n35) + ".")}
<h2>Deux revalorisations en 2026</h2>
<p>Le SMIC a changé deux fois cette année. Au 1er janvier 2026, le décret n° 2025-1228 du 17 décembre 2025 l'a porté à <strong>{e2(SMIC_HORAIRE_JANVIER)} brut de l'heure</strong>, soit {e2(SMIC_MENSUEL_JANVIER)} par mois. Au 1er juin 2026, l'arrêté du 22 mai 2026 l'a relevé à <strong>{e2(SMIC_HORAIRE)}</strong>, soit {e2(SMIC_MENSUEL_BRUT)} par mois : une hausse de {pct((SMIC_HORAIRE / SMIC_HORAIRE_JANVIER - 1) * 100, 2)}, déclenchée automatiquement parce que les prix avaient progressé d'au moins 2 % depuis la revalorisation précédente.</p>
{table(["Période", "Horaire brut", "Mensuel brut", "Mensuel net estimé"], [
    ["1er janvier au 31 mai 2026", e2(SMIC_HORAIRE_JANVIER), e2(SMIC_MENSUEL_JANVIER), e2(net_janv)],
    ["Depuis le 1er juin 2026", e2(SMIC_HORAIRE), e2(SMIC_MENSUEL_BRUT), e2(n35)],
])}
{note("Le gain net mensuel entre les deux valeurs est de " + e2(n35 - net_janv) + " pour un temps plein.")}
<h2>SMIC brut et net selon la durée du travail</h2>
<p>Le taux horaire est le même pour tous les salariés majeurs ; le salaire mensuel suit le nombre d'heures prévu au contrat, multiplié par 52 semaines puis divisé par 12 mois. La dernière ligne montre un contrat à 39 heures : les quatre heures au-delà de 35 heures sont majorées de 25 % et bénéficient de la réduction de cotisations salariales de 11,31 %, ce qui explique un net proportionnellement plus élevé.</p>
{table(["Durée hebdomadaire", "SMIC brut mensuel", "SMIC net mensuel"], lignes)}
{note("Calcul : 12,31 € × heures hebdomadaires × 52 ÷ 12, puis cotisations salariales 2026 du régime général (non-cadre). Hors mutuelle d'entreprise.")}
<h2>Mayotte</h2>
<p>Mayotte suit une trajectoire propre de rattrapage. Depuis le 1er juin 2026, le SMIC y est de <strong>{e2(SMIC_MAYOTTE_HORAIRE)} brut de l'heure</strong>, soit {e2(SMIC_MAYOTTE_MENSUEL)} par mois pour 35 heures. Service-public.gouv.fr ne publie pas de montant net pour ce département, dont les taux de cotisations diffèrent : nous n'en donnons donc pas.</p>
<h2>Les montants qui dépendent du SMIC</h2>
<ul>
<li>La rémunération minimale des <a href="/salaire-brut-net-alternance-apprentissage/">apprentis</a>, de 27 % à 100 % du SMIC selon l'âge et l'année.</li>
<li>La <a href="/cout-employeur/">réduction générale des cotisations patronales</a>, maximale au niveau du SMIC et nulle à partir de 3 SMIC.</li>
<li>Le plancher de rémunération des agents de la <a href="/salaire-brut-net-fonction-publique/">fonction publique</a>, complété par une indemnité différentielle.</li>
</ul>
"""
    js = """
            var h = v('w-heures');
            var brut = Math.round(12.31 * h * 52 / 12 * 100) / 100;
            var r = calculerBrutVersNet(brut, 'non-cadre', 1);
            out('r-brut', centimes(brut));
            out('r-net', centimes(r.netAvantImpot));
            out('r-horaire', centimes(h > 0 ? r.netAvantImpot / (h * 52 / 12) : 0));"""
    return {
        "slug": "smic-brut-net-2026",
        "title": "SMIC brut net 2026 : 1 867,02 € brut et 1 477,93 € net",
        "desc": "SMIC brut net 2026 : 12,31 € brut de l'heure depuis le 1er juin, soit 1 867,02 € brut et 1 477,93 € net par mois à 35 h. Tableau selon la durée du travail.",
        "h1": "SMIC brut et net 2026",
        "crumb": "SMIC brut net 2026",
        "widget_titre": "SMIC net selon vos heures",
        "widget": widget([champ("w-heures", "Heures par semaine", "35")],
                         [("r-brut", "SMIC brut mensuel"), ("r-net", "SMIC net mensuel"), ("r-horaire", "Net de l'heure")]),
        "js": js,
        "citable": f"Depuis le 1er juin 2026, le SMIC s'élève à {e2(SMIC_HORAIRE)} brut de l'heure, soit {e2(SMIC_MENSUEL_BRUT)} brut et environ {e2(SMIC_NET_MENSUEL_SP)} net par mois pour 35 heures par semaine, selon service-public.gouv.fr. Il était de {e2(SMIC_HORAIRE_JANVIER)} de l'heure du 1er janvier au 31 mai 2026. Le passage du brut au net retire environ 20,8 % de cotisations salariales et de CSG-CRDS ; un salarié à temps partiel touche le même taux horaire, proratisé : {e2(net(brut24))} net pour 24 heures par semaine. Côté employeur, la réduction générale dégressive unique efface l'essentiel des cotisations patronales à ce niveau : un temps plein au SMIC coûte environ {e(cout_detail(SMIC_MENSUEL_BRUT)['cout'])} par mois dans une entreprise de moins de onze salariés. À Mayotte, le SMIC horaire brut est de {e2(SMIC_MAYOTTE_HORAIRE)}.",
        "corps": corps,
        "sources": [SRC_SMIC, SRC_TAUX, SRC_PSS, SRC_RGDU],
        "faq": [
            ("Quel est le montant du SMIC net en 2026 ?",
             f"Depuis le 1er juin 2026, le SMIC net s'élève à environ {e2(SMIC_NET_MENSUEL_SP)} par mois pour 35 heures par semaine, soit {e2(SMIC_NET_HORAIRE_SP)} de l'heure. Ce montant, indiqué à titre indicatif par service-public.gouv.fr, correspond au brut de {e2(SMIC_MENSUEL_BRUT)} après cotisations salariales et CSG-CRDS. Une mutuelle d'entreprise obligatoire le réduit encore de sa part salariale, puis le prélèvement à la source s'applique le cas échéant."),
            ("Pourquoi le SMIC a-t-il augmenté en juin 2026 ?",
             f"Le Code du travail prévoit une revalorisation automatique en cours d'année dès que l'indice des prix de référence a progressé d'au moins 2 % depuis la revalorisation précédente. Ce seuil ayant été franchi, l'arrêté du 22 mai 2026 a porté le taux horaire brut de {e2(SMIC_HORAIRE_JANVIER)} à {e2(SMIC_HORAIRE)} au 1er juin 2026, soit une hausse de 2,41 % qui s'applique à tous les salaires versés pour le travail effectué depuis cette date."),
            ("Le SMIC est-il le même pour un temps partiel ?",
             f"Le taux horaire est identique, {e2(SMIC_HORAIRE)} brut, quelle que soit la durée du contrat. Le salaire mensuel minimum se calcule au prorata des heures prévues : un contrat de 24 heures par semaine donne {e2(brut24)} brut et environ {e2(net(brut24))} net par mois. Les heures complémentaires effectuées au-delà de la durée prévue au contrat sont majorées d'au moins 10 %."),
            ("Le SMIC s'applique-t-il aux apprentis et aux stagiaires ?",
             f"Pas directement. Un apprenti perçoit un pourcentage du SMIC qui dépend de son âge et de son année de formation, de 27 % à 100 %. Un stagiaire n'est pas salarié : il reçoit une gratification minimale de {e2(GRATIFICATION_HORAIRE)} par heure de stage en 2026, obligatoire au-delà de deux mois de présence. Dans les deux cas, des exonérations propres rapprochent le net du brut."),
            ("Combien coûte un salarié au SMIC à son employeur ?",
             f"Grâce à la réduction générale dégressive unique, les cotisations patronales sont presque entièrement effacées au niveau du SMIC. Pour une entreprise de moins de onze salariés, le coût total d'un temps plein au SMIC ressort à environ {e(cout_detail(SMIC_MENSUEL_BRUT)['cout'])} par mois avec un taux accidents du travail de 1 %. Le détail ligne par ligne figure sur notre page consacrée au coût employeur."),
        ],
        "related": ["salaire-brut-net-horaire", "salaire-brut-net-alternance-apprentissage", "heures-supplementaires-brut-net", "cout-employeur", "salaire-moyen-france", "salaire-brut-net-non-cadre"],
    }


def net_apprenti(brut):
    """Contrats conclus depuis le 1er mars 2025 : exonération salariale et CSG-CRDS jusqu'à 50 % du SMIC."""
    part = max(0, brut - APPRENTI_SEUIL_EXO)
    return brut - part * (TAUX_RETRAITE_T1 + TAUX_CSG_CRDS), part


def page_apprenti():
    grille = []
    detail = []
    for annee in range(3):
        ligne = [f"{annee + 1}{'re' if annee == 0 else 'e'} année"]
        for age, taux in APPRENTI_GRILLE.items():
            brut = arrondi(SMIC_EXACT * taux[annee] / 100, 2)
            ligne.append(f"{taux[annee]} % · {e2(brut)}")
        grille.append(ligne)
    for age, taux in APPRENTI_GRILLE.items():
        for annee in range(3):
            if age == "26 ans et plus" and annee > 0:
                continue
            brut = arrondi(SMIC_EXACT * taux[annee] / 100, 2)
            n, part = net_apprenti(brut)
            detail.append([age, "toutes" if age == "26 ans et plus" else f"{annee + 1}{'re' if annee == 0 else 'e'}",
                           e2(brut), e2(part), e2(n)])
    n_max, _ = net_apprenti(SMIC_MENSUEL_BRUT)
    n78, part78 = net_apprenti(arrondi(SMIC_EXACT * 0.78, 2))
    corps = f"""
<h2>Salaire minimum d'un apprenti en 2026</h2>
<p>La rémunération minimale est un pourcentage du SMIC, fixé selon l'âge de l'apprenti et l'année d'exécution du contrat. Avec le SMIC de {e2(SMIC_MENSUEL_BRUT)} brut en vigueur depuis le 1er juin 2026, la grille officielle donne les montants bruts mensuels suivants.</p>
{table(["Année", "16-17 ans", "18-20 ans", "21-25 ans", "26 ans et plus"], grille)}
{note("Source : service-public.gouv.fr, page vérifiée le 8 septembre 2026. Un apprenti de moins de 16 ans est payé comme un 16-17 ans. À partir de 21 ans, le pourcentage s'applique au salaire minimum conventionnel du poste s'il est plus élevé que le SMIC.")}
<h2>Du brut au net : la règle des 50 % du SMIC</h2>
<p>Pour les contrats conclus depuis le 1er mars 2025, l'apprenti est exonéré de cotisations salariales et de CSG-CRDS sur la partie de son salaire qui ne dépasse pas <strong>50 % du SMIC, soit {e2(APPRENTI_SEUIL_EXO)} par mois</strong>. Au-delà, la fraction qui dépasse supporte les cotisations ordinaires : environ 11,31 % pour la retraite de base et complémentaire et 9,53 % de CSG-CRDS, soit près de 20,8 % de la seule part excédentaire.</p>
{table(["Âge", "Année", "Brut minimum", "Part soumise", "Net estimé"], detail)}
{note("Net estimé hors mutuelle d'entreprise. Part soumise = brut moins " + e2(APPRENTI_SEUIL_EXO) + ". Exemple : un apprenti de 21 à 25 ans en 3e année gagne " + e2(SMIC_EXACT * 0.78) + " brut ; " + e2(part78) + " sont soumis, d'où un net d'environ " + e2(n78) + ".")}
<h2>Contrats commencés avant le 1er mars 2025</h2>
<p>Les contrats ayant débuté au plus tard le 28 février 2025 conservent l'ancien régime : exonération des cotisations salariales dans la limite de 79 % du SMIC, soit {e2(SMIC_EXACT * 0.79)} par mois, et exonération de CSG et de CRDS sans plafond. Pour ces apprentis, le net reste égal au brut tant que le salaire ne dépasse pas ce seuil, ce qui couvre toutes les cases de la grille sauf celle des 26 ans et plus.</p>
<h2>Impôt sur le revenu</h2>
<p>Le salaire de l'apprenti est exonéré d'impôt sur le revenu dans la limite du montant annuel du SMIC. Seule la fraction annuelle qui dépasse cette limite est à déclarer comme imposable : en pratique, un apprenti payé au pourcentage légal n'est imposé que s'il perçoit en plus des primes ou des heures supplémentaires importantes.</p>
"""
    js = """
            var grille = {'16': [27, 39, 55], '18': [43, 51, 67], '21': [53, 61, 78], '26': [100, 100, 100]};
            var pc = grille[document.getElementById('w-age').value][parseInt(document.getElementById('w-annee').value)];
            var brut = Math.round(12.31 * 35 * 52 / 12 * pc) / 100;
            var part = Math.max(0, brut - 933.51);
            var net = brut - part * (0.1131 + 0.097 * 0.9825);
            out('r-pct', pc + ' %');
            out('r-brut', centimes(brut));
            out('r-net', centimes(net));"""
    return {
        "slug": "salaire-brut-net-alternance-apprentissage",
        "title": "Salaire apprenti 2026 : brut et net selon l'âge et l'année",
        "desc": "Salaire apprenti 2026 : de 504,09 € à 1 867,02 € brut selon l'âge et l'année. Net calculé avec l'exonération jusqu'à 50 % du SMIC, grille officielle complète.",
        "h1": "Salaire apprenti 2026 : brut et net",
        "crumb": "Salaire apprenti 2026",
        "widget_titre": "Salaire minimum de l'apprenti",
        "widget": widget([choix("w-age", "Âge", [("16", "Moins de 18 ans"), ("18", "18 à 20 ans"), ("21", "21 à 25 ans"), ("26", "26 ans et plus")], "18"),
                          choix("w-annee", "Année du contrat", [("0", "1re année"), ("1", "2e année"), ("2", "3e année")], "0")],
                         [("r-pct", "Part du SMIC"), ("r-brut", "Brut minimum"), ("r-net", "Net estimé")],
                         "Contrat conclu depuis le 1er mars 2025, hors salaire conventionnel plus favorable et hors mutuelle."),
        "js": js,
        "citable": f"En 2026, un apprenti perçoit au minimum de 27 % à 100 % du SMIC selon son âge et son année de contrat, soit de {e2(SMIC_EXACT * 0.27)} à {e2(SMIC_MENSUEL_BRUT)} brut par mois depuis le 1er juin 2026. Pour les contrats conclus depuis le 1er mars 2025, le salaire est exonéré de cotisations salariales et de CSG-CRDS jusqu'à 50 % du SMIC, soit {e2(APPRENTI_SEUIL_EXO)} : le net est égal au brut en dessous de ce seuil, et un apprenti de 26 ans payé au SMIC touche environ {e2(n_max)} net. Le salaire est exonéré d'impôt dans la limite du SMIC annuel. Un apprenti de 18 à 20 ans en première année perçoit ainsi au moins {e2(SMIC_EXACT * 0.43)} brut, sans aucune retenue hors mutuelle d'entreprise.",
        "corps": corps,
        "sources": [SRC_APPRENTI, SRC_APPRENTI_URSSAF, SRC_SMIC, SRC_TAUX],
        "faq": [
            ("Quel est le salaire net d'un apprenti de 18 ans en 2026 ?",
             f"En première année, un apprenti de 18 à 20 ans perçoit au minimum 43 % du SMIC, soit {e2(SMIC_EXACT * 0.43)} brut par mois. Ce montant étant inférieur au seuil d'exonération de {e2(APPRENTI_SEUIL_EXO)}, aucune cotisation salariale ni CSG-CRDS n'est retenue pour un contrat conclu depuis mars 2025 : le net est égal au brut, hors éventuelle mutuelle d'entreprise."),
            ("À partir de quel salaire un apprenti paie-t-il des cotisations ?",
             f"Pour les contrats conclus depuis le 1er mars 2025, les cotisations salariales et la CSG-CRDS ne portent que sur la part du salaire qui dépasse 50 % du SMIC, soit {e2(APPRENTI_SEUIL_EXO)} par mois en 2026. Un apprenti de 18 à 20 ans en deuxième année, payé {e2(SMIC_EXACT * 0.51)}, cotise donc seulement sur {e2(SMIC_EXACT * 0.51 - APPRENTI_SEUIL_EXO)}."),
            ("Le salaire d'un apprenti augmente-t-il avec le SMIC ?",
             f"Oui, automatiquement. La rémunération étant un pourcentage du SMIC, la revalorisation du 1er juin 2026 a relevé tous les minima de 2,41 % sans avenant au contrat. Un apprenti de 21 à 25 ans en première année est ainsi passé de {e2(SMIC_MENSUEL_JANVIER * 0.53)} à {e2(SMIC_EXACT * 0.53)} brut par mois. L'employeur peut toujours verser davantage que le minimum légal."),
            ("Que se passe-t-il quand l'apprenti change de tranche d'âge ?",
             "Le pourcentage applicable augmente dès le premier jour du mois qui suit l'anniversaire de l'apprenti, sans attendre la nouvelle année de contrat. Un apprenti qui fête ses 21 ans en cours de deuxième année passe ainsi de 51 % à 61 % du SMIC. Le passage à l'année suivante du contrat produit le même effet à sa date anniversaire."),
        ],
        "related": ["smic-brut-net-2026", "salaire-brut-net-stage", "salaire-brut-net-horaire", "salaire-net-imposable", "cout-employeur", "salaire-moyen-france"],
    }


def page_moyen():
    i = INSEE
    lignes_dist = [
        ["10 % les moins payés gagnent moins de (D1)", e(i["d1"])],
        ["Salaire médian (la moitié gagne moins)", e(i["median_net"])],
        ["Salaire moyen", e(i["moyen_net"])],
        ["10 % les mieux payés gagnent plus de (D9)", e(i["d9"])],
    ]
    lignes_csp = [
        ["Cadres", e(i["cadres"]), pct(i["cadres"] / i["moyen_net"] * 100 - 100, 0).replace("-", "−")],
        ["Professions intermédiaires", e(i["prof_inter"]), pct(i["prof_inter"] / i["moyen_net"] * 100 - 100, 0).replace("-", "−")],
        ["Ouvriers", e(i["ouvriers"]), pct(i["ouvriers"] / i["moyen_net"] * 100 - 100, 0).replace("-", "−")],
        ["Employés", e(i["employes"]), pct(i["employes"] / i["moyen_net"] * 100 - 100, 0).replace("-", "−")],
    ]
    for l in lignes_csp:
        if not l[2].startswith("−"):
            l[2] = "+" + l[2]
    corps = f"""
<h2>Salaire net moyen et médian dans le secteur privé</h2>
<p>La dernière étude annuelle de l'Insee sur les salaires du secteur privé porte sur l'année 2024. Les montants sont exprimés en <strong>net mensuel en équivalent temps plein</strong> (EQTP) : le salaire de chaque poste est ramené à ce qu'il serait pour un temps complet sur toute l'année, ce qui permet de comparer un temps partiel ou un CDD de six mois avec un CDI à temps plein.</p>
{table(["Repère (net mensuel EQTP, 2024)", "Montant"], lignes_dist)}
{note("Source : Insee Première n° 2079, parue le 23 octobre 2025. Le salaire brut moyen correspondant est de " + e(i["moyen_brut"]) + " par mois. Le champ inclut depuis cette édition les apprentis, les stagiaires et Mayotte : les chiffres ne se comparent pas directement à ceux des éditions précédentes.")}
<h2>Moyenne et médiane : pourquoi l'écart</h2>
<p>Le salaire moyen dépasse le médian de {e(i["moyen_net"] - i["median_net"])}, parce que les hauts salaires tirent la moyenne vers le haut sans déplacer la médiane. La médiane, {e(i["median_net"])} net, décrit mieux la situation d'un salarié ordinaire : la moitié des salariés du privé gagne moins, l'autre moitié davantage. Pour se situer, c'est donc à elle et aux déciles qu'il faut se comparer, pas à la moyenne.</p>
<h2>Salaire moyen par catégorie socioprofessionnelle</h2>
{table(["Catégorie (net mensuel EQTP, 2024)", "Salaire moyen", "Écart à la moyenne"], lignes_csp)}
{note("Source : Insee Première n° 2079. Les femmes gagnent en moyenne " + i["ecart_fh"] + " % de moins que les hommes en EQTP en 2024.")}
<h2>Comparer avec le SMIC 2026</h2>
<p>Le SMIC net 2026, {e2(SMIC_NET_MENSUEL_SP)} par mois depuis le 1er juin, est proche du premier décile mesuré en 2024 ({e(i["d1"])}). Les deux montants ne portent pas sur la même année : au rythme des éditions précédentes, les salaires de 2026 ne seront publiés par l'Insee que fin 2027. Comparer son propre net de 2026 aux repères de 2024 conduit donc à se surestimer légèrement, de l'ordre de la hausse générale des salaires intervenue entre-temps.</p>
<h2>Du net Insee au brut de votre contrat</h2>
<p>Le net publié par l'Insee est un net de cotisations et de contributions sociales, avant impôt sur le revenu : il se compare au net avant impôt de votre bulletin, pas au montant viré après prélèvement à la source. Avec les taux 2026 du régime général, un net de {e(i["median_net"])} correspond à environ {e(brut_pour_net(i["median_net"]))} brut par mois pour un non-cadre, et un net de {e(i["moyen_net"])} à environ {e(brut_pour_net(i["moyen_net"]))} brut.</p>
"""
    js = f"""
            var n = v('w-net');
            var reperes = [[{i['d1']}, 'sous le 1er décile'], [{i['median_net']}, 'entre le 1er décile et la médiane'], [{i['moyen_net']}, 'entre la médiane et la moyenne'], [{i['d9']}, 'entre la moyenne et le 9e décile']];
            var pos = 'au-dessus du 9e décile';
            for (var k = 0; k < reperes.length; k++) {{ if (n < reperes[k][0]) {{ pos = reperes[k][1]; break; }} }}
            out('r-pos', pos);
            out('r-median', Math.round(n / {i['median_net']} * 100) + ' %');
            out('r-brut', euros(calculerNetVersBrut(n, 'non-cadre', 1).brutMensuel));"""
    return {
        "slug": "salaire-moyen-france",
        "title": "Salaire moyen en France : 2 733 € net, médian 2 190 €",
        "desc": "Salaire moyen en France : 2 733 € net par mois en équivalent temps plein dans le privé, médian 2 190 € (Insee, 2024). Déciles, cadres, employés et ouvriers.",
        "h1": "Salaire moyen et médian en France",
        "crumb": "Salaire moyen en France",
        "widget_titre": "Situer votre salaire net",
        "widget": widget([champ("w-net", "Votre salaire net mensuel (temps plein)", "2000")],
                         [("r-pos", "Votre position (privé, 2024)"), ("r-median", "Par rapport à la médiane"), ("r-brut", "Brut correspondant 2026")]),
        "js": js,
        "citable": f"En 2024, un salarié du secteur privé gagne en moyenne {e(i['moyen_net'])} net par mois en équivalent temps plein, soit {e(i['moyen_brut'])} brut, selon l'Insee. Le salaire médian est nettement plus bas, {e(i['median_net'])} net : la moitié des salariés gagne moins. Les 10 % les moins payés touchent moins de {e(i['d1'])} net, les 10 % les mieux payés plus de {e(i['d9'])}. Un cadre gagne en moyenne {e(i['cadres'])} net, un employé {e(i['employes'])}, et les femmes {i['ecart_fh']} % de moins que les hommes. Ces montants portent sur 2024, dernière année publiée, et sont exprimés avant impôt sur le revenu : ils se comparent au net avant impôt d'un bulletin de paie à temps complet.",
        "corps": corps,
        "sources": [SRC_INSEE, SRC_SMIC, SRC_TAUX],
        "faq": [
            ("Quel est le salaire moyen en France ?",
             f"Selon l'Insee, le salaire net moyen dans le secteur privé est de {e(i['moyen_net'])} par mois en équivalent temps plein en 2024, ce qui correspond à {e(i['moyen_brut'])} brut. C'est le chiffre de la dernière étude annuelle de l'Insee sur le secteur privé, l'Insee Première n° 2079 d'octobre 2025. Le salaire médian, moins sensible aux très hauts revenus, est de {e(i['median_net'])} net."),
            ("Quelle différence entre salaire moyen et salaire médian ?",
             f"Le salaire moyen additionne tous les salaires et divise par le nombre de salariés : quelques très hautes rémunérations suffisent à le tirer vers le haut. Le salaire médian partage les salariés en deux groupes de même taille. En 2024, il vaut {e(i['median_net'])} net, soit {e(i['moyen_net'] - i['median_net'])} de moins que la moyenne : c'est le meilleur repère pour savoir si l'on est bien payé."),
            ("Les chiffres de l'Insee sont-ils avant ou après impôt ?",
             "Ils sont nets de cotisations et de contributions sociales, mais avant impôt sur le revenu. Ils se comparent donc au net avant impôt de votre bulletin de paie, et non au montant viré sur votre compte après le prélèvement à la source. Ils sont en outre exprimés en équivalent temps plein : un salarié à mi-temps doit doubler son net avant de se comparer."),
            ("Quel est le salaire moyen d'un cadre ?",
             f"En 2024, un cadre du secteur privé gagne en moyenne {e(i['cadres'])} net par mois en équivalent temps plein, selon l'Insee. C'est {e(i['cadres'] - i['moyen_net'])} de plus que la moyenne de l'ensemble des salariés. Les professions intermédiaires perçoivent {e(i['prof_inter'])}, les ouvriers {e(i['ouvriers'])} et les employés {e(i['employes'])}, catégorie la moins rémunérée."),
        ],
        "related": ["salaire-brut-net-cadre", "smic-brut-net-2026", "salaire-brut-net-annuel", "salaire-brut-net-non-cadre", "salaire-brut-net-horaire", "salaire-brut-net-fonction-publique"],
    }


def brut_pour_net(n):
    from calcul import calculer_net_vers_brut
    return calculer_net_vers_brut(n, "non-cadre")["brut_mensuel"]


TAUX_STAGE = 0.069 + 0.004 + TAUX_CSG_CRDS  # part excédentaire : vieillesse + CSG-CRDS


def net_stage(gratif, heures):
    exc = max(0, gratif - GRATIFICATION_HORAIRE * heures)
    return gratif - exc * TAUX_STAGE, exc


def page_stage():
    exemples = [(140, "février 2026 (exemple officiel)"), (154, "janvier 2026 (exemple officiel)"),
                (161, "mars 2026 (exemple officiel)"), (HEURES_MENSUELLES, "moyenne d'un mois à 35 h")]
    l1 = [[f"{fmt2(h).replace(',00', '')} h", lib, e2(h * GRATIFICATION_HORAIRE)] for h, lib in exemples]
    l2 = []
    for taux in (4.50, 5.00, 5.50, 6.00, 7.00, 8.00):
        g = arrondi(taux * HEURES_MENSUELLES, 2)
        n, exc = net_stage(g, HEURES_MENSUELLES)
        l2.append([e2(taux), e2(g), e2(exc), e2(n)])
    g6 = arrondi(6 * HEURES_MENSUELLES, 2)
    n6, exc6 = net_stage(g6, HEURES_MENSUELLES)
    corps = f"""
<h2>Gratification minimale 2026</h2>
<p>La gratification minimale est égale à 15 % du plafond horaire de la Sécurité sociale, fixé à {PSS_HORAIRE} € en 2026 : elle s'établit donc à <strong>{e2(GRATIFICATION_HORAIRE)} par heure de stage</strong> depuis le 1er janvier 2026. Elle se calcule sur les heures de présence effective, si bien que le montant change d'un mois à l'autre, sauf si l'organisme choisit de lisser la somme totale sur la durée du stage.</p>
{table(["Heures dans le mois", "Situation", "Gratification minimale"], l1)}
{note("Les trois premières lignes reprennent l'exemple officiel publié par l'Urssaf pour un stage du 1er janvier au 30 avril 2026. La dernière correspond à 35 heures par semaine en moyenne (151,67 heures).")}
<h2>Quand la gratification est-elle obligatoire ?</h2>
<p>Elle est due lorsque le stage dure plus de deux mois au cours d'une même année d'enseignement, soit plus de 44 jours à raison de 7 heures par jour, ou à partir de la 309e heure de présence, consécutive ou non. Elle est alors versée chaque mois dès le premier jour de stage. Un même stagiaire ne peut pas rester plus de six mois par année d'enseignement dans le même organisme. Une convention de branche peut prévoir un montant supérieur.</p>
<h2>Gratification brute et nette</h2>
<p>Jusqu'à {e2(GRATIFICATION_HORAIRE)} de l'heure, la gratification est entièrement exonérée de cotisations et de CSG-CRDS : <strong>le net est égal au brut</strong>. Au-delà, seule la part qui dépasse le seuil est soumise aux cotisations de Sécurité sociale, à la CSG et à la CRDS ; les cotisations de retraite complémentaire et d'assurance chômage ne sont pas dues, le stagiaire n'étant pas salarié.</p>
{table(["Taux horaire", "Gratification (151,67 h)", "Part au-dessus du seuil", "Net estimé"], l2)}
{note("Estimation : sur la part excédentaire, vieillesse salariale 7,30 % et CSG-CRDS 9,70 % sur 98,25 %, soit environ 16,8 %. Exemple : à 6 € de l'heure, " + e2(exc6) + " sont soumis et le stagiaire reçoit environ " + e2(n6) + ".")}
<h2>Impôt sur le revenu</h2>
<p>La gratification de stage est exonérée d'impôt sur le revenu dans la limite du montant annuel du SMIC. Un stage de six mois rémunéré au minimum légal reste très en dessous de cette limite : aucune somme n'est à déclarer comme imposable, ni pour le stagiaire, ni pour ses parents s'il est rattaché à leur foyer fiscal.</p>
"""
    js = """
            var h = v('w-heures'), t = v('w-taux');
            var g = Math.round(h * t * 100) / 100;
            var exc = Math.max(0, g - 4.50 * h);
            out('r-brut', centimes(g));
            out('r-exc', centimes(exc));
            out('r-net', centimes(g - exc * (0.073 + 0.097 * 0.9825)));"""
    return {
        "slug": "salaire-brut-net-stage",
        "title": "Gratification de stage 2026 : 4,50 € de l'heure, brut et net",
        "desc": "Gratification de stage 2026 : 4,50 € par heure minimum, soit environ 682 € pour un mois à 35 h. Net égal au brut jusqu'à ce seuil, calcul au-delà et exemples.",
        "h1": "Gratification de stage 2026 : brut et net",
        "crumb": "Gratification de stage 2026",
        "widget_titre": "Gratification du mois",
        "widget": widget([champ("w-heures", "Heures de présence dans le mois", "154"),
                          champ("w-taux", "Montant horaire (€)", "4,50")],
                         [("r-brut", "Gratification brute"), ("r-exc", "Part soumise à cotisations"), ("r-net", "Gratification nette")]),
        "js": js,
        "citable": f"En 2026, la gratification minimale d'un stagiaire est de {e2(GRATIFICATION_HORAIRE)} par heure de stage, soit 15 % du plafond horaire de la Sécurité sociale de {PSS_HORAIRE} €. Pour un mois à 35 heures par semaine, cela représente environ {e2(GRATIFICATION_HORAIRE * HEURES_MENSUELLES)}. Elle est obligatoire dès que le stage dépasse deux mois ou 308 heures dans l'année d'enseignement. Jusqu'à {e2(GRATIFICATION_HORAIRE)} de l'heure, elle est exonérée de toutes cotisations et de CSG-CRDS : le net est égal au brut. Elle est aussi exonérée d'impôt dans la limite du SMIC annuel. Au-delà du seuil horaire, seule la part excédentaire supporte la vieillesse de base, la CSG et la CRDS, soit environ 16,8 % de cette part : à 6 € de l'heure à temps plein, le stagiaire reçoit environ {e2(n6)} net pour {e2(g6)} brut.",
        "corps": corps,
        "sources": [SRC_STAGE, SRC_STAGE_URSSAF, SRC_PSS, SRC_TAUX],
        "faq": [
            ("Quel est le montant minimum de la gratification de stage en 2026 ?",
             f"Le minimum légal est de {e2(GRATIFICATION_HORAIRE)} par heure de stage effectuée depuis le 1er janvier 2026, soit 15 % du plafond horaire de la Sécurité sociale. Pour 154 heures de présence dans le mois, comme dans l'exemple officiel de janvier 2026, la gratification minimale atteint {e2(154 * GRATIFICATION_HORAIRE)}. Une convention de branche ou un accord étendu peut imposer un montant supérieur."),
            ("La gratification de stage est-elle nette ou brute ?",
             f"Jusqu'à {e2(GRATIFICATION_HORAIRE)} de l'heure, les deux se confondent : la gratification est exonérée de toutes cotisations et contributions sociales, CSG et CRDS comprises. Si l'organisme verse davantage, seule la part qui dépasse ce seuil supporte la vieillesse de base, la CSG et la CRDS, soit environ 16,8 % de cette part. À 6 € de l'heure à temps plein, le net est d'environ {e2(n6)}."),
            ("À partir de combien de temps un stage doit-il être payé ?",
             "La gratification devient obligatoire lorsque le stage dure plus de deux mois, consécutifs ou non, au cours d'une même année d'enseignement. Deux mois correspondent à 44 jours de présence à raison de 7 heures par jour : l'obligation commence donc à la 309e heure. Elle est alors due depuis le premier jour du stage, pas seulement à partir du troisième mois."),
            ("Un stagiaire paie-t-il des impôts sur sa gratification ?",
             "Non dans la très grande majorité des cas. La gratification est exonérée d'impôt sur le revenu dans la limite du montant annuel du SMIC, qui dépasse largement ce que rapporte un stage de six mois au minimum légal. Seule la fraction annuelle qui excéderait cette limite serait imposable, ce qui ne concerne que des gratifications très supérieures au minimum."),
        ],
        "related": ["salaire-brut-net-alternance-apprentissage", "smic-brut-net-2026", "salaire-brut-net-horaire", "salaire-net-imposable", "salaire-moyen-france", "salaire-brut-net-journalier"],
    }


def page_cadre():
    lignes = []
    for b in (3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 10000):
        rc = calculer_brut_vers_net(b, "cadre")
        rn = calculer_brut_vers_net(b, "non-cadre")
        lignes.append([e(b), e2(rc["net_avant_impot"]), e2(rn["net_avant_impot"]),
                       e2(rn["net_avant_impot"] - rc["net_avant_impot"]), pct(rc["taux_cotisations"])])
    r5 = calculer_brut_vers_net(5000, "cadre")
    det = [[k, e2(val)] for k, val in r5["detail_salariales"].items() if val > 0]
    corps = f"""
<h2>Salaire brut en net pour un cadre en 2026</h2>
{table(["Brut mensuel", "Net cadre", "Net non-cadre", "Écart", "Taux de cotisations"], lignes)}
{note("Net avant impôt, régime général 2026, hors mutuelle et prévoyance d'entreprise. Plafond de la Sécurité sociale : " + e(PSS_MENSUEL) + " par mois.")}
<h2>Ce qui distingue vraiment un cadre</h2>
<p>Depuis la fusion des régimes Agirc et Arrco, un cadre et un non-cadre cotisent aux mêmes taux de retraite complémentaire. À brut égal, la seule cotisation propre aux cadres est celle de l'<strong>Apec</strong>, 0,024 % du salaire dans la limite de quatre plafonds : moins de deux euros par mois pour un brut de {e(5000)}. Le statut joue en revanche sur la prévoyance, que l'employeur doit financer pour ses cadres, et sur le temps de travail, souvent organisé en forfait annuel de 218 jours.</p>
<p>Le taux de cotisations ne dépend donc pas du statut mais du niveau de salaire. Il reste proche de 20,8 % jusqu'au plafond de la Sécurité sociale, puis diminue lentement : au-delà de {e(PSS_MENSUEL)}, la cotisation vieillesse plafonnée de 6,90 % cesse de s'appliquer, tandis que la retraite complémentaire passe de 3,15 % à 8,64 % et que la contribution d'équilibre technique de 0,14 % s'ajoute sur la totalité du salaire.</p>
<h2>Détail pour un cadre à 5 000 € brut</h2>
{table(["Cotisation salariale", "Montant mensuel"], det, ["Total", e2(r5["total_salarial"])])}
{note("Net avant impôt : " + e2(r5["net_avant_impot"]) + ". La CSG et la CRDS portent sur 98,25 % du brut.")}
<h2>La règle des 25 % ne tient plus</h2>
<p>On lit souvent qu'un cadre perd 25 % de son brut en cotisations. Avec les taux 2026, le prélèvement réel est plus faible, autour de {pct(calculer_brut_vers_net(4000, 'cadre')['taux_cotisations'])} à {e(4000)} brut et {pct(calculer_brut_vers_net(8000, 'cadre')['taux_cotisations'])} à {e(8000)}. L'écart avec les fiches de paie réelles vient de la mutuelle et de la prévoyance, dont la part salariale dépend du contrat de l'entreprise et peut ajouter un à deux points.</p>
"""
    js = """
            var r = calculerBrutVersNet(v('w-brut'), 'cadre', 1);
            out('r-net', centimes(r.netAvantImpot));
            out('r-annuel', euros(r.netAvantImpot * 12));
            out('r-taux', r.tauxCotisationsSalariales.toFixed(1).replace('.', ',') + ' %');"""
    return {
        "slug": "salaire-brut-net-cadre",
        "title": "Salaire brut net cadre 2026 : taux réel et tableau de calcul",
        "desc": "Salaire brut net cadre 2026 : environ 20,8 % de cotisations jusqu'au plafond de 4 005 €, puis moins. Tableau de 3 000 à 10 000 € brut, détail des lignes.",
        "h1": "Salaire brut net cadre 2026",
        "crumb": "Salaire brut net cadre",
        "widget_titre": "Brut en net pour un cadre",
        "widget": widget([champ("w-brut", "Salaire brut mensuel (€)", "4000")],
                         [("r-net", "Net mensuel avant impôt"), ("r-annuel", "Net annuel (12 mois)"), ("r-taux", "Taux de cotisations")]),
        "js": js,
        "citable": f"En 2026, un cadre paie environ 20,8 % de cotisations salariales jusqu'au plafond mensuel de la Sécurité sociale de {e(PSS_MENSUEL)}, puis un peu moins au-delà. Un brut de {e(4000)} donne ainsi {e2(net(4000, 'cadre'))} net avant impôt, et un brut de {e(6000)} environ {e2(net(6000, 'cadre'))}. À brut égal, un cadre ne cotise que 0,024 % de plus qu'un non-cadre, au titre de l'Apec : l'écart réel entre les deux statuts tient à la prévoyance et à la mutuelle d'entreprise, pas aux cotisations légales. Au-delà du plafond, la vieillesse plafonnée cesse de s'appliquer tandis que la retraite complémentaire passe de 3,15 % à 8,64 % : le taux global baisse lentement, jusqu'à {pct(calculer_brut_vers_net(8000, 'cadre')['taux_cotisations'])} pour {e(8000)} brut.",
        "corps": corps,
        "sources": [SRC_TAUX, SRC_PSS, SRC_HS_URSSAF],
        "faq": [
            ("Combien gagne net un cadre payé 4 000 € brut ?",
             f"En 2026, un cadre payé {e(4000)} brut par mois perçoit environ {e2(net(4000, 'cadre'))} net avant impôt, hors mutuelle et prévoyance d'entreprise. Les cotisations salariales représentent alors {pct(calculer_brut_vers_net(4000, 'cadre')['taux_cotisations'])} du brut. Le prélèvement à la source s'applique ensuite, au taux transmis par l'administration fiscale."),
            ("Un cadre cotise-t-il plus qu'un non-cadre ?",
             f"Très peu. Les taux de retraite complémentaire, de CSG-CRDS et de vieillesse sont identiques pour les deux statuts. Seule la cotisation Apec de 0,024 % est propre aux cadres, soit moins d'un euro par mois pour {e(3000)} brut. Un cadre cotise davantage en montant parce qu'il gagne souvent plus, pas parce que ses taux sont plus élevés."),
            ("Pourquoi le taux de cotisations baisse-t-il au-delà de 4 005 € ?",
             f"Le plafond mensuel de la Sécurité sociale vaut {e(PSS_MENSUEL)} en 2026. Au-delà, la cotisation vieillesse plafonnée de 6,90 % ne s'applique plus, ce qui compense la hausse de la retraite complémentaire, qui passe de 3,15 % à 8,64 %, et l'ajout de la contribution d'équilibre technique. Le taux global diminue donc lentement à mesure que le salaire s'élève."),
            ("Le forfait jours change-t-il le salaire net d'un cadre ?",
             "Non, il change la façon de compter le temps de travail, pas le calcul des cotisations. Un cadre au forfait annuel travaille au plus 218 jours par an et ne perçoit pas d'heures supplémentaires. S'il renonce à des jours de repos après avoir travaillé au moins 218 jours, la rémunération de ces jours bénéficie de la réduction de cotisations salariales des heures supplémentaires."),
        ],
        "related": ["salaire-brut-net-non-cadre", "salaire-moyen-france", "salaire-brut-net-annuel", "salaire-net-imposable", "cout-employeur", "salaire-brut-net-journalier"],
    }


def page_horaire():
    lignes = []
    for t in (SMIC_HORAIRE, 13, 14, 15, 16, 18, 20, 22, 25, 30):
        brut = t * HEURES_MENSUELLES
        n = net(brut)
        lignes.append([e2(t), e2(n / HEURES_MENSUELLES), e2(brut), e2(n)])
    corps = f"""
<h2>Taux horaire brut en net : tableau 2026</h2>
{table(["Brut de l'heure", "Net de l'heure", "Brut mensuel (151,67 h)", "Net mensuel"], lignes)}
{note("Non-cadre, temps plein de 35 heures par semaine, cotisations salariales 2026, hors mutuelle d'entreprise. La première ligne correspond au SMIC horaire en vigueur depuis le 1er juin 2026.")}
<h2>Pourquoi 151,67 heures par mois</h2>
<p>Un temps plein de 35 heures par semaine représente 35 × 52 ÷ 12 = <strong>151,67 heures par mois</strong>. C'est ce nombre qui figure sur les bulletins de paie et qui sert à passer d'un taux horaire à un salaire mensuel : 15 € brut de l'heure donnent ainsi {e2(15 * HEURES_MENSUELLES)} brut par mois, quel que soit le nombre de jours ouvrés du mois. Le salaire est dit mensualisé : il ne varie pas entre février et un mois de 31 jours.</p>
<h2>Le rapport net sur brut est presque constant</h2>
<p>Jusqu'au plafond de la Sécurité sociale, {e(PSS_MENSUEL)} par mois en 2026, soit environ {e2(PSS_MENSUEL / HEURES_MENSUELLES)} de l'heure à temps plein, les cotisations salariales représentent environ 20,8 % du brut : le net de l'heure vaut donc à peu près 79,2 % du brut de l'heure. Au-delà du plafond, la part prélevée diminue légèrement. Le statut cadre ne change presque rien à ce rapport.</p>
<h2>Temps partiel et heures supplémentaires</h2>
<p>Pour un temps partiel, le net horaire est le même que pour un temps plein au même taux : seul le nombre d'heures change. Les heures supplémentaires, majorées de 25 % puis de 50 %, rapportent davantage par heure, car elles bénéficient d'une réduction de cotisations salariales de 11,31 % : une heure supplémentaire au SMIC majorée de 25 % rapporte environ {e2(SMIC_HORAIRE * 1.25 * (1 - TAUX_RETRAITE_T1 - TAUX_CSG_CRDS + TAUX_REDUCTION_HS))} net, contre {e2(SMIC_NET_HORAIRE_SP)} pour une heure normale.</p>
"""
    js = """
            var t = v('w-taux'), h = v('w-heures');
            var brut = t * h * 52 / 12;
            var r = calculerBrutVersNet(brut, document.getElementById('w-statut').value, 1);
            out('r-heure', centimes(h > 0 ? r.netAvantImpot / (h * 52 / 12) : 0));
            out('r-mois', centimes(r.netAvantImpot));
            out('r-brut', centimes(brut));"""
    return {
        "slug": "salaire-brut-net-horaire",
        "title": "Salaire brut net horaire 2026 : du taux horaire au net",
        "desc": "Salaire brut net horaire 2026 : 12,31 € brut font 9,74 € net. Tableau du SMIC à 30 € de l'heure avec le salaire mensuel sur 151,67 h, et calcul pour vos heures.",
        "h1": "Salaire brut net horaire 2026",
        "crumb": "Salaire brut net horaire",
        "widget_titre": "Taux horaire brut en net",
        "widget": widget([champ("w-taux", "Taux horaire brut (€)", "15"),
                          champ("w-heures", "Heures par semaine", "35"),
                          choix("w-statut", "Statut", STATUT, "non-cadre")],
                         [("r-heure", "Net de l'heure"), ("r-mois", "Net mensuel"), ("r-brut", "Brut mensuel")]),
        "js": js,
        "citable": f"En 2026, un salaire horaire brut se convertit en net en retirant environ 20,8 % de cotisations salariales jusqu'au plafond de la Sécurité sociale. Le SMIC horaire de {e2(SMIC_HORAIRE)} brut donne ainsi {e2(SMIC_NET_HORAIRE_SP)} net, et un taux de 15 € brut environ {e2(net(15 * HEURES_MENSUELLES) / HEURES_MENSUELLES)} net. Pour obtenir le salaire mensuel, on multiplie le taux horaire par 151,67 heures, soit 35 heures par semaine sur 52 semaines divisées par 12 mois : 15 € de l'heure font {e2(15 * HEURES_MENSUELLES)} brut et {e2(net(15 * HEURES_MENSUELLES))} net par mois. Au-delà du plafond de la Sécurité sociale, soit environ {e2(PSS_MENSUEL / HEURES_MENSUELLES)} de l'heure à temps plein, la part prélevée diminue légèrement. Le statut cadre n'ajoute que 0,024 % de cotisation Apec.",
        "corps": corps,
        "sources": [SRC_SMIC, SRC_TAUX, SRC_PSS, SRC_HS_URSSAF],
        "faq": [
            ("Comment passer d'un salaire horaire brut au net ?",
             f"Jusqu'au plafond de la Sécurité sociale, multipliez le taux horaire brut par environ 0,792 : les cotisations salariales et la CSG-CRDS représentent près de 20,8 % du brut en 2026. Un taux de 14 € brut donne ainsi environ {e2(net(14 * HEURES_MENSUELLES) / HEURES_MENSUELLES)} net de l'heure. La mutuelle d'entreprise, propre à chaque contrat, réduit encore légèrement ce montant."),
            ("Quel est le SMIC horaire net en 2026 ?",
             f"Depuis le 1er juin 2026, le SMIC horaire est de {e2(SMIC_HORAIRE)} brut, soit environ {e2(SMIC_NET_HORAIRE_SP)} net selon service-public.gouv.fr. Du 1er janvier au 31 mai 2026, il était de {e2(SMIC_HORAIRE_JANVIER)} brut. Ce taux horaire s'applique à tous les salariés, à temps plein comme à temps partiel."),
            ("Comment calculer un salaire mensuel à partir du taux horaire ?",
             f"Multipliez le taux horaire par le nombre d'heures hebdomadaires, puis par 52 semaines, et divisez par 12 mois. Pour 35 heures par semaine, cela fait 151,67 heures par mois : 16 € de l'heure donnent {e2(16 * HEURES_MENSUELLES)} brut mensuel. Pour 28 heures par semaine, le même taux donne {e2(16 * 28 * 52 / 12)} brut."),
            ("Le net horaire est-il le même pour un cadre ?",
             "Presque. À taux horaire égal, un cadre cotise seulement 0,024 % de plus au titre de l'Apec, ce qui représente quelques centimes par mois. La différence réelle entre les deux bulletins tient à la mutuelle et à la prévoyance d'entreprise, souvent plus étendues pour les cadres, dont la part salariale dépend du contrat."),
        ],
        "related": ["smic-brut-net-2026", "salaire-brut-net-journalier", "heures-supplementaires-brut-net", "salaire-brut-net-annuel", "salaire-brut-net-non-cadre", "salaire-brut-net-stage"],
    }


def gain_hs(brut, h25, h50=0):
    t = brut / HEURES_MENSUELLES
    hs = h25 * t * 1.25 + h50 * t * 1.5
    gain = net(brut + hs) + hs * TAUX_REDUCTION_HS - net(brut)
    return t, hs, gain


def page_hs():
    h4 = 4 * 52 / 12
    lignes = []
    for b in (SMIC_MENSUEL_BRUT, 2000, 2500, 3000, 3500):
        t, hs, gain = gain_hs(b, h4)
        lignes.append([e2(b), e2(t), e2(hs), e2(gain), e2(gain / h4)])
    t8, hs8, gain8 = gain_hs(2000, 8 * 52 / 12, 2 * 52 / 12)
    corps = f"""
<h2>Combien rapportent les heures supplémentaires en net</h2>
<p>Le tableau ci-dessous calcule le gain net mensuel d'un salarié qui travaille <strong>39 heures par semaine</strong> au lieu de 35, soit 17,33 heures supplémentaires par mois majorées de 25 %. Le gain tient compte de la réduction de cotisations salariales de 11,31 % appliquée à la rémunération des heures supplémentaires.</p>
{table(["Brut de base (35 h)", "Taux horaire", "Heures sup. brutes", "Gain net mensuel", "Net par heure sup."], lignes)}
{note("Non-cadre, taux légaux de majoration, cotisations 2026, hors mutuelle. Exemple : avec 8 heures à 25 % et 2 heures à 50 % par semaine sur un brut de 2 000 €, les heures supplémentaires représentent " + e2(hs8) + " brut et rapportent " + e2(gain8) + " net par mois.")}
<h2>Les majorations légales</h2>
<p>Sauf taux différent prévu par la convention ou un accord collectif, les heures effectuées au-delà de 35 heures par semaine sont majorées de <strong>25 % de la 36e à la 43e heure</strong>, puis de <strong>50 % à partir de la 44e heure</strong>. Le contingent annuel est de 220 heures par salarié en l'absence d'accord ; au-delà, chaque heure ouvre en outre droit à une contrepartie obligatoire en repos.</p>
<h2>Moins de cotisations, pas d'impôt</h2>
<ul>
<li><strong>Cotisations salariales</strong> : la rémunération des heures supplémentaires, majoration comprise, bénéficie d'une réduction égale aux cotisations vieillesse et retraite complémentaire, dans la limite de 11,31 %. Seules la CSG et la CRDS restent dues, soit environ 9,5 % de l'heure payée.</li>
<li><strong>Impôt sur le revenu</strong> : les heures supplémentaires sont exonérées dans la limite de {e(PLAFOND_IR_HS)} nets par an. Elles n'entrent pas dans le <a href="/salaire-net-imposable/">net imposable</a> du bulletin, et donc pas dans l'assiette du prélèvement à la source.</li>
<li><strong>Côté employeur</strong> : une déduction forfaitaire de 1,50 € par heure supplémentaire dans les entreprises de moins de 20 salariés, et de 0,50 € dans celles de 20 salariés et plus.</li>
</ul>
<h2>Exemple officiel de l'Urssaf</h2>
<p>Un salarié à temps plein payé 12,50 € de l'heure effectue 10 heures supplémentaires en janvier 2026 au taux légal. Son brut se compose de 151,67 heures à 12,50 €, soit 1 895,88 €, et de 10 × 12,50 € × 125 % = 156,25 €. La réduction de cotisations salariales vaut 156,25 € × 11,31 % = 17,67 €.</p>
"""
    js = """
            var brut = v('w-brut'), h25 = v('w-h25'), h50 = v('w-h50');
            var t = brut / 151.67;
            var hs = h25 * t * 1.25 + h50 * t * 1.5;
            var base = calculerBrutVersNet(brut, 'non-cadre', 1).netAvantImpot;
            var total = calculerBrutVersNet(brut + hs, 'non-cadre', 1).netAvantImpot + hs * 0.1131;
            out('r-hs', centimes(hs));
            out('r-gain', centimes(total - base));
            out('r-total', centimes(total));"""
    return {
        "slug": "heures-supplementaires-brut-net",
        "title": "Heures supplémentaires brut net 2026 : calcul et majorations",
        "desc": "Heures supplémentaires brut net 2026 : majoration de 25 % puis 50 %, cotisations réduites de 11,31 % et exonération d'impôt jusqu'à 7 500 €. Calcul du gain net.",
        "h1": "Heures supplémentaires : du brut au net en 2026",
        "crumb": "Heures supplémentaires brut net",
        "widget_titre": "Calcul des heures supplémentaires",
        "widget": widget([champ("w-brut", "Salaire brut mensuel (35 h)", "2000"),
                          champ("w-h25", "Heures sup. à 25 % dans le mois", "17,33"),
                          champ("w-h50", "Heures sup. à 50 % dans le mois", "0")],
                         [("r-hs", "Heures sup. brutes"), ("r-gain", "Gain net"), ("r-total", "Net total du mois")],
                         "Non-cadre, taux légaux. 17,33 heures par mois correspondent à 39 heures par semaine."),
        "js": js,
        "citable": f"En 2026, une heure supplémentaire est payée au moins 25 % de plus de la 36e à la 43e heure de la semaine, puis 50 % au-delà. Sa rémunération bénéficie d'une réduction de cotisations salariales de 11,31 % et d'une exonération d'impôt sur le revenu jusqu'à {e(PLAFOND_IR_HS)} nets par an : seules la CSG et la CRDS sont prélevées. Pour un salarié à 2 000 € brut qui passe de 35 à 39 heures par semaine, les 17,33 heures supplémentaires du mois rapportent environ {e2(gain_hs(2000, 4 * 52 / 12)[2])} net. L'employeur bénéficie de son côté d'une déduction forfaitaire de 1,50 € par heure supplémentaire dans les entreprises de moins de 20 salariés, et de 0,50 € au-delà. Le contingent annuel est de 220 heures en l'absence d'accord collectif.",
        "corps": corps,
        "sources": [SRC_HS_SP, SRC_HS_URSSAF, SRC_HS_PATRONAL, SRC_TAUX],
        "faq": [
            ("Comment calculer le net d'une heure supplémentaire ?",
             f"Prenez le taux horaire brut, appliquez la majoration de 25 % ou 50 %, puis retirez seulement la CSG et la CRDS, soit environ 9,5 %, puisque la réduction de 11,31 % efface les cotisations vieillesse et retraite. Au SMIC, une heure majorée de 25 % vaut {e2(SMIC_HORAIRE * 1.25)} brut et rapporte environ {e2(SMIC_HORAIRE * 1.25 * (1 - TAUX_RETRAITE_T1 - TAUX_CSG_CRDS + TAUX_REDUCTION_HS))} net."),
            ("Les heures supplémentaires sont-elles imposables ?",
             f"Elles sont exonérées d'impôt sur le revenu dans la limite de {e(PLAFOND_IR_HS)} nets par an et par salarié. Cette part n'entre pas dans le net imposable du bulletin, ce qui réduit aussi le prélèvement à la source du mois. Au-delà de ce plafond annuel, les heures supplémentaires redeviennent imposables comme le reste du salaire."),
            ("Quelle différence entre heures supplémentaires et complémentaires ?",
             "Les heures supplémentaires concernent les salariés à temps plein, au-delà de 35 heures par semaine. Les heures complémentaires concernent les salariés à temps partiel, au-delà de la durée prévue au contrat : elles sont majorées de 10 % dans la limite du dixième de cette durée, puis de 25 %. Les deux bénéficient de la réduction de cotisations salariales."),
            ("Combien d'heures supplémentaires peut-on faire par an ?",
             "En l'absence d'accord collectif fixant un autre chiffre, le contingent annuel est de 220 heures par salarié. Les heures effectuées au-delà restent possibles mais ouvrent droit à une contrepartie obligatoire en repos. Toutes, dans le contingent ou au-delà, sont majorées et bénéficient de la réduction de cotisations salariales et de l'exonération d'impôt dans la limite annuelle."),
        ],
        "related": ["salaire-brut-net-horaire", "salaire-net-imposable", "smic-brut-net-2026", "cout-employeur", "salaire-brut-net-non-cadre", "salaire-brut-net-annuel"],
    }


def page_annuel():
    lignes = []
    for a in (SMIC_BRUT_ANNUEL_SP, 25000, 28000, 30000, 35000, 40000, 45000, 50000, 60000, 70000, 80000, 100000):
        nc = net(a / 12) * 12
        c = net(a / 12, "cadre") * 12
        lignes.append([e(a), e(nc), e(c), e(nc / 12), e(nc / 13)])
    corps = f"""
<h2>Brut annuel en net : tableau 2026</h2>
{table(["Brut annuel", "Net annuel non-cadre", "Net annuel cadre", "Net mensuel sur 12 mois", "Net mensuel sur 13 mois"], lignes)}
{note("Net avant impôt, cotisations 2026, hors mutuelle et prévoyance d'entreprise. La première ligne correspond au SMIC annuel brut publié par service-public.gouv.fr. Plafond annuel de la Sécurité sociale : " + e(48060) + ".")}
<h2>Douze ou treize mois : le net annuel ne change pas</h2>
<p>Un même brut annuel peut être versé en douze mensualités ou en treize, avec un treizième mois en fin d'année. Le net annuel est pratiquement identique dans les deux cas, parce que les cotisations plafonnées sont régularisées sur l'année : seul le net de chaque mois diffère. Un brut annuel de {e(35000)} donne ainsi {e(net(35000 / 12) * 12)} net sur l'année, soit {e(net(35000 / 12))} par mois sur douze mois ou {e(net(35000 / 12) * 12 / 13)} par mois sur treize.</p>
<h2>Annoncer un salaire annuel brut</h2>
<p>Les offres d'emploi et les contrats de cadres expriment souvent la rémunération en brut annuel. Pour comparer deux offres, ramenez-les au net annuel, puis vérifiez sur combien de mois le salaire est versé et si une part variable est incluse : une part variable n'est versée que si les objectifs sont atteints, et elle supporte les mêmes cotisations que le fixe. Le statut cadre ou non-cadre ne change presque rien au net, comme le montre l'écart minime entre les deux colonnes du tableau.</p>
<h2>Après l'impôt</h2>
<p>Le net annuel affiché est avant impôt sur le revenu. Pour estimer ce qui reste après le prélèvement à la source, il faut partir du <a href="/salaire-net-imposable/">net imposable</a>, qui dépasse le net versé de la CSG non déductible et de la CRDS, puis appliquer le barème et la situation du foyer : notre <a href="/simulateur-impot-sur-le-revenu/">simulateur d'impôt</a> fait ce calcul.</p>
"""
    js = """
            var a = v('w-annuel'), mois = parseInt(document.getElementById('w-mois').value);
            var r = calculerBrutVersNet(a / 12, document.getElementById('w-statut').value, 1);
            out('r-annuel', euros(r.netAvantImpot * 12));
            out('r-mois', euros(r.netAvantImpot * 12 / mois));
            out('r-brut-mois', euros(a / mois));"""
    return {
        "slug": "salaire-brut-net-annuel",
        "title": "Salaire brut annuel en net 2026 : tableau et calcul",
        "desc": f"Salaire brut annuel en net 2026 : 30 000 € brut font environ {e(net(2500) * 12)} net par an. Tableau de 22 404 à 100 000 € brut, cadre ou non, versé sur 12 ou 13 mois.",
        "h1": "Salaire brut annuel en net 2026",
        "crumb": "Brut annuel en net",
        "widget_titre": "Brut annuel en net",
        "widget": widget([champ("w-annuel", "Salaire brut annuel (€)", "35000"),
                          choix("w-statut", "Statut", STATUT, "non-cadre"),
                          choix("w-mois", "Versé sur", [("12", "12 mois"), ("13", "13 mois")], "12")],
                         [("r-annuel", "Net annuel"), ("r-mois", "Net par mois"), ("r-brut-mois", "Brut par mois")]),
        "js": js,
        "citable": f"En 2026, un salaire brut annuel se convertit en net en retirant environ 20,8 % de cotisations salariales jusqu'au plafond annuel de la Sécurité sociale de {e(48060)}. Un brut annuel de {e(30000)} donne ainsi environ {e(net(2500) * 12)} net par an, soit {e(net(2500))} par mois sur douze mois, et {e(50000)} brut environ {e(net(50000 / 12) * 12)} net. Le net annuel est le même que le salaire soit versé sur douze ou treize mois ; seul le montant mensuel change. Au-delà du plafond, le taux de cotisations baisse lentement, car la vieillesse plafonnée cesse de s'appliquer. Le statut cadre ne change presque rien : à {e(50000)} brut, l'écart annuel entre cadre et non-cadre est de {e(12 * (net(50000 / 12) - net(50000 / 12, 'cadre')))}.",
        "corps": corps,
        "sources": [SRC_TAUX, SRC_PSS, SRC_SMIC],
        "faq": [
            ("Combien font 30 000 € brut par an en net ?",
             f"En 2026, un salaire de {e(30000)} brut par an donne environ {e(net(2500) * 12)} net avant impôt pour un non-cadre, soit {e(net(2500))} par mois sur douze mois ou {e(net(2500) * 12 / 13)} sur treize mois. Le calcul exclut la mutuelle d'entreprise, dont la part salariale réduit encore le net de quelques dizaines d'euros par mois."),
            ("Comment convertir un brut annuel en net rapidement ?",
             f"Jusqu'à {e(48060)} brut par an, plafond de la Sécurité sociale 2026, multipliez le brut annuel par 0,792 : les cotisations salariales représentent environ 20,8 %. Au-delà, le coefficient augmente légèrement, car la cotisation vieillesse plafonnée cesse de s'appliquer. Pour un résultat exact, utilisez le calculateur de cette page, qui applique chaque taux à sa propre assiette."),
            ("Un treizième mois change-t-il le salaire annuel net ?",
             "Pas si le brut annuel reste le même. Un treizième mois répartit autrement une même rémunération : douze mensualités un peu plus faibles et un versement supplémentaire, souvent en décembre. Le net annuel ne bouge pratiquement pas. En revanche, un treizième mois ajouté à douze mensualités inchangées augmente bien le brut annuel, et donc le net."),
            ("Le salaire annuel affiché dans une offre est-il brut ou net ?",
             "En France, il est presque toujours exprimé en brut annuel, part variable parfois comprise. Vérifiez trois points avant de comparer : le nombre de mois de versement, la présence d'une part variable conditionnée à des objectifs, et l'existence d'avantages comme l'intéressement ou les titres-restaurant, qui ne figurent pas dans le brut annoncé."),
        ],
        "related": ["salaire-brut-net-cadre", "salaire-moyen-france", "salaire-net-imposable", "salaire-brut-net-horaire", "salaire-brut-net-non-cadre", "salaire-brut-net-journalier"],
    }


def page_imposable():
    lignes = []
    for b in (SMIC_MENSUEL_BRUT, 2000, 2500, 3000, 4000, 5000):
        r = calculer_brut_vers_net(b, "non-cadre")
        lignes.append([e2(b), e2(r["net_avant_impot"]), e2(r["net_imposable"] - r["net_avant_impot"]), e2(r["net_imposable"])])
    r25 = calculer_brut_vers_net(2500, "non-cadre")
    corps = f"""
<h2>Net imposable et net à payer en 2026</h2>
{table(["Brut mensuel", "Net avant impôt", "CSG non déductible et CRDS", "Net imposable"], lignes)}
{note("Non-cadre, cotisations 2026, sans mutuelle d'entreprise ni heures supplémentaires. CSG non déductible 2,40 % et CRDS 0,50 %, toutes deux sur 98,25 % du brut (Urssaf).")}
<h2>Pourquoi le net imposable dépasse le net versé</h2>
<p>Sur les 9,20 % de CSG prélevés sur le salaire, 6,80 % sont déductibles du revenu imposable et 2,40 % ne le sont pas. La CRDS, 0,50 %, ne l'est pas non plus. Ces 2,90 %, calculés sur 98,25 % du brut, ont été retenus sur votre salaire mais restent soumis à l'impôt : ils s'ajoutent donc au net versé pour former le net imposable. À {e(2500)} brut, cela représente {e2(r25["net_imposable"] - r25["net_avant_impot"])} par mois.</p>
<h2>Ce qui s'y ajoute et ce qui en sort</h2>
<ul>
<li><strong>La part patronale de la mutuelle</strong> s'ajoute au net imposable alors qu'elle n'est jamais versée au salarié. Si votre employeur finance 30 € de mutuelle par mois, votre net imposable augmente de 30 €.</li>
<li><strong>Les heures supplémentaires</strong> en sortent, dans la limite de {e(PLAFOND_IR_HS)} nets par an : elles sont exonérées d'impôt sur le revenu.</li>
<li><strong>Le salaire d'un apprenti et la gratification d'un stagiaire</strong> en sortent dans la limite du montant annuel du SMIC.</li>
<li><strong>Les avantages en nature</strong>, comme un véhicule de fonction utilisé à titre privé, s'y ajoutent pour leur valeur.</li>
</ul>
<h2>Le lien avec le prélèvement à la source</h2>
<p>Le taux de prélèvement à la source transmis par l'administration s'applique chaque mois au net imposable, et non au net versé. Le cumul annuel figurant sur le bulletin de décembre est le montant que l'administration reprend dans la déclaration de revenus préremplie : c'est lui qu'il faut contrôler au printemps, avant la déduction pour frais professionnels, appliquée ensuite par l'administration.</p>
"""
    js = """
            var r = calculerBrutVersNet(v('w-brut'), document.getElementById('w-statut').value, 1);
            var imp = r.netImposableMensuel + v('w-mutuelle');
            out('r-net', centimes(r.netAvantImpot));
            out('r-imp', centimes(imp));
            out('r-annuel', euros(imp * 12));"""
    return {
        "slug": "salaire-net-imposable",
        "title": "Salaire net imposable 2026 : calcul depuis le brut",
        "desc": "Salaire net imposable 2026 : net versé plus 2,40 % de CSG non déductible et 0,50 % de CRDS sur 98,25 % du brut. Tableau, part patronale de mutuelle, heures sup.",
        "h1": "Salaire net imposable 2026",
        "crumb": "Salaire net imposable",
        "widget_titre": "Calcul du net imposable",
        "widget": widget([champ("w-brut", "Salaire brut mensuel (€)", "2500"),
                          choix("w-statut", "Statut", STATUT, "non-cadre"),
                          champ("w-mutuelle", "Part patronale de mutuelle (€ par mois)", "0")],
                         [("r-net", "Net avant impôt"), ("r-imp", "Net imposable mensuel"), ("r-annuel", "Net imposable annuel")]),
        "js": js,
        "citable": f"Le salaire net imposable est le net versé auquel on rajoute la part de CSG non déductible, 2,40 %, et la CRDS, 0,50 %, calculées sur 98,25 % du brut, ainsi que la part patronale de la mutuelle. En 2026, un brut de {e(2500)} donne {e2(r25['net_avant_impot'])} net avant impôt et {e2(r25['net_imposable'])} net imposable. C'est sur ce montant que s'applique le taux du prélèvement à la source, et son cumul annuel est repris dans la déclaration préremplie. Les heures supplémentaires en sont exclues jusqu'à {e(PLAFOND_IR_HS)} nets par an. Pour {e(3000)} brut, l'écart entre net imposable et net versé atteint {e2(calculer_brut_vers_net(3000, 'non-cadre')['net_imposable'] - net(3000))} par mois hors mutuelle, un écart que l'on retrouve dans la déclaration de revenus préremplie.",
        "corps": corps,
        "sources": [SRC_TAUX, SRC_HS_SP, SRC_APPRENTI, SRC_STAGE],
        "faq": [
            ("Quelle différence entre net à payer et net imposable ?",
             "Le net à payer est la somme réellement versée sur votre compte, après cotisations et prélèvement à la source. Le net imposable est la base de l'impôt : il ajoute au net avant impôt la CSG non déductible et la CRDS, ainsi que la part patronale de la mutuelle, et il exclut les heures supplémentaires exonérées. Il est donc généralement plus élevé que le net versé."),
            ("Comment calculer le net imposable à partir du brut ?",
             f"Calculez d'abord le net avant impôt, puis ajoutez 2,90 % de 98,25 % du brut, qui correspondent à la CSG non déductible et à la CRDS. Ajoutez enfin la part patronale de la mutuelle, si votre employeur en finance une. Pour {e(3000)} brut en 2026, le net imposable atteint {e2(calculer_brut_vers_net(3000, 'non-cadre')['net_imposable'])} hors mutuelle."),
            ("Où trouver le net imposable sur la fiche de paie ?",
             "Il figure en bas du bulletin, souvent sous la mention « net imposable » ou « montant net imposable », à côté du taux et du montant du prélèvement à la source. Le bulletin de décembre indique aussi le cumul annuel, que l'administration fiscale reprend dans la déclaration de revenus préremplie du printemps suivant. Comparez ces deux montants avant de valider votre déclaration."),
            ("Pourquoi la mutuelle augmente-t-elle le net imposable ?",
             "La part de la complémentaire santé financée par l'employeur est considérée comme un complément de rémunération. Elle n'est pas versée au salarié, mais elle s'ajoute à son revenu imposable. C'est pourquoi le net imposable d'un salarié couvert par une mutuelle d'entreprise dépasse celui d'un salarié au même brut sans mutuelle collective."),
        ],
        "related": ["heures-supplementaires-brut-net", "salaire-brut-net-annuel", "salaire-brut-net-cadre", "salaire-brut-net-non-cadre", "salaire-brut-net-alsace-moselle", "salaire-brut-net-alternance-apprentissage"],
    }


def calcul_fp(im, primes=0.0):
    traitement = math.floor(im * POINT_ANNUEL_IM100 / 12) / 100  # tronqué au centime, comme service-public
    diff = max(0, SMIC_MENSUEL_BRUT - traitement)
    pension = traitement * TAUX_PENSION_CIVILE
    rafp = min(primes, 0.2 * traitement) * TAUX_RAFP
    csg = (traitement + diff + primes) * TAUX_CSG_CRDS
    brut = traitement + diff + primes
    return {"traitement": traitement, "diff": diff, "pension": pension, "rafp": rafp, "csg": csg,
            "brut": brut, "net": brut - pension - rafp - csg}


def page_fp():
    lignes = []
    for im in (366, 380, 400, 450, 500, 550, 600, 700, 800):
        r = calcul_fp(im)
        lignes.append([str(im), e2(r["traitement"]), e2(r["diff"]) if r["diff"] else "–", e2(r["pension"]), e2(r["csg"]), e2(r["net"])])
    ex = calcul_fp(500, 400)
    seuil = SMIC_MENSUEL_BRUT / (POINT_ANNUEL_IM100 / 1200)
    corps = f"""
<h2>Traitement brut et net selon l'indice majoré</h2>
<p>Le traitement indiciaire brut d'un fonctionnaire est égal à son indice majoré multiplié par la valeur du point. Celle-ci est fixée à {e2(POINT_ANNUEL_IM100)} par an pour l'indice majoré 100 depuis le 1er juillet 2023. Concrètement : <strong>traitement mensuel = indice majoré × {fmt2(POINT_ANNUEL_IM100)} ÷ 1 200</strong>.</p>
{table(["Indice majoré", "Traitement brut", "Indemnité différentielle", "Retenue pension 11,10 %", "CSG et CRDS", "Net sans primes"], lignes)}
{note("Fonctionnaire à temps complet, sans primes, ni indemnité de résidence, ni supplément familial, ni cotisation de complémentaire santé. Valeur du point et minimum de traitement : service-public.gouv.fr, page vérifiée le 1er juin 2026.")}
<h2>Le plancher du SMIC</h2>
<p>L'indice majoré minimum est 366, soit un traitement de {e2(calcul_fp(366)['traitement'])} brut par mois, inférieur au SMIC de {e2(SMIC_MENSUEL_BRUT)} en vigueur depuis le 1er juin 2026. Une <strong>indemnité différentielle</strong> complète alors la rémunération jusqu'au SMIC brut. Avec la valeur actuelle du point, tous les indices inférieurs à {int(seuil) + 1} en bénéficient. Pour un fonctionnaire, cette indemnité n'est pas soumise à la retenue pour pension, mais elle supporte la CSG et la CRDS.</p>
<h2>Les retenues sur le salaire d'un fonctionnaire</h2>
<ul>
<li><strong>Retenue pour pension civile</strong> : 11,10 % du traitement indiciaire brut, taux en vigueur depuis le 1er janvier 2020. Elle ne porte pas sur les primes.</li>
<li><strong>Retraite additionnelle de la fonction publique (RAFP)</strong> : 5 % à la charge de l'agent sur les primes et indemnités, dans la limite de 20 % du traitement indiciaire brut.</li>
<li><strong>CSG et CRDS</strong> : 9,70 % sur 98,25 % de l'ensemble de la rémunération, traitement et primes compris.</li>
</ul>
<p>Il n'y a ni cotisation chômage ni retraite complémentaire Agirc-Arrco : c'est pourquoi un fonctionnaire sans primes conserve un net proche de 79,4 % de son traitement, un taux voisin de celui d'un salarié du privé.</p>
<h2>Exemple avec primes</h2>
<p>Un agent à l'indice majoré 500 perçoit {e2(ex["traitement"])} de traitement brut et 400 € de primes. Il supporte {e2(ex["pension"])} de retenue pour pension, {e2(ex["rafp"])} de RAFP et {e2(ex["csg"])} de CSG-CRDS : son net s'établit à environ <strong>{e2(ex["net"])}</strong>, avant prélèvement à la source et cotisation de complémentaire santé.</p>
<h2>Ce que ce calcul ne couvre pas</h2>
<p>L'indemnité de résidence et le supplément familial de traitement s'ajoutent selon la commune d'affectation et la situation familiale. Certains corps subissent un abattement sur leurs primes au titre du transfert primes-points. Les agents contractuels, eux, relèvent du régime général de la Sécurité sociale et de l'Ircantec : leur passage du brut au net suit d'autres taux, que cette page ne détaille pas.</p>
"""
    js = f"""
            var im = v('w-im'), primes = v('w-primes');
            var t = Math.floor(im * {POINT_ANNUEL_IM100} / 12) / 100;
            var diff = Math.max(0, 1867.02 - t);
            var net = t + diff + primes - t * 0.111 - Math.min(primes, 0.2 * t) * 0.05 - (t + diff + primes) * 0.097 * 0.9825;
            out('r-traitement', centimes(t));
            out('r-brut', centimes(t + diff + primes));
            out('r-net', centimes(net));"""
    return {
        "slug": "salaire-brut-net-fonction-publique",
        "title": "Salaire brut net fonction publique 2026 : indice et calcul",
        "desc": "Salaire brut net fonction publique 2026 : traitement selon l'indice majoré, pension civile 11,10 %, RAFP sur les primes, CSG-CRDS. Tableau des indices 366 à 800",
        "h1": "Salaire brut net dans la fonction publique",
        "crumb": "Fonction publique",
        "widget_titre": "Traitement d'un fonctionnaire",
        "widget": widget([champ("w-im", "Indice majoré", "450", "numeric"),
                          champ("w-primes", "Primes mensuelles brutes (€)", "0")],
                         [("r-traitement", "Traitement indiciaire"), ("r-brut", "Brut total"), ("r-net", "Net estimé")],
                         "Fonctionnaire titulaire à temps complet, hors indemnité de résidence, supplément familial et complémentaire santé."),
        "js": js,
        "citable": f"Le traitement brut d'un fonctionnaire est égal à son indice majoré multiplié par {fmt2(POINT_ANNUEL_IM100)} € puis divisé par 1 200, la valeur du point étant inchangée depuis le 1er juillet 2023. En 2026, l'indice 450 donne ainsi {e2(calcul_fp(450)['traitement'])} brut par mois. Le fonctionnaire supporte une retenue pour pension de 11,10 % du traitement, 5 % de RAFP sur ses primes dans la limite de 20 % du traitement, et 9,70 % de CSG-CRDS sur 98,25 % de sa rémunération : sans primes, l'indice 450 laisse environ {e2(calcul_fp(450)['net'])} net. Les indices inférieurs à {int(seuil) + 1} reçoivent en plus une indemnité différentielle qui porte leur rémunération au SMIC de {e2(SMIC_MENSUEL_BRUT)} brut ; elle n'est pas soumise à la retenue pour pension.",
        "corps": corps,
        "sources": [SRC_FP, SRC_PENSION, SRC_RAFP, SRC_SMIC, SRC_TAUX],
        "faq": [
            ("Comment calculer le salaire d'un fonctionnaire à partir de son indice ?",
             f"Multipliez l'indice majoré par la valeur annuelle du point, {fmt2(POINT_ANNUEL_IM100)} € pour l'indice 100, puis divisez par 1 200 pour obtenir le traitement mensuel brut. L'indice 572 donne ainsi {e2(calcul_fp(572)['traitement'])} brut par mois, l'exemple donné par service-public.gouv.fr. Les primes, l'indemnité de résidence et le supplément familial s'ajoutent ensuite."),
            ("Quelles cotisations sont retenues sur le salaire d'un fonctionnaire ?",
             "Trois prélèvements principaux : la retenue pour pension civile de 11,10 % du traitement indiciaire, la cotisation à la retraite additionnelle de 5 % sur les primes dans la limite de 20 % du traitement, et la CSG-CRDS de 9,70 % sur 98,25 % de toute la rémunération. Il n'y a pas de cotisation chômage ni de retraite complémentaire Agirc-Arrco."),
            ("Le point d'indice a-t-il augmenté en 2026 ?",
             f"Non. La valeur du point est de {fmt2(POINT_ANNUEL_IM100)} € par an pour l'indice 100 depuis le 1er juillet 2023, et service-public.gouv.fr n'indique aucune revalorisation depuis. Les traitements des indices les plus bas ont en revanche suivi le SMIC grâce à l'indemnité différentielle, qui s'applique à tous les indices inférieurs à {int(seuil) + 1} depuis juin 2026."),
            ("Un fonctionnaire gagne-t-il plus net qu'un salarié du privé ?",
             f"À brut égal, les deux nets sont proches : un fonctionnaire sans primes conserve environ 79,4 % de son traitement, un salarié du privé environ 79,2 % de son brut jusqu'au plafond de la Sécurité sociale. L'écart se creuse avec les primes, qui ne supportent pas la retenue pour pension mais seulement la RAFP, plafonnée, et la CSG-CRDS."),
        ],
        "related": ["smic-brut-net-2026", "salaire-moyen-france", "salaire-net-imposable", "salaire-brut-net-annuel", "salaire-brut-net-cadre", "salaire-brut-net-non-cadre"],
    }


def cout_detail(brut, at=0.01):
    """Coût employeur détaillé, entreprise de moins de 11 salariés, non-cadre (taux Urssaf 2026)."""
    t1 = min(brut, PSS_MENSUEL)
    t2 = max(0, brut - PSS_MENSUEL)
    l4 = min(brut, 4 * PSS_MENSUEL)
    lignes = [
        ("Maladie, maternité, invalidité, décès", "13 %", brut * 0.13),
        ("Vieillesse plafonnée", "8,55 %", t1 * 0.0855),
        ("Vieillesse déplafonnée", "2,11 %", brut * 0.0211),
        ("Allocations familiales", "5,25 %", brut * 0.0525),
        ("Accidents du travail (hypothèse)", pct(at * 100, 2), brut * at),
        ("Assurance chômage", "4,00 %", l4 * 0.04),
        ("AGS", "0,25 %", l4 * 0.0025),
        ("Retraite complémentaire Agirc-Arrco", "4,72 % / 12,95 %", t1 * 0.0472 + t2 * 0.1295),
        ("Contribution d'équilibre général", "1,29 % / 1,62 %", t1 * 0.0129 + t2 * 0.0162),
        ("Contribution d'équilibre technique", "0,21 %", brut * 0.0021 if brut > PSS_MENSUEL else 0),
        ("Contribution solidarité autonomie", "0,30 %", brut * 0.003),
        ("Fnal (moins de 50 salariés)", "0,10 %", t1 * 0.001),
        ("Contribution au dialogue social", "0,016 %", brut * 0.00016),
        ("Formation professionnelle (moins de 11 salariés)", "0,55 %", brut * 0.0055),
        ("Taxe d'apprentissage", "0,68 %", brut * 0.0068),
    ]
    charges = sum(l[2] for l in lignes)
    coef = 0
    if brut < 3 * SMIC_MENSUEL_JANVIER:
        coef = min(0.3981, 0.02 + 0.3781 * (0.5 * (3 * SMIC_MENSUEL_JANVIER / brut - 1)) ** 1.75)
    rgdu = brut * coef
    return {"lignes": lignes, "charges": charges, "coef": coef, "rgdu": rgdu, "cout": brut + charges - rgdu}


def page_cout():
    bruts = (SMIC_MENSUEL_BRUT, 2000, 2500, 3000, 4000, 6000)
    calc = [cout_detail(b) for b in bruts]
    lignes = []
    for i, (lib, taux, _) in enumerate(calc[0]["lignes"]):
        lignes.append([lib, taux] + [e(c["lignes"][i][2]) for c in calc])
    lignes.append(["Réduction générale dégressive", "coefficient"] + [("− " + e(c["rgdu"])) if c["rgdu"] else "–" for c in calc])
    total = ["Coût total employeur", ""] + [e(c["cout"]) for c in calc]
    synth = [[e(b), e(c["charges"] - c["rgdu"]), e(c["cout"]), f"{c['cout'] / b:.2f}".replace(".", ",")] for b, c in zip(bruts, calc)]
    c2000 = cout_detail(2000)
    corps = f"""
<h2>Coût employeur selon le salaire brut</h2>
{table(["Salaire brut", "Charges patronales nettes", "Coût total", "Coût ÷ brut"], synth)}
{note("Entreprise de moins de 11 salariés, salarié non-cadre à temps plein, taux Urssaf 2026, taux accidents du travail supposé à 1 %. Hors mutuelle, prévoyance et versement mobilité.")}
<h2>Le détail ligne par ligne</h2>
{table(["Cotisation patronale", "Taux"] + [e(b) for b in bruts], lignes, total)}
{note("Les taux de tranche 2 (au-delà de " + e(PSS_MENSUEL) + ") sont indiqués après la barre oblique. Le taux accidents du travail réel est notifié chaque année par la Carsat et varie selon l'activité.")}
<h2>La réduction générale dégressive unique</h2>
<p>Depuis le 1er janvier 2026, une réduction unique remplace les anciens allègements sur les bas salaires. Elle s'applique aux rémunérations inférieures à <strong>3 SMIC</strong>, calculés sur la valeur du SMIC au 1er janvier 2026 ({e2(3 * SMIC_MENSUEL_JANVIER)} par mois). Dans une entreprise de moins de 50 salariés, le coefficient vaut 0,0200 + 0,3781 × [½ × (3 × SMIC annuel ÷ rémunération annuelle − 1)] puissance 1,75. Il atteint {fmt2(c2000['coef'] * 100)} % à {e(2000)} brut, soit {e(c2000['rgdu'])} de cotisations en moins chaque mois.</p>
<p>Conséquence : le coût d'un salarié progresse beaucoup plus vite que son brut entre le SMIC et 3 SMIC. Passer de {e(2000)} à {e(3000)} brut coûte {e(cout_detail(3000)['cout'] - c2000['cout'])} de plus à l'employeur, pour {e(net(3000) - net(2000))} de net supplémentaire pour le salarié.</p>
<h2>Ce qui n'est pas compté</h2>
<p>Le versement mobilité, dû à partir de 11 salariés selon la commune, la contribution formation portée à 1 % au même seuil, le Fnal à 0,50 % à partir de 50 salariés, la part patronale de la mutuelle et de la prévoyance, et pour les cadres la contribution Apec et la prévoyance obligatoire. Les heures supplémentaires ouvrent en outre droit à une déduction forfaitaire de 1,50 € par heure dans les entreprises de moins de 20 salariés.</p>
"""
    js = f"""
            var b = v('w-brut'), at = v('w-at') / 100;
            var p = 4005, t1 = Math.min(b, p), t2 = Math.max(0, b - p), l4 = Math.min(b, 4 * p);
            var ch = b * (0.13 + 0.0211 + 0.0525 + at + 0.003 + 0.00016 + 0.0055 + 0.0068) + t1 * (0.0855 + 0.0472 + 0.0129 + 0.001) + t2 * (0.1295 + 0.0162) + l4 * 0.0425 + (b > p ? b * 0.0021 : 0);
            var s = {SMIC_MENSUEL_JANVIER} * 3, coef = 0;
            if (b > 0 && b < s) {{ coef = Math.min(0.3981, 0.02 + 0.3781 * Math.pow(0.5 * (s / b - 1), 1.75)); }}
            out('r-charges', euros(ch - b * coef));
            out('r-cout', euros(b + ch - b * coef));
            out('r-net', euros(calculerBrutVersNet(b, 'non-cadre', 1).netAvantImpot));"""
    return {
        "slug": "cout-employeur",
        "title": "Coût employeur 2026 : charges patronales et coût total",
        "desc": f"Coût employeur 2026 : charges patronales ligne par ligne et réduction générale dégressive unique. Un salarié à 2 000 € brut coûte environ {e(c2000['cout'])} par mois.",
        "h1": "Coût employeur 2026 : du brut au coût total",
        "crumb": "Coût employeur",
        "widget_titre": "Calcul du coût employeur",
        "widget": widget([champ("w-brut", "Salaire brut mensuel (€)", "2000"),
                          champ("w-at", "Taux accidents du travail (%)", "1")],
                         [("r-charges", "Charges patronales nettes"), ("r-cout", "Coût total mensuel"), ("r-net", "Net versé au salarié")],
                         "Entreprise de moins de 11 salariés, non-cadre, taux Urssaf 2026."),
        "js": js,
        "citable": f"En 2026, le coût d'un salarié pour son employeur va d'environ {pct((cout_detail(SMIC_MENSUEL_BRUT)['cout'] / SMIC_MENSUEL_BRUT - 1) * 100, 0)} au-dessus du brut au niveau du SMIC à plus de {pct((cout_detail(6000)['cout'] / 6000 - 1) * 100, 0)} pour un salaire de {e(6000)}, dans une entreprise de moins de 11 salariés. L'écart vient de la réduction générale dégressive unique, qui efface jusqu'à 39,81 % du brut en cotisations patronales au SMIC et s'éteint à 3 SMIC. Un salarié payé {e(2000)} brut coûte ainsi environ {e(c2000['cout'])} par mois, pour {e(net(2000))} net versé. Le calcul retient les taux Urssaf 2026 et un taux accidents du travail de 1 % : maladie 13 %, vieillesse 10,66 %, allocations familiales 5,25 %, chômage 4,00 %, retraite complémentaire 6,01 % sur la tranche 1.",
        "corps": corps,
        "sources": [SRC_TAUX, SRC_RGDU, SRC_PSS, SRC_HS_PATRONAL],
        "faq": [
            ("Combien coûte un salarié payé 2 000 € brut ?",
             f"En 2026, dans une entreprise de moins de onze salariés, un non-cadre payé {e(2000)} brut coûte environ {e(c2000['cout'])} par mois, avec un taux accidents du travail de 1 %. Les cotisations patronales brutes atteignent {e(c2000['charges'])}, mais la réduction générale dégressive unique en retire {e(c2000['rgdu'])}. Le salarié perçoit {e(net(2000))} net avant impôt."),
            ("Qu'est-ce que la réduction générale dégressive unique ?",
             "C'est l'allègement de cotisations patronales en vigueur depuis le 1er janvier 2026 pour les salaires inférieurs à 3 SMIC. Son coefficient est maximal au SMIC, 39,81 % du brut dans les entreprises de moins de 50 salariés, puis diminue jusqu'à un plancher de 2 % juste avant 3 SMIC, et s'annule au-delà. Il porte sur la maladie, la vieillesse, les allocations familiales, la retraite complémentaire et le chômage."),
            ("Pourquoi le coût employeur augmente-t-il plus vite que le brut ?",
             f"Parce que la réduction générale diminue à mesure que le salaire monte. Entre le SMIC et 3 SMIC, chaque euro de brut supplémentaire fait perdre une partie de l'allègement. Passer un salarié de {e(2000)} à {e(3000)} brut coûte ainsi {e(cout_detail(3000)['cout'] - c2000['cout'])} de plus à l'employeur, alors que le salarié ne gagne que {e(net(3000) - net(2000))} net de plus."),
            ("Le coût employeur est-il le même dans toutes les entreprises ?",
             "Non. Il varie avec l'effectif, qui change le taux de la contribution formation, du Fnal et du coefficient de réduction générale, avec le taux accidents du travail propre à l'activité, avec la commune pour le versement mobilité, et avec la mutuelle et la prévoyance choisies. Les montants de cette page valent pour une entreprise de moins de onze salariés."),
        ],
        "related": ["smic-brut-net-2026", "salaire-brut-net-non-cadre", "salaire-brut-net-cadre", "heures-supplementaires-brut-net", "salaire-brut-net-annuel", "salaire-brut-net-alternance-apprentissage"],
    }


def page_non_cadre():
    lignes = []
    for b in (SMIC_MENSUEL_BRUT, 2000, 2200, 2500, 2800, 3000, 3500, 4000):
        r = calculer_brut_vers_net(b, "non-cadre")
        lignes.append([e2(b), e2(r["total_salarial"]), e2(r["net_avant_impot"]), e(r["net_avant_impot"] * 12)])
    r = calculer_brut_vers_net(2500, "non-cadre")
    assiettes = {"Vieillesse plafonnée": ("6,90 %", "jusqu'au plafond"), "Vieillesse déplafonnée": ("0,40 %", "totalité"),
                 "AGIRC-ARRCO T1": ("3,15 %", "jusqu'au plafond"), "CEG T1": ("0,86 %", "jusqu'au plafond"),
                 "CSG déductible": ("6,80 %", "98,25 % du brut"), "CSG non déductible": ("2,40 %", "98,25 % du brut"),
                 "CRDS": ("0,50 %", "98,25 % du brut")}
    det = [[k, a[0], a[1], e2(r["detail_salariales"][k])] for k, a in assiettes.items()]
    corps = f"""
<h2>Salaire brut en net pour un non-cadre en 2026</h2>
{table(["Brut mensuel", "Cotisations salariales", "Net avant impôt", "Net annuel"], lignes)}
{note("Régime général 2026, hors mutuelle d'entreprise. La première ligne correspond au SMIC à temps plein depuis le 1er juin 2026.")}
<h2>Les sept lignes du bulletin, pour 2 500 € brut</h2>
{table(["Cotisation", "Taux", "Assiette", "Montant"], det, ["Total", "", "", e2(r["total_salarial"])])}
{note("Net avant impôt : " + e2(r["net_avant_impot"]) + ". Taux salariaux Urssaf 2026 ; Agirc-Arrco et CEG sur la tranche 1, confirmés par l'Urssaf dans sa page sur les heures supplémentaires.")}
<h2>Pourquoi 20,8 % et pas 22 %</h2>
<p>Pour un non-cadre payé moins que le plafond de la Sécurité sociale, {e(PSS_MENSUEL)} par mois en 2026, les cotisations salariales légales représentent 11,31 % pour la retraite et 9,53 % de CSG-CRDS, soit <strong>environ 20,8 % du brut</strong>. Le chiffre de 22 % souvent cité correspond à peu près à ce taux augmenté de la part salariale d'une mutuelle d'entreprise, qui dépend du contrat collectif et ne peut pas être calculée à l'avance.</p>
<h2>Non-cadre au-delà du plafond</h2>
<p>Un non-cadre payé plus de {e(PSS_MENSUEL)} cotise exactement comme un cadre, à la cotisation Apec près : retraite complémentaire à 8,64 % sur la tranche 2, contribution d'équilibre général à 1,08 % et contribution d'équilibre technique à 0,14 % sur la totalité du salaire. La comparaison complète figure sur la page <a href="/cadre-vs-non-cadre/">cadre ou non-cadre</a>.</p>
"""
    js = """
            var r = calculerBrutVersNet(v('w-brut'), 'non-cadre', parseInt(document.getElementById('w-temps').value) / 100);
            out('r-net', centimes(r.netAvantImpot));
            out('r-cotis', centimes(r.totalSalarial));
            out('r-annuel', euros(r.netAvantImpot * 12));"""
    return {
        "slug": "salaire-brut-net-non-cadre",
        "title": "Salaire brut net non-cadre 2026 : taux et tableau de calcul",
        "desc": f"Salaire brut net non-cadre 2026 : 20,8 % de cotisations jusqu'à 4 005 € brut, soit {e(r['net_avant_impot'])} net pour 2 500 € brut. Tableau, détail du bulletin et calcul.",
        "h1": "Salaire brut net non-cadre 2026",
        "crumb": "Salaire brut net non-cadre",
        "widget_titre": "Brut en net pour un non-cadre",
        "widget": widget([champ("w-brut", "Salaire brut mensuel (€)", "2500"),
                          choix("w-temps", "Temps de travail", [("100", "Temps plein"), ("80", "80 %"), ("60", "60 %"), ("50", "50 %")], "100")],
                         [("r-net", "Net avant impôt"), ("r-cotis", "Cotisations salariales"), ("r-annuel", "Net annuel")],
                         "Pour un temps partiel, indiquez le brut d'un temps plein : il est proratisé."),
        "js": js,
        "citable": f"En 2026, un salarié non-cadre paie environ 20,8 % de cotisations salariales tant que son brut reste sous le plafond de la Sécurité sociale de {e(PSS_MENSUEL)} par mois : 11,31 % pour la retraite de base et complémentaire et 9,53 % de CSG-CRDS. Un brut de {e(2500)} donne ainsi {e2(r['net_avant_impot'])} net avant impôt, et le SMIC de {e2(SMIC_MENSUEL_BRUT)} environ {e2(SMIC_NET_MENSUEL_SP)}. La mutuelle d'entreprise s'y ajoute selon le contrat, ce qui explique les repères de 22 % souvent cités. Au-delà du plafond, un non-cadre cotise exactement comme un cadre, à la cotisation Apec près : retraite complémentaire à 8,64 % sur la part qui dépasse, contribution d'équilibre technique de 0,14 % sur la totalité.",
        "corps": corps,
        "sources": [SRC_TAUX, SRC_PSS, SRC_HS_URSSAF, SRC_SMIC],
        "faq": [
            ("Quel pourcentage retirer du brut pour un non-cadre ?",
             f"Environ 20,8 % en 2026, tant que le salaire reste sous {e(PSS_MENSUEL)} brut par mois. Ce taux réunit la vieillesse, la retraite complémentaire Agirc-Arrco, la contribution d'équilibre général, la CSG et la CRDS. Ajoutez la part salariale de la mutuelle d'entreprise pour retrouver le net exact de votre bulletin, qui dépend du contrat collectif."),
            ("Combien fait 2 000 € brut en net pour un non-cadre ?",
             f"En 2026, {e(2000)} brut par mois donnent {e2(net(2000))} net avant impôt pour un non-cadre, hors mutuelle. Sur l'année, cela représente environ {e(net(2000) * 12)} net. Le prélèvement à la source s'applique ensuite sur le net imposable, au taux personnalisé transmis par l'administration ou au taux neutre."),
            ("Un non-cadre cotise-t-il à l'assurance chômage ?",
             "Non. Le barème Urssaf 2026 des cotisations salariales du secteur privé ne comporte aucune part chômage, ni pour les non-cadres ni pour les cadres. Seule la part patronale de 4,00 % existe, avec la cotisation AGS de 0,25 %. Elle pèse sur le coût du salarié pour l'employeur, mais n'apparaît pas en retenue sur son salaire."),
            ("Le net d'un non-cadre change-t-il avec un temps partiel ?",
             "Le taux de cotisations reste le même, car il est proportionnel au salaire. Un non-cadre à 80 % d'un temps plein payé 2 500 € brut perçoit 80 % du net correspondant. Seule exception, les heures complémentaires effectuées au-delà de la durée du contrat bénéficient de la réduction de cotisations salariales et d'une exonération d'impôt."),
        ],
        "related": ["salaire-brut-net-cadre", "smic-brut-net-2026", "salaire-net-imposable", "cout-employeur", "salaire-brut-net-horaire", "salaire-brut-net-alsace-moselle"],
    }


def page_alsace():
    lignes = []
    for b in (SMIC_MENSUEL_BRUT, 2000, 2500, 3000, 4000, 5000):
        ng = net(b)
        na = net(b, alsace_moselle=True)
        lignes.append([e2(b), e2(ng), e2(na), e2(ng - na), e(12 * (ng - na))])
    corps = f"""
<h2>Salaire net en Alsace-Moselle en 2026</h2>
{table(["Brut mensuel", "Net régime général", "Net Alsace-Moselle", "Écart mensuel", "Écart annuel"], lignes)}
{note("Non-cadre, cotisations 2026, hors mutuelle. Cotisation salariale maladie supplémentaire de 1,30 % (Urssaf, taux 2026).")}
<h2>Qui est concerné</h2>
<p>Le régime local d'assurance maladie s'applique aux salariés qui travaillent dans le <strong>Bas-Rhin (67), le Haut-Rhin (68) et la Moselle (57)</strong>, Il s'agit d'un héritage de la période 1871-1918, maintenu après le retour de ces départements à la France. Il ne dépend pas du statut, cadre ou non-cadre.</p>
<h2>Une cotisation de plus, de meilleurs remboursements</h2>
<p>Les salariés du régime local versent une <strong>cotisation maladie supplémentaire de 1,30 %</strong>, qui n'existe nulle part ailleurs : à {e(2500)} brut, elle retire {e2(net(2500) - net(2500, alsace_moselle=True))} par mois du net. En contrepartie, le régime local complète les remboursements de l'assurance maladie, ce qui réduit le besoin de complémentaire santé. Côté employeur, ces départements appliquent aussi une taxe d'apprentissage spécifique de 0,44 %, sans solde.</p>
<h2>Impôt sur le revenu</h2>
<p>La cotisation de 1,30 % est une cotisation sociale obligatoire : elle est déduite du revenu imposable, comme les cotisations de retraite. Le <a href="/salaire-net-imposable/">net imposable</a> d'un salarié alsacien ou mosellan est donc inférieur, à brut égal, à celui d'un salarié du reste de la France, ce qui atténue un peu l'écart sur le net après impôt.</p>
"""
    js = """
            var b = v('w-brut'), s = document.getElementById('w-statut').value;
            var g = calculerBrutVersNet(b, s, 1).netAvantImpot;
            var a = calculerBrutVersNet(b, s, 1, { alsaceMoselle: true }).netAvantImpot;
            out('r-am', centimes(a));
            out('r-g', centimes(g));
            out('r-diff', centimes(g - a));"""
    return {
        "slug": "salaire-brut-net-alsace-moselle",
        "title": "Salaire brut net Alsace-Moselle 2026 : cotisation de 1,30 %",
        "desc": "Salaire brut net Alsace-Moselle 2026 : cotisation maladie supplémentaire de 1,30 % dans le 57, le 67 et le 68. Net comparé au régime général de 1 867 à 5 000 €.",
        "h1": "Salaire brut net en Alsace-Moselle",
        "crumb": "Alsace-Moselle",
        "widget_titre": "Net en Alsace-Moselle",
        "widget": widget([champ("w-brut", "Salaire brut mensuel (€)", "2500"),
                          choix("w-statut", "Statut", STATUT, "non-cadre")],
                         [("r-am", "Net Alsace-Moselle"), ("r-g", "Net régime général"), ("r-diff", "Écart mensuel")]),
        "js": js,
        "citable": f"En Alsace-Moselle, c'est-à-dire dans le Bas-Rhin, le Haut-Rhin et la Moselle, les salariés versent en 2026 une cotisation maladie supplémentaire de 1,30 % du brut au titre du régime local. À {e(2500)} brut, leur net avant impôt est de {e2(net(2500, alsace_moselle=True))}, contre {e2(net(2500))} dans le reste de la France, soit {e2(net(2500) - net(2500, alsace_moselle=True))} de moins par mois. En contrepartie, le régime local améliore les remboursements de santé, et la cotisation, déductible, réduit le revenu imposable. La cotisation concerne cadres et non-cadres, sur la totalité du brut : à {e(2500)} brut, l'écart atteint {e(12 * (net(2500) - net(2500, alsace_moselle=True)))} sur l'année. Côté employeur, ces trois départements appliquent une taxe d'apprentissage spécifique de 0,44 %, sans solde, au lieu de 0,68 % ailleurs.",
        "corps": corps,
        "sources": [SRC_TAUX, SRC_PSS, SRC_SMIC],
        "faq": [
            ("Pourquoi le salaire net est-il plus faible en Alsace-Moselle ?",
             f"Parce que les salariés du régime local paient une cotisation maladie supplémentaire de 1,30 % de leur brut, qui n'existe pas ailleurs. Pour {e(3000)} brut, elle représente {e2(net(3000) - net(3000, alsace_moselle=True))} par mois. Cette cotisation finance un meilleur remboursement des soins, ce qui permet souvent de réduire le coût de la complémentaire santé."),
            ("Quels départements appliquent le régime local ?",
             "Le Bas-Rhin, le Haut-Rhin et la Moselle, soit les départements 67, 68 et 57. Le régime s'applique aux salariés qui y travaillent, quel que soit leur lieu de résidence. La cotisation de 1,30 % apparaît alors sur le bulletin sous une ligne dédiée, à côté des cotisations du régime général, qui restent identiques."),
            ("Un cadre alsacien paie-t-il aussi les 1,30 % ?",
             "Oui. La cotisation du régime local ne dépend pas du statut : cadres et non-cadres la versent au même taux, sur l'ensemble de leur salaire brut. Elle s'ajoute aux cotisations ordinaires du régime général, qui restent identiques à celles du reste de la France, Apec comprise pour les cadres."),
            ("La cotisation Alsace-Moselle est-elle déductible des impôts ?",
             "Oui. Comme les autres cotisations sociales obligatoires, elle est retirée du salaire pour calculer le net imposable. À brut égal, un salarié du régime local déclare donc un revenu imposable un peu plus faible, et son prélèvement à la source est légèrement réduit, ce qui compense une petite partie de la baisse du net."),
        ],
        "related": ["salaire-brut-net-non-cadre", "salaire-brut-net-cadre", "salaire-net-imposable", "smic-brut-net-2026", "cout-employeur", "salaire-moyen-france"],
    }


def page_journalier():
    jours = HEURES_MENSUELLES / 7
    lignes = []
    for d in (SMIC_HORAIRE * 7, 100, 120, 150, 180, 200, 250, 300, 400):
        brut_m = d * jours
        n = net(brut_m)
        lignes.append([e2(d), e2(n / jours), e(brut_m), e(n)])
    corps = f"""
<h2>Salaire journalier brut en net : tableau 2026</h2>
{table(["Brut par jour", "Net par jour", "Brut mensuel équivalent", "Net mensuel équivalent"], lignes)}
{note("Journée de 7 heures, mois de 151,67 heures soit 21,67 jours, non-cadre, cotisations 2026, hors mutuelle. La première ligne correspond au SMIC horaire de 12,31 € sur 7 heures.")}
<h2>De la journée au mois</h2>
<p>Un temps plein de 35 heures par semaine représente 151,67 heures par mois, soit <strong>21,67 journées de 7 heures</strong>. C'est le coefficient qui permet de passer d'un salaire journalier à un équivalent mensuel : {e(150)} brut par jour correspondent à {e(150 * jours)} brut par mois. Le nombre de jours ouvrés varie d'un mois à l'autre, mais un salarié mensualisé perçoit le même salaire chaque mois.</p>
<h2>SMIC journalier 2026</h2>
<p>Avec un SMIC horaire de {e2(SMIC_HORAIRE)} brut depuis le 1er juin 2026, une journée de 7 heures vaut au minimum <strong>{e2(SMIC_HORAIRE * 7)} brut</strong>, soit environ {e2(net(SMIC_MENSUEL_BRUT) / jours)} net. Du 1er janvier au 31 mai 2026, elle valait {e2(SMIC_HORAIRE_JANVIER * 7)} brut.</p>
<h2>Cadres au forfait jours</h2>
<p>Les cadres au forfait annuel travaillent au plus 218 jours par an et sont payés au mois, pas à la journée. Un salaire journalier n'a de sens pour eux que pour valoriser des jours de repos rachetés : lorsque le salarié renonce à des jours de repos après avoir travaillé au moins 218 jours, leur rémunération bénéficie de la réduction de cotisations salariales applicable aux heures supplémentaires.</p>
<h2>CDD, intérim et vacations</h2>
<p>Pour un contrat court payé à la journée, le net se calcule de la même façon, mais d'autres sommes s'ajoutent en fin de mission : l'indemnité de fin de contrat et l'indemnité compensatrice de congés payés, détaillées sur notre page consacrée au <a href="/salaire-brut-net-interim/">salaire en intérim</a>.</p>
"""
    js = """
            var d = v('w-jour'), n = v('w-jours');
            var brut = d * n;
            var r = calculerBrutVersNet(brut, document.getElementById('w-statut').value, 1);
            out('r-jour', centimes(n > 0 ? r.netAvantImpot / n : 0));
            out('r-mois', euros(r.netAvantImpot));
            out('r-brut', euros(brut));"""
    return {
        "slug": "salaire-brut-net-journalier",
        "title": "Salaire journalier brut net 2026 : tableau et calcul du net",
        "desc": f"Salaire journalier brut net 2026 : 86,17 € brut par jour au SMIC sur 7 h, soit {e2(net(SMIC_MENSUEL_BRUT) / jours)} net. Tableau de 100 à 400 € par jour, équivalent mensuel sur 21,67 jours.",
        "h1": "Salaire journalier brut et net 2026",
        "crumb": "Salaire journalier",
        "widget_titre": "Salaire par jour en net",
        "widget": widget([champ("w-jour", "Salaire brut par jour (€)", "150"),
                          champ("w-jours", "Jours travaillés dans le mois", "21,67"),
                          choix("w-statut", "Statut", STATUT, "non-cadre")],
                         [("r-jour", "Net par jour"), ("r-mois", "Net du mois"), ("r-brut", "Brut du mois")]),
        "js": js,
        "citable": f"En 2026, un salaire journalier brut se convertit en net en retirant environ 20,8 % de cotisations salariales tant que le mois reste sous le plafond de la Sécurité sociale de {e(PSS_MENSUEL)}. Au SMIC de {e2(SMIC_HORAIRE)} de l'heure, une journée de 7 heures vaut {e2(SMIC_HORAIRE * 7)} brut, soit environ {e2(net(SMIC_MENSUEL_BRUT) / jours)} net. Un temps plein compte 21,67 journées de 7 heures par mois : {e(150)} brut par jour correspondent donc à {e(150 * jours)} brut et {e(net(150 * jours))} net par mois. Un cadre au forfait annuel travaille au plus 218 jours et reste payé au mois. Au-delà du plafond de la Sécurité sociale, soit environ {e2(PSS_MENSUEL / jours)} brut par jour sur un mois complet, la part prélevée diminue légèrement.",
        "corps": corps,
        "sources": [SRC_SMIC, SRC_TAUX, SRC_PSS, SRC_HS_URSSAF],
        "faq": [
            ("Comment calculer un salaire journalier net ?",
             f"Retirez environ 20,8 % du brut journalier tant que le salaire du mois reste sous {e(PSS_MENSUEL)} : c'est le poids des cotisations salariales et de la CSG-CRDS en 2026. Une journée payée {e(120)} brut rapporte ainsi environ {e2(net(120 * jours) / jours)} net. La mutuelle d'entreprise et le prélèvement à la source réduisent ensuite ce montant."),
            ("Combien de jours compte un mois de travail ?",
             "Pour un temps plein de 35 heures, on retient 151,67 heures par mois, soit 21,67 journées de 7 heures. Ce chiffre est une moyenne annuelle : un mois réel compte entre 20 et 23 jours ouvrés. Un salarié mensualisé est payé le même montant chaque mois ; seuls les contrats rémunérés à la journée suivent le nombre de jours effectivement travaillés."),
            ("Quel est le SMIC journalier en 2026 ?",
             f"Pour une journée de 7 heures, le SMIC journalier est de {e2(SMIC_HORAIRE * 7)} brut depuis le 1er juin 2026, contre {e2(SMIC_HORAIRE_JANVIER * 7)} du 1er janvier au 31 mai. En net, cela représente environ {e2(net(SMIC_MENSUEL_BRUT) / jours)} par jour. Une journée plus longue se paie en proportion, avec des majorations au-delà de 35 heures dans la semaine."),
            ("Comment passer d'un salaire journalier à un salaire mensuel ?",
             f"Multipliez le salaire journalier par 21,67 pour un temps plein de 35 heures par semaine. Une journée à {e(200)} brut correspond à {e(200 * jours)} brut par mois, soit environ {e(net(200 * jours))} net. Pour un temps partiel de trois jours par semaine, multipliez plutôt par 13, soit trois jours sur 52 semaines divisés par douze mois."),
        ],
        "related": ["salaire-brut-net-horaire", "smic-brut-net-2026", "salaire-brut-net-annuel", "salaire-brut-net-cadre", "heures-supplementaires-brut-net", "salaire-brut-net-stage"],
    }


PAGES = [page_smic, page_apprenti, page_moyen, page_stage, page_cadre, page_horaire, page_hs,
         page_annuel, page_imposable, page_fp, page_cout, page_non_cadre, page_alsace, page_journalier]

# Doublons : une seule page gardée, l'autre adresse renvoie vers elle.
REDIRECTIONS = {
    "calculateur-heures-supplementaires": "heures-supplementaires-brut-net",
    "calculateur-cout-employeur": "cout-employeur",
}

REDIRECT_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Redirection - Salaire Bruto Net</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0;url={url}">
<meta name="robots" content="noindex, follow">
</head>
<body>
<p>Cette page a été déplacée. <a href="{url}">Cliquez ici</a> si vous n'êtes pas redirigé automatiquement.</p>
<script>window.location.replace('{url}');</script>
</body>
</html>"""


def controler(p):
    """Règles de snippets et de FAQ (RECETTE §11) : arrêt avant toute écriture si une page est hors règle."""
    erreurs = []
    if not 50 <= len(p["title"]) <= 60:
        erreurs.append(f"title {len(p['title'])} car. : {p['title']}")
    if not 150 <= len(p["desc"]) <= 160:
        erreurs.append(f"description {len(p['desc'])} car. : {p['desc']}")
    for q, r in p["faq"]:
        n = compter_mots(r)
        if not 40 <= n <= 90:
            erreurs.append(f"FAQ {n} mots : {q}")
    if "—" in p["title"] + p["desc"] + p["corps"] + p["citable"] + "".join(r for _, r in p["faq"]):
        erreurs.append("tiret cadratin")
    return erreurs


def maj_sitemap(maj_iso):
    chemin = os.path.join(BASE_DIR, "sitemap.xml")
    with open(chemin, encoding="utf-8") as f:
        xml = f.read()
    ajouts = []
    for fn in PAGES:
        loc = f"{BASE_URL}/{fn()['slug']}/"
        bloc = re.search(r"<url>\s*<loc>" + re.escape(loc) + r"</loc>.*?</url>", xml, re.S)
        neuf = (f"    <url>\n        <loc>{loc}</loc>\n        <lastmod>{maj_iso}</lastmod>\n"
                f"        <changefreq>monthly</changefreq>\n        <priority>0.8</priority>\n    </url>")
        if bloc:
            xml = xml.replace(bloc.group(0), neuf.strip())
        else:
            ajouts.append(neuf)
    for slug in REDIRECTIONS:
        xml = re.sub(r"\s*<url>\s*<loc>" + re.escape(f"{BASE_URL}/{slug}/") + r"</loc>.*?</url>", "", xml, flags=re.S)
    if ajouts:
        xml = xml.replace("</urlset>", "\n".join(ajouts) + "\n</urlset>")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(xml)
    return len(ajouts)


def main():
    maj_iso, maj_lisible = date_maj(SCRIPT, "calcul.py")
    gabarit = extraire_gabarit()
    pages = [fn() for fn in PAGES]
    titres = {p["slug"]: p["crumb"] for p in pages}
    erreurs = {p["slug"]: controler(p) for p in pages}
    erreurs = {k: v for k, v in erreurs.items() if v}
    if erreurs:
        for slug, errs in erreurs.items():
            for err in errs:
                print(f"  ✗ {slug} : {err}")
        raise SystemExit("Pages hors règle : rien n'a été écrit.")
    for p in pages:
        for s in p["related"]:
            if s not in titres:
                raise SystemExit(f"{p['slug']} : lien connexe inconnu {s}")
    for p in pages:
        dossier = os.path.join(BASE_DIR, p["slug"])
        os.makedirs(dossier, exist_ok=True)
        with open(os.path.join(dossier, "index.html"), "w", encoding="utf-8") as f:
            f.write(rendre(p, gabarit, maj_iso, maj_lisible, titres))
        print(f"  ✓ {p['slug']}/ ({len(p['title'])} / {len(p['desc'])} car.)")
    for src, cible in REDIRECTIONS.items():
        with open(os.path.join(BASE_DIR, src, "index.html"), "w", encoding="utf-8") as f:
            f.write(REDIRECT_HTML.format(url=f"{BASE_URL}/{cible}/"))
        print(f"  ↪ {src}/ → /{cible}/")
    n = maj_sitemap(maj_iso or "2026-10-26")
    print(f"  ✓ sitemap.xml ({n} adresses ajoutées)")
    print(f"Date de mise à jour affichée : {maj_lisible or '(aucune, pas d’historique git)'}")


if __name__ == "__main__":
    main()
