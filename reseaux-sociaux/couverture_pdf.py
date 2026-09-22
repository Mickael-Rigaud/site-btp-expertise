# -*- coding: utf-8 -*-
"""Couverture Facebook au format PDF, pour reprise dans Canva.

Contrairement au PNG, chaque element reste un objet separe :
la photo, le voile bleu nuit, le logo, et surtout les textes, qui sont du
vrai texte vectoriel et non des pixels. Canva les rouvre donc en objets
modifiables.

    python reseaux-sociaux/couverture_pdf.py

Produit reseaux-sociaux/visuels/couverture-facebook.pdf (1640 x 664 points,
soit exactement le format demande par Facebook a 72 ppp) et un apercu PNG.
"""

import os
import sys

import fitz  # PyMuPDF

DOSSIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DOSSIER)

from visuels import NUIT, BLEU, ORANGE, BLANC, couvrir, image  # noqa: E402

SORTIE = os.path.join(DOSSIER, "visuels")
LARGEUR, HAUTEUR = 1640, 664

POLICES = {
    "demi": "C:/Windows/Fonts/seguisb.ttf",
    "normal": "C:/Windows/Fonts/segoeui.ttf",
}


def couleur(rvb):
    """PyMuPDF attend des composantes entre 0 et 1."""
    return tuple(c / 255 for c in rvb)


def ecrire(page, texte, fonte, taille, y, teinte):
    """Ecrit une ligne centree horizontalement, y etant la ligne de base."""
    police = fitz.Font(fontfile=POLICES[fonte])
    largeur = police.text_length(texte, fontsize=taille)
    plume = fitz.TextWriter(page.rect)
    plume.append(fitz.Point((LARGEUR - largeur) / 2, y), texte, font=police, fontsize=taille)
    plume.write_text(page, color=couleur(teinte))


def construire():
    # La photo de fond est le seul element qui reste une image : recadree
    # au format exact, elle est posee telle quelle sous le voile.
    fond = couvrir(image("hand-construction-plans-with-yellow-helmet-drawing-tool.webp"),
                   LARGEUR, HAUTEUR).convert("RGB")
    photo = os.path.join(SORTIE, "_fond-couverture.jpg")
    fond.save(photo, "JPEG", quality=88)

    document = fitz.open()
    page = document.new_page(width=LARGEUR, height=HAUTEUR)
    cadre = fitz.Rect(0, 0, LARGEUR, HAUTEUR)

    page.insert_image(cadre, filename=photo)
    # Voile separe de la photo : son opacite se regle dans Canva.
    page.draw_rect(cadre, color=None, fill=couleur(NUIT), fill_opacity=0.87)

    logo = os.path.join(os.path.dirname(DOSSIER), "identite", "logo-fond-sombre.png")
    large = 430
    haut = int(1303 * large / 1600)  # proportions du fichier source
    page.insert_image(
        fitz.Rect((LARGEUR - large) / 2, 200 - haut / 2, (LARGEUR + large) / 2, 200 + haut / 2),
        filename=logo, keep_proportion=True,
    )

    ecrire(page, "Expertise bâtiment & Assistance à Maîtrise d’Ouvrage", "demi", 36, 437, BLANC)
    ecrire(page, "Alpes-Maritimes (06) et Var (83)", "normal", 30, 487, BLEU)

    page.draw_rect(fitz.Rect(LARGEUR / 2 - 70, 520, LARGEUR / 2 + 70, 525),
                   color=None, fill=couleur(ORANGE))

    ecrire(page, "btpexpertise.fr  ·  06 81 65 15 91", "demi", 32, 580, BLANC)

    chemin = os.path.join(SORTIE, "couverture-facebook.pdf")
    document.save(chemin, garbage=3, deflate=True)

    # Apercu : ce que Canva affichera a l'ouverture.
    page.get_pixmap(dpi=96).save(os.path.join(SORTIE, "couverture-facebook-pdf-apercu.png"))
    document.close()
    os.remove(photo)
    return chemin


if __name__ == "__main__":
    chemin = construire()
    print("%s  %.0f Ko" % (os.path.basename(chemin), os.path.getsize(chemin) / 1024))
