#!/usr/bin/env python3
"""
Pages « temps de travail et absences » (ajoutées le 2026-10-27) : arrêt maladie, congé
paternité, jours fériés 2026, majorations de nuit et du dimanche, RTT, prime d'ancienneté.

Chaque montant 2026 a été relevé le 27 octobre 2026 sur service-public.gouv.fr, ameli.fr et
code.travail.gouv.fr (articles du Code du travail) : voir les constantes ci-dessous. Les
exemples chiffrés du texte sont calculés ici avec les mêmes formules que le simulateur JS.
"""

import datetime
import math

from thematiques_commun import *  # noqa: F401,F403

RELEVE = "27 octobre 2026"

# ── Chiffres officiels (relevés le 2026-10-27) ────────────────────────────────
# IJ maladie : service-public.gouv.fr F3053 (vérifié le 1er juin 2026) et ameli.fr :
# 50 % du salaire journalier de base (3 derniers salaires ÷ 91,25), salaire retenu dans la
# limite de 1,4 Smic mensuel, soit 2 613,83 € et 42,97 € brut par jour au plus pour un arrêt
# débuté depuis le 1er juillet 2026 ; carence de 3 jours ; CSG 6,2 % et CRDS 0,5 %.
IJ_PLAFOND_SMIC = 1.4
IJ_MALADIE_PLAFOND = round(IJ_PLAFOND_SMIC * SMIC_MENSUEL_BRUT, 2)  # 2 613,83 €
IJ_MALADIE_MAX = round(IJ_MALADIE_PLAFOND * 3 / 91.25 * 0.5, 2)      # 42,97 €
TAUX_CSG_CRDS_IJ = 0.067
# Maintien employeur : Code du travail L1226-1 (un an d'ancienneté), D1226-1 (90 % puis 2/3,
# 30 jours chacun), D1226-2 (+10 jours par période entière de 5 ans au-delà de la première
# année, 90 jours au plus), D1226-3 (à partir du 8e jour), D1226-5 (IJ déduites).
# Paternité : ameli.fr (page du 1er juin 2026) et service-public.gouv.fr F3156 : gain journalier
# de base plafonné au PSS (4 005 €), moins 21 %, soit 104,02 € par jour au plus.
IJ_PATERNITE_MAX = round(PSS_MENSUEL * 3 / 91.25 * 0.79, 2)  # 104,02 €
# Prime d'ancienneté : Code du travail numérique, conventions 1517 et 1351.
BASE_1517 = 1679

SRC_IJ_SP = ("Service-Public.fr, indemnités journalières maladie du salarié", "https://www.service-public.gouv.fr/particuliers/vosdroits/F3053")
SRC_IJ_AMELI = ("Ameli, arrêt maladie : indemnités journalières", "https://www.ameli.fr/assure/remboursements/indemnites-journalieres/arret-maladie")
SRC_D1226_1 = ("Code du travail, article D1226-1 (90 % puis deux tiers)", "https://code.travail.gouv.fr/code-du-travail/d1226-1")
SRC_D1226_2 = ("Code du travail, article D1226-2 (durées selon l'ancienneté)", "https://code.travail.gouv.fr/code-du-travail/d1226-2")
SRC_L1226_1 = ("Code du travail, article L1226-1 (indemnité complémentaire)", "https://code.travail.gouv.fr/code-du-travail/l1226-1")
SRC_PAT_SP = ("Service-Public.fr, congé de paternité et d'accueil de l'enfant", "https://www.service-public.gouv.fr/particuliers/vosdroits/F3156")
SRC_PAT_AMELI = ("Ameli, congé de paternité : vos indemnités journalières", "https://www.ameli.fr/assure/remboursements/indemnites-journalieres/conge-paternite-accueil-enfant")
SRC_CSN = ("Service-Public.fr, congé supplémentaire de naissance (23 juin 2026)", "https://www.service-public.gouv.fr/particuliers/actualites/A18939")
SRC_FERIES = ("Service-Public.fr, jours fériés et ponts dans le secteur privé", "https://www.service-public.gouv.fr/particuliers/vosdroits/F2405")
SRC_L3133_1 = ("Code du travail, article L3133-1 (fêtes légales)", "https://code.travail.gouv.fr/code-du-travail/l3133-1")
SRC_L3133_6 = ("Code du travail, article L3133-6 (1er mai travaillé)", "https://code.travail.gouv.fr/code-du-travail/l3133-6")
SRC_NUIT = ("Service-Public.fr, travail de nuit du salarié du secteur privé", "https://www.service-public.gouv.fr/particuliers/vosdroits/F2212")
SRC_DIMANCHE = ("Service-Public.fr, travail le dimanche d'un salarié du secteur privé", "https://www.service-public.gouv.fr/particuliers/vosdroits/F13887")
SRC_L3122_8 = ("Code du travail, article L3122-8 (contreparties au travail de nuit)", "https://code.travail.gouv.fr/code-du-travail/l3122-8")
SRC_RTT = ("Service-Public.fr, réduction du temps de travail (RTT) dans le privé", "https://www.service-public.gouv.fr/particuliers/vosdroits/F34151")
SRC_FORFAIT = ("Service-Public.fr, forfait annuel en heures ou en jours", "https://www.service-public.gouv.fr/particuliers/vosdroits/F19261")
SRC_CP = ("Service-Public.fr, congés payés du salarié du secteur privé", "https://www.service-public.gouv.fr/particuliers/vosdroits/F2258")
SRC_ANC_1517 = ("Code du travail numérique, prime d'ancienneté des commerces de détail non alimentaires (IDCC 1517)", "https://code.travail.gouv.fr/contribution/1517-quand-le-salarie-a-t-il-droit-a-une-prime-danciennete-quel-est-son-montant")
SRC_ANC_1351 = ("Code du travail numérique, prime d'ancienneté de la prévention et sécurité (IDCC 1351)", "https://code.travail.gouv.fr/contribution/1351-quand-le-salarie-a-t-il-droit-a-une-prime-danciennete-quel-est-son-montant")
SRC_MINIMA = ("Code du travail numérique, SMIC et salaire minimum conventionnel", "https://code.travail.gouv.fr/contribution/quel-est-le-salaire-minimum")


def j(n, dec=1):
    """Nombre de jours avec une décimale : « 23,3 »."""
    return f"{n:.{dec}f}".replace(".", ",")


# ── Arrêt maladie ─────────────────────────────────────────────────────────────

def duree_maintien(anc):
    """Jours indemnisés à 90 % (puis autant à deux tiers) selon D1226-1 et D1226-2."""
    if anc < 1:
        return 0
    return min(90, 30 + 10 * math.floor((anc - 1) / 5))


def arret(brut, jours, anc):
    ij = round(min(brut, IJ_MALADIE_PLAFOND) * 3 / 91.25 * 0.5, 2)
    j_ij = max(0, jours - 3)
    p = duree_maintien(anc)
    d90 = min(max(jours - 7, 0), p)
    d66 = min(max(jours - 7 - p, 0), p)
    quotidien = brut / 30
    comp = d90 * max(0, 0.9 * quotidien - ij) + d66 * max(0, 2 / 3 * quotidien - ij)
    ij_brut = ij * j_ij
    return {"ij": ij, "j_ij": j_ij, "ij_brut": ij_brut, "ij_net": ij_brut * (1 - TAUX_CSG_CRDS_IJ),
            "comp": comp, "manque": quotidien * jours - ij_brut - comp, "p": p}


def page_arret():
    ex = arret(2500, 15, 3)
    ex30 = arret(2500, 30, 3)
    lignes_anc = []
    for lib, anc in (("1 à 5 ans", 1), ("6 à 10 ans", 6), ("11 à 15 ans", 11), ("16 à 20 ans", 16),
                     ("21 à 25 ans", 21), ("26 à 30 ans", 26), ("31 ans et plus", 31)):
        p = duree_maintien(anc)
        lignes_anc.append([lib, f"{p} jours", f"{p} jours", f"{2 * p} jours"])
    lignes_ij = []
    for b in (SMIC_MENSUEL_BRUT, 2000, 2500, 3000, 4000):
        a = arret(b, 30, 3)
        lignes_ij.append([e(b), e2(a["ij"]), e2(a["ij"] * (1 - TAUX_CSG_CRDS_IJ)), e(a["ij_net"]), e(a["comp"])])
    corps = f"""
<h2>Indemnités journalières selon le salaire</h2>
{table(["Salaire brut mensuel", "IJ brute par jour", "IJ nette par jour", "IJ nettes sur 30 jours d'arrêt", "Complément employeur (1 à 5 ans d'ancienneté)"], lignes_ij)}
{note("Arrêt maladie ordinaire de 30 jours débuté depuis le 1er juillet 2026, trois derniers salaires identiques. IJ dues à partir du 4e jour (27 jours), complément employeur à partir du 8e jour (23 jours) au taux de 90 %. L'IJ nette retire 6,2 % de CSG et 0,5 % de CRDS.")}
<h2>Le calcul de la Sécurité sociale</h2>
<p>L'Assurance maladie additionne les trois derniers salaires bruts avant l'arrêt et divise le total par 91,25 : c'est le salaire journalier de base. L'indemnité journalière en vaut la moitié. Depuis le 1er avril 2025, le salaire retenu est plafonné à <strong>1,4 Smic mensuel</strong> au lieu de 1,8 : avec le Smic de {e2(SMIC_MENSUEL_BRUT)} en vigueur depuis le 1er juin 2026, le plafond atteint {e2(IJ_MALADIE_PLAFOND)} par mois et l'indemnité ne dépasse pas <strong>{e2(IJ_MALADIE_MAX)} brut par jour</strong>. Un salarié payé {e(4000)} brut touche donc la même IJ qu'un salarié payé {e(2700)}.</p>
<p>Les trois premiers jours ne sont pas indemnisés (délai de carence). L'IJ est versée pour chaque jour calendaire, week-end compris, et supporte 6,2 % de CSG et 0,5 % de CRDS. Elle est imposable, sauf pour une affection de longue durée exonérante, et le prélèvement à la source s'y applique.</p>
<h2>Le maintien de salaire par l'employeur</h2>
<p>Le Code du travail oblige l'employeur à compléter les IJ dès que le salarié a <strong>un an d'ancienneté</strong>, a envoyé son arrêt sous 48 heures et est pris en charge par la Sécurité sociale. Le complément démarre au 8e jour d'arrêt, ou dès le premier jour pour un accident du travail ou une maladie professionnelle. Il porte la rémunération à 90 % du brut pendant une première période, puis aux deux tiers pendant une seconde, IJ déduites.</p>
{table(["Ancienneté", "Jours à 90 %", "Jours à 66,66 %", "Total sur 12 mois"], lignes_anc)}
{note("Article D1226-2 : chaque période s'allonge de 10 jours par tranche entière de 5 ans d'ancienneté au-delà de la première année, sans dépasser 90 jours. Les arrêts des douze mois précédents s'imputent sur ces durées (article D1226-4).")}
<p>Beaucoup de conventions collectives font mieux : maintien à 100 %, suppression des 7 jours d'attente, ancienneté réduite. Le minimum légal ci-dessus est un plancher ; vérifiez votre convention avant de conclure à une perte de salaire.</p>
<h2>Exemple : 15 jours d'arrêt</h2>
<p>Un salarié payé {e(2500)} brut, présent depuis trois ans, est arrêté 15 jours. Il perçoit {ex['j_ij']} IJ de {e2(ex['ij'])}, soit {e2(ex['ij_brut'])} brut et {e2(ex['ij_net'])} net de CSG-CRDS. Son employeur ajoute {e2(ex['comp'])} brut pour les jours 8 à 15. Par rapport à 15 jours de salaire normal, il lui manque environ <strong>{e(ex['manque'])} brut</strong>, essentiellement à cause des trois jours de carence et des jours 4 à 7, couverts par la seule IJ. Sur un arrêt de 30 jours, le manque est de {e(ex30['manque'])} brut.</p>
"""
    js = f"""
            var b = v('w-brut'), n = Math.max(0, Math.round(v('w-jours'))), anc = v('w-anc');
            var ij = Math.round(Math.min(b, {IJ_MALADIE_PLAFOND}) * 3 / 91.25 * 0.5 * 100) / 100;
            var jij = Math.max(0, n - 3);
            var p = anc < 1 ? 0 : Math.min(90, 30 + 10 * Math.floor((anc - 1) / 5));
            var d90 = Math.min(Math.max(n - 7, 0), p), d66 = Math.min(Math.max(n - 7 - p, 0), p);
            var q = b / 30;
            var comp = d90 * Math.max(0, 0.9 * q - ij) + d66 * Math.max(0, 2 / 3 * q - ij);
            out('r-ij', centimes(ij));
            out('r-ijnet', euros(ij * jij * {1 - TAUX_CSG_CRDS_IJ}));
            out('r-comp', euros(comp));
            out('r-manque', euros(q * n - ij * jij - comp));"""
    return {
        "slug": "arret-maladie-salaire",
        "title": "Arrêt maladie 2026 : IJ, maintien de salaire et carence",
        "desc": f"Arrêt maladie 2026 : IJ de 50 % du salaire plafonnées à {e2(IJ_MALADIE_MAX)} brut par jour, 3 jours de carence, maintien employeur à 90 % dès un an d'ancienneté. Simulateur.",
        "h1": "Salaire pendant un arrêt maladie en 2026",
        "crumb": "Arrêt maladie",
        "widget_titre": "Ce que vous touchez pendant l'arrêt",
        "widget": widget([champ("w-brut", "Salaire brut mensuel (€)", "2500"),
                          champ("w-jours", "Durée de l'arrêt (jours)", "15", "numeric"),
                          champ("w-anc", "Ancienneté (années)", "3")],
                         [("r-ij", "IJ brute par jour"), ("r-ijnet", "IJ nettes versées"),
                          ("r-comp", "Complément employeur brut"), ("r-manque", "Manque à gagner brut")],
                         "Arrêt maladie ordinaire débuté depuis le 1er juillet 2026, minimum légal sans convention plus favorable."),
        "js": js,
        "citable": f"En 2026, un salarié en arrêt maladie perçoit de la Sécurité sociale une indemnité journalière égale à 50 % de son salaire journalier de base, calculé sur ses trois derniers salaires bruts divisés par 91,25. Ce salaire est plafonné à 1,4 Smic, soit {e2(IJ_MALADIE_PLAFOND)} par mois pour un arrêt débuté depuis le 1er juillet 2026 : l'IJ ne dépasse donc pas {e2(IJ_MALADIE_MAX)} brut par jour, avant 6,7 % de CSG et de CRDS. Elle n'est versée qu'à partir du 4e jour. Avec un an d'ancienneté, l'employeur complète ensuite à partir du 8e jour jusqu'à 90 % du brut pendant 30 jours, puis aux deux tiers pendant 30 jours, durées allongées de 10 jours par tranche de cinq ans d'ancienneté supplémentaire. Pour {e(2500)} brut et 15 jours d'arrêt, le manque à gagner atteint environ {e(ex['manque'])} brut, sauf convention plus favorable.",
        "corps": corps,
        "sources": [SRC_IJ_SP, SRC_IJ_AMELI, SRC_L1226_1, SRC_D1226_1, SRC_D1226_2, SRC_SMIC],
        "releve": RELEVE,
        "note_sources": "Les montants supposent un arrêt maladie ordinaire et le seul minimum légal : une convention collective, un accord d'entreprise ou un contrat de prévoyance peuvent prévoir un maintien plus élevé ou sans délai d'attente.",
        "faq": [
            ("Combien touche-t-on par jour en arrêt maladie en 2026 ?",
             f"La Sécurité sociale verse 50 % du salaire journalier de base, soit environ la moitié du brut quotidien moyen des trois derniers mois. Pour {e(2500)} brut par mois, l'IJ vaut {e2(arret(2500, 30, 3)['ij'])} brut par jour, environ {e2(arret(2500, 30, 3)['ij'] * 0.933)} après CSG et CRDS. Le salaire retenu étant plafonné à 1,4 Smic, l'IJ ne dépasse pas {e2(IJ_MALADIE_MAX)} brut par jour pour un arrêt débuté depuis juillet 2026."),
            ("Quand commence le paiement des indemnités journalières ?",
             "Au 4e jour d'arrêt : les trois premiers jours forment le délai de carence et ne sont pas payés par l'Assurance maladie. Il n'y a pas de nouvelle carence pour une prolongation, pour une reprise de moins de 48 heures entre deux arrêts, ni pour des arrêts successifs liés à une même affection de longue durée. Un accident du travail ou une maladie professionnelle est indemnisé dès le lendemain de l'arrêt."),
            ("L'employeur doit-il maintenir mon salaire pendant un arrêt ?",
             "Oui, en partie, si vous avez au moins un an d'ancienneté, que vous avez transmis l'arrêt dans les 48 heures et que la Sécurité sociale vous indemnise. À partir du 8e jour, il complète les IJ pour atteindre 90 % de votre brut pendant 30 jours, puis deux tiers pendant 30 jours. Ces durées augmentent avec l'ancienneté, et votre convention collective peut prévoir mieux."),
            ("Pourquoi le plafond des IJ a-t-il baissé en 2025 ?",
             f"Pour les arrêts commencés depuis le 1er avril 2025, le salaire pris en compte est limité à 1,4 Smic mensuel au lieu de 1,8 Smic. Cette mesure de la loi de financement de la Sécurité sociale réduit l'IJ des salariés payés au-delà d'environ {e(IJ_MALADIE_PLAFOND)} brut par mois. Elle ne change rien pour les autres. Le maintien de salaire légal par l'employeur, calculé sur la rémunération brute, n'est pas plafonné."),
            ("Les indemnités journalières maladie sont-elles imposables ?",
             "Oui. Les IJ maladie entrent dans le revenu imposable et le prélèvement à la source s'y applique, au taux transmis par l'administration fiscale. Seules les indemnités versées au titre d'une affection de longue durée reconnue comme exonérante échappent à l'impôt. Avant versement, l'Assurance maladie retient 6,2 % de CSG et 0,5 % de CRDS, sans cotisations de retraite ni de chômage."),
            ("Que se passe-t-il après 60 jours d'arrêt ?",
             "Pour un salarié qui a entre un et cinq ans d'ancienneté, le maintien légal par l'employeur s'arrête après 30 jours à 90 % et 30 jours aux deux tiers, comptés à partir du 8e jour. Il ne reste alors que les IJ de la Sécurité sociale, versées jusqu'à 12 mois sur trois ans, et l'éventuel contrat de prévoyance de l'entreprise, qui prend souvent le relais à ce stade."),
        ],
        "related": ["conge-paternite", "salaire-net-imposable", "indemnite-conges-payes", "simulateur-fiche-de-paie", "plafond-securite-sociale-2026", "smic-brut-net-2026"],
    }


# ── Congé paternité ───────────────────────────────────────────────────────────

def ij_paternite(brut):
    return round(min(brut, PSS_MENSUEL) * 3 / 91.25 * 0.79, 2)


def page_paternite():
    lignes = []
    for b in (SMIC_MENSUEL_BRUT, 2000, 2500, 3000, PSS_MENSUEL, 5000):
        ij = ij_paternite(b)
        nij = ij * (1 - TAUX_CSG_CRDS_IJ)
        lignes.append([e(b), e2(ij), e2(nij), e(nij * 25), e(net(b) * 25 / 30 - nij * 25)])
    ex = ij_paternite(2500)
    ex_net25 = ex * 0.933 * 25
    corps = f"""
<h2>Indemnités du congé paternité selon le salaire</h2>
{table(["Salaire brut mensuel", "IJ par jour", "IJ nette par jour", "Total net pour 25 jours", "Écart avec le salaire net"], lignes)}
{note("Trois derniers salaires identiques, congé de 25 jours calendaires. L'IJ retire 21 % au salaire journalier plafonné, puis 6,7 % de CSG et de CRDS. L'écart compare au salaire net de 25 jours sur une base de 30 jours par mois, hors convention qui maintiendrait le salaire.")}
<h2>25 jours, dont 4 obligatoires</h2>
<p>Le congé de paternité et d'accueil de l'enfant dure <strong>25 jours calendaires</strong>, ou <strong>32 jours</strong> en cas de naissances multiples. Il suit le congé de naissance de 3 jours ouvrables, payé par l'employeur comme du temps de travail. Les 4 premiers jours du congé de paternité sont obligatoires et se prennent immédiatement après ce congé de naissance ; les 21 jours restants (28 pour des jumeaux) peuvent être pris en une fois ou en deux périodes d'au moins 5 jours, dans les 6 mois qui suivent la naissance. L'employeur doit être prévenu un mois à l'avance de chaque période facultative.</p>
<h2>Le calcul de l'Assurance maladie</h2>
<p>L'indemnité journalière est égale au gain journalier de base : les trois derniers salaires, retenus dans la limite du plafond de la Sécurité sociale ({e(PSS_MENSUEL)} par mois en 2026), sont divisés par 91,25, puis diminués d'un taux forfaitaire de 21 % qui représente les cotisations salariales. Le maximum atteint <strong>{e2(IJ_PATERNITE_MAX)} par jour</strong> en 2026. Il n'y a pas de délai de carence et l'indemnité est due chaque jour, week-end compris. Elle supporte 6,2 % de CSG et 0,5 % de CRDS et reste imposable.</p>
<p>Pour y avoir droit, il faut 6 mois d'affiliation et au moins 150 heures de travail sur les 3 mois précédents, ou des cotisations sur au moins 1 015 fois le Smic horaire sur 6 mois. Un salarié payé {e(2500)} brut touche {e2(ex)} par jour, soit environ {e(ex_net25)} net pour les 25 jours.</p>
<h2>Le congé supplémentaire de naissance, depuis juillet 2026</h2>
<p>Depuis le 1er juillet 2026, chaque parent peut ajouter un à deux mois de congé supplémentaire de naissance, après le congé de paternité, dans les 9 mois qui suivent la naissance. Service-public.gouv.fr indique une indemnisation des salariés égale à 70 % du salaire plafonné le premier mois et à 60 % le second, avec un plafond de {e(PSS_MENSUEL)} par mois. Les montants journaliers exacts sont publiés par l'Assurance maladie : ce simulateur ne les calcule pas.</p>
"""
    js = f"""
            var b = v('w-brut'), n = Math.max(0, Math.round(v('w-jours')));
            var ij = Math.round(Math.min(b, {PSS_MENSUEL}) * 3 / 91.25 * 0.79 * 100) / 100;
            var nij = ij * {1 - TAUX_CSG_CRDS_IJ};
            var salaire = calculerBrutVersNet(b, 'non-cadre', 1).netAvantImpot * n / 30;
            out('r-ij', centimes(ij));
            out('r-nij', centimes(nij));
            out('r-total', euros(nij * n));
            out('r-ecart', euros(salaire - nij * n));"""
    return {
        "slug": "conge-paternite",
        "title": f"Congé paternité 2026 : indemnités jusqu'à {e2(IJ_PATERNITE_MAX)} par jour",
        "desc": f"Congé paternité 2026 : 25 jours (32 pour des jumeaux), IJ égales au salaire plafonné au PSS moins 21 %, au plus {e2(IJ_PATERNITE_MAX)} par jour. Montant net selon le salaire.",
        "h1": "Congé paternité 2026 : durée et indemnisation",
        "crumb": "Congé paternité",
        "widget_titre": "Indemnités de votre congé paternité",
        "widget": widget([champ("w-brut", "Salaire brut mensuel des 3 derniers mois (€)", "2500"),
                          choix("w-jours", "Durée du congé", [("25", "25 jours (naissance simple)"), ("32", "32 jours (naissances multiples)"), ("4", "4 jours obligatoires seulement")], "25")],
                         [("r-ij", "IJ brute par jour"), ("r-nij", "IJ nette par jour"), ("r-total", "Total net du congé"), ("r-ecart", "Écart avec votre salaire net")]),
        "js": js,
        "citable": f"En 2026, le congé de paternité et d'accueil de l'enfant dure 25 jours calendaires, ou 32 jours en cas de naissances multiples, après un congé de naissance de 3 jours payé par l'employeur. Les 4 premiers jours sont obligatoires. Pendant le congé, l'Assurance maladie verse une indemnité journalière égale au salaire des trois derniers mois, retenu dans la limite du plafond de la Sécurité sociale de {e(PSS_MENSUEL)} par mois, divisé par 91,25 et diminué de 21 %. Le maximum est de {e2(IJ_PATERNITE_MAX)} par jour, sans délai de carence, avant 6,7 % de CSG et de CRDS. Un salarié payé {e(2500)} brut perçoit {e2(ex)} par jour, soit environ {e(ex_net25)} net pour 25 jours. Depuis le 1er juillet 2026, un congé supplémentaire de naissance d'un à deux mois peut suivre.",
        "corps": corps,
        "sources": [SRC_PAT_SP, SRC_PAT_AMELI, SRC_CSN, SRC_PSS],
        "releve": RELEVE,
        "note_sources": "Les montants sont ceux de l'Assurance maladie pour un salarié du régime général ; une convention collective peut prévoir le maintien du salaire pendant le congé.",
        "faq": [
            ("Combien de jours dure le congé paternité en 2026 ?",
             "Le congé de paternité et d'accueil de l'enfant dure 25 jours calendaires pour une naissance simple et 32 jours pour des naissances multiples. Il s'ajoute au congé de naissance de 3 jours ouvrables payé par l'employeur, soit 28 jours au total. Les 4 premiers jours suivent obligatoirement le congé de naissance ; le reste se prend dans les 6 mois, en une ou deux périodes d'au moins 5 jours."),
            ("Quel est le montant maximum des indemnités de paternité ?",
             f"En 2026, l'indemnité journalière ne peut pas dépasser {e2(IJ_PATERNITE_MAX)} par jour avant CSG et CRDS. Ce maximum correspond à un salaire égal ou supérieur au plafond mensuel de la Sécurité sociale, {e(PSS_MENSUEL)}, divisé par 30,42 puis diminué de 21 %. Sur 25 jours, cela représente environ {e(IJ_PATERNITE_MAX * 25)} brut, et près de {e(IJ_PATERNITE_MAX * 25 * 0.933)} après prélèvements sociaux."),
            ("Le salaire est-il maintenu pendant le congé paternité ?",
             "La loi n'oblige pas l'employeur à maintenir le salaire pendant le congé de paternité : seules les indemnités journalières de l'Assurance maladie sont dues, sans délai de carence. Certaines conventions collectives et accords d'entreprise prévoient toutefois un complément, souvent jusqu'au salaire net. Les 3 jours du congé de naissance, eux, sont toujours payés par l'employeur comme des jours travaillés."),
            ("Quelles conditions pour toucher les indemnités de paternité ?",
             "Il faut être affilié depuis au moins 6 mois à la date du congé et justifier de 150 heures de travail salarié sur les 3 mois civils précédents, ou de cotisations sur un salaire au moins égal à 1 015 fois le Smic horaire sur les 6 derniers mois. Le congé lui-même est ouvert à tout salarié, sans condition d'ancienneté ni de type de contrat."),
            ("Les indemnités de paternité sont-elles imposables ?",
             "Oui. Comme les indemnités de maternité, elles entrent dans le revenu imposable et supportent le prélèvement à la source au taux transmis par l'administration fiscale. Avant versement, l'Assurance maladie retire 6,2 % de CSG et 0,5 % de CRDS. Elles sont versées tous les 14 jours sur la base de l'attestation de salaire transmise par l'employeur pour chaque période de congé."),
            ("Peut-on cumuler congé paternité et congé supplémentaire de naissance ?",
             "Oui. Depuis le 1er juillet 2026, chaque parent peut prendre un à deux mois de congé supplémentaire de naissance après le congé de paternité, dans les 9 mois suivant la naissance. Pour les enfants nés au premier semestre 2026, il doit débuter avant le 1er avril 2027. Il est indemnisé à 70 % du salaire plafonné le premier mois et à 60 % le second."),
        ],
        "related": ["arret-maladie-salaire", "plafond-securite-sociale-2026", "indemnite-conges-payes", "salaire-net-imposable", "jours-feries-2026", "smic-brut-net-2026"],
    }


# ── Jours fériés 2026 ─────────────────────────────────────────────────────────

FERIES = [("01-01", "Jour de l'An"), ("04-06", "Lundi de Pâques"), ("05-01", "Fête du Travail"),
          ("05-08", "Victoire 1945"), ("05-14", "Ascension"), ("05-25", "Lundi de Pentecôte"),
          ("07-14", "Fête nationale"), ("08-15", "Assomption"), ("11-01", "Toussaint"),
          ("11-11", "Armistice 1918"), ("12-25", "Noël")]
FERIES_AM = [("04-03", "Vendredi saint"), ("12-26", "Saint-Étienne")]
JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def d26(md):
    return datetime.date(2026, int(md[:2]), int(md[3:]))


def compte_mois(mois, alsace=False):
    feries = {d26(md) for md, _ in FERIES + (FERIES_AM if alsace else [])}
    ouvres = ouvrables = fer_sem = 0
    d = datetime.date(2026, mois, 1)
    while d.month == mois:
        if d.weekday() < 6 and d not in feries:
            ouvrables += 1
            if d.weekday() < 5:
                ouvres += 1
        if d in feries and d.weekday() < 5:
            fer_sem += 1
        d += datetime.timedelta(days=1)
    return ouvres, ouvrables, fer_sem


def page_feries():
    lignes = [[lib, f"{JOURS_FR[d26(md).weekday()]} {d26(md).day} {MOIS_FR[d26(md).month - 1]}"] for md, lib in FERIES]
    lignes_am = [[lib, f"{JOURS_FR[d26(md).weekday()]} {d26(md).day} {MOIS_FR[d26(md).month - 1]}"] for md, lib in FERIES_AM]
    mois_l = []
    tot = [0, 0, 0]
    for m in range(1, 13):
        o, ob, f = compte_mois(m)
        oa = compte_mois(m, True)[0]
        tot = [tot[0] + o, tot[1] + ob, tot[2] + oa]
        mois_l.append([MOIS_FR[m - 1].capitalize(), str(f), str(o), str(ob), str(oa)])
    sem = sum(1 for md, _ in FERIES if d26(md).weekday() < 5)
    corps = f"""
<h2>Les 11 jours fériés 2026</h2>
{table(["Fête légale", "Date en 2026"], lignes)}
{note("Liste de l'article L3133-1 du Code du travail ; dates publiées par service-public.gouv.fr. En 2026, " + str(sem) + " jours fériés tombent du lundi au vendredi : l'Assomption tombe un samedi et la Toussaint un dimanche.")}
<h2>Alsace-Moselle : deux jours de plus</h2>
{table(["Jour férié local", "Date en 2026"], lignes_am)}
{note("Le Vendredi saint est férié dans les communes ayant un temple protestant ou une église mixte ; service-public.gouv.fr le cite pour les départements du Bas-Rhin, du Haut-Rhin et de la Moselle. L'outre-mer ajoute la commémoration de l'abolition de l'esclavage, à une date propre à chaque territoire.")}
<h2>Les ponts de 2026</h2>
<p>Trois jours fériés tombent un vendredi (1er mai, 8 mai, 25 décembre) et deux un lundi (Pâques, Pentecôte) : autant de week-ends de trois jours sans rien poser. Les vrais ponts sont au nombre de trois : le <strong>vendredi 2 janvier</strong> après le Jour de l'An, le <strong>vendredi 15 mai</strong> après l'Ascension et le <strong>lundi 13 juillet</strong> avant la Fête nationale. Le mercredi 11 novembre coupe la semaine en deux sans pont simple. Aucune règle n'impose de pont : l'employeur, une convention ou un accord le décide, et les heures non travaillées peuvent être récupérées dans les douze mois, sans majoration.</p>
<h2>Jours ouvrés et ouvrables par mois en 2026</h2>
{table(["Mois", "Fériés en semaine", "Jours ouvrés", "Jours ouvrables", "Ouvrés Alsace-Moselle"], mois_l, ["Total 2026", str(sem), str(tot[0]), str(tot[1]), str(tot[2])])}
{note("Jours ouvrés : du lundi au vendredi, hors jours fériés. Jours ouvrables : du lundi au samedi, hors jours fériés. Le calcul suppose que tous les jours fériés sont chômés dans l'entreprise.")}
<h2>Travailler un jour férié</h2>
<p>Seul le <strong>1er mai</strong> est obligatoirement chômé et payé. Le salarié qui y travaille, dans une activité qui ne peut pas s'interrompre, reçoit en plus de son salaire une indemnité égale à ce salaire : sa journée est payée double. Pour les dix autres jours, la loi ne prévoit aucune majoration : c'est la convention collective qui la fixe. Un jour férié chômé ne fait pas baisser le salaire d'un salarié ayant au moins trois mois d'ancienneté. La journée de solidarité, souvent placée le lundi de Pentecôte, est une journée de 7 heures non rémunérée.</p>
"""
    feries_js = "[" + ",".join(f"'{md}'" for md, _ in FERIES) + "]"
    am_js = "[" + ",".join(f"'{md}'" for md, _ in FERIES_AM) + "]"
    js = f"""
            var m = parseInt(document.getElementById('w-mois').value, 10);
            var zone = document.getElementById('w-zone').value;
            var f = {feries_js};
            if (zone === 'am') f = f.concat({am_js});
            var o = 0, ob = 0, fs = 0;
            var debut = m === 0 ? 1 : m, fin = m === 0 ? 12 : m;
            for (var mm = debut; mm <= fin; mm++) {{
                var d = new Date(Date.UTC(2026, mm - 1, 1));
                while (d.getUTCMonth() === mm - 1) {{
                    var md = ('0' + (mm)).slice(-2) + '-' + ('0' + d.getUTCDate()).slice(-2);
                    var wd = (d.getUTCDay() + 6) % 7;
                    var ferie = f.indexOf(md) >= 0;
                    if (wd < 6 && !ferie) {{ ob++; if (wd < 5) o++; }}
                    if (ferie && wd < 5) fs++;
                    d = new Date(d.getTime() + 86400000);
                }}
            }}
            out('r-ouvres', String(o));
            out('r-ouvrables', String(ob));
            out('r-feries', String(fs));"""
    mois_opts = [("0", "Toute l'année 2026")] + [(str(m), MOIS_FR[m - 1].capitalize() + " 2026") for m in range(1, 13)]
    mai = compte_mois(5)
    return {
        "slug": "jours-feries-2026",
        "title": "Jours fériés 2026 : les 11 dates, ponts et jours ouvrés",
        "desc": f"Jours fériés 2026 : les 11 dates, dont {sem} en semaine, les ponts du 2 janvier, 15 mai et 13 juillet, l'Alsace-Moselle et le nombre de jours ouvrés de chaque mois.",
        "h1": "Jours fériés 2026 et jours ouvrés",
        "crumb": "Jours fériés 2026",
        "widget_titre": "Jours ouvrés et ouvrables en 2026",
        "widget": widget([choix("w-mois", "Période", mois_opts, "0"),
                          choix("w-zone", "Zone", [("fr", "France (hors Alsace-Moselle)"), ("am", "Alsace-Moselle")], "fr")],
                         [("r-ouvres", "Jours ouvrés"), ("r-ouvrables", "Jours ouvrables"), ("r-feries", "Fériés en semaine")]),
        "js": js,
        "citable": f"La France compte 11 jours fériés en 2026 : le jeudi 1er janvier, le lundi de Pâques 6 avril, le vendredi 1er mai, le vendredi 8 mai, l'Ascension le jeudi 14 mai, le lundi de Pentecôte 25 mai, le mardi 14 juillet, le samedi 15 août, le dimanche 1er novembre, le mercredi 11 novembre et le vendredi 25 décembre. {sem} d'entre eux tombent en semaine, ce qui laisse {tot[0]} jours ouvrés dans l'année si tous sont chômés. L'Alsace-Moselle ajoute le Vendredi saint, le 3 avril, et la Saint-Étienne, le samedi 26 décembre. Les ponts possibles sont le vendredi 2 janvier, le vendredi 15 mai et le lundi 13 juillet. Mai est le mois le plus court au travail, avec {mai[0]} jours ouvrés. Seul le 1er mai est obligatoirement chômé et payé double s'il est travaillé.",
        "corps": corps,
        "sources": [SRC_FERIES, SRC_L3133_1, SRC_L3133_6, SRC_RTT],
        "releve": RELEVE,
        "note_sources": "Les jours ouvrés supposent tous les jours fériés chômés ; votre convention collective ou l'usage de l'entreprise peuvent prévoir des jours travaillés.",
        "faq": [
            ("Combien y a-t-il de jours fériés en 2026 ?",
             f"Le Code du travail en fixe 11, dont {sem} tombent un jour de semaine en 2026 : l'Assomption est un samedi et la Toussaint un dimanche, ce qui ne donne pas de jour de repos en plus, sauf convention plus favorable. L'Alsace-Moselle en compte 13, avec le Vendredi saint et le 26 décembre, ce dernier tombant un samedi cette année. L'outre-mer ajoute la commémoration de l'abolition de l'esclavage."),
            ("Quels sont les ponts possibles en 2026 ?",
             "Trois ponts d'une journée existent en 2026 : le vendredi 2 janvier, le vendredi 15 mai après l'Ascension et le lundi 13 juillet avant la Fête nationale. Le 1er mai, le 8 mai et Noël tombant un vendredi, ils offrent des week-ends de trois jours sans pont. L'employeur reste libre d'accorder ou non un pont, et peut faire récupérer les heures dans les douze mois."),
            ("Combien de jours ouvrés compte l'année 2026 ?",
             f"L'année 2026 compte {tot[0]} jours ouvrés, du lundi au vendredi hors jours fériés, et {tot[1]} jours ouvrables, samedis compris. En Alsace-Moselle, le Vendredi saint retire un jour ouvré de plus, soit {tot[2]}. Après 25 jours de congés payés, il reste {tot[0] - 25} jours de travail pour un salarié à temps plein, ce qui sert de base au calcul des jours de RTT et du forfait jours."),
            ("Un jour férié travaillé est-il payé double ?",
             "Seulement le 1er mai. Le salarié qui travaille ce jour-là, dans une entreprise qui ne peut pas interrompre son activité, reçoit en plus de son salaire une indemnité égale à ce salaire. Pour les autres jours fériés, le Code du travail ne prévoit aucune majoration : votre convention collective ou votre contrat peuvent en accorder une, ou prévoir un repos compensateur."),
            ("Un jour férié qui tombe un samedi donne-t-il droit à un congé ?",
             "Non, en principe. Un jour férié qui tombe un jour habituellement non travaillé, comme le samedi 15 août ou le dimanche 1er novembre 2026, n'ouvre pas droit à un jour de repos supplémentaire ni à une indemnité. Une convention collective ou un accord d'entreprise peut toutefois prévoir de compenser ces jours, ce qui est fréquent dans certaines branches."),
            ("Quand placer la journée de solidarité en 2026 ?",
             "L'employeur la fixe après accord collectif ou, à défaut, après consultation du comité social et économique. Elle peut prendre la forme du travail d'un jour férié autre que le 1er mai, souvent le lundi de Pentecôte, le 25 mai 2026, d'un jour de RTT ou de 7 heures réparties autrement. Ces heures ne sont pas payées pour un salarié mensualisé."),
        ],
        "related": ["jours-rtt", "majoration-nuit-dimanche", "indemnite-conges-payes", "salaire-brut-net-journalier", "salaire-brut-net-alsace-moselle", "heures-supplementaires-brut-net"],
    }


# ── Majoration nuit et dimanche ───────────────────────────────────────────────

def majorations(brut, hn, mn, hd, md):
    th = brut / HEURES_MENSUELLES
    maj = th * (hn * mn + hd * md) / 100
    return maj, net(brut + maj) - net(brut)


def page_nuit():
    b = 2000
    th = b / HEURES_MENSUELLES
    lignes = []
    for lib, hn, mn, hd, md in (("20 h de nuit majorées à 10 %", 20, 10, 0, 0),
                                ("20 h de nuit majorées à 25 %", 20, 25, 0, 0),
                                ("40 h de nuit majorées à 25 %", 40, 25, 0, 0),
                                ("2 dimanches de 7 h majorés à 30 %", 0, 0, 14, 30),
                                ("2 dimanches de 7 h majorés à 50 %", 0, 0, 14, 50),
                                ("1 dimanche du maire de 7 h (100 %)", 0, 0, 7, 100)):
        maj, gn = majorations(b, hn, mn, hd, md)
        lignes.append([lib, e2(maj), e2(gn)])
    ex_maj, ex_net = majorations(2000, 20, 25, 7, 100)
    corps = f"""
<h2>Ce que rapportent les majorations</h2>
{table(["Situation (salaire de " + e(b) + " brut)", "Majoration brute", "Gain net"], lignes)}
{note("Taux horaire de " + e2(th) + " (" + e(b) + " ÷ 151,67 h), heures comprises dans l'horaire habituel : seule la majoration s'ajoute au salaire. Elle supporte les cotisations ordinaires, sans la réduction applicable aux heures supplémentaires. Les taux de 10 %, 25 %, 30 % et 50 % sont des exemples de conventions ; le 100 % est le minimum légal d'un dimanche du maire.")}
<h2>Le travail de nuit : un repos obligatoire, une majoration conventionnelle</h2>
<p>Est du travail de nuit tout travail accompli pendant une période d'au moins 9 heures consécutives comprenant l'intervalle de minuit à 5 heures, commençant au plus tôt à 21 heures et finissant au plus tard à 6 heures. Est <strong>travailleur de nuit</strong> le salarié qui y effectue au moins 3 heures deux fois par semaine, ou 270 heures sur douze mois.</p>
<p>Le Code du travail (article L3122-8) lui accorde obligatoirement un <strong>repos compensateur</strong>, et seulement « le cas échéant » une compensation salariale : <strong>aucun taux de majoration n'est fixé par la loi</strong>. C'est l'accord collectif qui le prévoit, souvent entre 10 % et 30 % du taux horaire selon les branches, parfois davantage pour des heures isolées. La durée quotidienne de nuit est limitée à 8 heures et la moyenne hebdomadaire à 40 heures sur douze semaines, sauf accord.</p>
<h2>Le travail du dimanche : tout dépend de la dérogation</h2>
<ul>
<li><strong>Dimanches du maire</strong> (12 par an au plus dans les commerces de détail) : salaire au moins doublé et repos compensateur équivalent.</li>
<li><strong>Grandes surfaces alimentaires de plus de 400 m² ouvertes après 13 heures</strong> en zone touristique, commerciale ou en gare : majoration d'au moins 30 %.</li>
<li><strong>Zones touristiques et commerciales</strong> : contreparties fixées par l'accord qui autorise l'ouverture.</li>
<li><strong>Dérogations permanentes</strong> (hôtels, cafés, restaurants, commerces alimentaires le matin, hôpitaux) et dérogation préfectorale : aucune majoration légale ; la convention collective décide.</li>
</ul>
<p>Le dimanche qui est aussi le 1er mai est payé double, comme tout 1er mai travaillé. Une heure de nuit un dimanche cumule en principe les deux majorations, sauf si la convention prévoit qu'elles ne se cumulent pas.</p>
<h2>Exemple chiffré</h2>
<p>Un salarié à {e(2000)} brut effectue dans le mois 20 heures de nuit majorées à 25 % et travaille un dimanche du maire de 7 heures. Ses majorations s'élèvent à {e2(ex_maj)} brut, soit environ <strong>{e2(ex_net)} net</strong> de plus sur sa fiche de paie.</p>
"""
    js = """
            var b = v('w-brut'), hn = v('w-hn'), mn = v('w-mn'), hd = v('w-hd'), md = v('w-md');
            var th = b / 151.67;
            var maj = th * (hn * mn + hd * md) / 100;
            var n0 = calculerBrutVersNet(b, 'non-cadre', 1).netAvantImpot;
            var n1 = calculerBrutVersNet(b + maj, 'non-cadre', 1).netAvantImpot;
            out('r-th', centimes(th));
            out('r-maj', centimes(maj));
            out('r-gain', centimes(n1 - n0));
            out('r-net', euros(n1));"""
    return {
        "slug": "majoration-nuit-dimanche",
        "title": "Majoration nuit et dimanche 2026 : règles légales et calcul",
        "desc": "Majoration des heures de nuit et du travail le dimanche en 2026 : ce que la loi impose (repos, dimanche du maire payé double), ce que fixe la convention.",
        "h1": "Majoration des heures de nuit et du dimanche",
        "crumb": "Nuit et dimanche",
        "widget_titre": "Vos majorations du mois",
        "widget": widget([champ("w-brut", "Salaire brut mensuel (€)", "2000"),
                          champ("w-hn", "Heures de nuit dans le mois", "20"),
                          champ("w-mn", "Majoration de nuit (%)", "25"),
                          champ("w-hd", "Heures travaillées le dimanche", "7"),
                          champ("w-md", "Majoration du dimanche (%)", "100")],
                         [("r-th", "Taux horaire brut"), ("r-maj", "Majorations brutes"), ("r-gain", "Gain net"), ("r-net", "Net du mois")],
                         "Saisissez les taux de votre convention collective. 100 % est le minimum légal d'un dimanche du maire."),
        "js": js,
        "citable": f"En 2026, aucune loi ne fixe de taux de majoration pour les heures de nuit dans le secteur privé : le Code du travail impose au travailleur de nuit un repos compensateur et laisse à l'accord collectif le soin de prévoir, le cas échéant, une compensation salariale, souvent de 10 % à 30 % du taux horaire. Le travail du dimanche suit la même logique, avec deux exceptions légales : les dimanches du maire, payés au moins le double avec un repos équivalent, et les grandes surfaces alimentaires ouvertes après 13 heures en zone touristique ou commerciale, majorées d'au moins 30 %. Le 1er mai travaillé est payé double. Pour un salarié à {e(2000)} brut, 20 heures de nuit à 25 % et un dimanche du maire de 7 heures ajoutent {e2(ex_maj)} brut, soit environ {e2(ex_net)} net.",
        "corps": corps,
        "sources": [SRC_NUIT, SRC_L3122_8, SRC_DIMANCHE, SRC_L3133_6, SRC_TAUX],
        "releve": RELEVE,
        "note_sources": "Les taux de majoration de nuit et la plupart des majorations du dimanche viennent de la convention collective : saisissez ceux qui s'appliquent à votre entreprise.",
        "faq": [
            ("Quelle est la majoration légale des heures de nuit ?",
             "Il n'y en a pas. L'article L3122-8 du Code du travail impose un repos compensateur au travailleur de nuit et ne prévoit une compensation salariale que « le cas échéant ». Le taux de majoration est donc fixé par la convention collective ou l'accord d'entreprise, le plus souvent entre 10 % et 30 % du taux horaire. Sans texte applicable, l'employeur doit au minimum accorder le repos compensateur."),
            ("À partir de quelle heure est-on payé en heures de nuit ?",
             "La période de nuit dure au moins 9 heures consécutives, comprend obligatoirement l'intervalle de minuit à 5 heures, commence au plus tôt à 21 heures et se termine au plus tard à 6 heures. Sans accord collectif, c'est la plage de 21 heures à 6 heures. La majoration éventuelle et ses horaires précis dépendent de la convention collective, qui peut retenir une plage plus courte."),
            ("Le travail du dimanche est-il payé double ?",
             "Seulement dans certains cas. Les dimanches du maire, accordés au plus 12 fois par an aux commerces de détail, sont payés au moins le double avec un repos équivalent. Les grandes surfaces alimentaires ouvertes après 13 heures en zone touristique ou commerciale majorent d'au moins 30 %. Dans les hôtels, cafés, restaurants ou hôpitaux, aucune majoration légale n'existe : seule la convention collective en prévoit."),
            ("Les majorations de nuit sont-elles soumises aux cotisations ?",
             "Oui. Les majorations de nuit et du dimanche sont du salaire : elles supportent toutes les cotisations salariales et patronales, la CSG et la CRDS, et entrent dans le revenu imposable. Elles ne bénéficient pas de la réduction de cotisations ni de l'exonération d'impôt des heures supplémentaires, sauf pour les heures de nuit qui sont aussi des heures supplémentaires, sur la seule part supplémentaire."),
            ("Peut-on refuser de travailler la nuit ou le dimanche ?",
             "Un travailleur de jour ne peut pas être affecté à un poste de nuit sans son accord : c'est une modification de son contrat. Le salarié de nuit peut demander un poste de jour pour des obligations familiales impérieuses. Pour le dimanche, le refus est libre et ne peut être sanctionné dans le cadre des dimanches du maire, des zones touristiques ou commerciales et des dérogations préfectorales."),
            ("Les majorations de nuit et du dimanche se cumulent-elles ?",
             "Le Code du travail ne l'interdit pas, et la règle générale veut que des majorations ayant des causes différentes se cumulent : une heure travaillée à 2 heures du matin un dimanche peut porter les deux. Beaucoup de conventions collectives précisent toutefois qu'elles ne se cumulent pas, ou que seule la plus favorable s'applique. Vérifiez la clause correspondante de votre convention."),
        ],
        "related": ["heures-supplementaires-brut-net", "jours-feries-2026", "salaire-brut-net-horaire", "jours-rtt", "simulateur-fiche-de-paie", "prime-anciennete"],
    }


# ── RTT ───────────────────────────────────────────────────────────────────────

def jours_nets_2026(cp=25, alsace=False):
    """Jours ouvrés 2026 moins les congés payés (jours fériés de semaine supposés chômés)."""
    ouvres = sum(compte_mois(m, alsace)[0] for m in range(1, 13))
    return ouvres - cp


def rtt(h, cp=25):
    base = jours_nets_2026(cp)
    moyenne = base * (h - 35) / h if h > 35 else 0
    r1607 = max(0, base - 1607 / (h / 5)) if h > 0 else 0
    return base, moyenne, r1607


def page_rtt():
    base = jours_nets_2026()
    lignes = []
    for h in (36, 37, 37.5, 38, 39):
        _, m, r = rtt(h)
        lignes.append([f"{fmt2(h).replace(',00', '')} h", f"{h - 35:g} h".replace(".", ","), j(m), j(r)])
    _, m39, r39 = rtt(39)
    ouvres = base + 25
    corps = f"""
<h2>RTT 2026 selon la durée hebdomadaire</h2>
{table(["Horaire", "Heures au-delà de 35 h", "RTT (35 h en moyenne)", "RTT (référence 1 607 h)"], lignes)}
{note(f"Année 2026 : {ouvres} jours ouvrés, moins 25 jours de congés payés, soit {base} jours de travail possibles. Les 9 jours fériés tombant en semaine sont supposés chômés. L'accord d'entreprise fixe le nombre réel, souvent arrondi.")}
<h2>D'où viennent les jours de RTT</h2>
<p>Les RTT compensent un horaire supérieur à 35 heures sans le payer en heures supplémentaires. Service-public.gouv.fr donne l'exemple d'un salarié à 39 heures : il acquiert 4 heures de RTT par semaine, soit une demi-journée. Le Code du travail ne fixe pas de nombre de jours : c'est l'accord collectif, signé avant le 22 août 2008 pour les accords de RTT proprement dits, ou un accord d'aménagement du temps de travail qui le détermine. Deux méthodes de calcul coexistent.</p>
<ul>
<li><strong>Revenir à 35 heures en moyenne</strong> : le salarié travaille ses jours à H heures, et les RTT ramènent la moyenne à 35 heures. Nombre de RTT = jours de travail possibles × (H − 35) ÷ H, soit {j(m39)} jours à 39 heures en 2026.</li>
<li><strong>Atteindre 1 607 heures par an</strong>, durée légale annuelle journée de solidarité comprise : on divise 1 607 par la durée d'une journée (H ÷ 5) et on retire le résultat des jours possibles. À 39 heures, cela donne {j(r39)} jours. C'est la méthode la plus fréquente dans les accords récents.</li>
</ul>
<h2>Le forfait jours</h2>
<p>Un cadre au forfait annuel travaille au plus <strong>218 jours</strong> par an. Ses jours de repos se déduisent du calendrier : {ouvres} jours ouvrés en 2026, moins 25 jours de congés payés, moins 218 jours, soit <strong>{base - 218} jours de repos</strong> cette année. Le chiffre varie chaque année avec le nombre de jours fériés tombant en semaine. S'il renonce à des jours de repos par avenant écrit, il peut travailler jusqu'à 235 jours, et chaque jour racheté est majoré d'au moins 10 %.</p>
<h2>Rachat des RTT non pris</h2>
<p>Pour les jours acquis entre le 1er janvier 2022 et le 31 décembre 2026, le salarié peut demander à son employeur de lui racheter ses RTT non pris. Le rachat est majoré au moins comme la première heure supplémentaire dans l'entreprise, exonéré d'impôt dans la limite de 7 500 € par an et allégé de cotisations salariales, comme les <a href="/heures-supplementaires-brut-net/">heures supplémentaires</a>.</p>
"""
    js = f"""
            var h = v('w-h'), cp = v('w-cp'), reg = document.getElementById('w-reg').value, fj = v('w-fj');
            var base = {base + 25} - cp;
            if (reg === 'forfait') {{
                out('r-base', String(base));
                out('r-moy', Math.max(0, base - fj).toLocaleString('fr-FR', {{maximumFractionDigits: 1}}) + ' j');
                out('r-1607', '–');
                return;
            }}
            var moy = h > 35 ? base * (h - 35) / h : 0;
            var r = h > 0 ? Math.max(0, base - 1607 / (h / 5)) : 0;
            out('r-base', String(base));
            out('r-moy', moy.toLocaleString('fr-FR', {{minimumFractionDigits: 1, maximumFractionDigits: 1}}) + ' j');
            out('r-1607', r.toLocaleString('fr-FR', {{minimumFractionDigits: 1, maximumFractionDigits: 1}}) + ' j');"""
    return {
        "slug": "jours-rtt",
        "title": f"RTT 2026 : nombre de jours par an à 39 h, 37 h ou au forfait",
        "desc": f"RTT 2026 : nombre de jours selon l'horaire, de {j(rtt(36)[1])} jours à 36 h à {j(m39)} jours à 39 h, {base - 218} jours de repos au forfait 218 jours, selon deux méthodes de calcul.",
        "h1": "Combien de jours de RTT en 2026 ?",
        "crumb": "RTT",
        "widget_titre": "Vos jours de RTT en 2026",
        "widget": widget([choix("w-reg", "Régime", [("heures", "Horaire hebdomadaire"), ("forfait", "Forfait annuel en jours")], "heures"),
                          champ("w-h", "Heures par semaine", "39"),
                          champ("w-cp", "Jours de congés payés (ouvrés)", "25", "numeric"),
                          champ("w-fj", "Jours du forfait", "218", "numeric")],
                         [("r-base", "Jours de travail possibles"), ("r-moy", "RTT (35 h en moyenne) ou repos du forfait"), ("r-1607", "RTT (référence 1 607 h)")]),
        "js": js,
        "citable": f"En 2026, un salarié à 39 heures par semaine obtient entre {j(r39)} et {j(m39)} jours de RTT selon la méthode retenue par son accord d'entreprise. L'année compte {ouvres} jours ouvrés, car 9 jours fériés tombent du lundi au vendredi ; après 25 jours de congés payés, il reste {base} jours de travail possibles. Si l'accord ramène l'horaire à 35 heures en moyenne, les RTT valent {base} × 4 ÷ 39, soit {j(m39)} jours. S'il vise la durée annuelle de 1 607 heures, on retire 1 607 ÷ 7,8 heures, soit 206 jours, et il reste {j(r39)} jours. Un cadre au forfait de 218 jours dispose de {base - 218} jours de repos en 2026. Le Code du travail ne fixe aucun nombre : c'est toujours l'accord collectif qui le détermine.",
        "corps": corps,
        "sources": [SRC_RTT, SRC_FORFAIT, SRC_FERIES, SRC_CP],
        "releve": RELEVE,
        "note_sources": "Le nombre réel de RTT est fixé par l'accord collectif de l'entreprise ou de la branche : ces calculs en donnent l'ordre de grandeur pour 2026.",
        "faq": [
            ("Combien de RTT pour 39 heures par semaine en 2026 ?",
             f"Entre {j(r39)} et {j(m39)} jours selon la méthode de l'accord. En 2026, il reste {base} jours de travail après 25 jours de congés payés et 9 jours fériés en semaine. Ramener 39 heures à 35 heures en moyenne donne {j(m39)} jours ; viser la durée annuelle de 1 607 heures en donne {j(r39)}. Beaucoup d'entreprises retiennent 22 ou 23 jours, arrondis par l'accord."),
            ("Combien de jours de repos pour un forfait de 218 jours en 2026 ?",
             f"{base - 218} jours. L'année 2026 compte {ouvres} jours ouvrés, une fois retirés les week-ends et les 9 jours fériés qui tombent en semaine. Après 25 jours de congés payés, il reste {base} jours, dont 218 sont travaillés. Le nombre de jours de repos change chaque année avec le calendrier : il dépend des jours fériés qui tombent un samedi ou un dimanche."),
            ("A-t-on droit à des RTT à 35 heures ?",
             "Non. Un salarié qui travaille 35 heures par semaine est déjà à la durée légale : il n'acquiert aucune heure de réduction du temps de travail. Les RTT n'existent que si l'horaire collectif dépasse 35 heures et qu'un accord prévoit de compenser ce dépassement par des jours de repos plutôt que par des heures supplémentaires payées et majorées."),
            ("Les jours de RTT non pris sont-ils perdus ?",
             "En principe, les RTT se prennent dans l'année, selon les délais fixés par l'accord : ceux qui ne sont pas posés à temps peuvent être perdus, sauf report prévu par l'accord ou versement sur un compte épargne-temps. Pour les jours acquis jusqu'au 31 décembre 2026, le salarié peut aussi en demander le rachat, majoré et exonéré d'impôt jusqu'à 7 500 € par an."),
            ("Un arrêt maladie réduit-il le nombre de RTT ?",
             "Cela dépend de l'accord. Lorsque les RTT s'acquièrent semaine après semaine par les heures effectuées au-delà de 35 heures, une absence pour maladie, qui n'est pas du travail effectif, peut réduire proportionnellement les jours acquis. La Cour de cassation l'admet si l'accord le prévoit. Les absences assimilées à du travail effectif par l'accord n'ont pas cet effet."),
            ("Les RTT sont-ils payés comme des jours travaillés ?",
             "Oui. Un jour de RTT pris ne fait pas baisser le salaire mensuel : la rémunération est lissée sur l'année et correspond déjà à l'horaire moyen de 35 heures, ou au forfait convenu. Les heures effectuées au-delà de 35 heures sont compensées par le repos, pas payées en heures supplémentaires. Seul un rachat de RTT non pris donne lieu à un paiement en plus."),
        ],
        "related": ["jours-feries-2026", "heures-supplementaires-brut-net", "salaire-brut-net-cadre", "indemnite-conges-payes", "majoration-nuit-dimanche", "salaire-brut-net-journalier"],
    }


# ── Prime d'ancienneté ────────────────────────────────────────────────────────

def taux_anc(grille, anc):
    if grille == "1517":
        return min(15, 3 * math.floor(anc / 3)) if anc >= 3 else 0
    if grille == "1351":
        for seuil, t in ((15, 12), (12, 10), (10, 8), (7, 5), (4, 2)):
            if anc > seuil:
                return t
        return 0
    return min(15, math.floor(anc))  # exemple : 1 % par année complète, plafonné à 15 %


def page_anciennete():
    lignes = []
    for anc in (3, 5, 6, 9, 12, 15, 20):
        t17 = taux_anc("1517", anc)
        t13 = taux_anc("1351", anc)
        lignes.append([f"{anc} ans", pct(t17, 0), e2(BASE_1517 * t17 / 100), pct(t13, 0)])
    sal = 2000
    prime = BASE_1517 * 9 / 100
    gain = net(sal + prime) - net(sal)
    js = """
            var g = document.getElementById('w-grille').value, anc = v('w-anc'), base = v('w-base'), sal = v('w-sal');
            var t = 0;
            if (g === '1517') { t = anc >= 3 ? Math.min(15, 3 * Math.floor(anc / 3)) : 0; }
            else if (g === '1351') { t = anc > 15 ? 12 : anc > 12 ? 10 : anc > 10 ? 8 : anc > 7 ? 5 : anc > 4 ? 2 : 0; }
            else { t = Math.min(15, Math.floor(anc)); }
            var prime = base * t / 100;
            var n0 = calculerBrutVersNet(sal, 'non-cadre', 1).netAvantImpot;
            var n1 = calculerBrutVersNet(sal + prime, 'non-cadre', 1).netAvantImpot;
            out('r-taux', t + ' %');
            out('r-prime', centimes(prime));
            out('r-gain', centimes(n1 - n0));
            out('r-net', euros(n1));"""
    corps = f"""
<h2>Deux grilles conventionnelles vérifiées</h2>
{table(["Ancienneté", "Commerces non alimentaires (IDCC 1517)", "Montant sur " + e(BASE_1517), "Prévention et sécurité (IDCC 1351)"], lignes)}
{note("IDCC 1517 : 3 % après 3 ans, 6 % après 6 ans, 9 % après 9 ans, 12 % après 12 ans, 15 % après 15 ans, calculés sur le minimum conventionnel du niveau I (1 679 € selon la fiche du Code du travail numérique mise à jour le 15 février 2024). IDCC 1351 : 2 % au-delà de 4 ans, 5 % au-delà de 7 ans, 8 % au-delà de 10 ans, 10 % au-delà de 12 ans, 12 % au-delà de 15 ans, sur le minimum conventionnel de la qualification, cadres exclus.")}
<h2>Une prime prévue par la convention, pas par la loi</h2>
<p>Le Code du travail ne prévoit aucune prime d'ancienneté. Elle existe lorsqu'une convention collective de branche, un accord d'entreprise, un usage, un engagement de l'employeur ou le contrat de travail la prévoit. Les règles varient donc d'un secteur à l'autre : le point de départ (souvent 3 ans), la progression (par paliers ou d'un point par an), le plafond (souvent autour de 15 %) et surtout l'assiette.</p>
<h2>Sur quelle base se calcule-t-elle ?</h2>
<p>La plupart des conventions appliquent le taux au <strong>salaire minimum conventionnel</strong> du coefficient ou du niveau, et non au salaire réel : deux salariés de même ancienneté et de même niveau touchent alors la même prime, quel que soit leur salaire. C'est le cas des deux conventions ci-dessus. D'autres appliquent le taux au salaire de base réel, ou à une valeur de point fixée par accord territorial, comme la convention de la métallurgie, qui réserve la prime aux salariés des groupes d'emplois A à E. Les minima conventionnels étant revalorisés par avenant, vérifiez la base en vigueur dans votre branche : le simulateur vous laisse la saisir.</p>
<h2>Ce que devient la prime sur la fiche de paie</h2>
<p>La prime d'ancienneté figure sur une ligne distincte du bulletin et s'ajoute au salaire. Elle supporte les cotisations et la CSG-CRDS comme le reste du salaire et entre dans le revenu imposable. À temps partiel, elle est en général proratisée. Exemple : un vendeur payé {e(sal)} brut avec 9 ans d'ancienneté dans un commerce non alimentaire touche 9 % de {e(BASE_1517)}, soit {e2(prime)} brut, ce qui lui rapporte environ <strong>{e2(gain)} net</strong> de plus chaque mois.</p>
"""
    return {
        "slug": "prime-anciennete",
        "title": "Prime d'ancienneté 2026 : calcul, taux par convention et net",
        "desc": "Prime d'ancienneté 2026 : non prévue par la loi, elle dépend de la convention collective. Taux de 3 % à 15 % selon les années, base de calcul et montant net.",
        "h1": "Prime d'ancienneté : calcul et montant net",
        "crumb": "Prime d'ancienneté",
        "widget_titre": "Votre prime d'ancienneté",
        "widget": widget([choix("w-grille", "Grille", [("1517", "Commerces de détail non alimentaires (IDCC 1517)"), ("1351", "Prévention et sécurité (IDCC 1351)"), ("libre", "Exemple : 1 % par an, plafond 15 %")], "1517"),
                          champ("w-anc", "Ancienneté (années)", "9"),
                          champ("w-base", "Base de calcul (minimum conventionnel, €)", str(BASE_1517)),
                          champ("w-sal", "Salaire brut mensuel (€)", str(sal))],
                         [("r-taux", "Taux"), ("r-prime", "Prime brute"), ("r-gain", "Prime nette"), ("r-net", "Salaire net avec prime")],
                         "La base de calcul est le salaire minimum conventionnel de votre niveau dans la plupart des conventions : vérifiez la valeur à jour."),
        "js": js,
        "citable": f"La prime d'ancienneté n'est pas prévue par le Code du travail : elle n'est due que si une convention collective, un accord d'entreprise, un usage ou le contrat de travail la prévoit. Son calcul suit alors une grille propre à chaque branche, appliquée le plus souvent au salaire minimum conventionnel et non au salaire réel. Dans les commerces de détail non alimentaires (IDCC 1517), elle vaut 3 % après 3 ans, puis 3 points de plus tous les 3 ans jusqu'à 15 % après 15 ans, sur le minimum du niveau I de {e(BASE_1517)}. Dans la prévention et la sécurité (IDCC 1351), elle va de 2 % au-delà de 4 ans à 12 % au-delà de 15 ans. Soumise aux cotisations, une prime de {e2(prime)} brut rapporte environ {e2(gain)} net.",
        "corps": corps,
        "sources": [SRC_ANC_1517, SRC_ANC_1351, SRC_MINIMA, SRC_TAUX],
        "releve": RELEVE,
        "note_sources": "Les grilles citées sont celles publiées par le Code du travail numérique ; un accord d'entreprise ou votre contrat peuvent prévoir mieux. Le net est estimé avec les cotisations 2026 d'un non-cadre, hors mutuelle.",
        "faq": [
            ("La prime d'ancienneté est-elle obligatoire ?",
             "Non, pas au titre de la loi. Le Code du travail n'en prévoit aucune. Elle devient obligatoire lorsqu'elle est prévue par la convention collective applicable, un accord d'entreprise, un usage constant, un engagement unilatéral de l'employeur ou le contrat de travail. Dans ce cas, l'employeur doit la verser selon les règles du texte, et la faire figurer sur une ligne distincte du bulletin de paie."),
            ("À partir de combien d'années touche-t-on une prime d'ancienneté ?",
             "Le plus souvent après 3 ans de présence dans l'entreprise, mais chaque convention fixe son seuil. Dans les commerces de détail non alimentaires, la prime démarre à 3 ans avec 3 %. Dans la prévention et la sécurité, elle commence au-delà de 4 ans avec 2 %. Certaines conventions démarrent dès un an, d'autres n'en prévoient aucune, comme la convention Syntec des bureaux d'études."),
            ("La prime d'ancienneté est-elle calculée sur le salaire réel ?",
             "Rarement. La plupart des conventions appliquent le taux au salaire minimum conventionnel du niveau ou du coefficient, pas au salaire effectivement versé. Deux salariés de même niveau et de même ancienneté touchent alors la même prime. D'autres textes retiennent le salaire de base réel ou une valeur de point. C'est la convention, ou l'accord d'entreprise, qui précise l'assiette exacte."),
            ("La prime d'ancienneté est-elle soumise aux cotisations et à l'impôt ?",
             "Oui. C'est un élément de salaire comme un autre : elle supporte les cotisations salariales et patronales, la CSG et la CRDS, et entre dans le salaire net imposable. Avec les taux 2026, un non-cadre conserve environ 78 % de la prime en net avant impôt. Elle compte aussi dans le salaire de référence des indemnités de licenciement et de congés payés."),
            ("Comment l'ancienneté est-elle décomptée pour la prime ?",
             "On compte en principe le temps de présence continue dans l'entreprise depuis l'embauche. La loi assimile certaines absences à du temps de présence, comme le congé de maternité ou l'arrêt pour accident du travail. Les conventions précisent le reste : dans les commerces non alimentaires, les suspensions du contrat comptent et le congé parental compte pour moitié. Les contrats successifs peuvent aussi être repris."),
            ("La prime d'ancienneté compte-t-elle pour atteindre le SMIC ?",
             "Non. Pour vérifier qu'un salarié est payé au moins au SMIC, la jurisprudence exclut la prime d'ancienneté, qui récompense la fidélité et non le travail fourni. Le salaire de base doit donc atteindre seul le minimum légal, puis la prime s'ajoute. Elle s'ajoute de la même façon au salaire minimum conventionnel lorsque la convention le précise, ce qui est le cas le plus fréquent."),
        ],
        "related": ["salaire-brut-net-non-cadre", "simulateur-fiche-de-paie", "smic-brut-net-2026", "indemnite-licenciement", "majoration-nuit-dimanche", "salaire-moyen-france"],
    }


PAGES = [page_arret, page_paternite, page_feries, page_nuit, page_rtt, page_anciennete]
