#!/usr/bin/env python3
"""
Module partagé de calcul salaire brut ↔ net (paramètres 2026).

Miroir exact de js/brut-net.js, le moteur servi aux visiteurs : mêmes taux, même
ordre de calcul, mêmes arrondis. Utilisé par generate-thematiques.py, generate.py
(qui garde sa propre copie historique) et generate-pages.py.

Sources des paramètres (vérifiées le 2026-10-26) :
  - plafond de la Sécurité sociale 2026 : URSSAF, 4 005 € par mois, 48 060 € par an ;
  - SMIC : 12,02 € brut de l'heure au 1er janvier 2026 (décret n° 2025-1228),
    12,31 € depuis le 1er juin 2026 (arrêté du 22 mai 2026), service-public.gouv.fr F2300 ;
  - taux salariaux : URSSAF, taux de cotisations secteur privé 2026 ;
  - réduction générale dégressive unique : URSSAF, coefficient des entreprises
    de moins de 50 salariés.
"""

import math

PSS_MENSUEL = 4005
PSS_ANNUEL = 48060
PSS_HORAIRE = 30
SMIC_HORAIRE = 12.31            # depuis le 1er juin 2026
SMIC_MENSUEL_BRUT = 1867.02     # 12,31 € × 151,67 h
SMIC_HORAIRE_JANVIER = 12.02    # du 1er janvier au 31 mai 2026
SMIC_MENSUEL_JANVIER = 1823.03  # référence de la réduction générale 2026
HEURES_MENSUELLES = 151.67      # 35 h × 52 / 12


def arrondi(val, decimales=0):
    """Arrondi commercial (0,5 vers le haut), comme Math.round en JavaScript."""
    f = 10 ** decimales
    return math.floor(val * f + 0.5) / f


def calculer_cotisations_salariales(brut_mensuel, statut, alsace_moselle=False):
    is_cadre = statut == "cadre"
    t1 = min(brut_mensuel, PSS_MENSUEL)
    t2 = max(0, brut_mensuel - PSS_MENSUEL)
    assiette_csg = brut_mensuel * 0.9825

    cotisations = {
        "Vieillesse plafonnée": t1 * 0.069,
        "Vieillesse déplafonnée": brut_mensuel * 0.004,
        "AGIRC-ARRCO T1": t1 * 0.0315,
        "AGIRC-ARRCO T2": t2 * 0.0864,
        "CEG T1": t1 * 0.0086,
        "CEG T2": t2 * 0.0108,
        "CSG déductible": assiette_csg * 0.068,
        "CSG non déductible": assiette_csg * 0.024,
        "CRDS": assiette_csg * 0.005,
    }
    if brut_mensuel > PSS_MENSUEL:
        cotisations["CET"] = brut_mensuel * 0.0014
    if is_cadre:
        cotisations["APEC (cadre)"] = min(brut_mensuel, PSS_MENSUEL * 4) * 0.00024
    if alsace_moselle:
        cotisations["Maladie Alsace-Moselle"] = brut_mensuel * 0.013

    total = sum(cotisations.values())
    return cotisations, total


def calculer_cotisations_patronales(brut_mensuel):
    t1 = min(brut_mensuel, PSS_MENSUEL)
    t2 = max(0, brut_mensuel - PSS_MENSUEL)

    cotisations = {
        "Maladie": brut_mensuel * 0.13,
        "Vieillesse plafonnée": t1 * 0.0855,
        "Vieillesse déplafonnée": brut_mensuel * 0.0211,
        "Allocations familiales": brut_mensuel * 0.0525,
        "Chômage et AGS": min(brut_mensuel, PSS_MENSUEL * 4) * 0.0425,
        "AGIRC-ARRCO T1": t1 * 0.0472,
        "AGIRC-ARRCO T2": t2 * 0.1295,
        "AT/MP (taux moyen)": brut_mensuel * 0.01,
        "CEG T1": t1 * 0.0129,
        "CEG T2": t2 * 0.0162,
        "CET": brut_mensuel * 0.0021 if brut_mensuel > PSS_MENSUEL else 0,
    }
    if 0 < brut_mensuel < SMIC_MENSUEL_JANVIER * 3:
        coef = min(0.3981, 0.02 + 0.3781 * (0.5 * (3 * SMIC_MENSUEL_JANVIER / brut_mensuel - 1)) ** 1.75)
        cotisations["Réduction générale dégressive"] = -brut_mensuel * coef
    total = sum(cotisations.values())
    return cotisations, total


def estimer_impot_revenu(net_imposable_annuel, nb_parts=1, parts_base=1):
    tranches = [
        (0, 11600, 0),
        (11600, 29579, 0.11),
        (29579, 84577, 0.30),
        (84577, 181917, 0.41),
        (181917, float("inf"), 0.45),
    ]

    def bareme(revenu_par_part):
        impot = 0
        for mini, maxi, taux in tranches:
            if revenu_par_part <= mini:
                break
            impot += (min(revenu_par_part, maxi) - mini) * taux
        return impot

    impot_qf = bareme(net_imposable_annuel / nb_parts) * nb_parts
    demi_parts_supp = nb_parts - parts_base
    if demi_parts_supp > 0:
        impot_sans_qf = bareme(net_imposable_annuel / parts_base) * parts_base
        plafond = 1807 * (demi_parts_supp / 0.5)
        if impot_sans_qf - impot_qf > plafond:
            impot_qf = impot_sans_qf - plafond
    decote = (1483 if parts_base >= 2 else 897) - 0.4525 * impot_qf
    if decote > 0:
        impot_qf = max(0, impot_qf - decote)
    return max(0, arrondi(impot_qf))


def calculer_brut_vers_net(brut_mensuel, statut, temps=1, alsace_moselle=False, nb_parts=1, parts_base=1):
    brut = brut_mensuel * temps
    cotis_sal, total_sal = calculer_cotisations_salariales(brut, statut, alsace_moselle)
    cotis_pat, total_pat = calculer_cotisations_patronales(brut)

    net_avant_impot = brut - total_sal
    net_imposable_mensuel = net_avant_impot + cotis_sal["CSG non déductible"] + cotis_sal["CRDS"]
    net_imposable_annuel = net_imposable_mensuel * 12
    abattement = min(max(net_imposable_annuel * 0.1, 509), 14555)
    impot_annuel = estimer_impot_revenu(net_imposable_annuel - abattement, nb_parts, parts_base)
    impot_mensuel = arrondi(impot_annuel / 12)

    return {
        "brut_mensuel": brut,
        "brut_annuel": brut * 12,
        "net_avant_impot": arrondi(net_avant_impot, 2),
        "net_apres_impot": arrondi(net_avant_impot - impot_mensuel, 2),
        "net_imposable": arrondi(net_imposable_mensuel, 2),
        "impot_mensuel": impot_mensuel,
        "impot_annuel": impot_annuel,
        "cout_employeur": arrondi(brut + total_pat, 2),
        "total_salarial": arrondi(total_sal, 2),
        "total_patronal": arrondi(total_pat, 2),
        "taux_cotisations": arrondi((total_sal / brut) * 1000) / 10 if brut > 0 else 0,
        "detail_salariales": cotis_sal,
        "detail_patronales": cotis_pat,
    }


def calculer_net_vers_brut(net_cible, statut, temps=1, alsace_moselle=False):
    brut_estime = net_cible * 1.3
    for _ in range(50):
        result = calculer_brut_vers_net(brut_estime, statut, temps, alsace_moselle)
        diff = result["net_avant_impot"] - net_cible
        if abs(diff) < 0.01:
            break
        brut_estime -= diff * 0.7
    return calculer_brut_vers_net(brut_estime, statut, temps, alsace_moselle)


def fmt(val):
    """Format number French style: 1 500"""
    return f"{int(arrondi(val)):,}".replace(",", " ")


def fmt2(val):
    """Format number with 2 decimals French style"""
    return f"{arrondi(val, 2):,.2f}".replace(",", " ").replace(".", ",")
