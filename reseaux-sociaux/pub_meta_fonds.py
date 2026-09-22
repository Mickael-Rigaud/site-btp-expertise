# -*- coding: utf-8 -*-
"""Les fonds seuls, sans un mot de texte — pour composer ailleurs.

    python reseaux-sociaux/pub_meta_fonds.py

Sort dans visuels/pub-meta/fonds/ la photo de chaque annonce, recadree au
format, avec le voile bleu nuit et les degrades de marque : l'image telle
qu'elle est sous le texte, prete a recevoir un titre pose dans Canva.

Deux versions par format :
  <annonce>-<format>-fond.jpg    avec le voile et les degrades
  <annonce>-<format>-photo.jpg   la photo seule, juste recadree

Le degrade du bas est ce qui rend un titre blanc lisible sur une photo claire.
En composant ailleurs, garder le texte dans sa moitie basse.

Reperes de marque, pour retrouver les memes couleurs :
  bleu nuit  #262C42     titre en blanc  #FFFFFF
  cyan       #0BBBF6     texte doux      #CED6E7
  orange     #FF8A00     (bouton : texte bleu nuit sur aplat orange)
Le pictogramme est dans identite/picto-fond-sombre.png, le logo complet
dans identite/logo-fond-sombre.png — les deux en PNG transparent.
"""

import os
import sys

from PIL import Image

DOSSIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DOSSIER)

from visuels import NUIT  # noqa: E402
from pub_meta import ANNONCES, FORMATS, SORTIE, cadrer, degrade, mesures, photo  # noqa: E402

FONDS = os.path.join(SORTIE, "fonds")


def fonds(annonce, taille, suffixe):
    m = mesures(annonce, taille)
    nue = cadrer(photo(annonce["photo"]), taille[0], taille[1],
                 annonce.get("cadrage", 0.5)).convert("RGBA")

    chemins = []
    chemin = os.path.join(FONDS, "%s%s-photo.jpg" % (annonce["cle"], suffixe))
    nue.convert("RGB").save(chemin, "JPEG", quality=92, optimize=True)
    chemins.append(chemin)

    traite = Image.alpha_composite(nue, Image.new("RGBA", taille, NUIT + (46,)))
    traite = Image.alpha_composite(traite, degrade(taille, *m["degrade_bas"]))
    traite = Image.alpha_composite(traite, degrade(taille, *m["degrade_haut"],
                                                   maxi=150, sens="haut"))
    chemin = os.path.join(FONDS, "%s%s-fond.jpg" % (annonce["cle"], suffixe))
    traite.convert("RGB").save(chemin, "JPEG", quality=92, optimize=True)
    chemins.append(chemin)
    return chemins


if __name__ == "__main__":
    os.makedirs(FONDS, exist_ok=True)
    for annonce in ANNONCES:
        for taille, suffixe in FORMATS:
            fonds(annonce, taille, suffixe)
        print("%-26s fond + photo en 4x5, 1x1, 9x16" % annonce["cle"])
    print("\n%d fichiers dans %s" % (len(os.listdir(FONDS)), FONDS))
