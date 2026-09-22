# -*- coding: utf-8 -*-
"""Decoupe logo-principal.png en calques animables, dans calques/.

Le logo n'a que trois couleurs pleines sur fond transparent, ce qui permet de
separer chaque element sans le redessiner :
  - bleu nuit  (38,44,66)  : l'anneau de la loupe, le manche, le texte
  - orange     (255,138,0) : l'immeuble en escalier (gauche) et la tour (droite)
  - cyan       (0,186,245) : la tour vitree centrale

Le manche de la loupe passe par-dessus le R de EXPERTISE et les deux sont soudes :
on ne cherche pas a les separer, on coupe simplement a la ligne y=1046 (juste
au-dessus des lettres). Le bas du manche part donc avec le texte, et se revele
avec lui au balayage.

logo-fond-sombre.png est le meme fichier au pixel pres, bleu nuit remplace par
blanc : on en tire les deux memes calques pour la version fond sombre.
"""
import numpy as np, json, os
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
IDENTITE = os.path.dirname(ICI)
OUT = os.path.join(ICI, "calques")
os.makedirs(OUT, exist_ok=True)

COUPE = 1046  # ligne qui separe le picto du texte


def charge(nom):
    return np.array(Image.open(os.path.join(IDENTITE, nom)).convert("RGBA"))


def classe(a, couleurs):
    """Attribue chaque pixel opaque a la couleur la plus proche.

    Un simple seuil laisserait de cote les pixels de transition entre deux
    couleurs (le bord ou un batiment touche l'anneau) : ils n'iraient dans aucun
    calque et laisseraient un cheveu blanc a la recomposition.
    """
    d = np.stack([np.abs(a[:, :, :3].astype(int) - np.array(c)).sum(axis=2) for c in couleurs])
    gagnant = d.argmin(axis=0)
    opaque = a[:, :, 3] > 15
    return [opaque & (gagnant == i) for i in range(len(couleurs))]


a = charge("logo-principal.png")
H, W = a.shape[:2]
ys, xs = np.mgrid[0:H, 0:W]
bleu, orange, cyan = classe(a, [(38, 44, 66), (255, 138, 0), (0, 186, 245)])

parts = {
    "anneau": bleu & (ys < COUPE),
    "texte": bleu & (ys >= COUPE),
    "tour-cyan": cyan,
    "tour-orange": orange & (xs >= 850),
}
# les sept niveaux de l'immeuble en escalier, du haut vers le bas
for i, (y0, y1) in enumerate([(438, 504), (505, 571), (572, 638), (639, 706),
                              (707, 773), (774, 840), (841, 10000)]):
    parts["esc%d" % i] = orange & (xs < 850) & (ys >= y0) & (ys <= y1)

meta = {"W": W, "H": H, "calques": []}
for nom, m in parts.items():
    yy, xx = np.nonzero(m)
    x0, x1, y0, y1 = int(xx.min()), int(xx.max()), int(yy.min()), int(yy.max())
    out = a.copy(); out[~m] = 0
    Image.fromarray(out[y0:y1 + 1, x0:x1 + 1]).save(os.path.join(OUT, nom + ".png"), optimize=True)
    meta["calques"].append(dict(name=nom, x=x0, y=y0, w=x1 - x0 + 1, h=y1 - y0 + 1))

# version fond sombre : memes cadres, bleu nuit remplace par blanc
b = charge("logo-fond-sombre.png")
blanc = classe(b, [(255, 255, 255), (255, 138, 0), (0, 186, 245)])[0]
cadres = {c["name"]: c for c in meta["calques"]}
for nom, m in [("anneau-b", blanc & (ys < COUPE)), ("texte-b", blanc & (ys >= COUPE))]:
    r = cadres[nom[:-2]]
    out = b.copy(); out[~m] = 0
    Image.fromarray(out[r["y"]:r["y"] + r["h"], r["x"]:r["x"] + r["w"]]).save(
        os.path.join(OUT, nom + ".png"), optimize=True)
    meta["calques"].append(dict(name=nom, x=r["x"], y=r["y"], w=r["w"], h=r["h"]))

json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
for c in meta["calques"]:
    print("%-12s x%4d y%4d %4dx%4d %5d ko" % (
        c["name"], c["x"], c["y"], c["w"], c["h"],
        os.path.getsize(os.path.join(OUT, c["name"] + ".png")) / 1024))
