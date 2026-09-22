# -*- coding: utf-8 -*-
"""Visuels publicitaires Meta — photo en fond, accroche courte, bouton.

Autre usage, donc autre gabarit que posts_carte.py : une publicite se lit en
une demi-seconde dans un fil, entre deux photos de vacances. Il lui faut une
image, une phrase et un bouton — pas une planche a lire.

    python reseaux-sociaux/pub_meta.py

Sort trois formats par annonce, ceux que Meta demande dans un meme jeu :
  -4x5    1080 x 1350   fil Facebook et Instagram (le format qui performe)
  -1x1    1080 x 1080   fil, carrousel, colonne de droite
  -9x16   1080 x 1920   stories et reels

La marque reste celle du cabinet : bleu nuit, filet orange, logo en haut a
gauche. Le texte tient volontairement en peu de mots — Meta ne bloque plus les
visuels charges, mais il les diffuse moins bien.

ATTENTION, annonces de recrutement : dans le gestionnaire de publicites, il
faut declarer la **categorie speciale « Emploi »**. Sans cela Meta rejette
l'annonce, et un compte qui recidive est restreint. Cette categorie interdit
le ciblage par age, sexe et code postal precis : viser large sur le 06 et le
83, et laisser l'annonce filtrer.

Les photos viennent de site/assets/img/ : ce sont celles du site, donc le
prospect qui clique retrouve le meme univers. Le jour ou Mickael fournit ses
propres photos de chantier, il suffit de changer la valeur `photo`.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter

DOSSIER = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(DOSSIER)
sys.path.insert(0, DOSSIER)

from visuels import NUIT, BLEU, ORANGE, BLANC, GRAS, DEMI, NORMAL, logo, police, poser, couvrir  # noqa: E402
from posts_planche import couper, lettrage  # noqa: E402

from PIL import Image as _Image


def photo(nom):
    """Cherche la photo : chantiers reels d'abord, puis le site, puis la reserve.

    `photos-chantier/` passe en premier : une vraie photo de Mickael doit
    toujours l'emporter sur l'image de banque de meme sujet.
    """
    for dossier in (os.path.join(RACINE, "photos-chantier"),
                    os.path.join(RACINE, "site", "assets", "img"),
                    os.path.join(RACINE, "reserve-images")):
        chemin = os.path.join(dossier, nom)
        if os.path.exists(chemin):
            return _Image.open(chemin).convert("RGBA")
    raise FileNotFoundError(nom)

SORTIE = os.path.join(DOSSIER, "visuels", "pub-meta")

FORMATS = (((1080, 1350), "-4x5"), ((1080, 1080), "-1x1"), ((1080, 1920), "-9x16"))

ANNONCES = [
    # --- Vendre l'AMO ----------------------------------------------------
    {"cle": "pub-amo-devis",
     "photo": "comp-maitrise-oeuvre.webp",
     "entete": "Assistance à maîtrise d’ouvrage",
     "titre": "Trois devis. Lequel est le bon ?",
     "phrase": "Un professionnel du bâtiment les compare avec vous, ligne à ligne.",
     "bouton": "Parler de mon projet"},

    {"cle": "pub-amo-chantier",
     # Photo de chantier de Mickael — une vraie piece en travaux, pas une
     # image de banque : c'est ce qui distingue l'annonce de la concurrence.
     "photo": "chantier-renovation-cloisons.jpg",
     "cadrage": 0.46,
     "entete": "Travaux · Alpes-Maritimes & Var",
     "titre": "Ne restez pas seul face aux entreprises",
     "phrase": "Définition des travaux, analyse des devis, visites de chantier, réception.",
     "bouton": "Être accompagné"},

    # --- Recruter des independants ---------------------------------------
    # Categorie speciale « Emploi » obligatoire cote Meta (voir l'en-tete).
    {"cle": "pub-recrutement-amo",
     "photo": "Expertise-avant-achat-immobilier-1.webp",
     "entete": "Recrutement · 06 & 83",
     "titre": "Vous êtes AMO indépendant ?",
     "phrase": "Le cabinet confie des missions à un réseau de professionnels indépendants.",
     "bouton": "Envoyer ma candidature"},

    {"cle": "pub-recrutement-expertise",
     "photo": "Fissure-maison-PACA.webp",
     # L'interpellation passe en sur-titre : le grand titre dit alors ce qui est
     # propose, et la phrase ce qu'il y a a faire.
     "entete": "Vous êtes expert bâtiment ?",
     # Titre court volontairement : « sur le 06 et le 83 » le faisait passer a
     # trois lignes, la derniere reduite a « le 83 ». La zone est dans la phrase.
     "titre": "Le cabinet cherche un indépendant",
     "phrase": "Fissures, humidité, malfaçons : des expertises à mener sur le 06 et le 83.",
     "bouton": "Envoyer ma candidature"},
]


def degrade(taille, depart, hauteur_utile, teinte=NUIT, maxi=246, sens="bas"):
    """Voile de marque, transparent au-dela de `depart`.

    Sans lui, un titre blanc pose sur une photo claire devient illisible des
    que Meta recompresse l'image. `sens="haut"` retourne le degrade pour
    asseoir le logo, qui tombe parfois sur un ciel ou un mur blanc.
    """
    largeur, hauteur = taille
    masque = Image.new("L", (1, hauteur), 0)
    plume = ImageDraw.Draw(masque)
    for y in range(hauteur):
        if y < depart:
            v = 0
        else:
            t = min(1.0, (y - depart) / max(1, hauteur_utile))
            v = int(maxi * (t ** 0.85))
        plume.point((0, y), fill=v)
    if sens == "haut":
        masque = masque.transpose(Image.FLIP_TOP_BOTTOM)
    masque = masque.resize((largeur, hauteur))
    voile = Image.new("RGBA", (largeur, hauteur), teinte + (0,))
    voile.putalpha(masque)
    return voile


def cadrer(photo, largeur, hauteur, ancre=0.5):
    """Recadre en remplissant la zone, avec le point d'interet a `ancre`.

    `couvrir()` de visuels.py coupe toujours au centre. Sur une photo de
    telephone, tres verticale, le centre tombe souvent sur le sol : `ancre`
    donne la part de l'image a garder au-dessus du cadre (0 = le haut).
    """
    ratio = max(largeur / photo.width, hauteur / photo.height)
    photo = photo.resize((int(photo.width * ratio) + 1, int(photo.height * ratio) + 1),
                         Image.LANCZOS)
    x = (photo.width - largeur) // 2
    y = int((photo.height - hauteur) * ancre)
    return photo.crop((x, y, x + largeur, y + hauteur))


def mesures(annonce, taille):
    """Toutes les positions de l'annonce, sans rien dessiner.

    Partagee avec pub_meta_vectoriel.py, qui refait la meme page en SVG et en
    PDF a texte modifiable : une seule source de verite pour la mise en page,
    comme `mesures_carte()` l'est pour les planches.
    """
    largeur, hauteur = taille
    story = hauteur > largeur * 1.5
    marge = int(largeur * 0.085)
    # Zone sure : dans une story, les interfaces mangent le bas de l'ecran.
    bas = hauteur - (int(hauteur * 0.16) if story else marge)

    corps = {"titre": int(largeur * (0.072 if not story else 0.075)),
             "phrase": int(largeur * 0.034),
             "entete": int(largeur * 0.024),
             "bouton": int(largeur * 0.033),
             "marque": int(largeur * 0.030)}

    regle = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    utile = largeur - 2 * marge
    lignes_titre = couper(regle, annonce["titre"], police(GRAS, corps["titre"]), utile)
    lignes_phrase = couper(regle, annonce["phrase"], police(NORMAL, corps["phrase"]), utile)

    haut_bouton = int(corps["bouton"] * 2.5)
    bloc = (len(lignes_titre) * corps["titre"] * 1.22 + corps["titre"] * 0.55
            + len(lignes_phrase) * corps["phrase"] * 1.45 + corps["phrase"] * 1.1
            + haut_bouton)
    haut_bloc = bas - bloc

    m = {"largeur": largeur, "hauteur": hauteur, "story": story, "marge": marge,
         "utile": utile, "corps": corps, "lignes_titre": lignes_titre,
         "lignes_phrase": lignes_phrase, "haut_bouton": haut_bouton,
         "haut_bloc": haut_bloc,
         "inter_titre": 1.22, "saut_titre": 0.55,
         "inter_phrase": 1.45, "saut_phrase": 1.1,
         "y_entete": haut_bloc - corps["entete"] * 2.4,
         "y_filet": haut_bloc - corps["entete"] * 1.05,
         "ecart_entete": 3.0,
         # Le degrade doit etre franc **au niveau du sur-titre**, pas seulement
         # sous le grand titre : un cyan pose sur une photo claire disparait.
         "degrade_bas": (int(haut_bloc - hauteur * 0.20), int(hauteur * 0.17)),
         "degrade_haut": (int(hauteur * 0.82), int(hauteur * 0.14)),
         "y_logo": marge if not story else int(hauteur * 0.09),
         "cote_logo": int(largeur * 0.056),
         "x_marque": marge + int(largeur * 0.075)}
    m["large_bouton"] = int(regle.textlength(annonce["bouton"],
                                             font=police(DEMI, corps["bouton"]))
                            + corps["bouton"] * 2.6)
    return m


def composer(annonce, taille, suffixe):
    largeur, hauteur = taille
    m = mesures(annonce, taille)
    marge, corps = m["marge"], m["corps"]

    fond = cadrer(photo(annonce["photo"]), largeur, hauteur,
                  annonce.get("cadrage", 0.5)).convert("RGBA")
    # Leger voile general : la photo recule, le texte passe devant.
    fond = Image.alpha_composite(fond, Image.new("RGBA", (largeur, hauteur), NUIT + (46,)))
    fond = Image.alpha_composite(fond, degrade(taille, *m["degrade_bas"]))
    # Bandeau haut, plus leger : il porte le logo et la signature.
    fond = Image.alpha_composite(fond, degrade(taille, *m["degrade_haut"],
                                               maxi=150, sens="haut"))

    dessin = ImageDraw.Draw(fond)
    f_titre = police(GRAS, corps["titre"])
    f_phrase = police(NORMAL, corps["phrase"])
    f_entete = police(DEMI, corps["entete"])
    f_bouton = police(DEMI, corps["bouton"])

    # --- Marque, en haut a gauche ---------------------------------------
    picto = logo("picto-fond-sombre.png")
    picto = picto.crop(picto.getbbox())
    poser(fond, picto, marge + m["cote_logo"] / 2, m["y_logo"] + m["cote_logo"] / 2,
          m["cote_logo"])
    dessin.text((m["x_marque"], m["y_logo"] + int(largeur * 0.008)),
                "BTP EXPERTISE", font=police(DEMI, corps["marque"]), fill=BLANC)

    # --- Bloc bas --------------------------------------------------------
    x = lettrage(dessin, (marge, m["y_entete"]), annonce["entete"].upper(),
                 f_entete, BLEU, m["ecart_entete"])
    dessin.line([(marge, m["y_filet"]), (x - 3, m["y_filet"])], fill=ORANGE, width=4)

    y = m["haut_bloc"]
    for ligne in m["lignes_titre"]:
        dessin.text((marge, y), ligne, font=f_titre, fill=BLANC)
        y += corps["titre"] * m["inter_titre"]
    y += corps["titre"] * m["saut_titre"]

    for ligne in m["lignes_phrase"]:
        dessin.text((marge, y), ligne, font=f_phrase, fill=(206, 214, 231))
        y += corps["phrase"] * m["inter_phrase"]
    y += corps["phrase"] * m["saut_phrase"]

    # Bouton : ce n'est pas le bouton cliquable de Meta, c'est son rappel —
    # l'oeil comprend qu'il y a quelque chose a faire.
    haut_bouton = m["haut_bouton"]
    dessin.rounded_rectangle([marge, y, marge + m["large_bouton"], y + haut_bouton],
                             radius=int(haut_bouton / 2), fill=ORANGE)
    dessin.text((marge + corps["bouton"] * 1.3,
                 y + (haut_bouton - corps["bouton"] * 1.32) / 2),
                annonce["bouton"], font=f_bouton, fill=NUIT)

    chemin = os.path.join(SORTIE, "%s%s.jpg" % (annonce["cle"], suffixe))
    # JPEG : Meta recompresse de toute facon, et un PNG lourd ralentit le
    # televersement d'un jeu de trois formats par annonce.
    fond.convert("RGB").save(chemin, "JPEG", quality=92, optimize=True)
    return chemin


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    for annonce in ANNONCES:
        for taille, suffixe in FORMATS:
            composer(annonce, taille, suffixe)
        print("%-26s 4x5 · 1x1 · 9x16" % annonce["cle"])
    print("\n%d fichiers dans %s" % (len(os.listdir(SORTIE)), SORTIE))
