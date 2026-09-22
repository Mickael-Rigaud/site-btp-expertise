# -*- coding: utf-8 -*-
"""Apercu du feed Instagram — les neuf premieres cases telles qu'on les verra.

La grille d'un profil se lit d'un coup d'oeil : c'est elle, plus que chaque
publication prise a part, qui donne l'impression de serieux. L'ordre choisi
ici alterne planche claire et carte sombre, case par case, pour que le damier
tienne meme quand les publications s'ajoutent trois par trois.

    python reseaux-sociaux/feed.py

Produit visuels/apercu-feed.png : l'en-tete du profil et la grille 3 x 3.
"""

import os
import sys

from PIL import Image, ImageDraw

DOSSIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DOSSIER)

from visuels import NUIT, BLEU, GRAS, DEMI, NORMAL, police  # noqa: E402

PLANCHES = os.path.join(DOSSIER, "visuels", "planches")
SORTIE = os.path.join(DOSSIER, "visuels")

FOND = (255, 255, 255)
GRIS = (110, 122, 145)
BORD = (223, 229, 238)

# De la publication la plus recente (en haut a gauche) a la plus ancienne.
# clair / sombre / clair, ligne apres ligne : le damier se maintient a mesure
# que de nouvelles publications poussent les anciennes vers le bas.
GRILLE = [
    "zones", "reunion", "plomberie",
    "independance", "avant-achat-planche", "expert-vs-immo",
    "avant-achat", "electricite", "litiges",
    "reception", "rapport", "etancheite",
    "humidite", "amo", "argiles",
    "malfacons", "fissures", "parcours",
    "honoraires", "visite-technique", "ouverture",
]

# La publication d'ouverture est la premiere publiee, donc la derniere case :
# c'est la seule qui rompt l'alternance, et les publications suivantes la
# pousseront de toute facon hors de la grille visible.

BIO = [
    "Expertise bâtiment & AMO — 06 et 83",
    "Fissures · infiltrations · malfaçons",
    "Avis technique indépendant",
    "Devis avant intervention ↓",  # le ⤵ de la vraie bio manque a Segoe UI
]


def entete(fond, dessin, largeur, marge):
    """Ce que voit le visiteur au-dessus de la grille."""
    profil = Image.open(os.path.join(SORTIE, "profil-1080.png")).convert("RGBA")
    taille = 168
    profil = profil.resize((taille, taille), Image.LANCZOS)
    masque = Image.new("L", (taille, taille), 0)
    ImageDraw.Draw(masque).ellipse([0, 0, taille - 1, taille - 1], fill=255)
    fond.paste(profil, (marge, marge), masque)
    dessin.ellipse([marge, marge, marge + taille, marge + taille], outline=BORD, width=2)

    x = marge + taille + 42
    dessin.text((x, marge + 4), "btpexpertise", font=police(DEMI, 34), fill=NUIT)

    chiffres = [("21", "publications"), ("—", "abonnés"), ("—", "abonnements")]
    xc = x
    for valeur, libelle in chiffres:
        dessin.text((xc, marge + 58), valeur, font=police(GRAS, 28), fill=NUIT)
        dessin.text((xc + 34, marge + 62), libelle, font=police(NORMAL, 24), fill=GRIS)
        xc += 34 + dessin.textlength(libelle, font=police(NORMAL, 24)) + 46

    y = marge + taille + 34
    dessin.text((marge, y), "BTP Expertise | Expert bâtiment 06-83",
                font=police(GRAS, 28), fill=NUIT)
    y += 42
    for ligne in BIO:
        dessin.text((marge, y), ligne, font=police(NORMAL, 27), fill=(60, 68, 88))
        y += 38
    dessin.text((marge, y + 2), "btpexpertise.fr", font=police(DEMI, 27), fill=BLEU)
    return y + 74


def composer():
    largeur = 1080
    marge, gouttiere = 34, 8
    cote = (largeur - 2 * marge - 2 * gouttiere) // 3

    hauteur = 1080  # provisoire, recalcule des que l'en-tete est mesure
    fond = Image.new("RGBA", (largeur, hauteur), FOND + (255,))
    bas_entete = entete(fond, ImageDraw.Draw(fond), largeur, marge)

    lignes = (len(GRILLE) + 2) // 3
    hauteur = int(bas_entete + lignes * cote + (lignes - 1) * gouttiere + marge)
    fond = Image.new("RGBA", (largeur, hauteur), FOND + (255,))
    dessin = ImageDraw.Draw(fond)
    bas_entete = entete(fond, dessin, largeur, marge)

    dessin.line([(0, bas_entete - 26), (largeur, bas_entete - 26)], fill=BORD, width=2)

    for i, cle in enumerate(GRILLE):
        case = Image.open(os.path.join(PLANCHES, "%s-1080.png" % cle)).convert("RGBA")
        case = case.resize((cote, cote), Image.LANCZOS)
        x = marge + (i % 3) * (cote + gouttiere)
        y = int(bas_entete + (i // 3) * (cote + gouttiere))
        fond.paste(case, (x, y))
        dessin.rectangle([x, y, x + cote - 1, y + cote - 1], outline=BORD, width=1)

    chemin = os.path.join(SORTIE, "apercu-feed.png")
    fond.convert("RGB").save(chemin)
    return chemin


if __name__ == "__main__":
    print(composer())
