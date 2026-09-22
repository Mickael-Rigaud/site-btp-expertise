# -*- coding: utf-8 -*-
"""Étanchéité : se préparer aux pluies d’automne

Article du site btpexpertise.fr. Modifiez le texte entre les guillemets,
enregistrez avec Ctrl+S, puis lancez build.py et publier.py.

Tant que la ligne  "brouillon": True,  est presente, l'article n'existe
pas sur le site : ni page, ni vignette, ni plan du site. Supprimez-la
pour le mettre en ligne.
"""

ARTICLE = {
    "slug": "episodes-mediterraneens-preparer-toiture-etancheite",
    "titre": ("Épisodes méditerranéens : vérifier son étanchéité "
              "avant les pluies d’automne"),
    "titre_court": "Étanchéité : se préparer aux pluies d’automne",
    "date": "2026-09-04",
    "date_affichee": "4 septembre 2026",
    "image": "conseil-etancheite.webp",
    "resume": (
        "L’automne 2026 s’annonce plus humide que la normale sur le pourtour "
        "méditerranéen. Les semaines qui viennent sont le bon moment pour vérifier "
        "toitures, évacuations et relevés d’étanchéité — avant que le premier gros "
        "épisode ne révèle les faiblesses."
    ),
    "meta_description": (
        "Avant les pluies d’automne dans le 06 et le 83 : les points d’étanchéité à "
        "vérifier sur une toiture-terrasse, une couverture et des évacuations."
    ),
    "corps": [
        ("p", "Sur la Côte d’Azur, la saison des pluies intenses s’ouvre à la fin de "
              "l’été et se prolonge jusqu’en novembre. Cette année, les modèles "
              "annoncent un automne plus humide que la normale sur le bassin "
              "méditerranéen, avec une instabilité croissante à partir de la fin "
              "septembre. Le Var et les Alpes-Maritimes ont déjà connu un épisode "
              "orageux en vigilance orange le 20 août, avec des cumuls de 40 à 60 "
              "millimètres par heure."),
        ("p", "Ces quelques semaines avant les premiers gros épisodes sont le moment "
              "utile pour regarder son bâtiment. Une fois l’eau entrée, on ne répare "
              "plus : on constate."),

        ("h2", "Pourquoi le bâti local encaisse mal ces pluies"),
        ("p", "Un épisode méditerranéen ne ressemble pas à une pluie ordinaire. Il "
              "déverse en une heure ce que la région reçoit parfois en un mois. Trois "
              "caractéristiques du bâti régional rendent ce phénomène redoutable :"),
        ("ul", ["<strong>Les toitures-terrasses</strong>, très répandues sur le "
                "littoral, évacuent par un nombre limité de descentes. Une seule "
                "obstruée, et l’eau stagne sur plusieurs centimètres.",
                "<strong>Les terrains en pente</strong>, du Mont-Boron aux collines de "
                "Grasse ou de l’arrière-pays varois, concentrent le ruissellement vers "
                "les constructions situées en contrebas.",
                "<strong>Les extensions et vérandas</strong> ajoutées après coup, dont "
                "le raccordement à l’existant est le point faible classique."]),
        ("p", "S’ajoute un effet moins visible : après un été sec, les sols argileux "
              "sont rétractés et fissurés. Ils absorbent mal les premières pluies, qui "
              "ruissellent au lieu de s’infiltrer."),

        ("h2", "Ce qu’on peut vérifier soi-même, depuis le sol"),
        ("p", "Sans monter sur un toit — ce qui reste dangereux et doit être laissé à "
              "des professionnels équipés — plusieurs points s’observent depuis le sol "
              "ou une fenêtre :"),
        ("ul", ["<strong>Les évacuations pluviales</strong> : gouttières encombrées de "
                "feuilles ou d’aiguilles de pin, crapaudines absentes, descentes "
                "fendues ou désolidarisées du mur.",
                "<strong>Les traces sur les façades</strong> : coulures verticales sous "
                "un débord de toiture, auréoles au pied des murs, salpêtre.",
                "<strong>Les appuis de fenêtre</strong> : un rejingot usé ou une pente "
                "insuffisante laisse l’eau revenir vers la menuiserie.",
                "<strong>Les abords</strong> : regards obstrués, terrain qui a pris de "
                "la pente vers la maison, seuil de porte au niveau du sol.",
                "<strong>Les plafonds des pièces sous toiture</strong> : une auréole "
                "sèche, même ancienne, signale un chemin d’eau déjà emprunté."]),
        ("citation", "Une auréole ancienne n’est pas une trace du passé : c’est le "
                     "signe qu’un chemin existe. Il se rouvrira au prochain épisode "
                     "important."),

        ("h2", "Les points qui demandent un regard technique"),
        ("p", "D’autres vérifications supposent un accès et une lecture de "
              "professionnel. Sur une toiture-terrasse, l’état des <strong>relevés "
              "d’étanchéité</strong> — la remontée du revêtement le long des murs et "
              "des acrotères — est déterminant : c’est là que l’eau passe le plus "
              "souvent. Leur hauteur, leur fixation en tête et leur état de "
              "vieillissement se contrôlent de près."),
        ("p", "Sur une couverture en tuiles, on regarde les solins contre les "
              "souches de cheminée, la zinguerie des noues, les tuiles déplacées par "
              "le vent des derniers épisodes, et l’état de l’écran sous toiture "
              "lorsqu’il est visible depuis les combles."),
        ("p", "Enfin, sur les bâtiments récents ou rénovés, la conformité de "
              "l’exécution se vérifie au regard des règles de l’art applicables. Une "
              "étanchéité mal relevée ou une évacuation sous-dimensionnée n’est pas "
              "une fatalité climatique : c’est un défaut de mise en œuvre, et cela "
              "change tout pour la suite."),

        ("h2", "Après un épisode : les réflexes qui comptent"),
        ("p", "Si de l’eau est entrée, l’urgence est de se mettre en sécurité et de "
              "limiter les dégâts. Mais dès que la situation le permet, trois gestes "
              "conditionnent la suite du dossier :"),
        ("ul", ["<strong>Photographier</strong> largement et tout de suite : les "
                "traces, les niveaux atteints, les biens touchés, avant tout "
                "nettoyage ou assèchement.",
                "<strong>Déclarer le sinistre à l’assureur</strong> dans les délais de "
                "votre contrat, sans attendre de savoir d’où vient l’eau.",
                "<strong>Vérifier l’arrêté de catastrophe naturelle</strong> pour votre "
                "commune : sa publication au Journal officiel ouvre un délai "
                "spécifique pour déclarer."]),
        ("p", "La question de l’origine — défaut d’entretien, malfaçon, événement "
              "exceptionnel — se tranche après, sur la base de constats. Elle "
              "détermine qui prend en charge quoi, et c’est souvent là que les avis "
              "divergent."),

        ("h2", "Quand faire appel à un expert"),
        ("p", "Un regard technique indépendant se justifie dans trois situations : "
              "avant la saison, pour savoir où vous en êtes et hiérarchiser les "
              "travaux ; après un sinistre, pour établir un constat objectif de "
              "l’origine et de l’étendue des désordres ; en cas de désaccord, lorsque "
              "l’expert de la compagnie d’assurance conclut à un défaut d’entretien "
              "et que vous n’êtes pas de cet avis."),
        ("p", "Dans ce dernier cas, l’écart est rarement une question de mauvaise foi : "
              "l’expert d’assurance travaille pour son mandant, et vous n’avez pas "
              "les mêmes moyens techniques pour défendre votre lecture des faits."),
        ("citation", "Vérifier avant coûte le prix d’une visite. Constater après, une "
                     "fois l’eau passée, coûte le prix des travaux — et parfois celui "
                     "d’un litige."),
    ],
}
