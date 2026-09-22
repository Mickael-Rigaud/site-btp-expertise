# -*- coding: utf-8 -*-
"""Cartes bleu nuit — l'autre moitie du feed, sans photo non plus.

Elles alternent avec les planches claires de posts_planche.py : une fois
posees en damier dans la grille Instagram, clair / sombre / clair, le compte
se reconnait avant meme d'etre lu.

    python reseaux-sociaux/posts_carte.py

Trois mises en page, choisies selon ce que dit la publication :
  chiffre  un montant ou une duree qui doit se lire de loin
  phrase   une position du cabinet, en grand
  liste    ce qu'on regarde, ce qu'on remet, ce qu'on ne fait pas
"""

import os
import sys

from PIL import Image, ImageDraw

DOSSIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DOSSIER)

from visuels import NUIT, BLEU, ORANGE, BLANC, GRAS, DEMI, NORMAL, logo, police, poser  # noqa: E402
from posts_planche import couper, lettrage  # noqa: E402

SORTIE = os.path.join(DOSSIER, "visuels", "planches")

# Deux jeux de couleurs pour un meme gabarit : la carte existe sur fond nuit
# et sur fond papier, ce qui permet d'alterner case par case dans le feed.
THEMES = {
    "nuit": {"fond": NUIT, "grille": (49, 56, 73), "fort": BLANC,
             "doux": (166, 176, 197), "logo": "picto-fond-sombre.png"},
    "papier": {"fond": (238, 243, 248), "grille": (214, 226, 237), "fort": NUIT,
               "doux": (110, 122, 145), "logo": "picto.png"},
}

OUVERTURE = {
    "cle": "ouverture", "genre": "sommaire", "entete": "Le cabinet ouvre ses pages",
    "titre": "Expertise bâtiment & Assistance à Maîtrise d’Ouvrage",
    "colonnes": [
        ["Visite technique et avis",
         "Fissures et désordres",
         "Humidité et infiltrations",
         "Malfaçons et non-conformités",
         "Plomberie et réseaux"],
        ["Installations électriques",
         "Expertise avant achat",
         "Litiges et expertise amiable",
         "Assistance à réception",
         "Réunion contradictoire"],
    ],
    "phrase": "Alpes-Maritimes et Var · Devis établi avant toute intervention",
}

CARTES = [
    {"cle": "honoraires", "genre": "chiffre", "entete": "Honoraires",
     "chiffre": "590 €", "unite": "TTC",
     "titre": "Le prix est connu avant l’intervention",
     "phrase": "Visite technique à partir de 590 € TTC. Expertise avec rapport détaillé à partir de 990 € TTC. AMO sur devis."},

    {"cle": "independance", "genre": "phrase", "entete": "Le cabinet",
     "titre": "Nous n’exécutons pas les travaux que nous examinons.",
     "phrase": "Aucun lien avec les entreprises en place, aucun intérêt dans les réparations préconisées."},

    {"cle": "avant-achat", "genre": "liste", "theme": "papier", "entete": "Expertise avant achat",
     "titre": "Ce qu’on regarde avant que vous signiez",
     "items": ["Structure, fissures, planchers",
               "Toiture, façades, étanchéité",
               "Humidité, ventilation, réseaux",
               "Traces de désordres repris"],
     "phrase": "Un état technique du bien, et de quoi négocier — ou renoncer."},

    {"cle": "amo", "genre": "liste", "entete": "Assistance à maîtrise d’ouvrage",
     "titre": "Ce que l’AMO n’est pas",
     "items": ["Ni direction des travaux",
               "Ni ordres aux entreprises",
               "Ni garantie de délai ou de budget",
               "Vous restez décisionnaire"],
     "phrase": "Un professionnel du bâtiment à vos côtés, qui conseille et vérifie."},

    {"cle": "malfacons", "genre": "phrase", "entete": "Malfaçons",
     "titre": "Un défaut visible n’est pas toujours une malfaçon.",
     "phrase": "L’analyse se fait au regard des prescriptions techniques applicables, pas à l’œil nu."},

    {"cle": "visite-technique", "genre": "liste", "theme": "papier",
     "entete": "Visite technique",
     "titre": "Ce que comprend une visite technique",
     "items": ["Un déplacement sur site",
               "Les constats et relevés utiles",
               "Un avis technique professionnel",
               "Sans rapport détaillé"],
     "phrase": "À partir de 590 € TTC. Le rapport détaillé relève d’une mission distincte."},

    {"cle": "expert-vs-immo", "genre": "duo", "entete": "Deux métiers différents",
     "titre": "Expert bâtiment ou expert immobilier ?",
     "colonnes": [
         {"titre": "Expert bâtiment", "items": ["État technique du bien",
                                                    "Désordres et causes",
                                                    "Préconisations de travaux"]},
         {"titre": "Expert immobilier", "items": ["Valeur vénale du bien",
                                                  "Prix de marché",
                                                  "Estimation patrimoniale"]},
     ],
     "phrase": "Nous faisons le premier. Un bien peut être bien valorisé et techniquement malade."},

    {"cle": "litiges", "genre": "phrase", "entete": "Litiges travaux",
     "titre": "Un constat technique pèse plus qu’un échange de courriers.",
     "phrase": "Expertise amiable : constater, analyser, et poser des faits opposables aux parties."},

    {"cle": "reunion", "genre": "liste", "theme": "papier", "entete": "Réunion contradictoire",
     "titre": "Vous n’y allez pas seul",
     "items": ["L’entreprise et son assureur",
               "L’expert de la partie adverse",
               "Parfois plusieurs intervenants",
               "Et vous, avec votre technicien"],
     "phrase": "Assistance technique du client pendant la réunion, face aux autres parties."},

    {"cle": "rapport", "genre": "liste", "entete": "Le rapport",
     "titre": "Ce que vous recevez après la visite",
     "items": ["Les constats, datés et localisés",
               "Les photographies annotées",
               "L’analyse des causes probables",
               "Les préconisations selon la mission"],
     "phrase": "Un document utilisable face à une entreprise, un assureur ou un vendeur."},

    {"cle": "zones", "genre": "chiffre", "entete": "Zone d’intervention",
     "chiffre": "06 · 83", "unite": "",
     "titre": "Alpes-Maritimes et Var",
     "phrase": "Nice, Cannes, Antibes, Grasse, Menton, et plus largement la Côte d’Azur."},
]


def grille(dessin, largeur, hauteur, teinte, pas=54):
    for x in range(0, largeur + 1, pas):
        dessin.line([(x, 0), (x, hauteur)], fill=teinte, width=1)
    for y in range(0, hauteur + 1, pas):
        dessin.line([(0, y), (largeur, y)], fill=teinte, width=1)


def pied(dessin, fond, largeur, hauteur, marge, theme):
    base = hauteur - marge - 46
    picto = logo(theme["logo"])
    picto = picto.crop(picto.getbbox())
    poser(fond, picto, marge + 23, base + 23, 46)
    f = police(DEMI, 27)
    dessin.text((marge + 64, base + 6), "BTP EXPERTISE", font=f, fill=theme["fort"])
    adresse = "btpexpertise.fr"
    dessin.text((largeur - marge - dessin.textlength(adresse, font=f), base + 6),
                adresse, font=f, fill=BLEU)


def mesures_carte(carte, taille, dessin):
    """Positions de la carte, sans rien dessiner — partagees avec planches_pdf."""
    largeur, hauteur = taille
    story = hauteur > largeur
    marge = 76 if not story else 88
    sommaire = carte["genre"] == "sommaire"

    m = {
        "largeur": largeur, "hauteur": hauteur, "marge": marge,
        "corps": {
            "entete": 22 if not story else 24,
            "titre": (46 if sommaire else 56) if not story else (52 if sommaire else 62),
            "phrase": 28 if not story else 32,
            "item": 33 if not story else 37,
            "liste": 27 if not story else 31,
            "gros": 168 if not story else 190,
        },
        "inter_titre": 1.2, "inter_phrase": 1.45, "inter_item": 1.62, "inter_liste": 1.75,
        "y_entete": marge + (0 if not story else 130),
        "marge_pied": marge if not story else marge + 130,
    }
    utile = largeur - 2 * marge
    m["utile"] = utile
    m["lignes_titre"] = couper(dessin, carte["titre"], police(GRAS, m["corps"]["titre"]), utile)
    m["lignes_phrase"] = couper(dessin, carte["phrase"], police(NORMAL, m["corps"]["phrase"]), utile)

    bloc = (len(m["lignes_titre"]) * m["corps"]["titre"] * m["inter_titre"] + 30
            + len(m["lignes_phrase"]) * m["corps"]["phrase"] * m["inter_phrase"])
    if carte["genre"] == "chiffre":
        bloc += m["corps"]["gros"] * 1.28
    if carte["genre"] == "liste":
        bloc += 30 + len(carte["items"]) * m["corps"]["item"] * m["inter_item"]
    if sommaire:
        bloc += 40 + len(carte["colonnes"][0]) * m["corps"]["liste"] * m["inter_liste"]
    if carte["genre"] == "duo":
        plus_longue = max(len(c["items"]) for c in carte["colonnes"])
        bloc += 40 + 50 + plus_longue * m["corps"]["item"] * m["inter_item"]

    apres_entete = m["y_entete"] + m["corps"]["entete"] + 60
    m["y_bloc"] = apres_entete + max(
        0, (hauteur - m["marge_pied"] - 46 - 40 - apres_entete - bloc) / 2)
    return m


def composer(carte, taille, suffixe):
    largeur, hauteur = taille
    theme = THEMES[carte.get("theme", "nuit")]
    fond = Image.new("RGBA", (largeur, hauteur), theme["fond"] + (255,))
    dessin = ImageDraw.Draw(fond)
    grille(dessin, largeur, hauteur, theme["grille"])

    m = mesures_carte(carte, taille, dessin)
    marge, corps = m["marge"], m["corps"]
    f_entete = police(DEMI, corps["entete"])
    f_titre = police(GRAS, corps["titre"])
    f_phrase = police(NORMAL, corps["phrase"])
    f_item = police(NORMAL, corps["item"])
    f_liste = police(NORMAL, corps["liste"])
    f_gros = police(GRAS, corps["gros"])

    y = m["y_entete"]
    x = lettrage(dessin, (marge, y), carte["entete"].upper(), f_entete, theme["doux"], 3.0)
    dessin.line([(marge, y + f_entete.size + 16), (x - 3, y + f_entete.size + 16)],
                fill=ORANGE, width=4)

    y = m["y_bloc"]
    if carte["genre"] == "chiffre":
        dessin.text((marge, y), carte["chiffre"], font=f_gros, fill=ORANGE)
        if carte["unite"]:
            xu = marge + dessin.textlength(carte["chiffre"], font=f_gros) + 16
            dessin.text((xu, y + f_gros.size * 0.42), carte["unite"], font=police(DEMI, 38),
                        fill=theme["doux"])
        y += f_gros.size * 1.28

    for ligne in m["lignes_titre"]:
        dessin.text((marge, y), ligne, font=f_titre, fill=theme["fort"])
        y += corps["titre"] * m["inter_titre"]

    if carte["genre"] == "sommaire":
        y += 40
        colonne_l = (m["utile"] - 40) / 2
        for c, colonne in enumerate(carte["colonnes"]):
            xc = marge + c * (colonne_l + 40)
            yc = y
            for item in colonne:
                dessin.line([(xc, yc + f_liste.size * 0.66), (xc + 18, yc + f_liste.size * 0.66)],
                            fill=ORANGE, width=3)
                dessin.text((xc + 32, yc), item, font=f_liste, fill=theme["fort"])
                yc += corps["liste"] * m["inter_liste"]
        y = yc

    if carte["genre"] == "duo":
        y += 40
        colonne_l = (m["utile"] - 40) / 2
        f_colonne = police(DEMI, int(corps["item"] * 0.92))
        bas = y
        for c, colonne in enumerate(carte["colonnes"]):
            xc = marge + c * (colonne_l + 40)
            dessin.text((xc, y), colonne["titre"], font=f_colonne, fill=ORANGE)
            yc = y + 50
            for item in colonne["items"]:
                dessin.line([(xc, yc + f_item.size * 0.62), (xc + 20, yc + f_item.size * 0.62)],
                            fill=theme["doux"], width=3)
                dessin.text((xc + 38, yc), item, font=f_item, fill=theme["fort"])
                yc += corps["item"] * m["inter_item"]
            bas = max(bas, yc)
        y = bas

    if carte["genre"] == "liste":
        y += 30
        for item in carte["items"]:
            dessin.line([(marge + 2, y + f_item.size * 0.62), (marge + 26, y + f_item.size * 0.62)],
                        fill=ORANGE, width=4)
            dessin.text((marge + 46, y), item, font=f_item, fill=theme["fort"])
            y += corps["item"] * m["inter_item"]

    y += 30
    for ligne in m["lignes_phrase"]:
        dessin.text((marge, y), ligne, font=f_phrase, fill=theme["doux"])
        y += corps["phrase"] * m["inter_phrase"]

    pied(dessin, fond, largeur, hauteur, m["marge_pied"], theme)

    chemin = os.path.join(SORTIE, "%s%s.png" % (carte["cle"], suffixe))
    fond.convert("RGB").save(chemin)
    return chemin


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    for carte in CARTES + [OUVERTURE]:
        composer(carte, (1080, 1080), "-1080")
        composer(carte, (1080, 1920), "-story")
        print("%-14s carre + story" % carte["cle"])
