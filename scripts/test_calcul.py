#!/usr/bin/env python3
"""
Tests du moteur brut → net et des chiffres cités sur l'accueil (RECETTE §17.4 et §22).

Lancement : npm test (ou python3 scripts/test_calcul.py depuis la racine du site).

Sources des cas chiffrés (relevées le 2026-10-31) :
  - taux salariaux 2026 : service-public.gouv.fr F2302 (vérifié le 1er janvier 2026) —
    vieillesse 6,90 % plafonnée + 0,40 % déplafonnée, Agirc-Arrco 3,15 % T1 / 8,64 % T2,
    CEG 0,86 % T1 / 1,08 % T2, CET 0,14 % au-delà du plafond, APEC 0,024 %,
    CSG 9,2 % (dont 2,4 % non déductible) et CRDS 0,5 % sur 98,25 % du brut,
    pas de cotisation chômage salariale depuis le 1er octobre 2018 ;
    taux Agirc-Arrco confirmés par reglementation.agirc-arrco.fr (cotisations 2026) ;
  - SMIC : service-public.gouv.fr F2300 — 1 867,02 € brut, 1 477,93 € net « à titre indicatif » ;
  - position INSEE : Insee Première n° 2132 (22/10/2026), figure 4, salaires mensuels nets
    EQTP du secteur privé en 2025, colonne Ensemble.
"""

import json
import os
import re
import shutil
import subprocess
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

import calcul  # noqa: E402

echecs = []


def verifier(condition, message):
    if not condition:
        echecs.append(message)


# 1. Moteur Python (miroir de js/brut-net.js)
CAS = [
    # (brut mensuel, statut, net avant impôt attendu)
    (1867.02, "non-cadre", 1477.93),   # SMIC, net indicatif de service-public F2300
    (2500, "non-cadre", 1978.99),      # 2 500 × (1 − 11,31 % − 9,70 % × 98,25 %)
    (2500, "cadre", 1978.39),          # + APEC 0,024 %
    (3000, "non-cadre", 2374.79),
    (5000, "non-cadre", 3962.83),      # tranche 2 et CET au-delà de 4 005 €
]
for brut, statut, attendu in CAS:
    net = calcul.calculer_brut_vers_net(brut, statut)["net_avant_impot"]
    verifier(abs(net - attendu) < 0.005, f"calcul.py : {brut} € {statut} → {net} (attendu {attendu})")

detail, _ = calcul.calculer_cotisations_salariales(2500, "non-cadre")
verifier(not any("hômage" in k for k in detail), "calcul.py : aucune cotisation chômage salariale ne doit exister")

# 2. Moteur JavaScript servi aux visiteurs : mêmes résultats que calcul.py
node = shutil.which("node")
if node:
    script = (
        "const fs=require('fs');eval(fs.readFileSync(process.argv[1],'utf8')+"
        "';globalThis.f=calculerBrutVersNet;');"
        "const cas=JSON.parse(process.argv[2]);"
        "console.log(JSON.stringify(cas.map(c=>f(c[0],c[1],1,{}).netAvantImpot)));"
    )
    sortie = subprocess.run(
        [node, "-e", script, os.path.join(RACINE, "js", "brut-net.js"), json.dumps(CAS)],
        capture_output=True, text=True, check=True,
    ).stdout
    for (brut, statut, attendu), net in zip(CAS, json.loads(sortie)):
        verifier(abs(net - attendu) < 0.005, f"js/brut-net.js : {brut} € {statut} → {net} (attendu {attendu})")
else:
    print("node absent : moteur JavaScript non testé")

# 3. Accueil : exemples cités = résultats du calculateur
accueil = open(os.path.join(RACINE, "index.html"), encoding="utf-8").read()
exemples = re.findall(r"<li><strong>(\d)[\u00a0\u202f ](\d{3})[\u00a0\u202f ]€ brut</strong>[\u00a0\u202f ]: environ (\d)[\u00a0\u202f ](\d{3})[\u00a0\u202f ]€ net</li>", accueil)
verifier(len(exemples) == 5, f"index.html : 5 exemples brut → net attendus, {len(exemples)} trouvés")
for b1, b2, n1, n2 in exemples:
    brut, net = int(b1 + b2), int(n1 + n2)
    calc = calcul.arrondi(calcul.calculer_brut_vers_net(brut, "non-cadre")["net_avant_impot"])
    verifier(net == calc, f"index.html : {brut} € brut annoncé {net} € net, le calculateur donne {calc:.0f} €")
verifier("22% pour un non-cadre" not in accueil and "25% pour un cadre" not in accueil,
         "index.html : taux forfaitaires 22 % / 25 % encore cités")

# 4. Accueil : déciles INSEE 2025 (Insee Première n° 2132, figure 4, Ensemble)
INSEE_2025 = [[10, 1519], [20, 1702], [30, 1861], [40, 2034], [50, 2238],
              [60, 2497], [70, 2850], [80, 3386], [90, 4441], [95, 5730], [99, 10552]]
m = re.search(r"var INSEE_PCT = (\[[\s\S]*?\]);", accueil)
verifier(m is not None, "index.html : tableau INSEE_PCT introuvable")
if m:
    verifier(json.loads(m.group(1)) == INSEE_2025, "index.html : INSEE_PCT différent des déciles INSEE 2025")

if echecs:
    print("\n".join("ÉCHEC " + e for e in echecs))
    sys.exit(1)
print(f"OK : {len(CAS)} cas du moteur (Python et JavaScript), exemples de l'accueil et déciles INSEE")
