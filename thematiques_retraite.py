#!/usr/bin/env python3
"""
Pages thématiques « retraite et revenus d'activité » (ajoutées le 2026-10-27) :
cumul emploi-retraite, retraite progressive, calcul de la retraite de base,
prime d'activité, portage salarial.

Chiffres relevés le 2026-10-27 sur service-public.gouv.fr, legifrance.gouv.fr,
caf.fr, lassuranceretraite.fr et urssaf.fr : voir les constantes ci-dessous.
Les calculs Python servent aux tableaux et aux exemples ; le JavaScript de chaque
page applique exactement les mêmes formules dans le navigateur.
"""

import math

from thematiques_commun import *  # noqa: F401,F403
from calcul import PSS_ANNUEL
from thematiques_commun import PSS_MENSUEL, SMIC_MENSUEL_JANVIER, e, e2, pct, net

RELEVE = "27 octobre 2026"

# ── Chiffres officiels (relevés le 2026-10-27) ────────────────────────────────
# Cumul emploi-retraite : service-public.gouv.fr F13243 (vérifié le 1er janvier 2026)
CUMUL_PLAFOND_160 = 2916.85      # 160 % du Smic sur 1 820 h, montant publié par service-public
CUMUL_NOUVELLE_PENSION_MAX = 2403  # € brut par an (5 % du PSS 2026)
CUMUL_2027_SEUIL = 7000          # € brut par an, annoncé (A18914, 22 mai 2026), décret non publié
# Retraite de base : service-public.gouv.fr F21552 (vérifié le 1er septembre 2026), F14043
GENERATIONS = [  # (libellé, âge légal en années, trimestres requis)
    ("1958 à 1960", 62, 167),
    ("janvier à août 1961", 62, 168),
    ("septembre à décembre 1961", 62.25, 169),
    ("1962", 62.5, 169),
    ("1963 à mars 1965", 62.75, 170),
    ("avril à décembre 1965", 63, 171),
    ("1966", 63.25, 172),
    ("1967", 63.5, 172),
    ("1968", 63.75, 172),
    ("1969 et après", 64, 172),
]
MIN_CONTRIBUTIF = 903.94          # € brut par mois, tous trimestres cotisés
MIN_CONTRIBUTIF_BASE = 756.29
MIN_CONTRIBUTIF_PLAFOND = 1410.89
PENSION_MAX = PSS_MENSUEL * 0.5   # 2 002,50 € brut par mois
POINT_AGIRC_ARRCO = 1.4386        # valeur de service du 1er novembre 2025 au 31 octobre 2026
# Prime d'activité : décret n° 2026-222 du 30 mars 2026, service-public.gouv.fr F2882 (vérifié le 1er juin 2026)
PA_MF = {("seul", 0): 638.28, ("seul", 1): 957.42, ("seul", 2): 1148.90,
         ("couple", 0): 957.42, ("couple", 1): 1148.90, ("couple", 2): 1340.39}
PA_ENFANT_SUPP = 255.31
PA_TAUX_REVENUS = 0.5985
PA_BONIF_DEBUT = 726.29           # 59 × Smic horaire (12,31 €)
PA_BONIF_PLEINE = 1698.78         # 138 × Smic horaire (12,31 €)
PA_BONIF_MAX = 240.63             # 37,7 % du montant forfaitaire
PA_FORFAIT_LOGEMENT = {1: 76.59, 2: 153.19, 3: 189.57}
PA_MINIMUM_VERSE = 15
# Portage salarial : convention de branche du 22 mars 2017, Code du travail L. 1254-2
PORTAGE_MIN = {"junior": 0.70, "senior": 0.75, "forfait jours": 0.85}


# ── Sources ───────────────────────────────────────────────────────────────────
SRC_CUMUL = ("Service-Public.fr, cumul emploi-retraite du salarié", "https://www.service-public.gouv.fr/particuliers/vosdroits/F13243")
SRC_CUMUL_2027 = ("Service-Public.fr, nouvelles règles du cumul emploi-retraite à partir de 2027", "https://www.service-public.gouv.fr/particuliers/actualites/A18914")
SRC_MONTANT_RETRAITE = ("Service-Public.fr, montant de la retraite de base du salarié", "https://www.service-public.gouv.fr/particuliers/vosdroits/F21552")
SRC_AGE_RETRAITE = ("Service-Public.fr, âge de départ à la retraite du salarié", "https://www.service-public.gouv.fr/particuliers/vosdroits/F14043")
SRC_SURCOTE = ("Service-Public.fr, surcote de la retraite du salarié", "https://www.service-public.gouv.fr/particuliers/vosdroits/F19643")
SRC_SURCOTE_CNAV = ("L'Assurance retraite, la surcote", "https://www.lassuranceretraite.fr/portail-info/hors-menu/annexe/salaries/montant-retraite/surcote-retraite.html")
SRC_AGIRC = ("Service-Public.fr, retraite complémentaire Agirc-Arrco", "https://www.service-public.gouv.fr/particuliers/vosdroits/F15396")
SRC_DEPART = ("Service-Public.fr, indemnité de départ à la retraite du salarié", "https://www.service-public.gouv.fr/particuliers/vosdroits/F13965")
SRC_PROGRESSIVE = ("Service-Public.fr, retraite progressive du salarié", "https://www.service-public.gouv.fr/particuliers/vosdroits/F12842")
SRC_PROGRESSIVE_60 = ("Service-Public.fr, retraite progressive dès 60 ans", "https://www.service-public.gouv.fr/particuliers/actualites/A18399")
SRC_PROGRESSIVE_FP = ("Service-Public.fr, retraite progressive de l'agent public", "https://www.service-public.gouv.fr/particuliers/vosdroits/F37400")
SRC_PA = ("Service-Public.fr, prime d'activité du salarié ou du fonctionnaire", "https://www.service-public.gouv.fr/particuliers/vosdroits/F2882")
SRC_PA_DECRET = ("Légifrance, décret n° 2026-222 du 30 mars 2026", "https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000053733855")
SRC_PA_CAF = ("Caf, la prime d'activité augmente en 2026", "https://www.caf.fr/allocataires/actualites/actualites-nationales/la-prime-d-activite-augmente-en-2026")
SRC_PA_BAREME = ("Caf, barème de la prime d'activité", "https://www.caf.fr/professionnels/offres-et-services/accompagnement-des-allocataires/bareme-prime-d-activite")
SRC_PORTAGE = ("Service-Public.fr Entreprendre, portage salarial", "https://entreprendre.service-public.gouv.fr/vosdroits/F31620")
SRC_PORTAGE_CODE = ("Légifrance, Code du travail, articles L. 1254-1 à L. 1254-31", "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072050/LEGISCTA000030435227/")
SRC_PORTAGE_CCN = ("Légifrance, convention collective du portage salarial, article 21", "https://www.legifrance.gouv.fr/conv_coll/article/KALIARTI000043706538")


# ── Outils de calcul (mêmes formules que le JavaScript des pages) ─────────────

def plafond_cumul(dernier_salaire):
    return max(CUMUL_PLAFOND_160, dernier_salaire)


def cumul_plafonne(base, compl, activite, dernier):
    plafond = plafond_cumul(dernier)
    total = base + compl + 0.9825 * activite
    depassement = max(0.0, total - plafond)
    base_versee = max(0.0, base - depassement)
    return plafond, depassement, base_versee


def pension_base(sam, trim, age, age_legal, requis):
    """Pension de base mensuelle brute du régime général : SAM × taux × durée / durée requise."""
    sam = min(sam, PSS_ANNUEL)
    decote = 0
    if age < 67:
        decote = int(min(max(0, requis - trim), math.ceil((67 - age) * 4 - 1e-9), 20))
    taux = 0.5 - 0.00625 * decote
    p = sam * taux * min(trim, requis) / requis / 12
    p = min(p, PENSION_MAX)
    surcote = 0
    if trim > requis and age > age_legal:
        surcote = int(min(trim - requis, math.floor((age - age_legal) * 4 + 1e-9)))
    return p * (1 + 0.0125 * surcote), taux, decote, surcote


def indemnite_depart(anciennete, salaire):
    if anciennete < 10:
        mois = 0
    elif anciennete < 15:
        mois = 0.5
    elif anciennete < 20:
        mois = 1
    elif anciennete < 30:
        mois = 1.5
    else:
        mois = 2
    return salaire * mois


def indemnite_mise_retraite(anciennete, salaire):
    return salaire * (min(anciennete, 10) / 4 + max(0, anciennete - 10) / 3)


def pa_bonif(r):
    if r <= PA_BONIF_DEBUT:
        return 0.0
    if r >= PA_BONIF_PLEINE:
        return PA_BONIF_MAX
    return PA_BONIF_MAX * (r - PA_BONIF_DEBUT) / (PA_BONIF_PLEINE - PA_BONIF_DEBUT)


def pa_forfait(foyer, enfants):
    base = PA_MF[(foyer, min(enfants, 2))]
    return base + PA_ENFANT_SUPP * max(0, enfants - 2)


def prime_activite(r1, foyer="seul", enfants=0, r2=0.0, autres=0.0, logement=False):
    mf = pa_forfait(foyer, enfants)
    personnes = (2 if foyer == "couple" else 1) + enfants
    fl = PA_FORFAIT_LOGEMENT[min(personnes, 3)] if logement else 0
    r2 = r2 if foyer == "couple" else 0
    revenus = r1 + r2
    pa = mf + PA_TAUX_REVENUS * revenus + pa_bonif(r1) + pa_bonif(r2) - max(mf, revenus + autres + fl)
    return pa if pa >= PA_MINIMUM_VERSE else 0.0


def cout_portage(b):
    """Coût employeur d'un salarié porté cadre : entreprise de 50 salariés et plus, AT 1 %,
    prévoyance cadre 1,50 % sur la tranche 1, réduction générale dégressive (50 salariés et plus)."""
    t1, t2, l4 = min(b, PSS_MENSUEL), max(0, b - PSS_MENSUEL), min(b, 4 * PSS_MENSUEL)
    ch = (b * (0.13 + 0.0211 + 0.0525 + 0.01 + 0.003 + 0.005 + 0.00016 + 0.01 + 0.0068)
          + t1 * (0.0855 + 0.0472 + 0.0129 + 0.015) + t2 * (0.1295 + 0.0162)
          + l4 * (0.04 + 0.0025 + 0.00036) + (b * 0.0021 if b > PSS_MENSUEL else 0))
    s = 3 * SMIC_MENSUEL_JANVIER
    coef = min(0.4021, 0.02 + 0.3821 * (0.5 * (s / b - 1)) ** 1.75) if 0 < b < s else 0
    return b + ch - b * coef


def portage(tjm, jours, frais_gestion, frais_pro=0.0):
    ca = tjm * jours
    enveloppe = max(0.0, ca * (1 - frais_gestion) - frais_pro)
    lo, hi = 0.0, enveloppe
    for _ in range(60):
        mid = (lo + hi) / 2
        if cout_portage(mid) > enveloppe:
            hi = mid
        else:
            lo = mid
    total_brut = lo
    brut = total_brut / 1.1
    reserve = total_brut - brut
    n = calculer_brut_vers_net(brut, "cadre")["net_avant_impot"] if brut > 0 else 0
    return {"ca": ca, "enveloppe": enveloppe, "brut": brut, "reserve": reserve, "net": n,
            "frais": ca * frais_gestion}


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_cumul():
    ex_base, ex_compl, ex_act, ex_dernier = 1100, 500, 1500, 2600
    plaf, dep, base_v = cumul_plafonne(ex_base, ex_compl, ex_act, ex_dernier)
    lignes = []
    for act in (800, 1200, 1500, 2000, 2500):
        p, d, b = cumul_plafonne(ex_base, ex_compl, act, ex_dernier)
        lignes.append([e(act), e2(ex_base + ex_compl + 0.9825 * act), e2(d), e2(b), e2(b + ex_compl + act)])
    reduc_2027 = max(0, ex_act * 12 - CUMUL_2027_SEUIL) * 0.5 / 12
    corps = f"""
<h2>Cumul intégral ou cumul plafonné</h2>
<p>Tout dépend des conditions dans lesquelles la retraite a été prise. Le <strong>cumul intégral</strong> s'applique si vous percevez une pension de base à taux plein (soit avec tous les trimestres requis dès l'âge légal, soit à 67 ans) et si vous avez demandé toutes vos retraites, de base et complémentaires, françaises et étrangères. Vous pouvez alors cumuler sans limite pension et salaire. Si l'une de ces conditions manque, c'est le <strong>cumul plafonné</strong> : pensions brutes et revenus d'activité ne doivent pas dépasser ensemble le plus favorable de deux plafonds.</p>
{table(["Règle en 2026", "Cumul intégral", "Cumul plafonné"], [
    ["Condition", "Taux plein et toutes les retraites liquidées", "Les autres cas"],
    ["Plafond", "Aucun", f"{e2(CUMUL_PLAFOND_160)} brut par mois ou dernier salaire"],
    ["Dépassement", "Sans effet", "Pension de base réduite d'autant"],
    ["Nouveaux droits à retraite", f"Oui, jusqu'à {e(CUMUL_NOUVELLE_PENSION_MAX)} brut par an", "Non"],
])}
{note("Service-public.gouv.fr, fiche F13243 vérifiée le 1er janvier 2026. Le montant de 2 916,85 € correspond à 160 % du Smic horaire de janvier 2026 (12,02 €) sur 1 820 heures par an ; service-public n'a pas publié de montant recalculé depuis la hausse du Smic du 1er juin 2026.")}
<h2>Comment le plafond est appliqué</h2>
<p>Le revenu d'activité n'est retenu qu'à hauteur de 98,25 % de son montant brut, la part soumise à la CSG. Les pensions sont prises avant prélèvements sociaux. Le dernier salaire de référence est la moyenne mensuelle des salaires soumis à CSG des trois derniers mois avant la retraite. Si le total dépasse le plafond, l'excédent est retiré de la pension de base, jamais des complémentaires ; si l'excédent dépasse la pension, elle est suspendue.</p>
<p>Exemple : pension de base de {e(ex_base)}, complémentaire de {e(ex_compl)}, dernier salaire de {e(ex_dernier)}. Le plafond retenu est donc {e2(plaf)}. Avec une reprise d'activité payée {e(ex_act)} brut, le total retenu atteint {e2(ex_base + ex_compl + 0.9825 * ex_act)} : le dépassement de {e2(dep)} ramène la pension de base à {e2(base_v)}.</p>
{table(["Salaire brut repris", "Total retenu", "Dépassement", "Pension de base versée", "Revenu brut total"], lignes)}
{note("Mêmes pensions et même dernier salaire que l'exemple. Le revenu brut total additionne pension de base versée, complémentaire et salaire.")}
<h2>Reprendre chez son dernier employeur</h2>
<p>Chez un nouvel employeur, l'activité peut reprendre dès le lendemain du départ. Chez le dernier employeur, il faut attendre au moins six mois après la date d'effet de la retraite, faute de quoi la pension est suspendue. Le délai ne s'applique pas en cumul intégral pour certaines activités librement cumulables (activités artistiques, consultations ponctuelles, mandats électifs).</p>
<h2>Ce qui change au 1er janvier 2027</h2>
<p>La loi de financement de la Sécurité sociale pour 2026 (article 102) remplace ce système pour les personnes dont la retraite prend effet à partir du 1er janvier 2027. La distinction entre cumul intégral et plafonné disparaît, seul l'âge compte : avant l'âge légal, tout revenu d'activité est déduit de la pension dès le premier euro ; entre l'âge légal et 67 ans, le cumul est libre jusqu'à un seuil annoncé de {e(CUMUL_2027_SEUIL)} brut par an, puis la pension est réduite de la moitié du dépassement ; à partir de 67 ans, le cumul est intégral et ouvre de nouveaux droits.</p>
<p>Avec le salaire de l'exemple ({e(ex_act)} brut par mois, soit {e(ex_act * 12)} par an), un retraité de 65 ans parti en 2027 verrait sa pension réduite d'environ {e2(reduc_2027)} par mois. Le décret qui doit fixer le seuil de 7 000 € n'était pas publié au 22 mai 2026, date de l'annonce de service-public.gouv.fr : ce montant reste donc indicatif. Les retraités partis avant 2027 gardent les règles actuelles.</p>
<p>Pour estimer la pension elle-même, voir notre page sur le <a href="/calcul-retraite/">calcul de la retraite de base</a> ; pour réduire son activité avant de partir, la <a href="/retraite-progressive/">retraite progressive</a>.</p>
"""
    js = f"""
            var base = v('w-base'), compl = v('w-compl'), act = v('w-act'), dernier = v('w-dernier');
            var mode = document.getElementById('w-mode').value;
            var plafond = Math.max({CUMUL_PLAFOND_160}, dernier);
            var total = base + compl + 0.9825 * act;
            var dep = mode === 'integral' ? 0 : Math.max(0, total - plafond);
            var baseV = Math.max(0, base - dep);
            out('r-plafond', mode === 'integral' ? 'Aucun' : centimes(plafond));
            out('r-dep', centimes(dep));
            out('r-base', centimes(baseV));
            out('r-total', centimes(baseV + compl + act));"""
    return {
        "slug": "cumul-emploi-retraite",
        "title": "Cumul emploi-retraite 2026 : plafond de 2 916,85 € et calcul",
        "desc": "Cumul emploi-retraite 2026 : intégral ou plafonné à 2 916,85 € brut par mois ou au dernier salaire. Simulateur de la pension réduite et règles de 2027.",
        "h1": "Cumul emploi-retraite 2026",
        "crumb": "Cumul emploi-retraite",
        "widget_titre": "Pension versée en cumul emploi-retraite",
        "widget": widget([champ("w-base", "Pension de base brute (€/mois)", "1100"),
                          champ("w-compl", "Pensions complémentaires brutes (€/mois)", "500"),
                          champ("w-act", "Salaire brut de reprise (€/mois)", "1500"),
                          champ("w-dernier", "Dernier salaire brut avant retraite (€/mois)", "2600"),
                          choix("w-mode", "Type de cumul", [("plafonne", "Cumul plafonné"), ("integral", "Cumul intégral")], "plafonne")],
                         [("r-plafond", "Plafond appliqué"), ("r-dep", "Dépassement"), ("r-base", "Pension de base versée"), ("r-total", "Revenu brut total")],
                         "Le salaire est retenu à 98,25 % de son montant, la part soumise à la CSG. Montants bruts avant prélèvements sociaux."),
        "js": js,
        "citable": f"En 2026, un retraité du secteur privé peut reprendre un emploi et garder sa pension. Le cumul est intégral, donc sans limite, s'il a obtenu sa retraite de base à taux plein et liquidé toutes ses pensions, de base et complémentaires. Sinon, le cumul est plafonné : pensions brutes et 98,25 % du salaire brut ne doivent pas dépasser ensemble {e2(CUMUL_PLAFOND_160)} par mois (160 % du Smic, montant publié par service-public.gouv.fr) ou le dernier salaire avant la retraite s'il est plus élevé. Au-delà, la pension de base est réduite du dépassement. Chez son dernier employeur, il faut attendre six mois. En cumul intégral, l'activité ouvre une seconde pension de base, plafonnée à {e(CUMUL_NOUVELLE_PENSION_MAX)} brut par an. Ces règles changent pour les retraites prenant effet à partir du 1er janvier 2027.",
        "corps": corps,
        "sources": [SRC_CUMUL, SRC_CUMUL_2027, SRC_MONTANT_RETRAITE, SRC_SMIC],
        "faq": [
            ("Peut-on toucher sa retraite et un salaire en même temps ?",
             "Oui. Tout retraité du régime général peut reprendre une activité salariée ou indépendante. La seule question est de savoir si le cumul est libre ou plafonné. Il est libre dès que la pension de base a été obtenue à taux plein et que toutes les retraites ont été demandées. Dans les autres cas, le total des pensions et du salaire est limité, et la pension de base diminue au-delà du plafond."),
            ("Quel est le plafond du cumul emploi-retraite en 2026 ?",
             f"Le plafond est le plus favorable de deux montants : 160 % du Smic, soit {e2(CUMUL_PLAFOND_160)} brut par mois selon service-public.gouv.fr, ou le dernier salaire brut mensuel avant la retraite, calculé sur la moyenne des trois derniers mois. Les pensions brutes et 98,25 % du salaire de reprise s'additionnent pour être comparés à ce plafond. Il ne s'applique qu'en cumul plafonné."),
            ("Faut-il attendre avant de retravailler chez son ancien employeur ?",
             "Oui, six mois au moins après la date d'effet de la retraite, sinon le versement de la pension est suspendu. Chez un autre employeur, aucun délai n'est imposé : la reprise est possible dès le lendemain du départ. Le délai de six mois vise à éviter qu'un salarié liquide sa retraite tout en gardant exactement le même poste au même endroit."),
            ("Le cumul emploi-retraite permet-il d'augmenter sa retraite ?",
             f"En cumul intégral, oui, depuis la réforme de 2023 : les cotisations versées pendant la reprise ouvrent une seconde pension de base, calculée sans décote ni majoration et plafonnée à {e(CUMUL_NOUVELLE_PENSION_MAX)} brut par an en 2026, accordée une seule fois par caisse. L'activité peut aussi rapporter des points Agirc-Arrco. En cumul plafonné, les cotisations restent dues mais n'ouvrent aucun droit nouveau."),
            ("Que change la loi de financement pour 2026 au cumul emploi-retraite ?",
             f"Pour les retraites prenant effet à partir du 1er janvier 2027, la distinction entre cumul intégral et plafonné disparaît. Avant l'âge légal, le revenu d'activité est déduit de la pension dès le premier euro. Entre l'âge légal et 67 ans, le cumul est libre jusqu'à un seuil annoncé de {e(CUMUL_2027_SEUIL)} brut par an, puis la pension baisse de la moitié du dépassement. Après 67 ans, il est intégral."),
            ("Les indemnités journalières comptent-elles dans le plafond ?",
             "Dans le système actuel, seuls les revenus d'activité professionnelle sont comparés au plafond, à hauteur de 98,25 % de leur montant. À partir de 2027, les revenus de remplacement comme les indemnités journalières seront pris en compte avant l'âge légal, selon l'annonce de service-public.gouv.fr. En cas de doute sur une situation précise, la caisse de retraite peut faire le calcul sur demande."),
        ],
        "related": ["calcul-retraite", "retraite-progressive", "salaire-brut-net-annuel", "smic-brut-net-2026", "plafond-securite-sociale-2026", "portage-salarial"],
        "releve": RELEVE,
        "note_sources": "Les montants sont bruts, avant CSG, CRDS et Casa ; la pension de base et les complémentaires sont à reprendre de vos relevés de caisse.",
    }


def page_progressive():
    S, q, P = 3000, 0.6, 1600
    b = S * q
    n = net(b)
    lignes = [[pct(qq * 100, 0), e(S * qq), e2(net(S * qq)), e2(P * (1 - qq)), e2(net(S * qq) + P * (1 - qq))]
              for qq in (0.4, 0.5, 0.6, 0.7, 0.8)]
    corps = f"""
<h2>Les conditions en 2026</h2>
{table(["Condition", "Salarié du privé", "Agent public titulaire"], [
    ["Âge minimum", "60 ans", "60 ans"],
    ["Durée d'assurance", "150 trimestres", "150 trimestres"],
    ["Temps de travail", "40 % à 80 % d'un temps complet", "50 % à 90 %"],
    ["Accord de l'employeur", "Refus motivé seulement", "Selon les nécessités du service"],
])}
{note("Âge abaissé à 60 ans pour tous les assurés depuis le 1er septembre 2025 (décret du 15 juillet 2025). Service-public.gouv.fr, fiches F12842 et F37400. Les trimestres comptent tous régimes de base confondus.")}
<p>L'âge de 60 ans ne dépend plus de la génération : il s'applique à tous, même si l'âge légal de départ est, lui, compris entre 62 ans et 9 mois et 64 ans selon l'année de naissance. La retraite progressive est exclue en cas de préretraite ou si une indemnité de départ sert à compléter le salaire.</p>
<h2>Le calcul de la fraction de pension</h2>
<p>La caisse calcule d'abord une pension provisoire, sur les droits acquis à la date de la demande, pour chaque régime de base et complémentaire. Elle en verse une fraction égale à <strong>100 % moins la quotité travaillée</strong> : à 60 %, vous percevez 40 % de la pension provisoire. Avec un salaire de {e(S)} brut à temps plein et une pension provisoire de {e(P)} brut, un passage à 60 % donne {e(b)} brut de salaire, soit {e2(n)} net, plus {e2(P * (1 - q))} de pension brute.</p>
{table(["Quotité", "Salaire brut", "Salaire net", "Part de pension brute", "Total"], lignes)}
{note("Salaire de 3 000 € brut à temps plein, non-cadre, cotisations 2026 ; pension provisoire de 1 600 € brut. Le total additionne un salaire net et une pension brute, avant CSG, CRDS et Casa sur la pension.")}
<h2>Démarches et délais</h2>
<p>Le salarié adresse sa demande de temps partiel à l'employeur par lettre recommandée, au moins deux mois avant la date voulue. L'employeur a deux mois pour répondre : sans réponse écrite et motivée, la demande est acceptée, et un refus doit montrer que la durée demandée est incompatible avec l'activité de l'entreprise. La demande de pension se fait ensuite en ligne sur Info Retraite, au plus tôt cinq mois avant la date souhaitée, avec l'attestation de l'employeur.</p>
<h2>Au départ définitif</h2>
<p>Les trimestres et les points acquis pendant le temps partiel s'ajoutent. La pension définitive est recalculée et ne peut pas être inférieure à la pension provisoire. Le salarié peut aussi demander à cotiser sur la base d'un temps plein (surcotisation), avec l'accord de l'employeur, pour ne pas perdre de droits. Un changement de quotité entre 40 % et 80 % révise la fraction versée le mois suivant ; une sortie de cette fourchette suspend le versement, et un retour à temps plein y met fin.</p>
<p>Pour estimer la pension provisoire, voir le <a href="/calcul-retraite/">calcul de la retraite de base</a> ; après le départ définitif, une reprise d'activité relève du <a href="/cumul-emploi-retraite/">cumul emploi-retraite</a>.</p>
"""
    js = """
            var s = v('w-salaire'), q = v('w-quotite') / 100, p = v('w-pension');
            if (q < 0.4 || q > 0.8) { out('r-brut', 'Hors 40-80 %'); out('r-net', '–'); out('r-part', '–'); out('r-total', '–'); return; }
            var brut = s * q;
            var n = calculerBrutVersNet(brut, document.getElementById('w-statut').value, 1).netAvantImpot;
            out('r-brut', euros(brut));
            out('r-net', centimes(n));
            out('r-part', centimes(p * (1 - q)));
            out('r-total', centimes(n + p * (1 - q)));"""
    return {
        "slug": "retraite-progressive",
        "title": "Retraite progressive 2026 : dès 60 ans, calcul de la pension",
        "desc": "Retraite progressive 2026 : dès 60 ans avec 150 trimestres, temps partiel de 40 à 80 %. Simulateur du salaire net et de la fraction de pension versée.",
        "h1": "Retraite progressive 2026",
        "crumb": "Retraite progressive",
        "widget_titre": "Salaire et pension en retraite progressive",
        "widget": widget([champ("w-salaire", "Salaire brut à temps plein (€/mois)", "3000"),
                          champ("w-quotite", "Temps de travail (% d'un temps plein)", "60"),
                          champ("w-pension", "Pension provisoire brute (€/mois)", "1600"),
                          choix("w-statut", "Statut", STATUT, "non-cadre")],
                         [("r-brut", "Salaire brut"), ("r-net", "Salaire net"), ("r-part", "Pension brute versée"), ("r-total", "Total mensuel")],
                         "La pension provisoire figure dans votre estimation sur info-retraite.fr. Le total additionne salaire net et pension brute."),
        "js": js,
        "citable": f"La retraite progressive permet à un salarié de travailler à temps partiel tout en touchant une partie de sa retraite. En 2026, elle est ouverte dès 60 ans, quelle que soit l'année de naissance, à condition de réunir 150 trimestres d'assurance et de travailler entre 40 % et 80 % d'un temps complet. La fraction de pension versée est égale à 100 % moins la quotité travaillée : à 60 % de temps de travail, le salarié reçoit 40 % de sa pension provisoire. Avec {e(S)} brut à temps plein et une pension provisoire de {e(P)}, cela donne {e2(n)} net de salaire et {e2(P * (1 - q))} brut de pension par mois. Au départ définitif, la pension est recalculée avec les droits acquis pendant le temps partiel et ne peut pas être inférieure à la pension provisoire.",
        "corps": corps,
        "sources": [SRC_PROGRESSIVE, SRC_PROGRESSIVE_60, SRC_PROGRESSIVE_FP, SRC_AGE_RETRAITE, SRC_TAUX],
        "faq": [
            ("À partir de quel âge peut-on demander la retraite progressive ?",
             "Depuis le 1er septembre 2025, à 60 ans pour tous les assurés, salariés comme agents publics, en application du décret du 15 juillet 2025. Auparavant, l'âge d'accès était fixé deux ans avant l'âge légal de départ, ce qui le faisait reculer avec la réforme de 2023. Il faut en plus réunir 150 trimestres d'assurance, tous régimes de base confondus, et travailler à temps partiel."),
            ("Quelle part de la retraite touche-t-on en retraite progressive ?",
             "La fraction versée est égale à 100 % moins la quotité de temps de travail. Un salarié à 70 % touche 30 % de sa pension provisoire, un salarié à 40 % en touche 60 %. Cette pension provisoire est calculée sur les droits acquis à la date de la demande, pour la retraite de base comme pour la complémentaire Agirc-Arrco, puis révisée si la quotité change."),
            ("L'employeur peut-il refuser une retraite progressive ?",
             "Il peut refuser le passage à temps partiel, mais seulement par une réponse écrite et motivée, envoyée dans les deux mois suivant la demande. Le refus doit expliquer en quoi la durée de travail demandée est incompatible avec l'activité économique de l'entreprise. Sans réponse dans ce délai, la demande est réputée acceptée et le salarié peut solliciter sa pension auprès des caisses."),
            ("La retraite progressive diminue-t-elle la retraite définitive ?",
             "Non. Les trimestres et les points acquis pendant le temps partiel s'ajoutent aux droits antérieurs, et la pension définitive ne peut pas être inférieure à la pension provisoire. Le salaire à temps partiel réduit en revanche le salaire annuel moyen si ces années comptent parmi les 25 meilleures ; la surcotisation sur la base d'un temps plein, possible avec l'accord de l'employeur, évite cet effet."),
            ("Peut-on cumuler retraite progressive et deux emplois à temps partiel ?",
             "Oui, si la durée totale de travail chez les différents employeurs reste comprise entre 40 % et 80 % d'un temps complet. La quotité retenue est la somme des temps partiels. Chaque employeur remplit une attestation. Si le total sort de la fourchette, le versement est suspendu, puis reprend dès que la condition est de nouveau remplie, sur simple déclaration à la caisse."),
            ("Comment est calculé le temps partiel d'un salarié au forfait jours ?",
             "Pour un salarié au forfait annuel en jours, la quotité se calcule en rapportant le nombre de jours prévus par la convention de forfait au plafond de 218 jours. Un forfait réduit de 131 jours correspond ainsi à environ 60 %, et ouvre droit à 40 % de la pension provisoire. Le forfait réduit doit être formalisé par écrit avec l'employeur."),
        ],
        "related": ["calcul-retraite", "cumul-emploi-retraite", "salaire-brut-net-horaire", "salaire-brut-net-non-cadre", "salaire-brut-net-cadre", "jours-rtt"],
        "releve": RELEVE,
        "note_sources": "Le salaire net est estimé avec les cotisations 2026 du régime général, hors mutuelle ; la pension est indiquée brute, avant CSG, CRDS et Casa.",
    }


def page_calcul_retraite():
    gen = GENERATIONS[4]  # 1963 à mars 1965
    p_ex, taux_ex, dec_ex, _ = pension_base(30000, 166, 62.75, gen[1], gen[2])
    p_plein, _, _, _ = pension_base(30000, 170, 62.75, gen[1], gen[2])
    p_sur, _, _, sur_ex = pension_base(30000, 174, 63.75, gen[1], gen[2])
    sp, _, _, _ = pension_base(38400, 170, 62.75, gen[1], gen[2])
    gen_lignes = [[g[0], f"{int(g[1])} ans" + (f" et {round((g[1] - int(g[1])) * 12)} mois" if g[1] % 1 else ""), str(g[2])]
                  for g in GENERATIONS]
    idr = indemnite_depart(25, 2800)
    imr = indemnite_mise_retraite(25, 2800)
    agirc_ex = 6000 * POINT_AGIRC_ARRCO / 12
    corps = f"""
<h2>La formule de la retraite de base</h2>
<p>Au régime général, la pension annuelle brute est égale au <strong>salaire annuel moyen × taux × durée d'assurance ÷ durée requise</strong>. Le salaire annuel moyen est la moyenne des 25 meilleures années, chaque année étant revalorisée et retenue dans la limite du plafond de la Sécurité sociale de l'époque. Le taux plein est de 50 %. La pension de base ne peut pas dépasser la moitié du plafond, soit <strong>{e2(PENSION_MAX)} brut par mois en 2026</strong>, sauf surcote.</p>
<p>Service-public.gouv.fr donne l'exemple d'un salaire annuel moyen de 38 400 € avec 170 trimestres, autant que la durée requise : la pension atteint {e(sp * 12)} par an, soit {e(sp)} brut par mois.</p>
<h2>Âge légal et trimestres requis selon l'année de naissance</h2>
{table(["Date de naissance", "Âge légal", "Trimestres requis"], gen_lignes)}
{note("Service-public.gouv.fr, fiches F14043 (vérifiée le 14 août 2026) et F21552 (vérifiée le 1er septembre 2026). La loi de financement de la Sécurité sociale pour 2026 a suspendu la réforme de 2023 : les assurés nés de 1963 à mars 1965 partent à 62 ans et 9 mois avec 170 trimestres. Le taux plein est accordé sans condition de durée à 67 ans.")}
<h2>Décote et surcote</h2>
<p>Partir avant 67 ans sans tous les trimestres coûte une <strong>décote de 0,625 point de taux par trimestre manquant</strong>, dans la limite de 20 trimestres : le taux descend au minimum à 37,5 %. Le nombre de trimestres manquants est le plus petit de deux écarts, celui qui sépare de la durée requise et celui qui sépare de 67 ans. À l'inverse, chaque trimestre cotisé après l'âge légal et au-delà de la durée requise ajoute une <strong>surcote de 1,25 %</strong> à la pension.</p>
{table(["Cas (né en 1964, salaire moyen 30 000 €)", "Trimestres", "Taux", "Pension brute mensuelle"], [
    ["Départ à 62 ans et 9 mois, 4 trimestres manquants", "166", pct(taux_ex * 100, 2), e2(p_ex)],
    ["Départ à 62 ans et 9 mois, durée complète", "170", "50,00 %", e2(p_plein)],
    [f"Départ à 63 ans et 9 mois, {sur_ex} trimestres de surcote", "174", "50,00 % + 5 %", e2(p_sur)],
])}
{note("Pension de base du régime général seule. Le minimum contributif porte une pension à taux plein à au moins 903,94 € brut par mois si tous les trimestres ont été cotisés (756,29 € sinon), tant que le total des retraites reste sous 1 410,89 €.")}
<h2>La retraite complémentaire Agirc-Arrco</h2>
<p>Elle s'ajoute à la pension de base et se calcule en points : nombre de points × valeur de service du point, <strong>{fmt2(POINT_AGIRC_ARRCO)} €</strong> du 1er novembre 2025 au 31 octobre 2026. 6 000 points donnent ainsi {e2(agirc_ex)} brut par mois. Une revalorisation au 1er novembre 2026 a été annoncée par la presse ; nous ne l'avons pas trouvée publiée sur un site officiel à la date du relevé, et le simulateur garde donc la valeur de {fmt2(POINT_AGIRC_ARRCO)} €. Votre nombre de points figure sur votre relevé de carrière.</p>
<h2>L'indemnité de départ à la retraite</h2>
<p>Un salarié qui part volontairement à la retraite avec au moins dix ans d'ancienneté reçoit une indemnité légale d'un demi-mois de salaire (10 à 15 ans), un mois (15 à 20 ans), un mois et demi (20 à 30 ans) ou deux mois (30 ans et plus). Le salaire de référence est le plus favorable entre la moyenne des douze derniers mois et celle des trois derniers. Si c'est l'employeur qui met le salarié à la retraite, l'indemnité est au moins égale à l'indemnité légale de licenciement : un quart de mois par année jusqu'à dix ans, un tiers au-delà. Pour {e(2800)} de salaire et 25 ans d'ancienneté : {e(idr)} en départ volontaire, {e2(imr)} en mise à la retraite. Une convention collective peut prévoir mieux.</p>
<div class="rounded-xl border border-slate-200 bg-white p-4 mt-4 mb-4">
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">{champ("w-anc", "Ancienneté (années)", "25")}{champ("w-sref", "Salaire brut de référence (€/mois)", "2800")}</div>
{resultats([("r-depart", "Départ volontaire"), ("r-mise", "Mise à la retraite")])}
</div>
<p>L'indemnité de départ volontaire est soumise à cotisations, à la CSG et à l'impôt sur le revenu ; celle de mise à la retraite bénéficie d'exonérations dans certaines limites. Pour un départ par rupture d'un commun accord, voir l'<a href="/indemnite-rupture-conventionnelle/">indemnité de rupture conventionnelle</a>.</p>
"""
    opts = [(f"{g[1]}|{g[2]}", f"{g[0]} ({g[2]} trimestres)") for g in GENERATIONS]
    js = """
            var sam = Math.min(v('w-sam'), 48060), trim = v('w-trim'), age = v('w-age');
            var g = document.getElementById('w-gen').value.split('|');
            var al = parseFloat(g[0]), req = parseFloat(g[1]);
            var dec = 0;
            if (age < 67) { dec = Math.min(Math.max(0, req - trim), Math.ceil((67 - age) * 4 - 1e-9), 20); }
            var taux = 0.5 - 0.00625 * dec;
            var p = sam * taux * Math.min(trim, req) / req / 12;
            p = Math.min(p, 2002.5);
            var sur = 0;
            if (trim > req && age > al) { sur = Math.min(trim - req, Math.floor((age - al) * 4 + 1e-9)); }
            p = p * (1 + 0.0125 * sur);
            var compl = v('w-points') * %(point)s / 12;
            if (age < al) { out('r-taux', 'Avant l\\'âge légal'); } else { out('r-taux', (taux * 100).toFixed(2).replace('.', ',') + ' %%' + (sur ? ' + ' + (sur * 1.25).toFixed(2).replace('.', ',') + ' %%' : '')); }
            out('r-base', centimes(p));
            out('r-compl', centimes(compl));
            out('r-total', centimes(p + compl));
            var anc = v('w-anc'), sref = v('w-sref');
            var mois = anc < 10 ? 0 : anc < 15 ? 0.5 : anc < 20 ? 1 : anc < 30 ? 1.5 : 2;
            out('r-depart', centimes(sref * mois));
            out('r-mise', centimes(sref * (Math.min(anc, 10) / 4 + Math.max(0, anc - 10) / 3)));""" % {"point": POINT_AGIRC_ARRCO}
    return {
        "slug": "calcul-retraite",
        "title": "Retraite de base 2026 : calcul de la pension, taux et décote",
        "desc": "Retraite de base 2026 : salaire annuel moyen × 50 % × trimestres ÷ durée requise, plafond 2 002,50 € par mois. Simulateur avec décote, surcote et Agirc-Arrco.",
        "h1": "Calcul de la retraite 2026",
        "crumb": "Calcul de la retraite",
        "widget_titre": "Estimer sa pension de retraite",
        "widget": widget([champ("w-sam", "Salaire annuel moyen brut (€)", "30000"),
                          choix("w-gen", "Année de naissance", opts, f"{GENERATIONS[4][1]}|{GENERATIONS[4][2]}"),
                          champ("w-trim", "Trimestres validés au départ", "170"),
                          champ("w-age", "Âge de départ (ans, ex. 62,75)", "62,75"),
                          champ("w-points", "Points Agirc-Arrco", "6000")],
                         [("r-taux", "Taux appliqué"), ("r-base", "Pension de base brute"), ("r-compl", "Complémentaire brute"), ("r-total", "Total brut mensuel")],
                         "Salaire annuel moyen : moyenne de vos 25 meilleures années, chacune plafonnée au PSS. Estimation hors majorations pour enfants et minimum contributif."),
        "js": js,
        "citable": f"La retraite de base d'un salarié du privé se calcule en 2026 avec la formule salaire annuel moyen × taux × trimestres validés ÷ trimestres requis. Le salaire annuel moyen porte sur les 25 meilleures années, chacune plafonnée au plafond de la Sécurité sociale. Le taux plein est de 50 % ; chaque trimestre manquant avant 67 ans retire 0,625 point, jusqu'à 37,5 %, et chaque trimestre travaillé en plus après l'âge légal ajoute 1,25 % à la pension. Depuis la suspension de la réforme par la loi de financement pour 2026, une personne née en 1964 peut partir à 62 ans et 9 mois avec 170 trimestres. Avec 30 000 € de salaire annuel moyen et une carrière complète, la pension de base atteint {e2(p_plein)} brut par mois, sans dépasser {e2(PENSION_MAX)}. La complémentaire Agirc-Arrco s'y ajoute, au prix de {fmt2(POINT_AGIRC_ARRCO)} € le point.",
        "corps": corps,
        "sources": [SRC_MONTANT_RETRAITE, SRC_AGE_RETRAITE, SRC_SURCOTE, SRC_SURCOTE_CNAV, SRC_AGIRC, SRC_DEPART],
        "faq": [
            ("Comment est calculé le salaire annuel moyen de la retraite ?",
             "La caisse retient les 25 années civiles où vous avez le mieux gagné, 24 ou 23 dans certains cas liés aux enfants. Chaque salaire annuel est limité au plafond de la Sécurité sociale de l'année concernée, puis revalorisé par des coefficients officiels pour tenir compte des prix. L'année du départ n'est pas comptée. La moyenne obtenue est le salaire annuel moyen utilisé dans la formule."),
            ("Quel est l'âge de départ à la retraite pour une personne née en 1965 ?",
             "Cela dépend du mois de naissance. Né entre janvier et mars 1965, vous pouvez partir à 62 ans et 9 mois avec 170 trimestres, grâce à la suspension de la réforme votée pour 2026. Né entre avril et décembre 1965, l'âge légal est de 63 ans et la durée requise de 171 trimestres. Dans les deux cas, le taux plein est automatique à 67 ans."),
            ("Combien coûte un trimestre manquant sur la retraite ?",
             "Chaque trimestre manquant retire 0,625 point au taux de 50 %, soit une baisse de 1,25 % de la pension de base, auquel s'ajoute l'effet de la proratisation : la pension est aussi multipliée par les trimestres validés rapportés aux trimestres requis. Quatre trimestres manquants font ainsi passer le taux à 47,5 % et réduisent la pension d'environ 7,3 % au total."),
            ("Quel est le montant maximum de la retraite de base en 2026 ?",
             f"La pension de base du régime général est limitée à la moitié du plafond annuel de la Sécurité sociale, soit {e2(PENSION_MAX)} brut par mois en 2026. Seule la surcote permet de dépasser ce plafond. Les retraites complémentaires, comme l'Agirc-Arrco, n'ont pas de plafond comparable : elles dépendent uniquement du nombre de points acquis pendant la carrière."),
            ("Qu'est-ce que le minimum contributif ?",
             f"C'est un montant plancher accordé aux pensions à taux plein : {e2(MIN_CONTRIBUTIF)} brut par mois en 2026 si tous les trimestres requis ont été cotisés, {e2(MIN_CONTRIBUTIF_BASE)} sinon. Il n'est versé que si le total des retraites, de base et complémentaires, ne dépasse pas {e2(MIN_CONTRIBUTIF_PLAFOND)} brut par mois ; à défaut, il est réduit d'autant. La caisse l'applique automatiquement lors du calcul."),
            ("L'indemnité de départ à la retraite est-elle imposable ?",
             "Oui, lorsque le départ est volontaire : l'indemnité est soumise à l'impôt sur le revenu, aux cotisations sociales et à la CSG-CRDS, comme un salaire. Lorsque l'employeur met le salarié à la retraite, l'indemnité bénéficie d'exonérations sociales et fiscales dans certaines limites. La convention collective peut prévoir un montant plus élevé que le minimum légal, qu'il faut toujours vérifier."),
        ],
        "related": ["retraite-progressive", "cumul-emploi-retraite", "plafond-securite-sociale-2026", "salaire-brut-net-annuel", "salaire-brut-net-fonction-publique", "indemnite-licenciement"],
        "releve": RELEVE,
        "note_sources": "Les pensions sont des estimations brutes, avant CSG, CRDS et Casa ; seule l'estimation de votre caisse sur info-retraite.fr fait foi.",
    }


def page_prime_activite():
    smic_net = SMIC_NET_MENSUEL_SP
    pa_smic = prime_activite(smic_net)
    pa_smic_al = prime_activite(smic_net, logement=True)
    lignes = []
    for r in (700, 1000, 1200, smic_net, 1700, 2000):
        lignes.append([e2(r), e2(pa_bonif(r)), e2(prime_activite(r)), e2(prime_activite(r, logement=True))])
    fam = [
        ["Personne seule", e2(pa_forfait("seul", 0)), e2(prime_activite(1200))],
        ["Seul avec un enfant", e2(pa_forfait("seul", 1)), e2(prime_activite(1200, "seul", 1))],
        ["Couple sans enfant, un salaire", e2(pa_forfait("couple", 0)), e2(prime_activite(1200, "couple", 0))],
        ["Couple avec deux enfants, un salaire", e2(pa_forfait("couple", 2)), e2(prime_activite(1200, "couple", 2))],
    ]
    corps = f"""
<h2>La formule de la prime d'activité</h2>
<p>La Caf calcule chaque trimestre : <strong>montant forfaitaire + 59,85 % des revenus professionnels + bonifications individuelles − ressources du foyer</strong>. Les ressources retenues ne peuvent pas être inférieures au montant forfaitaire. Elles comprennent les revenus d'activité, les autres revenus (pensions, allocations hors exceptions) et un forfait logement si le foyer touche une aide au logement ou est logé gratuitement. La prime n'est pas versée si elle est inférieure à 15 €.</p>
{table(["Paramètre au 1er avril 2026", "Montant"], [
    ["Montant forfaitaire, personne seule", e2(PA_MF[("seul", 0)])],
    ["Part des revenus professionnels retenue", "59,85 %"],
    ["Bonification : début", f"{e2(PA_BONIF_DEBUT)} de revenus"],
    ["Bonification maximale", f"{e2(PA_BONIF_MAX)} dès {e2(PA_BONIF_PLEINE)}"],
    ["Forfait logement 1, 2, 3 personnes et plus", f"{e2(76.59)}, {e2(153.19)}, {e2(189.57)}"],
])}
{note("Décret n° 2026-222 du 30 mars 2026 et service-public.gouv.fr, fiche F2882 vérifiée le 1er juin 2026. Les seuils de la bonification (59 et 138 fois le Smic horaire) sont ceux calculés par service-public avec le Smic de 12,31 € ; une page de la Caf publiée en avril les donne avec le Smic de janvier (1 658,76 € pour le plein).")}
<h2>Ce que change la réforme d'avril 2026</h2>
<p>Le décret du 30 mars 2026 a revalorisé le forfait de 0,8 % et surtout renforcé la bonification individuelle : son maximum passe de 29,101 % à 37,7 % du montant forfaitaire, soit {e2(PA_BONIF_MAX)}, et il est atteint à 138 fois le Smic horaire au lieu de 120. Les salariés payés entre le Smic et 1,15 Smic sont les premiers gagnants. Les premiers versements recalculés sont intervenus à partir de juillet 2026, selon le trimestre déclaré.</p>
<h2>Montant selon le salaire, personne seule</h2>
{table(["Revenus d'activité nets", "Bonification", "Prime sans aide au logement", "Prime avec aide au logement"], lignes)}
{note(f"Personne seule sans enfant ni autre ressource. La ligne {e2(smic_net)} correspond au Smic net à temps plein depuis le 1er juin 2026.")}
<h2>Montant selon la composition du foyer</h2>
{table(["Foyer, 1 200 € nets de salaire", "Montant forfaitaire", "Prime estimée"], fam)}
{note("Sans aide au logement ni autre ressource ; dans les couples, un seul membre travaille. Le montant majoré des parents isolés, accordé sous conditions pendant une durée limitée, n'est pas pris en compte.")}
<p>Ces calculs restent des estimations : la Caf retient les revenus nets des trois mois précédant la déclaration, compte certaines prestations familiales et applique des règles particulières aux indépendants, aux étudiants et aux apprentis. Seul le simulateur de la Caf, puis la déclaration trimestrielle, donnent le montant exact.</p>
"""
    js = """
            var r1 = v('w-r1'), r2 = v('w-r2'), autres = v('w-autres');
            var foyer = document.getElementById('w-foyer').value, enf = Math.max(0, Math.round(v('w-enf')));
            var logement = document.getElementById('w-logement').value === 'oui';
            var mf = foyer === 'couple' ? [957.42, 1148.90, 1340.39][Math.min(enf, 2)] : [638.28, 957.42, 1148.90][Math.min(enf, 2)];
            mf += 255.31 * Math.max(0, enf - 2);
            if (foyer !== 'couple') { r2 = 0; }
            var pers = (foyer === 'couple' ? 2 : 1) + enf;
            var fl = logement ? [76.59, 153.19, 189.57][Math.min(pers, 3) - 1] : 0;
            function bonif(r) { if (r <= 726.29) return 0; if (r >= 1698.78) return 240.63; return 240.63 * (r - 726.29) / (1698.78 - 726.29); }
            var b = bonif(r1) + bonif(r2);
            var pa = mf + 0.5985 * (r1 + r2) + b - Math.max(mf, r1 + r2 + autres + fl);
            if (pa < 15) { pa = 0; }
            out('r-mf', centimes(mf));
            out('r-bonif', centimes(b));
            out('r-pa', centimes(pa));"""
    return {
        "slug": "prime-activite",
        "title": "Prime d'activité 2026 : simulateur, forfait de 638,28 €",
        "desc": "Prime d'activité 2026 : montant forfaitaire de 638,28 €, 59,85 % des revenus et bonification jusqu'à 240,63 €. Simulateur selon salaire, couple et enfants.",
        "h1": "Prime d'activité 2026",
        "crumb": "Prime d'activité",
        "widget_titre": "Estimer sa prime d'activité",
        "widget": widget([champ("w-r1", "Votre salaire net (€/mois)", fmt2(smic_net).replace(" ", "")),
                          choix("w-foyer", "Situation", [("seul", "Seul"), ("couple", "En couple")], "seul"),
                          champ("w-enf", "Enfants à charge", "0", "numeric"),
                          champ("w-r2", "Salaire net du conjoint (€/mois)", "0"),
                          champ("w-autres", "Autres ressources du foyer (€/mois)", "0"),
                          choix("w-logement", "Aide au logement ou logé gratuitement", [("non", "Non"), ("oui", "Oui")], "non")],
                         [("r-mf", "Montant forfaitaire"), ("r-bonif", "Bonifications"), ("r-pa", "Prime d'activité estimée")],
                         "Estimation indicative avec le barème du 1er avril 2026 : la Caf ou la MSA calcule seule le montant dû, sur vos trois derniers mois de revenus."),
        "js": js,
        "citable": f"La prime d'activité complète les revenus des salariés modestes de 18 ans et plus. Depuis le 1er avril 2026, la Caf la calcule ainsi : un montant forfaitaire de {e2(PA_MF[('seul', 0)])} pour une personne seule, plus 59,85 % des revenus professionnels, plus une bonification individuelle qui démarre à {e2(PA_BONIF_DEBUT)} de revenus et atteint {e2(PA_BONIF_MAX)} dès {e2(PA_BONIF_PLEINE)}, moins les ressources du foyer. Pour une personne seule payée au Smic net à temps plein, soit {e2(smic_net)}, la prime estimée atteint environ {e2(pa_smic)} par mois, ou {e2(pa_smic_al)} si elle touche une aide au logement, qui ajoute un forfait de 76,59 € aux ressources. La prime n'est pas imposable, n'est pas versée sous 15 € et se renouvelle par déclaration trimestrielle.",
        "corps": corps,
        "sources": [SRC_PA, SRC_PA_DECRET, SRC_PA_CAF, SRC_PA_BAREME, SRC_SMIC],
        "faq": [
            ("Quel salaire maximum pour toucher la prime d'activité ?",
             f"Il n'existe pas de plafond unique : tout dépend du foyer. Pour une personne seule sans autre ressource, la prime estimée s'éteint vers {e(2150)} nets par mois avec le barème d'avril 2026, soit environ 1,45 fois le Smic net ; la Caf parle d'un seuil de sortie proche de 1,5 Smic. Un couple ou un parent atteint un seuil plus élevé, car le montant forfaitaire augmente avec chaque personne du foyer."),
            ("Comment est calculée la bonification individuelle en 2026 ?",
             f"Chaque membre du foyer qui travaille y a droit séparément. Elle est nulle jusqu'à {e2(PA_BONIF_DEBUT)} de revenus d'activité mensuels, augmente ensuite en ligne droite et atteint son maximum de {e2(PA_BONIF_MAX)} à {e2(PA_BONIF_PLEINE)}, montant au-delà duquel elle ne bouge plus. Le décret du 30 mars 2026 a relevé ce maximum de près de 56 € pour les revenus proches du Smic."),
            ("Qu'est-ce que le forfait logement de la prime d'activité ?",
             "C'est une somme ajoutée d'office aux ressources du foyer lorsqu'il perçoit une aide au logement, est propriétaire sans emprunt ou est logé gratuitement. Au 1er avril 2026, il vaut 76,59 € pour une personne seule, 153,19 € pour deux personnes et 189,57 € à partir de trois. Comme il augmente les ressources retenues, il diminue la prime du même montant."),
            ("La prime d'activité est-elle versée aux apprentis et aux étudiants ?",
             "Oui, à condition que leurs revenus d'activité dépassent, chaque mois du trimestre, un seuil égal à 78 % du Smic net environ. En dessous, ils ne peuvent pas y prétendre, sauf s'ils ont des enfants à charge. La Caf vérifie ce seuil mois par mois au moment de la déclaration trimestrielle, et les rémunérations d'apprenti comptent comme des revenus professionnels."),
            ("Quand la prime d'activité est-elle versée ?",
             "La prime est versée chaque mois, vers le 5, à partir du mois de la demande, et son montant reste fixe pendant trois mois. Il est ensuite recalculé à partir de la déclaration trimestrielle, qui porte sur les revenus des trois mois précédents, désormais préremplis avec le montant net social. Oublier cette déclaration interrompt les versements jusqu'à ce qu'elle soit faite."),
            ("Les heures supplémentaires comptent-elles pour la prime d'activité ?",
             "Oui. Toutes les rémunérations d'activité entrent dans les revenus professionnels, y compris les heures supplémentaires et les primes, pour leur montant net. Une hausse de salaire augmente donc la part de 59,85 % et la bonification, mais aussi les ressources déduites, si bien que la prime baisse progressivement à mesure que le salaire progresse, sans jamais faire perdre plus qu'elle ne rapporte."),
        ],
        "related": ["smic-brut-net-2026", "salaire-brut-net-horaire", "heures-supplementaires-brut-net", "salaire-brut-net-alternance-apprentissage", "salaire-net-imposable", "salaire-moyen-france"],
        "releve": RELEVE,
        "note_sources": "La prime estimée ne tient compte ni des prestations familiales, ni des règles propres aux indépendants : seul le calcul de la Caf ou de la MSA fait foi.",
    }


def page_portage():
    ex = portage(500, 18, 0.08)
    lignes = []
    for tjm in (300, 400, 500, 650, 800):
        r = portage(tjm, 18, 0.08)
        lignes.append([e(tjm), e(r["ca"]), e(r["brut"]), e(r["reserve"]), e(r["net"]), pct(r["net"] / r["ca"] * 100, 0)])
    mins = [[k, pct(t * 100, 0), e2(PSS_MENSUEL * t)] for k, t in PORTAGE_MIN.items()]
    corps = f"""
<h2>Du chiffre d'affaires au salaire net</h2>
<p>En portage salarial, le client paie la société de portage, qui reverse au consultant un salaire. Le calcul suit toujours le même ordre : <strong>chiffre d'affaires hors taxes − frais de gestion − frais professionnels remboursés = enveloppe</strong> ; l'enveloppe finance le coût employeur complet, c'est-à-dire le salaire brut, la réserve financière et les cotisations patronales ; on retire enfin les cotisations salariales pour obtenir le net.</p>
<p>Avec un tarif de {e(500)} par jour sur 18 jours et 8 % de frais de gestion, le chiffre d'affaires de {e(ex['ca'])} laisse une enveloppe de {e(ex['enveloppe'])}. Elle couvre un salaire brut de {e(ex['brut'])}, une réserve financière de {e(ex['reserve'])} et les cotisations patronales ; le net avant impôt ressort à <strong>{e(ex['net'])}</strong>, soit {pct(ex['net'] / ex['ca'] * 100, 0)} du chiffre d'affaires.</p>
{table(["Tarif journalier", "Chiffre d'affaires", "Salaire brut", "Réserve", "Net mensuel", "Net ÷ CA"], lignes)}
{note("18 jours facturés, 8 % de frais de gestion, aucun frais professionnel, statut cadre, entreprise de portage de 50 salariés et plus, taux Urssaf 2026, accident du travail 1 %, prévoyance cadre 1,50 % sur la tranche 1, réduction générale dégressive comprise, hors versement mobilité et mutuelle.")}
<h2>Frais de gestion et réserve financière</h2>
<p>Les frais de gestion ne sont pas réglementés : ils se négocient avec la société de portage, le plus souvent entre 5 % et 10 % du chiffre d'affaires. La <strong>réserve financière</strong> est en revanche prévue par la convention collective de branche : 10 % du salaire de base, mis de côté sur le compte d'activité et versés en fin de mission ou de contrat. Le salaire comprend aussi une indemnité d'apport d'affaires de 5 % du salaire de base. Le simulateur traite la réserve comme un salaire différé, soumis aux mêmes cotisations.</p>
<h2>La rémunération minimale en 2026</h2>
<p>Le portage n'est ouvert qu'aux salariés autonomes, experts dans leur domaine, et suppose un salaire minimum calculé sur le plafond mensuel de la Sécurité sociale (4 005 € en 2026). La convention de branche fixe trois niveaux, auxquels s'ajoute la réserve financière ; à défaut d'accord, le Code du travail retient 75 % du plafond pour un temps plein.</p>
{table(["Niveau", "Part du PSS", "Minimum brut mensuel 2026"], mins)}
{note("Convention collective de branche des salariés en portage salarial du 22 mars 2017, article 21 ; Code du travail, article L. 1254-2. Montants pour un temps plein, indemnité d'apport d'affaires comprise.")}
<p>Un consultant porté reste salarié : il cotise au chômage, à la retraite de base et complémentaire, et bénéficie de la prévoyance cadre. C'est la différence avec la micro-entreprise, moins chère en cotisations mais sans assurance chômage. Le passage du brut au net suit les règles des <a href="/salaire-brut-net-cadre/">salaires cadres</a> ; le détail des cotisations patronales figure sur la page <a href="/cout-employeur/">coût employeur</a>.</p>
"""
    js = """
            var tjm = v('w-tjm'), jours = v('w-jours'), fg = v('w-frais') / 100, fp = v('w-fpro');
            var ca = tjm * jours, env = Math.max(0, ca * (1 - fg) - fp);
            function cout(b) {
                var p = 4005, t1 = Math.min(b, p), t2 = Math.max(0, b - p), l4 = Math.min(b, 4 * p);
                var ch = b * (0.13 + 0.0211 + 0.0525 + 0.01 + 0.003 + 0.005 + 0.00016 + 0.01 + 0.0068) + t1 * (0.0855 + 0.0472 + 0.0129 + 0.015) + t2 * (0.1295 + 0.0162) + l4 * (0.04 + 0.0025 + 0.00036) + (b > p ? b * 0.0021 : 0);
                var s = %(smic)s * 3, coef = 0;
                if (b > 0 && b < s) { coef = Math.min(0.4021, 0.02 + 0.3821 * Math.pow(0.5 * (s / b - 1), 1.75)); }
                return b + ch - b * coef;
            }
            var lo = 0, hi = env;
            for (var i = 0; i < 60; i++) { var mid = (lo + hi) / 2; if (cout(mid) > env) { hi = mid; } else { lo = mid; } }
            var brut = lo / 1.1, reserve = lo - brut;
            var n = brut > 0 ? calculerBrutVersNet(brut, 'cadre', 1).netAvantImpot : 0;
            out('r-ca', euros(ca));
            out('r-brut', euros(brut));
            out('r-reserve', euros(reserve));
            out('r-net', euros(n));
            out('r-total', euros(n + fp));""" % {"smic": SMIC_MENSUEL_JANVIER}
    return {
        "slug": "portage-salarial",
        "title": "Portage salarial 2026 : simulateur du TJM au salaire net",
        "desc": f"Portage salarial 2026 : à 500 € par jour sur 18 jours et 8 % de frais, il reste environ {e(ex['net'])} net par mois. Simulateur avec réserve de 10 % et cotisations.",
        "h1": "Portage salarial 2026 : du TJM au net",
        "crumb": "Portage salarial",
        "widget_titre": "Salaire net en portage salarial",
        "widget": widget([champ("w-tjm", "Tarif journalier HT (€)", "500"),
                          champ("w-jours", "Jours facturés dans le mois", "18"),
                          champ("w-frais", "Frais de gestion (%)", "8"),
                          champ("w-fpro", "Frais professionnels remboursés (€/mois)", "0")],
                         [("r-ca", "Chiffre d'affaires"), ("r-brut", "Salaire brut"), ("r-reserve", "Réserve financière"), ("r-net", "Net avant impôt"), ("r-total", "Net + frais remboursés")],
                         "Statut cadre, société de portage de 50 salariés et plus, cotisations 2026. Les frais professionnels sont remboursés sans cotisations, sur justificatifs."),
        "js": js,
        "citable": f"En portage salarial, le salaire net dépend du chiffre d'affaires facturé, des frais de gestion de la société de portage et des cotisations sociales d'un cadre. En 2026, un consultant facturant {e(500)} hors taxes par jour pendant 18 jours génère {e(ex['ca'])} de chiffre d'affaires ; après 8 % de frais de gestion, l'enveloppe de {e(ex['enveloppe'])} finance un salaire brut d'environ {e(ex['brut'])}, une réserve financière de {e(ex['reserve'])} versée en fin de mission et les cotisations patronales. Il touche alors environ {e(ex['net'])} net par mois avant impôt, soit {pct(ex['net'] / ex['ca'] * 100, 0)} du chiffre d'affaires. Les frais de gestion se négocient, généralement entre 5 % et 10 %. Le salaire minimum, fixé par la convention de branche, va de 70 % à 85 % du plafond mensuel de la Sécurité sociale, soit {e2(PSS_MENSUEL * 0.7)} à {e2(PSS_MENSUEL * 0.85)} brut.",
        "corps": corps,
        "sources": [SRC_PORTAGE, SRC_PORTAGE_CODE, SRC_PORTAGE_CCN, SRC_PSS, SRC_RGDU, SRC_TAUX],
        "faq": [
            ("Quel pourcentage du chiffre d'affaires reste en net en portage salarial ?",
             f"Un peu moins de la moitié. Avec 8 % de frais de gestion et le statut cadre, notre simulateur donne un net avant impôt compris entre 46 % et 48 % du chiffre d'affaires hors taxes selon le tarif journalier. La part est un peu plus élevée pour les petits tarifs, qui profitent de la réduction générale des cotisations patronales sous trois Smic. Les frais professionnels remboursés améliorent le résultat."),
            ("Qu'est-ce que la réserve financière en portage salarial ?",
             "C'est une somme égale à 10 % du salaire de base, mise de côté chaque mois sur le compte d'activité du salarié porté. Elle est versée à la fin de la mission ou du contrat, ou peut servir à maintenir un salaire entre deux missions. Elle est soumise aux cotisations comme un salaire normal. Les salariés en CDD perçoivent à la place une indemnité de précarité."),
            ("Quel est le salaire minimum en portage salarial en 2026 ?",
             f"La convention de branche fixe trois niveaux, calculés sur le plafond mensuel de la Sécurité sociale de 4 005 € : 70 % pour un junior, soit {e2(PSS_MENSUEL * 0.7)} brut, 75 % pour un senior, soit {e2(PSS_MENSUEL * 0.75)}, et 85 % pour un forfait jours, soit {e2(PSS_MENSUEL * 0.85)}. Ces montants concernent un temps plein et incluent l'indemnité d'apport d'affaires de 5 %."),
            ("Le salarié porté a-t-il droit au chômage ?",
             "Oui. Le salarié porté est un salarié à part entière, en CDD ou en CDI, et la société de portage verse les contributions d'assurance chômage. À la fin d'un contrat, il peut donc s'inscrire à France Travail et percevoir l'allocation d'aide au retour à l'emploi s'il remplit les conditions habituelles de durée d'affiliation. C'est un avantage décisif face à la micro-entreprise."),
            ("Quels frais de gestion prend une société de portage ?",
             "Ils ne sont fixés par aucun texte et figurent dans la convention d'adhésion. Les sociétés affichent le plus souvent des taux de 5 % à 10 % du chiffre d'affaires hors taxes, parfois dégressifs avec le volume facturé, parfois plafonnés par mois. Comparer les offres suppose de vérifier ce que couvrent ces frais : assurance responsabilité civile, avance de trésorerie, gestion des notes de frais."),
            ("Peut-on faire du portage salarial à temps partiel ?",
             "Oui. Le salaire minimum est alors proratisé selon le temps de travail prévu au contrat. Un consultant qui facture dix jours par mois peut donc être porté, à condition que son chiffre d'affaires couvre ce minimum proratisé, les frais de gestion et les cotisations. Le simulateur accepte n'importe quel nombre de jours facturés dans le mois."),
        ],
        "related": ["salaire-brut-net-cadre", "cout-employeur", "plafond-securite-sociale-2026", "reduction-fillon-2026", "allocation-chomage-are", "salaire-ingenieur-informatique"],
        "releve": RELEVE,
        "note_sources": "Le net est estimé avec les cotisations 2026 d'un cadre du régime général, hors mutuelle ; les frais de gestion varient d'une société de portage à l'autre.",
    }


PAGES = [page_cumul, page_progressive, page_calcul_retraite, page_prime_activite, page_portage]
