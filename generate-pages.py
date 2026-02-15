#!/usr/bin/env python3
"""
Génère les pages Phase 2 : statuts professionnels, périodes, contenu éducatif, outils.
Usage : python generate-pages.py
"""

import os
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://salairebrutonet.com"
TODAY = date.today().isoformat()

# ── Template HTML commun ──────────────────────────────────────────────────────

def page_head(title, description, canonical, keywords=""):
    return f'''<!DOCTYPE html>
<html lang="fr" class="scroll-smooth"><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{canonical}">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect fill='%230284c7' rx='20' width='100' height='100'/><text x='50%' y='55%' dominant-baseline='middle' text-anchor='middle' font-size='60'>💰</text></svg>">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:locale" content="fr_FR">
    <meta property="og:site_name" content="SalaireBrutNet">
    <meta name="robots" content="index, follow">
    <meta name="keywords" content="{keywords}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{ sans: ['Inter', 'sans-serif'] }},
                    colors: {{
                        brand: {{ 50:'#f0f9ff',100:'#e0f2fe',200:'#bae6fd',400:'#38bdf8',500:'#0ea5e9',600:'#0284c7',700:'#0369a1',900:'#0c4a6e' }},
                        emerald: {{ 50:'#ecfdf5',100:'#d1fae5',500:'#10b981',600:'#059669',700:'#047857' }}
                    }}
                }}
            }}
        }}
    </script>
    <style>
        input[type=range] {{ -webkit-appearance: none; background: transparent; }}
        input[type=range]::-webkit-slider-thumb {{ -webkit-appearance: none; height: 20px; width: 20px; border-radius: 50%; background: #fff; border: 2px solid #0ea5e9; cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.15); margin-top: -8px; }}
        input[type=range]::-webkit-slider-runnable-track {{ width: 100%; height: 4px; cursor: pointer; background: linear-gradient(to right, #0ea5e9 0%, #0ea5e9 var(--progress, 0%), #e2e8f0 var(--progress, 0%), #e2e8f0 100%); border-radius: 9999px; }}
        input[type=number]::-webkit-inner-spin-button, input[type=number]::-webkit-outer-spin-button {{ -webkit-appearance: none; margin: 0; }}
        input[type=number] {{ -moz-appearance: textfield; }}
    </style>
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {{ "@type": "ListItem", "position": 1, "name": "Calculateur Salaire Brut Net", "item": "{BASE_URL}/" }},
            {{ "@type": "ListItem", "position": 2, "name": "{title.split(' | ')[0].split(' - ')[0]}", "item": "{canonical}" }}
        ]
    }}
    </script>
</head>'''


HEADER = '''
<body class="bg-slate-50 text-slate-600 antialiased selection:bg-brand-100 selection:text-brand-900 flex flex-col min-h-screen">
    <header class="sticky top-0 z-50 w-full border-b border-slate-200 bg-white/90 backdrop-blur-md">
        <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
            <a href="/" class="flex items-center gap-2">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white">
                    <i data-lucide="calculator" class="h-5 w-5"></i>
                </div>
                <span class="text-base font-semibold tracking-tight text-slate-900">SalaireBrutNet</span>
            </a>
            <nav class="hidden md:flex gap-8">
                <a href="/" class="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Calculateur</a>
                <a href="/simulateur-impot-sur-le-revenu/" class="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Simulateur Impôts</a>
                <a href="/mission.html" class="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Notre Mission</a>
            </nav>
        </div>
    </header>
    <main class="flex-grow">
'''

FOOTER = '''
    </main>
    <footer class="bg-white border-t border-slate-200 py-10">
        <div class="mx-auto max-w-7xl px-4 flex flex-col md:flex-row justify-between items-center gap-6">
            <a href="/" class="flex items-center gap-2">
                <div class="flex h-6 w-6 items-center justify-center rounded bg-slate-900 text-white">
                    <i data-lucide="calculator" class="h-3 w-3"></i>
                </div>
                <span class="text-sm font-semibold text-slate-900">SalaireBrutNet</span>
            </a>
            <p class="text-xs text-slate-500">© 2025 SalaireBrutNet · Estimation indicative</p>
            <div class="flex gap-4">
                <a href="/" class="text-xs text-slate-500 hover:text-slate-900">Calculateur</a>
                <a href="/mentions-legales.html" class="text-xs text-slate-500 hover:text-slate-900">Mentions légales</a>
                <a href="/mission.html" class="text-xs text-slate-500 hover:text-slate-900">Notre Mission</a>
                <a href="/simulateur-impot-sur-le-revenu/" class="text-xs text-slate-500 hover:text-slate-900">Simulateur Impôts</a>
            </div>
        </div>
    </footer>
    <script src="/js/brut-net.js"></script>
    <script>lucide.createIcons();</script>
'''


def breadcrumb(label):
    return f'''
        <nav class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
            <ol class="flex items-center gap-2 text-sm text-slate-500">
                <li><a href="/" class="hover:text-brand-600 transition-colors">Accueil</a></li>
                <li><i data-lucide="chevron-right" class="h-4 w-4"></i></li>
                <li class="text-slate-900 font-medium">{label}</li>
            </ol>
        </nav>'''


def calculator_widget(default_val=2500, statut_default="non-cadre", mode="brut"):
    """Inline calculator widget reusable across pages."""
    if mode == "brut":
        label_input = "Salaire brut mensuel"
        label_result = "Salaire net mensuel"
        result_id = "result-net-widget"
        calc_fn = "calculerBrutVersNet"
        result_field = "netAvantImpot"
    else:
        label_input = "Salaire net mensuel"
        label_result = "Salaire brut mensuel"
        result_id = "result-brut-widget"
        calc_fn = "calculerNetVersBrut"
        result_field = "brutMensuel"

    cadre_selected = 'selected' if statut_default == 'cadre' else ''
    nc_selected = 'selected' if statut_default == 'non-cadre' else ''

    return f'''
        <section class="py-12 px-4">
            <div class="mx-auto max-w-3xl">
                <h2 class="text-xl font-bold text-slate-900 mb-6 text-center">Calculateur rapide</h2>
                <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-1">{label_input}</label>
                            <input type="number" id="widget-input" value="{default_val}" min="0" max="20000" step="50"
                                class="w-full rounded-lg border border-slate-200 px-3 py-2 text-lg font-bold text-slate-900 focus:border-brand-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-1">Statut</label>
                            <select id="widget-statut" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:outline-none">
                                <option value="non-cadre" {nc_selected}>Non-cadre</option>
                                <option value="cadre" {cadre_selected}>Cadre</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-1">Temps de travail</label>
                            <select id="widget-temps" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:outline-none">
                                <option value="100" selected>100%</option>
                                <option value="80">80%</option>
                                <option value="60">60%</option>
                                <option value="50">50%</option>
                            </select>
                        </div>
                    </div>
                    <div class="rounded-xl bg-brand-50 border border-brand-100 p-4 text-center">
                        <p class="text-sm text-brand-600 font-medium">{label_result}</p>
                        <p class="text-3xl font-bold text-slate-900" id="{result_id}">—</p>
                    </div>
                </div>
            </div>
        </section>
    <script>
    (function() {{
        const inp = document.getElementById('widget-input');
        const sel = document.getElementById('widget-statut');
        const tmp = document.getElementById('widget-temps');
        const res = document.getElementById('{result_id}');
        function calc() {{
            const v = parseFloat(inp.value) || 0;
            const r = {calc_fn}(v, sel.value, parseInt(tmp.value)/100);
            res.textContent = formatMoney(r.{result_field});
        }}
        inp.addEventListener('input', calc);
        sel.addEventListener('change', calc);
        tmp.addEventListener('change', calc);
        calc();
    }})();
    </script>'''


def links_grid(title, links):
    """Build a grid of internal links."""
    items = ""
    for url, label in links:
        items += f'''<a href="{url}" class="block rounded-xl border border-slate-200 bg-white p-3 text-center hover:border-brand-300 hover:shadow-sm transition-all">
            <span class="block text-sm font-medium text-slate-900">{label}</span>
        </a>\n'''
    return f'''
        <section class="bg-white border-t border-slate-200 py-12 px-4">
            <div class="mx-auto max-w-4xl">
                <h2 class="text-lg font-bold text-slate-900 mb-4">{title}</h2>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                    {items}
                </div>
            </div>
        </section>'''


RELATED_LINKS = [
    ("/salaire-brut-net-cadre/", "Brut net cadre"),
    ("/salaire-brut-net-non-cadre/", "Brut net non-cadre"),
    ("/salaire-brut-net-fonction-publique/", "Fonction publique"),
    ("/difference-salaire-brut-net/", "Différence brut/net"),
    ("/cotisations-sociales-salariales/", "Cotisations sociales"),
    ("/cout-employeur/", "Coût employeur"),
    ("/smic-brut-net-2025/", "SMIC 2025"),
    ("/salaire-brut-net-mensuel/", "Calcul mensuel"),
]


def write_page(slug, html_content):
    """Write page to slug/index.html"""
    folder = os.path.join(BASE_DIR, slug)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  ✓ {slug}/index.html")


# ── 1. Pages par statut professionnel ──────────────────────────────────────────

def gen_status_pages():
    pages = [
        {
            "slug": "salaire-brut-net-cadre",
            "title": "Salaire Brut Net Cadre 2025 : Calcul et Cotisations",
            "desc": "Calculez votre salaire brut en net en tant que cadre. Cotisations spécifiques cadre (CET, AGIRC-ARRCO), taux détaillés et simulateur gratuit 2025.",
            "kw": "salaire brut net cadre, brut en net cadre, cotisations cadre, calcul salaire cadre",
            "h1": "Salaire Brut Net <span class=\"text-brand-600\">Cadre</span> 2025",
            "statut_default": "cadre",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900 mt-8">Spécificités du statut cadre</h2>
                <p>En tant que <strong>cadre</strong>, vos cotisations salariales sont légèrement plus élevées qu'un non-cadre. La principale différence réside dans la <strong>CET (Contribution d'Équilibre Technique)</strong> de 0,14% prélevée sur la totalité de votre salaire brut.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Cotisations salariales cadre 2025</h3>
                <p>Voici le détail des cotisations prélevées sur votre salaire brut :</p>
                <ul class="space-y-1">
                    <li><strong>Vieillesse plafonnée</strong> : 6,90% (sur la tranche 1, jusqu'à 3 864 €/mois)</li>
                    <li><strong>Vieillesse déplafonnée</strong> : 0,40% (sur la totalité du brut)</li>
                    <li><strong>AGIRC-ARRCO Tranche 1</strong> : 3,15% (jusqu'au plafond SS)</li>
                    <li><strong>AGIRC-ARRCO Tranche 2</strong> : 8,64% (au-delà du plafond SS)</li>
                    <li><strong>CEG T1</strong> : 0,86% | <strong>CEG T2</strong> : 1,08%</li>
                    <li><strong>CET</strong> : 0,14% (spécifique cadre, sur la totalité)</li>
                    <li><strong>CSG déductible</strong> : 6,80% | <strong>CSG non déductible</strong> : 2,40% | <strong>CRDS</strong> : 0,50% (sur 98,25% du brut)</li>
                </ul>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Différence cadre vs non-cadre</h3>
                <p>Pour un même salaire brut, un <strong>cadre touche environ 3% de moins en net</strong> qu'un non-cadre, principalement à cause de la CET. Par exemple, pour 3 000 € brut mensuel :</p>
                <ul>
                    <li>Non-cadre : environ 2 340 € net</li>
                    <li>Cadre : environ 2 336 € net</li>
                </ul>
                <p>La différence est faible sur les salaires inférieurs au plafond de la Sécurité sociale. Elle augmente pour les hauts salaires en raison des cotisations sur la tranche 2.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Avantages du statut cadre</h3>
                <p>Malgré des cotisations légèrement plus élevées, le statut cadre offre des avantages :</p>
                <ul>
                    <li><strong>Retraite complémentaire plus élevée</strong> grâce aux cotisations AGIRC-ARRCO majorées</li>
                    <li><strong>Prévoyance obligatoire</strong> (couverture décès, invalidité)</li>
                    <li><strong>Période d'essai plus longue</strong> (jusqu'à 4 mois renouvelable)</li>
                    <li><strong>Préavis de démission/licenciement allongé</strong> (3 mois en général)</li>
                </ul>
            """
        },
        {
            "slug": "salaire-brut-net-non-cadre",
            "title": "Salaire Brut Net Non-Cadre 2025 : Calcul et Cotisations",
            "desc": "Calculez votre salaire brut en net en tant que non-cadre. Taux de cotisations 2025, détail des charges et simulateur gratuit.",
            "kw": "salaire brut net non cadre, brut en net non cadre, cotisations non cadre, employé",
            "h1": "Salaire Brut Net <span class=\"text-brand-600\">Non-Cadre</span> 2025",
            "statut_default": "non-cadre",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900 mt-8">Le statut non-cadre (employé / ouvrier)</h2>
                <p>Le statut <strong>non-cadre</strong> concerne la majorité des salariés en France. Les cotisations salariales représentent environ <strong>22% du salaire brut</strong>, ce qui signifie que pour 100 € brut, vous touchez environ 78 € net.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Cotisations salariales non-cadre 2025</h3>
                <ul class="space-y-1">
                    <li><strong>Vieillesse plafonnée</strong> : 6,90% (tranche 1)</li>
                    <li><strong>Vieillesse déplafonnée</strong> : 0,40% (totalité)</li>
                    <li><strong>AGIRC-ARRCO T1</strong> : 3,15% | <strong>T2</strong> : 8,64%</li>
                    <li><strong>CEG T1</strong> : 0,86% | <strong>CEG T2</strong> : 1,08%</li>
                    <li><strong>CSG + CRDS</strong> : 9,70% (sur 98,25% du brut)</li>
                </ul>
                <p>Contrairement aux cadres, les non-cadres ne paient pas la cotisation CET (0,14%), ce qui leur laisse un net légèrement supérieur.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Exemples de conversion non-cadre</h3>
                <ul>
                    <li><a href="/1500-euros-brut-en-net/" class="text-brand-600 hover:text-brand-700">1 500 € brut</a> → environ 1 170 € net</li>
                    <li><a href="/2000-euros-brut-en-net/" class="text-brand-600 hover:text-brand-700">2 000 € brut</a> → environ 1 560 € net</li>
                    <li><a href="/2500-euros-brut-en-net/" class="text-brand-600 hover:text-brand-700">2 500 € brut</a> → environ 1 950 € net</li>
                    <li><a href="/3000-euros-brut-en-net/" class="text-brand-600 hover:text-brand-700">3 000 € brut</a> → environ 2 340 € net</li>
                </ul>
            """
        },
        {
            "slug": "salaire-brut-net-fonction-publique",
            "title": "Salaire Brut Net Fonction Publique 2025 : Calcul Fonctionnaire",
            "desc": "Calculez votre salaire brut en net dans la fonction publique. Cotisations spécifiques fonctionnaire, taux réduits et simulateur gratuit 2025.",
            "kw": "salaire brut net fonction publique, brut net fonctionnaire, cotisations fonctionnaire, traitement brut net",
            "h1": "Salaire Brut Net <span class=\"text-brand-600\">Fonction Publique</span> 2025",
            "statut_default": "non-cadre",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900 mt-8">Particularités de la fonction publique</h2>
                <p>Les <strong>fonctionnaires</strong> bénéficient de cotisations sociales plus faibles que les salariés du privé. Le taux de cotisations salariales est d'environ <strong>16 à 17%</strong> du traitement brut, contre 22-25% dans le privé.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Cotisations spécifiques fonctionnaire</h3>
                <ul class="space-y-1">
                    <li><strong>Pension civile (retraite)</strong> : 11,10% du traitement indiciaire</li>
                    <li><strong>CSG déductible</strong> : 6,80% (sur 98,25% du brut)</li>
                    <li><strong>CSG non déductible</strong> : 2,40%</li>
                    <li><strong>CRDS</strong> : 0,50%</li>
                    <li><strong>RAFP</strong> : 5% (sur primes, plafonné à 20% du traitement)</li>
                </ul>
                <p>Les fonctionnaires ne cotisent <strong>pas au chômage</strong> ni à la retraite complémentaire AGIRC-ARRCO (ils ont le régime de la CNRACL ou la pension civile).</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Règle de conversion rapide</h3>
                <p>Pour un fonctionnaire, le salaire net représente environ <strong>83% du traitement brut</strong> (hors primes), soit un taux de cotisation d'environ 17%. C'est plus avantageux que le privé.</p>
                <p class="text-sm text-slate-500 mt-4">Note : notre calculateur ci-dessous utilise les taux du secteur privé. Pour un calcul précis fonction publique, appliquez un coefficient d'environ 0,83 à votre traitement brut.</p>
            """
        },
        {
            "slug": "salaire-brut-net-auto-entrepreneur",
            "title": "Salaire Brut Net Auto-Entrepreneur 2025 : Calcul Revenus",
            "desc": "Calculez vos revenus nets en auto-entrepreneur. Cotisations sociales micro-entreprise, abattement fiscal et simulateur 2025.",
            "kw": "auto entrepreneur brut net, revenu net auto entrepreneur, charges micro entreprise, cotisations auto entrepreneur",
            "h1": "Revenus <span class=\"text-brand-600\">Auto-Entrepreneur</span> 2025",
            "statut_default": "non-cadre",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900 mt-8">Le régime auto-entrepreneur (micro-entreprise)</h2>
                <p>Le calcul brut/net pour un <strong>auto-entrepreneur</strong> est très différent du salariat. Il n'y a pas de "salaire brut" à proprement parler, mais un <strong>chiffre d'affaires</strong> sur lequel sont appliquées des cotisations forfaitaires.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Taux de cotisations micro-entreprise 2025</h3>
                <ul class="space-y-1">
                    <li><strong>Prestations de services (BIC)</strong> : 21,2% du CA</li>
                    <li><strong>Prestations de services (BNC)</strong> : 21,1% du CA</li>
                    <li><strong>Activités commerciales (vente)</strong> : 12,3% du CA</li>
                    <li><strong>Professions libérales (CIPAV)</strong> : 21,2% du CA</li>
                </ul>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Versement libératoire de l'impôt</h3>
                <p>Si vous optez pour le <strong>versement libératoire</strong>, un taux supplémentaire s'ajoute :</p>
                <ul>
                    <li>Vente de marchandises : +1%</li>
                    <li>Prestations de services BIC : +1,7%</li>
                    <li>Prestations de services BNC : +2,2%</li>
                </ul>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Exemple concret</h3>
                <p>Pour un consultant en micro-BNC facturant <strong>5 000 € par mois</strong> :</p>
                <ul>
                    <li>Cotisations sociales : 5 000 × 21,1% = 1 055 €</li>
                    <li>Revenu net avant impôt : environ <strong>3 945 €</strong></li>
                </ul>
                <p class="text-sm text-slate-500 mt-4">Note : le calculateur ci-dessous est conçu pour les salariés du privé. Les auto-entrepreneurs doivent appliquer les taux forfaitaires ci-dessus.</p>
            """
        },
        {
            "slug": "salaire-brut-net-alternance-apprentissage",
            "title": "Salaire Brut Net Alternance et Apprentissage 2025",
            "desc": "Calculez votre salaire brut en net en alternance ou apprentissage. Exonérations, grille de rémunération et simulateur 2025.",
            "kw": "salaire alternance brut net, apprentissage brut net, rémunération alternant, salaire apprenti net",
            "h1": "Salaire Brut Net <span class=\"text-brand-600\">Alternance</span> 2025",
            "statut_default": "non-cadre",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900 mt-8">Rémunération en alternance et apprentissage</h2>
                <p>Les apprentis et alternants bénéficient d'un régime spécial : leur rémunération est calculée en <strong>pourcentage du SMIC</strong> et ils sont largement exonérés de cotisations sociales salariales.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Grille de rémunération apprentissage 2025</h3>
                <p>La rémunération minimum dépend de l'âge et de l'année d'apprentissage (base SMIC 2025 : 1 801,80 € brut) :</p>
                <ul class="space-y-1">
                    <li><strong>16-17 ans</strong> : 27% (1ère année) → 39% (2e) → 55% (3e) du SMIC</li>
                    <li><strong>18-20 ans</strong> : 43% → 51% → 67% du SMIC</li>
                    <li><strong>21-25 ans</strong> : 53% → 61% → 78% du SMIC</li>
                    <li><strong>26 ans et +</strong> : 100% du SMIC ou du minimum conventionnel</li>
                </ul>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Brut = Net pour les apprentis ?</h3>
                <p>Bonne nouvelle : pour les apprentis dont la rémunération ne dépasse pas <strong>79% du SMIC</strong>, le salaire brut est égal au salaire net. Les cotisations salariales sont entièrement exonérées.</p>
                <p>Au-delà de 79% du SMIC, seule la part excédentaire est soumise aux cotisations normales.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Contrat de professionnalisation</h3>
                <p>Les alternants en contrat de professionnalisation sont soumis aux cotisations classiques (comme un salarié standard). Leur rémunération minimum est :</p>
                <ul>
                    <li><strong>Moins de 21 ans</strong> : 55% du SMIC (65% si bac pro)</li>
                    <li><strong>21-25 ans</strong> : 70% du SMIC (80% si bac pro)</li>
                    <li><strong>26 ans et +</strong> : 100% du SMIC ou 85% du minimum conventionnel</li>
                </ul>
            """
        },
        {
            "slug": "salaire-brut-net-stage",
            "title": "Salaire Brut Net Stage 2025 : Gratification Stagiaire",
            "desc": "Calculez la gratification de stage brut en net. Seuil d'exonération, cotisations stagiaire et montant minimum 2025.",
            "kw": "gratification stage brut net, salaire stagiaire net, stage rémunération, indemnité stage cotisations",
            "h1": "Gratification de <span class=\"text-brand-600\">Stage</span> Brut Net 2025",
            "statut_default": "non-cadre",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900 mt-8">La gratification de stage en 2025</h2>
                <p>Les stages de plus de 2 mois consécutifs doivent obligatoirement être rémunérés. On parle de <strong>gratification</strong> et non de salaire, car le stagiaire n'est pas un salarié.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Montant minimum 2025</h3>
                <p>La gratification minimum est de <strong>4,35 € par heure</strong>, soit environ <strong>669 € par mois</strong> pour un temps plein (154 heures). Ce montant correspond à 15% du plafond horaire de la Sécurité sociale.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Brut = Net pour les stagiaires</h3>
                <p>Tant que la gratification ne dépasse pas le seuil de <strong>4,35 €/heure</strong> (environ 669 €/mois), elle est <strong>totalement exonérée</strong> de cotisations sociales et d'impôt sur le revenu. Le brut est donc égal au net.</p>
                <p>Si l'employeur verse plus que le minimum, seule la <strong>fraction excédentaire</strong> est soumise aux cotisations sociales classiques.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Exemple</h3>
                <ul>
                    <li><strong>Gratification de 669 €</strong> : 669 € net (pas de cotisations)</li>
                    <li><strong>Gratification de 1 000 €</strong> : les cotisations s'appliquent sur 331 € (1 000 - 669), net ≈ 927 €</li>
                    <li><strong>Gratification de 1 500 €</strong> : cotisations sur 831 €, net ≈ 1 317 €</li>
                </ul>
            """
        },
        {
            "slug": "salaire-brut-net-interim",
            "title": "Salaire Brut Net Intérim 2025 : Calcul Intérimaire",
            "desc": "Calculez votre salaire brut en net en intérim. IFM, ICCP, cotisations intérimaire et simulateur gratuit 2025.",
            "kw": "salaire intérim brut net, brut net intérimaire, IFM, indemnité fin de mission, ICCP",
            "h1": "Salaire Brut Net <span class=\"text-brand-600\">Intérim</span> 2025",
            "statut_default": "non-cadre",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900 mt-8">Rémunération en intérim</h2>
                <p>Les <strong>intérimaires</strong> sont soumis aux mêmes cotisations que les salariés du secteur privé. Le calcul brut/net est donc identique. Cependant, la rémunération totale inclut des primes spécifiques.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Indemnité de Fin de Mission (IFM)</h3>
                <p>À la fin de chaque mission, l'intérimaire perçoit une <strong>IFM de 10%</strong> de la rémunération brute totale. Cette prime compense la précarité de l'emploi.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Indemnité Compensatrice de Congés Payés (ICCP)</h3>
                <p>L'intérimaire reçoit aussi une <strong>ICCP de 10%</strong> calculée sur le brut total + IFM.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Exemple de calcul intérim</h3>
                <p>Pour une mission d'un mois à <strong>2 000 € brut</strong> :</p>
                <ul>
                    <li>Salaire brut de base : 2 000 €</li>
                    <li>IFM (10%) : + 200 €</li>
                    <li>ICCP (10% sur 2 200 €) : + 220 €</li>
                    <li>Brut total : <strong>2 420 €</strong></li>
                    <li>Net (après ~22% de cotisations) : environ <strong>1 888 €</strong></li>
                </ul>
                <p>L'IFM et l'ICCP sont soumises aux cotisations sociales et à l'impôt sur le revenu.</p>
            """
        },
    ]

    for p in pages:
        html = page_head(p["title"], p["desc"], f'{BASE_URL}/{p["slug"]}/', p["kw"])
        html += HEADER
        html += breadcrumb(p["h1"].replace('<span class="text-brand-600">', '').replace('</span>', ''))
        html += f'''
        <section class="px-4 pb-6">
            <div class="mx-auto max-w-4xl">
                <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-6">{p["h1"]}</h1>
            </div>
        </section>'''
        html += calculator_widget(2500, p["statut_default"], "brut")
        html += f'''
        <section class="bg-white border-t border-slate-200 py-12 px-4">
            <div class="mx-auto max-w-4xl prose prose-slate">
                {p["content"]}
            </div>
        </section>'''
        html += links_grid("Pages connexes", RELATED_LINKS)
        html += FOOTER
        html += "\n</body></html>"
        write_page(p["slug"], html)


# ── 2. Pages par période ──────────────────────────────────────────────────────

def gen_period_pages():
    pages = [
        {
            "slug": "salaire-brut-net-mensuel",
            "title": "Salaire Brut Net Mensuel 2025 : Calcul Mois par Mois",
            "desc": "Convertissez votre salaire brut mensuel en net. Cotisations détaillées mois par mois, cadre et non-cadre. Calculateur gratuit 2025.",
            "kw": "salaire brut net mensuel, brut en net par mois, calcul salaire mensuel",
            "h1": "Salaire Brut Net <span class=\"text-brand-600\">Mensuel</span> 2025",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900 mt-8">Calcul mensuel du salaire brut en net</h2>
                <p>Le <strong>salaire brut mensuel</strong> est le montant le plus couramment utilisé dans les contrats de travail et les fiches de paie en France. C'est la base de référence pour calculer vos cotisations et votre salaire net.</p>
                <p>Pour convertir votre brut mensuel en net, il faut déduire environ <strong>22% de cotisations salariales</strong> (non-cadre) ou <strong>25%</strong> (cadre). Le montant exact dépend de votre niveau de salaire par rapport au <strong>plafond de la Sécurité sociale</strong> (3 864 €/mois en 2025).</p>
                <h3 class="text-lg font-semibold text-slate-900 mt-6">Tableau rapide brut → net mensuel</h3>
                <ul>
                    <li><a href="/1500-euros-brut-en-net/" class="text-brand-600">1 500 € brut/mois</a> → ~1 170 € net</li>
                    <li><a href="/2000-euros-brut-en-net/" class="text-brand-600">2 000 € brut/mois</a> → ~1 560 € net</li>
                    <li><a href="/2500-euros-brut-en-net/" class="text-brand-600">2 500 € brut/mois</a> → ~1 950 € net</li>
                    <li><a href="/3000-euros-brut-en-net/" class="text-brand-600">3 000 € brut/mois</a> → ~2 340 € net</li>
                    <li><a href="/4000-euros-brut-en-net/" class="text-brand-600">4 000 € brut/mois</a> → ~3 120 € net</li>
                    <li><a href="/5000-euros-brut-en-net/" class="text-brand-600">5 000 € brut/mois</a> → ~3 900 € net</li>
                </ul>
            """
        },
        {
            "slug": "salaire-brut-net-annuel",
            "title": "Salaire Brut Net Annuel 2025 : Conversion Année Complète",
            "desc": "Convertissez votre salaire brut annuel en net annuel. Calculateur gratuit avec détail des cotisations sur 12 mois.",
            "kw": "salaire brut net annuel, brut en net par an, salaire annuel net, conversion annuelle",
            "h1": "Salaire Brut Net <span class=\"text-brand-600\">Annuel</span> 2025",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900 mt-8">Du brut annuel au net annuel</h2>
                <p>Le <strong>salaire brut annuel</strong> est souvent mentionné dans les offres d'emploi et les contrats de travail. Pour obtenir votre net annuel, divisez par 12 pour obtenir le brut mensuel, puis appliquez les cotisations.</p>
                <p>La formule rapide : <strong>net annuel ≈ brut annuel × 0,78</strong> (non-cadre) ou <strong>× 0,75</strong> (cadre).</p>
                <h3 class="text-lg font-semibold text-slate-900 mt-6">Exemples de conversion annuelle</h3>
                <ul>
                    <li><strong>20 000 € brut/an</strong> → ~15 600 € net/an (~1 300 €/mois)</li>
                    <li><strong>25 000 € brut/an</strong> → ~19 500 € net/an (~1 625 €/mois)</li>
                    <li><strong>30 000 € brut/an</strong> → ~23 400 € net/an (~1 950 €/mois)</li>
                    <li><strong>35 000 € brut/an</strong> → ~27 300 € net/an (~2 275 €/mois)</li>
                    <li><strong>40 000 € brut/an</strong> → ~31 200 € net/an (~2 600 €/mois)</li>
                    <li><strong>50 000 € brut/an</strong> → ~39 000 € net/an (~3 250 €/mois)</li>
                </ul>
                <p>Attention : ces montants sont des estimations. Le calcul exact dépend de votre statut et du plafond de la Sécurité sociale.</p>
            """
        },
        {
            "slug": "salaire-brut-net-horaire",
            "title": "Salaire Brut Net Horaire 2025 : Taux Horaire Brut en Net",
            "desc": "Convertissez votre taux horaire brut en net. Calcul sur base 35h/semaine, SMIC horaire et simulateur gratuit 2025.",
            "kw": "taux horaire brut net, salaire horaire brut en net, smic horaire net, brut en net heure",
            "h1": "Taux Horaire <span class=\"text-brand-600\">Brut Net</span> 2025",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900 mt-8">Convertir un taux horaire brut en net</h2>
                <p>Pour convertir un <strong>taux horaire brut en net</strong>, la méthode est simple : appliquez le même coefficient que pour le salaire mensuel, soit environ <strong>×0,78</strong> (non-cadre) ou <strong>×0,75</strong> (cadre).</p>
                <h3 class="text-lg font-semibold text-slate-900 mt-6">Base de calcul</h3>
                <p>En France, la durée légale du travail est de <strong>35 heures par semaine</strong>, soit <strong>151,67 heures par mois</strong> (35h × 52 semaines / 12 mois). Pour passer du taux horaire au salaire mensuel : taux horaire × 151,67.</p>
                <h3 class="text-lg font-semibold text-slate-900 mt-6">SMIC horaire 2025</h3>
                <ul>
                    <li><strong>SMIC brut horaire</strong> : 11,88 €</li>
                    <li><strong>SMIC net horaire</strong> : ~9,27 € (non-cadre)</li>
                    <li><strong>SMIC mensuel brut</strong> : 1 801,80 €</li>
                    <li><strong>SMIC mensuel net</strong> : ~1 426 €</li>
                </ul>
                <h3 class="text-lg font-semibold text-slate-900 mt-6">Exemples de taux horaires</h3>
                <ul>
                    <li><strong>12 € brut/h</strong> → ~9,36 € net/h → ~1 420 €/mois net</li>
                    <li><strong>15 € brut/h</strong> → ~11,70 € net/h → ~1 775 €/mois net</li>
                    <li><strong>20 € brut/h</strong> → ~15,60 € net/h → ~2 366 €/mois net</li>
                    <li><strong>25 € brut/h</strong> → ~19,50 € net/h → ~2 958 €/mois net</li>
                    <li><strong>30 € brut/h</strong> → ~23,40 € net/h → ~3 550 €/mois net</li>
                </ul>
            """
        },
        {
            "slug": "salaire-brut-net-journalier",
            "title": "Salaire Brut Net Journalier 2025 : Calcul par Jour",
            "desc": "Convertissez votre salaire brut journalier en net. Calcul sur base 7h/jour, TJM freelance et simulateur 2025.",
            "kw": "salaire journalier brut net, TJM brut net, taux journalier net, salaire par jour",
            "h1": "Salaire <span class=\"text-brand-600\">Journalier</span> Brut Net 2025",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900 mt-8">Calcul du salaire journalier brut en net</h2>
                <p>Le <strong>salaire journalier</strong> se calcule sur une base de <strong>7 heures par jour</strong> (35h / 5 jours). Il y a en moyenne <strong>21,67 jours ouvrés par mois</strong> (260 jours / 12 mois).</p>
                <h3 class="text-lg font-semibold text-slate-900 mt-6">Formule de conversion</h3>
                <ul>
                    <li>Salaire mensuel = Taux journalier × 21,67</li>
                    <li>Taux journalier = Salaire mensuel / 21,67</li>
                    <li>Net journalier ≈ Brut journalier × 0,78 (non-cadre)</li>
                </ul>
                <h3 class="text-lg font-semibold text-slate-900 mt-6">Exemples</h3>
                <ul>
                    <li><strong>100 € brut/jour</strong> → ~78 € net/jour → ~2 167 € brut/mois</li>
                    <li><strong>150 € brut/jour</strong> → ~117 € net/jour → ~3 250 € brut/mois</li>
                    <li><strong>200 € brut/jour</strong> → ~156 € net/jour → ~4 334 € brut/mois</li>
                    <li><strong>300 € brut/jour</strong> → ~234 € net/jour → ~6 501 € brut/mois</li>
                    <li><strong>500 € brut/jour</strong> → ~390 € net/jour → ~10 835 € brut/mois</li>
                </ul>
                <h3 class="text-lg font-semibold text-slate-900 mt-6">TJM Freelance</h3>
                <p>Attention : le TJM (Taux Journalier Moyen) d'un freelance ne se convertit pas de la même façon. Un freelance doit prendre en compte ses charges sociales (environ 22-45% selon le statut), ses congés non payés et ses frais professionnels.</p>
            """
        },
        {
            "slug": "taux-horaire-brut-net",
            "title": "Taux Horaire Brut Net 2025 : Convertisseur Horaire",
            "desc": "Convertissez votre taux horaire brut en net et inversement. Base 35h, SMIC horaire et calculateur gratuit 2025.",
            "kw": "taux horaire brut net, convertir taux horaire, brut net heure, salaire horaire calcul",
            "h1": "Convertisseur <span class=\"text-brand-600\">Taux Horaire</span> Brut Net",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900 mt-8">Pourquoi convertir son taux horaire ?</h2>
                <p>Connaître son <strong>taux horaire net</strong> est utile pour comparer des offres d'emploi, négocier un salaire ou évaluer la rentabilité d'heures supplémentaires.</p>
                <h3 class="text-lg font-semibold text-slate-900 mt-6">Comment calculer</h3>
                <p>Le taux horaire brut se trouve sur votre fiche de paie ou se calcule ainsi :</p>
                <ul>
                    <li><strong>Taux horaire brut</strong> = Salaire brut mensuel / 151,67 heures</li>
                    <li><strong>Taux horaire net</strong> = Taux horaire brut × 0,78 (non-cadre) ou × 0,75 (cadre)</li>
                </ul>
                <p>Pour utiliser notre calculateur ci-dessus, entrez votre salaire mensuel brut (taux horaire × 151,67).</p>
                <h3 class="text-lg font-semibold text-slate-900 mt-6">Grille indicative</h3>
                <ul>
                    <li><strong>SMIC</strong> : 11,88 € brut/h → 9,27 € net/h</li>
                    <li><strong>14 €/h brut</strong> → 10,92 € net/h (2 123 € brut/mois)</li>
                    <li><strong>18 €/h brut</strong> → 14,04 € net/h (2 730 € brut/mois)</li>
                    <li><strong>22 €/h brut</strong> → 17,16 € net/h (3 337 € brut/mois)</li>
                    <li><strong>30 €/h brut</strong> → 23,40 € net/h (4 550 € brut/mois)</li>
                </ul>
            """
        },
    ]

    for p in pages:
        html = page_head(p["title"], p["desc"], f'{BASE_URL}/{p["slug"]}/', p["kw"])
        html += HEADER
        html += breadcrumb(p["h1"].replace('<span class="text-brand-600">', '').replace('</span>', ''))
        html += f'''
        <section class="px-4 pb-6">
            <div class="mx-auto max-w-4xl">
                <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-6">{p["h1"]}</h1>
            </div>
        </section>'''
        html += calculator_widget(2500, "non-cadre", "brut")
        html += f'''
        <section class="bg-white border-t border-slate-200 py-12 px-4">
            <div class="mx-auto max-w-4xl prose prose-slate">
                {p["content"]}
            </div>
        </section>'''
        html += links_grid("Pages connexes", RELATED_LINKS)
        html += FOOTER
        html += "\n</body></html>"
        write_page(p["slug"], html)


# ── 3. Pages de contenu éducatif ──────────────────────────────────────────────

def gen_content_pages():
    pages = [
        {
            "slug": "difference-salaire-brut-net",
            "title": "Différence entre Salaire Brut et Net 2025 : Explications Complètes",
            "desc": "Comprendre la différence entre salaire brut et salaire net. Cotisations sociales, calcul détaillé et exemples concrets pour 2025.",
            "kw": "différence brut net, c'est quoi le salaire brut, salaire brut vs net, explication brut net",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900">Qu'est-ce que le salaire brut ?</h2>
                <p>Le <strong>salaire brut</strong> est la rémunération totale inscrite sur votre contrat de travail, avant toute déduction. C'est le montant que votre employeur s'engage à vous verser. Il inclut votre salaire de base, les éventuelles primes, heures supplémentaires et avantages en nature.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Qu'est-ce que le salaire net ?</h2>
                <p>Le <strong>salaire net</strong> (ou "net à payer avant impôt") est ce que vous recevez effectivement sur votre compte bancaire, après déduction de toutes les cotisations sociales salariales. Depuis 2019, le <strong>net après impôt</strong> tient aussi compte du prélèvement à la source.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Que se passe-t-il entre le brut et le net ?</h2>
                <p>Entre votre salaire brut et votre salaire net, plusieurs cotisations sont prélevées :</p>
                <ul class="space-y-2">
                    <li><strong>Assurance vieillesse</strong> (retraite de base) : 6,90% + 0,40%</li>
                    <li><strong>Retraite complémentaire</strong> (AGIRC-ARRCO) : 3,15% à 8,64%</li>
                    <li><strong>CSG</strong> (Contribution Sociale Généralisée) : 9,20% sur 98,25% du brut</li>
                    <li><strong>CRDS</strong> : 0,50% sur 98,25% du brut</li>
                    <li><strong>CEG</strong> : 0,86% à 1,08%</li>
                </ul>
                <p>Au total, ces cotisations représentent environ <strong>22% pour un non-cadre</strong> et <strong>25% pour un cadre</strong>.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Les différents "nets" sur votre fiche de paie</h2>
                <ul class="space-y-2">
                    <li><strong>Net à payer avant impôt</strong> : brut - cotisations salariales. C'est le "salaire net" classique.</li>
                    <li><strong>Net imposable</strong> : net + CSG non déductible + CRDS. Sert de base au calcul de l'impôt.</li>
                    <li><strong>Net à payer</strong> : net avant impôt - prélèvement à la source. C'est ce qui arrive sur votre compte.</li>
                </ul>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Formule rapide de conversion</h2>
                <p>Pour une estimation rapide :</p>
                <ul>
                    <li><strong>Non-cadre</strong> : Salaire net ≈ Salaire brut × 0,78</li>
                    <li><strong>Cadre</strong> : Salaire net ≈ Salaire brut × 0,75</li>
                    <li><strong>Fonction publique</strong> : Salaire net ≈ Salaire brut × 0,83</li>
                </ul>
                <p>Pour un calcul précis, utilisez notre <a href="/" class="text-brand-600 hover:text-brand-700">calculateur brut/net</a>.</p>
            """
        },
        {
            "slug": "cotisations-sociales-salariales",
            "title": "Cotisations Sociales Salariales 2025 : Détail et Taux Complets",
            "desc": "Détail complet des cotisations sociales salariales 2025. Taux, assiettes, plafonds et explication de chaque cotisation prélevée sur votre salaire brut.",
            "kw": "cotisations sociales salariales, charges salariales, taux cotisations 2025, détail cotisations",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900">Les cotisations sociales en France</h2>
                <p>Les <strong>cotisations sociales salariales</strong> sont des prélèvements obligatoires sur votre salaire brut qui financent la protection sociale : retraite, maladie, chômage, etc. Voici le détail complet pour 2025.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Tableau des cotisations salariales 2025</h2>
                <table class="w-full text-sm border-collapse mt-4">
                    <thead><tr class="border-b-2 border-slate-300">
                        <th class="py-2 text-left">Cotisation</th><th class="py-2 text-right">Taux</th><th class="py-2 text-right">Assiette</th>
                    </tr></thead>
                    <tbody>
                        <tr class="border-b border-slate-100"><td class="py-2">Vieillesse plafonnée</td><td class="py-2 text-right">6,90%</td><td class="py-2 text-right">Tranche 1 (≤ PSS)</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">Vieillesse déplafonnée</td><td class="py-2 text-right">0,40%</td><td class="py-2 text-right">Totalité</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">AGIRC-ARRCO T1</td><td class="py-2 text-right">3,15%</td><td class="py-2 text-right">Tranche 1</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">AGIRC-ARRCO T2</td><td class="py-2 text-right">8,64%</td><td class="py-2 text-right">Tranche 2 (&gt; PSS)</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">CEG T1</td><td class="py-2 text-right">0,86%</td><td class="py-2 text-right">Tranche 1</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">CEG T2</td><td class="py-2 text-right">1,08%</td><td class="py-2 text-right">Tranche 2</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">CET (cadres uniquement)</td><td class="py-2 text-right">0,14%</td><td class="py-2 text-right">Totalité</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">CSG déductible</td><td class="py-2 text-right">6,80%</td><td class="py-2 text-right">98,25% du brut</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">CSG non déductible</td><td class="py-2 text-right">2,40%</td><td class="py-2 text-right">98,25% du brut</td></tr>
                        <tr><td class="py-2">CRDS</td><td class="py-2 text-right">0,50%</td><td class="py-2 text-right">98,25% du brut</td></tr>
                    </tbody>
                </table>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Le Plafond de la Sécurité Sociale (PSS)</h2>
                <p>En 2025, le PSS est de <strong>3 864 €/mois</strong> (46 368 €/an). Les cotisations en "Tranche 1" s'appliquent jusqu'à ce plafond. Au-delà, ce sont les cotisations "Tranche 2" qui prennent le relais.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">À quoi servent ces cotisations ?</h2>
                <ul class="space-y-2">
                    <li><strong>Vieillesse</strong> : finance votre retraite de base (régime général)</li>
                    <li><strong>AGIRC-ARRCO</strong> : finance votre retraite complémentaire (points)</li>
                    <li><strong>CSG</strong> : finance la Sécurité sociale (maladie, famille, etc.)</li>
                    <li><strong>CRDS</strong> : rembourse la dette sociale</li>
                    <li><strong>CEG</strong> : équilibre le régime de retraite complémentaire</li>
                </ul>
            """
        },
        {
            "slug": "salaire-net-avant-apres-impot",
            "title": "Salaire Net Avant et Après Impôt 2025 : Comprendre la Différence",
            "desc": "Différence entre net avant impôt et net après impôt. Prélèvement à la source, net imposable et calcul détaillé 2025.",
            "kw": "net avant impôt, net après impôt, prélèvement à la source, net imposable, salaire net impôt",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900">Net avant impôt vs net après impôt</h2>
                <p>Depuis janvier 2019, l'<strong>impôt sur le revenu</strong> est prélevé directement sur votre salaire. Votre fiche de paie affiche donc deux montants nets distincts.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Le net avant impôt</h2>
                <p>Le <strong>net avant impôt</strong> (ou "net à payer avant impôt sur le revenu") est votre salaire brut moins les cotisations sociales salariales. C'est le montant historiquement appelé "salaire net".</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Le prélèvement à la source (PAS)</h2>
                <p>Le <strong>prélèvement à la source</strong> est calculé sur votre <strong>net imposable</strong> (légèrement différent du net à payer). Le taux est déterminé par l'administration fiscale en fonction de vos revenus de l'année précédente.</p>
                <p>Trois options de taux :</p>
                <ul>
                    <li><strong>Taux personnalisé</strong> : calculé sur les revenus de votre foyer fiscal</li>
                    <li><strong>Taux individualisé</strong> : pour les couples avec des revenus différents</li>
                    <li><strong>Taux neutre</strong> : grille par défaut si vous ne souhaitez pas communiquer votre situation</li>
                </ul>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Exemple concret</h2>
                <p>Pour un salaire brut de 2 500 €/mois (non-cadre, célibataire) :</p>
                <ul>
                    <li>Net avant impôt : ~1 950 €</li>
                    <li>Prélèvement à la source (~5%) : ~98 €</li>
                    <li><strong>Net après impôt</strong> : ~1 852 €</li>
                </ul>
            """
        },
        {
            "slug": "cout-employeur",
            "title": "Coût Employeur 2025 : Calcul du Super-Brut et Charges Patronales",
            "desc": "Calculez le coût total employeur (super-brut). Détail des cotisations patronales, charges et simulateur gratuit 2025.",
            "kw": "coût employeur, super brut, charges patronales, cotisations patronales, coût salarié entreprise",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900">Qu'est-ce que le coût employeur ?</h2>
                <p>Le <strong>coût employeur</strong> (ou "super-brut") est le montant total que l'entreprise dépense pour employer un salarié. Il comprend le salaire brut + les cotisations patronales. En moyenne, le coût employeur représente environ <strong>1,45 fois le salaire brut</strong>.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Cotisations patronales 2025</h2>
                <table class="w-full text-sm border-collapse mt-4">
                    <thead><tr class="border-b-2 border-slate-300">
                        <th class="py-2 text-left">Cotisation</th><th class="py-2 text-right">Taux</th><th class="py-2 text-right">Assiette</th>
                    </tr></thead>
                    <tbody>
                        <tr class="border-b border-slate-100"><td class="py-2">Maladie</td><td class="py-2 text-right">7,00%</td><td class="py-2 text-right">Totalité</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">Vieillesse plafonnée</td><td class="py-2 text-right">8,55%</td><td class="py-2 text-right">Tranche 1</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">Vieillesse déplafonnée</td><td class="py-2 text-right">2,02%</td><td class="py-2 text-right">Totalité</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">Allocations familiales</td><td class="py-2 text-right">3,45% / 5,25%</td><td class="py-2 text-right">Totalité</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">Chômage</td><td class="py-2 text-right">4,05%</td><td class="py-2 text-right">Tranche A</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">AGIRC-ARRCO T1</td><td class="py-2 text-right">4,72%</td><td class="py-2 text-right">Tranche 1</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">AGIRC-ARRCO T2</td><td class="py-2 text-right">12,95%</td><td class="py-2 text-right">Tranche 2</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">AT/MP</td><td class="py-2 text-right">~1,00%</td><td class="py-2 text-right">Totalité</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">CEG T1 / T2</td><td class="py-2 text-right">1,29% / 1,62%</td><td class="py-2 text-right">T1 / T2</td></tr>
                        <tr><td class="py-2">CET</td><td class="py-2 text-right">0,21%</td><td class="py-2 text-right">Totalité</td></tr>
                    </tbody>
                </table>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Exemples de coût employeur</h2>
                <ul>
                    <li><strong>SMIC (1 802 € brut)</strong> → coût employeur : ~2 067 € (allègements de charges inclus)</li>
                    <li><strong>2 500 € brut</strong> → coût employeur : ~3 600 €</li>
                    <li><strong>4 000 € brut</strong> → coût employeur : ~5 800 €</li>
                    <li><strong>6 000 € brut</strong> → coût employeur : ~8 760 €</li>
                </ul>
            """
        },
        {
            "slug": "lire-fiche-de-paie",
            "title": "Comprendre sa Fiche de Paie 2025 : Guide Ligne par Ligne",
            "desc": "Guide complet pour lire et comprendre votre fiche de paie. Chaque ligne expliquée : brut, cotisations, net imposable, net à payer.",
            "kw": "comprendre fiche de paie, lire bulletin de salaire, explication fiche de paie, bulletin de paie 2025",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900">Les zones de votre fiche de paie</h2>
                <p>Votre <strong>bulletin de salaire</strong> se divise en plusieurs zones distinctes. Voici un guide pour comprendre chacune d'entre elles.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">1. Identification (en-tête)</h3>
                <p>Informations sur l'employeur (SIRET, convention collective, code APE) et le salarié (nom, poste, ancienneté, numéro de sécurité sociale).</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">2. Rémunération brute</h3>
                <p>Salaire de base, heures supplémentaires, primes, avantages en nature. Le total constitue votre <strong>salaire brut</strong>.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">3. Cotisations sociales</h3>
                <p>Depuis 2018, les cotisations sont regroupées en 5 grandes catégories :</p>
                <ul>
                    <li><strong>Santé</strong> : maladie, complémentaire santé</li>
                    <li><strong>Accidents du travail</strong></li>
                    <li><strong>Retraite</strong> : vieillesse de base + complémentaire</li>
                    <li><strong>Famille</strong> : allocations familiales</li>
                    <li><strong>Chômage</strong> : assurance chômage</li>
                </ul>
                <p>Chaque ligne indique la base, le taux salarial et le taux patronal.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">4. Net imposable</h3>
                <p>Le <strong>net imposable</strong> = brut - cotisations salariales + CSG non déductible + CRDS. C'est la base du prélèvement à la source.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">5. Net à payer</h3>
                <p>Le <strong>net à payer avant impôt</strong>, puis le prélèvement à la source, puis le <strong>net à payer</strong> final viré sur votre compte.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">6. Cumuls annuels</h3>
                <p>Totaux depuis janvier : brut cumulé, net imposable cumulé, impôt prélevé cumulé. Utile pour votre déclaration de revenus.</p>
            """
        },
        {
            "slug": "smic-brut-net-2025",
            "title": "SMIC 2025 Brut et Net : Montant Mensuel, Horaire et Annuel",
            "desc": "SMIC 2025 brut et net : montant mensuel (1 801,80€ brut → 1 426€ net), horaire (11,88€) et annuel. Calcul détaillé et évolution.",
            "kw": "smic 2025, smic brut net, smic mensuel 2025, smic horaire 2025, smic net",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900">Le SMIC en 2025</h2>
                <p>Le <strong>SMIC</strong> (Salaire Minimum Interprofessionnel de Croissance) est le salaire minimum légal en France. Il est revalorisé chaque année au 1er janvier.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Montants du SMIC 2025</h2>
                <table class="w-full text-sm border-collapse mt-4">
                    <thead><tr class="border-b-2 border-slate-300">
                        <th class="py-2 text-left">Période</th><th class="py-2 text-right">Brut</th><th class="py-2 text-right">Net (≈)</th>
                    </tr></thead>
                    <tbody>
                        <tr class="border-b border-slate-100"><td class="py-2">Horaire</td><td class="py-2 text-right">11,88 €</td><td class="py-2 text-right">9,27 €</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">Journalier (7h)</td><td class="py-2 text-right">83,16 €</td><td class="py-2 text-right">64,89 €</td></tr>
                        <tr class="border-b border-slate-100"><td class="py-2">Mensuel (151,67h)</td><td class="py-2 text-right">1 801,80 €</td><td class="py-2 text-right">1 426 €</td></tr>
                        <tr><td class="py-2">Annuel</td><td class="py-2 text-right">21 621,60 €</td><td class="py-2 text-right">17 112 €</td></tr>
                    </tbody>
                </table>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Évolution récente du SMIC</h2>
                <ul>
                    <li><strong>2024</strong> : 11,65 €/h brut (1 766,92 €/mois)</li>
                    <li><strong>2023</strong> : 11,52 €/h brut (1 747,20 €/mois)</li>
                    <li><strong>2022</strong> : 11,07 €/h brut (1 678,95 €/mois)</li>
                </ul>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Qui est concerné ?</h2>
                <p>Environ <strong>17% des salariés</strong> en France sont rémunérés au SMIC. Certaines conventions collectives prévoient des minimums supérieurs au SMIC.</p>
            """
        },
        {
            "slug": "salaire-moyen-france",
            "title": "Salaire Moyen en France 2025 : Statistiques Brut et Net",
            "desc": "Salaire moyen et médian en France en 2025. Statistiques par âge, secteur, région. Brut et net comparés.",
            "kw": "salaire moyen france, salaire médian france, salaire moyen 2025, statistiques salaire",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900">Salaire moyen vs salaire médian</h2>
                <p>Le <strong>salaire moyen</strong> est la moyenne de tous les salaires : il est tiré vers le haut par les très hauts revenus. Le <strong>salaire médian</strong> est plus représentatif : la moitié des salariés gagne plus, l'autre moitié gagne moins.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Chiffres clés 2025</h2>
                <ul>
                    <li><strong>Salaire brut moyen</strong> : environ 2 630 €/mois (privé, temps plein)</li>
                    <li><strong>Salaire net moyen</strong> : environ 2 050 €/mois</li>
                    <li><strong>Salaire brut médian</strong> : environ 2 100 €/mois</li>
                    <li><strong>Salaire net médian</strong> : environ 1 640 €/mois</li>
                </ul>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Par catégorie socioprofessionnelle</h2>
                <ul>
                    <li><strong>Cadres</strong> : ~4 500 € brut/mois (~3 375 € net)</li>
                    <li><strong>Professions intermédiaires</strong> : ~2 600 € brut/mois (~2 028 € net)</li>
                    <li><strong>Employés</strong> : ~1 900 € brut/mois (~1 482 € net)</li>
                    <li><strong>Ouvriers</strong> : ~2 000 € brut/mois (~1 560 € net)</li>
                </ul>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Où vous situez-vous ?</h2>
                <p>Utilisez notre <a href="/" class="text-brand-600 hover:text-brand-700">calculateur brut/net</a> pour convertir votre salaire et le comparer aux statistiques nationales.</p>
            """
        },
        {
            "slug": "negocier-salaire",
            "title": "Négocier son Salaire 2025 : Guide et Conseils Pratiques",
            "desc": "Comment négocier son salaire à l'embauche ou lors d'un entretien annuel. Conseils pratiques, arguments et erreurs à éviter.",
            "kw": "négocier salaire, négociation salaire embauche, augmentation salaire, demander augmentation",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900">Pourquoi négocier son salaire ?</h2>
                <p>Ne pas négocier peut vous coûter des dizaines de milliers d'euros sur votre carrière. Même une différence de <strong>100 € brut/mois</strong> représente 1 200 € brut/an, soit plus de 40 000 € sur 30 ans (sans compter les augmentations en pourcentage).</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Négocier à l'embauche</h2>
                <ul>
                    <li><strong>Renseignez-vous</strong> sur les salaires du marché pour votre poste et votre région</li>
                    <li><strong>Demandez en brut annuel</strong> : c'est la norme en France</li>
                    <li><strong>Donnez une fourchette</strong> plutôt qu'un chiffre précis (ex: "entre 35 000 et 40 000 € brut annuel")</li>
                    <li><strong>Ne négociez pas que le salaire</strong> : télétravail, tickets restaurant, mutuelle, RTT sont aussi négociables</li>
                </ul>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Négocier une augmentation</h2>
                <ul>
                    <li><strong>Préparez vos arguments</strong> : résultats concrets, responsabilités élargies, compétences acquises</li>
                    <li><strong>Choisissez le bon moment</strong> : entretien annuel, après un succès, lors d'une prise de responsabilité</li>
                    <li><strong>Quantifiez</strong> : demandez un montant précis, pas "une petite augmentation"</li>
                    <li><strong>Pensez en net</strong> : vérifiez l'impact réel avec notre <a href="/" class="text-brand-600 hover:text-brand-700">calculateur</a></li>
                </ul>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Brut vs net : la vraie différence</h2>
                <p>Attention : une augmentation de 200 € brut ne représente qu'environ <strong>156 € net de plus par mois</strong> (non-cadre). Pensez toujours à convertir pour connaître l'impact réel sur votre pouvoir d'achat.</p>
            """
        },
        {
            "slug": "salaire-net-imposable",
            "title": "Salaire Net Imposable 2025 : Définition et Calcul",
            "desc": "Qu'est-ce que le salaire net imposable ? Différence avec le net à payer, calcul détaillé et impact sur le prélèvement à la source.",
            "kw": "salaire net imposable, net imposable calcul, différence net imposable net à payer",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900">Qu'est-ce que le net imposable ?</h2>
                <p>Le <strong>salaire net imposable</strong> est le montant utilisé comme base pour calculer votre impôt sur le revenu et votre prélèvement à la source. Il est <strong>supérieur au net à payer</strong> car il réintègre certaines cotisations non déductibles fiscalement.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Formule de calcul</h2>
                <p><strong>Net imposable = Salaire brut - Cotisations salariales déductibles</strong></p>
                <p>Concrètement : Net imposable = Net à payer + CSG non déductible (2,40%) + CRDS (0,50%)</p>
                <p>Le net imposable est donc environ <strong>2 à 3% supérieur</strong> au net à payer.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Exemple</h2>
                <p>Pour 2 500 € brut mensuel (non-cadre) :</p>
                <ul>
                    <li>Net à payer avant impôt : ~1 950 €</li>
                    <li>CSG non déductible (2,40% × 98,25% × 2 500) : ~59 €</li>
                    <li>CRDS (0,50% × 98,25% × 2 500) : ~12 €</li>
                    <li><strong>Net imposable</strong> : ~2 021 €</li>
                </ul>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Impact sur l'impôt</h2>
                <p>C'est le net imposable (× 12 mois) qui détermine votre tranche d'imposition et votre taux de prélèvement à la source. Un net imposable plus élevé signifie un impôt potentiellement plus élevé.</p>
            """
        },
        {
            "slug": "avantages-en-nature",
            "title": "Avantages en Nature 2025 : Impact sur le Salaire Brut et Net",
            "desc": "Comment les avantages en nature (voiture, logement, repas) impactent votre salaire brut et net. Évaluation et cotisations 2025.",
            "kw": "avantages en nature, voiture de fonction brut net, logement de fonction, avantages salaire",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900">Qu'est-ce qu'un avantage en nature ?</h2>
                <p>Un <strong>avantage en nature</strong> est un bien ou service fourni gratuitement par l'employeur (ou à prix réduit) : voiture de fonction, logement, repas, téléphone... Ces avantages s'ajoutent à votre salaire brut et sont soumis aux cotisations et à l'impôt.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Principaux avantages en nature</h2>
                <ul class="space-y-2">
                    <li><strong>Voiture de fonction</strong> : évaluation forfaitaire de 9% à 12% du prix d'achat TTC/an, ou au réel (usage personnel)</li>
                    <li><strong>Logement de fonction</strong> : évaluation forfaitaire selon barème ou valeur locative</li>
                    <li><strong>Repas</strong> : 5,35 € par repas en 2025 (forfait URSSAF)</li>
                    <li><strong>Téléphone/ordinateur</strong> : 10% du prix d'achat par an (usage mixte)</li>
                </ul>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Impact sur votre salaire</h2>
                <p>L'avantage en nature est <strong>ajouté au brut</strong> puis <strong>retiré du net</strong>. Résultat : vous payez les cotisations et l'impôt sur cet avantage, mais vous n'en voyez pas la valeur dans votre virement.</p>
                <p>Exemple : voiture évaluée à 300 €/mois → votre brut augmente de 300 €, vos cotisations augmentent, mais votre net à payer diminue d'environ 230 €.</p>
            """
        },
        {
            "slug": "heures-supplementaires-brut-net",
            "title": "Heures Supplémentaires Brut en Net 2025 : Calcul et Exonérations",
            "desc": "Calculez vos heures supplémentaires brut en net. Majoration 25-50%, exonération fiscale et plafond 2025.",
            "kw": "heures supplémentaires brut net, calcul heures sup, majoration heures supplémentaires, exonération heures sup",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900">Majoration des heures supplémentaires</h2>
                <p>Les heures travaillées au-delà de 35h/semaine sont majorées :</p>
                <ul>
                    <li><strong>De la 36e à la 43e heure</strong> : +25% du taux horaire</li>
                    <li><strong>À partir de la 44e heure</strong> : +50% du taux horaire</li>
                </ul>
                <p>Une convention collective peut prévoir des taux différents (minimum 10%).</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Exonération fiscale</h2>
                <p>Les heures supplémentaires bénéficient d'une <strong>exonération d'impôt sur le revenu</strong> dans la limite de <strong>7 500 € net par an</strong>. Elles restent soumises aux cotisations sociales mais bénéficient d'une <strong>réduction de cotisations salariales</strong> de 11,31%.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Exemple de calcul</h2>
                <p>Pour un salarié à 15 €/heure brut faisant 4 heures sup par semaine :</p>
                <ul>
                    <li>Taux majoré (25%) : 15 € × 1,25 = 18,75 €/h brut</li>
                    <li>4h × 18,75 € × 4,33 semaines = 324,75 € brut/mois en heures sup</li>
                    <li>Réduction cotisations salariales (-11,31%) : économie de ~37 €</li>
                    <li>Net supplémentaire : environ <strong>290 €/mois</strong> (exonéré d'impôt)</li>
                </ul>
            """
        },
        {
            "slug": "prime-brut-en-net",
            "title": "Prime Brut en Net 2025 : Calcul des Primes et Cotisations",
            "desc": "Convertissez une prime brute en net. Primes exceptionnelles, 13ème mois, intéressement : cotisations et fiscalité 2025.",
            "kw": "prime brut en net, calcul prime nette, prime exceptionnelle cotisations, convertir prime",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900">Comment convertir une prime brute en net ?</h2>
                <p>Les primes versées par l'employeur sont soumises aux <strong>mêmes cotisations sociales</strong> que le salaire. Pour convertir une prime brute en net, appliquez le même taux que pour votre salaire : environ <strong>22% pour un non-cadre</strong> et <strong>25% pour un cadre</strong>.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Types de primes</h2>
                <ul class="space-y-2">
                    <li><strong>Prime exceptionnelle</strong> : soumise à cotisations et impôt (sauf PPV sous conditions)</li>
                    <li><strong>13ème mois</strong> : soumis à cotisations et impôt (un mois de salaire supplémentaire)</li>
                    <li><strong>Prime d'ancienneté</strong> : intégrée au brut mensuel, cotisations classiques</li>
                    <li><strong>Intéressement/participation</strong> : exonéré de cotisations si placé sur un PEE/PERCO (CSG/CRDS dues)</li>
                    <li><strong>Prime de Partage de la Valeur (PPV)</strong> : exonérée de cotisations et d'impôt jusqu'à 3 000 € (ou 6 000 € avec accord d'intéressement)</li>
                </ul>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Exemples de conversion</h2>
                <ul>
                    <li><strong>Prime de 500 € brut</strong> → ~390 € net (non-cadre) / ~375 € net (cadre)</li>
                    <li><strong>Prime de 1 000 € brut</strong> → ~780 € net (non-cadre) / ~750 € net (cadre)</li>
                    <li><strong>Prime de 2 000 € brut</strong> → ~1 560 € net (non-cadre) / ~1 500 € net (cadre)</li>
                </ul>
                <p>Attention : la prime peut vous faire changer de tranche d'imposition le mois où elle est versée, augmentant temporairement votre prélèvement à la source.</p>
            """
        },
        {
            "slug": "13eme-mois-brut-net",
            "title": "13ème Mois Brut Net 2025 : Calcul et Cotisations",
            "desc": "Calculez votre 13ème mois brut en net. Cotisations sociales, impact fiscal et modalités de versement 2025.",
            "kw": "13ème mois brut net, treizième mois cotisations, prime 13eme mois net, calcul 13eme mois",
            "content": """
                <h2 class="text-xl font-semibold text-slate-900">Qu'est-ce que le 13ème mois ?</h2>
                <p>Le <strong>13ème mois</strong> est une prime conventionnelle ou contractuelle correspondant généralement à un mois de salaire supplémentaire. Il n'est pas obligatoire légalement mais peut être prévu par votre convention collective ou votre contrat de travail.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Cotisations sur le 13ème mois</h2>
                <p>Le 13ème mois est soumis aux <strong>mêmes cotisations sociales</strong> que votre salaire habituel. Il est intégralement soumis à l'impôt sur le revenu.</p>
                <p>Pour un 13ème mois de 2 500 € brut (non-cadre) : net ≈ <strong>1 950 €</strong>, avant prélèvement à la source.</p>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Modalités de versement</h2>
                <ul>
                    <li><strong>En une fois</strong> : généralement en décembre</li>
                    <li><strong>En deux fois</strong> : moitié en juin, moitié en décembre</li>
                    <li><strong>Mensualisé</strong> : 1/12ème ajouté chaque mois au salaire</li>
                </ul>

                <h2 class="text-xl font-semibold text-slate-900 mt-8">Impact sur l'impôt</h2>
                <p>Si votre 13ème mois est versé en une fois, votre prélèvement à la source sera plus élevé ce mois-là. Mais le trop-perçu sera régularisé lors de votre déclaration annuelle. Si le 13ème mois est mensualisé, l'impact fiscal est lissé.</p>
            """
        },
    ]

    for p in pages:
        html = page_head(p["title"], p["desc"], f'{BASE_URL}/{p["slug"]}/', p["kw"])
        html += HEADER
        html += breadcrumb(p["title"].split(" :")[0].split(" 2025")[0])
        html += f'''
        <section class="px-4 pb-6">
            <div class="mx-auto max-w-4xl">
                <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 mb-6">{p["title"].split(" :")[0]}</h1>
            </div>
        </section>'''
        html += calculator_widget(2500, "non-cadre", "brut")
        html += f'''
        <section class="bg-white border-t border-slate-200 py-12 px-4">
            <div class="mx-auto max-w-4xl prose prose-slate">
                {p["content"]}
            </div>
        </section>'''
        html += links_grid("Pages connexes", RELATED_LINKS)
        html += FOOTER
        html += "\n</body></html>"
        write_page(p["slug"], html)


# ── 4. Pages outils complémentaires ──────────────────────────────────────────

def gen_tool_pages():
    # Calculateur coût employeur
    html = page_head(
        "Calculateur Coût Employeur 2025 : Simulez le Super-Brut",
        "Calculez le coût total employeur (super-brut) pour un salarié. Cotisations patronales détaillées et simulateur gratuit 2025.",
        f"{BASE_URL}/calculateur-cout-employeur/",
        "calculateur coût employeur, super brut, charges patronales, coût salarié"
    )
    html += HEADER
    html += breadcrumb("Calculateur Coût Employeur")
    html += '''
        <section class="px-4 pb-6">
            <div class="mx-auto max-w-4xl">
                <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 mb-6">Calculateur <span class="text-brand-600">Coût Employeur</span> 2025</h1>
                <p class="text-slate-500">Calculez le coût total pour l'entreprise (super-brut) en incluant les cotisations patronales.</p>
            </div>
        </section>

        <section class="py-12 px-4">
            <div class="mx-auto max-w-3xl">
                <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-1">Salaire brut mensuel</label>
                            <input type="number" id="widget-input" value="2500" min="0" max="20000" step="50"
                                class="w-full rounded-lg border border-slate-200 px-3 py-2 text-lg font-bold text-slate-900 focus:border-brand-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-1">Statut</label>
                            <select id="widget-statut" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900">
                                <option value="non-cadre" selected>Non-cadre</option>
                                <option value="cadre">Cadre</option>
                            </select>
                        </div>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
                        <div class="rounded-xl bg-brand-50 border border-brand-100 p-4 text-center">
                            <p class="text-xs text-brand-600 font-medium">Coût employeur</p>
                            <p class="text-2xl font-bold text-slate-900" id="res-cout">—</p>
                            <p class="text-xs text-slate-500">par mois</p>
                        </div>
                        <div class="rounded-xl bg-slate-50 border border-slate-200 p-4 text-center">
                            <p class="text-xs text-slate-600 font-medium">Cotisations patronales</p>
                            <p class="text-2xl font-bold text-slate-900" id="res-patron">—</p>
                        </div>
                        <div class="rounded-xl bg-slate-50 border border-slate-200 p-4 text-center">
                            <p class="text-xs text-slate-600 font-medium">Net salarié</p>
                            <p class="text-2xl font-bold text-slate-900" id="res-net">—</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    <script>
    (function() {
        const inp = document.getElementById('widget-input');
        const sel = document.getElementById('widget-statut');
        function calc() {
            const r = calculerBrutVersNet(parseFloat(inp.value)||0, sel.value, 1);
            document.getElementById('res-cout').textContent = formatMoney(r.coutEmployeur);
            document.getElementById('res-patron').textContent = formatMoney(r.totalPatronal);
            document.getElementById('res-net').textContent = formatMoney(r.netAvantImpot);
        }
        inp.addEventListener('input', calc);
        sel.addEventListener('change', calc);
        calc();
    })();
    </script>

        <section class="bg-white border-t border-slate-200 py-12 px-4">
            <div class="mx-auto max-w-4xl prose prose-slate">
                <h2 class="text-xl font-semibold text-slate-900">Comprendre le coût employeur</h2>
                <p>Le <strong>coût employeur</strong> représente le montant total que l'entreprise dépense pour un salarié. Il comprend le salaire brut auquel s'ajoutent les cotisations patronales (environ 45% du brut).</p>
                <p>Pour un salaire brut de 2 500 €, le coût employeur est d'environ <strong>3 625 €</strong>. L'entreprise dépense donc 45% de plus que ce qu'elle vous verse en brut.</p>
                <h3 class="text-lg font-semibold text-slate-900 mt-6">Ratio net perçu / coût employeur</h3>
                <p>Sur les 3 625 € dépensés par l'employeur, le salarié ne perçoit qu'environ 1 950 € net. Cela signifie que le salarié touche environ <strong>54% du coût total</strong>. Le reste finance la protection sociale.</p>
            </div>
        </section>'''
    html += links_grid("Pages connexes", RELATED_LINKS)
    html += FOOTER
    html += "\n</body></html>"
    write_page("calculateur-cout-employeur", html)

    # Comparateur salaire par pays
    html = page_head(
        "Comparateur Salaire Net par Pays 2025 : France, Belgique, Suisse",
        "Comparez le salaire net dans différents pays européens. France vs Belgique vs Suisse vs Luxembourg : cotisations et pouvoir d'achat.",
        f"{BASE_URL}/comparateur-salaire-net-par-pays/",
        "comparateur salaire pays, salaire net france belgique suisse, salaire europe comparaison"
    )
    html += HEADER
    html += breadcrumb("Comparateur Salaire Net par Pays")
    html += '''
        <section class="px-4 pb-6">
            <div class="mx-auto max-w-4xl">
                <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 mb-6">Comparateur <span class="text-brand-600">Salaire Net par Pays</span></h1>
                <p class="text-slate-500">Comparez le salaire net pour un même brut dans différents pays francophones européens.</p>
            </div>
        </section>

        <section class="bg-white border-t border-slate-200 py-12 px-4">
            <div class="mx-auto max-w-4xl">
                <h2 class="text-xl font-bold text-slate-900 mb-6">Comparaison pour 3 000 € brut mensuel</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="border-b-2 border-slate-200">
                                <th class="py-3 text-left font-semibold text-slate-900">Pays</th>
                                <th class="py-3 text-right font-semibold text-slate-900">Brut</th>
                                <th class="py-3 text-right font-semibold text-slate-900">Cotisations (%)</th>
                                <th class="py-3 text-right font-semibold text-slate-900">Net avant impôt</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="border-b border-slate-100"><td class="py-3">🇫🇷 France</td><td class="py-3 text-right">3 000 €</td><td class="py-3 text-right">~22%</td><td class="py-3 text-right font-medium">~2 340 €</td></tr>
                            <tr class="border-b border-slate-100"><td class="py-3">🇧🇪 Belgique</td><td class="py-3 text-right">3 000 €</td><td class="py-3 text-right">~13,07%</td><td class="py-3 text-right font-medium">~2 608 €</td></tr>
                            <tr class="border-b border-slate-100"><td class="py-3">🇨🇭 Suisse</td><td class="py-3 text-right">3 000 CHF</td><td class="py-3 text-right">~12-15%</td><td class="py-3 text-right font-medium">~2 550 CHF</td></tr>
                            <tr class="border-b border-slate-100"><td class="py-3">🇱🇺 Luxembourg</td><td class="py-3 text-right">3 000 €</td><td class="py-3 text-right">~12,5%</td><td class="py-3 text-right font-medium">~2 625 €</td></tr>
                            <tr><td class="py-3">🇩🇪 Allemagne</td><td class="py-3 text-right">3 000 €</td><td class="py-3 text-right">~20%</td><td class="py-3 text-right font-medium">~2 400 €</td></tr>
                        </tbody>
                    </table>
                </div>
                <p class="text-xs text-slate-400 mt-4">* Estimations indicatives, les taux varient selon la situation personnelle et le canton/région. L'impôt sur le revenu n'est pas inclus.</p>
            </div>
        </section>

        <section class="py-12 px-4">
            <div class="mx-auto max-w-4xl prose prose-slate">
                <h2 class="text-xl font-semibold text-slate-900">Pourquoi les cotisations varient-elles autant ?</h2>
                <p>Chaque pays a son propre système de protection sociale. La France a l'un des taux de cotisations les plus élevés d'Europe, mais en contrepartie offre une couverture sociale très complète (santé, retraite, chômage, famille).</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">France : cotisations élevées, protection forte</h3>
                <p>Avec environ 22% de cotisations salariales, la France offre une couverture maladie universelle, des allocations familiales généreuses, un système de retraite par répartition et une assurance chômage.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Suisse : cotisations basses, coût de la vie élevé</h3>
                <p>Les cotisations sont plus basses, mais l'assurance maladie est obligatoire et entièrement à la charge du salarié (300-500 CHF/mois en moyenne). Le coût de la vie est aussi nettement plus élevé.</p>

                <h3 class="text-lg font-semibold text-slate-900 mt-6">Belgique : cotisations basses, impôts élevés</h3>
                <p>Les cotisations sociales salariales sont plus basses qu'en France (~13%), mais l'impôt sur le revenu est parmi les plus élevés d'Europe (jusqu'à 50%), ce qui réduit fortement le net après impôt.</p>

                <p class="mt-6">Pour calculer votre salaire net en France précisément, utilisez notre <a href="/" class="text-brand-600 hover:text-brand-700">calculateur brut/net</a>.</p>
            </div>
        </section>'''
    html += links_grid("Pages connexes", RELATED_LINKS)
    html += FOOTER
    html += "\n</body></html>"
    write_page("comparateur-salaire-net-par-pays", html)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=== Génération des pages Phase 2 ===\n")

    print("1. Pages par statut professionnel...")
    gen_status_pages()

    print("\n2. Pages par période...")
    gen_period_pages()

    print("\n3. Pages de contenu éducatif...")
    gen_content_pages()

    print("\n4. Pages outils complémentaires...")
    gen_tool_pages()

    print("\n=== Terminé ! ===")


if __name__ == "__main__":
    main()
