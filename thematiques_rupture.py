#!/usr/bin/env python3
"""
Pages thématiques « fin de contrat » (ajoutées le 2026-10-27) : rupture conventionnelle,
indemnité de licenciement, allocation chômage (ARE), préavis, congés payés.

Chiffres relevés le 2026-10-27 :
- service-public.gouv.fr F987 (indemnité légale, vérifiée le 5 juin 2026), F19030 (rupture
  conventionnelle, 26 juin 2026), F408 (imposition des indemnités, 15 avril 2026 : plafond
  288 360 € en 2026), F2855 (préavis), F24660 (indemnité compensatrice de préavis),
  F33359 (indemnité de congés payés, 6 février 2026), F37482 (congés et arrêt maladie),
  A18945 (chômage après rupture conventionnelle au 1er septembre 2026, loi n° 2026-470) ;
- urssaf.fr : contribution patronale spécifique portée à 40 % pour les ruptures dont le terme
  est postérieur au 1er janvier 2026 (loi n° 2025-1403 du 30 décembre 2025), exonération
  sociale dans la limite de 2 PASS (96 120 €), aucune au-delà de 10 PASS (480 600 €) ;
- unedic.org : « Paramètres utiles avril 2026 », communiqué du 30 juin 2026 (pas de
  revalorisation au 1er juillet 2026 : partie fixe 13,18 €, minimum 32,13 €, plancher de
  dégressivité 92,57 €), diviseur du différé spécifique 111,8 pour 2026 ;
- francetravail.fr : différé congés payés (plafond 30 jours) et délai d'attente de 7 jours.
"""

import math

from thematiques_commun import *  # noqa: F401,F403

RELEVE = "27 octobre 2026"

# ── Chiffres officiels 2026 ──────────────────────────────────────────────────
PASS_2026 = 48060                      # 48 060 €
EXO_SOCIALE_MAX = 2 * PASS_2026        # 96 120 €
SEUIL_10_PASS = 10 * PASS_2026         # 480 600 €
EXO_FISCALE_MAX = 6 * PASS_2026        # 288 360 € (service-public F408)
TAUX_CONTRIB_RC = 0.40                 # contribution patronale spécifique (L137-12 CSS)
TAUX_CSG_CRDS_RUPTURE = 0.097          # CSG 9,2 % + CRDS 0,5 %, sans abattement
DIVISEUR_DIFFERE = 111.8               # différé spécifique 2026 (Unédic, France Travail)
DIFFERE_MAX, DIFFERE_MAX_ECO = 150, 75
DIFFERE_CP_MAX = 30
DELAI_ATTENTE = 7
ARE_FIXE, ARE_MIN, ARE_PLANCHER_DEGR = 13.18, 32.13, 92.57
ARE_SEUIL_CSG = 61                     # seuil d'exonération CSG-CRDS (Unédic, 1er janvier 2026)
ARE_DUREE_MAX = {"moins55": 548, "55-56": 685, "57plus": 822}
ARE_DUREE_MAX_RC = {"moins55": 456, "55-56": 624, "57plus": 624}  # 15 et 20,5 mois, en jours (environ)

SRC_LICENCIEMENT = ("Service-Public.fr, indemnité de licenciement du salarié en CDI", "https://www.service-public.gouv.fr/particuliers/vosdroits/F987")
SRC_RC = ("Service-Public.fr, rupture conventionnelle du CDI", "https://www.service-public.gouv.fr/particuliers/vosdroits/F19030")
SRC_RC_CALCUL = ("Service-Public.fr, calcul de l'indemnité spécifique de rupture conventionnelle", "https://www.service-public.gouv.fr/particuliers/vosdroits/F31539")
SRC_IMPOT_INDEMNITES = ("Service-Public.fr, imposition des indemnités de rupture", "https://www.service-public.gouv.fr/particuliers/vosdroits/F408")
SRC_URSSAF_RC = ("Urssaf, les indemnités de rupture conventionnelle", "https://www.urssaf.fr/accueil/employeur/embaucher-gerer-salaries/gerer-fin-relation-travail/rupture-conventionnelle.html")
SRC_URSSAF_LIC = ("Urssaf, l'indemnité de licenciement pour motif personnel", "https://www.urssaf.fr/accueil/employeur/embaucher-gerer-salaries/gerer-fin-relation-travail/licenciement-motif-personnel.html")
SRC_URSSAF_ECO = ("Urssaf, les indemnités de licenciement pour motif économique", "https://www.urssaf.fr/accueil/employeur/embaucher-gerer-salaries/gerer-fin-relation-travail/licenciement-economique.html")
SRC_CT_L1234_9 = ("Code du travail, article L1234-9 (indemnité de licenciement)", "https://code.travail.gouv.fr/code-du-travail/l1234-9")
SRC_RC_CHOMAGE = ("Service-Public.fr, chômage après rupture conventionnelle au 1er septembre 2026", "https://www.service-public.gouv.fr/particuliers/actualites/A18945")
SRC_UNEDIC_DIFFERE = ("Unédic, différé d'indemnisation spécifique (diviseur 2026)", "https://www.unedic.org/la-reglementation/fiches-thematiques/differe-dindemnisation-specifique-en-cas-dindemnites-supra-legales")
SRC_FT_DIFFERE = ("France Travail, quand commence le versement de l'allocation", "https://www.francetravail.fr/candidat/mes-droits-aux-aides-et-allocati/lessentiel-a-savoir-sur-lallocat/pendant-combien-de-temps-vais-je/quand-vais-je-commencer-a-recevo.html")
SRC_UNEDIC_REVALO = ("Unédic, pas de revalorisation des allocations au 1er juillet 2026", "https://www.unedic.org/actualites/allocations-dassurance-chomage-pas-de-revalorisation-au-1er-juillet-2026")
SRC_UNEDIC_DUREE = ("Unédic, durée d'indemnisation", "https://www.unedic.org/la-reglementation/fiches-thematiques/duree-dindemnisation")
SRC_ARE_SP = ("Service-Public.fr, montant de l'allocation chômage (ARE)", "https://www.service-public.gouv.fr/particuliers/vosdroits/F14860")
SRC_PREAVIS = ("Service-Public.fr, préavis de licenciement", "https://www.service-public.gouv.fr/particuliers/vosdroits/F2855")
SRC_PREAVIS_INDEMNITE = ("Service-Public.fr, indemnité compensatrice de préavis", "https://www.service-public.gouv.fr/particuliers/vosdroits/F24660")
SRC_CT_L1234_1 = ("Code du travail, article L1234-1 (durée du préavis)", "https://code.travail.gouv.fr/code-du-travail/l1234-1")
SRC_CP_CALCUL = ("Service-Public.fr, calcul de l'indemnité de congés payés", "https://www.service-public.gouv.fr/particuliers/vosdroits/F33359")
SRC_CP_MALADIE = ("Service-Public.fr, congés payés acquis pendant un arrêt maladie", "https://www.service-public.gouv.fr/particuliers/vosdroits/F37482")
SRC_CP_COMPENSATRICE = ("Service-Public.fr, indemnité compensatrice de congés payés", "https://www.service-public.gouv.fr/particuliers/vosdroits/F24661")
SRC_CT_L3141_24 = ("Code du travail, article L3141-24 (règle du dixième)", "https://code.travail.gouv.fr/code-du-travail/l3141-24")


def arr(x):
    """Arrondi commercial à l'unité (0,5 vers le haut), identique à Math.round en JS."""
    return math.floor(x + 0.5)


def indemnite_legale(salaire, annees, mois=0):
    """Indemnité légale de licenciement (R1234-2) : 1/4 de mois par an jusqu'à 10 ans, 1/3 au-delà,
    années incomplètes au prorata des mois complets."""
    anc = annees + mois / 12
    return salaire * (min(anc, 10) / 4 + max(0, anc - 10) / 3)


def regime_rupture(total, legale, remu_annuelle, retraite_possible=False):
    """Parts exonérées d'impôt, de cotisations et de CSG-CRDS d'une indemnité de rupture (2026)."""
    if retraite_possible:
        exo_ir = 0.0
    else:
        exo_ir = min(total, max(legale, min(max(2 * remu_annuelle, total / 2), EXO_FISCALE_MAX)))
    exo_soc = 0.0 if total > SEUIL_10_PASS else min(exo_ir, EXO_SOCIALE_MAX)
    exo_csg = min(legale, exo_soc)
    csg = (total - exo_csg) * TAUX_CSG_CRDS_RUPTURE
    return {"exo_ir": exo_ir, "imposable": total - exo_ir, "exo_soc": exo_soc,
            "soumis_cotis": total - exo_soc, "exo_csg": exo_csg, "csg": csg}


def differe_specifique(supra, economique=False):
    return min(math.floor(max(0, supra) / DIVISEUR_DIFFERE), DIFFERE_MAX_ECO if economique else DIFFERE_MAX)


JS_LEGALE = """
            function legale(s, anc) { return s * (Math.min(anc, 10) / 4 + Math.max(0, anc - 10) / 3); }"""


# ── Rupture conventionnelle ──────────────────────────────────────────────────

def page_rc():
    s, a, m = 2500, 6, 0
    leg = indemnite_legale(s, a, m)
    nego = 8000
    supra = nego - leg
    dif = differe_specifique(supra)
    sjr = s * 12 / 365
    iccp = 1200
    dif_cp = min(math.floor(iccp / sjr), DIFFERE_CP_MAX)
    reg = regime_rupture(nego, leg, s * 12)
    contrib = reg["exo_soc"] * TAUX_CONTRIB_RC
    lignes = []
    for anc in (1, 2, 5, 8, 10, 15, 20, 30):
        lignes.append([f"{anc} an{'s' if anc > 1 else ''}"] + [e(indemnite_legale(sal, anc)) for sal in (SMIC_MENSUEL_BRUT, 2500, 3500, 5000)])
    l_dif = []
    for montant in (1000, 5000, 10000, 16770, 25000):
        d = differe_specifique(montant)
        l_dif.append([e(montant), f"{d} jours", f"{d + DELAI_ATTENTE} jours"])
    corps = f"""
<h2>Indemnité minimale selon le salaire et l'ancienneté</h2>
<p>L'indemnité spécifique de rupture conventionnelle ne peut pas être inférieure à l'indemnité légale de licenciement, ou à l'indemnité conventionnelle si votre convention collective prévoit mieux. Contrairement au licenciement, elle est due quelle que soit l'ancienneté : un salarié présent depuis cinq mois a droit au prorata. Le calcul retient un quart de mois de salaire par année jusqu'à dix ans, puis un tiers de mois par année au-delà.</p>
{table(["Ancienneté", "Au SMIC", "2 500 € brut", "3 500 € brut", "5 000 € brut"], lignes)}
{note("Salaire de référence brut mensuel : moyenne des 12 derniers mois ou des 3 derniers mois, primes annuelles proratisées, selon la formule la plus favorable. SMIC à " + e2(SMIC_MENSUEL_BRUT) + " depuis le 1er juin 2026. Minimum légal : une convention collective peut prévoir davantage.")}
<h2>Le calendrier, de l'entretien au premier versement</h2>
<ul>
<li><strong>Entretien et signature</strong> : au moins un entretien ; la convention peut être signée le jour même.</li>
<li><strong>Rétractation</strong> : 15 jours calendaires après la signature, pour chaque partie, sans motif.</li>
<li><strong>Homologation</strong> : la DDETS dispose de 15 jours ouvrables ; son silence vaut homologation. Le contrat prend fin au plus tôt le lendemain.</li>
<li><strong>Différé spécifique</strong> : la part de l'indemnité qui dépasse l'indemnité légale, divisée par 111,8 en 2026, donne un nombre de jours sans allocation, plafonné à {DIFFERE_MAX} jours.</li>
<li><strong>Différé congés payés</strong> : l'indemnité compensatrice de congés payés divisée par le salaire journalier de référence, plafonné à {DIFFERE_CP_MAX} jours.</li>
<li><strong>Délai d'attente</strong> : {DELAI_ATTENTE} jours, une seule fois par période de douze mois.</li>
</ul>
{table(["Part supra-légale", "Différé spécifique", "Avec le délai d'attente"], l_dif)}
{note("Diviseur 2026 : 111,8 (Unédic, France Travail). Jours arrondis à l'unité inférieure. Le différé congés payés s'ajoute éventuellement.")}
<h2>Un exemple complet</h2>
<p>Un salarié payé {e(s)} brut par mois, présent depuis {a} ans, négocie {e(nego)}. Le minimum légal est de {e2(leg)} ; la part supra-légale, {e2(supra)}, entraîne {dif} jours de différé spécifique. S'il reçoit aussi {e(iccp)} d'indemnité compensatrice de congés payés, le différé congés payés est de {dif_cp} jours (salaire journalier de référence d'environ {e2(sjr)}). Avec le délai d'attente, la première allocation arrive après {dif + dif_cp + DELAI_ATTENTE} jours. Toute l'indemnité est exonérée d'impôt et de cotisations ; seule la CSG-CRDS est due sur la part supra-légale, soit {e(reg['csg'])}. L'employeur paie {e(contrib)} de contribution patronale spécifique à 40 %.</p>
<h2>Impôt, cotisations et contribution patronale en 2026</h2>
<p>Pour un salarié qui ne peut pas encore liquider sa retraite de base, l'indemnité échappe à l'impôt sur le revenu dans la limite du plus élevé de trois montants : l'indemnité légale ou conventionnelle, deux fois la rémunération brute de l'année précédente, ou la moitié de l'indemnité, sans dépasser {e(EXO_FISCALE_MAX)} en 2026. La part exonérée d'impôt l'est aussi de cotisations jusqu'à {e(EXO_SOCIALE_MAX)} (2 plafonds annuels de la Sécurité sociale) ; au-delà de {e(SEUIL_10_PASS)}, tout est soumis. La CSG-CRDS (9,7 %) ne s'applique qu'au-delà du minimum légal ou conventionnel.</p>
<p>Côté employeur, la contribution patronale spécifique passe de 30 % à <strong>40 %</strong> pour les ruptures dont le terme est postérieur au 1er janvier 2026 (loi de financement de la Sécurité sociale pour 2026). Elle porte sur la part exonérée de cotisations : une rupture conventionnelle coûte donc nettement plus qu'un licenciement à indemnité égale.</p>
<h2>Chômage : ce qui change le 1er septembre 2026</h2>
<p>La loi n° 2026-470 du 11 juin 2026 réduit la durée maximale d'indemnisation après une rupture conventionnelle pour les contrats rompus à compter du 1er septembre 2026 : <strong>15 mois</strong> au lieu de 18 avant 55 ans, <strong>20,5 mois</strong> à partir de 55 ans. Le montant de l'allocation ne change pas. Service-public.gouv.fr indiquait, à notre relevé, que des textes d'application étaient encore attendus ; les durées exactes en jours n'étaient pas publiées. Le détail du calcul figure sur notre page <a href="/allocation-chomage-are/">allocation chômage (ARE)</a>.</p>
"""
    js = JS_LEGALE + f"""
            var s = v('w-salaire'), anc = v('w-annees') + v('w-mois') / 12, nego = v('w-nego'), cp = v('w-iccp');
            var leg = legale(s, anc);
            var supra = Math.max(0, nego - leg);
            var dif = Math.min(Math.floor(supra / {DIVISEUR_DIFFERE}), {DIFFERE_MAX});
            var sjr = s * 12 / 365;
            var difcp = sjr > 0 ? Math.min(Math.floor(cp / sjr), {DIFFERE_CP_MAX}) : 0;
            out('r-min', centimes(leg));
            out('r-supra', centimes(supra));
            out('r-differe', dif + ' j + ' + difcp + ' j + {DELAI_ATTENTE} j');
            out('r-total', (dif + difcp + {DELAI_ATTENTE}) + ' jours');"""
    citable = (f"En 2026, l'indemnité de rupture conventionnelle ne peut pas être inférieure à l'indemnité légale de licenciement : un quart de mois de salaire brut par année d'ancienneté jusqu'à dix ans, un tiers de mois par année au-delà, au prorata des mois complets et sans condition d'ancienneté minimale. "
               f"Pour {e(s)} brut par mois et {a} ans d'ancienneté, le minimum est de {e2(leg)}. Le salarié dispose de 15 jours calendaires pour se rétracter, puis l'administration de 15 jours ouvrables pour homologuer. "
               f"Côté chômage, la part qui dépasse l'indemnité légale crée un différé spécifique égal à cette part divisée par 111,8, plafonné à {DIFFERE_MAX} jours, auquel s'ajoutent le différé congés payés (30 jours au plus) et le délai d'attente de {DELAI_ATTENTE} jours. "
               f"Depuis le 1er janvier 2026, l'employeur paie une contribution spécifique de 40 % sur la part exonérée de cotisations.")
    return {
        "slug": "indemnite-rupture-conventionnelle",
        "title": "Rupture conventionnelle 2026 : indemnité, carence et délai",
        "desc": "Rupture conventionnelle 2026 : indemnité minimale selon salaire et ancienneté, différé chômage (part supra-légale ÷ 111,8), délai de 7 jours, contribution 40 %.",
        "h1": "Indemnité de rupture conventionnelle 2026",
        "crumb": "Rupture conventionnelle",
        "widget_titre": "Indemnité et carence chômage",
        "widget": widget([champ("w-salaire", "Salaire brut mensuel de référence (€)", "2500"),
                          champ("w-annees", "Ancienneté : années", "6", "numeric"),
                          champ("w-mois", "et mois complets", "0", "numeric"),
                          champ("w-nego", "Indemnité négociée (€)", "8000"),
                          champ("w-iccp", "Indemnité de congés payés (€)", "1200")],
                         [("r-min", "Indemnité minimale"), ("r-supra", "Part supra-légale"),
                          ("r-differe", "Différés + attente"), ("r-total", "Avant la 1re allocation")],
                         "Différé spécifique, différé congés payés et délai d'attente, barème France Travail 2026. Minimum légal ; votre convention collective peut prévoir plus."),
        "js": js,
        "citable": citable,
        "corps": corps,
        "sources": [SRC_RC, SRC_RC_CALCUL, SRC_LICENCIEMENT, SRC_IMPOT_INDEMNITES, SRC_URSSAF_RC, SRC_UNEDIC_DIFFERE, SRC_FT_DIFFERE, SRC_RC_CHOMAGE],
        "releve": RELEVE,
        "note_sources": "Les montants sont des minimums légaux bruts : une convention collective peut prévoir une indemnité plus élevée, et France Travail reste seul juge des différés appliqués.",
        "faq": [
            ("Comment se calcule l'indemnité minimale de rupture conventionnelle ?",
             f"Elle est égale à l'indemnité légale de licenciement : un quart de mois de salaire brut par année d'ancienneté jusqu'à dix ans, puis un tiers de mois par année supplémentaire. Le salaire retenu est la moyenne la plus favorable des 12 ou des 3 derniers mois. Pour {e(s)} brut et {a} ans, cela donne {e2(leg)}. Si votre convention collective prévoit une indemnité de licenciement plus élevée, c'est elle qui sert de plancher."),
            ("Quel est le délai de carence après une rupture conventionnelle ?",
             f"Trois délais s'additionnent avant la première allocation. Le différé spécifique correspond à la part de l'indemnité qui dépasse le minimum légal, divisée par 111,8 en 2026, dans la limite de {DIFFERE_MAX} jours. Le différé congés payés dépend de l'indemnité compensatrice reçue, dans la limite de 30 jours. Le délai d'attente de {DELAI_ATTENTE} jours s'ajoute enfin. Une indemnité égale au minimum légal n'entraîne aucun différé spécifique."),
            ("L'indemnité de rupture conventionnelle est-elle imposable ?",
             f"Non dans la plupart des cas. Elle est exonérée d'impôt sur le revenu dans la limite du plus élevé entre le minimum légal ou conventionnel, deux fois la rémunération brute de l'année précédente et la moitié de l'indemnité, avec un plafond de {e(EXO_FISCALE_MAX)} en 2026. Si vous pouvez déjà liquider une pension de retraite de base, elle devient entièrement imposable et soumise aux cotisations."),
            ("Combien coûte une rupture conventionnelle à l'employeur en 2026 ?",
             f"En plus de l'indemnité, l'employeur verse une contribution patronale spécifique de 40 % sur la part exonérée de cotisations, contre 30 % jusqu'en 2025. Pour une indemnité de {e(nego)} entièrement exonérée, cela représente {e(contrib)}. S'y ajoutent les cotisations sur la part éventuellement soumise et l'indemnité compensatrice de congés payés, due comme pour toute fin de contrat."),
            ("Peut-on signer une rupture conventionnelle avec moins d'un an d'ancienneté ?",
             "Oui. Le Code du travail n'exige aucune ancienneté minimale, contrairement à l'indemnité de licenciement qui suppose huit mois de présence. L'indemnité spécifique est alors calculée au prorata des mois complets : six mois d'ancienneté pour 2 000 € brut donnent 250 €. L'ouverture de droits au chômage reste soumise à la condition d'avoir travaillé au moins six mois sur les deux dernières années."),
            ("La rupture conventionnelle réduit-elle la durée du chômage en 2026 ?",
             "Oui pour les contrats rompus à compter du 1er septembre 2026. La loi du 11 juin 2026 limite l'indemnisation à 15 mois avant 55 ans et à 20,5 mois ensuite, contre 18 mois et jusqu'à 27 mois pour un licenciement. Le montant journalier, lui, est calculé comme pour toute autre fin de contrat. À notre relevé, certains textes d'application n'étaient pas encore publiés."),
        ],
        "related": ["indemnite-licenciement", "allocation-chomage-are", "indemnite-conges-payes", "indemnite-preavis", "plafond-securite-sociale-2026", "cout-employeur"],
    }


# ── Indemnité de licenciement ────────────────────────────────────────────────

def page_licenciement():
    lignes = []
    for anc in (1, 3, 5, 8, 10, 12, 15, 20, 25, 30):
        lignes.append([f"{anc} an{'s' if anc > 1 else ''}", f"{fmt2(indemnite_legale(1, anc))} mois"] +
                      [e(indemnite_legale(sal, anc)) for sal in (2000, 3000, 4500)])
    # Exemple supra-légal
    s, a = 3000, 12
    leg = indemnite_legale(s, a)
    tot = 60000
    reg = regime_rupture(tot, leg, s * 12)
    s2, a2, tot2 = 4000, 15, 150000
    leg2 = indemnite_legale(s2, a2)
    reg2 = regime_rupture(tot2, leg2, s2 * 12)
    ex_frac = indemnite_legale(1500, 3, 6)
    corps = f"""
<h2>Indemnité légale de licenciement : barème 2026</h2>
<p>Le Code du travail (articles L1234-9 et R1234-2) accorde à tout salarié en CDI licencié après au moins <strong>8 mois d'ancienneté ininterrompue</strong> une indemnité minimale, sauf faute grave ou lourde. Elle vaut <strong>un quart de mois</strong> de salaire par année jusqu'à dix ans, puis <strong>un tiers de mois</strong> par année au-delà. Les années incomplètes comptent au prorata des mois complets, et l'ancienneté se mesure à la fin du préavis, même non effectué.</p>
{table(["Ancienneté", "En mois de salaire", "2 000 € brut", "3 000 € brut", "4 500 € brut"], lignes)}
{note("Salaire de référence brut : moyenne des 12 derniers mois ou des 3 derniers mois (primes annuelles au prorata), la plus favorable des deux. Exemple officiel de service-public.gouv.fr : 1 500 € et 3 ans 6 mois donnent " + e2(ex_frac) + ".")}
<h2>Licenciement économique</h2>
<p>Le minimum est le même que pour un licenciement pour motif personnel : la formule légale ne distingue pas le motif. Ce qui change se trouve autour : le contrat de sécurisation professionnelle (CSP), proposé dans les entreprises de moins de 1 000 salariés, supprime le préavis et ouvre une allocation de 75 % du salaire journalier de référence pendant un an pour un salarié ayant au moins un an d'ancienneté ; le différé spécifique d'indemnisation chômage est plafonné à {DIFFERE_MAX_ECO} jours au lieu de {DIFFERE_MAX}. Les indemnités versées dans le cadre d'un plan de sauvegarde de l'emploi sont totalement exonérées d'impôt sur le revenu.</p>
<h2>Indemnité imposable ou non : les plafonds 2026</h2>
<p>La part légale ou conventionnelle n'est jamais imposable. Au-delà, une indemnité supra-légale négociée reste exonérée dans la limite du plus élevé de deux montants, deux fois la rémunération brute de l'année précédente ou la moitié de l'indemnité, avec un plafond de <strong>{e(EXO_FISCALE_MAX)}</strong> en 2026 (6 plafonds annuels de la Sécurité sociale). Côté cotisations, l'exonération s'arrête à <strong>{e(EXO_SOCIALE_MAX)}</strong> (2 plafonds), et disparaît entièrement si le total dépasse {e(SEUIL_10_PASS)}. La CSG et la CRDS, au taux de 9,7 %, s'appliquent dès que l'on dépasse le minimum légal ou conventionnel.</p>
{table(["Cas", "Indemnité légale", "Exonérée d'impôt", "Soumise à cotisations", "CSG-CRDS due"], [
    [f"{e(s)} brut, {a} ans, {e(tot)} versés", e(leg), e(reg['exo_ir']), e(reg['soumis_cotis']), e(reg['csg'])],
    [f"{e(s2)} brut, {a2} ans, {e(tot2)} versés", e(leg2), e(reg2['exo_ir']), e(reg2['soumis_cotis']), e(reg2['csg'])],
])}
{note("Rémunération de l'année précédente supposée égale à 12 fois le salaire mensuel. Hors plan de sauvegarde de l'emploi et hors indemnités fixées par le juge, qui suivent des règles propres.")}
<h2>Indemnité supra-légale et chômage</h2>
<p>Ce qui dépasse le minimum légal retarde le premier versement de l'allocation chômage : le montant supra-légal divisé par 111,8 donne le nombre de jours de différé en 2026. Les dommages et intérêts accordés par le conseil de prud'hommes pour licenciement sans cause réelle et sérieuse ne sont pas pris en compte. Pour une séparation négociée, voyez aussi la <a href="/indemnite-rupture-conventionnelle/">rupture conventionnelle</a>, dont le minimum est identique mais qui ne suppose aucune ancienneté.</p>
"""
    js = JS_LEGALE + f"""
            var s = v('w-salaire'), anc = v('w-annees') + v('w-mois') / 12, tot = v('w-total');
            var leg = anc >= 8 / 12 ? legale(s, anc) : 0;
            if (tot < leg) {{ tot = leg; }}
            var exoIr = Math.min(tot, Math.max(leg, Math.min(Math.max(2 * s * 12, tot / 2), {EXO_FISCALE_MAX})));
            var exoSoc = tot > {SEUIL_10_PASS} ? 0 : Math.min(exoIr, {EXO_SOCIALE_MAX});
            var exoCsg = Math.min(leg, exoSoc);
            out('r-legale', anc >= 8 / 12 ? centimes(leg) : 'Non due (< 8 mois)');
            out('r-imposable', euros(tot - exoIr));
            out('r-cotis', euros(tot - exoSoc));
            out('r-csg', euros((tot - exoCsg) * {TAUX_CSG_CRDS_RUPTURE}));"""
    citable = (f"En 2026, l'indemnité légale de licenciement est due à tout salarié en CDI qui justifie d'au moins 8 mois d'ancienneté, sauf faute grave ou lourde. Elle vaut un quart de mois de salaire brut par année d'ancienneté jusqu'à dix ans, puis un tiers de mois par année au-delà : {e(indemnite_legale(2000, 5))} pour 2 000 € brut et 5 ans, {e(leg)} pour {e(s)} et {a} ans. "
               f"Le salaire de référence est la moyenne la plus favorable des 12 ou des 3 derniers mois. Le minimum est identique pour un licenciement économique. "
               f"L'indemnité légale n'est ni imposable ni soumise à cotisations ; une indemnité supra-légale reste exonérée d'impôt jusqu'à {e(EXO_FISCALE_MAX)} et de cotisations jusqu'à {e(EXO_SOCIALE_MAX)}, mais supporte 9,7 % de CSG-CRDS au-delà du minimum légal ou conventionnel.")
    return {
        "slug": "indemnite-licenciement",
        "title": "Indemnité de licenciement 2026 : calcul légal et imposition",
        "desc": "Indemnité de licenciement 2026 : 1/4 de mois par année jusqu'à 10 ans, 1/3 au-delà. Économique, supra-légale, part imposable et cotisations jusqu'à 96 120 €.",
        "h1": "Indemnité de licenciement 2026",
        "crumb": "Indemnité de licenciement",
        "widget_titre": "Indemnité légale et part imposable",
        "widget": widget([champ("w-salaire", "Salaire brut mensuel de référence (€)", "3000"),
                          champ("w-annees", "Ancienneté : années", "12", "numeric"),
                          champ("w-mois", "et mois complets", "0", "numeric"),
                          champ("w-total", "Indemnité totale versée (€)", "60000")],
                         [("r-legale", "Indemnité légale"), ("r-imposable", "Part imposable"),
                          ("r-cotis", "Part soumise à cotisations"), ("r-csg", "CSG-CRDS due")],
                         "Hors plan de sauvegarde de l'emploi. Rémunération de l'année précédente estimée à 12 fois le salaire saisi. Une indemnité totale inférieure au minimum légal est relevée à ce minimum."),
        "js": js,
        "citable": citable,
        "corps": corps,
        "sources": [SRC_LICENCIEMENT, SRC_CT_L1234_9, SRC_IMPOT_INDEMNITES, SRC_URSSAF_LIC, SRC_URSSAF_ECO, SRC_UNEDIC_DIFFERE],
        "releve": RELEVE,
        "note_sources": "Les montants sont des minimums légaux bruts : votre convention collective peut prévoir une indemnité conventionnelle plus élevée, qui devient alors le plancher.",
        "faq": [
            ("Quelle ancienneté faut-il pour toucher une indemnité de licenciement ?",
             "Il faut au moins 8 mois d'ancienneté ininterrompue chez le même employeur, appréciés à la date d'envoi de la lettre de licenciement. Le salarié licencié pour faute grave ou lourde n'y a pas droit. L'ancienneté retenue pour le calcul court ensuite jusqu'à la fin du préavis, même si l'employeur vous en a dispensé : le préavis non effectué compte donc dans le montant."),
            ("L'indemnité de licenciement économique est-elle plus élevée ?",
             f"Le minimum légal est strictement le même : un quart de mois de salaire par année jusqu'à dix ans, un tiers au-delà. Les accords de plan de sauvegarde de l'emploi prévoient souvent davantage, et ces indemnités sont alors exonérées d'impôt en totalité. Le différé d'indemnisation chômage lié à la part supra-légale est aussi plafonné à {DIFFERE_MAX_ECO} jours au lieu de {DIFFERE_MAX}."),
            ("L'indemnité de licenciement est-elle imposable ?",
             f"La part légale ou conventionnelle ne l'est jamais. Une part supra-légale reste exonérée jusqu'au plus élevé de deux montants, deux fois votre rémunération brute de l'année précédente ou la moitié de l'indemnité, dans la limite de {e(EXO_FISCALE_MAX)} en 2026. Le surplus s'ajoute à vos revenus imposables ; vous pouvez demander l'étalement ou le système du quotient pour en limiter l'effet."),
            ("Qu'est-ce qu'une indemnité supra-légale ?",
             "C'est tout ce que l'employeur verse au-delà du minimum légal ou conventionnel, généralement à l'issue d'une négociation ou d'une transaction. Elle n'est pas obligatoire. Elle supporte la CSG-CRDS à 9,7 %, reste en principe exonérée d'impôt et de cotisations dans certaines limites, et retarde le versement du chômage : chaque tranche de 111,8 € ajoute un jour de différé en 2026."),
            ("Quel salaire retenir pour calculer l'indemnité ?",
             "On compare deux moyennes brutes et on garde la plus favorable : celle des 12 derniers mois précédant la notification, ou celle des 3 derniers mois, en intégrant les primes annuelles au prorata d'un douzième par mois. Si vous étiez en arrêt maladie ou en temps partiel thérapeutique, on retient les mois précédant cet arrêt, pour ne pas pénaliser le salarié malade."),
            ("Les cotisations sociales s'appliquent-elles à l'indemnité de licenciement ?",
             f"Pas sur la part exonérée d'impôt, dans la limite de {e(EXO_SOCIALE_MAX)} en 2026, soit deux plafonds annuels de la Sécurité sociale. Au-delà de ce plafond, le surplus est soumis aux cotisations comme un salaire. Si l'indemnité totale dépasse {e(SEUIL_10_PASS)}, elle est entièrement soumise dès le premier euro. La CSG-CRDS vise toute la part supérieure au minimum légal ou conventionnel."),
        ],
        "related": ["indemnite-rupture-conventionnelle", "indemnite-preavis", "allocation-chomage-are", "indemnite-conges-payes", "plafond-securite-sociale-2026", "salaire-net-imposable"],
    }


# ── Allocation chômage (ARE) ─────────────────────────────────────────────────

def are_calcul(brut_mensuel, age="moins55", mois=24, motif="licenciement"):
    sjr = brut_mensuel * 12 / 365
    aj = max(0.404 * sjr + ARE_FIXE, 0.57 * sjr, ARE_MIN)
    aj = min(aj, 0.75 * sjr) if sjr > 0 else 0
    retraite = min(0.03 * sjr, max(0, aj - ARE_MIN))
    apres = aj - retraite
    csg = min(aj * 0.9825 * 0.067, max(0, apres - ARE_SEUIL_CSG)) if aj >= ARE_SEUIL_CSG else 0
    net_j = apres - csg
    jours = math.ceil(round(min(mois, 36 if age != "moins55" else 24) * 365 / 12 * 0.75, 6))
    plafond = (ARE_DUREE_MAX_RC if motif == "rc2026" else ARE_DUREE_MAX)[age]
    jours = max(182, min(jours, plafond)) if mois >= 6 else 0
    degr = aj > ARE_PLANCHER_DEGR and age == "moins55"
    aj_degr = max(ARE_PLANCHER_DEGR, aj * 0.7) if degr else aj
    return {"sjr": sjr, "aj": aj, "net_j": net_j, "net_m": net_j * 30, "brut_m": aj * 30,
            "jours": jours, "aj_degr": aj_degr, "degr": degr}


def page_are():
    lignes = []
    for b in (SMIC_MENSUEL_BRUT, 2000, 2500, 3000, 4000, 5000, 7000):
        r = are_calcul(b)
        lignes.append([e(b), e2(r["sjr"]), e2(r["aj"]), e(r["net_m"]), pct(r["net_m"] / net(b) * 100, 0),
                       e2(r["aj_degr"]) if r["degr"] else "non"])
    duree = []
    for m in (6, 12, 18, 24):
        duree.append([f"{m} mois", f"{are_calcul(2500, 'moins55', m)['jours']} jours",
                      f"{are_calcul(2500, '55-56', m)['jours']} jours", f"{are_calcul(2500, '57plus', m)['jours']} jours"])
    duree.append(["36 mois", "548 jours (plafond)", f"{are_calcul(2500, '55-56', 36)['jours']} jours",
                  f"{are_calcul(2500, '57plus', 36)['jours']} jours"])
    r25 = are_calcul(2500)
    r40 = are_calcul(4000)
    corps = f"""
<h2>Montant de l'ARE selon le salaire brut</h2>
<p>L'allocation journalière brute est le plus élevé de trois montants : 40,4 % du salaire journalier de référence plus une partie fixe de <strong>{e2(ARE_FIXE)}</strong>, 57 % de ce salaire, ou l'allocation minimale de <strong>{e2(ARE_MIN)}</strong>. Elle ne peut pas dépasser 75 % du salaire journalier de référence. Ces montants n'ont pas été revalorisés au 1er juillet 2026 : le conseil d'administration de l'Unédic n'a pas trouvé de majorité le 30 juin 2026, ce sont donc ceux du 1er juillet 2025 qui s'appliquent.</p>
{table(["Brut mensuel", "Salaire journalier", "ARE brute / jour", "ARE nette / mois", "Part du net", "Après 6 mois"], lignes)}
{note("Salaire journalier de référence = brut mensuel × 12 ÷ 365 (carrière complète sur la période). Net : retenue retraite complémentaire de 3 % du salaire journalier, puis CSG 6,2 % et CRDS 0,5 % sur 98,25 % de l'allocation au-delà du seuil de 61 € par jour. Mensualisation sur 30 jours. La part du net compare à votre ancien salaire net.")}
<h2>Combien de temps touche-t-on le chômage ?</h2>
<p>La durée d'indemnisation est égale au nombre de jours calendaires écoulés entre le premier jour du premier contrat et la fin du dernier, dans une période de référence de 24 mois (36 mois à partir de 55 ans), multiplié par le <strong>coefficient de 0,75</strong> appliqué tant que le taux de chômage reste sous 9 %. Il faut avoir travaillé au moins 130 jours ou 910 heures sur cette période ; la durée minimale est de 182 jours.</p>
{table(["Durée travaillée", "Moins de 55 ans", "55 et 56 ans", "57 ans et plus"], duree)}
{note("Fins de contrat depuis le 1er avril 2025 : plafonds de 548 jours (18 mois), 685 jours (22,5 mois) et 822 jours (27 mois). Emploi continu supposé ; les périodes sans contrat sont retenues dans la limite de 70 % des jours travaillés.")}
<h2>Chômage après une rupture conventionnelle</h2>
<p>Le montant est calculé comme après un licenciement. Deux choses diffèrent. Le versement commence plus tard si l'indemnité négociée dépasse le minimum légal (différé spécifique, voir notre page sur la <a href="/indemnite-rupture-conventionnelle/">rupture conventionnelle</a>). Et pour un contrat rompu à compter du 1er septembre 2026, la loi n° 2026-470 du 11 juin 2026 ramène la durée maximale à <strong>15 mois avant 55 ans</strong> et <strong>20,5 mois à partir de 55 ans</strong>. Le simulateur les traduit en environ 456 et 624 jours ; les durées exactes en jours n'étaient pas encore publiées à notre relevé.</p>
<h2>La dégressivité au 7e mois</h2>
<p>Un allocataire de moins de 55 ans dont l'allocation dépasse {e2(ARE_PLANCHER_DEGR)} brut par jour voit son montant réduit de 30 % à partir du 183e jour indemnisé, sans descendre sous {e2(ARE_PLANCHER_DEGR)}. Cela concerne les salaires d'environ 4 940 € brut mensuels et plus : à {e(4000)} brut, l'allocation de {e2(r40['aj'])} par jour n'est pas touchée.</p>
"""
    js = f"""
            var b = v('w-brut'), age = document.getElementById('w-age').value, m = v('w-mois'), motif = document.getElementById('w-motif').value;
            var sjr = b * 12 / 365;
            var aj = Math.max(0.404 * sjr + {ARE_FIXE}, 0.57 * sjr, {ARE_MIN});
            aj = sjr > 0 ? Math.min(aj, 0.75 * sjr) : 0;
            var ret = Math.min(0.03 * sjr, Math.max(0, aj - {ARE_MIN}));
            var apres = aj - ret;
            var csg = aj >= {ARE_SEUIL_CSG} ? Math.min(aj * 0.9825 * 0.067, Math.max(0, apres - {ARE_SEUIL_CSG})) : 0;
            var plaf = motif === 'rc2026' ? {{moins55: 456, '55-56': 624, '57plus': 624}} : {{moins55: 548, '55-56': 685, '57plus': 822}};
            var jours = Math.ceil(Math.round(Math.min(m, age === 'moins55' ? 24 : 36) * 365 / 12 * 0.75 * 1e6) / 1e6);
            jours = m >= 6 ? Math.max(182, Math.min(jours, plaf[age])) : 0;
            var degr = aj > {ARE_PLANCHER_DEGR} && age === 'moins55';
            out('r-jour', centimes(aj));
            out('r-mois', euros((apres - csg) * 30));
            out('r-duree', jours ? jours + ' jours (' + (jours / 30.42).toFixed(1).replace('.', ',') + ' mois)' : 'Pas de droit (< 6 mois)');
            out('r-degr', degr ? centimes(Math.max({ARE_PLANCHER_DEGR}, aj * 0.7)) + ' / jour' : 'Pas de baisse');"""
    citable = (f"En 2026, l'allocation chômage (ARE) est égale au plus élevé de trois montants : 40,4 % du salaire journalier de référence plus {e2(ARE_FIXE)}, 57 % de ce salaire, ou {e2(ARE_MIN)} par jour, dans la limite de 75 % du salaire journalier. "
               f"Pour un ancien salaire de {e(2500)} brut par mois, l'allocation atteint {e2(r25['aj'])} brut par jour, soit environ {e(r25['net_m'])} net par mois de 30 jours. "
               f"La durée d'indemnisation correspond aux jours travaillés sur les 24 derniers mois, multipliés par 0,75 : 548 jours au plus avant 55 ans, 685 jours à 55 et 56 ans, 822 jours à partir de 57 ans. "
               f"Après une rupture conventionnelle signée pour un contrat rompu depuis le 1er septembre 2026, le plafond tombe à 15 mois avant 55 ans. Les montants n'ont pas été revalorisés au 1er juillet 2026.")
    return {
        "slug": "allocation-chomage-are",
        "title": "Allocation chômage ARE 2026 : montant net et durée de droits",
        "desc": "Allocation chômage ARE 2026 : 40,4 % du salaire journalier + 13,18 € ou 57 %, minimum 32,13 €. Montant net par mois, durée de 548 à 822 jours. Calcul gratuit.",
        "h1": "Allocation chômage (ARE) 2026 : montant et durée",
        "crumb": "Chômage (ARE)",
        "widget_titre": "Estimer votre allocation chômage",
        "widget": widget([champ("w-brut", "Salaire brut mensuel moyen (€)", "2500"),
                          champ("w-mois", "Mois travaillés sur la période", "24", "numeric"),
                          choix("w-age", "Âge à la fin du contrat", [("moins55", "Moins de 55 ans"), ("55-56", "55 ou 56 ans"), ("57plus", "57 ans et plus")], "moins55"),
                          choix("w-motif", "Fin de contrat", [("licenciement", "Licenciement, fin de CDD, rupture avant le 1er sept. 2026"), ("rc2026", "Rupture conventionnelle depuis le 1er sept. 2026")], "licenciement")],
                         [("r-jour", "ARE brute par jour"), ("r-mois", "ARE nette par mois"),
                          ("r-duree", "Durée des droits"), ("r-degr", "Après le 6e mois")],
                         "Estimation pour un emploi continu, hors cas particuliers (temps partiel, intermittents, Mayotte). Seul France Travail notifie le montant et la durée."),
        "js": js,
        "citable": citable,
        "corps": corps,
        "sources": [SRC_ARE_SP, SRC_UNEDIC_REVALO, SRC_UNEDIC_DUREE, SRC_RC_CHOMAGE, SRC_FT_DIFFERE],
        "releve": RELEVE,
        "note_sources": "Les montants nets sont estimés au taux normal de CSG (6,2 %) ; un revenu fiscal de référence modeste entraîne un taux réduit ou une exonération que le simulateur ne prend pas en compte.",
        "faq": [
            ("Comment est calculé le salaire journalier de référence ?",
             "France Travail additionne les salaires bruts perçus sur la période de référence, 24 mois avant 55 ans et 36 mois ensuite, puis divise par le nombre de jours calendaires entre le premier jour du premier contrat et la fin du dernier. Les périodes sans contrat sont comptées dans la limite de 70 % des jours travaillés. Pour un emploi continu, cela revient au salaire mensuel multiplié par 12 et divisé par 365."),
            ("Combien de temps touche-t-on le chômage en 2026 ?",
             "Autant de jours que vous en avez travaillé sur la période de référence, multipliés par 0,75. Pour deux ans d'emploi continu avant 55 ans, cela donne 548 jours, soit 18 mois. Les plafonds sont de 685 jours à 55 et 56 ans et de 822 jours à partir de 57 ans. Après une rupture conventionnelle effective depuis le 1er septembre 2026, ils tombent à 15 et 20,5 mois."),
            ("Le chômage est-il versé dès le lendemain de la fin du contrat ?",
             "Non. Un délai d'attente de 7 jours s'applique toujours, une fois par période de douze mois. S'y ajoutent un différé lié à l'indemnité compensatrice de congés payés, de 30 jours au plus, et un différé spécifique si vous avez reçu une indemnité supérieure au minimum légal, de 150 jours au plus. Ces délais retardent le premier paiement sans réduire la durée totale de vos droits."),
            ("Quel est le montant minimum de l'allocation chômage en 2026 ?",
             f"L'allocation minimale est de {e2(ARE_MIN)} brut par jour, soit {e2(ARE_MIN * 30)} pour un mois de 30 jours, sans dépasser 75 % de l'ancien salaire journalier. Ce montant n'a pas été revalorisé au 1er juillet 2026. Pour les petits salaires, c'est souvent la limite de 75 % qui s'applique : un salaire de 1 200 € brut donne environ 29,59 € par jour."),
            ("Qui est concerné par la dégressivité de l'allocation ?",
             f"Les allocataires de moins de 55 ans à la fin de leur contrat dont l'allocation dépasse {e2(ARE_PLANCHER_DEGR)} brut par jour, ce qui correspond à un ancien salaire d'environ 4 940 € brut par mois. À partir du septième mois d'indemnisation, l'allocation est multipliée par 0,7 sans pouvoir descendre sous {e2(ARE_PLANCHER_DEGR)} par jour. Depuis avril 2025, le seuil d'âge est passé de 57 à 55 ans."),
            ("L'allocation chômage est-elle imposable ?",
             "Oui. L'ARE est un revenu de remplacement imposable, déclaré automatiquement par France Travail et soumis au prélèvement à la source au taux de votre foyer. Avant cela, elle supporte une retenue de 3 % du salaire journalier pour la retraite complémentaire, puis la CSG et la CRDS, sauf si le montant journalier est faible ou si votre revenu fiscal de référence ouvre droit à une exonération."),
        ],
        "related": ["indemnite-rupture-conventionnelle", "indemnite-licenciement", "indemnite-conges-payes", "salaire-brut-net-interim", "salaire-net-imposable", "smic-brut-net-2026"],
    }


# ── Préavis ──────────────────────────────────────────────────────────────────

def duree_preavis(mois_anc, handicape=False):
    if mois_anc < 6:
        return 0
    base = 1 if mois_anc < 24 else 2
    return min(base * 2, 3) if handicape else base


def page_preavis():
    l_duree = [
        ["Moins de 6 mois", "Convention collective ou usage", "Convention collective ou usage"],
        ["De 6 mois à moins de 2 ans", "1 mois", "2 mois"],
        ["2 ans et plus", "2 mois", "3 mois"],
    ]
    lignes = []
    for b in (SMIC_MENSUEL_BRUT, 2000, 2500, 3000, 4000, 5000):
        lignes.append([e(b), e(b), e(b * 2), e(b * 2 * 0.1), e(net(b) * 2)])
    s, mois = 2800, 2
    ex_brut = s * mois
    ex_cp = ex_brut * 0.1
    corps = f"""
<h2>Durée légale du préavis de licenciement</h2>
<p>L'article L1234-1 du Code du travail fixe un minimum selon l'ancienneté, appréciée au jour de l'envoi de la lettre de licenciement. Votre convention collective, votre contrat ou un usage peuvent prévoir plus long ; c'est alors la durée la plus favorable qui s'applique. Il n'y a pas de préavis en cas de faute grave ou lourde, d'inaptitude, de force majeure ou d'adhésion au contrat de sécurisation professionnelle.</p>
{table(["Ancienneté", "Préavis légal", "Travailleur handicapé"], l_duree)}
{note("Le préavis du travailleur handicapé est doublé dans la limite de 3 mois. En Moselle, Bas-Rhin et Haut-Rhin, le droit local prévoit des durées propres, de 1 jour à 6 semaines selon le mode de rémunération. Pour une démission, seule la convention collective fixe la durée.")}
<h2>Indemnité compensatrice de préavis : le calcul</h2>
<p>Si l'employeur vous dispense d'effectuer le préavis, il doit vous verser la rémunération que vous auriez perçue en travaillant : salaire de base, heures supplémentaires régulières, primes et commissions, avantages en nature, titres-restaurant, jours de RTT. Les congés payés qui auraient été acquis pendant le préavis s'y ajoutent, généralement par la règle du dixième. La date de fin du contrat ne change pas : vous restez salarié jusqu'au terme du préavis et pouvez commencer un nouvel emploi plus tôt.</p>
{table(["Salaire brut", "1 mois de préavis", "2 mois de préavis", "Congés payés sur 2 mois", "Net estimé, 2 mois"], lignes)}
{note("Congés payés afférents calculés au dixième. Net estimé avec les cotisations salariales 2026 d'un non-cadre, hors mutuelle et prélèvement à la source.")}
<h2>Un exemple</h2>
<p>Un salarié payé {e(s)} brut par mois, licencié après 4 ans d'ancienneté, est dispensé de ses {mois} mois de préavis. Il perçoit une indemnité compensatrice de {e(ex_brut)} brut, plus {e(ex_cp)} d'indemnité de congés payés afférente, soit {e(ex_brut + ex_cp)} brut. Cette somme est soumise aux cotisations et imposable comme un salaire ; elle se cumule avec l'<a href="/indemnite-licenciement/">indemnité de licenciement</a> et l'<a href="/indemnite-conges-payes/">indemnité compensatrice de congés payés</a>.</p>
<h2>Quand l'indemnité n'est pas due</h2>
<ul>
<li>Vous avez demandé à ne pas effectuer le préavis et l'employeur a accepté.</li>
<li>Licenciement pour faute grave ou lourde, ou pour inaptitude d'origine non professionnelle.</li>
<li>Rupture conventionnelle : aucun préavis n'existe, la date de fin est fixée dans la convention.</li>
<li>Arrêt maladie pendant un préavis que l'employeur n'avait pas dispensé.</li>
</ul>
"""
    js = """
            var s = v('w-salaire'), m = v('w-anc'), h = document.getElementById('w-handicap').value === 'oui';
            var d = m < 6 ? 0 : (m < 24 ? 1 : 2);
            if (h && d) { d = Math.min(d * 2, 3); }
            var brut = s * d;
            out('r-duree', d ? d + ' mois' : 'Selon convention');
            out('r-brut', euros(brut));
            out('r-cp', euros(brut * 0.1));
            out('r-net', euros(calculerBrutVersNet(s, 'non-cadre', 1).netAvantImpot * d));"""
    citable = (f"En 2026, le préavis légal de licenciement est d'un mois pour un salarié ayant entre 6 mois et 2 ans d'ancienneté, et de deux mois au-delà de 2 ans ; sous 6 mois, il dépend de la convention collective ou des usages. Il est doublé pour un travailleur handicapé, dans la limite de 3 mois. "
               f"Si l'employeur dispense le salarié de l'effectuer, il lui doit une indemnité compensatrice égale au salaire brut qu'il aurait touché, primes, avantages et congés payés compris : {e(s * 2)} brut pour deux mois à {e(s)}, plus {e(s * 2 * 0.1)} de congés payés afférents. "
               "Cette indemnité est imposable et soumise aux cotisations comme un salaire. Elle n'est pas due en cas de faute grave, de rupture conventionnelle ou de dispense demandée par le salarié.")
    return {
        "slug": "indemnite-preavis",
        "title": "Indemnité de préavis 2026 : durée légale et montant brut net",
        "desc": "Indemnité compensatrice de préavis 2026 : 1 mois de 6 mois à 2 ans d'ancienneté, 2 mois au-delà, 3 mois si handicapé. Montant brut, net et congés payés.",
        "h1": "Préavis de licenciement et indemnité compensatrice 2026",
        "crumb": "Préavis",
        "widget_titre": "Durée et indemnité de préavis",
        "widget": widget([champ("w-salaire", "Salaire brut mensuel (€)", "2800"),
                          champ("w-anc", "Ancienneté en mois", "48", "numeric"),
                          choix("w-handicap", "Travailleur handicapé", [("non", "Non"), ("oui", "Oui")], "non")],
                         [("r-duree", "Préavis légal"), ("r-brut", "Indemnité brute"),
                          ("r-cp", "Congés payés afférents"), ("r-net", "Indemnité nette estimée")],
                         "Minimum légal du licenciement hors faute grave. Une convention collective peut prévoir un préavis plus long, notamment pour les cadres."),
        "js": js,
        "citable": citable,
        "corps": corps,
        "sources": [SRC_PREAVIS, SRC_PREAVIS_INDEMNITE, SRC_CT_L1234_1, SRC_TAUX],
        "releve": RELEVE,
        "faq": [
            ("Quelle est la durée du préavis de licenciement ?",
             "Elle dépend de votre ancienneté au jour de l'envoi de la lettre de licenciement. Sous 6 mois, la convention collective ou les usages la fixent. De 6 mois à moins de 2 ans, le Code du travail impose au moins un mois. À partir de 2 ans, au moins deux mois. Beaucoup de conventions accordent trois mois aux cadres : vérifiez la vôtre, car la durée la plus longue l'emporte."),
            ("Comment est calculée l'indemnité compensatrice de préavis ?",
             "Elle correspond exactement à ce que vous auriez gagné en travaillant pendant le préavis : salaire de base, heures supplémentaires habituelles, primes fixes et variables, commissions, avantages en nature, titres-restaurant et jours de RTT. Les congés payés acquis pendant cette période s'y ajoutent, le plus souvent au dixième. Elle peut être versée mois par mois ou en une fois avec le solde de tout compte."),
            ("L'indemnité de préavis est-elle imposable ?",
             "Oui. Contrairement à l'indemnité de licenciement, l'indemnité compensatrice de préavis a la nature d'un salaire : elle supporte les cotisations sociales, la CSG et la CRDS, et elle entre dans le revenu imposable avec prélèvement à la source. Elle figure sur le bulletin de paie et compte aussi dans le salaire de référence retenu par France Travail pour l'allocation chômage."),
            ("Peut-on refuser d'effectuer son préavis ?",
             "Le salarié peut demander une dispense, mais l'employeur est libre de refuser. S'il accepte à votre demande, aucune indemnité n'est due pour la période non travaillée. Si au contraire c'est l'employeur qui vous dispense, vous ne pouvez pas vous y opposer et il doit vous verser l'indemnité compensatrice. Quitter son poste sans accord expose à devoir une indemnité à l'employeur."),
            ("Le préavis est-il prolongé par des congés ou un arrêt maladie ?",
             "Les congés payés fixés avant la notification du licenciement suspendent le préavis, qui est prolongé d'autant. Un accident du travail ou une maladie professionnelle survenant pendant le préavis le suspend aussi. En revanche, un arrêt pour maladie ordinaire ne le prolonge pas : le contrat prend fin à la date prévue, et l'employeur ne doit pas d'indemnité pour la période d'arrêt non dispensée."),
            ("Y a-t-il un préavis en cas de rupture conventionnelle ?",
             "Non. La rupture conventionnelle ne comporte pas de préavis : les parties fixent librement la date de fin du contrat, au plus tôt le lendemain de l'homologation. Aucune indemnité compensatrice de préavis n'est donc due. Si vous souhaitez partir plus tard, il suffit de choisir une date de rupture plus éloignée dans la convention, en continuant à travailler normalement jusque-là."),
        ],
        "related": ["indemnite-licenciement", "indemnite-rupture-conventionnelle", "indemnite-conges-payes", "allocation-chomage-are", "salaire-brut-net-cadre", "salaire-brut-net-non-cadre"],
    }


# ── Congés payés ─────────────────────────────────────────────────────────────

def jours_acquis(mois_maladie, mois_travail=12):
    j = (mois_travail - mois_maladie) * 2.5 + min(mois_maladie * 2, 24)
    return min(math.ceil(j), 30)


def page_cp():
    s, annuel, jours, jo = 2000, 24000, 10, 21
    maintien = s * jours / jo
    dixieme = annuel / 10 * jours / 25
    lignes = []
    for sal, var in ((SMIC_MENSUEL_BRUT, 0), (2000, 0), (2000, 2400), (2500, 0), (3000, 4000), (4000, 0)):
        an = sal * 12 + var
        m5 = sal * 5 / 21.67
        d5 = an / 10 * 5 / 25
        lignes.append([e(sal), e(an), e2(m5), e2(d5), "dixième" if d5 > m5 else "maintien"])
    l_acq = [[f"{mm} mois", f"{jours_acquis(mm)} jours ouvrables"] for mm in (0, 1, 3, 6, 12)]
    iccp_jours = 12
    iccp = max(2500 * iccp_jours / 26, 2500 * 12 / 10 * iccp_jours / 30)
    corps = f"""
<h2>Maintien de salaire ou dixième : le plus favorable</h2>
<p>L'article L3141-24 du Code du travail impose deux calculs et le versement du plus élevé. La <strong>règle du dixième</strong> attribue un dixième de la rémunération brute de la période de référence (du 1er juin au 31 mai, sauf accord) pour l'ensemble des congés, au prorata des jours pris. Le <strong>maintien de salaire</strong> verse ce que vous auriez gagné en travaillant. Le dixième l'emporte dès que la période de référence comprend des heures supplémentaires, des primes mensuelles ou une augmentation récente.</p>
{table(["Salaire brut mensuel", "Rémunération de la période", "Maintien, 5 jours", "Dixième, 5 jours", "Le plus favorable"], lignes)}
{note("5 jours ouvrés de congés. Maintien calculé sur 21,67 jours ouvrés par mois en moyenne ; l'horaire réel du mois peut donner un résultat légèrement différent. Les lignes avec une rémunération supérieure à 12 salaires intègrent heures supplémentaires ou primes mensuelles.")}
<h2>L'exemple officiel</h2>
<p>Service-public.gouv.fr prend un salarié payé {e(s)} brut par mois, soit {e(annuel)} sur la période de référence, qui pose deux semaines de congés. Maintien de salaire : {e(s)} × 10 jours ÷ {jo} jours ouvrés du mois = <strong>{e2(maintien)}</strong>. Dixième : {e(annuel)} ÷ 10 × 10 ÷ 25 = <strong>{e2(dixieme)}</strong>. Le salarié reçoit {e2(max(maintien, dixieme))}.</p>
<h2>Indemnité compensatrice en fin de contrat</h2>
<p>Les congés acquis et non pris au départ sont payés sous forme d'indemnité compensatrice, quel que soit le motif de la rupture, y compris la faute lourde. Elle se calcule de la même façon, en comparant les deux méthodes. Exemple : 12 jours ouvrables restants pour {e(2500)} brut par mois donnent environ {e(iccp)} brut. Cette somme est imposable et soumise à cotisations ; elle retarde aussi le premier versement du chômage (différé congés payés, 30 jours au plus).</p>
<h2>Congés acquis pendant un arrêt maladie</h2>
<p>Depuis la loi du 22 avril 2024, un arrêt maladie d'origine non professionnelle ouvre droit à <strong>2 jours ouvrables par mois</strong>, dans la limite de 24 jours par période de référence ; un accident du travail ou une maladie professionnelle ouvre droit à 2,5 jours comme du travail effectif. L'employeur doit vous informer, dans le mois qui suit votre reprise, du nombre de jours acquis ; vous disposez ensuite de 15 mois pour les prendre. Pour l'indemnité, la rémunération de l'arrêt est retenue à 80 % (maladie ordinaire) ou à 100 % (origine professionnelle).</p>
{table(["Mois d'arrêt maladie dans l'année", "Congés acquis sur 12 mois"], l_acq)}
{note("Période de référence complète de 12 mois, maladie non professionnelle. Un nombre de jours non entier est arrondi à l'entier supérieur.")}
"""
    js = """
            var s = v('w-salaire'), an = v('w-annuel'), j = v('w-jours'), jo = v('w-jo'), mal = Math.min(v('w-maladie'), 12);
            var maintien = jo > 0 ? s * j / jo : 0;
            var dixieme = an / 10 * j / 25;
            out('r-maintien', centimes(maintien));
            out('r-dixieme', centimes(dixieme));
            out('r-du', centimes(Math.max(maintien, dixieme)));
            out('r-acquis', Math.min(Math.ceil((12 - mal) * 2.5 + Math.min(mal * 2, 24)), 30) + ' jours');"""
    citable = (f"En 2026, l'indemnité de congés payés est égale au plus favorable de deux montants. La règle du dixième donne un dixième de la rémunération brute de la période de référence pour 25 jours ouvrés de congés, au prorata des jours pris ; le maintien de salaire donne ce que le salarié aurait gagné en travaillant. "
               f"Pour {e(s)} brut par mois et deux semaines de congés, le maintien rapporte {e2(maintien)} et le dixième {e2(dixieme)} : l'employeur doit {e2(dixieme)}. "
               "Chaque mois de travail ouvre 2,5 jours ouvrables, soit 30 jours par an. Depuis la loi du 22 avril 2024, un arrêt maladie non professionnel ouvre 2 jours par mois, 24 au plus. Les congés non pris au départ sont payés par l'indemnité compensatrice, calculée de la même façon et due quel que soit le motif de la rupture.")
    return {
        "slug": "indemnite-conges-payes",
        "title": "Indemnité de congés payés 2026 : maintien ou dixième, calcul",
        "desc": "Indemnité de congés payés 2026 : comparez maintien de salaire et règle du dixième, indemnité compensatrice de fin de contrat, congés acquis en arrêt maladie.",
        "h1": "Indemnité de congés payés 2026",
        "crumb": "Congés payés",
        "widget_titre": "Indemnité de vos congés",
        "widget": widget([champ("w-salaire", "Salaire brut mensuel (€)", "2000"),
                          champ("w-annuel", "Brut de la période de référence (€)", "24000"),
                          champ("w-jours", "Jours ouvrés de congés", "10", "numeric"),
                          champ("w-jo", "Jours ouvrés du mois", "21", "numeric"),
                          champ("w-maladie", "Mois d'arrêt maladie dans l'année", "0", "numeric")],
                         [("r-maintien", "Maintien de salaire"), ("r-dixieme", "Règle du dixième"),
                          ("r-du", "Montant dû"), ("r-acquis", "Congés acquis sur l'année")],
                         "Montants bruts. Pour une indemnité compensatrice de fin de contrat, saisissez les jours restants."),
        "js": js,
        "citable": citable,
        "corps": corps,
        "sources": [SRC_CP_CALCUL, SRC_CP_COMPENSATRICE, SRC_CP_MALADIE, SRC_CT_L3141_24, SRC_FT_DIFFERE],
        "releve": RELEVE,
        "note_sources": "Les montants sont bruts : l'indemnité de congés payés supporte les mêmes cotisations que le salaire. Une convention collective peut prévoir des jours supplémentaires.",
        "faq": [
            ("Quelle méthode choisir entre maintien de salaire et dixième ?",
             "Vous n'avez pas à choisir : l'employeur doit faire les deux calculs et verser le résultat le plus élevé. Le maintien de salaire est souvent plus favorable juste après une augmentation, car il retient le salaire actuel. Le dixième l'emporte quand la période de référence comporte des heures supplémentaires, des primes mensuelles ou des commissions, qui gonflent la rémunération totale."),
            ("Combien de jours de congés payés acquiert-on par mois ?",
             "Un salarié acquiert 2,5 jours ouvrables par mois de travail effectif chez le même employeur, soit 30 jours ouvrables ou cinq semaines pour une année complète. En jours ouvrés, cela équivaut à 25 jours. Un nombre non entier est arrondi à l'entier supérieur. Les congés maternité, paternité, les accidents du travail et désormais les arrêts maladie ouvrent aussi des droits."),
            ("Acquiert-on des congés payés pendant un arrêt maladie ?",
             "Oui depuis le 24 avril 2024. Un arrêt pour maladie ou accident non professionnel ouvre 2 jours ouvrables par mois, dans la limite de 24 jours par période de référence. Un accident du travail ou une maladie professionnelle ouvre 2,5 jours par mois, sans limite de durée. L'employeur doit vous informer de vos droits dans le mois suivant la reprise, et vous avez 15 mois pour les poser."),
            ("Qu'est-ce que l'indemnité compensatrice de congés payés ?",
             "C'est le paiement des congés acquis et non pris lorsque le contrat prend fin, quel que soit le motif : démission, licenciement, rupture conventionnelle ou fin de CDD. Elle se calcule comme l'indemnité de congés payés, en comparant maintien de salaire et dixième. Elle figure sur le dernier bulletin, supporte les cotisations et retarde le premier versement de l'allocation chômage de 30 jours au plus."),
            ("Les primes comptent-elles dans le calcul des congés payés ?",
             "Celles qui rémunèrent le travail fourni pendant l'année, oui : prime d'ancienneté, prime d'assiduité mensuelle, majorations d'heures supplémentaires et de nuit, commissions, avantages en nature. Les primes versées pour l'année entière, travail et congés confondus, sont exclues : prime de fin d'année, intéressement, participation et prime de bilan. Les frais professionnels n'entrent jamais dans l'assiette."),
            ("Que devient le dixième pour un salarié à temps partiel ?",
             "La règle est la même : un dixième de la rémunération brute réellement perçue sur la période de référence. Un salarié à temps partiel acquiert autant de jours de congés qu'un salarié à temps plein, 2,5 jours ouvrables par mois, mais chaque jour est payé sur la base de sa rémunération réduite. Les heures complémentaires effectuées pendant la période augmentent le dixième."),
        ],
        "related": ["indemnite-preavis", "indemnite-rupture-conventionnelle", "indemnite-licenciement", "arret-maladie-salaire", "jours-rtt", "heures-supplementaires-brut-net"],
    }


PAGES = [page_rc, page_licenciement, page_are, page_preavis, page_cp]
