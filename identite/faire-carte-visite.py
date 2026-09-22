"""Construit la carte de visite : HTML autonome + les deux PDF.

    python faire-carte-visite.py

Produit, dans ce dossier :
  carte-visite.html                          page autonome (logos en data URI)
  Carte-BTP-Expertise-canva-85x55.pdf        format fini, a importer dans Canva
  Carte-BTP-Expertise-imprimeur-91x61.pdf    avec 3 mm de fond perdu

Le texte et la mise en page se modifient dans carte-visite.src.html, ou les
logos passent par les marqueurs __LOGO_CLAIR__ / __LOGO_SOMBRE__.

Chrome imprime une page blanche apres chaque face : on ne garde que les pages
qui portent du texte, puis on assemble recto + verso en un seul PDF.
"""

import base64
import io
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).parent
SOURCE = ICI / "carte-visite.src.html"
PAGE = ICI / "carte-visite.html"

LOGOS = {
    "__LOGO_CLAIR__": "logo-principal.png",
    "__LOGO_SOMBRE__": "logo-fond-sombre.png",
}
LARGEUR_LOGO = 900  # px : largement suffisant pour 17 mm d'impression

SORTIES = {
    # suffixe d'URL -> nom du PDF
    "": "Carte-BTP-Expertise-imprimeur-91x61.pdf",
    "bleed=0": "Carte-BTP-Expertise-canva-85x55.pdf",
}

CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def logo_data_uri(nom: str) -> str:
    from PIL import Image

    image = Image.open(ICI / nom)
    hauteur = round(image.height * LARGEUR_LOGO / image.width)
    image = image.resize((LARGEUR_LOGO, hauteur), Image.LANCZOS)
    tampon = io.BytesIO()
    image.save(tampon, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(tampon.getvalue()).decode()


def construire_page() -> None:
    html = SOURCE.read_text(encoding="utf-8")
    for marqueur, fichier in LOGOS.items():
        html = html.replace(marqueur, logo_data_uri(fichier))
    PAGE.write_text(html, encoding="utf-8")
    print(f"{PAGE.name} : {len(html) // 1024} Ko")


def chrome() -> str:
    for chemin in CHROME:
        if Path(chemin).exists():
            return chemin
    sys.exit("Chrome introuvable : les PDF ne peuvent pas etre generes.")


def construire_pdf() -> None:
    from pypdf import PdfReader, PdfWriter

    navigateur = chrome()
    base = PAGE.as_uri()
    temporaires = []

    for parametres, nom_pdf in SORTIES.items():
        ecrivain = PdfWriter()
        for face in ("recto", "verso"):
            requete = "&".join(filter(None, [parametres, f"face={face}"]))
            temporaire = ICI / f"_{face}.pdf"
            temporaires.append(temporaire)
            subprocess.run(
                [
                    navigateur,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-pdf-header-footer",
                    "--virtual-time-budget=15000",
                    f"--print-to-pdf={temporaire}",
                    f"{base}?{requete}",
                ],
                check=True,
                capture_output=True,
            )
            for page in PdfReader(temporaire).pages:
                if page.extract_text().strip():  # ecarte la page blanche
                    ecrivain.add_page(page)
        with open(ICI / nom_pdf, "wb") as fichier:
            ecrivain.write(fichier)
        pages = PdfReader(ICI / nom_pdf).pages
        format_mm = [
            f"{round(float(p.mediabox.width) * 25.4 / 72)} x "
            f"{round(float(p.mediabox.height) * 25.4 / 72)} mm"
            for p in pages
        ]
        print(f"{nom_pdf} : {len(pages)} pages, {format_mm[0]}")

    for temporaire in temporaires:
        temporaire.unlink(missing_ok=True)


if __name__ == "__main__":
    construire_page()
    construire_pdf()
