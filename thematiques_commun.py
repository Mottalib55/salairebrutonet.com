#!/usr/bin/env python3
"""
Outils communs aux pages thématiques de salairebrutonet.com : chiffres officiels,
gabarit HTML, champs du calculateur, sources. Importé par generate-thematiques.py
et par les modules de pages thematiques_*.py.
"""


import html
import json
import math
import os
import re
import subprocess

from calcul import (
    HEURES_MENSUELLES, PSS_ANNUEL, PSS_HORAIRE, PSS_MENSUEL, SMIC_HORAIRE, SMIC_HORAIRE_JANVIER,
    SMIC_MENSUEL_BRUT, SMIC_MENSUEL_JANVIER, arrondi, calculer_brut_vers_net, fmt, fmt2,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://salairebrutonet.com"
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
             "knowsAbout": ["Paie", "Cotisations sociales", "Droit du travail", "Impôt sur le revenu", "Retraite"],
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
    # La date de mise à jour vit en bas de page et dans WebPage.dateModified, jamais
    # au-dessus du simulateur (RECETTE §8.4, règle du 2026-10-15 ; check-trame.py).
    date_haut = ""
    releve = p.get("releve", "26 octobre 2026")
    note_sources = p.get("note_sources", "Les montants nets sont des estimations du régime général : la mutuelle et la prévoyance d'entreprise, propres à chaque contrat, n'y sont pas déduites.")
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
                    <p class="tp-note mt-3">Chiffres relevés sur ces sites le {releve}. {note_sources} <a href="/methodologie/">Méthode de calcul</a>.</p>
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



# ── Calculs partagés ─────────────────────────────────────────────────────────

def brut_pour_net(n):
    from calcul import calculer_net_vers_brut
    return calculer_net_vers_brut(n, "non-cadre")["brut_mensuel"]



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

