# -*- coding: utf-8 -*-
"""Six autres styles de publicite — deuxieme serie.

    python reseaux-sociaux/pub_styles2.py

La premiere serie (`pub_styles.py`) restait proche du gabarit maison : photo,
degrade, texte en bas. Celle-ci s'en eloigne franchement.

  rapport   la photo annotee comme une piece de rapport d'expertise
  orange    aplat orange plein cadre, typo noire, une bande de photo
  editorial la photo cadree dans une marge papier, facon magazine
  question  une question en grand, sa reponse dans un encadre clair
  mosaique  quatre vignettes, quatre domaines d'expertise
  macaron   un tampon oblique sur la photo, pour le recrutement

Sortie : visuels/pub-meta/styles/, en 1080 x 1350.

Prudence de redaction, heritee de DIRECTION-VISUELLE.md : sur une photo
reelle, aucune valeur chiffree ni constat date — ce serait presenter une
image de banque comme un dossier traite. Les annotations disent la methode,
pas le resultat.
"""

import os
import sys

from PIL import Image, ImageDraw

DOSSIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DOSSIER)

from visuels import NUIT, BLEU, ORANGE, BLANC, GRAS, DEMI, NORMAL, logo, police, poser  # noqa: E402
from posts_planche import couper, lettrage  # noqa: E402
from pub_meta import cadrer, degrade, photo  # noqa: E402
from pub_styles import L, H, MARGE, DOUX, ARDOISE, bouton, grille, marque, surtitre  # noqa: E402

SORTIE = os.path.join(DOSSIER, "visuels", "pub-meta", "styles")
PAPIER = (240, 244, 249)


def enregistrer(image, nom):
    chemin = os.path.join(SORTIE, nom + ".jpg")
    image.convert("RGB").save(chemin, "JPEG", quality=92, optimize=True)
    print("%-28s %s" % (nom, "1080 x 1350"))
    return chemin


def bloc(dessin, texte, x, y, fonte, teinte, largeur, interligne=1.2):
    for ligne in couper(dessin, texte, fonte, largeur):
        dessin.text((x, y), ligne, font=fonte, fill=teinte)
        y += fonte.size * interligne
    return y


# ---------------------------------------------------------------------------
# 1 · Rapport — la photo annotee comme une piece d'expertise
# ---------------------------------------------------------------------------

def style_rapport():
    image = Image.new("RGBA", (L, H), PAPIER + (255,))
    dessin = ImageDraw.Draw(image)
    grille(dessin, teinte=(219, 228, 238))

    # La photo, encadree comme une planche : elle laisse voir le papier autour.
    haut, bas = int(H * 0.155), int(H * 0.60)
    vue = cadrer(photo("Fissure-maison-PACA.webp"), L - 2 * MARGE, bas - haut, 0.5)
    image.alpha_composite(vue.convert("RGBA"), (MARGE, haut))
    dessin.rectangle([MARGE, haut, L - MARGE, bas], outline=(206, 216, 229), width=3)

    # Repere numerote + ligne de rappel, comme sur un plan.
    reperes = [(0.28, 0.30, "le tracé"), (0.52, 0.55, "l’ouverture"), (0.74, 0.78, "les reprises")]
    fonte = police(DEMI, int(L * 0.026))
    for numero, (part_x, part_y, libelle) in enumerate(reperes, 1):
        cx = MARGE + (L - 2 * MARGE) * part_x
        cy = haut + (bas - haut) * part_y
        dessin.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=ORANGE)
        dessin.text((cx - 7, cy - 15), str(numero),
                    font=police(GRAS, int(L * 0.028)), fill=NUIT)
        # Le libelle part a droite, sauf s'il sortait de la photo : il bascule alors
        # a gauche du repere plutot que d'etre coupe au bord.
        large = dessin.textlength(libelle, font=fonte)
        # Le libelle est pose sur une pastille bleu nuit : en blanc sur la photo,
        # il disparaissait des que le mur etait clair.
        if cx + 72 + large < L - MARGE - 16:
            dessin.line([(cx + 26, cy), (cx + 62, cy)], fill=ORANGE, width=3)
            xt = cx + 72
        else:
            dessin.line([(cx - 62, cy), (cx - 26, cy)], fill=ORANGE, width=3)
            xt = cx - 72 - large
        dessin.rounded_rectangle([xt - 16, cy - fonte.size * 0.95,
                                  xt + large + 16, cy + fonte.size * 0.95],
                                 radius=int(fonte.size * 0.9), fill=NUIT)
        dessin.text((xt, cy - fonte.size * 0.62), libelle, font=fonte, fill=BLANC)

    marque(image, dessin, teinte=NUIT, picto="picto.png")

    y = bas + int(H * 0.035)
    surtitre(dessin, "Expertise bâtiment", y, teinte=(90, 103, 132))
    y += int(H * 0.048)
    y = bloc(dessin, "Ce qu’un expert lit sur ce mur", MARGE, y,
             police(GRAS, int(L * 0.062)), NUIT, L - 2 * MARGE)
    y += int(H * 0.012)
    y = bloc(dessin, "Le tracé donne l’origine, l’ouverture la gravité, "
                     "les reprises l’ancienneté. Le reste s’écrit dans le rapport.",
             MARGE, y, police(NORMAL, int(L * 0.030)), (98, 108, 130), L - 2 * MARGE, 1.45)
    bouton(image, dessin, "Faire expertiser", y + int(H * 0.025))
    return enregistrer(image, "style-rapport-expertise")


# ---------------------------------------------------------------------------
# 2 · Orange — aplat plein cadre, typo noire, une bande de photo
# ---------------------------------------------------------------------------

def style_orange():
    image = Image.new("RGBA", (L, H), ORANGE + (255,))
    dessin = ImageDraw.Draw(image)

    marque(image, dessin, teinte=NUIT, picto="picto.png")

    y = int(H * 0.16)
    corps = int(L * 0.115)
    fonte = police(GRAS, corps)
    for ligne in ("NE SIGNEZ", "PAS SEUL."):
        dessin.text((MARGE, y), ligne, font=fonte, fill=NUIT)
        y += corps * 1.02

    y += int(H * 0.02)
    y = bloc(dessin, "Un professionnel du bâtiment à vos côtés pour définir les travaux, "
                     "comparer les devis et vérifier ce qui se fait.",
             MARGE, y, police(DEMI, int(L * 0.034)), NUIT, L - 2 * MARGE, 1.4)

    # Bande de photo en pied : l'aplat respire, et le sujet reste identifiable.
    bande = int(H * 0.30)
    vue = cadrer(photo("chantier-renovation-cloisons.jpg"), L, bande, 0.45)
    image.alpha_composite(vue.convert("RGBA"), (0, H - bande))
    dessin = ImageDraw.Draw(image)
    bouton(image, dessin, "Être accompagné", H - bande - int(H * 0.105),
           fond=NUIT, encre=BLANC)
    return enregistrer(image, "style-orange-amo")


# ---------------------------------------------------------------------------
# 3 · Editorial — la photo cadree dans une marge papier
# ---------------------------------------------------------------------------

def style_editorial():
    image = Image.new("RGBA", (L, H), PAPIER + (255,))
    dessin = ImageDraw.Draw(image)

    bord = int(L * 0.055)
    haut = int(H * 0.13)
    bas = int(H * 0.60)
    vue = cadrer(photo("projet-renovation.webp"), L - 2 * bord, bas - haut, 0.5)
    arrondi = Image.new("L", (vue.width, vue.height), 0)
    ImageDraw.Draw(arrondi).rounded_rectangle([0, 0, vue.width, vue.height], radius=28, fill=255)
    image.paste(vue.convert("RGB"), (bord, haut), arrondi)

    # Etiquette posee a cheval sur la photo, comme un bandeau de magazine.
    fonte = police(DEMI, int(L * 0.026))
    texte = "ASSISTANCE À MAÎTRISE D’OUVRAGE"
    large = dessin.textlength(texte, font=fonte) + 3.0 * len(texte) + 56
    dessin.rounded_rectangle([bord + 24, bas - 30, bord + 24 + large, bas + 30],
                             radius=30, fill=NUIT)
    lettrage(dessin, (bord + 52, bas - 30 + (60 - fonte.size * 1.32) / 2), texte,
             fonte, BLANC, 3.0)

    y = bas + int(H * 0.075)
    y = bloc(dessin, "Vos travaux méritent un œil qui n’a rien à vendre",
             bord + 24, y, police(GRAS, int(L * 0.060)), NUIT, L - 2 * bord - 48, 1.18)
    y += int(H * 0.016)
    y = bloc(dessin, "Le cabinet n’exécute aucun des travaux qu’il vous aide à commander.",
             bord + 24, y, police(NORMAL, int(L * 0.031)), (98, 108, 130),
             L - 2 * bord - 48, 1.45)

    dessin.rectangle([bord + 24, y + int(H * 0.014), bord + 134, y + int(H * 0.014) + 6],
                     fill=ORANGE)
    marque(image, dessin, y=H - int(H * 0.085), teinte=NUIT, picto="picto.png")
    return enregistrer(image, "style-editorial-amo")


# ---------------------------------------------------------------------------
# 4 · Question — une question en grand, sa reponse dans un encadre
# ---------------------------------------------------------------------------

def style_question():
    image = Image.new("RGBA", (L, H), NUIT + (255,))
    dessin = ImageDraw.Draw(image)
    grille(dessin)
    marque(image, dessin)

    y = int(H * 0.17)
    surtitre(dessin, "La question qu’on nous pose", y)

    y += int(H * 0.06)
    y = bloc(dessin, "Une fissure, faut-il s’inquiéter ?", MARGE, y,
             police(GRAS, int(L * 0.078)), BLANC, L - 2 * MARGE, 1.18)

    y += int(H * 0.05)
    hauteur = int(H * 0.26)
    dessin.rounded_rectangle([MARGE, y, L - MARGE, y + hauteur], radius=26, fill=PAPIER)
    dessin.rectangle([MARGE, y + 26, MARGE + 6, y + hauteur - 26], fill=ORANGE)
    bloc(dessin, "Cela dépend de son tracé, de son ouverture et de son évolution. "
                 "Trois choses qu’on ne juge pas sur une photo — d’où la visite.",
         MARGE + 38, y + 40, police(NORMAL, int(L * 0.033)), NUIT,
         L - 2 * MARGE - 76, 1.45)

    y += hauteur + int(H * 0.04)
    bloc(dessin, "Expertise bâtiment · Alpes-Maritimes et Var", MARGE, y,
         police(DEMI, int(L * 0.030)), BLEU, L - 2 * MARGE)
    bouton(image, dessin, "Poser ma question", y + int(H * 0.05))
    return enregistrer(image, "style-question-expertise")


# ---------------------------------------------------------------------------
# 5 · Mosaique — quatre vignettes, quatre domaines
# ---------------------------------------------------------------------------

def style_mosaique():
    image = Image.new("RGBA", (L, H), NUIT + (255,))
    dessin = ImageDraw.Draw(image)
    marque(image, dessin)

    y = int(H * 0.155)
    surtitre(dessin, "Ce que le cabinet examine", y)
    y += int(H * 0.05)
    y = bloc(dessin, "Quatre désordres, une même méthode", MARGE, y,
             police(GRAS, int(L * 0.058)), BLANC, L - 2 * MARGE, 1.18)

    y += int(H * 0.025)
    vignettes = [("Fissure-maison-PACA.webp", "Fissures"),
                 ("comp-infiltrations.webp", "Humidité"),
                 ("comp-malfacons.webp", "Malfaçons"),
                 ("exp-reception.webp", "Réception")]
    large = (L - 2 * MARGE - 18) // 2
    haut = int(large * 0.82)
    fonte = police(DEMI, int(L * 0.032))
    for index, (fichier, libelle) in enumerate(vignettes):
        x = int(MARGE + (index % 2) * (large + 18))
        yv = int(y + (index // 2) * (haut + 18))
        vue = cadrer(photo(fichier), large, haut, 0.5).convert("RGBA")
        vue.alpha_composite(degrade((large, haut), int(haut * 0.42), int(haut * 0.45)))
        arrondi = Image.new("L", (large, haut), 0)
        ImageDraw.Draw(arrondi).rounded_rectangle([0, 0, large, haut], radius=22, fill=255)
        image.paste(vue.convert("RGB"), (x, yv), arrondi)
        plume = ImageDraw.Draw(image)
        plume.line([(x + 22, yv + haut - 40), (x + 46, yv + haut - 40)], fill=ORANGE, width=4)
        plume.text((x + 58, yv + haut - 40 - fonte.size * 0.66), libelle, font=fonte, fill=BLANC)

    dessin = ImageDraw.Draw(image)
    y += 2 * haut + 18 + int(H * 0.03)
    bouton(image, dessin, "Demander une expertise", y)
    return enregistrer(image, "style-mosaique-expertise")


# ---------------------------------------------------------------------------
# 6 · Macaron — un tampon oblique sur la photo
# ---------------------------------------------------------------------------

def style_macaron():
    image = cadrer(photo("Expertise-avant-achat-immobilier-1.webp"), L, H, 0.42).convert("RGBA")
    image = Image.alpha_composite(image, Image.new("RGBA", (L, H), NUIT + (92,)))
    image = Image.alpha_composite(image, degrade((L, H), int(H * 0.66), int(H * 0.18)))

    # Tampon : dessine a plat, puis pivote — comme un autocollant pose de travers.
    cote = int(L * 0.50)
    tampon = Image.new("RGBA", (cote, cote), (0, 0, 0, 0))
    plume = ImageDraw.Draw(tampon)
    plume.ellipse([0, 0, cote, cote], fill=ORANGE)
    plume.ellipse([14, 14, cote - 14, cote - 14], outline=NUIT, width=3)
    corps = int(L * 0.042)
    fonte = police(GRAS, corps)
    lignes = ["NOUS", "RECRUTONS", "UN EXPERT"]
    yt = (cote - len(lignes) * corps * 1.16) / 2
    for ligne in lignes:
        plume.text(((cote - plume.textlength(ligne, font=fonte)) / 2, yt), ligne,
                   font=fonte, fill=NUIT)
        yt += corps * 1.16
    tampon = tampon.rotate(-11, expand=True, resample=Image.BICUBIC)
    image.alpha_composite(tampon, (L - tampon.width - int(L * 0.05), int(H * 0.085)))

    dessin = ImageDraw.Draw(image)
    marque(image, dessin)

    y = int(H * 0.74)
    y = bloc(dessin, "Expert bâtiment indépendant, 06 & 83", MARGE, y,
             police(GRAS, int(L * 0.054)), BLANC, L - 2 * MARGE, 1.2)
    y += int(H * 0.012)
    y = bloc(dessin, "Missions confiées par le cabinet, au sein d’un réseau "
                     "de professionnels indépendants.",
             MARGE, y, police(NORMAL, int(L * 0.030)), DOUX, L - 2 * MARGE, 1.45)
    bouton(image, dessin, "Envoyer ma candidature", y + int(H * 0.022))
    return enregistrer(image, "style-macaron-recrutement")


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    style_rapport()
    style_orange()
    style_editorial()
    style_question()
    style_mosaique()
    style_macaron()
