"""Construit le flyer A5 recto-verso : page HTML autonome + les deux PDF.

    python faire-flyer.py

Produit, dans ce dossier :
  flyer.html                               page autonome (images en data URI)
  Flyer-BTP-Expertise-A5.pdf               format fini, a importer dans Canva
  Flyer-BTP-Expertise-A5-fond-perdu.pdf    154 x 216 mm pour l'imprimeur

Chaque PDF fait deux pages : le recto, puis le verso.

Les textes se modifient dans flyer.src.html. Le QR code est genere ici meme a
partir de SITE : changer l'adresse suffit, il n'y a pas d'image a remplacer.
"""

import base64
import io
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).parent
PROJET = ICI.parent
SOURCE = ICI / "flyer.src.html"
PAGE = ICI / "flyer.html"

LOGO_SOMBRE = ICI / "logo-fond-sombre.png"   # pour les fonds bleu nuit
LOGO_CLAIR = ICI / "logo-principal.png"      # pour les fonds clairs
PHOTO = PROJET / "site/assets/img/exp-reunion.webp"   # photo du medaillon

SITE = "https://btpexpertise.fr"             # cible du QR code
QR_ENCRE = "#262C42"                         # marine, jamais l'inverse

FACES = ("fr", "fv")                         # recto puis verso
FORMATS = {"bleed=0": "", "": "-fond-perdu"}

CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def encoder(tampon: io.BytesIO, type_mime: str) -> str:
    return f"data:{type_mime};base64," + base64.b64encode(tampon.getvalue()).decode()


def logo_data_uri(chemin: Path) -> str:
    from PIL import Image

    image = Image.open(chemin)
    image = image.resize((900, round(image.height * 900 / image.width)), Image.LANCZOS)
    tampon = io.BytesIO()
    image.save(tampon, "PNG", optimize=True)
    return encoder(tampon, "image/png")


def qr_data_uri() -> str:
    """QR du site, en PNG large : imprime a 27 mm, il faut tenir les 300 dpi."""
    import segno

    code = segno.make(SITE, error="m")
    tampon = io.BytesIO()
    # 25 modules + 2 de marge blanche, x 16 px = 464 px pour 27 mm, soit ~435 dpi
    code.save(tampon, kind="png", scale=16, border=2, dark=QR_ENCRE, light="#FFFFFF")
    return encoder(tampon, "image/png")


def photo_data_uri() -> str:
    """Photo du medaillon : carree, en couleur, coupee au centre."""
    from PIL import Image

    image = Image.open(PHOTO).convert("RGB")
    cote = min(image.size)
    gauche = (image.width - cote) // 2
    haut = (image.height - cote) // 2
    image = image.crop((gauche, haut, gauche + cote, haut + cote))
    image = image.resize((900, 900), Image.LANCZOS)
    tampon = io.BytesIO()
    image.save(tampon, "JPEG", quality=88, optimize=True)
    return encoder(tampon, "image/jpeg")


def construire_page() -> None:
    for fichier in (SOURCE, LOGO_SOMBRE, LOGO_CLAIR, PHOTO):
        if not fichier.exists():
            sys.exit(f"Fichier introuvable : {fichier}")
    html = SOURCE.read_text(encoding="utf-8")
    html = html.replace("__LOGO_SOMBRE__", logo_data_uri(LOGO_SOMBRE))
    html = html.replace("__LOGO_CLAIR__", logo_data_uri(LOGO_CLAIR))
    html = html.replace("__PHOTO__", photo_data_uri())
    html = html.replace("__QR__", qr_data_uri())
    PAGE.write_text(html, encoding="utf-8")
    print(f"{PAGE.name} : {len(html) // 1024} Ko  (QR vers {SITE})")


def chrome() -> str:
    for chemin in CHROME:
        if Path(chemin).exists():
            return chemin
    sys.exit("Chrome introuvable : les PDF ne peuvent pas etre generes.")


def construire_pdf() -> None:
    from pypdf import PdfReader, PdfWriter

    navigateur = chrome()
    temporaire = ICI / "_page.pdf"

    for parametres, suffixe in FORMATS.items():
        ecrivain = PdfWriter()
        for face in FACES:
            requete = "&".join(filter(None, [parametres, f"p={face}"]))
            subprocess.run(
                [
                    navigateur,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-pdf-header-footer",
                    "--virtual-time-budget=20000",
                    f"--print-to-pdf={temporaire}",
                    f"{PAGE.as_uri()}?{requete}",
                ],
                check=True,
                capture_output=True,
            )
            for page in PdfReader(temporaire).pages:
                if page.extract_text().strip():  # ecarte la page blanche de Chrome
                    ecrivain.add_page(page)
        fichier = ICI / f"Flyer-BTP-Expertise-A5{suffixe}.pdf"
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
