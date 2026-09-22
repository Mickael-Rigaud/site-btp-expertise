# -*- coding: utf-8 -*-
"""Visuels des publications organiques — Facebook et Instagram.

Huit publications a passer avant les campagnes, sur un gabarit commun :
photo du site en haut, panneau bleu nuit en bas avec l'etiquette du sujet,
un titre, une phrase, et le pied de marque.

    python reseaux-sociaux/posts.py

Chaque sujet sort en deux formats : carre 1080 pour le fil, et 1080 x 1920
pour les stories et les reels. Les legendes correspondantes sont dans
TEXTES-A-COPIER.md.

La mise en page vit dans `geometrie()`, qui ne dessine rien : posts_pdf.py
l'appelle aussi, pour que les PNG et les PDF ne divergent jamais.
"""

import os
import sys

from PIL import Image, ImageDraw

DOSSIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DOSSIER)

from visuels import (NUIT, BLEU, ORANGE, BLANC, GRAS, DEMI, NORMAL,  # noqa: E402
                     couvrir, image, logo, police, poser)

SORTIE = os.path.join(DOSSIER, "visuels", "publications")
DOUX = (196, 204, 220)
MARQUE = "BTP EXPERTISE"
ADRESSE = "btpexpertise.fr"

# etiquette, titre, phrase, photo
PUBLICATIONS = [
    ("fissures", "Fissures",
     "Toutes les fissures ne se valent pas",
     "Forme, orientation, évolution dans le temps : c’est l’analyse qui dit s’il faut surveiller ou reprendre.",
     "exp-fissures.webp"),

    ("avant-achat", "Avant achat",
     "Avant de signer, faites regarder le bien",
     "Toiture, façades, réseaux, humidité : ce qui se voit sur place engage souvent plusieurs milliers d’euros.",
     "exp-avant-achat.webp"),

    ("reception", "Réception de travaux",
     "Le jour de la réception, tout se joue",
     "Ce qui n’est pas noté en réserve ce jour-là devient beaucoup plus difficile à faire reprendre ensuite.",
     "exp-reception.webp"),

    ("humidite", "Humidité",
     "L’eau n’entre pas toujours là où la tache apparaît",
     "Infiltration, remontée capillaire, condensation, fuite de réseau : même mur, traitements différents.",
     "exp-humidite.webp"),

    ("malfacons", "Malfaçons",
     "Un défaut visible n’est pas toujours une malfaçon",
     "L’analyse se fait au regard des prescriptions techniques applicables, pas à l’œil nu.",
     "exp-malfacons.webp"),

    ("independance", "Le cabinet",
     "Nous n’exécutons pas les travaux que nous examinons",
     "Aucun intérêt dans les réparations préconisées : c’est ce qui donne sa valeur au constat.",
     "Expertise-batiment-a-Antibes-et-Nice.webp"),

    ("honoraires", "Honoraires",
     "Le prix est connu avant l’intervention",
     "Visite technique à partir de 590 € TTC, expertise avec rapport détaillé à partir de 990 € TTC.",
     "honoraires-devis.webp"),

    ("zones", "Zone d’intervention",
     "Alpes-Maritimes et Var",
     "Nice, Cannes, Antibes, Grasse, Menton, et plus largement la Côte d’Azur.",
     # Pas "Ville-de-Nice.webp" : cette photo du site ne montre pas la Cote d'Azur.
     "BTP-Expertise-RIviera-Nice.webp"),
]


# ---------------------------------------------------------------------------
# Mise en page — commune au PNG et au PDF
# ---------------------------------------------------------------------------

def couper(texte, largeur_texte, largeur_max):
    """Repartit le texte en lignes qui tiennent dans largeur_max.

    largeur_texte est fourni par l'appelant : Pillow et PyMuPDF mesurent
    chacun avec leur propre moteur, mais sur les memes polices.
    """
    lignes, ligne = [], ""
    for mot in texte.split():
        essai = (ligne + " " + mot).strip()
        if largeur_texte(essai) <= largeur_max or not ligne:
            ligne = essai
        else:
            lignes.append(ligne)
            ligne = mot
    if ligne:
        lignes.append(ligne)
    return lignes


def geometrie(taille, titre, phrase, etiquette, mesurer):
    """Positions et decoupes du gabarit, sans rien dessiner.

    `mesurer(texte, role, corps)` rend la largeur du texte pour la police du
    role demande. Roles : titre, phrase, etiquette, pied.
    """
    largeur, hauteur = taille
    story = hauteur > largeur

    g = {
        "largeur": largeur,
        "hauteur": hauteur,
        "marge": 88 if story else 76,
        # Les stories laissent le bas libre : l'interface d'Instagram s'y pose.
        "marge_bas": 230 if story else 76,
        "corps": {
            "titre": 66 if story else 62,
            "phrase": 34 if story else 31,
            "etiquette": 25 if story else 23,
            "pied": 30 if story else 28,
        },
        "inter_titre": 1.22,
        "inter_phrase": 1.45,
        "ecart_etiquette": 2.4,
        "pied_h": 46,
        "degrade_h": 150,
        "etiquette": etiquette.upper(),
    }

    marge = g["marge"]
    utile = largeur - 2 * marge
    g["lignes_titre"] = couper(titre, lambda t: mesurer(t, "titre", g["corps"]["titre"]), utile)
    g["lignes_phrase"] = couper(phrase, lambda t: mesurer(t, "phrase", g["corps"]["phrase"]), utile)

    bloc = (len(g["lignes_titre"]) * g["corps"]["titre"] * g["inter_titre"]
            + 26
            + len(g["lignes_phrase"]) * g["corps"]["phrase"] * g["inter_phrase"])
    g["haut_panneau"] = int(hauteur - g["marge_bas"] - g["pied_h"] - 46 - bloc - 62)

    g["y_titre"] = g["haut_panneau"] + 62
    g["y_phrase"] = g["y_titre"] + len(g["lignes_titre"]) * g["corps"]["titre"] * g["inter_titre"] + 26
    g["base_pied"] = hauteur - g["marge_bas"] - g["pied_h"]

    lettres = g["etiquette"]
    larg_lettres = sum(mesurer(c, "etiquette", g["corps"]["etiquette"]) for c in lettres)
    g["largeur_etiquette"] = larg_lettres + g["ecart_etiquette"] * (len(lettres) - 1)
    g["pilule"] = (marge, marge,
                   marge + g["largeur_etiquette"] + 44,
                   marge + g["corps"]["etiquette"] + 26)
    return g


# ---------------------------------------------------------------------------
# Rendu PNG
# ---------------------------------------------------------------------------

def degrade(largeur, hauteur):
    """Transition photo → panneau, pour eviter la coupure nette."""
    masque = Image.linear_gradient("L").resize((largeur, hauteur))
    voile = Image.new("RGBA", (largeur, hauteur), NUIT + (255,))
    voile.putalpha(masque)
    return voile


def composer(cle, etiquette, titre, phrase, photo, taille, suffixe):
    largeur, hauteur = taille
    fond = couvrir(image(photo), largeur, hauteur)
    dessin = ImageDraw.Draw(fond)

    fontes = {
        "titre": lambda c: police(GRAS, c),
        "phrase": lambda c: police(NORMAL, c),
        "etiquette": lambda c: police(DEMI, c),
        "pied": lambda c: police(DEMI, c),
    }
    g = geometrie(taille, titre, phrase, etiquette,
                  lambda t, role, corps: dessin.textlength(t, font=fontes[role](corps)))

    marge = g["marge"]
    f_titre = fontes["titre"](g["corps"]["titre"])
    f_phrase = fontes["phrase"](g["corps"]["phrase"])
    f_etiq = fontes["etiquette"](g["corps"]["etiquette"])
    f_pied = fontes["pied"](g["corps"]["pied"])

    fond.alpha_composite(degrade(largeur, g["degrade_h"]),
                         (0, g["haut_panneau"] - g["degrade_h"]))
    dessin.rectangle([0, g["haut_panneau"], largeur, hauteur], fill=NUIT + (255,))

    dessin.rounded_rectangle(list(g["pilule"]),
                             radius=(g["corps"]["etiquette"] + 26) / 2, fill=ORANGE + (255,))
    x = marge + 22
    for lettre in g["etiquette"]:
        dessin.text((x, marge + 11), lettre, font=f_etiq, fill=NUIT)
        x += dessin.textlength(lettre, font=f_etiq) + g["ecart_etiquette"]

    y = g["y_titre"]
    for ligne in g["lignes_titre"]:
        dessin.text((marge, y), ligne, font=f_titre, fill=BLANC)
        y += g["corps"]["titre"] * g["inter_titre"]
    y = g["y_phrase"]
    for ligne in g["lignes_phrase"]:
        dessin.text((marge, y), ligne, font=f_phrase, fill=DOUX)
        y += g["corps"]["phrase"] * g["inter_phrase"]

    base = g["base_pied"]
    picto = logo("logo-compact-fond-sombre.png")
    picto = picto.crop(picto.getbbox())
    poser(fond, picto, marge + g["pied_h"] / 2, base + g["pied_h"] / 2,
          int(g["pied_h"] * picto.width / picto.height))
    dessin.text((marge + g["pied_h"] + 18, base + 6), MARQUE, font=f_pied, fill=BLANC)
    dessin.text((largeur - marge - dessin.textlength(ADRESSE, font=f_pied), base + 6),
                ADRESSE, font=f_pied, fill=BLEU)

    chemin = os.path.join(SORTIE, "%s%s.png" % (cle, suffixe))
    fond.convert("RGB").save(chemin)
    return chemin


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    for cle, etiquette, titre, phrase, photo in PUBLICATIONS:
        composer(cle, etiquette, titre, phrase, photo, (1080, 1080), "-1080")
        composer(cle, etiquette, titre, phrase, photo, (1080, 1920), "-story")
        print("%-14s carre + story" % cle)
    print("\n%d fichiers dans %s" % (len(os.listdir(SORTIE)), SORTIE))
