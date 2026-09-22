# -*- coding: utf-8 -*-
"""Visuels des pages Facebook et Instagram de BTP Expertise.

Produit dans reseaux-sociaux/visuels/ les images aux formats attendus par
Meta, a partir du logo de identite/ et des photos du site.

    python reseaux-sociaux/visuels.py

Formats produits :
  profil-1080.png            photo de profil Facebook et Instagram (carre,
                             affichee en rond : marge de securite prevue)
  couverture-facebook.png    1640 x 664, contenu utile dans la bande centrale
  couverture-facebook-mobile-preview.png  ce que le mobile en garde
  post-annonce-1080.png      premier post d'ouverture, carre
  story-annonce-1080x1920.png  version story / reel de couverture
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "reseaux-sociaux", "visuels")

NUIT = (38, 44, 66)
BLEU = (11, 187, 246)
ORANGE = (255, 138, 0)
BLANC = (255, 255, 255)

POLICES = "C:/Windows/Fonts/"


def police(nom, taille):
    """Segoe UI a defaut de Montserrat, qui n'est pas installee sur ce PC."""
    for fichier in (nom, "segoeuib.ttf", "arialbd.ttf"):
        chemin = os.path.join(POLICES, fichier)
        if os.path.exists(chemin):
            return ImageFont.truetype(chemin, taille)
    return ImageFont.load_default()


GRAS = "segoeuib.ttf"
DEMI = "seguisb.ttf"
NORMAL = "segoeui.ttf"


def image(nom):
    return Image.open(os.path.join(RACINE, "site", "assets", "img", nom)).convert("RGBA")


def logo(nom):
    return Image.open(os.path.join(RACINE, "identite", nom)).convert("RGBA")


def poser(fond, calque, x, y, largeur):
    """Colle calque redimensionne a `largeur`, centre sur (x, y)."""
    ratio = largeur / calque.width
    hauteur = int(calque.height * ratio)
    calque = calque.resize((largeur, hauteur), Image.LANCZOS)
    fond.alpha_composite(calque, (int(x - largeur / 2), int(y - hauteur / 2)))
    return hauteur


def centrer_texte(dessin, y, texte, fonte, couleur, largeur_totale, interligne=1.35):
    """Ecrit un texte centre, une ligne par element de `texte` si c'est une liste."""
    lignes = texte if isinstance(texte, (list, tuple)) else [texte]
    for ligne in lignes:
        boite = dessin.textbbox((0, 0), ligne, font=fonte)
        largeur = boite[2] - boite[0]
        dessin.text((largeur_totale / 2 - largeur / 2, y), ligne, font=fonte, fill=couleur)
        y += (boite[3] - boite[1]) * interligne + fonte.size * 0.35
    return y


def ombre_portee(calque, decalage=(0, 14), flou=26, opacite=0.34, teinte=NUIT):
    """Pose une ombre douce sous un PNG transparent.

    L'ombre est la silhouette du calque — son canal alpha — decalee, floutee
    et attenuee. La toile est agrandie de la portee du flou, sinon l'ombre est
    coupee net au bord de l'image.
    """
    marge = flou * 3
    dx, dy = decalage
    taille = (calque.width + 2 * marge, calque.height + 2 * marge)

    masque = Image.new("L", taille, 0)
    masque.paste(calque.split()[3], (marge + dx, marge + dy))
    masque = masque.filter(ImageFilter.GaussianBlur(flou))
    masque = masque.point(lambda v: int(v * opacite))

    ombre = Image.new("RGBA", taille, teinte + (0,))
    ombre.putalpha(masque)
    ombre.alpha_composite(calque, (marge, marge))
    return ombre


def couvrir(photo, largeur, hauteur):
    """Recadre la photo en remplissant la zone, comme un background-size: cover."""
    ratio = max(largeur / photo.width, hauteur / photo.height)
    photo = photo.resize((int(photo.width * ratio) + 1, int(photo.height * ratio) + 1), Image.LANCZOS)
    x = (photo.width - largeur) // 2
    y = (photo.height - hauteur) // 2
    return photo.crop((x, y, x + largeur, y + hauteur))


# ---------------------------------------------------------------------------
# Photo de profil : le pictogramme sur fond blanc, dans le cercle de securite
# ---------------------------------------------------------------------------

def profil():
    """Deux versions : fond blanc (sobre) et fond bleu nuit (plus visible au fil).

    La version claire porte une ombre douce : sur le blanc du profil, le
    pictogramme manquait de relief. Sur fond nuit, une ombre sombre ne se
    verrait pas — inutile de l'ajouter.

    Chaque version sort aussi en JPEG : Instagram refuse regulierement les PNG
    a canal alpha au televersement de la photo de profil.
    """
    for nom, marque, couleur, ombre in (
        ("profil-1080", "picto.png", BLANC, True),
        ("profil-1080-fond-nuit", "picto-fond-sombre.png", NUIT, False),
    ):
        taille = 1080
        fond = Image.new("RGBA", (taille, taille), couleur + (255,))
        picto = logo(marque)
        picto = picto.crop(picto.getbbox())  # le PNG source a des marges inegales

        # Facebook et Instagram rognent en rond : le pictogramme lui-meme doit
        # tenir dans ~58 % du carre, sinon ses bords touchent la decoupe.
        large_picto = int(taille * 0.58)
        if picto.height > picto.width:
            large_picto = int(large_picto * picto.width / picto.height)

        if ombre:
            nu = picto.width
            picto = ombre_portee(picto, decalage=(0, 14), flou=22, opacite=0.28)
            # L'ombre agrandit la toile : on redimensionne la toile entiere pour
            # que le pictogramme, lui, garde la taille voulue.
            large_picto = int(large_picto * picto.width / nu)

        poser(fond, picto, taille / 2, taille / 2, large_picto)

        plat = fond.convert("RGB")
        plat.save(os.path.join(SORTIE, nom + ".png"))
        # JPEG sans transparence ni metadonnees : le fichier a donner a Instagram,
        # qui refuse regulierement les PNG a canal alpha.
        plat.save(os.path.join(SORTIE, nom + ".jpg"), "JPEG", quality=92, optimize=True)
        # Version legere, a essayer si le televersement echoue encore.
        plat.resize((640, 640), Image.LANCZOS).save(
            os.path.join(SORTIE, nom.replace("1080", "640") + ".jpg"),
            "JPEG", quality=88, optimize=True)


def logos_ombres():
    """Versions ombrees du logo, pour les documents et les reseaux."""
    dossier = os.path.join(RACINE, "identite")
    for nom in ("logo-principal.png", "logo-compact.png"):
        avec = ombre_portee(logo(nom))
        avec.save(os.path.join(dossier, nom.replace(".png", "-ombre.png")))


# ---------------------------------------------------------------------------
# Couverture Facebook
# ---------------------------------------------------------------------------

def couverture():
    largeur, hauteur = 1640, 664
    photo = couvrir(image("hand-construction-plans-with-yellow-helmet-drawing-tool.webp"), largeur, hauteur)
    photo = photo.filter(ImageFilter.GaussianBlur(2))

    voile = Image.new("RGBA", (largeur, hauteur), NUIT + (222,))
    fond = Image.alpha_composite(photo, voile)

    dessin = ImageDraw.Draw(fond)
    # Le mobile ne garde qu'une bande centrale : tout le contenu y reste.
    poser(fond, logo("logo-fond-sombre.png"), largeur / 2, 200, 430)

    y = centrer_texte(dessin, 400, "Expertise bâtiment & Assistance à Maîtrise d’Ouvrage",
                      police(DEMI, 36), BLANC, largeur)
    centrer_texte(dessin, y + 6, "Alpes-Maritimes (06) et Var (83)",
                  police(NORMAL, 30), BLEU, largeur)

    # Filet orange, repris du site
    dessin.rectangle([largeur / 2 - 70, 520, largeur / 2 + 70, 525], fill=ORANGE)
    centrer_texte(dessin, 548, "btpexpertise.fr  ·  06 81 65 15 91",
                  police(DEMI, 32), BLANC, largeur)

    fond.convert("RGB").save(os.path.join(SORTIE, "couverture-facebook.png"))

    # Ce que le telephone garde de la couverture : bande centrale au ratio 16:9.
    apercu = fond.crop((int(largeur / 2 - 590), 0, int(largeur / 2 + 590), hauteur))
    apercu.convert("RGB").save(os.path.join(SORTIE, "couverture-facebook-mobile-preview.png"))


# ---------------------------------------------------------------------------
# Post d'annonce
# ---------------------------------------------------------------------------

def annonce(taille=(1080, 1080), nom="post-annonce-1080.png"):
    largeur, hauteur = taille
    photo = couvrir(image("Expertise-batiment-PACA.webp"), largeur, hauteur)
    voile = Image.new("RGBA", (largeur, hauteur), NUIT + (232,))
    fond = Image.alpha_composite(photo, voile)
    dessin = ImageDraw.Draw(fond)

    marque = logo("logo-fond-sombre.png")
    large_logo = int(largeur * 0.46)
    haut_logo = int(marque.height * large_logo / marque.width)

    titre = police(GRAS, int(largeur * 0.050))
    chapo = police(NORMAL, int(largeur * 0.036))
    pied = police(DEMI, int(largeur * 0.038))

    bloc = (haut_logo + int(largeur * 0.07)          # logo + respiration
            + 2 * titre.size * 1.5 + int(largeur * 0.03)
            + 2 * chapo.size * 1.6 + int(largeur * 0.05)
            + 2 * pied.size * 1.6
            + largeur * 0.11)   # marge : les hauteurs mesurees sont approchees
    y = (hauteur - bloc) / 2

    poser(fond, marque, largeur / 2, y + haut_logo / 2, large_logo)
    y += haut_logo + largeur * 0.07

    y = centrer_texte(dessin, y, ["Fissures, infiltrations,", "malfaçons, réception de travaux"],
                      titre, BLANC, largeur, interligne=1.5)
    y = centrer_texte(dessin, y + largeur * 0.03,
                      ["Un regard technique indépendant", "pour comprendre votre bâtiment"],
                      chapo, (205, 212, 228), largeur, interligne=1.6)

    y += largeur * 0.04
    dessin.rectangle([largeur / 2 - 60, y, largeur / 2 + 60, y + 5], fill=ORANGE)
    centrer_texte(dessin, y + largeur * 0.035, ["Nice · Cannes · Antibes", "btpexpertise.fr"],
                  pied, BLEU, largeur, interligne=1.6)

    fond.convert("RGB").save(os.path.join(SORTIE, nom))


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    profil()
    logos_ombres()
    couverture()
    annonce()
    annonce((1080, 1920), "story-annonce-1080x1920.png")
    for fichier in sorted(os.listdir(SORTIE)):
        chemin = os.path.join(SORTIE, fichier)
        print("%-42s %6.0f Ko" % (fichier, os.path.getsize(chemin) / 1024))
