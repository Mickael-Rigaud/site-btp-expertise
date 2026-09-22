# -*- coding: utf-8 -*-
"""Réception de travaux : le rôle des réserves

Article du site btpexpertise.fr. Modifiez le texte entre les guillemets,
enregistrez avec Ctrl+S, puis lancez build.py et publier.py.

Tant que la ligne  "brouillon": True,  est presente, l'article n'existe
pas sur le site : ni page, ni vignette, ni plan du site. Supprimez-la
pour le mettre en ligne.
"""

ARTICLE = {
    "slug": "reception-travaux-reserves-garanties",
    "titre": ("Réception de travaux : pourquoi les réserves protègent "
              "vos garanties"),
    "titre_court": "Réception de travaux : le rôle des réserves",
    "date": "2026-08-11",
    "date_affichee": "11 août 2026",
    "image": "Reception-des-travaux.webp",
    "resume": (
        "La réception est l’acte juridique le plus important de votre chantier. Elle "
        "déclenche les garanties légales — et ferme la porte à tout ce que vous n’avez "
        "pas signalé ce jour-là."
    ),
    "meta_description": (
        "Réception de travaux : ce que déclenche la signature du procès-verbal, comment "
        "rédiger des réserves utiles et pourquoi se faire assister."
    ),
    "corps": [
        ("p", "Beaucoup de maîtres d’ouvrage considèrent la réception comme une formalité "
              "de fin de chantier. C’est en réalité <strong>l’acte juridique le plus "
              "important</strong> de toute l’opération."),
        ("h2", "Ce que la réception déclenche"),
        ("p", "La signature du procès-verbal de réception produit trois effets immédiats :"),
        ("ul", ["Le transfert de la garde de l’ouvrage : le bâtiment devient le vôtre, "
                "avec les risques associés",
                "Le point de départ des garanties légales : parfait achèvement un an, "
                "bon fonctionnement deux ans, décennale dix ans",
                "L’exigibilité du solde du marché, sous réserve de la retenue de garantie"]),
        ("citation", "Tant que la réception n’est pas prononcée, les garanties légales ne "
                     "courent pas. Une fois prononcée sans réserve, les défauts apparents "
                     "que vous n’avez pas signalés sont considérés comme acceptés."),
        ("h2", "La différence entre défaut apparent et défaut caché"),
        ("p", "C’est le point qui coûte le plus cher aux particuliers. Un <strong>défaut "
              "apparent</strong> — une fissure visible, un carrelage mal aligné, une porte "
              "qui frotte — devait être relevé le jour de la réception. Passé ce moment, "
              "il est réputé accepté."),
        ("p", "Un <strong>défaut caché</strong>, invisible lors de la réception, reste "
              "couvert par les garanties. Encore faut-il pouvoir démontrer qu’il ne "
              "pouvait pas être constaté ce jour-là — d’où l’intérêt d’un procès-verbal "
              "précis et documenté."),
        ("h2", "Rédiger des réserves qui tiennent"),
        ("p", "Une réserve utile est une réserve <strong>localisée, décrite et "
              "photographiée</strong>. « Peinture à revoir » n’engage à rien. « Chambre 2, "
              "mur nord : traces de reprise et défaut de planéité sur environ 2 m² » "
              "engage l’entreprise sur un périmètre identifiable."),
        ("ul", ["Situer précisément la pièce et l’élément concerné",
                "Décrire le désordre en termes techniques, pas en impressions",
                "Photographier chaque réserve, avec un repère d’échelle si possible",
                "Fixer un délai de reprise dans le procès-verbal",
                "Conserver la retenue de garantie jusqu’à la levée effective"]),
        ("h2", "Le cas de la réception tacite"),
        ("p", "Attention à une situation fréquente : prendre possession des lieux, "
              "emménager et régler le solde peut être interprété comme une "
              "<strong>réception tacite</strong>, sans aucune réserve. Le fait de ne pas "
              "avoir organisé de réunion de réception ne protège donc pas — au contraire."),
        ("h2", "Pourquoi se faire assister"),
        ("p", "Le jour de la réception, vous êtes seul face à des professionnels qui "
              "connaissent le vocabulaire, les tolérances admises et les DTU applicables. "
              "Un expert indépendant repère les défauts d’exécution qu’un œil non averti "
              "laisse passer, les formule dans les termes qui engagent, et vous évite de "
              "signer un document qui vous prive de vos recours."),
        ("citation", "Une réception de travaux se prépare. Le jour où vous signez, il est "
                     "déjà trop tard pour ajouter ce que vous n’avez pas vu."),
    ],
}
