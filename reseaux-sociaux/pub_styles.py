# -*- coding: utf-8 -*-
"""Cinq autres styles de publicite, a choisir avant d'aller plus loin.

    python reseaux-sociaux/pub_styles.py

Le gabarit de pub_meta.py — photo, degrade, accroche, bouton — fait une
annonce sobre mais toujours la meme. Ces cinq-la reprennent des mecaniques
qui marchent ailleurs, transposees dans la charte du cabinet : bleu nuit,
cyan, orange, Segoe UI.

  liste    la prestation deballee en pastilles, sur fond nuit
  duo      deux colonnes opposees : sans accompagnement / avec le cabinet
  typo     une phrase enorme sur une photo plein cadre, rien d'autre
  bandeau  un bloc orange oblique qui coupe la photo, pour interpeller
  etapes   la mission en quatre temps numerotes

Sortie : visuels/pub-meta/styles/, en 1080 x 1350. Une fois un style retenu,
il rejoindra pub_meta.py et sortira dans les trois formats comme les autres.

Les textes respectent les memes regles que le reste : l'AMO conseille et
verifie sans diriger les travaux, et le recrutement s'adresse a des
independants. Aucun chiffre, aucun avis client : rien d'invente.
"""

import os
import sys

from PIL import Image, ImageDraw

DOSSIER = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(DOSSIER)
sys.path.insert(0, DOSSIER)

from visuels import NUIT, BLEU, ORANGE, BLANC, GRAS, DEMI, NORMAL, logo, police, poser  # noqa: E402
from posts_planche import couper, lettrage  # noqa: E402
from pub_meta import cadrer, degrade, photo  # noqa: E402

SORTIE = os.path.join(DOSSIER, "visuels", "pub-meta", "styles")

L, H = 1080, 1350
MARGE = int(L * 0.085)
DOUX = (206, 214, 231)
GRIS = (122, 132, 156)
ARDOISE = (49, 56, 73)


def toile(fond=NUIT):
    return Image.new("RGBA", (L, H), fond + (255,))


def grille(dessin, teinte=ARDOISE, pas=54):
    for x in range(0, L + 1, pas):
        dessin.line([(x, 0), (x, H)], fill=teinte, width=1)
    for y in range(0, H + 1, pas):
        dessin.line([(0, y), (L, y)], fill=teinte, width=1)


def marque(image, dessin, y=None, teinte=BLANC, picto="picto-fond-sombre.png"):
    y = MARGE if y is None else y
    cote = int(L * 0.056)
    signe = logo(picto)
    signe = signe.crop(signe.getbbox())
    poser(image, signe, MARGE + cote / 2, y + cote / 2, cote)
    dessin.text((MARGE + int(L * 0.075), y + int(L * 0.008)), "BTP EXPERTISE",
                font=police(DEMI, int(L * 0.030)), fill=teinte)


def surtitre(dessin, texte, y, teinte=BLEU):
    corps = int(L * 0.024)
    x = lettrage(dessin, (MARGE, y), texte.upper(), police(DEMI, corps), teinte, 3.0)
    dessin.line([(MARGE, y + corps * 1.35), (x - 3, y + corps * 1.35)], fill=ORANGE, width=4)
    return x


def bouton(image, dessin, texte, y, x=MARGE, fond=ORANGE, encre=NUIT):
    corps = int(L * 0.033)
    fonte = police(DEMI, corps)
    haut = int(corps * 2.5)
    large = int(dessin.textlength(texte, font=fonte) + corps * 2.6)
    dessin.rounded_rectangle([x, y, x + large, y + haut], radius=haut // 2, fill=fond)
    dessin.text((x + corps * 1.3, y + (haut - corps * 1.32) / 2), texte, font=fonte, fill=encre)
    return y + haut


def enregistrer(image, nom):
    chemin = os.path.join(SORTIE, nom + ".jpg")
    image.convert("RGB").save(chemin, "JPEG", quality=92, optimize=True)
    print("%-28s %s" % (nom, "1080 x 1350"))
    return chemin


# ---------------------------------------------------------------------------
# 1 · Liste — la prestation deballee, comme une carte de services
# ---------------------------------------------------------------------------

def style_liste():
    image = toile()
    dessin = ImageDraw.Draw(image)
    grille(dessin)
    marque(image, dessin)

    y = int(H * 0.17)
    surtitre(dessin, "Assistance à maîtrise d’ouvrage", y)

    y += int(H * 0.055)
    corps = int(L * 0.068)
    for ligne in couper(dessin, "Ce que le cabinet fait à vos côtés",
                        police(GRAS, corps), L - 2 * MARGE):
        dessin.text((MARGE, y), ligne, font=police(GRAS, corps), fill=BLANC)
        y += corps * 1.2

    y += int(H * 0.03)
    items = ["Définir précisément les travaux",
             "Consulter et comparer les entreprises",
             "Analyser les devis, ligne à ligne",
             "Visiter le chantier, relever ce qui cloche",
             "Assister à la réception et aux réserves"]
    corps = int(L * 0.034)
    fonte = police(DEMI, corps)
    haut = int(corps * 2.5)
    for numero, item in enumerate(items, 1):
        dessin.rounded_rectangle([MARGE, y, L - MARGE, y + haut], radius=18,
                                 fill=(45, 52, 76))
        # Pastille du numero, en cyan : elle rythme la liste sans la surcharger.
        dessin.ellipse([MARGE + 16, y + (haut - 46) / 2, MARGE + 62, y + (haut + 46) / 2],
                       fill=BLEU)
        dessin.text((MARGE + 30, y + (haut - corps * 1.1) / 2), str(numero),
                    font=police(GRAS, int(corps * 0.85)), fill=NUIT)
        dessin.text((MARGE + 84, y + (haut - corps * 1.32) / 2), item, font=fonte, fill=BLANC)
        y += haut + 16

    y += int(H * 0.02)
    corps = int(L * 0.030)
    dessin.text((MARGE, y), "Le cabinet conseille et vérifie. Vous décidez.",
                font=police(NORMAL, corps), fill=DOUX)
    bouton(image, dessin, "Parler de mon projet", y + int(H * 0.05))
    return enregistrer(image, "style-liste-amo")


# ---------------------------------------------------------------------------
# 2 · Duo — deux colonnes opposees
# ---------------------------------------------------------------------------

def style_duo():
    image = toile((240, 244, 249))
    dessin = ImageDraw.Draw(image)
    marque(image, dessin, teinte=NUIT, picto="picto.png")

    y = int(H * 0.17)
    surtitre(dessin, "Travaux · 06 & 83", y, teinte=(90, 103, 132))

    y += int(H * 0.055)
    corps = int(L * 0.068)
    for ligne in couper(dessin, "Deux façons de lancer des travaux",
                        police(GRAS, corps), L - 2 * MARGE):
        dessin.text((MARGE, y), ligne, font=police(GRAS, corps), fill=NUIT)
        y += corps * 1.2

    y += int(H * 0.035)
    large = (L - 2 * MARGE - 24) / 2
    hauteur = int(H * 0.42)
    colonnes = [
        {"x": MARGE, "fond": (225, 230, 238), "encre": (98, 108, 130), "puce": GRIS,
         "titre": "Seul", "items": ["Trois devis illisibles",
                                    "Des travaux mal définis",
                                    "Des écarts découverts trop tard",
                                    "Une réception subie"]},
        {"x": MARGE + large + 24, "fond": NUIT, "encre": BLANC, "puce": ORANGE,
         "titre": "Avec le cabinet", "items": ["Un besoin écrit noir sur blanc",
                                               "Des offres comparées ligne à ligne",
                                               "Des visites et des comptes rendus",
                                               "Des réserves posées"]},
    ]
    for colonne in colonnes:
        x = colonne["x"]
        dessin.rounded_rectangle([x, y, x + large, y + hauteur], radius=26, fill=colonne["fond"])
        dessin.text((x + 30, y + 30), colonne["titre"], font=police(GRAS, int(L * 0.040)),
                    fill=colonne["encre"])
        yi = y + 30 + int(L * 0.040) * 1.9
        corps = int(L * 0.029)
        fonte = police(NORMAL, corps)
        for item in colonne["items"]:
            for i, ligne in enumerate(couper(dessin, item, fonte, large - 76)):
                if i == 0:
                    dessin.line([(x + 30, yi + corps * 0.62), (x + 52, yi + corps * 0.62)],
                                fill=colonne["puce"], width=4)
                dessin.text((x + 66, yi), ligne, font=fonte, fill=colonne["encre"])
                yi += corps * 1.35
            yi += corps * 0.6

    y += hauteur + int(H * 0.035)
    dessin.text((MARGE, y), "Vous restez décisionnaire. Le cabinet vérifie.",
                font=police(NORMAL, int(L * 0.030)), fill=(98, 108, 130))
    bouton(image, dessin, "Être accompagné", y + int(H * 0.048))
    return enregistrer(image, "style-duo-amo")


# ---------------------------------------------------------------------------
# 3 · Typo — une phrase enorme, une photo, rien d'autre
# ---------------------------------------------------------------------------

def style_typo():
    image = cadrer(photo("Fissure-maison-PACA.webp"), L, H, 0.5).convert("RGBA")
    image = Image.alpha_composite(image, Image.new("RGBA", (L, H), NUIT + (108,)))
    image = Image.alpha_composite(image, degrade((L, H), int(H * 0.30), int(H * 0.40)))
    dessin = ImageDraw.Draw(image)
    marque(image, dessin)

    corps = int(L * 0.105)
    fonte = police(GRAS, corps)
    lignes = couper(dessin, "Une fissure ne se lit pas à l’œil nu.", fonte, L - 2 * MARGE)
    y = H - int(H * 0.085) - len(lignes) * corps * 1.1 - int(H * 0.115)
    for ligne in lignes:
        dessin.text((MARGE, y), ligne, font=fonte, fill=BLANC)
        y += corps * 1.1

    y += int(H * 0.018)
    dessin.rectangle([MARGE, y, MARGE + 110, y + 6], fill=ORANGE)
    dessin.text((MARGE, y + int(H * 0.028)),
                "Expertise bâtiment · Alpes-Maritimes et Var",
                font=police(DEMI, int(L * 0.032)), fill=BLEU)
    return enregistrer(image, "style-typo-expertise")


# ---------------------------------------------------------------------------
# 4 · Bandeau — un bloc orange oblique en travers de la photo
# ---------------------------------------------------------------------------

def style_bandeau():
    image = cadrer(photo("Expertise-avant-achat-immobilier-1.webp"), L, H, 0.4).convert("RGBA")
    image = Image.alpha_composite(image, Image.new("RGBA", (L, H), NUIT + (70,)))

    # Le bandeau est dessine a plat puis pivote : PIL ne sait pas incliner du
    # texte, mais il sait faire tourner un calque entier.
    calque = Image.new("RGBA", (int(L * 1.5), int(H * 0.22)), (0, 0, 0, 0))
    plume = ImageDraw.Draw(calque)
    plume.rectangle([0, 0, calque.width, calque.height], fill=ORANGE)
    texte = "VOUS ÊTES EXPERT BÂTIMENT ?"
    # Le bandeau est plus large que l'image pour que ses bouts sortent du cadre,
    # mais le texte, lui, doit tenir dans l'image : on cherche le corps qui le
    # fait entrer dans 84 % de la largeur, incliné compris.
    corps = int(L * 0.072)
    while corps > 20 and plume.textlength(texte, font=police(GRAS, corps)) > L * 0.84:
        corps -= 1
    fonte = police(GRAS, corps)
    plume.text(((calque.width - plume.textlength(texte, font=fonte)) / 2,
                (calque.height - corps * 1.32) / 2), texte, font=fonte, fill=NUIT)
    calque = calque.rotate(-7, expand=True, resample=Image.BICUBIC)
    image.alpha_composite(calque, (int((L - calque.width) / 2), int(H * 0.40)))

    image = Image.alpha_composite(image, degrade((L, H), int(H * 0.68), int(H * 0.16)))
    dessin = ImageDraw.Draw(image)
    marque(image, dessin)

    y = int(H * 0.755)
    corps = int(L * 0.036)
    fonte = police(NORMAL, corps)
    for ligne in couper(dessin,
                        "Le cabinet confie des missions d’expertise à des indépendants "
                        "installés, sur le 06 et le 83.", fonte, L - 2 * MARGE):
        dessin.text((MARGE, y), ligne, font=fonte, fill=BLANC)
        y += corps * 1.45
    bouton(image, dessin, "Envoyer ma candidature", y + int(H * 0.022),
           fond=BLANC, encre=NUIT)
    return enregistrer(image, "style-bandeau-recrutement")


# ---------------------------------------------------------------------------
# 5 · Etapes — la mission en quatre temps numerotes
# ---------------------------------------------------------------------------

def style_etapes():
    image = toile()
    dessin = ImageDraw.Draw(image)

    # Photo en bandeau haut, fondue dans le bleu nuit.
    bande = int(H * 0.38)
    haut = cadrer(photo("chantier-renovation-cloisons.jpg"), L, bande, 0.38).convert("RGBA")
    image.alpha_composite(haut, (0, 0))
    image.alpha_composite(degrade((L, bande), int(bande * 0.35), int(bande * 0.65)), (0, 0))
    dessin = ImageDraw.Draw(image)
    marque(image, dessin)

    y = int(H * 0.42)
    surtitre(dessin, "Assistance à maîtrise d’ouvrage", y)

    y += int(H * 0.05)
    corps = int(L * 0.062)
    dessin.text((MARGE, y), "La mission, en quatre temps", font=police(GRAS, corps), fill=BLANC)
    y += corps * 1.5

    etapes = [("Définir", "Ce qu’il faut faire, et ce qui peut attendre."),
              ("Consulter", "Les entreprises, puis comparer leurs offres."),
              ("Suivre", "Des visites, des observations, des comptes rendus."),
              ("Réceptionner", "Les réserves posées, écrites, suivies.")]
    for numero, (titre, detail) in enumerate(etapes, 1):
        dessin.text((MARGE, y), "0%d" % numero, font=police(GRAS, int(L * 0.042)), fill=ORANGE)
        dessin.text((MARGE + 86, y - 2), titre, font=police(DEMI, int(L * 0.038)), fill=BLANC)
        dessin.text((MARGE + 86, y + int(L * 0.045)), detail,
                    font=police(NORMAL, int(L * 0.028)), fill=DOUX)
        y += int(H * 0.082)
        if numero < len(etapes):
            dessin.line([(MARGE, y - 22), (L - MARGE, y - 22)], fill=ARDOISE, width=2)

    bouton(image, dessin, "Découvrir l’AMO", y - 4)
    return enregistrer(image, "style-etapes-amo")


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    style_liste()
    style_duo()
    style_typo()
    style_bandeau()
    style_etapes()
    print("\n%d fichiers dans %s" % (len(os.listdir(SORTIE)), SORTIE))
