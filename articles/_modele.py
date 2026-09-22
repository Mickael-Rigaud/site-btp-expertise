# -*- coding: utf-8 -*-
"""MODÈLE — ne pas modifier ce fichier.

Son nom commence par un souligné, donc il est ignoré par le site.
Pour écrire un nouvel article : copiez-le, renommez la copie en
    AAAA-MM-JJ-titre-en-minuscules-avec-des-tirets.py
et remplissez les champs ci-dessous.
"""

ARTICLE = {
    # Tant que cette ligne est là, l'article n'existe pas sur le site.
    # Supprimez-la quand Mickael a validé.
    "brouillon": True,

    # Adresse de la page : /conseils/<slug>/
    # Uniquement des minuscules, des chiffres et des tirets.
    "slug": "titre-court-en-minuscules-avec-des-tirets",

    # Titre complet, affiché en haut de l'article
    "titre": "Le titre complet de l’article",

    # Version courte, pour la vignette et le fil d'Ariane (60 caractères max)
    "titre_court": "Titre court",

    "date": "2026-01-01",
    "date_affichee": "1er janvier 2026",

    # Image d'en-tête, à déposer dans site/assets/img/
    "image": "conseil-nom-de-limage.webp",

    # Résumé affiché sous la vignette, 2 à 3 phrases
    "resume": (
        "Deux ou trois phrases qui donnent envie de lire, et qui disent "
        "concrètement ce que le lecteur va y gagner."
    ),

    # Phrase affichée par Google sous le titre (155 caractères environ)
    "meta_description": (
        "Ce que contient l’article, avec le département ou la ville quand "
        "c’est pertinent."
    ),

    # Le corps de l'article. Chaque ligne est un bloc, dans l'ordre.
    # Types disponibles :
    #   "p"        un paragraphe
    #   "h2"       un titre de section
    #   "h3"       un sous-titre
    #   "ul"       une liste à puces (une liste Python de phrases)
    #   "citation" une phrase mise en avant
    #   "image"    insère l'image nommée par la clé indiquée, ici "image"
    "corps": [
        ("p", "Le paragraphe d’introduction : le contexte, et pourquoi le "
              "sujet se pose maintenant."),

        ("h2", "Un titre de section"),
        ("p", "Un paragraphe."),
        ("ul", ["Un premier point, avec du <strong>gras</strong> si utile.",
                "Un deuxième point.",
                "Un troisième point."]),

        ("h2", "Une autre section"),
        ("p", "Un paragraphe."),
        ("citation", "Une phrase forte, mise en avant dans un encadré."),

        ("h2", "Ce qu’il faut retenir"),
        ("p", "La conclusion, sans promesse de résultat ni démarchage."),
    ],
}
