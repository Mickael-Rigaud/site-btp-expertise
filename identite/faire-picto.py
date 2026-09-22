# -*- coding: utf-8 -*-
"""Repare le pictogramme : `logo-compact*.png` a son cercle rogne.

Dans les deux PNG compacts livres a l'origine, la loupe touche le bord droit
et le bord bas de l'image : partout ou on les pose, le cercle apparait aplati
d'un cote et le manche coupe. Le defaut se voit des que le logo depasse une
trentaine de pixels — sur une publicite, il saute aux yeux.

Le logo complet, lui, est intact. On y decoupe donc le pictogramme, juste
au-dessus de la ligne de texte, et on lui rend une marge transparente.

    python identite/faire-picto.py

Produit `picto.png` (a poser sur fond clair) et `picto-fond-sombre.png`.
Les scripts des reseaux sociaux utilisent ceux-la ; les anciens compacts
restent en place pour les supports deja imprimes.
"""

import os

from PIL import Image

DOSSIER = os.path.dirname(os.path.abspath(__file__))

# Mesuree sur le canal alpha de logo-fond-sombre.png (1600 x 1303) :
# le cercle occupe x 348-1379 et y 8-1040, la ligne de texte commence a 1050.
# On coupe juste avant elle : le cercle est entier, le manche amorce.
DECOUPE = (335, 0, 1395, 1048)
MARGE = 26  # respiration transparente, sinon le trait blanc touche le bord


def picto(source, destination):
    image = Image.open(os.path.join(DOSSIER, source)).convert("RGBA")
    coupe = image.crop(DECOUPE)
    toile = Image.new("RGBA", (coupe.width + 2 * MARGE, coupe.height + 2 * MARGE), (0, 0, 0, 0))
    toile.alpha_composite(coupe, (MARGE, MARGE))
    toile.save(os.path.join(DOSSIER, destination))
    return toile.size


if __name__ == "__main__":
    for source, destination in (("logo-principal.png", "picto.png"),
                                ("logo-fond-sombre.png", "picto-fond-sombre.png")):
        print("%-28s -> %-24s %s" % (source, destination, picto(source, destination)))
