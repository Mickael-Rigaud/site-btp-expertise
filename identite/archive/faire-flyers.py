"""Construit les trois flyers A5 : page HTML autonome + les PDF.

    python faire-flyers.py

Produit, dans ce dossier :
  flyers.html                              page autonome (images en data URI)
  Flyer-1-Desordres-A5.pdf                 format fini, a importer dans Canva
  Flyer-1-Desordres-A5-fond-perdu.pdf      154 x 216 mm pour l'imprimeur
  ... idem pour les flyers 2 et 3

Les textes se modifient dans flyers.src.html. Les images y sont des marqueurs
(__LOGO_SOMBRE__, __IMG_FISSURES__...) remplaces ici par des data URI.

Chrome imprime parfois une page blanche apres la page utile : on ne garde que
les pages qui portent du texte, puis on assemble recto + verso.
"""

import base64
import io
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).parent
PROJET = ICI.parent
SOURCE = ICI / "flyers.src.html"
PAGE = ICI / "flyers.html"

# marqueur -> (fichier, largeur cible en px, qualite JPEG ou None pour du PNG)
IMAGES = {
    "__LOGO_SOMBRE__": (ICI / "logo-fond-sombre.png", 900, None),
    "__IMG_FISSURES__": (PROJET / "reserve-images/moe-fissures.webp", 1408, 86),
    "__IMG_ACHAT__": (PROJET / "site/assets/img/exp-avant-achat.webp", 1200, 86),
    "__IMG_CHANTIER__": (PROJET / "reserve-images/moe-renovation-chantier.webp", 1408, 86),
}

FLYERS = {
    "Flyer-1-Desordres": ("f1r", "f1v"),
    "Flyer-2-Avant-achat": ("f2r", "f2v"),
    "Flyer-3-AMO": ("f3r", "f3v"),
}

CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def data_uri(chemin: Path, largeur: int, qualite: int | None) -> str:
    from PIL import Image

    image = Image.open(chemin)
    if image.width > largeur:
        hauteur = round(image.height * largeur / image.width)
        image = image.resize((largeur, hauteur), Image.LANCZOS)
    tampon = io.BytesIO()
    if qualite is None:
        image.save(tampon, "PNG", optimize=True)
        type_mime = "image/png"
    else:
        image.convert("RGB").save(tampon, "JPEG", quality=qualite, optimize=True)
        type_mime = "image/jpeg"
    return f"data:{type_mime};base64," + base64.b64encode(tampon.getvalue()).decode()


def construire_page() -> None:
    html = SOURCE.read_text(encoding="utf-8")
    for marqueur, (chemin, largeur, qualite) in IMAGES.items():
        if not chemin.exists():
            sys.exit(f"Image introuvable : {chemin}")
        html = html.replace(marqueur, data_uri(chemin, largeur, qualite))
    PAGE.write_text(html, encoding="utf-8")
    print(f"{PAGE.name} : {len(html) // 1024} Ko")


def chrome() -> str:
    for chemin in CHROME:
        if Path(chemin).exists():
            return chemin
    sys.exit("Chrome introuvable : les PDF ne peuvent pas etre generes.")


def imprimer(navigateur: str, requete: str, sortie: Path) -> None:
    subprocess.run(
        [
            navigateur,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--virtual-time-budget=20000",
            f"--print-to-pdf={sortie}",
            f"{PAGE.as_uri()}?{requete}",
        ],
        check=True,
        capture_output=True,
    )


def construire_pdf() -> None:
    from pypdf import PdfReader, PdfWriter

    navigateur = chrome()
    temporaire = ICI / "_page.pdf"

    for nom, faces in FLYERS.items():
        for suffixe, parametres in (("", "bleed=0"), ("-fond-perdu", "")):
            ecrivain = PdfWriter()
            for face in faces:
                requete = "&".join(filter(None, [parametres, f"p={face}"]))
                imprimer(navigateur, requete, temporaire)
                for page in PdfReader(temporaire).pages:
                    if page.extract_text().strip():  # ecarte la page blanche
                        ecrivain.add_page(page)
            fichier = ICI / f"{nom}-A5{suffixe}.pdf"
            with open(fichier, "wb") as sortie:
                ecrivain.write(sortie)
            pages = PdfReader(fichier).pages
            taille = pages[0].mediabox
            print(
                f"{fichier.name} : {len(pages)} pages, "
                f"{round(float(taille.width) * 25.4 / 72)} x "
                f"{round(float(taille.height) * 25.4 / 72)} mm"
            )

    temporaire.unlink(missing_ok=True)


if __name__ == "__main__":
    construire_page()
    construire_pdf()
