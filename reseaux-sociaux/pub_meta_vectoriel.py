# -*- coding: utf-8 -*-
"""Les annonces Meta en SVG et en PDF a texte modifiable.

    python reseaux-sociaux/pub_meta_vectoriel.py

Le JPEG de pub_meta.py est une image aplatie : rien n'y est modifiable. Ici,
seule la photo de fond reste une image — elle porte le recadrage, le voile
bleu nuit et les degrades. Tout le reste est un objet separe : le sur-titre,
le titre, la phrase, le bouton, le filet orange, le pictogramme et le nom du
cabinet. On peut donc corriger une accroche sans tout refaire.

Sorties :
  visuels/pub-meta/svg/<annonce>-<format>.svg   editeurs vectoriels, navigateur
  visuels/pub-meta/pdf/<annonce>-<format>.pdf   Canva, impression
  visuels/pub-meta/pdf/pub-meta.pdf             les quatre 4:5, une page chacune

Les positions viennent toutes de `pub_meta.mesures()` : le JPEG, le SVG et le
PDF sortent du meme gabarit, une seule correction vaut pour les trois.

Deux limites a connaitre :

  - **Canva** reecrit le texte d'un PDF importe avec ses propres polices ; il
    reste modifiable, mais la cesure des lignes peut bouger d'un mot. Verifier
    la mise en page apres import.
  - **Le SVG** appelle la police Segoe UI par son nom, sans l'incorporer : sur
    une machine qui ne l'a pas, le systeme lui substitue une approchante et les
    longueurs de ligne changent un peu. Le PDF, lui, embarque ses polices.
"""

import base64
import os
import sys

import fitz  # PyMuPDF
from PIL import Image, ImageDraw

DOSSIER = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(DOSSIER)
sys.path.insert(0, DOSSIER)

from visuels import NUIT, BLEU, ORANGE, BLANC, GRAS, DEMI, NORMAL, police  # noqa: E402
from couverture_pdf import couleur  # noqa: E402
from pub_meta import (ANNONCES, FORMATS, SORTIE, cadrer, degrade, mesures,  # noqa: E402
                      photo)

SVG = os.path.join(SORTIE, "svg")
PDF = os.path.join(SORTIE, "pdf")
TEMPO = os.path.join(SORTIE, "_tempo")

DOUX = (206, 214, 231)

# Les memes fichiers de police que PIL, cote PDF : les longueurs mesurees a la
# composition et celles du PDF doivent coincider.
FICHIERS = {"titre": "C:/Windows/Fonts/segoeuib.ttf",
            "phrase": "C:/Windows/Fonts/segoeui.ttf",
            "demi": "C:/Windows/Fonts/seguisb.ttf"}
FONTES = {role: fitz.Font(fontfile=chemin) for role, chemin in FICHIERS.items()}

# La correspondance avec les fontes PIL, pour ne pas melanger les deux mondes.
PIL_FONTE = {"titre": GRAS, "phrase": NORMAL, "demi": DEMI}

FAMILLE = {"titre": ("Segoe UI, Arial, sans-serif", "700"),
           "phrase": ("Segoe UI, Arial, sans-serif", "400"),
           "demi": ("Segoe UI Semibold, Segoe UI, Arial, sans-serif", "600")}


def ligne_de_base(y_haut, role, corps):
    """PIL pose le haut de la lettre, PDF et SVG posent la ligne de base."""
    return y_haut + FONTES[role].ascender * corps


def fond_aplati(annonce, taille, chemin):
    """La photo recadree, son voile et ses degrades — sans aucun texte."""
    largeur, hauteur = taille
    m = mesures(annonce, taille)
    image = cadrer(photo(annonce["photo"]), largeur, hauteur,
                   annonce.get("cadrage", 0.5)).convert("RGBA")
    image = Image.alpha_composite(image, Image.new("RGBA", taille, NUIT + (46,)))
    image = Image.alpha_composite(image, degrade(taille, *m["degrade_bas"]))
    image = Image.alpha_composite(image, degrade(taille, *m["degrade_haut"],
                                                 maxi=150, sens="haut"))
    image.convert("RGB").save(chemin, "JPEG", quality=88, optimize=True)
    return chemin


def picto_transparent(chemin):
    """Le pictogramme detoure, pose tel quel dans le SVG et dans le PDF."""
    image = Image.open(os.path.join(RACINE, "identite", "picto-fond-sombre.png"))
    image = image.convert("RGBA")
    image.crop(image.getbbox()).save(chemin)
    return chemin


def echapper(texte):
    return texte.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rvb(teinte):
    return "#%02x%02x%02x" % teinte


def large_lettrage(texte, corps, ecart):
    """Largeur du sur-titre espace lettre a lettre, comme le fait `lettrage()`."""
    regle = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    fonte = police(PIL_FONTE["demi"], corps)
    return sum(regle.textlength(lettre, font=fonte) + ecart for lettre in texte)


# ---------------------------------------------------------------------------
# SVG
# ---------------------------------------------------------------------------

def svg(annonce, taille, suffixe):
    largeur, hauteur = taille
    m = mesures(annonce, taille)
    marge, corps = m["marge"], m["corps"]

    os.makedirs(TEMPO, exist_ok=True)
    jpg = fond_aplati(annonce, taille, os.path.join(TEMPO, "fond.jpg"))
    png = picto_transparent(os.path.join(TEMPO, "picto.png"))

    def encoder(chemin, genre):
        with open(chemin, "rb") as fichier:
            return "data:image/%s;base64,%s" % (
                genre, base64.b64encode(fichier.read()).decode("ascii"))

    def texte(contenu, x, y_haut, role, corps_texte, teinte, ecart=None):
        famille, graisse = FAMILLE[role]
        espace = ' letter-spacing="%.1f"' % ecart if ecart else ""
        return ('  <text x="%.1f" y="%.1f" font-family="%s" font-weight="%s" '
                'font-size="%d" fill="%s"%s xml:space="preserve">%s</text>'
                % (x, ligne_de_base(y_haut, role, corps_texte), famille, graisse,
                   corps_texte, rvb(teinte), espace, echapper(contenu)))

    lignes = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
              'width="%d" height="%d" viewBox="0 0 %d %d">' % (largeur, hauteur, largeur, hauteur),
              '  <title>%s</title>' % echapper(annonce["titre"]),
              '  <image x="0" y="0" width="%d" height="%d" xlink:href="%s"/>'
              % (largeur, hauteur, encoder(jpg, "jpeg")),
              '  <image x="%d" y="%d" width="%d" height="%d" xlink:href="%s"/>'
              % (marge, m["y_logo"], m["cote_logo"], m["cote_logo"], encoder(png, "png")),
              texte("BTP EXPERTISE", m["x_marque"], m["y_logo"] + int(largeur * 0.008),
                    "demi", corps["marque"], BLANC)]

    entete = annonce["entete"].upper()
    lignes.append(texte(entete, marge, m["y_entete"], "demi", corps["entete"], BLEU,
                        ecart=m["ecart_entete"]))
    lignes.append('  <rect x="%d" y="%.1f" width="%.1f" height="4" fill="%s"/>'
                  % (marge, m["y_filet"],
                     large_lettrage(entete, corps["entete"], m["ecart_entete"]) - 3,
                     rvb(ORANGE)))

    y = m["haut_bloc"]
    for ligne in m["lignes_titre"]:
        lignes.append(texte(ligne, marge, y, "titre", corps["titre"], BLANC))
        y += corps["titre"] * m["inter_titre"]
    y += corps["titre"] * m["saut_titre"]

    for ligne in m["lignes_phrase"]:
        lignes.append(texte(ligne, marge, y, "phrase", corps["phrase"], DOUX))
        y += corps["phrase"] * m["inter_phrase"]
    y += corps["phrase"] * m["saut_phrase"]

    haut = m["haut_bouton"]
    lignes.append('  <rect x="%d" y="%.1f" width="%d" height="%d" rx="%d" fill="%s"/>'
                  % (marge, y, m["large_bouton"], haut, haut // 2, rvb(ORANGE)))
    lignes.append(texte(annonce["bouton"], marge + corps["bouton"] * 1.3,
                        y + (haut - corps["bouton"] * 1.32) / 2,
                        "demi", corps["bouton"], NUIT))
    lignes.append('</svg>')

    chemin = os.path.join(SVG, "%s%s.svg" % (annonce["cle"], suffixe))
    with open(chemin, "w", encoding="utf-8") as fichier:
        fichier.write("\n".join(lignes) + "\n")
    return chemin


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------

def page_pdf(document, annonce, taille):
    largeur, hauteur = taille
    m = mesures(annonce, taille)
    marge, corps = m["marge"], m["corps"]

    os.makedirs(TEMPO, exist_ok=True)
    jpg = fond_aplati(annonce, taille, os.path.join(TEMPO, "fond.jpg"))
    png = picto_transparent(os.path.join(TEMPO, "picto.png"))

    page = document.new_page(width=largeur, height=hauteur)
    page.insert_image(fitz.Rect(0, 0, largeur, hauteur), filename=jpg)
    page.insert_image(fitz.Rect(marge, m["y_logo"],
                                marge + m["cote_logo"], m["y_logo"] + m["cote_logo"]),
                      filename=png, keep_proportion=True)

    def ecrire(contenu, x, y_haut, role, corps_texte, teinte):
        plume = fitz.TextWriter(page.rect)
        plume.append(fitz.Point(x, ligne_de_base(y_haut, role, corps_texte)), contenu,
                     font=FONTES[role], fontsize=corps_texte)
        plume.write_text(page, color=couleur(teinte))

    ecrire("BTP EXPERTISE", m["x_marque"], m["y_logo"] + int(largeur * 0.008),
           "demi", corps["marque"], BLANC)

    # Sur-titre : lettre a lettre, pour retrouver l'espacement de la version PNG.
    entete = annonce["entete"].upper()
    plume = fitz.TextWriter(page.rect)
    x = marge
    base = ligne_de_base(m["y_entete"], "demi", corps["entete"])
    regle = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    fonte_pil = police(PIL_FONTE["demi"], corps["entete"])
    for lettre in entete:
        plume.append(fitz.Point(x, base), lettre, font=FONTES["demi"],
                     fontsize=corps["entete"])
        x += regle.textlength(lettre, font=fonte_pil) + m["ecart_entete"]
    plume.write_text(page, color=couleur(BLEU))
    page.draw_rect(fitz.Rect(marge, m["y_filet"], x - 3, m["y_filet"] + 4),
                   color=None, fill=couleur(ORANGE))

    y = m["haut_bloc"]
    for ligne in m["lignes_titre"]:
        ecrire(ligne, marge, y, "titre", corps["titre"], BLANC)
        y += corps["titre"] * m["inter_titre"]
    y += corps["titre"] * m["saut_titre"]

    for ligne in m["lignes_phrase"]:
        ecrire(ligne, marge, y, "phrase", corps["phrase"], DOUX)
        y += corps["phrase"] * m["inter_phrase"]
    y += corps["phrase"] * m["saut_phrase"]

    haut = m["haut_bouton"]
    page.draw_rect(fitz.Rect(marge, y, marge + m["large_bouton"], y + haut),
                   color=None, fill=couleur(ORANGE), radius=0.5)
    ecrire(annonce["bouton"], marge + corps["bouton"] * 1.3,
           y + (haut - corps["bouton"] * 1.32) / 2, "demi", corps["bouton"], NUIT)
    return page


def pdf(annonce, taille, suffixe):
    document = fitz.open()
    page_pdf(document, annonce, taille)
    chemin = os.path.join(PDF, "%s%s.pdf" % (annonce["cle"], suffixe))
    document.save(chemin, garbage=3, deflate=True)
    document.close()
    return chemin


if __name__ == "__main__":
    for dossier in (SVG, PDF, TEMPO):
        os.makedirs(dossier, exist_ok=True)

    for annonce in ANNONCES:
        for taille, suffixe in FORMATS:
            svg(annonce, taille, suffixe)
            pdf(annonce, taille, suffixe)
        print("%-26s svg + pdf en 4x5, 1x1, 9x16" % annonce["cle"])

    # Deux recueils : tout, et les seules annonces de recrutement.
    for nom, choisies in (("pub-meta.pdf", ANNONCES),
                          ("recrutement-meta.pdf",
                           [a for a in ANNONCES if a["cle"].startswith("pub-recrutement")])):
        recueil = fitz.open()
        for annonce in choisies:
            page_pdf(recueil, annonce, FORMATS[0][0])
        chemin = os.path.join(PDF, nom)
        recueil.save(chemin, garbage=3, deflate=True)
        recueil.close()
        print("\n%-26s %d pages en 4:5, %.0f Ko" % (nom, len(choisies),
                                                    os.path.getsize(chemin) / 1024))

    for reste in os.listdir(TEMPO):
        os.remove(os.path.join(TEMPO, reste))
    os.rmdir(TEMPO)
