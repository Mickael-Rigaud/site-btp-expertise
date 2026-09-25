# -*- coding: utf-8 -*-
"""
Contenu éditorial du site BTP Expertise.

C'est ici qu'on modifie les textes, les coordonnées, les villes et les pages.
Le rendu HTML est produit par build.py.

Les articles de conseils font exception : ils vivent chacun dans leur
fichier, dans le dossier articles/. Voir articles/A-LIRE.md.
"""

import os
import runpy


def charger_articles():
    """Lit un article par fichier dans articles/, du plus récent au plus ancien.

    Un fichier mal formé arrête la génération avec le nom du fichier fautif :
    mieux vaut un message clair qu'un article silencieusement absent du site.
    """
    dossier = os.path.join(os.path.dirname(os.path.abspath(__file__)), "articles")
    if not os.path.isdir(dossier):
        return []

    articles = []
    for nom in sorted(os.listdir(dossier)):
        if not nom.endswith(".py") or nom.startswith("_"):
            continue
        chemin = os.path.join(dossier, nom)
        try:
            espace = runpy.run_path(chemin)
        except Exception as erreur:
            raise SystemExit(
                "Article illisible : articles/%s\n  %s: %s\n"
                "Rouvrez ce fichier, la modification precedente l'a casse."
                % (nom, type(erreur).__name__, erreur)
            )
        if "ARTICLE" not in espace:
            raise SystemExit(
                "articles/%s ne definit pas ARTICLE = {...}" % nom
            )
        article = espace["ARTICLE"]
        article["fichier"] = nom
        articles.append(article)

    articles.sort(key=lambda a: a.get("date", ""), reverse=True)
    return articles


# ---------------------------------------------------------------------------
# Identité et coordonnées
# ---------------------------------------------------------------------------

SITE = {
    "nom": "BTP Expertise",
    "baseline": "Expertise bâtiment &amp; Assistance à Maîtrise d’Ouvrage",
    "domaine": "btpexpertise.fr",
    "url": "https://btpexpertise.fr",
    "fondateur": "Mickael Rigaud",

    "telephone": "06 81 65 15 91",
    "telephone_lien": "+33681651591",

    # Adresse affichée publiquement
    "adresse_rue": "18 Place Masséna",
    "adresse_cp": "06000",
    "adresse_ville": "Nice",
    "adresse_pays": "France",

    # E-mail mis en avant sur le site (boîte OVH à créer)
    "email": "contact@btpexpertise.fr",
    # Boîte de communication existante, utilisée pour recevoir les demandes
    # tant que la boîte OVH n'existe pas.
    "email_reception": "contact.btpexpertiseriviera@gmail.com",

    # Coordonnées géographiques de la place Masséna, pour les données structurées
    "latitude": "43.6976",
    "longitude": "7.2707",

    "horaires": "Du lundi au vendredi, 8h30 – 19h00",

    # Formulaire : adresse du script Google qui enregistre la demande,
    # range les photos dans Drive et envoie les deux courriels.
    # Voir backoffice/INSTALLATION.md pour l'obtenir.
    "form_action": "https://script.google.com/macros/s/AKfycbxGfCu-gWM9VL3yuyTxqcIwC2c5mpiNlscWFZrAXXwXqBatAHtkaK-V5iS2f7Q7ikjN/exec",
    # Doit etre identique au champ "jeton" de backoffice/Code.gs
    "jeton_formulaire": "btpx-2026-a7f3",

    # L'agenda est servi par le meme script que le formulaire : le site
    # demande les creneaux libres a "form_action" et y enregistre la
    # reservation. Aucun service exterieur.
}

DESCRIPTION_PIED = (
    "Cabinet d’expertise en bâtiment &amp; d’Assistance à Maîtrise d’Ouvrage, "
    "dans les Alpes-Maritimes et le Var."
)

DESCRIPTION_COURTE = (
    "BTP Expertise est un cabinet d’expertise en bâtiment &amp; d’Assistance à Maîtrise "
    "d’Ouvrage (AMO) "
    "indépendant intervenant auprès des particuliers et des professionnels. "
    "Spécialisé dans l’analyse des fissures, infiltrations, malfaçons et désordres "
    "structurels, le cabinet vous accompagne avec rigueur et objectivité dans la "
    "compréhension et la résolution de vos problématiques techniques."
)

# ---------------------------------------------------------------------------
# Zones d'intervention — référencement local
# ---------------------------------------------------------------------------

VILLES_06 = [
    "Nice", "Cannes", "Antibes", "Grasse", "Cagnes-sur-Mer", "Le Cannet",
    "Saint-Laurent-du-Var", "Menton", "Vallauris", "Mandelieu-la-Napoule",
    "Mougins", "Villeneuve-Loubet", "Valbonne – Sophia Antipolis", "Vence",
    "Biot", "Juan-les-Pins", "Beausoleil", "Roquebrune-Cap-Martin",
    "Saint-Jean-Cap-Ferrat", "Carros", "Mouans-Sartoux", "La Colle-sur-Loup",
]

VILLES_83 = [
    "Toulon", "La Seyne-sur-Mer", "Hyères", "Fréjus", "Draguignan",
    "Saint-Raphaël", "Six-Fours-les-Plages", "La Garde", "La Valette-du-Var",
    "Sanary-sur-Mer", "Bandol", "Brignoles", "Saint-Tropez", "Sainte-Maxime",
    "Le Lavandou", "Cavalaire-sur-Mer", "Ollioules", "Cogolin", "Le Muy",
    "Roquebrune-sur-Argens", "La Crau", "Saint-Cyr-sur-Mer",
]

# ---------------------------------------------------------------------------
# Villes prioritaires (§23) et référencement local (§24)
# ---------------------------------------------------------------------------
# Nice, Cannes et Antibes passent avant les autres communes. Chaque bloc décrit
# un parc immobilier réel et des désordres qui lui sont propres : le cahier des
# charges interdit explicitement les pages identiques où seul le nom change.

VILLES_PRIORITAIRES = [
    {
        "nom": "Nice",
        "cp": "06000",
        "titre": "Expert bâtiment à Nice",
        "chapo": (
            "Du Vieux-Nice aux collines de Cimiez et de Fabron, le parc niçois mêle "
            "immeubles anciens, copropriétés du front de mer et constructions des "
            "années 60-70."
        ),
        "desordres": [
            ("Fissures et désordres structurels",
             "Bâti ancien du Vieux-Nice, terrains en pente des collines et "
             "constructions sur remblai du bord de mer."),
            ("Humidité et infiltrations",
             "Remontées capillaires dans les rez-de-chaussée anciens, étanchéité "
             "des terrasses et toitures-terrasses exposées."),
            ("Malfaçons après rénovation",
             "Forte activité de rénovation dans l’ancien, souvent menée vite et "
             "sans contrôle indépendant avant réception."),
        ],
        "quartiers": [
            "Vieux-Nice", "Carré d’Or", "Cimiez", "Fabron", "Riquier",
            "Libération", "Saint-Isidore", "Mont-Boron",
        ],
        "slug": "nice",
        # Qualificatif du <title> : il doit tenir sous 70 caracteres
        "seo": "fissures et infiltrations",
        "meta": (
            "Expert bâtiment à Nice : fissures, infiltrations, malfaçons et "
            "assistance à maîtrise d’ouvrage. Vieux-Nice, Cimiez, Fabron, "
            "Mont-Boron. Rendez-vous sous 48 h."
        ),
        "contexte": [
            ("Nice n’a pas un parc immobilier, elle en a trois, et ils ne "
             "vieillissent pas de la même façon. Le centre historique aligne des "
             "immeubles des XVIII<sup>e</sup> et XIX<sup>e</sup> siècles, murs "
             "porteurs en maçonnerie hourdée à la chaux, planchers bois. Les "
             "collines — Cimiez, Mont-Boron, Fabron — sont bâties en pente, sur "
             "des terrains où le soutènement fait partie de la structure. Le "
             "front de mer et les quartiers gagnés sur le Paillon reposent en "
             "partie sur des remblais."),
            ("Dans l’ancien, les désordres les plus fréquents tiennent à l’eau "
             "et au temps : remontées capillaires dans les rez-de-chaussée sans "
             "coupure de capillarité, enduits ciment posés sur des murs qui "
             "respiraient à la chaux, planchers bois fragilisés par des fuites "
             "anciennes. Une fissure y raconte rarement la même histoire que "
             "dans une construction récente."),
            ("Sur les hauteurs, la question est presque toujours celle du sol et "
             "de l’eau qu’il reçoit. Un mur de soutènement qui se déverse, un "
             "drainage saturé après un épisode méditerranéen, une terrasse dont "
             "les eaux de ruissellement partent vers la construction plutôt que "
             "loin d’elle : les fissures apparaissent dans le bâtiment, la cause "
             "est souvent à l’extérieur."),
            ("Enfin, Nice est une ville où l’on rénove beaucoup, vite, et parfois "
             "sans contrôle indépendant avant la réception. C’est le moment où "
             "un regard technique coûte le moins cher et rapporte le plus : "
             "après la réception sans réserves, la charge de la preuve change "
             "de camp."),
        ],
        "faq": [
            ("Faut-il faire expertiser un appartement du Vieux-Nice avant de l’acheter ?",
             "C’est le secteur où cela se justifie le plus. Le diagnostic "
             "immobilier obligatoire du vendeur ne dit rien de l’état de la "
             "structure, des planchers ni des parties communes. Dans un immeuble "
             "ancien, ce sont précisément les postes qui coûtent cher : reprise "
             "de plancher, ravalement voté en assemblée, humidité structurelle."),
            ("J’ai des fissures sur un mur de soutènement à Cimiez, est-ce grave ?",
             "Cela dépend de leur orientation, de leur évolution et de ce que le "
             "mur retient. Un soutènement qui bouge peut entraîner le terrain, "
             "donc le bâti. Photographiez, datez, et faites constater avant la "
             "saison des pluies : c’est un désordre qui s’aggrave par épisodes, "
             "pas de façon continue."),
        ],
    },
    {
        "nom": "Cannes",
        "cp": "06400",
        "titre": "Expert bâtiment à Cannes",
        "chapo": (
            "Résidences balnéaires de la Croisette, copropriétés de La Bocca et "
            "villas des hauteurs : un parc très exposé au climat marin et à la "
            "pression locative saisonnière."
        ),
        "desordres": [
            ("Étanchéité et façades",
             "Exposition au sel et aux embruns, balcons et garde-corps des "
             "immeubles du front de mer."),
            ("Copropriétés et parties communes",
             "Désordres partagés, ravalements contestés, litiges entre "
             "copropriétaires et entreprises."),
            ("Expertise avant achat",
             "Marché tendu, décisions rapides : un regard technique avant de "
             "signer évite les mauvaises surprises."),
        ],
        "quartiers": [
            "La Croisette", "La Bocca", "Le Suquet", "Palm Beach",
            "Californie", "Petit Juas", "Républiques",
        ],
        "slug": "cannes",
        "seo": "étanchéité et copropriétés",
        "meta": (
            "Expert bâtiment à Cannes : étanchéité, façades, copropriétés et "
            "expertise avant achat. Croisette, La Bocca, Le Suquet, Californie. "
            "Rendez-vous sous 48 h."
        ),
        "contexte": [
            ("À Cannes, le climat marin est un acteur du chantier. Le sel porté "
             "par les embruns pénètre les bétons, atteint les armatures et les "
             "fait gonfler en rouillant : le béton éclate de l’intérieur. Sur le "
             "front de mer, ce phénomène concerne d’abord les ouvrages les plus "
             "exposés — nez de balcons, garde-corps scellés, appuis de fenêtre, "
             "sous-faces de loggias."),
            ("C’est pourquoi un éclat de béton laissant apparaître un fer rouillé "
             "ne se traite pas en rebouchant. Tant que l’armature n’est pas "
             "passivée et l’enrobage rétabli, le désordre repart. La différence "
             "entre une réparation qui tient vingt ans et une qui rouvre en deux "
             "hivers se joue là, et elle est invisible sur un devis."),
            ("L’autre particularité cannoise est la copropriété. Beaucoup de "
             "désordres y sont partagés : une infiltration dans un appartement "
             "vient souvent d’une terrasse, d’une façade ou d’une descente "
             "communes. La vraie question devient alors « qui doit payer », et "
             "elle se tranche sur des constats techniques, pas en assemblée. Un "
             "avis indépendant, rendu avant que les positions se figent, évite "
             "des années de blocage."),
            ("Enfin, le marché est tendu et les décisions se prennent vite, "
             "souvent sur des biens loués en saison, entretenus au fil de l’eau. "
             "Faire regarder un bien avant de signer n’est pas un luxe : c’est "
             "le seul moment où l’information a encore une valeur de négociation."),
        ],
        "faq": [
            ("Qui paie l’expertise quand le désordre touche les parties communes ?",
             "Si vous mandatez l’expertise à titre personnel, elle est à votre "
             "charge. Le syndicat des copropriétaires peut aussi la voter en "
             "assemblée, et elle est alors répartie selon les tantièmes. Beaucoup "
             "de copropriétaires commencent par une expertise personnelle pour "
             "savoir où ils en sont avant de porter le sujet en assemblée."),
            ("Un éclat de béton sur un balcon, faut-il agir tout de suite ?",
             "Oui, pour deux raisons. La corrosion des aciers ne s’arrête pas "
             "seule, et un morceau de béton qui se détache d’un balcon en étage "
             "pose une question de sécurité. Le constat sert aussi à qualifier "
             "le désordre : entretien courant ou atteinte à la solidité, ce qui "
             "ne relève pas des mêmes garanties."),
        ],
    },
    {
        "nom": "Antibes",
        "cp": "06600",
        "titre": "Expert bâtiment à Antibes",
        "chapo": (
            "Entre le cap d’Antibes, Juan-les-Pins et les quartiers résidentiels, "
            "villas individuelles et petites copropriétés dominent, avec beaucoup "
            "d’extensions et de piscines."
        ),
        "desordres": [
            ("Fissures sur maisons individuelles",
             "Sols argileux sensibles au retrait-gonflement, extensions mal "
             "désolidarisées du bâti existant."),
            ("Piscines, terrasses et extensions",
             "Travaux réalisés sans étude préalable, désordres d’étanchéité et "
             "de structure au raccordement."),
            ("Réception de travaux",
             "Chantiers de rénovation nombreux : les réserves formulées à la "
             "réception protègent vos garanties."),
        ],
        "quartiers": [
            "Cap d’Antibes", "Juan-les-Pins", "Vieil Antibes", "La Fontonne",
            "Les Semboules", "Badine", "Puy",
        ],
        "slug": "antibes",
        "seo": "fissures et extensions",
        "meta": (
            "Expert bâtiment à Antibes : fissures, extensions, piscines et "
            "réception de travaux. Cap d’Antibes, Juan-les-Pins, La Fontonne. "
            "Rendez-vous sous 48 h."
        ),
        "contexte": [
            ("Antibes est d’abord une ville de maisons. Villas du cap, pavillons "
             "de La Fontonne ou des Semboules, petites copropriétés de "
             "Juan-les-Pins : le bâti individuel domine, et avec lui une "
             "question qui revient sans cesse, celle des sols. Une partie du "
             "territoire repose sur des terrains argileux, sensibles au "
             "retrait-gonflement : ils se rétractent en période de sécheresse, "
             "gonflent au retour des pluies. Les fondations suivent, et la "
             "maison fissure."),
            ("Ce phénomène explique la forme des désordres qu’on y observe. Les "
             "fissures apparaissent en escalier dans les angles, au-dessus des "
             "ouvertures, ou à la jonction entre deux volumes construits à des "
             "époques différentes. Elles varient avec les saisons, ce qui trompe "
             "souvent : une fissure qui « se referme » en hiver n’est pas une "
             "fissure qui guérit."),
            ("Le point le plus fréquent reste le raccordement des extensions. "
             "Une véranda, un garage transformé, une pièce ajoutée : si le nouvel "
             "ouvrage n’est pas correctement désolidarisé de l’existant, les deux "
             "structures n’ont ni le même poids, ni les mêmes fondations, ni les "
             "mêmes mouvements. La fissure se forme exactement à la jonction, et "
             "elle est structurelle, pas esthétique."),
            ("Piscines et terrasses posent une question voisine. Creuser modifie "
             "les écoulements et décharge le terrain d’un côté ; une étanchéité "
             "de plage mal traitée envoie l’eau vers les fondations plutôt que "
             "vers un exutoire. Beaucoup de ces travaux sont réalisés sans étude "
             "de sol préalable, dans une région où elle est pourtant devenue "
             "déterminante."),
        ],
        "faq": [
            ("Ma véranda fissure à la jonction avec la maison, est-ce normal ?",
             "Un léger jeu au raccordement peut être admissible s’il a été prévu "
             "et traité par un joint de dilatation. Une fissure qui s’ouvre, "
             "traverse, ou laisse passer l’eau, non : elle signale que les deux "
             "ouvrages travaillent l’un contre l’autre. C’est le désordre le plus "
             "courant sur les extensions, et il relève souvent des garanties "
             "constructeur si les travaux sont récents."),
            ("Après une sécheresse, puis-je faire jouer la garantie catastrophe naturelle ?",
             "Uniquement si la commune fait l’objet d’un arrêté de catastrophe "
             "naturelle publié au Journal officiel pour la période concernée. "
             "L’arrêté ouvre le droit à indemnisation, il ne le garantit pas : "
             "il faut ensuite démontrer le lien entre la sécheresse et les "
             "désordres. C’est précisément ce qu’un constat technique établit."),
        ],
    },
]

# ---------------------------------------------------------------------------
# Les dix missions d'expertise (§6 du cahier des charges)
# ---------------------------------------------------------------------------
# "accueil" marque les cinq missions mises en avant sur la page d'accueil.
# "picto" renvoie à un tracé SVG défini dans build.py (PICTOS).
#
# ATTENTION : l'analyse des installations électriques ne doit jamais être
# présentée comme un diagnostic électrique réglementaire.

EXPERTISES = [
    {
        "id": "visite-technique",
        "image": "exp-avis-technique.webp",
        "image_alt": "Plans, loupe et rapport d’expertise sur une table",
        "titre": "Visite technique &amp; avis",
        "picto": "loupe",
        "icone": "Avis-Technique-Nice.webp",
        "accueil": True,
        "resume": (
            "Analyse ponctuelle d’une problématique permettant d’obtenir un avis "
            "technique professionnel."
        ),
        "texte": (
            "Vous avez un doute sur un désordre, un devis ou l’état d’un bien : nous "
            "nous déplaçons, observons et vous donnons un avis technique argumenté."
        ),
        "points": [
            "Déplacement sur site",
            "Observation et relevés",
            "Avis technique oral ou écrit",
            "Recommandations sur la suite à donner",
        ],
    },
    {
        "id": "malfacons",
        "image": "exp-malfacons.webp",
        "image_alt": "Mur fissuré examiné à la caméra thermique",
        "titre": "Malfaçons &amp; non-conformités",
        "picto": "loupe-defaut",
        "icone": "Recherche-malfacon.webp",
        "accueil": True,
        "resume": (
            "Identification des défauts de mise en œuvre, anomalies apparentes et "
            "analyse au regard des prescriptions techniques applicables."
        ),
        "texte": (
            "Nous examinons les travaux réalisés afin d’identifier les défauts de mise "
            "en œuvre et les anomalies apparentes, puis nous les analysons au regard "
            "des prescriptions techniques applicables."
        ),
        "points": [
            "Constat des anomalies apparentes",
            "Analyse au regard des DTU et règles de l’art",
            "Rapport photographique",
            "Préconisations de reprise",
        ],
    },
    {
        "id": "fissures",
        "image": "exp-fissures.webp",
        "image_alt": "Fissures sur une façade",
        "titre": "Fissures &amp; désordres",
        "picto": "fissure",
        "icone": "Expertise-technique.webp",
        "accueil": True,
        "resume": (
            "Observation, caractérisation et analyse des causes possibles des "
            "fissurations et désordres constatés."
        ),
        "texte": (
            "Toutes les fissures ne se valent pas. Nous les caractérisons, recherchons "
            "leurs causes probables et évaluons leur évolutivité afin d’orienter les "
            "décisions à prendre."
        ),
        "points": [
            "Caractérisation des fissures",
            "Recherche des causes probables",
            "Évaluation de l’évolutivité",
            "Orientation des travaux de reprise",
        ],
    },
    {
        "id": "humidite",
        "image": "exp-humidite.webp",
        "image_alt": "Traces d’humidité sur un mur intérieur",
        "titre": "Humidité &amp; infiltrations",
        "picto": "goutte",
        "icone": "Rapports-clairs-et-detailles.webp",
        "accueil": True,
        "resume": (
            "Recherche et analyse des phénomènes d’humidité, infiltrations, "
            "condensation, ventilation et de leurs origines probables."
        ),
        "texte": (
            "Traces, moisissures, salpêtre, condensation : nous recherchons l’origine "
            "réelle du phénomène avant d’engager des travaux souvent coûteux et parfois "
            "inadaptés."
        ),
        "points": [
            "Mesures d’humidité",
            "Analyse de la ventilation",
            "Recherche des origines probables",
            "Hiérarchisation des interventions",
        ],
    },
    {
        "id": "plomberie",
        "image": "exp-plomberie.webp",
        "image_alt": "Mesure de la pente d’une canalisation d’évacuation en "
                     "sous-sol : 1 degré relevé au niveau électronique",
        "titre": "Plomberie &amp; réseaux",
        "picto": "robinet",
        "icone": "Reactivite-disponibilite.webp",
        "accueil": False,
        "resume": (
            "Analyse des alimentations, évacuations, installations sanitaires, fuites, "
            "défauts de mise en œuvre et désordres affectant les réseaux."
        ),
        "texte": (
            "Nous analysons les alimentations, les évacuations et les installations "
            "sanitaires afin d’identifier les fuites, défauts de mise en œuvre et "
            "désordres affectant les réseaux."
        ),
        "points": [
            "Alimentations et évacuations",
            "Installations sanitaires",
            "Recherche de fuites apparentes",
            "Défauts de mise en œuvre",
        ],
    },
    {
        "id": "electricite",
        "image": "exp-electricite.webp",
        "image_alt": "Tableau électrique ouvert et ancien compteur, "
                     "contrôle visuel au multimètre",
        "titre": "Installations électriques",
        "picto": "eclair",
        "icone": "Avis-Technique-Nice.webp",
        "accueil": False,
        "resume": (
            "Analyse des tableaux, protections, circuits, mise à la terre, défauts de "
            "mise en œuvre et anomalies apparentes."
        ),
        "texte": (
            "Nous analysons les tableaux, protections, circuits et mises à la terre "
            "afin de relever les défauts de mise en œuvre et anomalies apparentes."
        ),
        "points": [
            "Tableaux et protections",
            "Circuits et mise à la terre",
            "Anomalies apparentes",
            "Points de vigilance",
        ],
        # Mention imposée par le cahier des charges : ce n'est pas un diagnostic
        # électrique réglementaire, et le site ne doit pas le laisser croire.
        "avertissement": (
            "Cette prestation constitue une analyse technique et ne remplace pas le "
            "diagnostic électrique réglementaire réalisé par un organisme certifié."
        ),
    },
    {
        "id": "avant-achat",
        "image": "exp-avant-achat.webp",
        "image_alt": "Remise de clés d’un logement",
        "titre": "Expertise avant achat",
        "picto": "cles",
        "icone": "Expertise-avant-achat-immobilier.webp",
        "accueil": True,
        "resume": (
            "Analyse technique indépendante d’un appartement ou d’une maison avant "
            "acquisition."
        ),
        "texte": (
            "Avant de signer, un regard technique indépendant vous évite les mauvaises "
            "surprises et vous donne des arguments pour négocier en connaissance de cause."
        ),
        "points": [
            "Visite technique du bien",
            "Relevé des désordres apparents",
            "Estimation des travaux à prévoir",
            "Compte rendu avant signature",
        ],
    },
    {
        "id": "litiges",
        "image": "exp-reunion.webp",
        "image_alt": "Réunion technique autour de plans",
        "titre": "Litiges travaux &amp; expertise amiable",
        "picto": "balance",
        "icone": "Reunion-contradictoire.webp",
        "accueil": False,
        "resume": (
            "Constat et analyse technique dans le cadre d’un différend relatif à des "
            "travaux."
        ),
        "texte": (
            "En cas de désaccord avec une entreprise, nous établissons un constat "
            "technique objectif et documenté, exploitable dans le cadre d’une résolution "
            "amiable du différend."
        ),
        "points": [
            "Constat technique documenté",
            "Analyse des responsabilités techniques",
            "Chiffrage des reprises",
            "Appui dans la résolution amiable",
        ],
    },
    {
        "id": "reception",
        "image": "exp-reception.webp",
        "image_alt": "Signature de documents de réception de travaux",
        "titre": "Assistance à réception",
        "picto": "presse-papier",
        "icone": "Reception-travaux.webp",
        "accueil": False,
        "resume": (
            "Accompagnement lors de la réception, identification des défauts apparents "
            "et assistance à la formulation des réserves."
        ),
        "texte": (
            "La réception est un moment décisif : c’est elle qui déclenche les garanties. "
            "Nous vous accompagnons pour identifier les défauts apparents et formuler "
            "des réserves précises."
        ),
        "points": [
            "Présence le jour de la réception",
            "Identification des défauts apparents",
            "Formulation des réserves",
            "Suivi de la levée des réserves",
        ],
    },
    {
        "id": "reunion-contradictoire",
        "image": "comp-maitrise-oeuvre.webp",
        "image_alt": "Plans annotés et casque de chantier",
        "titre": "Réunion contradictoire",
        "picto": "personnes",
        "icone": "Reunion-contradictoire.webp",
        "accueil": False,
        "resume": (
            "Assistance technique du client lors d’une réunion avec les entreprises, "
            "experts ou autres parties concernées."
        ),
        "texte": (
            "Face à une entreprise ou à un expert d’assurance, vous n’êtes pas sur un "
            "pied d’égalité technique. Nous vous assistons pour que vos arguments soient "
            "entendus et consignés."
        ),
        "points": [
            "Préparation du dossier technique",
            "Présence à la réunion",
            "Argumentation technique",
            "Compte rendu des échanges",
        ],
    },
]

# ---------------------------------------------------------------------------

ETAPES = [
    ("Premier contact &amp; étude du besoin",
     "Échange sur votre projet, vos problématiques techniques ou vos besoins "
     "d’accompagnement afin de définir la mission adaptée."),
    ("Analyse technique &amp; devis",
     "Étude de votre situation et élaboration d’une proposition claire adaptée à votre "
     "projet ou à votre chantier."),
    ("Planification &amp; organisation",
     "Validation de la mission, coordination des interventions et planification selon vos "
     "contraintes et disponibilités."),
    ("Intervention &amp; visite sur site",
     "Déplacement sur site pour réaliser les constats, relevés techniques, contrôles et "
     "observations nécessaires."),
    ("Suivi technique &amp; coordination",
     "Accompagnement des travaux, échanges avec les entreprises et suivi des différentes "
     "étapes du chantier."),
    ("Compte-rendu &amp; préconisations",
     "Remise d’un rapport, de recommandations techniques ou d’un suivi détaillé selon la "
     "mission réalisée."),
    ("Réception &amp; accompagnement final",
     "Assistance jusqu’à la réception des travaux et accompagnement dans les démarches ou "
     "décisions finales."),
]

# ---------------------------------------------------------------------------
# Les deux portes d'entrée : « J'ai un problème » / « J'ai un projet »
# ---------------------------------------------------------------------------
# Toute l'organisation commerciale du site repose sur ces deux besoins.
# Le visiteur doit comprendre l'activité du cabinet en quelques secondes.

HERO = {
    "label": "Expertise indépendante &amp; conseil technique sur la Côte d’Azur",
    "titre": "Expertise bâtiment &amp; <em>Assistance à Maîtrise d’Ouvrage</em>",
    "accroche": (
        "Un regard technique indépendant pour comprendre votre bâtiment, "
        "sécuriser vos travaux et défendre vos intérêts."
    ),
    "action_expertise": "J’ai besoin d’une expertise",
    "action_amo": "Je souhaite être accompagné dans mes travaux",
}

BESOINS = [
    {
        "besoin": "J’ai un problème",
        "metier": "Expertise bâtiment",
        "verbes": "Constater &nbsp;&middot;&nbsp; Analyser &nbsp;&middot;&nbsp; Préconiser",
        "texte": (
            "Fissures, humidité, malfaçons, plomberie, électricité, litiges, réception ou "
            "projet d’acquisition : BTP Expertise analyse votre situation et vous apporte "
            "un regard technique indépendant."
        ),
        "action": "Découvrir nos expertises",
        "url": "/expertises/",
        "teinte": "bleu",
    },
    {
        "besoin": "J’ai un projet",
        "metier": "Assistance à Maîtrise d’Ouvrage",
        "verbes": "Conseiller &nbsp;&middot;&nbsp; Sécuriser &nbsp;&middot;&nbsp; Accompagner",
        "texte": (
            "BTP Expertise vous accompagne dans la définition de votre projet, l’analyse "
            "des devis, le choix des entreprises, le déroulement des travaux et leur "
            "réception."
        ),
        "action": "Découvrir notre accompagnement AMO",
        "url": "/amo/",
        "teinte": "orange",
    },
]


# ---------------------------------------------------------------------------
# Honoraires (§16 à §19 du cahier des charges)
# ---------------------------------------------------------------------------
# Tarifs de départ, TTC, repris du Manuel opérationnel V5 (§2 et §3).
#
# Le manuel exprime ses montants HORS TAXES. Le site s'adresse d'abord à des
# particuliers, à qui le prix doit être annoncé toutes taxes comprises : les
# montants ci-dessous sont donc les montants HT du manuel majorés de 20 %.
# Le HT d'origine est rappelé en commentaire pour que la comparaison avec le
# manuel reste immédiate.
#
# La grille complète n'est affichée que sur la page Honoraires ; l'accueil
# n'en montre que trois lignes (§18).
#
# Chaque ligne : (intitulé, ce que la mission recouvre, tarif de départ TTC).

HONORAIRES_MENTION = (
    "Tarifs TTC à partir de, établis selon la nature de la mission, la surface "
    "du bien, la complexité du dossier et le lieu d’intervention. Un devis est "
    "établi avant toute intervention."
)

# L'AMO ne se chiffre pas au forfait : elle suit le montant des travaux.
AMO_MENTION = (
    "Les honoraires d’assistance à maîtrise d’ouvrage représentent de 5 à 8 % "
    "du montant HT des travaux, selon le montant, la durée, la complexité et le "
    "niveau d’accompagnement, avec un minimum d’honoraires de 3 500 € HT."
)

# Les trois seules lignes affichées sur l'accueil (§18)
HONORAIRES_ACCUEIL = [
    ("Expertise pré-achat", "à partir de 900 € TTC"),
    ("Expertise désordres &amp; malfaçons", "à partir de 1 200 € TTC"),
    ("Assistance à maîtrise d’ouvrage", "à partir de 5 % des travaux"),
]

# ---------------------------------------------------------------------------
# Rejoignez-nous : réseau de professionnels indépendants (§21)
# ---------------------------------------------------------------------------
# Formulation imposée : « réseau de professionnels indépendants ». Ne jamais
# laisser entendre qu'il s'agit de salariés du cabinet.

RESEAU_CHAPO = (
    "BTP Expertise développe un réseau de professionnels indépendants spécialisés "
    "dans les différentes disciplines du bâtiment afin de mobiliser les compétences "
    "adaptées aux spécificités de chaque dossier."
)

RESEAU_PROFILS = [
    "Experts bâtiment généralistes",
    "Ingénieurs structure",
    "Spécialistes fissures / structure",
    "Spécialistes humidité / étanchéité",
    "Thermiciens",
    "Économistes de la construction",
    "Spécialistes électricité",
    "Spécialistes plomberie",
    "Spécialistes couverture",
    "Spécialistes assainissement",
    "Autres spécialistes techniques",
]

# Les deux seuls départements où le cabinet intervient. Proposer les autres
# faisait candidater des experts hors zone, sans mission possible à la clé.
RESEAU_DEPARTEMENTS = [
    "Alpes-Maritimes (06)",
    "Var (83)",
]

RESEAU_EXPERIENCE = [
    "Moins de 5 ans",
    "5 à 10 ans",
    "10 à 20 ans",
    "Plus de 20 ans",
]

# ---------------------------------------------------------------------------
# Parcours en deux colonnes : Expertise à gauche, AMO à droite
# ---------------------------------------------------------------------------
# Repris du visuel fourni par Mickael Rigaud. Reproduit en HTML/CSS et non en
# image, pour rester lisible sur mobile et indexable par Google (§10).

PARCOURS_TITRE = "Deux expertises complémentaires, un seul objectif&nbsp;: <em>défendre vos intérêts</em>"
PARCOURS_CHAPO = (
    "Selon votre situation, nous intervenons en tant qu’expert indépendant ou "
    "vous accompagnons dans vos projets en toute transparence."
)

PARCOURS = [
    {
        "cle": "expertise",
        "titre": "Expertise bâtiment",
        "verbes": "Comprendre, constater, analyser, préconiser.",
        "phrase": "Un regard indépendant pour éclairer vos décisions.",
        "icone": "loupe",
        "etapes": [
            ("Prise de contact &amp; étude du dossier",
             "Échange sur votre problématique et analyse des documents transmis.",
             "dialogue"),
            ("Analyse &amp; préparation",
             "Étude de votre situation et définition du périmètre de l’expertise adaptée.",
             "liste"),
            ("Intervention sur site",
             "Déplacement pour réaliser les constats, relevés et observations nécessaires.",
             "maison"),
            ("Analyse technique",
             "Examen détaillé des désordres, recherche des causes et impacts.",
             "diagnostic"),
            ("Rédaction du rapport",
             "Remise d’un rapport clair et argumenté avec constats, causes et préconisations.",
             "rapport"),
            ("Restitution &amp; échanges",
             "Présentation du rapport et réponses à vos questions ou aux parties concernées.",
             "personnes"),
            ("Accompagnement suite à l’expertise",
             "Conseils pour la suite : réparations, échanges, négociations, actions à mener.",
             "poignee"),
        ],
    },
    {
        "cle": "amo",
        "titre": "Assistance à Maîtrise d’Ouvrage (AMO)",
        "verbes": "Conseiller, assister, contrôler, accompagner.",
        "phrase": "Vous aider à prendre les bonnes décisions à chaque étape.",
        "icone": "casque",
        "etapes": [
            ("Étude du besoin &amp; du projet",
             "Analyse de vos objectifs, contraintes, budget et faisabilité technique.",
             "cible"),
            ("Analyse des solutions &amp; estimations",
             "Étude des options possibles et estimation du coût global des travaux.",
             "calcul"),
            ("Consultation des entreprises",
             "Rédaction des pièces de consultation, envoi et collecte des offres.",
             "personnes"),
            ("Analyse comparative &amp; recommandations",
             "Comparaison des devis et conseils pour choisir les entreprises les plus adaptées.",
             "balance"),
            ("Accompagnement pendant les travaux",
             "Visites de chantier, contrôles visuels, suivi de l’avancement et assistance "
             "dans les échanges avec les entreprises.",
             "presse-papier"),
            ("Comptes rendus &amp; préconisations",
             "Rédaction de comptes rendus réguliers et recommandations si nécessaire.",
             "crayon"),
            ("Assistance à la réception",
             "Accompagnement lors de la réception des travaux et à la levée des réserves.",
             "valide"),
        ],
    },
]

PARCOURS_PIED = (
    "Indépendance, transparence et rigueur à chaque étape",
    "Un seul engagement : vous apporter des conseils objectifs et défendre vos intérêts.",
)

# ---------------------------------------------------------------------------
# Quatre blocs de réassurance et engagement d'indépendance
# ---------------------------------------------------------------------------
# L'absence de rémunération par les entreprises est la différenciation
# commerciale principale du cabinet : ne pas diluer cette formulation.

ENGAGEMENT = (
    "BTP Expertise n’est pas rémunéré par les entreprises intervenant sur les "
    "projets de ses clients."
)

REASSURANCE = [
    ("Expérience terrain",
     "Une connaissance concrète des métiers, techniques et problématiques du bâtiment."),
    ("Indépendance",
     "Un regard objectif au service des intérêts du client."),
    ("Analyse structurée",
     "Constats, photographies, analyses et préconisations selon la mission confiée."),
    ("Réactivité",
     "Interventions sur Nice, Cannes, Antibes et plus largement sur la Côte d’Azur."),
]

# ---------------------------------------------------------------------------
# Trois raisons de choisir le cabinet
# ---------------------------------------------------------------------------

RAISONS = [
    ("Expertise &amp; accompagnement technique",
     "Une analyse rigoureuse de vos projets, pathologies du bâtiment, travaux et "
     "problématiques techniques.",
     "Expertise-technique.webp"),
    ("Suivi de projet &amp; coordination",
     "Un accompagnement structuré pour le suivi des travaux, la coordination des "
     "intervenants et le contrôle qualité.",
     "Rapports-clairs-et-detailles.webp"),
    ("Réactivité &amp; proximité",
     "Une disponibilité constante et un interlocuteur unique pour vous accompagner à "
     "chaque étape de votre projet.",
     "Reactivite-disponibilite.webp"),
]

# ---------------------------------------------------------------------------
# Compétences techniques
# ---------------------------------------------------------------------------

COMPETENCES = [
    ("comp-maitrise-oeuvre.webp",
     "Assistance à Maîtrise d’Ouvrage",
     "Coordination des travaux, suivi des intervenants et contrôle qualité pour garantir "
     "le bon déroulement de votre projet."),
    ("comp-malfacons.webp",
     "Malfaçons et non-conformités",
     "Identification des défauts d’exécution, non-respect des règles de l’art ou des normes "
     "en vigueur. Analyse précise des désordres et préconisations techniques adaptées."),
    ("comp-infiltrations.webp",
     "Infiltrations et problèmes d’étanchéité",
     "Recherche de l’origine des infiltrations d’eau (toiture, façade, terrasse, "
     "menuiseries). Diagnostic technique pour identifier les causes et définir les "
     "solutions appropriées."),
    ("comp-fissures.webp",
     "Fissures et atteintes structurelles",
     "Analyse des fissurations des murs, planchers ou façades afin de déterminer leur "
     "origine, leur gravité et les risques potentiels pour la solidité de l’ouvrage."),
]

# ---------------------------------------------------------------------------
# Assistance à Maîtrise d'Ouvrage (AMO)
# ---------------------------------------------------------------------------
# Remplace l'ancienne offre de maîtrise d'œuvre. La distinction est juridique
# et non cosmétique : le cabinet conseille et assiste le maître d'ouvrage, qui
# reste décisionnaire et contracte directement avec les entreprises. Aucune
# formulation ne doit laisser entendre une direction des travaux, une mission
# OPC, ni une garantie de délais, de budget ou de bonne exécution.

AMO_TITRE = "Assistance à Maîtrise d’Ouvrage"
AMO_ACCROCHE = (
    "Un professionnel du bâtiment à vos côtés pour sécuriser votre projet de travaux."
)
# Exemples de projets accompagnés en AMO.
# ATTENTION : tant que ce ne sont pas de vraies photos de chantiers du cabinet,
# ne pas nommer de commune ni de client. Les libellés décrivent le type de projet
# et la nature de la mission, sans laisser croire à une référence identifiable.
# Voir §15 du cahier des charges : « Ne jamais publier d'éléments permettant
# d'identifier le client sans son autorisation. »

AMO_PROJETS = [
    ("projet-renovation.webp",
     "Rénovation complète",
     "Consultation des entreprises, analyse des devis et suivi jusqu’à la réception.",
     "Chantier de rénovation dans une bâtisse en pierre"),
    ("projet-incendie.webp",
     "Remise en état après sinistre",
     "Définition des travaux de reprise et accompagnement face aux intervenants.",
     "Reprise de cloisons après un incendie"),
    ("projet-fissures.webp",
     "Reprise de fissures",
     "Analyse des désordres, comparaison des solutions et contrôle des travaux.",
     "Fissures sur une façade"),
    ("projet-humidite.webp",
     "Traitement de l’humidité",
     "Recherche des causes, choix de l’entreprise et vérification des reprises.",
     "Traces d’humidité sur un mur intérieur"),
]

AMO = [
    ("Étude du projet",
     "Analyse des besoins, objectifs, contraintes et priorités."),
    ("Définition des travaux",
     "Assistance dans la définition des prestations nécessaires."),
    ("Consultation des entreprises",
     "Accompagnement dans la recherche et la consultation des professionnels."),
    ("Analyse des devis",
     "Comparaison technique et financière des propositions."),
    ("Aide au choix des entreprises",
     "Analyse des offres et conseil au maître d’ouvrage avant sa décision."),
    ("Accompagnement pendant les travaux",
     "Visites sur site et observations techniques."),
    ("Contrôle visuel de la qualité apparente",
     "Identification des anomalies apparentes et points nécessitant une attention particulière."),
    ("Comptes rendus &amp; conseils",
     "Synthèse des observations, points de vigilance et recommandations."),
    ("Assistance à réception",
     "Accompagnement lors de la réception et assistance à la formulation des réserves."),
]

# Cadre de l'intervention — à afficher sur la page AMO. Protège le cabinet et
# évite toute confusion avec une mission de maîtrise d'œuvre.

AMO_PRINCIPE = (
    "BTP Expertise conseille et assiste le maître d’ouvrage. Le maître d’ouvrage reste "
    "décisionnaire et contracte directement avec les entreprises."
)

AMO_EXCLUSIONS = [
    "la direction des travaux",
    "les ordres d’exécution aux entreprises",
    "les plans d’exécution",
    "la direction de l’exécution",
    "une mission d’ordonnancement, pilotage et coordination (OPC)",
    "la garantie des délais",
    "la garantie du budget final",
    "la garantie de bonne exécution des entreprises",
]

# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------

FAQ = [
    ("Dans quels cas faire appel à un expert en bâtiment ?",
     ["Il est recommandé de faire appel à un expert en bâtiment en cas de fissures, "
      "infiltrations, malfaçons, litiges avec un constructeur ou après un sinistre. "
      "L’expert analyse la situation de manière indépendante et vous aide à comprendre "
      "l’origine des désordres ainsi que les solutions possibles."]),
    ("Quelle est la différence entre un expert d’assurance et un expert bâtiment ?",
     ["L’expert d’assurance intervient pour le compte de la compagnie d’assurance.",
      "L’expert bâtiment, lui, défend exclusivement vos intérêts. Il vous accompagne de "
      "manière neutre et objective dans l’analyse technique de votre bien et peut vous "
      "assister en cas de désaccord."]),
    ("Comment se déroule une expertise ?",
     ["L’expertise comprend généralement une visite sur site, l’analyse des désordres "
      "constatés, l’identification des causes probables et la rédaction d’un rapport "
      "détaillé. Ce rapport vous sert à comprendre la situation, à dialoguer avec les "
      "entreprises et à décider de la suite à donner."]),
    ("Le rapport d’expertise est-il utilisable en justice ?",
     ["Oui. Un rapport d’expertise peut servir de base technique dans une "
      "procédure judiciaire. Il permet d’appuyer votre dossier avec des éléments factuels "
      "et techniques. Toutefois, seul le juge peut désigner un expert judiciaire si "
      "nécessaire."]),
    ("Quelle est la différence entre un expert immobilier et un expert bâtiment ?",
     ["Ces deux métiers répondent à des questions différentes. L’<strong>expert immobilier</strong> estime la <strong>valeur vénale</strong> d’un bien : combien il vaut "
      "sur le marché, au regard de son emplacement, de sa surface et des transactions "
      "comparables. Son travail relève de l’évaluation financière.",
      "L’<strong>expert bâtiment</strong> analyse l’<strong>état technique</strong> de la construction : origine des fissures, causes d’une infiltration, conformité des travaux "
      "réalisés, désordres apparents et risques d’évolution. Son travail relève du diagnostic technique.",
      "Concrètement : pour savoir à quel prix vendre ou acheter, c’est un expert immobilier. Pour savoir si le bâtiment présente des désordres, ce qu’ils coûteront à "
      "reprendre et qui en est responsable, c’est un expert bâtiment. Les deux sont "
      "complémentaires : une expertise technique avant achat éclaire d’ailleurs souvent "
      "la négociation du prix."]),
    ("Intervenez-vous uniquement en cas de sinistre ?",
     ["Non. L’expertise peut également intervenir en prévention, par exemple avant un achat "
      "immobilier, lors de la réception de travaux ou pour vérifier la conformité d’un "
      "chantier. Une analyse en amont permet souvent d’éviter des litiges coûteux."]),
    ("Intervenez-vous dans le Var et les Alpes-Maritimes ?",
     ["Oui. Le cabinet intervient sur l’ensemble des Alpes-Maritimes (06) et du Var (83), "
      "de Menton à Saint-Cyr-sur-Mer, ainsi que plus largement en région "
      "Provence-Alpes-Côte d’Azur. Nice, Cannes, Antibes, Grasse, Toulon, Hyères, Fréjus "
      "ou Draguignan font partie de nos secteurs d’intervention habituels."]),
    ("Sous quel délai intervenez-vous ?",
     ["Nous revenons vers vous sous 24 à 48 heures ouvrées après réception de votre demande. "
      "Le délai de visite sur site dépend de la nature de la mission et de l’urgence de la "
      "situation ; les désordres évolutifs sont traités en priorité."]),
]

# ---------------------------------------------------------------------------
# Formulaire de demande
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Prise de rendez-vous : parcours court, avant de detailler le projet
# ---------------------------------------------------------------------------
# Le cabinet confirme le creneau : rien n'est reserve automatiquement, ce qui
# evite de bloquer un deplacement sur une demande non qualifiee.

FORMATS_RDV = [
    ("telephone", "Échange téléphonique", "30 minutes",
     "Mickael vous appelle au créneau choisi pour cerner votre situation."),
    ("visio", "Visioconférence", "30 minutes",
     "Pratique si vous disposez déjà de photos, de devis ou de documents à montrer."),
]

# Le formulaire est un outil de qualification (§20) : d'abord le besoin
# (expertise ou AMO), puis la problématique, puis les informations.

BESOINS_DEMANDE = [
    "Expertise bâtiment",
    "Assistance à Maîtrise d’Ouvrage",
]

# La liste des demandes dépend du besoin choisi juste avant.
# Côté AMO, ce sont les missions de la page /amo/ : la liste se met donc à jour
# toute seule si les missions évoluent.
DEMANDES_PAR_BESOIN = {
    "Expertise bâtiment": [
        "Fissures",
        "Humidité / infiltration",
        "Malfaçons / non-conformités",
        "Plomberie",
        "Électricité",
        "Litige travaux",
        "Avant achat",
        "Réception de travaux",
        "Autre",
    ],
    "Assistance à Maîtrise d’Ouvrage": [titre for titre, _ in AMO] + ["Autre"],
}

# Conservée pour les pages qui citent l'ensemble des sujets traités.
PROBLEMATIQUES = DEMANDES_PAR_BESOIN["Expertise bâtiment"]

TYPES_BIEN = [
    "Appartement",
    "Maison individuelle",
    "Villa",
    "Immeuble / copropriété",
    "Local professionnel",
    "Autre",
]

# Conservées pour la prise de rendez-vous, qui reste volontairement courte.
TYPES_DEMANDE = [
    "Expertise bâtiment",
    "Assistance à Maîtrise d’Ouvrage (AMO)",
    "Analyse de devis",
    "Expertise avant achat",
    "Assistance à réception",
]

# ---------------------------------------------------------------------------
# Article de conseils
# ---------------------------------------------------------------------------

# Les articles vivent chacun dans leur fichier, dans le dossier articles/.
# Un fichier = un article. Voir articles/A-LIRE.md.
ARTICLES = charger_articles()


# ---------------------------------------------------------------------------
# Règlement en ligne
# ---------------------------------------------------------------------------
# Chaque montant correspond à un lien de paiement créé dans le tableau de bord
# Stripe (Paiements → Liens de paiement). Tant qu'un lien vaut "A_CONFIGURER",
# le bouton correspondant est désactivé et affiche un message.

PAIEMENT = {
    # Lien à montant libre, pour régler une somme indiquée sur la lettre de mission
    "lien_libre": "A_CONFIGURER",

    # Un règlement par mission, au tarif de départ de la grille des honoraires.
    # Chaque "lien" recevra l'adresse d'un lien de paiement Stripe ; tant qu'il
    # vaut A_CONFIGURER, le bouton affiche « Bientôt disponible ».
    # La grille des missions, et le seul endroit où elle vit.
    #
    # Chaque prestation : ce qu'elle recouvre (« etapes »), ce que le client
    # reçoit (« livrable »), et son tarif de départ.
    #
    # Trois formes de tarif, que la page sait distinguer :
    #   "900 €"       un montant de départ, réglable en ligne
    #   "5 %"         une part des travaux — ni « TTC », ni bouton de paiement
    #   "Sur devis"   ni l'un ni l'autre
    # « lien » ne sert qu'aux montants fixes ; tant qu'il vaut A_CONFIGURER,
    # le bouton affiche « Bientôt disponible ».
    "prestations": [
        ("Expertise bâtiment", [
            {
                "nom": "Expertise pré-achat",
                "etapes": ["Inspection technique du bien",
                           "Identification des anomalies et points de vigilance",
                           "Travaux à anticiper"],
                "livrable": "Rapport de synthèse",
                "tarif": "900 €",
                "lien": "A_CONFIGURER",
            },
            {
                "nom": "Expertise désordres &amp; malfaçons",
                "etapes": ["Constat des désordres",
                           "Analyse des causes probables",
                           "Préconisations techniques"],
                "livrable": "Rapport d’expertise détaillé",
                "tarif": "1 200 €",
                "lien": "A_CONFIGURER",
            },
            {
                "nom": "Assistance à réception de travaux",
                "etapes": ["Contrôle des travaux réalisés",
                           "Identification des défauts et non-conformités apparentes",
                           "Aide à la formulation des réserves"],
                "livrable": "Relevé des réserves",
                "tarif": "750 €",
                "lien": "A_CONFIGURER",
            },
        ]),
        ("Assistance à Maîtrise d’Ouvrage", [
            {
                "nom": "AMO ciblée",
                "etapes": ["Périmètre limité, peu de lots",
                           "Durée courte, accompagnement contenu"],
                "tarif": "5 %",
                "lien": "",
            },
            {
                "nom": "AMO étendue",
                "etapes": ["Plusieurs lots, accompagnement régulier",
                           "Durée intermédiaire"],
                "tarif": "Sur devis",
                "lien": "",
            },
            {
                "nom": "AMO importante",
                "etapes": ["Nombreux lots, longue durée",
                           "Complexité ou interfaces élevées"],
                "tarif": "Sur devis",
                "lien": "",
            },
        ]),
    ],
}


# ---------------------------------------------------------------------------
# Intelligence artificielle — à faire valider par le cabinet
# ---------------------------------------------------------------------------
# Décrire ici les usages RÉELS. Ne rien déclarer qui ne soit pas pratiqué :
# cette mention engage la responsabilité du cabinet.

IA = {
    "utilisee": True,
    "usages": [
        "l’aide à la rédaction et à la relecture des rapports d’expertise "
        "(orthographe, structure, cohérence des constats) ;",
        "le classement et la synthèse des pièces reçues dans un dossier "
        "(courriers, devis, photographies, procès-verbaux) ;",
        "la préparation de courriers et de comptes rendus.",
    ],
    "jamais": [
        "l’analyse technique des désordres et la détermination de leurs causes ;",
        "les conclusions et préconisations du rapport ;",
        "l’évaluation des responsabilités ou des montants de reprise.",
    ],
}

# ---------------------------------------------------------------------------
# Mentions légales — champs à compléter par le cabinet
# ---------------------------------------------------------------------------

LEGAL = {
    "raison_sociale": "BTP Expertise",
    "forme_juridique": "Société par actions simplifiée (SAS)",
    "siren": "954 043 295",
    "tva": "FR76954043295",
    # Mentions obligatoires pour une societe : les deux lignes apparaissent
    # dans les mentions legales des qu'elles sont renseignees.
    "capital": "",          # ex. "5 000 €" — A COMPLETER
    # Societe recemment creee : l'immatriculation est annoncee en cours plutot
    # que passee sous silence. A remplacer par "RCS <greffe> 954 043 295".
    "rcs": "En cours",
    "directeur_publication": SITE["fondateur"],
    # Le jour où le contrat est signé : remplacer par le nom de l'assureur et
    # le numéro de contrat. La ligne « N° de contrat » réapparaît toute seule
    # dès qu'elle n'est plus vide, et la clause Assurance des CGV se remet
    # d'elle-même en affirmatif (voir build.py).
    "assurance_nom": "Souscription en cours",
    "assurance_contrat": "",
    "assurance_couverture": "France métropolitaine",
    "hebergeur_nom": "OVH SAS",
    "hebergeur_adresse": "2 rue Kellermann, 59100 Roubaix, France",
    "hebergeur_tel": "1007",
    "hebergeur_site": "https://www.ovhcloud.com",
    "date_maj": "3 septembre 2026",
}
