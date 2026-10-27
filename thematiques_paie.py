#!/usr/bin/env python3
"""
Pages thématiques « paie » ajoutées le 2026-10-27 : barème kilométrique, plafond de la
Sécurité sociale, prélèvement à la source, réduction Fillon (RGDU), fiche de paie, CESU.

Chiffres relevés le 27 octobre 2026 :
- barème kilométrique : service-public.gouv.fr, actualité A14686 du 9 avril 2026 (revenus 2025,
  barème de l'arrêté du 27 mars 2023 reconduit) et fiche F1989 (abattement 10 % : 509 à 14 555 €) ;
- PASS : arrêté du 22 décembre 2025 (JORFTEXT000053143451), Urssaf, service-public A15386 (PASS 2027) ;
- grilles du taux par défaut : BOFiP BOI-BAREME-000037-20260706 (applicables depuis le 1er mai 2026) ;
- RGDU : urssaf.fr, page mise à jour le 13 juillet 2026 (Tmin 0,0200, Tdelta 0,3781 / 0,3821, P 1,75,
  Smic du 1er janvier 2026, ratios d'imputation) ;
- taux secteur privé : urssaf.fr, page mise à jour le 1er janvier 2026 ;
- particulier employeur : urssaf.fr, actualité du 19 janvier 2026 (AT 2,06 %, vieillesse déplafonnée
  2,11 %), service-public F12384 (déduction de 2 € par heure) et F12 (crédit d'impôt).
"""

from thematiques_commun import *  # noqa: F401,F403
from calcul import estimer_impot_revenu

RELEVE = "27 octobre 2026"

SRC_KM_SP = ("Service-Public.fr, barèmes kilométriques 2026 (9 avril 2026)", "https://www.service-public.gouv.fr/particuliers/actualites/A14686")
SRC_FRAIS_REELS = ("Service-Public.fr, frais professionnels : forfait ou frais réels", "https://www.service-public.gouv.fr/particuliers/vosdroits/F1989")
SRC_KM_ARRETE = ("Légifrance, arrêté du 27 mars 2023 fixant le barème forfaitaire", "https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000047373493")
SRC_PSS_ARRETE = ("Légifrance, arrêté du 22 décembre 2025 fixant le plafond pour 2026", "https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000053143451")
SRC_PSS_2027 = ("Service-Public.fr, plafond annuel de la Sécurité sociale en 2027", "https://www.service-public.gouv.fr/particuliers/actualites/A15386")
SRC_PAS_BOFIP = ("BOFiP, grilles de taux par défaut du prélèvement à la source", "https://bofip.impots.gouv.fr/bofip/11255-PGP.html")
SRC_PAS_SP = ("Service-Public.fr, prélèvement à la source", "https://www.service-public.gouv.fr/particuliers/vosdroits/F34009")
SRC_PAS_IMPOTS = ("impots.gouv.fr, la non-transmission de mon taux à mon employeur", "https://www.impots.gouv.fr/particulier/la-non-transmission-de-mon-taux-mon-employeur")
SRC_PAS_INDIV = ("impots.gouv.fr, taux foyer et taux individualisé", "https://www.impots.gouv.fr/particulier/lindividualisation-des-taux-de-prelevement")
SRC_RGDU_SP = ("Entreprendre.Service-Public.fr, réduction générale dégressive unique", "https://entreprendre.service-public.gouv.fr/vosdroits/F24542")
SRC_BULLETIN = ("Service-Public.fr, bulletin de paie", "https://www.service-public.gouv.fr/particuliers/vosdroits/F559")
SRC_PART_EVOL = ("Urssaf, particuliers employeurs : ce qui a changé au 1er janvier 2026", "https://www.urssaf.fr/accueil/actualites/particuliers-evolutions-012026.html")
SRC_PART_TAUX = ("Urssaf, taux de cotisations des salariés à domicile", "https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-particuliers.html")
SRC_PART_DEDUC = ("Service-Public.fr, exonération et déduction du particulier employeur", "https://www.service-public.gouv.fr/particuliers/vosdroits/F12384")
SRC_CI_DOMICILE = ("Service-Public.fr (fiche F12), aide fiscale aux services à la personne", "https://www.service-public.gouv.fr/particuliers/vosdroits/F12")


# ── Barème kilométrique (revenus 2025, publié le 9 avril 2026) ────────────────

KM_VOITURES = [  # (libellé, (a1), (a2, b2), (a3)) : jusqu'à 5 000 km, 5 001 à 20 000 km, au-delà
    ("3 CV et moins", 0.529, (0.316, 1065), 0.370),
    ("4 CV", 0.606, (0.340, 1330), 0.407),
    ("5 CV", 0.636, (0.357, 1395), 0.427),
    ("6 CV", 0.665, (0.374, 1457), 0.447),
    ("7 CV et plus", 0.697, (0.394, 1515), 0.470),
]
KM_MOTOS = [  # jusqu'à 3 000 km, 3 001 à 6 000 km, au-delà
    ("1 ou 2 CV", 0.395, (0.099, 891), 0.248),
    ("3, 4 ou 5 CV", 0.468, (0.082, 1158), 0.275),
    ("Plus de 5 CV", 0.606, (0.079, 1583), 0.343),
]
KM_CYCLO = ("Cyclomoteur", 0.315, (0.079, 711), 0.198)


def frais_km(ligne, d, seuils):
    _, a1, (a2, b2), a3 = ligne
    if d <= seuils[0]:
        return d * a1
    if d <= seuils[1]:
        return d * a2 + b2
    return d * a3


def fv(x):
    return f"{x:.3f}".replace(".", ",")


def formule(ligne):
    _, a1, (a2, b2), a3 = ligne
    return [f"d × {fv(a1)}", f"(d × {fv(a2)}) + {fmt(b2)}", f"d × {fv(a3)}"]


def page_km():
    v5 = KM_VOITURES[2]
    ex = frais_km(v5, 10000, (5000, 20000))
    ex_elec = ex * 1.2
    abatt = min(max(30000 * 0.10, 509), 14555)
    synth = []
    for lib, *_ in KM_VOITURES:
        ligne = next(l for l in KM_VOITURES if l[0] == lib)
        synth.append([lib] + [e(frais_km(ligne, d, (5000, 20000))) for d in (3000, 8000, 12000, 20000, 25000)])
    corps = f"""
<h2>Le barème des voitures pour les revenus 2025</h2>
<p>La lettre d désigne la distance parcourue à titre professionnel dans l'année, trajets domicile-travail compris. Le résultat est le montant annuel des frais que vous pouvez déduire, en euros.</p>
{table(["Puissance administrative", "Jusqu'à 5 000 km", "De 5 001 à 20 000 km", "Au-delà de 20 000 km"], [[l[0]] + formule(l) for l in KM_VOITURES])}
{note("Véhicules thermiques, hybrides et à hydrogène. Pour une voiture 100 % électrique, le montant obtenu est majoré de 20 %.")}
<h2>Deux-roues motorisés et cyclomoteurs</h2>
{table(["Puissance administrative", "Jusqu'à 3 000 km", "De 3 001 à 6 000 km", "Au-delà de 6 000 km"], [[l[0]] + formule(l) for l in KM_MOTOS] + [["Cyclomoteur (50 cm³ au plus)"] + formule(KM_CYCLO)])}
{note("Barèmes publiés par service-public.gouv.fr le 9 avril 2026 pour la déclaration des revenus 2025. Ils reprennent sans changement ceux de l'arrêté du 27 mars 2023 : c'est la troisième année sans revalorisation.")}
<h2>Montants déductibles selon la distance</h2>
{table(["Voiture", "3 000 km", "8 000 km", "12 000 km", "20 000 km", "25 000 km"], synth)}
{note("Montants annuels arrondis à l'euro, véhicule thermique. Ajoutez 20 % pour un véhicule électrique.")}
<h2>Frais réels ou abattement de 10 % : le bon choix</h2>
<p>Par défaut, l'administration retire 10 % de vos salaires pour frais professionnels, au minimum 509 € et au maximum 14 555 € par personne pour les revenus 2025. Opter pour les frais réels n'a d'intérêt que si le total de vos frais justifiés dépasse ce forfait. Avec un salaire net imposable de {e(30000)} par an, l'abattement vaut {e(abatt)} ; une voiture de 5 CV qui parcourt {fmt(10000)} km professionnels donne {e(ex)} de frais, soit {e(ex - abatt)} de revenu imposable en moins. Les frais de repas, de péage et de stationnement s'ajoutent sur justificatifs, mais pas les intérêts d'un crédit auto, déjà couverts par le barème.</p>
<p>Le barème couvre la dépréciation du véhicule, l'entretien, les pneus, le carburant et l'assurance. La distance domicile-travail n'est retenue en principe que dans la limite de 40 km par trajet ; au-delà, il faut justifier de circonstances particulières (emploi précaire, conjoint travaillant ailleurs, contraintes familiales). Le barème s'applique au plus à la puissance de 7 CV : une voiture de 9 CV se calcule sur la ligne « 7 CV et plus ».</p>
<h2>Indemnités kilométriques versées par l'employeur</h2>
<p>Le même barème sert à l'employeur qui rembourse les déplacements effectués avec le véhicule personnel du salarié : dans ses limites, l'indemnité est exonérée de cotisations sociales et d'impôt sur le revenu. Un salarié remboursé ainsi ne peut pas déduire une seconde fois les mêmes kilomètres en frais réels ; il doit alors ajouter l'indemnité à son revenu déclaré s'il opte pour les frais réels.</p>
"""
    js = """
            var cat = document.getElementById('w-cat').value, d = v('w-km'), elec = document.getElementById('w-elec').value === 'oui';
            var B = {
                v3: [0.529, 0.316, 1065, 0.370], v4: [0.606, 0.340, 1330, 0.407], v5: [0.636, 0.357, 1395, 0.427],
                v6: [0.665, 0.374, 1457, 0.447], v7: [0.697, 0.394, 1515, 0.470],
                m2: [0.395, 0.099, 891, 0.248], m5: [0.468, 0.082, 1158, 0.275], m6: [0.606, 0.079, 1583, 0.343],
                cy: [0.315, 0.079, 711, 0.198]
            }[cat];
            var s1 = cat.charAt(0) === 'v' ? 5000 : 3000, s2 = cat.charAt(0) === 'v' ? 20000 : 6000;
            var f = d <= s1 ? d * B[0] : (d <= s2 ? d * B[1] + B[2] : d * B[3]);
            if (elec) f = f * 1.2;
            var sal = v('w-sal'), ab = Math.min(Math.max(sal * 0.1, 509), 14555);
            out('r-frais', euros(f));
            out('r-km', d > 0 ? centimes(f / d) : '–');
            out('r-abatt', euros(ab));
            out('r-gain', f > ab ? euros(f - ab) + ' de plus' : 'Abattement plus favorable');"""
    cats = [("v3", "Voiture 3 CV et moins"), ("v4", "Voiture 4 CV"), ("v5", "Voiture 5 CV"), ("v6", "Voiture 6 CV"),
            ("v7", "Voiture 7 CV et plus"), ("m2", "Moto 1 ou 2 CV"), ("m5", "Moto 3 à 5 CV"), ("m6", "Moto plus de 5 CV"),
            ("cy", "Cyclomoteur")]
    return {
        "slug": "bareme-kilometrique-2026",
        "title": "Barème kilométrique 2026 : tableau officiel et frais réels",
        "desc": "Barème kilométrique 2026 (revenus 2025) : formules par CV, motos, électrique +20 %. Une voiture de 5 CV à 10 000 km donne 4 965 € de frais déductibles.",
        "h1": "Barème kilométrique 2026",
        "crumb": "Barème kilométrique 2026",
        "widget_titre": "Frais kilométriques déductibles",
        "widget": widget([choix("w-cat", "Véhicule", cats, "v5"),
                          champ("w-km", "Kilomètres professionnels dans l'année", "10000"),
                          choix("w-elec", "Véhicule 100 % électrique", [("non", "Non"), ("oui", "Oui, +20 %")], "non"),
                          champ("w-sal", "Salaire net imposable annuel (€)", "30000")],
                         [("r-frais", "Frais déductibles"), ("r-km", "Par kilomètre"), ("r-abatt", "Abattement de 10 %"), ("r-gain", "Frais réels")],
                         "Comparaison avec l'abattement de 10 % sur les seuls frais de véhicule ; ajoutez vos autres frais justifiés (repas, péages, parking)."),
        "js": js,
        "citable": f"Le barème kilométrique 2026 est celui qui sert à déclarer les revenus de 2025, au printemps 2026. Publié par service-public.gouv.fr le 9 avril 2026, il n'a pas été revalorisé et reprend les montants de l'arrêté du 27 mars 2023. Pour une voiture de 5 CV, les frais se calculent ainsi : d × 0,636 jusqu'à 5 000 km, (d × 0,357) + 1 395 de 5 001 à 20 000 km, d × 0,427 au-delà. Une 5 CV qui parcourt {fmt(10000)} km professionnels dans l'année ouvre donc droit à {e(ex)} de frais déductibles, et {e(ex_elec)} si elle est 100 % électrique, grâce à la majoration de 20 %. Ces frais ne remplacent l'abattement forfaitaire de 10 %, compris entre 509 € et 14 555 €, que si vous optez pour les frais réels et que leur total le dépasse.",
        "corps": corps,
        "sources": [SRC_KM_SP, SRC_FRAIS_REELS, SRC_KM_ARRETE],
        "releve": RELEVE,
        "note_sources": "Le barème couvre les frais de véhicule ; les autres frais réels (repas, péages, stationnement) s'ajoutent sur justificatifs.",
        "faq": [
            ("Le barème kilométrique a-t-il augmenté en 2026 ?",
             "Non. Le barème publié le 9 avril 2026 pour la déclaration des revenus 2025 reprend à l'identique celui de 2023, déjà reconduit en 2024 et en 2025. Sa dernière hausse, de 5,4 %, remonte à l'arrêté du 27 mars 2023. Les montants par cheval fiscal, les tranches de distance et la majoration de 20 % pour les véhicules électriques restent donc ceux que vous connaissiez."),
            ("Quelle année de revenus couvre le barème kilométrique 2026 ?",
             "Il s'applique aux kilomètres parcourus en 2025, que vous déclarez au printemps 2026 si vous optez pour les frais réels. Il sert aussi aux employeurs pour exonérer les indemnités kilométriques versées en 2026. Les déplacements faits en 2026 seront déclarés en 2027, avec le barème que l'administration publiera à ce moment-là."),
            ("Comment calculer ses frais kilométriques avec une voiture électrique ?",
             f"Appliquez la formule de la puissance administrative du véhicule, puis multipliez le résultat par 1,2. Une voiture électrique de 5 CV qui parcourt {fmt(10000)} km professionnels donne {e(ex)} avec le barème ordinaire, puis {e(ex_elec)} après la majoration de 20 %. Les hybrides rechargeables n'y ont pas droit : seule la motorisation 100 % électrique ouvre la majoration."),
            ("Faut-il compter l'aller et le retour domicile-travail ?",
             "Oui, chaque jour travaillé compte deux trajets. Un salarié qui habite à 20 km de son travail et vient 210 jours dans l'année parcourt 8 400 km. La distance est retenue en principe dans la limite de 40 km par trajet ; au-delà, l'administration demande de justifier l'éloignement, par exemple un emploi précaire ou le lieu de travail du conjoint."),
            ("Les frais réels sont-ils plus intéressants que l'abattement de 10 % ?",
             f"Seulement si leur total dépasse l'abattement automatique, qui vaut 10 % du salaire, entre 509 € et 14 555 €. Pour {e(30000)} de salaire imposable, l'abattement est de {e(abatt)} : une 5 CV doit parcourir environ 5 700 km professionnels pour le dépasser. Les repas pris sur le lieu de travail, les péages et le stationnement s'ajoutent et font souvent pencher la balance."),
            ("Peut-on utiliser le barème pour une voiture de plus de 7 CV ?",
             "Oui, mais le calcul s'arrête à la ligne « 7 CV et plus » : une voiture de 9 ou 11 CV est traitée comme une 7 CV. Le législateur a plafonné la puissance prise en compte pour ne pas avantager les véhicules les plus puissants. Si vos dépenses réelles sont plus élevées, vous pouvez renoncer au barème et déclarer les frais effectivement payés, factures à l'appui."),
        ],
        "related": ["salaire-net-imposable", "salaire-brut-net-annuel", "taux-prelevement-a-la-source", "plafond-securite-sociale-2026", "simulateur-fiche-de-paie", "cout-employeur"],
    }


# ── Plafond de la Sécurité sociale ────────────────────────────────────────────

PASS_2026 = [("Année", 48060), ("Trimestre", 12015), ("Mois", 4005), ("Quinzaine", 2003),
             ("Semaine", 924), ("Jour", 220), ("Heure (durée inférieure à 5 heures)", 30)]
PASS_HISTO = [(2024, 46368, 3864), (2025, 47100, 3925), (2026, 48060, 4005)]


def tranches(brut, temps=1.0):
    p = PSS_MENSUEL * temps
    return min(brut, p), max(0, min(brut, 8 * p) - p), p


def page_pss():
    exemples = []
    for b in (2000, 3500, 4005, 5000, 7000, 10000):
        t1, t2, _ = tranches(b)
        exemples.append([e(b), e(t1), e(t2), pct(b * 12 / PSS_ANNUEL * 100, 0).replace(" %", " %")])
    t1, t2, _ = tranches(5000)
    corps = f"""
<h2>Le plafond 2026 selon la périodicité de paie</h2>
{table(["Périodicité", "Plafond 2026"], [[lib, e(v)] for lib, v in PASS_2026])}
{note("Arrêté du 22 décembre 2025, publié au Journal officiel le 23 décembre 2025 : valeur mensuelle 4 005 €, valeur journalière 220 €, pour les périodes d'emploi courant à compter du 1er janvier 2026. Les autres valeurs sont celles publiées par l'Urssaf. Mayotte a un plafond propre, plus bas.")}
<h2>Une hausse de 2 % en 2026, de 1,74 % annoncée pour 2027</h2>
{table(["Année", "Plafond annuel", "Plafond mensuel"], [[str(a), e(an), e(m)] for a, an, m in PASS_HISTO] + [["2027 (annoncé)", e(48900), e(4075)]])}
{note("Le plafond 2027 a été annoncé le 19 octobre 2026 par le Bulletin officiel de la Sécurité sociale ; l'arrêté qui le confirme doit paraître avant la fin de l'année 2026.")}
<p>Un salaire de décembre 2025 versé en janvier 2026 reste calculé avec le plafond de 2025, {e(3925)} par mois : c'est la période d'emploi qui compte, pas la date de paiement.</p>
<h2>Tranche 1, tranche 2 : comment le plafond découpe un salaire</h2>
<p>Plusieurs cotisations ne portent que sur la partie du salaire inférieure au plafond, la tranche 1 : vieillesse plafonnée, retraite complémentaire Agirc-Arrco au taux de la première tranche, Fnal des petites entreprises. La tranche 2 va du plafond à huit fois le plafond, soit de {e(PSS_MENSUEL)} à {e(8 * PSS_MENSUEL)} par mois, avec des taux Agirc-Arrco plus élevés. Pour {e(5000)} brut, la tranche 1 vaut {e(t1)} et la tranche 2 {e(t2)}.</p>
{table(["Salaire brut mensuel", "Tranche 1", "Tranche 2", "En % du plafond"], exemples)}
{note("Salarié à temps plein présent tout le mois. À temps partiel, le plafond est réduit au prorata de la durée du travail.")}
<h2>Les montants qui dépendent du plafond en 2026</h2>
<ul>
<li>Assurance chômage et AGS : cotisations dues jusqu'à 4 plafonds, soit {e(4 * PSS_ANNUEL)} par an.</li>
<li>Indemnités de rupture : exonérées de cotisations dans la limite de 2 plafonds, {e(2 * PSS_ANNUEL)}, et totalement assujetties au-delà de 10 plafonds.</li>
<li>Gratification de stage : minimum de 15 % du plafond horaire, soit 4,50 € par heure.</li>
<li>Retraite de base : le salaire annuel moyen ne retient chaque année que la part sous le plafond.</li>
<li>Indemnités journalières de maternité et de paternité : calculées sur les salaires retenus dans la limite du plafond mensuel.</li>
</ul>
<p>Le <a href="/cout-employeur/">coût employeur</a> et le <a href="/salaire-brut-net-cadre/">salaire net d'un cadre</a> changent de pente au passage du plafond : au-delà, les cotisations de vieillesse plafonnée s'arrêtent mais la retraite complémentaire de tranche 2 prend le relais.</p>
"""
    js = """
            var b = v('w-brut'), t = v('w-temps') / 100;
            var p = 4005 * (t > 0 ? t : 1);
            var t1 = Math.min(b, p), t2 = Math.max(0, Math.min(b, 8 * p) - p);
            out('r-plafond', euros(p));
            out('r-t1', euros(t1));
            out('r-t2', euros(t2));
            out('r-part', (b / p * 100).toLocaleString('fr-FR', { maximumFractionDigits: 0 }) + ' %');"""
    return {
        "slug": "plafond-securite-sociale-2026",
        "title": "Plafond Sécurité sociale 2026 : PASS 48 060 €, PMSS 4 005 €",
        "desc": "Plafond de la Sécurité sociale 2026 : 48 060 € par an, 4 005 € par mois, 220 € par jour. Calculez les tranches 1 et 2 de votre salaire et les usages du plafond.",
        "h1": "Plafond de la Sécurité sociale 2026",
        "crumb": "Plafond Sécurité sociale 2026",
        "widget_titre": "Tranches de votre salaire",
        "widget": widget([champ("w-brut", "Salaire brut mensuel (€)", "5000"),
                          champ("w-temps", "Temps de travail (% d'un temps plein)", "100")],
                         [("r-plafond", "Plafond du mois"), ("r-t1", "Tranche 1"), ("r-t2", "Tranche 2"), ("r-part", "Salaire / plafond")]),
        "js": js,
        "citable": f"Le plafond annuel de la Sécurité sociale (PASS) s'élève à 48 060 € en 2026, soit 4 005 € par mois, 924 € par semaine, 220 € par jour et 30 € par heure pour une durée de travail inférieure à cinq heures. Fixé par l'arrêté du 22 décembre 2025, il progresse de 2 % par rapport à 2025, où il valait 47 100 € par an et 3 925 € par mois. Il sert à découper le salaire en tranches : la tranche 1 va jusqu'au plafond, la tranche 2 de 1 à 8 plafonds, et plusieurs cotisations de retraite ne s'appliquent qu'en deçà. Un salaire de {e(5000)} brut se répartit ainsi en {e(t1)} de tranche 1 et {e(t2)} de tranche 2. Pour 2027, le Bulletin officiel de la Sécurité sociale annonce 48 900 € par an et 4 075 € par mois.",
        "corps": corps,
        "sources": [SRC_PSS, SRC_PSS_ARRETE, SRC_PSS_2027, SRC_TAUX],
        "releve": RELEVE,
        "note_sources": "Valeurs applicables en métropole et dans les départements d'outre-mer hors Mayotte.",
        "faq": [
            ("Quel est le montant du PASS en 2026 ?",
             "Le plafond annuel de la Sécurité sociale vaut 48 060 € pour 2026, contre 47 100 € en 2025. Le plafond mensuel, celui qu'on lit sur un bulletin de paie, est de 4 005 €. Ces valeurs, fixées par l'arrêté du 22 décembre 2025, s'appliquent aux cotisations dues sur les périodes d'emploi du 1er janvier au 31 décembre 2026."),
            ("Pourquoi la quinzaine vaut-elle 2 003 € et non 2 002,50 € ?",
             "Les plafonds autres que l'annuel sont arrondis à l'euro. La moitié exacte du plafond mensuel donnerait 2 002,50 € ; l'arrondi conduit à 2 003 €. Le même principe explique le plafond hebdomadaire de 924 €, alors que 48 060 € divisés par 52 semaines donnent 924,23 €. Les logiciels de paie appliquent directement ces valeurs arrondies."),
            ("Comment le plafond est-il calculé pour un salarié à temps partiel ?",
             f"Il est réduit au prorata de la durée prévue au contrat. Un salarié à 80 % d'un temps plein a un plafond mensuel de {e(PSS_MENSUEL * 0.8)}. Sur un salaire de {e(3500)} brut à 80 %, la tranche 1 s'arrête donc à {e(PSS_MENSUEL * 0.8)} et le reste, {e(3500 - PSS_MENSUEL * 0.8)}, relève de la tranche 2. Un accord peut prévoir de cotiser sur un plafond de temps plein pour la retraite."),
            ("Quel plafond appliquer à un salaire de décembre payé en janvier ?",
             "Celui de l'année pendant laquelle le travail a été effectué. Un salaire de décembre 2025 versé le 5 janvier 2026 reste soumis au plafond de 2025, soit 3 925 € par mois. Inversement, une prime versée en 2026 au titre d'une période de 2026 suit le plafond de 4 005 €, et se rattache au mois de son versement."),
            ("À quoi sert le plafond de la Sécurité sociale pour la retraite ?",
             "Le régime général ne retient chaque année que la part du salaire inférieure au plafond pour calculer le salaire annuel moyen des 25 meilleures années. La retraite de base est donc limitée : à taux plein, elle ne dépasse pas la moitié du plafond. Au-delà, ce sont les points Agirc-Arrco de la tranche 2, cotisés jusqu'à huit plafonds, qui complètent la pension."),
            ("Quel sera le plafond de la Sécurité sociale en 2027 ?",
             "Le Bulletin officiel de la Sécurité sociale a annoncé le 19 octobre 2026 un plafond de 48 900 € par an pour 2027, soit 4 075 € par mois et 224 € par jour, en hausse de 1,74 %. Ces montants doivent encore être confirmés par un arrêté publié avant la fin de 2026. Ils s'appliqueront aux salaires des périodes d'emploi à partir de janvier 2027."),
        ],
        "related": ["salaire-brut-net-cadre", "cout-employeur", "simulateur-fiche-de-paie", "reduction-fillon-2026", "salaire-brut-net-stage", "calcul-retraite"],
    }


# ── Prélèvement à la source : grilles du taux par défaut (depuis le 1er mai 2026) ─

GRILLE_METRO = [(1635, 0), (1698, 0.5), (1807, 1.3), (1928, 2.1), (2060, 2.9), (2170, 3.5), (2315, 4.1),
                (2738, 5.3), (3135, 7.5), (3571, 9.9), (4019, 11.9), (4690, 13.8), (5624, 15.8), (7037, 17.9),
                (8789, 20), (12200, 24), (16523, 28), (25937, 33), (55558, 38), (None, 43)]
GRILLE_GRM = [(1875, 0), (1989, 0.5), (2191, 1.3), (2392, 2.1), (2642, 2.9), (2786, 3.5), (2881, 4.1),
              (3170, 5.3), (3920, 7.5), (5016, 9.9), (5697, 11.9), (6599, 13.8), (7907, 15.8), (8789, 17.9),
              (9989, 20), (13738, 24), (18253, 28), (27858, 33), (60893, 38), (None, 43)]
GRILLE_GM = [(2008, 0), (2170, 0.5), (2420, 1.3), (2728, 2.1), (2833, 2.9), (2930, 3.5), (3026, 4.1),
             (3362, 5.3), (4639, 7.5), (6005, 9.9), (6772, 11.9), (7858, 13.8), (8644, 15.8), (9577, 17.9),
             (11115, 20), (14953, 24), (19020, 28), (30482, 33), (64341, 38), (None, 43)]


def taux_neutre(base, grille=GRILLE_METRO):
    for borne, t in grille:
        if borne is None or base < borne:
            return t
    return 43


def lignes_grille(grille):
    out_, bas = [], 0
    for borne, t in grille:
        if bas == 0:
            lib = f"Moins de {fmt(borne)} €"
        elif borne is None:
            lib = f"{fmt(bas)} € ou plus"
        else:
            lib = f"De {fmt(bas)} à moins de {fmt(borne)} €"
        out_.append([lib, pct(t, 1).replace(",0 %", " %")])
        bas = borne
    return out_


def js_grille(grille):
    return "[" + ",".join(f"[{b if b is not None else 1e12},{t}]" for b, t in grille) + "]"


def page_pas():
    exemples = []
    for b in (1700, 2000, 2500, 3000, 4000, 6000):
        exemples.append([e(b), pct(taux_neutre(b), 1).replace(",0 %", " %"), e2(b * taux_neutre(b) / 100)])
    t2500 = taux_neutre(2500)
    corps = f"""
<h2>La grille du taux non personnalisé en métropole</h2>
<p>Le taux par défaut, dit aussi taux neutre ou non personnalisé, se lit dans une grille selon la base mensuelle de prélèvement, c'est-à-dire le salaire net imposable du mois. Il ne tient compte ni de la situation de famille ni des autres revenus du foyer : il est calé sur un célibataire sans enfant.</p>
{table(["Base mensuelle de prélèvement", "Taux"], lignes_grille(GRILLE_METRO))}
{note("Grille applicable aux revenus perçus depuis le 1er mai 2026 en métropole et pour les non-résidents (BOFiP, BOI-BAREME-000037). Les limites ont été relevées de 0,9 % au 1er mai 2026, en application de l'article 4 de la loi de finances pour 2026.")}
<h2>Exemples de prélèvement au taux neutre</h2>
{table(["Net imposable mensuel", "Taux neutre", "Prélèvement du mois"], exemples)}
<h2>Guadeloupe, Martinique, La Réunion, Guyane et Mayotte</h2>
<p>Les départements d'outre-mer ont leurs propres grilles, avec des seuils plus élevés, pour tenir compte de la réfaction de l'impôt de 30 % ou 40 % qui y est appliquée.</p>
{table(["Base mensuelle (Guadeloupe, Martinique, La Réunion)", "Taux"], lignes_grille(GRILLE_GRM))}
{table(["Base mensuelle (Guyane, Mayotte)", "Taux"], lignes_grille(GRILLE_GM))}
<h2>Taux personnalisé, taux individualisé, taux neutre</h2>
<p>Le taux personnalisé est calculé par l'administration à partir de votre dernière déclaration : l'impôt afférent aux revenus soumis au prélèvement, divisé par ces mêmes revenus. Il est transmis à l'employeur, qui l'applique chaque mois au net imposable. Depuis septembre 2025, les couples mariés ou pacsés reçoivent par défaut un taux individualisé, calculé sur les revenus de chacun ; le taux du foyer reste disponible sur option. Le taux neutre ne s'applique que lorsque l'employeur n'a pas reçu de taux, au début d'un premier emploi par exemple, ou lorsque le salarié refuse de lui transmettre le sien.</p>
<p>Refuser de transmettre son taux ne change pas l'impôt dû. Si le taux neutre prélève moins que le taux personnalisé, la différence doit être versée chaque mois à l'administration fiscale, au plus tard le dernier jour du mois suivant ; s'il prélève plus, l'excédent est remboursé après la déclaration de l'année suivante. Pour estimer l'impôt annuel complet, utilisez le <a href="/simulateur-impot-sur-le-revenu/">simulateur d'impôt sur le revenu</a>.</p>
"""
    js = f"""
            var G = {{ metro: {js_grille(GRILLE_METRO)}, grm: {js_grille(GRILLE_GRM)}, gm: {js_grille(GRILLE_GM)} }};
            var base = v('w-base'), zone = document.getElementById('w-zone').value, parts = parseFloat(document.getElementById('w-parts').value);
            var g = G[zone], tn = 43;
            for (var i = 0; i < g.length; i++) {{ if (base < g[i][0]) {{ tn = g[i][1]; break; }} }}
            var annuel = base * 12, abatt = Math.min(Math.max(annuel * 0.1, 509), 14555);
            var ir = estimerImpotRevenu(annuel - abatt, parts, parts >= 2 ? 2 : 1);
            var tp = annuel > 0 ? Math.round(ir / annuel * 1000) / 10 : 0;
            out('r-tn', tn.toLocaleString('fr-FR') + ' %');
            out('r-pn', centimes(base * tn / 100));
            out('r-tp', tp.toLocaleString('fr-FR') + ' %');
            out('r-pp', centimes(base * tp / 100));"""
    return {
        "slug": "taux-prelevement-a-la-source",
        "title": "Prélèvement à la source 2026 : taux neutre et personnalisé",
        "desc": "Prélèvement à la source 2026 : grille du taux neutre depuis le 1er mai, de 0 % sous 1 635 € à 43 %. Comparez-la avec votre taux personnalisé, estimé en direct.",
        "h1": "Taux de prélèvement à la source 2026",
        "crumb": "Prélèvement à la source",
        "widget_titre": "Taux neutre ou taux personnalisé",
        "widget": widget([champ("w-base", "Salaire net imposable mensuel (€)", "2500"),
                          choix("w-zone", "Lieu de résidence", [("metro", "Métropole"), ("grm", "Guadeloupe, Martinique, La Réunion"), ("gm", "Guyane, Mayotte")], "metro"),
                          choix("w-parts", "Parts fiscales", [("1", "1 part"), ("1.5", "1,5 part"), ("2", "2 parts"), ("2.5", "2,5 parts"), ("3", "3 parts")], "1")],
                         [("r-tn", "Taux neutre"), ("r-pn", "Prélevé au taux neutre"), ("r-tp", "Taux personnalisé estimé"), ("r-pp", "Prélevé au taux personnalisé")],
                         "Taux personnalisé estimé pour un foyer dont le salaire est le seul revenu, barème 2026 de métropole ; l'administration calcule le vôtre à partir de votre déclaration."),
        "js": js,
        "citable": f"Le taux de prélèvement à la source appliqué par l'employeur est, en principe, le taux personnalisé calculé par l'administration fiscale à partir de la dernière déclaration de revenus. À défaut, l'employeur applique un taux non personnalisé, lu dans une grille officielle selon le salaire net imposable du mois. Depuis le 1er mai 2026, la grille de métropole commence à 0 % pour une base inférieure à 1 635 € et monte jusqu'à 43 % au-delà de 55 558 € par mois ; un salarié payé {e(2500)} net imposable se voit appliquer {pct(t2500, 1)}, soit {e2(2500 * t2500 / 100)} par mois. Les départements d'outre-mer ont des grilles propres aux seuils plus élevés. Le taux neutre ne change pas l'impôt final : l'écart avec le taux personnalisé se régularise par des versements mensuels complémentaires ou par un remboursement l'année suivante.",
        "corps": corps,
        "sources": [SRC_PAS_BOFIP, SRC_PAS_SP, SRC_PAS_IMPOTS, SRC_PAS_INDIV],
        "releve": RELEVE,
        "note_sources": "Le taux personnalisé affiché est une estimation pour un foyer sans autre revenu ; seul le taux transmis par l'administration fait foi.",
        "faq": [
            ("À partir de quel salaire paie-t-on le prélèvement à la source au taux neutre ?",
             "En métropole, la grille applicable depuis le 1er mai 2026 donne un taux de 0 % tant que le net imposable mensuel reste inférieur à 1 635 €. Le taux passe à 0,5 % de 1 635 € à 1 698 €, puis 1,3 % jusqu'à 1 807 €. En Guadeloupe, à la Martinique et à La Réunion, le seuil du taux nul est de 1 875 € ; en Guyane et à Mayotte, de 2 008 €."),
            ("Le taux neutre fait-il payer plus d'impôt ?",
             "Non, l'impôt final est le même. Le taux neutre ne fait que changer le rythme des paiements. Si votre taux personnalisé est plus élevé, vous devez verser vous-même la différence chaque mois à l'administration, sous peine de majoration. S'il est plus bas, comme souvent pour une famille avec enfants, vous avancez trop d'impôt et récupérez l'excédent l'été suivant."),
            ("Qu'est-ce que le taux individualisé appliqué aux couples ?",
             "Depuis septembre 2025, chaque membre d'un couple marié ou pacsé reçoit par défaut un taux calculé sur ses propres revenus, au lieu d'un taux commun au foyer. Celui qui gagne le moins voit son prélèvement baisser, l'autre le voit monter, mais l'impôt total du foyer ne change pas. Le taux du foyer reste disponible sur option dans l'espace particulier d'impots.gouv.fr."),
            ("Pourquoi les grilles du taux neutre ont-elles changé le 1er mai 2026 ?",
             "La loi de finances pour 2026, promulguée en février, a relevé de 0,9 % les limites des tranches du barème et des grilles du taux par défaut. Les logiciels de paie ne pouvant pas appliquer ce changement en janvier, l'administration l'a fait entrer en vigueur sur les revenus versés à partir du 1er mai 2026. Les grilles de janvier à avril gardaient les seuils précédents."),
            ("Comment calculer son taux personnalisé de prélèvement ?",
             f"Divisez l'impôt dû sur les revenus soumis au prélèvement par le montant net imposable de ces revenus, avant l'abattement de 10 %. Un célibataire qui gagne {e(2500)} net imposable par mois sans autre revenu paie environ {e(estimer_impot_revenu(30000 - 3000, 1, 1))} d'impôt par an, soit un taux proche de {pct(estimer_impot_revenu(30000 - 3000, 1, 1) / 300, 1)}. L'administration fait ce calcul pour vous après chaque déclaration."),
            ("Peut-on demander à son employeur d'appliquer le taux neutre ?",
             "Oui. Dans votre espace particulier, l'option de non-transmission du taux demande à l'administration de ne pas communiquer votre taux personnalisé. L'employeur applique alors la grille officielle. Le choix est utile pour ne pas révéler des revenus du conjoint ou des revenus fonciers, mais il impose de verser chaque mois le complément éventuel, calculé et prélevé sur votre compte."),
        ],
        "related": ["salaire-net-imposable", "simulateur-fiche-de-paie", "bareme-kilometrique-2026", "salaire-brut-net-annuel", "salaire-moyen-france", "plafond-securite-sociale-2026"],
    }


# ── Réduction générale dégressive unique (ex-réduction Fillon) ────────────────

SMIC_REF_RGDU = SMIC_MENSUEL_JANVIER  # 1 823,03 € : Smic du 1er janvier 2026, retenu toute l'année


def coef_rgdu(brut, grande=False):
    tdelta = 0.3821 if grande else 0.3781
    seuil = 3 * SMIC_REF_RGDU
    if brut <= 0 or brut >= seuil:
        return 0.0
    return min(0.02 + tdelta, 0.02 + tdelta * (0.5 * (seuil / brut - 1)) ** 1.75)


def page_rgdu():
    bruts = (SMIC_MENSUEL_JANVIER, SMIC_MENSUEL_BRUT, 2000, 2500, 3000, 3500, 4000, 5000, 5400)
    lignes = []
    for b in bruts:
        c1, c2 = coef_rgdu(b), coef_rgdu(b, True)
        lignes.append([e2(b), f"{c1:.4f}".replace(".", ","), e(b * c1),
                       f"{c2:.4f}".replace(".", ","), e(b * c2)])
    c2000 = coef_rgdu(2000)
    c2000g = coef_rgdu(2000, True)
    cs = coef_rgdu(SMIC_MENSUEL_BRUT)
    corps = f"""
<h2>La formule 2026</h2>
<p>La réduction est égale à la rémunération annuelle brute multipliée par un coefficient. En métropole et dans les départements d'outre-mer hors Mayotte, ce coefficient vaut :</p>
<p><strong>Tmin + Tdelta × [½ × (3 × Smic annuel ÷ rémunération annuelle brute − 1)]<sup>1,75</sup></strong></p>
{table(["Paramètre", "Moins de 50 salariés", "50 salariés et plus"], [
    ["Tmin", "0,0200", "0,0200"],
    ["Tdelta", "0,3781", "0,3821"],
    ["Puissance P", "1,75", "1,75"],
    ["Coefficient maximal", "0,3981", "0,4021"],
])}
{note("Paramètres publiés par l'Urssaf (page mise à jour le 13 juillet 2026). L'écart entre les deux colonnes vient du Fnal : 0,10 % sous 50 salariés, 0,50 % au-delà.")}
<p>Le Smic retenu est celui du <strong>1er janvier 2026, {e2(SMIC_REF_RGDU)} par mois</strong> pour 35 heures, même après la revalorisation du 1er juin. L'Urssaf admet l'écriture équivalente 2,9293 × Smic du 1er juin. Conséquence : la réduction s'éteint à {e2(3 * SMIC_REF_RGDU)} brut par mois, soit {e(3 * SMIC_REF_RGDU * 12)} par an, et un salarié payé au Smic de juin, {e2(SMIC_MENSUEL_BRUT)}, n'atteint plus tout à fait le coefficient maximal : {f"{cs:.4f}".replace(".", ",")} au lieu de 0,3981.</p>
<h2>Coefficient et réduction selon le salaire</h2>
{table(["Brut mensuel", "Coef. < 50", "Réduction < 50", "Coef. 50 et +", "Réduction 50 et +"], lignes)}
{note("Calcul mensuel pour un temps plein sans heures supplémentaires. En paie, le calcul est annuel et régularisé chaque mois ; le Smic de la formule est proratisé pour un temps partiel ou une absence, et majoré des heures supplémentaires.")}
<h2>Ce qui a changé par rapport à la réduction Fillon</h2>
<p>Jusqu'en 2025, la réduction Fillon s'arrêtait à 1,6 Smic, et deux autres allègements la complétaient : le taux réduit de la cotisation maladie (7 % au lieu de 13 %) et celui des allocations familiales (3,45 % au lieu de 5,25 %). Depuis le 1er janvier 2026, la réduction générale dégressive unique remplace les trois. Elle descend plus doucement et s'étend jusqu'à 3 Smic, avec un plancher de 2 % (le Tmin) qui subsiste jusqu'au seuil : un salaire juste sous 3 Smic garde 2 % de réduction, puis tombe à zéro au-delà.</p>
<h2>Où la réduction s'impute</h2>
<p>Le montant se répartit entre l'Urssaf et la caisse de retraite complémentaire. Sous 50 salariés, la part Urssaf vaut réduction × 0,3380 ÷ 0,3981 et la part Agirc-Arrco réduction × 0,0601 ÷ 0,3981 ; à partir de 50 salariés, 0,3420 ÷ 0,4021 et 0,0601 ÷ 0,4021. La réduction porte sur les cotisations patronales maladie, vieillesse, allocations familiales, accidents du travail dans la limite de la part mutualisée, Fnal, contribution solidarité autonomie, assurance chômage et retraite complémentaire légale. Pour voir l'effet sur le coût total d'un salarié, la page <a href="/cout-employeur/">coût employeur</a> détaille chaque cotisation.</p>
"""
    js = f"""
            var b = v('w-brut'), grande = document.getElementById('w-effectif').value === '50';
            var td = grande ? 0.3821 : 0.3781, s = 3 * {SMIC_REF_RGDU}, c = 0;
            if (b > 0 && b < s) {{ c = Math.min(0.02 + td, 0.02 + td * Math.pow(0.5 * (s / b - 1), 1.75)); }}
            var r = b * c, ur = grande ? 0.3420 / 0.4021 : 0.3380 / 0.3981;
            out('r-coef', c.toLocaleString('fr-FR', {{ minimumFractionDigits: 4, maximumFractionDigits: 4 }}));
            out('r-mois', euros(r));
            out('r-an', euros(r * 12));
            out('r-urssaf', euros(r * ur));"""
    return {
        "slug": "reduction-fillon-2026",
        "title": "Réduction Fillon 2026 : RGDU, coefficient jusqu'à 3 Smic",
        "desc": f"Réduction Fillon 2026 devenue RGDU : formule, coefficient maximal 0,3981 ou 0,4021, extinction à 3 Smic. À {fmt(2000)} € brut, l'employeur économise {fmt(round(2000 * c2000))} € par mois.",
        "h1": "Réduction Fillon 2026 : la réduction générale dégressive unique",
        "crumb": "Réduction Fillon 2026",
        "widget_titre": "Réduction générale d'un salarié",
        "widget": widget([champ("w-brut", "Salaire brut mensuel (€)", "2000"),
                          choix("w-effectif", "Effectif de l'entreprise", [("49", "Moins de 50 salariés"), ("50", "50 salariés et plus")], "49")],
                         [("r-coef", "Coefficient"), ("r-mois", "Réduction du mois"), ("r-an", "Sur 12 mois"), ("r-urssaf", "Dont part Urssaf")],
                         "Temps plein, sans heures supplémentaires, Smic de référence du 1er janvier 2026 (1 823,03 €)."),
        "js": js,
        "citable": f"Depuis le 1er janvier 2026, la réduction Fillon n'existe plus sous son ancien nom : elle est remplacée par la réduction générale dégressive unique (RGDU), qui absorbe aussi les taux réduits de cotisation maladie et d'allocations familiales. Son coefficient vaut 0,0200 + 0,3781 × [½ × (3 × Smic annuel ÷ rémunération annuelle − 1)] puissance 1,75 dans une entreprise de moins de 50 salariés, avec 0,3821 à la place de 0,3781 à partir de 50 salariés. Il est plafonné à 0,3981 ou 0,4021 et s'annule à 3 Smic, calculés sur le Smic du 1er janvier 2026, soit {e2(3 * SMIC_REF_RGDU)} brut par mois. Pour un salarié payé {e(2000)} brut dans une petite entreprise, le coefficient est de {f'{c2000:.4f}'.replace('.', ',')} : l'employeur économise environ {e(2000 * c2000)} de cotisations chaque mois, {e(2000 * c2000 * 12)} sur l'année.",
        "corps": corps,
        "sources": [SRC_RGDU, SRC_RGDU_SP, SRC_TAUX, SRC_SMIC],
        "releve": RELEVE,
        "note_sources": "Calcul pour un employeur de droit commun ; les régimes particuliers (Mayotte, apprentis exonérés, déduction forfaitaire spécifique) suivent d'autres règles.",
        "faq": [
            ("La réduction Fillon existe-t-elle encore en 2026 ?",
             "Plus sous ce nom. La loi de financement de la Sécurité sociale pour 2025 l'a fusionnée, au 1er janvier 2026, avec les taux réduits des cotisations maladie et allocations familiales dans une réduction générale dégressive unique. Les fiches de paie et la DSN parlent désormais de RGDU, mais le principe reste le même : un allègement patronal maximal au Smic, qui décroît avec le salaire."),
            ("Quel Smic retenir pour calculer la RGDU en 2026 ?",
             f"Celui du 1er janvier 2026, soit {e2(SMIC_REF_RGDU)} par mois pour 35 heures, même pour les paies versées après la revalorisation du 1er juin. L'Urssaf présente une formule équivalente avec 2,9293 fois le Smic de juin. Le seuil de sortie reste ainsi fixé à {e2(3 * SMIC_REF_RGDU)} brut mensuels pour un temps plein toute l'année."),
            ("Pourquoi un salarié au Smic n'a-t-il plus le coefficient maximal ?",
             f"Parce que le Smic a augmenté au 1er juin 2026 alors que la formule garde la valeur de janvier. À {e2(SMIC_MENSUEL_BRUT)} brut, le rapport entre trois Smic de janvier et le salaire tombe sous 3, et le coefficient descend à {f'{cs:.4f}'.replace('.', ',')} au lieu de 0,3981 dans une entreprise de moins de 50 salariés. La perte reste faible, une dizaine d'euros par mois."),
            ("Que se passe-t-il juste au-dessus de 3 Smic ?",
             f"La réduction disparaît d'un coup. Grâce au Tmin de 0,02, un salaire juste inférieur à {e2(3 * SMIC_REF_RGDU)} garde environ 2 % de réduction, soit une centaine d'euros par mois ; un euro de plus et elle tombe à zéro. Ce palier est l'un des effets de seuil les plus discutés de la réforme, notamment pour les augmentations accordées autour de 5 500 € brut."),
            ("La RGDU s'applique-t-elle aux heures supplémentaires ?",
             "Oui, la rémunération des heures supplémentaires entre dans le salaire annuel de la formule, mais le Smic de référence est majoré du nombre d'heures supplémentaires et complémentaires payées. Le coefficient ne baisse donc pas mécaniquement parce que le salarié fait des heures. Dans les entreprises de moins de 20 salariés, une déduction forfaitaire de 1,50 € par heure supplémentaire s'ajoute."),
            ("Comment la réduction est-elle répartie entre Urssaf et retraite complémentaire ?",
             "Le montant total est ventilé selon le poids des cotisations allégées. Sous 50 salariés, la part déclarée à l'Urssaf est égale à la réduction multipliée par 0,3380 puis divisée par 0,3981 ; le reste, avec le ratio 0,0601 sur 0,3981, s'impute sur les cotisations Agirc-Arrco. À partir de 50 salariés, les ratios sont 0,3420 et 0,0601 rapportés à 0,4021."),
        ],
        "related": ["cout-employeur", "smic-brut-net-2026", "simulateur-fiche-de-paie", "plafond-securite-sociale-2026", "heures-supplementaires-brut-net", "salaire-brut-net-non-cadre"],
    }


# ── Fiche de paie ─────────────────────────────────────────────────────────────

def bulletin(brut, statut="non-cadre", effectif=10, at=0.01):
    """Bulletin simplifié 2026 (taux Urssaf secteur privé), mêmes formules que le JS de la page."""
    p = PSS_MENSUEL
    t1, t2, l4 = min(brut, p), max(0, min(brut, 8 * p) - p), min(brut, 4 * p)
    r = calculer_brut_vers_net(brut, statut)
    pat = (brut * (0.13 + 0.0211 + 0.0525 + at + 0.003 + 0.00016 + 0.0068 + (0.0055 if effectif < 11 else 0.01))
           + t1 * (0.0855 + 0.0472 + 0.0129) + t2 * (0.1295 + 0.0162) + l4 * 0.0425
           + (brut * 0.0021 if brut > p else 0)
           + (t1 * 0.001 if effectif < 50 else brut * 0.005)
           + (l4 * 0.00036 if statut == "cadre" else 0))
    red = brut * coef_rgdu(brut, effectif >= 50)
    return {"net": r["net_avant_impot"], "sal": brut - r["net_avant_impot"], "pat": pat - red, "red": red,
            "imposable": r["net_imposable"], "r": r}


def page_fiche():
    ex = bulletin(2500)
    imp = ex["imposable"]
    tn = taux_neutre(imp)
    corps = f"""
<h2>Ce que contient une fiche de paie en 2026</h2>
<p>Le bulletin suit un ordre fixé par le Code du travail : la rémunération brute, puis les cotisations regroupées par risque (santé, accidents du travail, retraite, famille, assurance chômage), la CSG et la CRDS, le net à payer avant impôt, l'impôt prélevé à la source et le net versé. Le simulateur ci-dessus reprend cet ordre, ligne par ligne, avec les taux 2026 publiés par l'Urssaf.</p>
<h2>Exemple : {e(2500)} brut, non-cadre, entreprise de 10 salariés</h2>
{table(["Ligne du bulletin", "Montant"], [
    ["Salaire de base", e2(2500)],
    ["Cotisations et contributions salariales", "− " + e2(ex["sal"])],
    ["Net à payer avant impôt sur le revenu", e2(ex["net"])],
    ["Net imposable", e2(imp)],
    [f"Impôt prélevé au taux neutre ({pct(tn, 1)})", "− " + e2(imp * tn / 100)],
    ["Net versé", e2(ex["net"] - imp * tn / 100)],
    ["Cotisations patronales après réduction générale", e2(ex["pat"])],
    ["Coût total pour l'employeur", e2(2500 + ex["pat"])],
])}
{note("Taux accidents du travail supposé à 1 %, hors mutuelle et prévoyance d'entreprise, hors versement mobilité. La réduction générale dégressive unique, " + e2(ex["red"]) + " ici, est déjà déduite des cotisations patronales.")}
<h2>Net à payer, net imposable, net social : trois nets différents</h2>
<p>Le <strong>net à payer avant impôt</strong> est le brut diminué de toutes les cotisations salariales et de la CSG-CRDS. Le <strong>net imposable</strong> lui ajoute la CSG non déductible (2,40 %) et la CRDS (0,50 %), calculées sur 98,25 % du brut, ainsi que la part patronale de la mutuelle : c'est la base de l'impôt et du prélèvement à la source. Le <strong>montant net social</strong>, affiché depuis 2024, sert aux caisses d'allocations familiales pour calculer la prime d'activité et le RSA ; il réintègre certains éléments exonérés.</p>
<h2>Les taux salariaux de 2026</h2>
{table(["Cotisation salariale", "Taux", "Assiette"], [
    ["Vieillesse plafonnée", "6,90 %", "Tranche 1"],
    ["Vieillesse déplafonnée", "0,40 %", "Totalité"],
    ["Retraite complémentaire Agirc-Arrco", "3,15 % / 8,64 %", "Tranche 1 / tranche 2"],
    ["Contribution d'équilibre général", "0,86 % / 1,08 %", "Tranche 1 / tranche 2"],
    ["Contribution d'équilibre technique", "0,14 %", "Totalité, au-delà du plafond"],
    ["CSG déductible", "6,80 %", "98,25 % du brut"],
    ["CSG non déductible et CRDS", "2,40 % + 0,50 %", "98,25 % du brut"],
    ["Apec (cadres)", "0,024 %", "Jusqu'à 4 plafonds"],
])}
{note("Tranche 1 : jusqu'au plafond de la Sécurité sociale, 4 005 € par mois en 2026. En Alsace-Moselle, une cotisation maladie salariale de 1,30 % s'ajoute.")}
<p>Les lignes patronales suivent les taux Urssaf 2026 : maladie 13 %, vieillesse 8,55 % sur la tranche 1 et 2,11 % sur la totalité, allocations familiales 5,25 %, assurance chômage 4 % et AGS 0,25 %, retraite complémentaire 4,72 % et 12,95 %, contribution solidarité autonomie 0,30 %, Fnal, formation professionnelle et taxe d'apprentissage. Le détail par cotisation et l'effet de la taille de l'entreprise sont expliqués sur la page <a href="/cout-employeur/">coût employeur</a>, et la formule de l'allègement sur la page <a href="/reduction-fillon-2026/">réduction Fillon 2026</a>.</p>
"""
    js = f"""
            var b = v('w-brut'), st = document.getElementById('w-statut').value, eff = parseInt(document.getElementById('w-eff').value, 10);
            var tauxSaisi = String(document.getElementById('w-pas').value).trim();
            var r = calculerBrutVersNet(b, st, 1);
            var p = 4005, t1 = Math.min(b, p), t2 = Math.max(0, Math.min(b, 8 * p) - p), l4 = Math.min(b, 4 * p), at = 0.01;
            var L = [
                ['Maladie, maternité, invalidité, décès', b * 0.13],
                ['Vieillesse plafonnée', t1 * 0.0855],
                ['Vieillesse déplafonnée', b * 0.0211],
                ['Allocations familiales', b * 0.0525],
                ['Accidents du travail (1 %)', b * at],
                ['Assurance chômage et AGS', l4 * 0.0425],
                ['Retraite complémentaire Agirc-Arrco', t1 * 0.0472 + t2 * 0.1295],
                ['Contribution d\\'équilibre général', t1 * 0.0129 + t2 * 0.0162],
                ['Contribution d\\'équilibre technique', b > p ? b * 0.0021 : 0],
                ['Contribution solidarité autonomie', b * 0.003],
                ['Fnal', eff < 50 ? t1 * 0.001 : b * 0.005],
                ['Dialogue social', b * 0.00016],
                ['Formation professionnelle', b * (eff < 11 ? 0.0055 : 0.01)],
                ['Taxe d\\'apprentissage', b * 0.0068]
            ];
            if (st === 'cadre') L.push(['Apec', l4 * 0.00036]);
            var s = 3 * {SMIC_REF_RGDU}, td = eff >= 50 ? 0.3821 : 0.3781, c = 0;
            if (b > 0 && b < s) {{ c = Math.min(0.02 + td, 0.02 + td * Math.pow(0.5 * (s / b - 1), 1.75)); }}
            var pat = 0; for (var i = 0; i < L.length; i++) pat += L[i][1];
            var red = b * c; pat -= red;
            var imp = r.netImposableMensuel;
            var G = {js_grille(GRILLE_METRO)}, tn = 43;
            for (var j = 0; j < G.length; j++) {{ if (imp < G[j][0]) {{ tn = G[j][1]; break; }} }}
            var taux = tauxSaisi === '' ? tn : (parseFloat(tauxSaisi.replace(',', '.')) || 0);
            var pas = Math.round(imp * taux) / 100;
            out('r-net', centimes(r.netAvantImpot));
            out('r-imp', centimes(imp));
            out('r-verse', centimes(r.netAvantImpot - pas));
            out('r-cout', centimes(b + pat));
            var D = r.detailCotisationsSalariales, h = '<div class="tp-wrap"><table class="tp-table"><thead><tr><th>Ligne</th><th>Salarié</th><th>Employeur</th></tr></thead><tbody>';
            h += '<tr><td>Salaire de base</td><td>' + centimes(b) + '</td><td></td></tr>';
            for (var k in D) {{ if (D[k].montant > 0) h += '<tr><td>' + D[k].label + '</td><td>− ' + centimes(D[k].montant) + '</td><td></td></tr>'; }}
            for (var m = 0; m < L.length; m++) {{ if (L[m][1] > 0) h += '<tr><td>' + L[m][0] + '</td><td></td><td>' + centimes(L[m][1]) + '</td></tr>'; }}
            if (red > 0) h += '<tr><td>Réduction générale dégressive</td><td></td><td>− ' + centimes(red) + '</td></tr>';
            h += '<tr class="tp-total"><td>Net à payer avant impôt</td><td>' + centimes(r.netAvantImpot) + '</td><td>' + centimes(pat) + '</td></tr>';
            h += '<tr><td>Net imposable</td><td>' + centimes(imp) + '</td><td></td></tr>';
            h += '<tr><td>Impôt à la source (' + taux.toLocaleString('fr-FR') + ' %)</td><td>− ' + centimes(pas) + '</td><td></td></tr>';
            h += '<tr class="tp-total"><td>Net versé</td><td>' + centimes(r.netAvantImpot - pas) + '</td><td></td></tr></tbody></table></div>';
            document.getElementById('w-bulletin').innerHTML = h;"""
    return {
        "slug": "simulateur-fiche-de-paie",
        "title": "Fiche de paie 2026 : bulletin de salaire simulé en détail",
        "desc": "Fiche de paie 2026 simulée ligne par ligne : cotisations salariales et patronales, net à payer, net imposable, impôt à la source et net versé, taux Urssaf.",
        "h1": "Fiche de paie 2026 : simulez votre bulletin de salaire",
        "crumb": "Fiche de paie",
        "widget_titre": "Votre bulletin de paie",
        "widget": widget([champ("w-brut", "Salaire brut mensuel (€)", "2500"),
                          choix("w-statut", "Statut", STATUT, "non-cadre"),
                          choix("w-eff", "Effectif de l'entreprise", [("10", "Moins de 11 salariés"), ("20", "11 à 49 salariés"), ("50", "50 salariés et plus")], "10"),
                          champ("w-pas", "Taux de prélèvement à la source (%, vide = taux neutre)", "")],
                         [("r-net", "Net avant impôt"), ("r-imp", "Net imposable"), ("r-verse", "Net versé"), ("r-cout", "Coût employeur")],
                         "Taux accidents du travail de 1 %, hors mutuelle, prévoyance et versement mobilité.") + '<div id="w-bulletin" class="mt-4"></div>',
        "js": js,
        "citable": f"Une fiche de paie 2026 part du salaire brut, retire les cotisations salariales de retraite (6,90 % et 0,40 % de vieillesse, 3,15 % d'Agirc-Arrco et 0,86 % de CEG sous le plafond) puis la CSG et la CRDS, à 9,70 % de 98,25 % du brut. Pour un non-cadre payé {e(2500)} brut, il reste {e2(ex['net'])} de net à payer avant impôt ; le net imposable, qui réintègre la CSG non déductible et la CRDS, s'élève à {e2(imp)}. Au taux neutre de {pct(tn, 1)}, applicable en l'absence de taux personnalisé, l'impôt prélevé à la source est de {e2(imp * tn / 100)} et le net versé de {e2(ex['net'] - imp * tn / 100)}. Côté employeur, les cotisations patronales, diminuées de la réduction générale dégressive unique, portent le coût total à environ {e(2500 + ex['pat'])} dans une entreprise de moins de onze salariés.",
        "corps": corps,
        "sources": [SRC_TAUX, SRC_BULLETIN, SRC_RGDU, SRC_PAS_BOFIP],
        "releve": RELEVE,
        "faq": [
            ("Comment lire le net à payer sur une fiche de paie ?",
             "Le net à payer avant impôt est le brut diminué des cotisations salariales et de la CSG-CRDS. Il apparaît en caractères plus grands que les autres lignes, avant le prélèvement à la source. Le montant réellement viré sur votre compte est le net versé, en bas du bulletin, après l'impôt et d'éventuels acomptes, titres-restaurant ou remboursements de transport."),
            ("Pourquoi le net imposable est-il plus élevé que le net à payer ?",
             f"Parce qu'une partie de la CSG et la CRDS ne sont pas déductibles du revenu imposable : 2,40 % et 0,50 % de 98,25 % du brut, soit environ {e2(2500 * 0.029 * 0.9825)} pour {e(2500)} brut. La part de mutuelle payée par l'employeur s'y ajoute aussi. C'est ce montant qui sert de base au prélèvement à la source et que vous retrouvez prérempli sur votre déclaration."),
            ("Quelles cotisations patronales figurent sur un bulletin de salaire ?",
             "L'employeur paie la maladie à 13 %, la vieillesse à 8,55 % et 2,11 %, les allocations familiales à 5,25 %, les accidents du travail selon le taux notifié, l'assurance chômage à 4 % et l'AGS à 0,25 %, la retraite complémentaire, la contribution solidarité autonomie, le Fnal, la formation et la taxe d'apprentissage. La réduction générale dégressive unique vient ensuite en diminution."),
            ("Le simulateur de fiche de paie tient-il compte de la mutuelle ?",
             "Non, car son coût dépend de chaque contrat. La part salariale de la mutuelle obligatoire, souvent entre 15 et 50 € par mois, se retire du net à payer ; la part patronale s'ajoute au net imposable et au coût employeur. La prévoyance, obligatoire pour les cadres et fréquente pour les autres salariés, suit le même traitement et doit être ajoutée à part."),
            ("Quel taux de prélèvement à la source le simulateur applique-t-il ?",
             "Si vous laissez le champ vide, il applique la grille du taux neutre de métropole en vigueur depuis le 1er mai 2026, calculée sur le net imposable du mois. Si vous saisissez votre taux personnalisé, celui qui figure sur votre bulletin ou dans votre espace impots.gouv.fr, le prélèvement et le net versé sont recalculés avec ce taux."),
            ("Pourquoi deux salariés au même brut n'ont-ils pas le même net ?",
             "Le statut cadre ajoute la cotisation Apec et, en pratique, une prévoyance obligatoire ; la mutuelle varie selon les entreprises ; l'Alsace-Moselle prélève 1,30 % de plus pour le régime local ; les heures supplémentaires bénéficient d'une réduction de cotisations salariales. Le taux de prélèvement à la source, enfin, dépend de la situation fiscale de chacun et change le net versé."),
        ],
        "related": ["cout-employeur", "salaire-net-imposable", "taux-prelevement-a-la-source", "reduction-fillon-2026", "salaire-brut-net-cadre", "salaire-brut-net-non-cadre"],
    }


# ── CESU : salarié du particulier employeur ───────────────────────────────────

# Taux salariaux (Urssaf, salariés à domicile) : vieillesse 6,90 % + 0,40 %, Ircem prévoyance 1,04 %,
# Agirc-Arrco 3,15 %, CEG 0,86 %, CSG-CRDS 9,70 % sur 98,25 % du brut.
CESU_SAL = 0.069 + 0.004 + 0.0104 + 0.0315 + 0.0086 + 0.097 * 0.9825
# Taux patronaux 2026 : maladie et CSA 13,30 %, vieillesse 8,55 % + 2,11 % (2026), allocations familiales 5,25 %,
# AT 2,06 % (2026), Fnal 0,10 %, Ircem 2,45 %, Agirc-Arrco 4,72 %, CEG 1,29 %, chômage 4,00 %,
# formation 0,85 %, dialogue social 0,016 %.
CESU_PAT = 0.133 + 0.0855 + 0.0211 + 0.0525 + 0.0206 + 0.001 + 0.0245 + 0.0472 + 0.0129 + 0.04 + 0.0085 + 0.00016
DEDUC_HEURE = 2.0


def cesu(net_h, heures):
    brut_h = net_h / (1 - CESU_SAL)
    brut = brut_h * heures
    pat_brut = brut * CESU_PAT
    deduc = min(pat_brut, DEDUC_HEURE * heures)
    pat = pat_brut - deduc
    cout = brut + pat
    return {"brut_h": brut_h, "brut": brut, "sal": brut - net_h * heures, "pat": pat, "deduc": deduc,
            "cout": cout, "apres_ci": cout / 2}


def page_cesu():
    ex = cesu(13, 20)
    lignes = []
    for n in (11, 12, 13, 15, 18, 20):
        c = cesu(n, 1)
        lignes.append([e2(n), e2(c["brut_h"]), e2(c["pat"]), e2(c["cout"]), e2(c["apres_ci"])])
    corps = f"""
<h2>Du net horaire au brut et au coût réel</h2>
<p>Avec le Cesu déclaratif, le particulier employeur déclare le salaire net qu'il verse ; l'Urssaf en déduit le brut et calcule les cotisations, prélevées sur son compte. Les cotisations salariales représentent environ {pct(CESU_SAL * 100, 1)} du brut : le net vaut donc à peu près {pct((1 - CESU_SAL) * 100, 1)} du brut. Les cotisations patronales, environ {pct(CESU_PAT * 100, 1)} du brut, sont diminuées d'une déduction forfaitaire de 2 € par heure travaillée.</p>
{table(["Net horaire", "Brut horaire", "Charges patronales nettes", "Coût horaire", "Après crédit d'impôt"], lignes)}
{note("Estimation par heure en métropole, hors Alsace-Moselle, employeur non exonéré, congés payés inclus dans le net. Les taux sont ceux du barème Urssaf des salariés à domicile, mis à jour des changements du 1er janvier 2026 (accidents du travail 2,06 %, vieillesse déplafonnée 2,11 %) ; le montant exact est celui que calcule le service Cesu.")}
<h2>Les taux de cotisations du particulier employeur</h2>
{table(["Cotisation", "Part salariale", "Part patronale"], [
    ["Maladie et contribution solidarité autonomie", "", "13,30 %"],
    ["Vieillesse plafonnée", "6,90 %", "8,55 %"],
    ["Vieillesse déplafonnée", "0,40 %", "2,11 %"],
    ["Allocations familiales", "", "5,25 %"],
    ["Accidents du travail", "", "2,06 %"],
    ["Ircem prévoyance, Fived, paritarisme, départ à la retraite", "1,04 %", "2,45 %"],
    ["Retraite complémentaire tranche 1", "3,15 %", "4,72 %"],
    ["Contribution d'équilibre général", "0,86 %", "1,29 %"],
    ["Assurance chômage", "", "4,00 %"],
    ["Fnal, formation, dialogue social", "", "0,966 %"],
    ["CSG et CRDS (sur 98,25 % du brut)", "9,70 %", ""],
])}
{note("La cotisation d'assurance chômage retenue ici est le taux de droit commun de 4 % ; le barème détaillé du particulier employeur pour 2026 n'était pas consultable sur urssaf.fr le 27 octobre 2026, seules les deux hausses du 1er janvier l'étaient.")}
<h2>Déduction forfaitaire et exonérations</h2>
<p>Tout particulier employeur non exonéré bénéficie d'une déduction de <strong>2 € par heure</strong> sur ses cotisations patronales, appliquée automatiquement par l'Urssaf, sauf sur les heures de congés payés. Elle est de 3,70 € par heure dans les départements d'outre-mer (décret du 17 février 2014) et suit un barème propre à Mayotte. Les employeurs de plus de 70 ans, les personnes dépendantes ou handicapées et les parents d'un enfant handicapé peuvent, sous conditions, être exonérés de cotisations patronales de Sécurité sociale ; la déduction ne se cumule pas avec cette exonération.</p>
<h2>Le crédit d'impôt de 50 %</h2>
<p>Les sommes versées, salaire et cotisations, ouvrent droit à un crédit d'impôt de 50 %, dans la limite de 12 000 € de dépenses par an, majorée de 1 500 € par enfant à charge ou membre du foyer de plus de 65 ans, sans dépasser 15 000 € (18 000 € la première année d'emploi direct, 20 000 € en cas d'invalidité). Les aides reçues, comme l'APA ou le Cesu préfinancé par un employeur, sont déduites de la base. Avec l'avance immédiate, proposée par le service Cesu+, le crédit est déduit au moment du paiement au lieu d'être versé l'année suivante. Pour l'impôt dû par ailleurs, voyez le <a href="/simulateur-impot-sur-le-revenu/">simulateur d'impôt sur le revenu</a>.</p>
"""
    js = f"""
            var n = v('w-net'), h = v('w-heures'), am = document.getElementById('w-zone').value === 'am';
            var ts = {CESU_SAL} + (am ? 0.013 : 0), tp = {CESU_PAT};
            var bh = ts < 1 ? n / (1 - ts) : 0, b = bh * h;
            var pb = b * tp, pat = pb - Math.min(pb, {DEDUC_HEURE} * h), cout = b + pat;
            out('r-brut', centimes(b));
            out('r-pat', centimes(pat));
            out('r-cout', centimes(cout));
            out('r-ci', centimes(cout / 2));"""
    return {
        "slug": "cesu-brut-net",
        "title": "CESU brut net 2026 : salaire, cotisations et crédit d'impôt",
        "desc": f"CESU brut net 2026 : le net vaut environ {fmt(round((1 - CESU_SAL) * 100))} % du brut. Cotisations du particulier employeur, déduction de 2 € par heure, coût après crédit d'impôt de 50 %.",
        "h1": "CESU brut net 2026 : salaire et coût réel",
        "crumb": "CESU brut net",
        "widget_titre": "Coût d'un salarié déclaré au Cesu",
        "widget": widget([champ("w-net", "Salaire net horaire (€, congés payés inclus)", "13"),
                          champ("w-heures", "Heures dans le mois", "20"),
                          choix("w-zone", "Lieu de travail", [("metro", "Métropole"), ("am", "Alsace-Moselle")], "metro")],
                         [("r-brut", "Salaire brut du mois"), ("r-pat", "Charges patronales nettes"), ("r-cout", "Coût total"), ("r-ci", "Après crédit d'impôt")],
                         "Estimation pour un employeur non exonéré ; le service Cesu calcule le montant exact à chaque déclaration."),
        "js": js,
        "citable": f"Avec le Cesu, le particulier employeur déclare un salaire net ; l'Urssaf en déduit le brut, sachant que les cotisations salariales d'un salarié à domicile pèsent environ {pct(CESU_SAL * 100, 1)} du brut. Un net de 13 € de l'heure correspond ainsi à environ {e2(ex['brut_h'])} brut. L'employeur paie en plus des cotisations patronales d'environ {pct(CESU_PAT * 100, 1)} du brut, diminuées d'une déduction forfaitaire de 2 € par heure. Pour 20 heures par mois à 13 € net, le coût total est d'environ {e2(ex['cout'])}, dont {e2(ex['sal'] + ex['pat'])} de cotisations. Le crédit d'impôt de 50 %, accordé sur le salaire et les cotisations dans la limite de 12 000 € de dépenses par an, ramène la charge réelle à {e2(ex['apres_ci'])} par mois. Deux taux patronaux ont changé au 1er janvier 2026 : accidents du travail à 2,06 % et vieillesse déplafonnée à 2,11 %.",
        "corps": corps,
        "sources": [SRC_PART_EVOL, SRC_PART_TAUX, SRC_PART_DEDUC, SRC_CI_DOMICILE],
        "releve": RELEVE,
        "note_sources": "Les cotisations du particulier employeur sont estimées à partir des taux publiés ; le décompte du service Cesu fait foi.",
        "faq": [
            ("Comment passer du net au brut avec le Cesu ?",
             f"Divisez le net par environ {fmt2(1 - CESU_SAL).replace(',', ',')}, soit un brut supérieur d'environ {pct((1 / (1 - CESU_SAL) - 1) * 100, 0)} au net. Un net de 13 € de l'heure correspond à {e2(cesu(13, 1)['brut_h'])} brut. Le service Cesu fait ce calcul pour vous : vous déclarez le net versé, et le brut figure sur l'attestation d'emploi envoyée au salarié."),
            ("Le salaire déclaré au Cesu inclut-il les congés payés ?",
             "Le plus souvent, oui. Pour un salarié qui travaille de façon occasionnelle ou quelques heures par semaine, l'usage est de majorer chaque heure de 10 % au titre des congés payés et de la payer avec le salaire. La déduction forfaitaire de 2 € ne s'applique pas à cette majoration, puisqu'elle ne porte que sur les heures réellement travaillées."),
            ("Quelle est la déduction forfaitaire du particulier employeur en 2026 ?",
             "Elle est de 2 € par heure travaillée en métropole, retirée automatiquement des cotisations patronales de Sécurité sociale. Elle passe à 3,70 € par heure en Guadeloupe, en Guyane, à la Martinique, à La Réunion, à Saint-Barthélemy, à Saint-Martin et à Saint-Pierre-et-Miquelon,. Mayotte suit un barème propre. Elle ne se cumule pas avec une exonération."),
            ("Combien coûte vraiment une heure de ménage déclarée au Cesu ?",
             f"Pour 13 € net de l'heure, comptez environ {e2(cesu(13, 1)['cout'])} de coût total après la déduction de 2 €, cotisations comprises. Le crédit d'impôt de 50 % ramène la dépense à {e2(cesu(13, 1)['apres_ci'])}. À 15 € net, le coût passe à {e2(cesu(15, 1)['cout'])}, soit {e2(cesu(15, 1)['apres_ci'])} après crédit d'impôt."),
            ("Qui a droit au crédit d'impôt pour un salarié à domicile ?",
             "Tout foyer qui emploie un salarié à domicile pour des services à la personne, imposable ou non, puisque le crédit est remboursé s'il dépasse l'impôt. Il vaut 50 % des salaires et cotisations, dans la limite de 12 000 € par an, majorée de 1 500 € par enfant à charge ou membre du foyer de plus de 65 ans, avec un plafond de 15 000 €."),
            ("Les cotisations du Cesu ont-elles augmenté en 2026 ?",
             "Deux taux patronaux ont été relevés au 1er janvier 2026 : la cotisation accidents du travail, fixée à 2,06 % pour les salariés à domicile, et la vieillesse déplafonnée, portée de 2,02 % à 2,11 %. Le Smic, passé à 12,02 € brut de l'heure en janvier, restait alors inférieur au minimum de la convention collective et n'a pas changé le salaire net minimum à verser."),
        ],
        "related": ["smic-brut-net-2026", "salaire-brut-net-horaire", "salaire-assistante-maternelle", "cout-employeur", "simulateur-fiche-de-paie", "taux-prelevement-a-la-source"],
    }


PAGES = [page_km, page_pss, page_pas, page_rgdu, page_fiche, page_cesu]
