# -*- coding: utf-8 -*-
"""Planches et cartes en PDF, pour reprise dans Canva.

Les positions viennent de `posts_planche.mesures()` et
`posts_carte.mesures_carte()` : le PDF et le PNG sortent du meme gabarit.

Ce qui est vectoriel : le quadrillage, les aplats, le cartouche et **tous les
textes de mise en page** — entete, titre, phrase, listes, chiffres, pied. Ce
qui reste en image : le schema dessine des planches, avec ses reperes, et le
pictogramme. Un schema eclate en centaines d'objets serait ingerable dans
Canva ; le texte editable, lui, est ce qu'on veut vraiment pouvoir corriger.

    python reseaux-sociaux/planches_pdf.py

Produit dans visuels/planches/pdf/ : un PDF par sujet, plus les recueils
`planches-carre.pdf` / `planches-story.pdf`, qui ouvrent les quinze
publications comme un document multipage.
"""

import os
import sys

import fitz  # PyMuPDF
from PIL import Image, ImageDraw

DOSSIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DOSSIER)

from visuels import NUIT, BLEU, ORANGE, BLANC, GRAS, DEMI, NORMAL, police  # noqa: E402
from couverture_pdf import couleur  # noqa: E402
from posts_pdf import FONTES, mesurer, ligne_de_base  # noqa: E402
import posts_planche as planche  # noqa: E402
import posts_carte as carte  # noqa: E402

SORTIE = os.path.join(DOSSIER, "visuels", "planches", "pdf")
TEMPO = os.path.join(SORTIE, "_tempo")

# Le recueil suit l'ordre de publication : presentation, puis les services.
ORDRE = [
    "ouverture", "visite-technique", "honoraires",
    "parcours", "fissures", "malfacons",
    "argiles", "amo", "humidite",
    "etancheite", "rapport", "reception",
    "litiges", "electricite", "avant-achat",
    "expert-vs-immo", "avant-achat-planche", "independance",
    "plomberie", "reunion", "zones",
]


def ecrire(page, texte, role, corps, x, y_haut, teinte):
    """Une ligne de texte, posee comme Pillow la poserait."""
    plume = fitz.TextWriter(page.rect)
    plume.append(fitz.Point(x, ligne_de_base(y_haut, role, corps)), texte,
                 font=FONTES[role], fontsize=corps)
    plume.write_text(page, color=couleur(teinte))


def lettrage(page, texte, role, corps, x, y_haut, teinte, ecart=3.0):
    plume = fitz.TextWriter(page.rect)
    base = ligne_de_base(y_haut, role, corps)
    for lettre in texte:
        plume.append(fitz.Point(x, base), lettre, font=FONTES[role], fontsize=corps)
        x += mesurer(lettre, role, corps) + ecart
    plume.write_text(page, color=couleur(teinte))
    return x


def quadrillage(page, largeur, hauteur, pas, teinte, fort=None):
    for i, x in enumerate(range(0, int(largeur) + 1, pas)):
        t = fort if (fort and i % 5 == 0) else teinte
        page.draw_line(fitz.Point(x, 0), fitz.Point(x, hauteur), color=couleur(t), width=1)
    for i, y in enumerate(range(0, int(hauteur) + 1, pas)):
        t = fort if (fort and i % 5 == 0) else teinte
        page.draw_line(fitz.Point(0, y), fitz.Point(largeur, y), color=couleur(t), width=1)


def picto(page, chemin, x, y, cote):
    page.insert_image(fitz.Rect(x, y, x + cote, y + cote), filename=chemin, keep_proportion=True)


def chemin_logo(nom):
    return os.path.join(os.path.dirname(DOSSIER), "identite", nom)


# ---------------------------------------------------------------------------
# Planches
# ---------------------------------------------------------------------------

def page_planche(document, cle, entete, titre, phrase, taille):
    largeur, hauteur = taille
    mesureur = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    m = planche.mesures(taille, titre, phrase, mesureur)
    marge = m["marge"]

    page = document.new_page(width=largeur, height=hauteur)
    page.draw_rect(fitz.Rect(0, 0, largeur, hauteur), color=None, fill=couleur(planche.PAPIER))
    quadrillage(page, largeur, hauteur, 27, planche.CARREAU, planche.CARREAU_FORT)

    # Le schema garde ses reperes : il part en image transparente.
    calque = planche.calque_schema(cle, taille, m)
    fichier = os.path.join(TEMPO, "schema-%s-%d.png" % (cle, hauteur))
    calque.save(fichier)
    page.insert_image(fitz.Rect(0, 0, largeur, hauteur), filename=fichier)

    corps = m["corps"]["entete"]
    x = lettrage(page, entete.upper(), "etiquette", corps, marge, m["y_entete"], NUIT)
    page.draw_rect(fitz.Rect(marge, m["y_entete"] + corps + 16, x - 3,
                             m["y_entete"] + corps + 20), color=None, fill=couleur(ORANGE))

    y = m["haut_texte"]
    for ligne in m["lignes_titre"]:
        ecrire(page, ligne, "titre", m["corps"]["titre"], marge, y, NUIT)
        y += m["corps"]["titre"] * m["inter_titre"]
    y += 22
    for ligne in m["lignes_phrase"]:
        ecrire(page, ligne, "phrase", m["corps"]["phrase"], marge, y, planche.GRIS)
        y += m["corps"]["phrase"] * m["inter_phrase"]

    # Cartouche
    bas = m["bas_cartouche"]
    haut = bas - 92
    page.draw_rect(fitz.Rect(marge, haut, largeur - marge, bas),
                   color=couleur(NUIT), fill=couleur(BLANC), width=2)
    picto(page, chemin_logo("picto.png"), marge + 32, (haut + bas) / 2 - 26, 52)
    ecrire(page, "BTP EXPERTISE", "titre", 27, marge + 100, haut + 22, NUIT)
    ecrire(page, "Expertise bâtiment & AMO", "phrase", 21, marge + 100, haut + 54, planche.GRIS)

    x_case = largeur - marge - 250
    page.draw_line(fitz.Point(x_case, haut), fitz.Point(x_case, bas), color=couleur(NUIT), width=2)
    ecrire(page, "Alpes-Maritimes · Var", "phrase", 21, x_case + 26, haut + 22, planche.GRIS)
    ecrire(page, "btpexpertise.fr", "pied", 24, x_case + 26, haut + 50, BLEU)


# ---------------------------------------------------------------------------
# Cartes
# ---------------------------------------------------------------------------

def page_carte(document, fiche, taille):
    largeur, hauteur = taille
    theme = carte.THEMES[fiche.get("theme", "nuit")]
    mesureur = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    m = carte.mesures_carte(fiche, taille, mesureur)
    marge, corps = m["marge"], m["corps"]

    page = document.new_page(width=largeur, height=hauteur)
    page.draw_rect(fitz.Rect(0, 0, largeur, hauteur), color=None, fill=couleur(theme["fond"]))
    quadrillage(page, largeur, hauteur, 54, theme["grille"])

    x = lettrage(page, fiche["entete"].upper(), "etiquette", corps["entete"],
                 marge, m["y_entete"], theme["doux"])
    page.draw_rect(fitz.Rect(marge, m["y_entete"] + corps["entete"] + 16, x - 3,
                             m["y_entete"] + corps["entete"] + 20), color=None, fill=couleur(ORANGE))

    y = m["y_bloc"]
    if fiche["genre"] == "chiffre":
        ecrire(page, fiche["chiffre"], "titre", corps["gros"], marge, y, ORANGE)
        if fiche["unite"]:
            xu = marge + mesurer(fiche["chiffre"], "titre", corps["gros"]) + 16
            ecrire(page, fiche["unite"], "pied", 38, xu, y + corps["gros"] * 0.42, theme["doux"])
        y += corps["gros"] * 1.28

    for ligne in m["lignes_titre"]:
        ecrire(page, ligne, "titre", corps["titre"], marge, y, theme["fort"])
        y += corps["titre"] * m["inter_titre"]

    if fiche["genre"] == "sommaire":
        y += 40
        colonne_l = (m["utile"] - 40) / 2
        for c, colonne in enumerate(fiche["colonnes"]):
            xc = marge + c * (colonne_l + 40)
            yc = y
            for item in colonne:
                page.draw_line(fitz.Point(xc, yc + corps["liste"] * 0.66),
                               fitz.Point(xc + 18, yc + corps["liste"] * 0.66),
                               color=couleur(ORANGE), width=3)
                ecrire(page, item, "phrase", corps["liste"], xc + 32, yc, theme["fort"])
                yc += corps["liste"] * m["inter_liste"]
        y = yc

    if fiche["genre"] == "liste":
        y += 30
        for item in fiche["items"]:
            page.draw_line(fitz.Point(marge + 2, y + corps["item"] * 0.62),
                           fitz.Point(marge + 26, y + corps["item"] * 0.62),
                           color=couleur(ORANGE), width=4)
            ecrire(page, item, "phrase", corps["item"], marge + 46, y, theme["fort"])
            y += corps["item"] * m["inter_item"]

    y += 30
    for ligne in m["lignes_phrase"]:
        ecrire(page, ligne, "phrase", corps["phrase"], marge, y, theme["doux"])
        y += corps["phrase"] * m["inter_phrase"]

    base = hauteur - m["marge_pied"] - 46
    picto(page, chemin_logo(theme["logo"]), marge, base, 46)
    ecrire(page, "BTP EXPERTISE", "pied", 27, marge + 64, base + 6, theme["fort"])
    adresse = "btpexpertise.fr"
    ecrire(page, adresse, "pied", 27, largeur - marge - mesurer(adresse, "pied", 27), base + 6, BLEU)


# ---------------------------------------------------------------------------

def produire(taille, suffixe, nom_recueil):
    planches = {p[0]: p for p in planche.PLANCHES}
    cartes = {c["cle"]: c for c in carte.CARTES + [carte.OUVERTURE]}

    recueil = fitz.open()
    for cle in ORDRE:
        if cle in planches:
            page_planche(recueil, *planches[cle], taille=taille)
        else:
            page_carte(recueil, cartes[cle], taille)

        seul = fitz.open()
        seul.insert_pdf(recueil, from_page=recueil.page_count - 1, to_page=recueil.page_count - 1)
        seul.save(os.path.join(SORTIE, "%s%s.pdf" % (cle, suffixe)), garbage=3, deflate=True)
        seul.close()

    chemin = os.path.join(SORTIE, nom_recueil)
    recueil.save(chemin, garbage=3, deflate=True)
    recueil.close()
    return chemin


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    os.makedirs(TEMPO, exist_ok=True)

    for taille, suffixe, recueil in (((1080, 1080), "-1080", "planches-carre.pdf"),
                                     ((1080, 1920), "-story", "planches-story.pdf")):
        chemin = produire(taille, suffixe, recueil)
        print("%-24s %5.0f Ko" % (os.path.basename(chemin), os.path.getsize(chemin) / 1024))

    for reste in os.listdir(TEMPO):
        os.remove(os.path.join(TEMPO, reste))
    os.rmdir(TEMPO)
    print("\n%d fichiers dans %s" % (len(os.listdir(SORTIE)), SORTIE))
