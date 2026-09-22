# -*- coding: utf-8 -*-
"""Les publications en PDF, pour reprise dans Canva.

Meme gabarit que posts.py — la mise en page vient de sa fonction
`geometrie()`, il n'y a donc qu'une seule source de verite — mais chaque
element reste un objet : la photo, le panneau bleu nuit, la pastille orange,
le logo, et surtout les textes, qui sont du vrai texte vectoriel.

    python reseaux-sociaux/posts_pdf.py

Produit, dans visuels/publications/pdf/ :
  <sujet>-1080.pdf / <sujet>-story.pdf   une page par sujet
  publications-carre.pdf                 les huit carres, un par page
  publications-story.pdf                 les huit stories

Canva ouvre un PDF multipage comme un document a plusieurs pages : le fichier
groupe est le plus pratique pour tout reprendre d'un coup.
"""

import os
import sys

import fitz  # PyMuPDF

DOSSIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DOSSIER)

from visuels import NUIT, BLEU, ORANGE, BLANC, couvrir, image  # noqa: E402
from posts import PUBLICATIONS, DOUX, MARQUE, ADRESSE, geometrie  # noqa: E402
from couverture_pdf import couleur  # noqa: E402

SORTIE = os.path.join(DOSSIER, "visuels", "publications", "pdf")
TEMPO = os.path.join(DOSSIER, "visuels", "publications", "_tempo")

FICHIERS = {
    "titre": "C:/Windows/Fonts/segoeuib.ttf",
    "phrase": "C:/Windows/Fonts/segoeui.ttf",
    "etiquette": "C:/Windows/Fonts/seguisb.ttf",
    "pied": "C:/Windows/Fonts/seguisb.ttf",
}
FONTES = {role: fitz.Font(fontfile=chemin) for role, chemin in FICHIERS.items()}


def mesurer(texte, role, corps):
    return FONTES[role].text_length(texte, fontsize=corps)


def ligne_de_base(y_haut, role, corps):
    """PIL pose le haut de la lettre, PDF pose la ligne de base."""
    return y_haut + FONTES[role].ascender * corps


def degrade_png(largeur, hauteur, chemin):
    """PyMuPDF ne trace pas de degrade : on lui donne une image transparente."""
    from PIL import Image
    masque = Image.linear_gradient("L").resize((largeur, hauteur))
    voile = Image.new("RGBA", (largeur, hauteur), NUIT + (255,))
    voile.putalpha(masque)
    voile.save(chemin)
    return chemin


def page_publication(document, cle, etiquette, titre, phrase, photo, taille):
    largeur, hauteur = taille
    g = geometrie(taille, titre, phrase, etiquette, mesurer)
    marge = g["marge"]

    page = document.new_page(width=largeur, height=hauteur)

    fond = couvrir(image(photo), largeur, hauteur).convert("RGB")
    jpg = os.path.join(TEMPO, "%s-%d.jpg" % (cle, hauteur))
    fond.save(jpg, "JPEG", quality=88)
    page.insert_image(fitz.Rect(0, 0, largeur, hauteur), filename=jpg)

    voile = degrade_png(largeur, g["degrade_h"], os.path.join(TEMPO, "degrade-%d.png" % largeur))
    page.insert_image(
        fitz.Rect(0, g["haut_panneau"] - g["degrade_h"], largeur, g["haut_panneau"]),
        filename=voile)
    page.draw_rect(fitz.Rect(0, g["haut_panneau"], largeur, hauteur),
                   color=None, fill=couleur(NUIT))

    # Pastille du sujet
    x0, y0, x1, y1 = g["pilule"]
    page.draw_rect(fitz.Rect(x0, y0, x1, y1), color=None, fill=couleur(ORANGE), radius=0.5)

    plume = fitz.TextWriter(page.rect)
    corps = g["corps"]["etiquette"]
    x = marge + 22
    base = ligne_de_base(marge + 11, "etiquette", corps)
    for lettre in g["etiquette"]:
        plume.append(fitz.Point(x, base), lettre, font=FONTES["etiquette"], fontsize=corps)
        x += mesurer(lettre, "etiquette", corps) + g["ecart_etiquette"]
    plume.write_text(page, color=couleur(NUIT))

    # Titre
    plume = fitz.TextWriter(page.rect)
    corps = g["corps"]["titre"]
    y = g["y_titre"]
    for ligne in g["lignes_titre"]:
        plume.append(fitz.Point(marge, ligne_de_base(y, "titre", corps)), ligne,
                     font=FONTES["titre"], fontsize=corps)
        y += corps * g["inter_titre"]
    plume.write_text(page, color=couleur(BLANC))

    # Phrase
    plume = fitz.TextWriter(page.rect)
    corps = g["corps"]["phrase"]
    y = g["y_phrase"]
    for ligne in g["lignes_phrase"]:
        plume.append(fitz.Point(marge, ligne_de_base(y, "phrase", corps)), ligne,
                     font=FONTES["phrase"], fontsize=corps)
        y += corps * g["inter_phrase"]
    plume.write_text(page, color=couleur(DOUX))

    # Pied de marque
    picto = os.path.join(os.path.dirname(DOSSIER), "identite", "logo-compact-fond-sombre.png")
    pied_h = g["pied_h"]
    page.insert_image(
        fitz.Rect(marge, g["base_pied"], marge + pied_h, g["base_pied"] + pied_h),
        filename=picto, keep_proportion=True)

    corps = g["corps"]["pied"]
    base = ligne_de_base(g["base_pied"] + 6, "pied", corps)
    plume = fitz.TextWriter(page.rect)
    plume.append(fitz.Point(marge + pied_h + 18, base), MARQUE, font=FONTES["pied"], fontsize=corps)
    plume.write_text(page, color=couleur(BLANC))

    plume = fitz.TextWriter(page.rect)
    plume.append(fitz.Point(largeur - marge - mesurer(ADRESSE, "pied", corps), base),
                 ADRESSE, font=FONTES["pied"], fontsize=corps)
    plume.write_text(page, color=couleur(BLEU))


def produire(taille, suffixe, nom_groupe):
    groupe = fitz.open()
    for cle, etiquette, titre, phrase, photo in PUBLICATIONS:
        page_publication(groupe, cle, etiquette, titre, phrase, photo, taille)

        seul = fitz.open()
        seul.insert_pdf(groupe, from_page=groupe.page_count - 1, to_page=groupe.page_count - 1)
        seul.save(os.path.join(SORTIE, "%s%s.pdf" % (cle, suffixe)), garbage=3, deflate=True)
        seul.close()

    chemin = os.path.join(SORTIE, nom_groupe)
    groupe.save(chemin, garbage=3, deflate=True)
    groupe.close()
    return chemin


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    os.makedirs(TEMPO, exist_ok=True)

    for taille, suffixe, groupe in (((1080, 1080), "-1080", "publications-carre.pdf"),
                                    ((1080, 1920), "-story", "publications-story.pdf")):
        chemin = produire(taille, suffixe, groupe)
        print("%-26s %5.0f Ko" % (os.path.basename(chemin), os.path.getsize(chemin) / 1024))

    for reste in os.listdir(TEMPO):
        os.remove(os.path.join(TEMPO, reste))
    os.rmdir(TEMPO)
    print("\n%d fichiers dans %s" % (len(os.listdir(SORTIE)), SORTIE))
