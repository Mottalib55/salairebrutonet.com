#!/usr/bin/env python3
"""
Régénère les deux tableaux « Exemples de conversion brut → net » de /prime-brut-en-net/
à partir du moteur (calcul.py), entre les marqueurs <!-- prime-tableaux:debut --> et
<!-- prime-tableaux:fin -->. Rien d'autre dans la page n'est modifié.

Hypothèses affichées dans la page :
  - la prime s'ajoute à un salaire qui, sur l'année, reste sous le plafond de la Sécurité
    sociale (48 060 € en 2026) : elle supporte donc les taux de la tranche 1 du moteur ;
  - le prélèvement à la source s'applique au net imposable de la prime (net + CSG non
    déductible + CRDS), à un taux illustratif de 5 % (non-cadre) et 7,5 % (cadre).

Usage : python3 scripts/gen-prime-tableaux.py [--check]
  --check : n'écrit rien, sort en erreur si la page n'est pas à jour (utilisé par npm test).
"""

import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

import calcul  # noqa: E402

PAGE = os.path.join(RACINE, "prime-brut-en-net", "index.html")
DEBUT, FIN = "<!-- prime-tableaux:debut -->", "<!-- prime-tableaux:fin -->"
PRIMES = [500, 1000, 2000, 5000]
NB = " "


def euros(val, decimales=True):
    if decimales:
        txt = f"{calcul.arrondi(val, 2):,.2f}".replace(",", NB).replace(".", ",")
    else:
        txt = f"{int(calcul.arrondi(val)):,}".replace(",", NB)
    return txt + NB + "€"


def pct(val):
    return f"{val:.2f}".replace(".", ",").rstrip("0").rstrip(",") + NB + "%"


def taux_tranche_1(statut):
    """Taux salarial global sous le plafond (proportionnel au brut sur la tranche 1)."""
    detail, total = calcul.calculer_cotisations_salariales(1000, statut)
    non_deductible = detail["CSG non déductible"] + detail["CRDS"]
    return total / 1000, non_deductible / 1000


def tableau(titre, statut, taux_pas):
    taux, nd = taux_tranche_1(statut)
    lignes = []
    for i, prime in enumerate(PRIMES):
        # Chaque colonne arrondie au centime, puis les différences : les lignes s'additionnent juste
        cotis = calcul.arrondi(prime * taux, 2)
        net = calcul.arrondi(prime - cotis, 2)
        impot = calcul.arrondi((net + prime * nd) * taux_pas, 2)
        classe = ' class="border-b border-slate-100"' if i < len(PRIMES) - 1 else ""
        lignes.append(
            f'                        <tr{classe}><td class="py-2">{euros(prime, False)}</td>'
            f'<td class="py-2 text-right">-{euros(cotis)}</td>'
            f'<td class="py-2 text-right">{euros(net)}</td>'
            f'<td class="py-2 text-right">-{euros(impot)}</td>'
            f'<td class="py-2 text-right">{euros(net - impot)}</td></tr>'
        )
    return (
        f'                <h3 class="text-lg font-semibold text-slate-900 mt-6">{titre} ({pct(taux * 100)} de cotisations, taux PAS {pct(taux_pas * 100)})</h3>\n'
        '                <table class="w-full text-sm border-collapse mt-4">\n'
        '                    <thead><tr class="border-b-2 border-slate-300">\n'
        '                        <th class="py-2 text-left">Prime brute</th>\n'
        f'                        <th class="py-2 text-right">Cotisations ({pct(taux * 100)})</th>\n'
        '                        <th class="py-2 text-right">Net avant impôt</th>\n'
        f'                        <th class="py-2 text-right">Impôt ({pct(taux_pas * 100)})</th>\n'
        '                        <th class="py-2 text-right">Net après impôt</th>\n'
        '                    </tr></thead>\n'
        '                    <tbody>\n'
        + "\n".join(lignes) + "\n"
        '                    </tbody>\n'
        '                </table>\n'
    )


def bloc():
    return (
        f"{DEBUT}\n"
        "                <p>Voici des exemples concrets pour différents montants de primes classiques (soumises à cotisations pleines), "
        f"calculés avec les taux 2026 de notre simulateur pour une rémunération annuelle restant sous le plafond de la Sécurité sociale (48{NB}060{NB}€). "
        f"L'impôt est appliqué au net imposable de la prime, à un taux de prélèvement illustratif{NB}:</p>\n\n"
        + tableau("Non-cadre", "non-cadre", 0.05) + "\n"
        + tableau("Cadre", "cadre", 0.075)
        + f"                {FIN}"
    )


def main():
    page = open(PAGE, encoding="utf-8").read()
    i, j = page.find(DEBUT), page.find(FIN)
    if i < 0 or j < 0:
        raise SystemExit("Marqueurs prime-tableaux introuvables : arrêt sans rien écrire.")
    nouvelle = page[:i] + bloc() + page[j + len(FIN):]
    if "--check" in sys.argv:
        if nouvelle != page:
            raise SystemExit("prime-brut-en-net : tableaux différents du moteur (lancer scripts/gen-prime-tableaux.py)")
        print("prime-brut-en-net : tableaux à jour")
        return
    if nouvelle != page:
        open(PAGE, "w", encoding="utf-8").write(nouvelle)
        print("prime-brut-en-net : tableaux régénérés")
    else:
        print("prime-brut-en-net : déjà à jour")


if __name__ == "__main__":
    main()
