#!/usr/bin/env python3
"""
Pages « métiers » ajoutées le 2026-10-27 : assistante maternelle, ingénieur informatique,
enseignant, interne en médecine, aide-soignant, infirmier. Importé par generate-thematiques.py.

Chiffres relevés le 27 octobre 2026 :
- assistants maternels : fiche DREETS Pays de la Loire au 12 juin 2026 (minimum conventionnel
  4,20 € brut et 3,28 € net par heure et par enfant depuis le 1er juin 2026, 4,37 € et 3,41 € avec
  le titre AM-GE, plancher légal 0,281 SMIC = 3,46 €, indemnité d'entretien 3,92 € pour 9 h,
  plancher 2,65 €), article D423-9 du CASF, Urssaf (actualité « ce qui change au 1er juin 2026 ») ;
- Syntec (IDCC 1486) : accord du 26 juin 2024 sur les salaires minimaux (annexe III), étendu par
  arrêté du 8 novembre 2024, en vigueur depuis le 1er janvier 2025, aucun accord salarial plus récent
  sur Légifrance au 27 octobre 2026 ;
- professeurs certifiés : décret n° 2017-789 (article 5, indices bruts en vigueur depuis le
  6 août 2023), correspondance indice brut / indice majoré du décret n° 82-1105 au 1er janvier 2024,
  arrêté du 19 juillet 2023 (ISOE part fixe 2 550 €), arrêté du 19 juillet 2023 modifiant l'arrêté du
  12 mars 2021 (prime d'attractivité par échelon) ;
- internes : annexe X de l'arrêté du 8 juillet 2022 (montants au 1er juillet 2023, toujours en
  vigueur au 27 octobre 2026), Ircantec (taux d'appel agent tranche A 2,84 % en 2026) ;
- aides-soignants : décret n° 2021-1267 modifié par le décret n° 2022-1207 (en vigueur depuis le
  1er septembre 2022), catégorie B (décret n° 2021-1257) ;
- infirmiers : décret n° 2021-1262 (en vigueur depuis le 1er octobre 2021) ;
- CTI : 49 points d'indice majoré (décret n° 2020-1152, fonction-publique.gouv.fr) ;
- valeur du point : 5 907,34 € par an pour l'IM 100 depuis le 1er juillet 2023 (service-public F461,
  vérifié le 1er juin 2026, aucune revalorisation en 2026).
"""

import json
import math

from thematiques_commun import *  # noqa: F401,F403

RELEVE = "27 octobre 2026"

# ── Sources ───────────────────────────────────────────────────────────────────
SRC_AM_DREETS = ("DREETS Pays de la Loire, rémunération des assistants maternels au 12 juin 2026", "https://pays-de-la-loire.dreets.gouv.fr/sites/pays-de-la-loire.dreets.gouv.fr/IMG/pdf/fiche_remu_indemnites_frais_au_12062026.pdf")
SRC_AM_CASF = ("Légifrance, Code de l'action sociale et des familles, articles D423-5 et suivants", "https://www.legifrance.gouv.fr/codes/id/LEGIARTI000018261020")
SRC_AM_URSSAF = ("Urssaf, particuliers employeurs : ce qui change au 1er juin 2026", "https://www.urssaf.fr/accueil/actualites/particuliers-evolutions-minimas.html")
SRC_AM_PAJE = ("Pajemploi, la rémunération de l'assistante maternelle", "https://www.pajemploi.urssaf.fr/portail/accueil/assistante-maternelle-agreee/je-suis-remuneree-et-declaree/la-remuneration.html")
SRC_SYNTEC = ("Légifrance, convention Syntec (IDCC 1486), accord du 26 juin 2024 sur les salaires minimaux", "https://www.legifrance.gouv.fr/conv_coll/id/KALIARTI000050228718/?idConteneur=KALICONT000005635173")
SRC_SYNTEC_EXT = ("Légifrance, arrêté d'extension du 8 novembre 2024", "https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000050663556")
SRC_CERTIFIES = ("Légifrance, décret n° 2017-789 fixant l'échelonnement indiciaire des enseignants", "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000034601473")
SRC_ATTRACTIVITE = ("Légifrance, arrêté du 19 juillet 2023 sur la prime d'attractivité", "https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000047862595")
SRC_ISOE = ("Légifrance, arrêté du 19 juillet 2023 sur l'ISOE et l'ISAE", "https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000047862611")
SRC_INTERNES = ("Légifrance, arrêté du 8 juillet 2022, annexe X (rémunération des internes)", "https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000047847275")
SRC_IRCANTEC = ("Ircantec, taux de cotisations au 1er janvier 2026", "https://www.ircantec.retraites.fr/employeur/actualite/augmentation-des-taux-de-cotisations-ircantec-au-1er-janvier-2026")
SRC_GARDES = ("Légifrance, arrêté du 12 juillet 2010 sur l'indemnisation des gardes des internes", "https://www.legifrance.gouv.fr/jorf/id/JORFSCTA000022502921")
SRC_AS = ("Légifrance, décret n° 2021-1267, échelonnement des aides-soignants de la FPH", "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000044126512")
SRC_AS_STATUT = ("Légifrance, décret n° 2021-1257, statut des aides-soignants de la FPH", "https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000044126316")
SRC_IDE = ("Légifrance, décret n° 2021-1262, échelonnement des infirmiers de la FPH", "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000044126441")
SRC_CTI = ("Fonction-publique.gouv.fr, le complément de traitement indiciaire", "https://www.fonction-publique.gouv.fr/etre-agent-public/ma-remuneration/les-elements-accessoires-de-remuneration/le-complement-de-traitement-indiciaire-cti")

NOTE_FP = ("Les montants nets sont calculés pour un fonctionnaire à temps complet : retenue pour pension de 11,10 %, RAFP de 5 % sur les primes, "
           "CSG et CRDS. Ni le supplément familial de traitement, ni la complémentaire santé, ni le prélèvement à la source n'y figurent.")

# ── Fonction publique : traitement et retenues ───────────────────────────────
POINT_MENSUEL = POINT_ANNUEL_IM100 / 1200          # 4,9228 € par point d'indice majoré et par mois
CTI_POINTS = 49


def traitement_im(im):
    """Traitement indiciaire brut mensuel, tronqué au centime comme service-public."""
    return math.floor(im * POINT_ANNUEL_IM100 / 12) / 100


CTI = round(CTI_POINTS * POINT_ANNUEL_IM100 / 1200, 2)  # 241,22 € (service-public, fonction-publique.gouv.fr)


def net_fp(im, cti=0.0, primes=0.0, ir=0.0):
    """Net d'un fonctionnaire : pension 11,10 % sur traitement (+ CTI), RAFP 5 % sur primes et
    indemnité de résidence dans la limite de 20 % du traitement, CSG-CRDS 9,70 % sur 98,25 %."""
    t = traitement_im(im)
    brut = t + cti + primes + ir
    pension = (t + cti) * TAUX_PENSION_CIVILE
    rafp = min(primes + ir, 0.2 * t) * TAUX_RAFP
    csg = brut * TAUX_CSG_CRDS
    return {"traitement": t, "brut": brut, "pension": pension, "rafp": rafp, "csg": csg,
            "net": brut - pension - rafp - csg}


JS_FP = f"""
            function trait(im) {{ return Math.floor(im * {POINT_ANNUEL_IM100} / 12) / 100; }}
            function netfp(im, cti, primes, ir) {{
                var t = trait(im), brut = t + cti + primes + ir;
                return {{ t: t, brut: brut, net: brut - (t + cti) * 0.111 - Math.min(primes + ir, 0.2 * t) * 0.05 - brut * 0.097 * 0.9825 }};
            }}"""


def ech(n):
    return "1er" if n == 1 else f"{n}e"


# ── 1. Assistante maternelle ─────────────────────────────────────────────────
AM_BRUT = 4.20            # minimum conventionnel depuis le 1er juin 2026
AM_NET = 3.28
AM_BRUT_TITRE = 4.37
AM_NET_TITRE = 3.41
AM_PLANCHER = 3.46        # 0,281 × 12,31 €
AM_RATIO = AM_NET / AM_BRUT
AM_ENTRETIEN_9H = 3.92
AM_ENTRETIEN_MIN = 2.65
AM_ENTRETIEN_HEURE = 0.435


def am_entretien(h):
    if h >= 9:
        return AM_ENTRETIEN_9H + (h - 9) * AM_ENTRETIEN_HEURE
    return max(AM_ENTRETIEN_MIN, AM_ENTRETIEN_9H / 9 * h)


def am_mensuel(taux, heures, semaines):
    """Salaire de base mensualisé par enfant : 52 semaines en année complète, semaines programmées sinon."""
    return taux * heures * (52 if semaines >= 47 else semaines) / 12


def page_assmat():
    lignes = []
    for h, sem in ((45, 47), (40, 47), (50, 47), (40, 36), (30, 36)):
        b = am_mensuel(AM_BRUT, h, sem)
        lignes.append([f"{h} h", "année complète" if sem >= 47 else f"{sem} semaines", e2(b), e2(b * AM_RATIO)])
    ex = am_mensuel(AM_BRUT, 45, 47)
    ex3 = ex * 3
    inc = am_mensuel(AM_BRUT, 40, 36)
    jours = 5 * 47 / 12
    ent10 = am_entretien(10)
    corps = f"""
<h2>Le salaire minimum d'une assistante maternelle en 2026</h2>
{table(["Minimum par heure et par enfant", "Brut", "Net"], [
    ["Minimum conventionnel depuis le 1er juin 2026", e2(AM_BRUT), e2(AM_NET)],
    ["Avec le titre « assistant maternel, garde d'enfants »", e2(AM_BRUT_TITRE), e2(AM_NET_TITRE)],
    ["Plancher légal : 0,281 × SMIC horaire", e2(AM_PLANCHER), "–"],
    ["Minimum conventionnel du 1er avril 2025 au 31 mai 2026", e2(3.64), "–"],
])}
{note("Montants publiés par la DREETS Pays de la Loire dans sa fiche du 12 juin 2026 et par l'Urssaf. Le plancher légal de l'article D423-9 du Code de l'action sociale et des familles est inférieur au minimum de la convention collective du particulier employeur (IDCC 3239) : c'est le minimum conventionnel qui s'applique.")}
<h2>Mensualisation : année complète ou incomplète</h2>
<p>Le salaire d'une assistante maternelle est toujours mensualisé : il est le même chaque mois, quel que soit le nombre de jours du mois. Deux formules coexistent.</p>
<ul>
<li><strong>Année complète</strong>, quand l'enfant est accueilli 47 semaines par an ou plus, les cinq semaines de congés payés étant comprises dans la mensualisation : salaire horaire × heures par semaine × 52 ÷ 12. Pour 45 heures par semaine au minimum conventionnel, cela fait {e2(ex)} brut et {e2(ex * AM_RATIO)} net par mois et par enfant.</li>
<li><strong>Année incomplète</strong>, quand l'accueil porte sur 46 semaines ou moins : salaire horaire × heures par semaine × semaines programmées ÷ 12. Les congés payés ne sont pas compris dans ce salaire de base : ils sont versés en plus, au moment où ils sont pris, lors du congé principal ou en une fois en juin, selon ce que prévoit le contrat. Pour 40 heures sur 36 semaines, le salaire de base est de {e2(inc)} brut par mois.</li>
</ul>
{table(["Heures par semaine", "Accueil", "Brut mensuel par enfant", "Net mensuel par enfant"], lignes)}
{note("Calcul au minimum conventionnel de 4,20 € brut de l'heure. Net obtenu avec le rapport entre le net et le brut publiés (3,28 ÷ 4,20, soit 78,1 %). Hors congés payés de l'année incomplète, hors indemnités d'entretien et de repas.")}
<h2>Les indemnités qui s'ajoutent au salaire</h2>
<p>L'<strong>indemnité d'entretien</strong> couvre les frais de l'assistante maternelle (eau, chauffage, jeux, matériel). Elle n'est pas un salaire : elle ne supporte aucune cotisation et n'est pas due quand l'enfant est absent. Le minimum est de {e2(AM_ENTRETIEN_9H)} pour une journée de 9 heures, soit 90 % du minimum garanti de 4,35 €. Pour une journée plus longue, on ajoute 0,435 € par heure au-delà de 9 heures : 10 heures d'accueil donnent {e2(ent10)}. Pour une journée plus courte, on retient le plus favorable entre {e2(AM_ENTRETIEN_MIN)} et 3,92 € ÷ 9 × le nombre d'heures.</p>
<p>L'<strong>indemnité de repas</strong> n'est due que si l'assistante maternelle fournit les repas ; son montant est fixé au contrat. L'<strong>indemnité kilométrique</strong> s'applique quand elle transporte l'enfant avec son véhicule, entre le barème de l'administration et le barème fiscal.</p>
<h2>Plusieurs enfants accueillis</h2>
<p>Une assistante maternelle signe un contrat avec chaque famille : chaque salaire se calcule séparément, puis ils s'additionnent. Trois enfants accueillis 45 heures par semaine en année complète au minimum conventionnel représentent {e2(ex3)} brut et {e2(ex3 * AM_RATIO)} net par mois, auxquels s'ajoutent environ {e(am_entretien(9) * jours * 3)} d'indemnités d'entretien pour des journées de 9 heures, cinq jours par semaine.</p>
<h2>Heures majorées</h2>
<p>Les heures au-delà de 45 heures par semaine sont majorées d'au moins 10 %, au taux prévu par le contrat. Entre la durée prévue au contrat et 45 heures, les heures complémentaires peuvent être majorées si le contrat le prévoit.</p>
"""
    js = f"""
            var taux = v('w-taux'), h = v('w-h'), sem = v('w-sem'), j = v('w-jours'), dj = v('w-duree');
            var brut = taux * h * (sem >= 47 ? 52 : sem) / 12;
            var ent = dj >= 9 ? 3.92 + (dj - 9) * 0.435 : Math.max(2.65, 3.92 / 9 * dj);
            out('r-brut', centimes(brut));
            out('r-net', centimes(brut * {AM_NET} / {AM_BRUT}));
            out('r-ent', centimes(ent * j * Math.min(sem, 47) / 12));
            out('r-cp', sem >= 47 ? 'inclus' : centimes(brut * 12 * 0.1));"""
    return {
        "slug": "salaire-assistante-maternelle",
        "title": "Salaire assistante maternelle 2026 : 4,20 € brut de l'heure",
        "desc": "Salaire assistante maternelle 2026 : 4,20 € brut et 3,28 € net par heure et par enfant depuis juin. Mensualisation, année incomplète, indemnité d'entretien.",
        "h1": "Salaire d'une assistante maternelle en 2026",
        "crumb": "Assistante maternelle",
        "widget_titre": "Salaire mensualisé pour un enfant",
        "widget": widget([champ("w-taux", "Salaire horaire brut (€)", "4,20"),
                          champ("w-h", "Heures d'accueil par semaine", "45"),
                          champ("w-sem", "Semaines d'accueil par an", "47"),
                          champ("w-jours", "Jours d'accueil par semaine", "5"),
                          champ("w-duree", "Heures d'accueil par jour", "9")],
                         [("r-brut", "Salaire brut mensuel"), ("r-net", "Salaire net mensuel"),
                          ("r-ent", "Entretien par mois"), ("r-cp", "Congés payés par an")],
                         "47 semaines ou plus : année complète (52 ÷ 12). 46 semaines ou moins : année incomplète, congés payés estimés à 10 % du salaire annuel et versés en plus."),
        "js": js,
        "citable": f"Depuis le 1er juin 2026, une assistante maternelle agréée gagne au minimum {e2(AM_BRUT)} brut, soit {e2(AM_NET)} net, par heure et par enfant accueilli, selon la convention collective du particulier employeur. Ce minimum passe à {e2(AM_BRUT_TITRE)} brut ({e2(AM_NET_TITRE)} net) pour une professionnelle titulaire du titre « assistant maternel, garde d'enfants ». Le salaire est mensualisé : en année complète, on multiplie le taux horaire par les heures hebdomadaires puis par 52, avant de diviser par 12. Un enfant gardé 45 heures par semaine rapporte ainsi {e2(ex)} brut et {e2(ex * AM_RATIO)} net par mois. S'y ajoute une indemnité d'entretien non soumise à cotisations, d'au moins {e2(AM_ENTRETIEN_9H)} pour une journée de 9 heures. Le plancher légal, 0,281 fois le SMIC horaire, s'élève à {e2(AM_PLANCHER)} et reste inférieur au minimum conventionnel.",
        "corps": corps,
        "sources": [SRC_AM_DREETS, SRC_AM_URSSAF, SRC_AM_CASF, SRC_AM_PAJE],
        "releve": RELEVE,
        "note_sources": "Le net est obtenu avec le rapport publié entre le salaire net et le salaire brut minimum ; le net exact dépend des cotisations calculées par Pajemploi.",
        "faq": [
            ("Quel est le tarif horaire minimum d'une assistante maternelle en 2026 ?",
             f"Depuis le 1er juin 2026, le minimum conventionnel est de {e2(AM_BRUT)} brut par heure et par enfant, soit {e2(AM_NET)} net. Il était de 3,64 € brut du 1er avril 2025 au 31 mai 2026. Une assistante maternelle titulaire du titre professionnel de la branche a droit à {e2(AM_BRUT_TITRE)} brut. Les parents peuvent toujours convenir d'un tarif plus élevé, fixé dans le contrat de travail."),
            ("Comment calculer la mensualisation d'une assistante maternelle ?",
             "En année complète, multipliez le salaire horaire par le nombre d'heures d'accueil par semaine, puis par 52, et divisez par 12. En année incomplète, remplacez 52 par le nombre de semaines d'accueil programmées, 46 au plus. Le montant obtenu est versé tous les mois à l'identique, y compris les mois où l'enfant est moins présent, puis régularisé en fin de contrat si l'accueil réel a différé."),
            ("Quelle différence entre année complète et année incomplète ?",
             "L'année complète correspond à un accueil d'au moins 47 semaines par an : les cinq semaines de congés payés sont alors comprises dans le salaire mensualisé calculé sur 52 semaines. En année incomplète, l'enfant est accueilli 46 semaines ou moins, souvent hors vacances scolaires : le salaire de base porte sur les seules semaines programmées et les congés payés sont versés en supplément."),
            ("L'indemnité d'entretien est-elle imposable ?",
             f"L'indemnité d'entretien n'est pas un salaire : elle ne supporte ni cotisations ni CSG, et elle n'est pas due en cas d'absence de l'enfant. Son minimum est de {e2(AM_ENTRETIEN_9H)} pour 9 heures d'accueil, sans pouvoir descendre sous {e2(AM_ENTRETIEN_MIN)} par jour. Pour l'impôt sur le revenu, les assistantes maternelles bénéficient d'un régime particulier qui tient compte de ces indemnités dans le calcul du revenu déclaré."),
            ("Combien gagne une assistante maternelle avec trois enfants ?",
             f"Avec trois enfants accueillis 45 heures par semaine en année complète, au minimum conventionnel, le salaire atteint {e2(ex3)} brut et environ {e2(ex3 * AM_RATIO)} net par mois. Il faut y ajouter les indemnités d'entretien, de l'ordre de {e(am_entretien(9) * jours * 3)} par mois pour des journées de 9 heures cinq jours par semaine, et les indemnités de repas si elle fournit les repas."),
            ("Les heures au-delà de 45 heures sont-elles majorées ?",
             "Oui. Les heures de travail effectuées au-delà de 45 heures par semaine ouvrent droit à une majoration de salaire dont le taux est fixé au contrat et ne peut être inférieur à 10 %. Les heures faites au-delà de la durée prévue au contrat mais sans dépasser 45 heures sont des heures complémentaires, majorées seulement si les parties l'ont prévu par écrit."),
        ],
        "related": ["cesu-brut-net", "smic-brut-net-2026", "salaire-brut-net-horaire", "indemnite-conges-payes", "salaire-net-imposable", "simulateur-fiche-de-paie"],
    }


# ── 2. Ingénieur informatique ────────────────────────────────────────────────
SYNTEC_IC = [  # position, coefficient, minimum mensuel brut (accord du 26 juin 2024)
    ("1.1", 95, 2135), ("1.2", 100, 2240), ("2.1", 105, 2315), ("2.1", 115, 2530), ("2.2", 130, 2850),
    ("2.3", 150, 3275), ("3.1", 170, 3650), ("3.2", 210, 4495), ("3.3", 270, 5755),
]


def net_cadre_annuel(brut_annuel, mois=12):
    """Net mensuel moyen d'un cadre à partir du brut annuel (primes réparties sur l'année)."""
    return calculer_brut_vers_net(brut_annuel / 12, "cadre")["net_avant_impot"]


def page_ingenieur():
    lignes = []
    for pos, coef, m in SYNTEC_IC:
        lignes.append([f"{pos} (coefficient {coef})", e(m), e(m * 12), e(net_cadre_annuel(m * 12))])
    exemples = [(38000,), (45000,), (55000,), (70000,)]
    l2 = [[e(b), e(b / 12), e(net_cadre_annuel(b)), e(net_cadre_annuel(b) * 12)] for (b,) in exemples]
    n45 = net_cadre_annuel(45000)
    corps = f"""
<h2>Les minima Syntec des ingénieurs et cadres</h2>
<p>La plupart des ingénieurs informatiques salariés d'une entreprise de services numériques ou d'un cabinet de conseil relèvent de la convention collective des bureaux d'études techniques, dite Syntec (IDCC 1486). Ses minima mensuels bruts pour les ingénieurs et cadres sont fixés par l'accord du 26 juin 2024, étendu par arrêté du 8 novembre 2024 et appliqué depuis le 1er janvier 2025. Aucun accord salarial plus récent n'était publié sur Légifrance au 27 octobre 2026 : ces minima restent ceux de 2026.</p>
{table(["Position", "Minimum mensuel brut", "Minimum annuel brut", "Net mensuel cadre"], lignes)}
{note("Grille des ingénieurs et cadres de l'annexe III. La position 2.1 compte deux coefficients : 105 avant 26 ans, 115 à partir de 26 ans. Net avant impôt calculé avec les cotisations salariales 2026 d'un cadre, hors mutuelle et prévoyance.")}
<h2>Ce que disent les statistiques publiques</h2>
<p>Aucune source publique ne publie de salaire 2026 propre aux ingénieurs informatiques : l'Insee diffuse les salaires par grande catégorie avec deux ans de décalage. Dans le secteur privé, un cadre percevait en moyenne <strong>{e(INSEE['cadres'])} net par mois en 2024</strong> (Insee Première n° 2079), tous métiers confondus. Les montants que l'on voit circuler pour un « ingénieur informatique débutant » ou « confirmé » proviennent d'enquêtes privées et d'offres d'emploi : nous ne les reprenons pas, faute de pouvoir les vérifier.</p>
<h2>Du brut annuel au net mensuel</h2>
<p>Les offres d'emploi en informatique sont presque toujours exprimées en brut annuel. Pour un cadre en 2026, le passage au net retire environ 21 à 22 % jusqu'au plafond de la Sécurité sociale, un peu moins au-delà, avant le prélèvement à la source.</p>
{table(["Brut annuel", "Brut mensuel (sur 12 mois)", "Net mensuel avant impôt", "Net annuel"], l2)}
{note("Statut cadre, temps plein, cotisations salariales 2026 du régime général, hors mutuelle et prévoyance d'entreprise.")}
<h2>Points d'attention</h2>
<ul>
<li>Un salaire versé sur 13 mois ne change pas le net annuel : il se répartit seulement autrement.</li>
<li>Le forfait jours et les modalités de temps de travail de la convention Syntec imposent souvent une rémunération supérieure au minimum de la position : vérifiez la clause de votre contrat.</li>
<li>La prime de vacances Syntec, égale au moins à 10 % de l'indemnité de congés payés globale de l'ensemble des salariés, s'ajoute au salaire.</li>
<li>Un ingénieur en régie ou au forfait jours reste soumis au même calcul de cotisations : seul le brut change le net.</li>
</ul>
"""
    js = """
            var b = v('w-brut'), pos = document.getElementById('w-pos').value.split('|');
            var mini = parseFloat(pos[1]);
            var r = calculerBrutVersNet(b / 12, 'cadre', 1);
            out('r-net', euros(r.netAvantImpot));
            out('r-netan', euros(r.netAvantImpot * 12));
            out('r-min', euros(mini * 12));
            out('r-ecart', (b >= mini * 12 ? '+ ' : '− ') + euros(Math.abs(b - mini * 12)));"""
    options = [(f"{p}|{m}", f"Position {p}, coefficient {c}") for p, c, m in SYNTEC_IC]
    return {
        "slug": "salaire-ingenieur-informatique",
        "title": "Salaire ingénieur informatique 2026 : minima Syntec et net",
        "desc": f"Salaire ingénieur informatique 2026 : minimum Syntec de 2 135 à 5 755 € brut par mois selon la position, et net mensuel d'un cadre. 45 000 € brut = {fmt(n45)} € net.",
        "h1": "Salaire d'un ingénieur informatique en 2026",
        "crumb": "Ingénieur informatique",
        "widget_titre": "Du brut annuel au net, face au minimum Syntec",
        "widget": widget([champ("w-brut", "Salaire brut annuel (€)", "45000"),
                          choix("w-pos", "Position Syntec", options, "2.2|2850")],
                         [("r-net", "Net mensuel"), ("r-netan", "Net annuel"),
                          ("r-min", "Minimum Syntec annuel"), ("r-ecart", "Écart au minimum")]),
        "js": js,
        "citable": f"En 2026, un ingénieur informatique salarié relevant de la convention Syntec (IDCC 1486) ne peut pas être payé moins que le minimum de sa position : de {e(2135)} brut par mois en position 1.1 à {e(5755)} en position 3.3, selon l'accord du 26 juin 2024 étendu le 8 novembre 2024 et toujours en vigueur. Un jeune diplômé de 26 ans et plus classé en position 2.1 doit percevoir au moins {e(2530)} brut par mois, soit {e(2530 * 12)} par an. Sur le net, un cadre payé {e(45000)} brut par an touche environ {e(n45)} net par mois avant impôt. Aucune statistique publique ne donne de salaire 2026 propre à ce métier ; la moyenne des cadres du privé était de {e(INSEE['cadres'])} net par mois en 2024 selon l'Insee.",
        "corps": corps,
        "sources": [SRC_SYNTEC, SRC_SYNTEC_EXT, SRC_INSEE, SRC_TAUX],
        "releve": RELEVE,
        "faq": [
            ("Quel est le salaire minimum d'un ingénieur Syntec en 2026 ?",
             f"Le minimum dépend de la position. Pour un ingénieur ou cadre, il va de {e(2135)} brut par mois en position 1.1 à {e(5755)} en position 3.3. Un ingénieur débutant de 26 ans ou plus est généralement classé en position 2.1, coefficient 115, avec un minimum de {e(2530)} brut par mois. Ces montants viennent de l'accord du 26 juin 2024, appliqué depuis janvier 2025."),
            ("Combien fait 45 000 € brut annuel en net pour un ingénieur ?",
             f"Pour un cadre à temps plein, {e(45000)} brut par an donnent environ {e(n45)} net par mois avant impôt, soit {e(n45 * 12)} net sur l'année. Le prélèvement à la source vient ensuite en déduction, selon le taux du foyer. Une mutuelle d'entreprise obligatoire réduit aussi le net de quelques dizaines d'euros par mois."),
            ("Existe-t-il une statistique officielle du salaire des ingénieurs informatiques ?",
             f"Pas pour 2026. L'Insee publie les salaires du privé par catégorie socioprofessionnelle avec environ deux ans de décalage : en 2024, un cadre gagnait en moyenne {e(INSEE['cadres'])} net par mois, tous métiers réunis. Les chiffres par métier qui circulent en ligne proviennent d'enquêtes privées ou d'annonces, dont la méthode n'est pas publique."),
            ("Quelle position Syntec pour un ingénieur débutant ?",
             f"La grille Syntec classe les ingénieurs débutants en position 1.1 ou 1.2 tant qu'ils sont en période d'adaptation, puis en position 2.1. Cette position a deux coefficients : 105 avant 26 ans, soit {e(2315)} brut par mois au minimum, et 115 à partir de 26 ans, soit {e(2530)}. La classification exacte dépend des fonctions réellement exercées, pas seulement du diplôme."),
            ("La prime de vacances Syntec s'ajoute-t-elle au salaire ?",
             "Oui. La convention Syntec prévoit une prime de vacances dont le montant global, pour l'ensemble des salariés de l'entreprise, est au moins égal à 10 % de la masse globale des indemnités de congés payés. Elle est soumise aux mêmes cotisations que le salaire. Certaines entreprises l'intègrent dans un treizième mois ou dans d'autres primes versées dans l'année, à condition qu'elles soient payées entre mai et octobre."),
            ("Un ingénieur informatique est-il forcément cadre ?",
             "Non. Le statut cadre dépend de la classification dans la convention collective, pas du titre de poste. Dans la convention Syntec, les ingénieurs et cadres ont leur propre grille, distincte de celle des ETAM. Un technicien ou développeur classé ETAM cotise comme un non-cadre, et son net est légèrement supérieur à brut égal, faute de cotisation Apec."),
        ],
        "related": ["salaire-brut-net-cadre", "salaire-brut-net-annuel", "salaire-moyen-france", "portage-salarial", "jours-rtt", "simulateur-fiche-de-paie"],
    }


# ── 3. Enseignant (professeur certifié) ──────────────────────────────────────
CERT_CN = [395, 446, 453, 466, 481, 497, 524, 562, 595, 634, 678]       # classe normale, échelons 1 à 11
CERT_HC = [595, 629, 673, 720, 768, 811, 826]                           # hors classe, échelons 1 à 7
CERT_CE = [700, 740, 780, 835]                                          # classe exceptionnelle, échelons 1 à 4
ATTRACTIVITE = [2130, 2980, 3370, 3180, 2880, 2500, 1500, 400, 400]     # classe normale, échelons 1 à 9
ISOE = 2550


def ens_net(im, pa=0.0, ir_taux=0.0):
    primes = ISOE / 12 + pa / 12
    ir = traitement_im(im) * ir_taux
    return net_fp(im, 0, primes, ir)


def page_enseignant():
    lignes = []
    for i, im in enumerate(CERT_CN, 1):
        pa = ATTRACTIVITE[i - 1] if i <= 9 else 0
        r = ens_net(im, pa)
        lignes.append([ech(i), str(im), e2(r["traitement"]), e(pa) if pa else "–", e2(r["net"])])
    l_hc = []
    for i, im in enumerate(CERT_HC, 1):
        r = ens_net(im)
        l_hc.append([f"Hors classe, {ech(i)} échelon", str(im), e2(r["traitement"]), e2(r["net"])])
    for i, im in enumerate(CERT_CE, 1):
        r = ens_net(im)
        l_hc.append([f"Classe exceptionnelle, {ech(i)} échelon", str(im), e2(r["traitement"]), e2(r["net"])])
    d = ens_net(CERT_CN[0], ATTRACTIVITE[0])
    f11 = ens_net(CERT_CN[10])
    options = ([(f"cn{i}", f"Classe normale, {ech(i)} échelon (IM {im})") for i, im in enumerate(CERT_CN, 1)]
               + [(f"hc{i}", f"Hors classe, {ech(i)} échelon (IM {im})") for i, im in enumerate(CERT_HC, 1)]
               + [(f"ce{i}", f"Classe exceptionnelle, {ech(i)} échelon (IM {im})") for i, im in enumerate(CERT_CE, 1)])
    grille = json.dumps({"cn": CERT_CN, "hc": CERT_HC, "ce": CERT_CE})
    corps = f"""
<h2>Grille des professeurs certifiés en 2026</h2>
<p>Le traitement d'un enseignant titulaire dépend de son échelon : chaque échelon correspond à un indice majoré, multiplié par la valeur du point d'indice. Celle-ci reste fixée à {e2(POINT_ANNUEL_IM100)} par an pour l'indice 100 depuis le 1er juillet 2023, sans revalorisation en 2026 selon service-public.gouv.fr. Un point d'indice vaut donc {fmt2(POINT_MENSUEL)} € brut par mois.</p>
{table(["Classe normale", "Indice majoré", "Traitement brut", "Prime d'attractivité par an", "Net mensuel estimé"], lignes)}
{note("Indices bruts du décret n° 2017-789 (version en vigueur depuis le 6 août 2023), convertis en indices majorés selon le barème du décret n° 82-1105 au 1er janvier 2024. Net estimé avec la part fixe de l'ISOE (212,50 € par mois) et la prime d'attractivité de l'échelon, sans indemnité de résidence.")}
<h2>Hors classe et classe exceptionnelle</h2>
{table(["Grade et échelon", "Indice majoré", "Traitement brut", "Net mensuel estimé"], l_hc)}
{note("Net estimé avec la part fixe de l'ISOE, sans prime d'attractivité, réservée aux échelons 1 à 9 de la classe normale. Le 5e échelon de la classe exceptionnelle est placé en hors-échelle A et n'est pas détaillé ici.")}
<h2>Les primes communes à tous les certifiés</h2>
<ul>
<li><strong>Part fixe de l'ISOE</strong> (indemnité de suivi et d'orientation des élèves) : {e(ISOE)} brut par an depuis le 1er septembre 2023, soit 212,50 € par mois. Les professeurs des écoles perçoivent l'ISAE, du même montant.</li>
<li><strong>Prime d'attractivité</strong> : de 400 € à 3 370 € brut par an selon l'échelon de la classe normale, du 1er au 9e échelon, fixée par l'arrêté du 19 juillet 2023.</li>
<li><strong>Indemnité de résidence</strong> : 0 %, 1 % ou 3 % du traitement selon la commune d'affectation.</li>
<li><strong>Pacte enseignant et missions</strong> : la part fonctionnelle de l'ISOE, professeur principal ou missions du pacte, et les heures supplémentaires s'ajoutent selon l'activité réelle ; elles ne figurent pas dans les tableaux.</li>
</ul>
<h2>Du brut au net</h2>
<p>Un enseignant titulaire ne cotise pas comme un salarié du privé : il supporte la retenue pour pension civile de 11,10 % sur son seul traitement indiciaire, la retraite additionnelle (RAFP) de 5 % sur ses primes dans la limite de 20 % du traitement, et la CSG-CRDS sur l'ensemble. Un certifié au 1er échelon perçoit ainsi {e2(d['brut'])} brut, primes comprises, et environ <strong>{e2(d['net'])} net</strong>. Au 11e échelon de la classe normale, le net atteint environ {e2(f11['net'])}. Les règles générales du calcul sont détaillées sur notre page consacrée au <a href="/salaire-brut-net-fonction-publique/">salaire brut et net dans la fonction publique</a>.</p>
<p>L'abattement « transfert primes-points », prévu par le décret n° 2016-588, retient en outre jusqu'à 389 € par an sur les primes des fonctionnaires de catégorie A : selon les bulletins, il réduit le net d'une trentaine d'euros par mois. Nous ne l'intégrons pas au calcul.</p>
"""
    js = JS_FP + f"""
            var g = {grille}, pa = {json.dumps(ATTRACTIVITE)};
            var sel = document.getElementById('w-ech').value, cl = sel.slice(0, 2), n = parseInt(sel.slice(2), 10);
            var im = g[cl][n - 1];
            var prime = (cl === 'cn' && n <= 9) ? pa[n - 1] / 12 : 0;
            var irt = parseFloat(document.getElementById('w-ir').value);
            var r = netfp(im, 0, {ISOE} / 12 + prime + v('w-autres'), trait(im) * irt);
            out('r-t', centimes(r.t));
            out('r-brut', centimes(r.brut));
            out('r-net', centimes(r.net));"""
    return {
        "slug": "salaire-enseignant",
        "title": "Salaire enseignant 2026 : grille des certifiés, brut et net",
        "desc": f"Salaire enseignant 2026 : grille des certifiés par échelon, indice majoré, ISOE et prime d'attractivité. Un débutant touche environ {fmt(d['net'])} € net par mois.",
        "h1": "Salaire d'un enseignant en 2026 : la grille des certifiés",
        "crumb": "Salaire enseignant",
        "widget_titre": "Traitement net d'un professeur certifié",
        "widget": widget([choix("w-ech", "Grade et échelon", options, "cn1"),
                          choix("w-ir", "Indemnité de résidence", [("0", "0 %"), ("0.01", "1 %"), ("0.03", "3 %")], "0"),
                          champ("w-autres", "Autres primes mensuelles brutes (€)", "0")],
                         [("r-t", "Traitement indiciaire"), ("r-brut", "Brut avec primes"), ("r-net", "Net mensuel")],
                         "ISOE part fixe et prime d'attractivité de l'échelon comprises. Hors supplément familial, heures supplémentaires et abattement transfert primes-points."),
        "js": js,
        "citable": f"En 2026, un professeur certifié débutant, au 1er échelon de la classe normale, est rémunéré sur l'indice majoré 395, soit un traitement de {e2(d['traitement'])} brut par mois, la valeur du point d'indice n'ayant pas bougé depuis juillet 2023. S'y ajoutent la part fixe de l'ISOE, {e(ISOE)} brut par an, et une prime d'attractivité de {e(ATTRACTIVITE[0])} par an au 1er échelon, qui culmine à {e(3370)} au 3e échelon. Après retenue pour pension de 11,10 %, RAFP et CSG-CRDS, le net atteint environ {e2(d['net'])} par mois. Au 11e et dernier échelon de la classe normale, indice 678, le traitement est de {e2(f11['traitement'])} brut et le net d'environ {e2(f11['net'])}. La hors classe culmine à l'indice 826 et la classe exceptionnelle à l'indice 835, avant la hors-échelle A.",
        "corps": corps,
        "sources": [SRC_CERTIFIES, SRC_ISOE, SRC_ATTRACTIVITE, SRC_FP, SRC_PENSION],
        "releve": RELEVE,
        "note_sources": NOTE_FP,
        "faq": [
            ("Combien gagne un professeur certifié débutant en 2026 ?",
             f"Au 1er échelon de la classe normale, un professeur certifié perçoit un traitement de {e2(d['traitement'])} brut par mois, auquel s'ajoutent 212,50 € de part fixe d'ISOE et {e2(ATTRACTIVITE[0] / 12)} de prime d'attractivité. Son net est d'environ {e2(d['net'])} par mois, avant prélèvement à la source et sans indemnité de résidence. Les heures supplémentaires et missions du pacte s'ajoutent en plus."),
            ("Quelle est la valeur du point d'indice des enseignants en 2026 ?",
             f"Les enseignants titulaires partagent la valeur du point de toute la fonction publique : {e2(POINT_ANNUEL_IM100)} par an pour l'indice majoré 100, soit {fmt2(POINT_MENSUEL)} € par mois et par point. Cette valeur est inchangée depuis le 1er juillet 2023. Les hausses de rémunération récentes sont passées par les primes, notamment l'ISOE et la prime d'attractivité, plutôt que par le point."),
            ("Quel est le montant de la prime d'attractivité par échelon ?",
             "Depuis le 1er septembre 2023, la prime d'attractivité annuelle brute est de 2 130 € au 1er échelon, 2 980 € au 2e, 3 370 € au 3e, 3 180 € au 4e, 2 880 € au 5e, 2 500 € au 6e, 1 500 € au 7e et 400 € aux 8e et 9e échelons de la classe normale. Elle est versée chaque mois par douzième et supporte la CSG et la RAFP."),
            ("Combien gagne un enseignant en fin de carrière ?",
             f"Un certifié au 11e échelon de la classe normale est à l'indice 678, soit {e2(f11['traitement'])} brut par mois et environ {e2(f11['net'])} net avec l'ISOE. En hors classe, le 7e échelon atteint l'indice 826 ; en classe exceptionnelle, le 4e échelon l'indice 835, puis la hors-échelle A au 5e échelon. L'accès à ces grades dépend d'un avancement au choix."),
            ("Un enseignant contractuel est-il payé sur la même grille ?",
             "Non. Les enseignants contractuels relèvent de grilles propres fixées par académie, en général plus basses, et cotisent au régime général et à l'Ircantec au lieu de la retenue pour pension civile. Leur passage du brut au net suit donc les taux d'un agent contractuel. Les montants de cette page concernent les professeurs certifiés titulaires et stagiaires."),
            ("L'indemnité de résidence change-t-elle beaucoup le salaire ?",
             f"Elle représente 0 %, 1 % ou 3 % du traitement brut selon la commune d'affectation. Pour un débutant à l'indice 395 affecté en zone à 3 %, cela ajoute {e2(traitement_im(395) * 0.03)} brut par mois. Elle supporte la CSG et la RAFP, mais pas la retenue pour pension. Les communes de la région parisienne et de quelques grandes agglomérations sont classées dans la zone à 3 %."),
        ],
        "related": ["salaire-brut-net-fonction-publique", "salaire-moyen-france", "salaire-infirmier", "heures-supplementaires-brut-net", "taux-prelevement-a-la-source", "calcul-retraite"],
    }


# ── 4. Interne en médecine ───────────────────────────────────────────────────
INTERNES = [19406.35, 21483.24, 28408.30, 28430.36, 28448.22]   # brut annuel, 1re à 5e année
ISP = 435.18                                                     # sujétions particulières, semestres 1 à 4
RESPO = {4: 2154.10, 5: 4273.93}                                 # prime de responsabilité annuelle (médecine)
TAUX_IRCANTEC = 0.0284
TAUX_INTERNE = 0.069 + 0.004 + TAUX_IRCANTEC + TAUX_CSG_CRDS     # vieillesse, Ircantec, CSG-CRDS


def interne(annee, gardes=0.0):
    brut = INTERNES[annee - 1] / 12 + (ISP if annee <= 2 else 0) + RESPO.get(annee, 0) / 12 + gardes
    return brut, brut * (1 - TAUX_INTERNE)


def page_interne():
    lignes = []
    for a in range(1, 6):
        brut, n = interne(a)
        lignes.append([f"{a}{'re' if a == 1 else 'e'} année", e2(INTERNES[a - 1]), e2(brut), e2(n)])
    b1, n1 = interne(1)
    b3, n3 = interne(3)
    corps = f"""
<h2>Rémunération des internes par année</h2>
{table(["Année d'internat", "Rémunération annuelle brute", "Brut mensuel avec primes", "Net mensuel estimé"], lignes)}
{note("Montants de l'annexe X de l'arrêté du 8 juillet 2022, en vigueur au 1er juillet 2023 et toujours applicables au 27 octobre 2026 : aucune revalorisation n'a été publiée depuis. Le brut mensuel comprend l'indemnité de sujétions particulières (1re et 2e années) et la prime de responsabilité (4e et 5e années de médecine). Hors gardes, avantages en nature et indemnités de logement.")}
<h2>Les éléments qui s'ajoutent</h2>
<ul>
<li><strong>Indemnité de sujétions particulières</strong> : {e2(ISP)} brut par mois pendant les quatre premiers semestres, soit les deux premières années.</li>
<li><strong>Prime de responsabilité</strong> : {e2(RESPO[4])} brut par an en 4e année et {e2(RESPO[5])} en 5e année pour les internes en médecine.</li>
<li><strong>Gardes</strong> : chaque garde est indemnisée en plus. Le montant unitaire a été revalorisé à plusieurs reprises depuis l'arrêté du 12 juillet 2010 ; nous n'avons pas pu vérifier sur une source officielle sa valeur exacte en 2026, d'où un champ libre dans le simulateur.</li>
<li><strong>Docteurs juniors</strong> : en phase de consolidation, ils perçoivent {e2(28495.49)} brut par an selon l'annexe XI du même arrêté.</li>
</ul>
<h2>Du brut au net</h2>
<p>Un interne est un agent public non titulaire : il cotise à l'assurance vieillesse du régime général (6,90 % plafonné et 0,40 % déplafonné), à la retraite complémentaire Ircantec (2,84 % en tranche A en 2026, taux d'appel) et à la CSG-CRDS (9,70 % sur 98,25 % du brut). Il ne cotise ni à l'Agirc-Arrco ni à l'assurance chômage. Au total, environ {pct(TAUX_INTERNE * 100)} du brut est retenu. Un interne de 1re année perçoit ainsi {e2(b1)} brut par mois et environ <strong>{e2(n1)} net</strong>, avant gardes et prélèvement à la source.</p>
<p>Le passage en 3e année marque le saut le plus net : la rémunération annuelle passe de {e(INTERNES[1])} à {e(INTERNES[2])}, mais l'indemnité de sujétions particulières s'arrête. Le net mensuel hors gardes passe à {e2(n3)}.</p>
"""
    js = f"""
            var g = {json.dumps(INTERNES)}, a = parseInt(document.getElementById('w-annee').value, 10);
            var respo = {{4: {RESPO[4]}, 5: {RESPO[5]}}};
            var brut = g[a - 1] / 12 + (a <= 2 ? {ISP} : 0) + (respo[a] || 0) / 12 + v('w-gardes');
            out('r-brut', centimes(brut));
            out('r-net', centimes(brut * (1 - {TAUX_INTERNE})));
            out('r-an', euros(brut * (1 - {TAUX_INTERNE}) * 12));"""
    return {
        "slug": "salaire-interne-medecine",
        "title": "Salaire interne en médecine 2026 : brut et net par année",
        "desc": f"Salaire interne en médecine 2026 : de {fmt(INTERNES[0])} € à {fmt(INTERNES[4])} € brut par an selon l'année, plus sujétions et prime de responsabilité. Net mensuel et gardes.",
        "h1": "Salaire d'un interne en médecine en 2026",
        "crumb": "Interne en médecine",
        "widget_titre": "Net mensuel d'un interne",
        "widget": widget([choix("w-annee", "Année d'internat", [(str(a), f"{a}{'re' if a == 1 else 'e'} année") for a in range(1, 6)], "1"),
                          champ("w-gardes", "Indemnités de garde du mois, brut (€)", "0")],
                         [("r-brut", "Brut mensuel"), ("r-net", "Net mensuel"), ("r-an", "Net sur 12 mois")]),
        "js": js,
        "citable": f"En 2026, un interne en médecine de 1re année perçoit une rémunération de {e2(INTERNES[0])} brut par an, à laquelle s'ajoute une indemnité de sujétions particulières de {e2(ISP)} brut par mois pendant les deux premières années : soit {e2(b1)} brut et environ {e2(n1)} net par mois, hors gardes. La rémunération passe à {e2(INTERNES[1])} en 2e année, {e2(INTERNES[2])} en 3e année, puis {e2(INTERNES[4])} en 5e année, avec une prime de responsabilité en 4e et 5e années. Ces montants sont ceux de l'arrêté du 8 juillet 2022, revalorisés au 1er juillet 2023 et inchangés depuis. Un interne cotise au régime général pour la vieillesse, à l'Ircantec et à la CSG-CRDS, soit environ {pct(TAUX_INTERNE * 100)} de retenues ; les gardes s'ajoutent au salaire.",
        "corps": corps,
        "sources": [SRC_INTERNES, SRC_IRCANTEC, SRC_GARDES, SRC_TAUX],
        "releve": RELEVE,
        "note_sources": "Net estimé avec les taux salariaux 2026 d'un agent public non titulaire (vieillesse, Ircantec, CSG-CRDS), hors mutuelle, logement et repas.",
        "faq": [
            ("Combien gagne un interne de première année en 2026 ?",
             f"Un interne de 1re année perçoit {e2(INTERNES[0])} brut par an, soit {e2(INTERNES[0] / 12)} par mois, plus l'indemnité de sujétions particulières de {e2(ISP)}. Cela fait {e2(b1)} brut et environ {e2(n1)} net par mois avant gardes et prélèvement à la source. Ces montants n'ont pas été revalorisés depuis le 1er juillet 2023."),
            ("Les gardes des internes sont-elles payées en plus ?",
             "Oui. Chaque garde de nuit, de dimanche ou de jour férié donne lieu à une indemnité forfaitaire versée en plus de la rémunération mensuelle, et soumise aux mêmes cotisations. Le montant unitaire est fixé par arrêté et a été revalorisé depuis 2010 ; pour connaître la somme exacte, référez-vous à votre bulletin de paie et saisissez le total du mois dans le simulateur."),
            ("Pourquoi le salaire augmente-t-il fortement en troisième année ?",
             f"La grille prévoit un saut entre la 2e année, {e(INTERNES[1])} brut par an, et la 3e année, {e(INTERNES[2])}, soit plus de {e(INTERNES[2] - INTERNES[1])} de hausse annuelle. Dans le même temps, l'indemnité de sujétions particulières, versée pendant les quatre premiers semestres, s'arrête. Le net mensuel progresse donc moins que la seule rémunération de base."),
            ("Un interne cotise-t-il au chômage et à l'Agirc-Arrco ?",
             "Non. L'interne est un agent public non titulaire des établissements de santé. Il cotise à l'assurance vieillesse du régime général et à la retraite complémentaire des agents non titulaires, l'Ircantec, au taux de 2,84 % en tranche A en 2026. Il ne cotise pas à l'Agirc-Arrco, réservée au secteur privé, et la part salariale d'assurance chômage n'existe plus depuis 2018."),
            ("Combien gagne un docteur junior ?",
             f"Le docteur junior, en phase de consolidation du troisième cycle, perçoit {e2(28495.49)} brut par an selon l'annexe XI de l'arrêté du 8 juillet 2022, montant au 1er juillet 2023. Cela représente environ {e2(28495.49 / 12)} brut par mois, auxquels s'ajoutent les gardes et, le cas échéant, des primes propres à cette phase fixées par d'autres textes."),
            ("Le salaire d'un interne est-il imposable ?",
             "Oui. La rémunération, les indemnités de sujétions, les primes et les gardes sont des revenus salariaux imposables. Le prélèvement à la source s'applique dès le premier mois, au taux personnalisé du foyer ou au taux neutre de la grille. Une partie de la CSG reste non déductible, ce qui rend le net imposable un peu supérieur au net versé."),
        ],
        "related": ["salaire-infirmier", "salaire-aide-soignant", "salaire-brut-net-fonction-publique", "taux-prelevement-a-la-source", "majoration-nuit-dimanche", "salaire-net-imposable"],
    }


# ── 5. Aide-soignant (FPH, catégorie B) ──────────────────────────────────────
AS_CN = [373, 375, 377, 388, 401, 414, 429, 444, 461, 485, 517]        # classe normale, IB 389 à 610
AS_CS = [387, 399, 411, 424, 442, 460, 480, 499, 519, 539, 560]        # classe supérieure, IB 433 à 665
AS_CN_IB = [389, 397, 416, 434, 452, 468, 491, 510, 535, 567, 610]
AS_CS_IB = [433, 449, 464, 484, 508, 532, 561, 585, 612, 638, 665]


def page_aide_soignant():
    lignes = []
    for i, (ib, im) in enumerate(zip(AS_CN_IB, AS_CN), 1):
        r = net_fp(im, CTI)
        lignes.append([ech(i), str(ib), str(im), e2(r["traitement"]), e2(r["brut"]), e2(r["net"])])
    l2 = []
    for i, (ib, im) in enumerate(zip(AS_CS_IB, AS_CS), 1):
        r = net_fp(im, CTI)
        l2.append([ech(i), str(ib), str(im), e2(r["traitement"]), e2(r["net"])])
    d = net_fp(AS_CN[0], CTI)
    f = net_fp(AS_CS[-1], CTI)
    options = ([(f"cn{i}", f"Classe normale, {ech(i)} échelon (IM {im})") for i, im in enumerate(AS_CN, 1)]
               + [(f"cs{i}", f"Classe supérieure, {ech(i)} échelon (IM {im})") for i, im in enumerate(AS_CS, 1)])
    corps = f"""
<h2>Grille des aides-soignants de la fonction publique hospitalière</h2>
<p>Depuis la réforme issue du Ségur de la santé, le corps des aides-soignants et des auxiliaires de puériculture de la fonction publique hospitalière est classé en catégorie B. Il compte deux grades, la classe normale et la classe supérieure. Les indices bruts ci-dessous sont ceux du décret n° 2021-1267, modifié par le décret n° 2022-1207 et en vigueur depuis le 1er septembre 2022.</p>
{table(["Classe normale", "Indice brut", "Indice majoré", "Traitement brut", "Brut avec CTI", "Net estimé"], lignes)}
{note("Indices majorés selon le barème du décret n° 82-1105 au 1er janvier 2024. Brut avec le complément de traitement indiciaire de 49 points (" + e2(CTI) + "). Hors primes, indemnités de nuit, de dimanche et jours fériés, et supplément familial.")}
<h2>Classe supérieure</h2>
{table(["Classe supérieure", "Indice brut", "Indice majoré", "Traitement brut", "Net estimé avec CTI"], l2)}
<h2>Aide-soignant débutant</h2>
<p>Un aide-soignant titulaire qui débute au 1er échelon de la classe normale est à l'indice majoré 373 : son traitement indiciaire est de {e2(d['traitement'])} brut par mois, un montant inférieur au SMIC brut de {e2(SMIC_MENSUEL_BRUT)}. Une indemnité différentielle peut alors être due selon les éléments de rémunération pris en compte par l'établissement ; le simulateur ne l'ajoute pas. Avec le complément de traitement indiciaire (CTI) de {e2(CTI)}, versé à tous les agents non médicaux des établissements de santé, la rémunération atteint {e2(d['brut'])} brut, soit environ <strong>{e2(d['net'])} net</strong> avant primes.</p>
<h2>Les primes et indemnités</h2>
<p>Le CTI, créé par le décret n° 2020-1152, vaut 49 points d'indice majoré et suit la valeur du point. Il supporte la retenue pour pension et compte pour la retraite. S'ajoutent selon le poste : la prime spéciale de sujétion, la prime de service, les indemnités de travail de nuit, de dimanche et de jours fériés, et la prime « grand âge » en gériatrie. Leurs montants dépendent du planning et de l'établissement : saisissez-les dans le champ « autres primes » du simulateur à partir de votre bulletin. Elles supportent la CSG et la RAFP, pas la retenue pour pension.</p>
<p>En fin de carrière, au 11e échelon de la classe supérieure, l'indice majoré 560 donne {e2(f['traitement'])} de traitement et environ {e2(f['net'])} net avec le CTI.</p>
"""
    grille = json.dumps({"cn": AS_CN, "cs": AS_CS})
    js = JS_FP + f"""
            var g = {grille}, sel = document.getElementById('w-ech').value;
            var im = g[sel.slice(0, 2)][parseInt(sel.slice(2), 10) - 1];
            var r = netfp(im, {CTI}, v('w-primes'), 0);
            out('r-t', centimes(r.t));
            out('r-brut', centimes(r.brut));
            out('r-net', centimes(r.net));"""
    return {
        "slug": "salaire-aide-soignant",
        "title": "Salaire aide-soignant 2026 : grille FPH, débutant et net",
        "desc": f"Salaire aide-soignant 2026 : grille de la fonction publique hospitalière par échelon, CTI de 241,22 € et net. Un débutant touche {fmt(d['net'])} € net hors primes.",
        "h1": "Salaire d'un aide-soignant en 2026",
        "crumb": "Aide-soignant",
        "widget_titre": "Net d'un aide-soignant titulaire",
        "widget": widget([choix("w-ech", "Grade et échelon", options, "cn1"),
                          champ("w-primes", "Autres primes mensuelles brutes (€)", "0")],
                         [("r-t", "Traitement indiciaire"), ("r-brut", "Brut avec CTI et primes"), ("r-net", "Net mensuel")],
                         "Fonctionnaire hospitalier à temps complet. CTI de 49 points compris ; nuits, dimanches et primes de service à saisir dans « autres primes »."),
        "js": js,
        "citable": f"En 2026, un aide-soignant titulaire de la fonction publique hospitalière débute au 1er échelon de la classe normale, à l'indice majoré 373, soit un traitement de {e2(d['traitement'])} brut par mois avec la valeur du point inchangée depuis juillet 2023. Le complément de traitement indiciaire de 49 points, {e2(CTI)} brut, porte sa rémunération à {e2(d['brut'])} brut, soit environ {e2(d['net'])} net avant primes de nuit, de dimanche ou de service. Le corps est classé en catégorie B depuis la réforme du Ségur de la santé et compte deux grades. Au 11e échelon de la classe supérieure, indice 560, le net atteint environ {e2(f['net'])} par mois avec le CTI. Les retenues d'un fonctionnaire hospitalier sont la pension CNRACL de 11,10 %, la RAFP sur les primes et la CSG-CRDS.",
        "corps": corps,
        "sources": [SRC_AS, SRC_AS_STATUT, SRC_CTI, SRC_FP],
        "releve": RELEVE,
        "note_sources": NOTE_FP,
        "faq": [
            ("Quel est le salaire d'un aide-soignant débutant à l'hôpital ?",
             f"Au 1er échelon de la classe normale, indice majoré 373, le traitement indiciaire est de {e2(d['traitement'])} brut par mois. Avec le complément de traitement indiciaire de {e2(CTI)}, la rémunération atteint {e2(d['brut'])} brut, soit environ {e2(d['net'])} net. Les indemnités de nuit, de dimanche et de jours fériés, ainsi que la prime de service, s'ajoutent selon le planning."),
            ("Les aides-soignants sont-ils en catégorie B ?",
             "Oui. Le décret n° 2021-1257 du 29 septembre 2021 a classé le corps des aides-soignants et des auxiliaires de puériculture de la fonction publique hospitalière en catégorie B. Ce reclassement, issu des accords du Ségur de la santé, s'est accompagné d'une nouvelle grille indiciaire et de deux grades : la classe normale et la classe supérieure."),
            ("Qu'est-ce que le complément de traitement indiciaire ?",
             f"Le CTI est un complément de 49 points d'indice majoré, soit {e2(CTI)} brut par mois en 2026, créé par le décret n° 2020-1152 après le Ségur de la santé. Il est versé aux agents non médicaux des établissements de santé et de nombreux établissements médico-sociaux. Il supporte la retenue pour pension et compte pour le calcul de la retraite."),
            ("Un aide-soignant du privé est-il payé pareil ?",
             "Non. Dans une clinique ou un Ehpad privé, l'aide-soignant est salarié de droit privé : son salaire suit la convention collective de l'établissement et ses cotisations sont celles du régime général et de l'Agirc-Arrco. Le passage du brut au net y retire environ 22 % au lieu de 20 % pour un fonctionnaire hospitalier sans primes."),
            ("Combien gagne un aide-soignant en fin de carrière ?",
             f"Au 11e et dernier échelon de la classe supérieure, à l'indice majoré 560, le traitement indiciaire est de {e2(f['traitement'])} brut par mois. Avec le CTI, la rémunération atteint {e2(f['brut'])} brut et environ {e2(f['net'])} net, hors primes et indemnités liées aux horaires. Le passage en classe supérieure se fait au choix, selon l'ancienneté et la valeur professionnelle."),
            ("Les primes de nuit et de dimanche sont-elles soumises à cotisations ?",
             "Elles supportent la CSG et la CRDS, ainsi que la retraite additionnelle de la fonction publique au taux de 5 %, dans la limite de 20 % du traitement indiciaire. Elles ne supportent pas la retenue pour pension de 11,10 %, qui ne porte que sur le traitement et le CTI. Elles ne comptent donc pas pour la pension de base CNRACL."),
        ],
        "related": ["salaire-infirmier", "salaire-brut-net-fonction-publique", "majoration-nuit-dimanche", "salaire-interne-medecine", "smic-brut-net-2026", "calcul-retraite"],
    }


# ── 6. Infirmier (FPH, catégorie A) ──────────────────────────────────────────
IDE_G1 = [395, 424, 447, 468, 491, 518, 550, 580, 610, 645, 678]       # 1er grade, IB 444 à 821
IDE_G2 = [427, 450, 478, 506, 534, 563, 593, 624, 656, 690, 727]       # 2e grade, IB 489 à 886
IDE_G1_IB = [444, 484, 514, 544, 576, 611, 653, 693, 732, 778, 821]


def page_infirmier():
    lignes = []
    for i, (ib, im) in enumerate(zip(IDE_G1_IB, IDE_G1), 1):
        r = net_fp(im, CTI)
        lignes.append([ech(i), str(ib), str(im), e2(r["traitement"]), e2(r["brut"]), e2(r["net"])])
    l2 = []
    for i, im in enumerate(IDE_G2, 1):
        r = net_fp(im, CTI)
        l2.append([ech(i), str(im), e2(r["traitement"]), e2(r["net"])])
    d = net_fp(IDE_G1[0], CTI)
    d150 = net_fp(IDE_G1[0], CTI, 150)
    f = net_fp(IDE_G1[-1], CTI)
    options = ([(f"g1{i}", f"1er grade, {ech(i)} échelon (IM {im})") for i, im in enumerate(IDE_G1, 1)]
               + [(f"g2{i}", f"2e grade, {ech(i)} échelon (IM {im})") for i, im in enumerate(IDE_G2, 1)])
    corps = f"""
<h2>Grille des infirmiers en soins généraux (FPH)</h2>
<p>Les infirmiers titulaires de la fonction publique hospitalière appartiennent au corps des infirmiers en soins généraux et spécialisés, de catégorie A. Leur grille est fixée par le décret n° 2021-1262 du 29 septembre 2021, entré en vigueur le 1er octobre 2021 et inchangé depuis. Une infirmière diplômée d'État recrutée comme titulaire débute au 1er échelon du premier grade.</p>
{table(["1er grade", "Indice brut", "Indice majoré", "Traitement brut", "Brut avec CTI", "Net estimé"], lignes)}
{note("Indices majorés selon le barème du décret n° 82-1105 au 1er janvier 2024, valeur du point de 5 907,34 € par an. Brut avec le complément de traitement indiciaire de 49 points (" + e2(CTI) + "). Hors primes et indemnités liées aux horaires.")}
<h2>Deuxième grade</h2>
{table(["2e grade", "Indice majoré", "Traitement brut", "Net estimé avec CTI"], l2)}
{note("Le troisième grade regroupe les infirmiers spécialisés (bloc opératoire, anesthésie, puériculture) et culmine à l'indice brut 940.")}
<h2>Infirmière débutante : brut et net</h2>
<p>Au 1er échelon, indice majoré 395, le traitement indiciaire est de {e2(d['traitement'])} brut par mois. Avec le CTI, la rémunération atteint {e2(d['brut'])} brut, soit environ <strong>{e2(d['net'])} net</strong> avant primes. Avec 150 € de primes et indemnités par mois, le net passe à environ {e2(d150['net'])}. Les retenues sont la pension CNRACL de 11,10 % sur le traitement et le CTI, la RAFP de 5 % sur les primes et la CSG-CRDS sur l'ensemble.</p>
<h2>Primes et majorations</h2>
<p>Le net réel d'un infirmier hospitalier dépend beaucoup de son planning : indemnités de travail de nuit, de dimanche et de jours fériés, indemnité de sujétion spéciale, prime de service, primes de spécialité ou de service de soins critiques. Leurs montants varient selon l'établissement et les horaires effectués ; saisissez le total relevé sur votre bulletin dans le champ « autres primes ». Le travail de nuit et de week-end est détaillé sur notre page consacrée aux <a href="/majoration-nuit-dimanche/">majorations de nuit et de dimanche</a>.</p>
<p>En fin de premier grade, au 11e échelon, l'indice majoré 678 donne {e2(f['traitement'])} de traitement et environ {e2(f['net'])} net avec le CTI. Le deuxième grade culmine à l'indice majoré 727.</p>
"""
    grille = json.dumps({"g1": IDE_G1, "g2": IDE_G2})
    js = JS_FP + f"""
            var g = {grille}, sel = document.getElementById('w-ech').value;
            var im = g[sel.slice(0, 2)][parseInt(sel.slice(2), 10) - 1];
            var r = netfp(im, {CTI}, v('w-primes'), 0);
            out('r-t', centimes(r.t));
            out('r-brut', centimes(r.brut));
            out('r-net', centimes(r.net));"""
    return {
        "slug": "salaire-infirmier",
        "title": "Salaire infirmier 2026 : grille FPH, débutant et net mensuel",
        "desc": f"Salaire infirmier 2026 : grille des infirmiers en soins généraux de la FPH, indice 395 au début, CTI de 241,22 €. Une infirmière débutante touche {fmt(d['net'])} € net.",
        "h1": "Salaire d'un infirmier en 2026",
        "crumb": "Infirmier",
        "widget_titre": "Net d'un infirmier titulaire",
        "widget": widget([choix("w-ech", "Grade et échelon", options, "g11"),
                          champ("w-primes", "Autres primes mensuelles brutes (€)", "0")],
                         [("r-t", "Traitement indiciaire"), ("r-brut", "Brut avec CTI et primes"), ("r-net", "Net mensuel")],
                         "Fonctionnaire hospitalier à temps complet. CTI de 49 points compris ; nuits, dimanches, ISS et prime de service à saisir dans « autres primes »."),
        "js": js,
        "citable": f"En 2026, une infirmière en soins généraux titulaire de la fonction publique hospitalière débute au 1er échelon du premier grade, à l'indice majoré 395. Son traitement indiciaire est de {e2(d['traitement'])} brut par mois, la valeur du point étant inchangée depuis juillet 2023. Le complément de traitement indiciaire de 49 points, {e2(CTI)}, porte la rémunération à {e2(d['brut'])} brut, soit environ {e2(d['net'])} net avant primes. Les indemnités de nuit, de dimanche, de jours fériés et la prime de service s'ajoutent selon le planning et l'établissement. Au 11e échelon du premier grade, indice 678, le net atteint environ {e2(f['net'])} par mois avec le CTI. La grille est fixée par le décret n° 2021-1262, en vigueur depuis octobre 2021.",
        "corps": corps,
        "sources": [SRC_IDE, SRC_CTI, SRC_FP, SRC_PENSION],
        "releve": RELEVE,
        "note_sources": NOTE_FP,
        "faq": [
            ("Combien gagne une infirmière débutante à l'hôpital public ?",
             f"Au 1er échelon du premier grade, à l'indice majoré 395, une infirmière titulaire perçoit {e2(d['traitement'])} de traitement brut et {e2(CTI)} de complément de traitement indiciaire, soit {e2(d['brut'])} brut. Son net est d'environ {e2(d['net'])} par mois avant primes de nuit, de dimanche et de service, qui ajoutent souvent plusieurs centaines d'euros selon le planning."),
            ("Combien d'échelons compte la grille des infirmiers ?",
             "Le premier grade du corps des infirmiers en soins généraux et spécialisés compte onze échelons, de l'indice brut 444 à 821, et le deuxième grade onze échelons, de 489 à 886. Le troisième grade, réservé aux infirmiers spécialisés, en compte neuf et culmine à l'indice brut 940. Ces indices sont fixés par le décret n° 2021-1262."),
            ("Le CTI est-il versé aux infirmiers ?",
             f"Oui. Le complément de traitement indiciaire de 49 points d'indice majoré, soit {e2(CTI)} brut par mois en 2026, est versé à tous les agents non médicaux des établissements publics de santé, infirmiers compris. Il supporte la retenue pour pension et compte pour la retraite, comme le traitement indiciaire lui-même."),
            ("Une infirmière en clinique privée gagne-t-elle plus ?",
             "Cela dépend de la convention collective et de l'établissement. Une infirmière salariée d'une clinique relève du régime général et de l'Agirc-Arrco : à brut égal, son net est un peu plus faible que celui d'une fonctionnaire hospitalière sans primes, car ses cotisations salariales sont plus élevées. Les primes et l'évolution de carrière diffèrent aussi."),
            ("Quelles primes s'ajoutent au salaire d'un infirmier ?",
             "Les principales sont l'indemnité de sujétion spéciale, la prime de service, les indemnités de travail de nuit, de dimanche et de jours fériés, et les primes liées à certains services comme les soins critiques. Leurs montants dépendent des horaires effectués et de l'établissement. Elles supportent la CSG, la CRDS et la RAFP, mais pas la retenue pour pension."),
            ("Combien gagne un infirmier en fin de premier grade ?",
             f"Au 11e échelon du premier grade, à l'indice majoré 678, le traitement indiciaire est de {e2(f['traitement'])} brut par mois. Avec le CTI, la rémunération atteint {e2(f['brut'])} brut, soit environ {e2(f['net'])} net hors primes. Le passage au deuxième grade permet de monter jusqu'à l'indice majoré 727."),
        ],
        "related": ["salaire-aide-soignant", "salaire-interne-medecine", "salaire-brut-net-fonction-publique", "majoration-nuit-dimanche", "salaire-enseignant", "taux-prelevement-a-la-source"],
    }


PAGES = [page_assmat, page_ingenieur, page_enseignant, page_interne, page_aide_soignant, page_infirmier]
