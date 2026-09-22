# -*- coding: utf-8 -*-
"""Rendu des animations ou la loupe grossit les batiments qui sont derriere.

Les batiments sont poses a 72 % de leur taille ; le verre grossit x1,39 ce qui
passe dessous. Quand la loupe se cale au centre, les deux facteurs s'annulent et
l'image redonne exactement le logo.

    python rendu-loupe.py <scenario> planche|frames|diff

Scenarios : balayage (defaut), inspection, mise-au-point.
"""
import numpy as np, os, sys
from PIL import Image
import rendu as base
import commun as C

W, H = base.W, base.H
CX, CY = base.CX, base.CY
XX, YY = base.XX, base.YY
EASE_TRAJET = base.bezier(.45, .05, .3, 1)
EASE_ZOOM = base.bezier(.4, 0, .2, 1.08)

SCENARIOS = {
    # la loupe entre par la gauche, balaie les facades, depasse puis se cale
    "balayage": dict(
        duree=5.0, trace=None,
        trajet=[(0, -380, -70), (.42, -130, 34), (.72, 96, -28), (1, 0, 0)],
        t_trajet=0.40, d_trajet=1.95,
        zoom=None, manche=None, nom=(2.35, .9), t_reflet=2.90),

    # elle s'arrete sur chaque batiment, comme on releve un point a la fois
    "inspection": dict(
        duree=6.0, trace=None,
        trajet=[(0, -440, -40),
                (.16, -215, 100), (.28, -215, 100),     # l'immeuble en escalier
                (.44, -20, -70), (.56, -20, -70),       # la tour vitree
                (.72, 185, 85), (.84, 185, 85),         # l'immeuble de droite
                (1, 0, 0)],
        t_trajet=0.35, d_trajet=3.00,
        zoom=None, manche=None, nom=(3.45, .9), t_reflet=4.00),

    # la loupe est posee, et c'est le grossissement qui monte : la mise au point
    "mise-au-point": dict(
        duree=5.2, trace=(0.85, 1.05),
        trajet=[(0, 0, 0), (1, 0, 0)], t_trajet=0.0, d_trajet=0.1,
        zoom=[(0, 1.0), (.78, 1.06), (1, 1.0)], t_zoom=2.00, d_zoom=0.85,
        manche=(1.95, .45), nom=(2.85, .9), t_reflet=3.60),
}


def etape(pts, p, ease):
    """Interpole une liste (pourcentage, valeurs...) comme le ferait le CSS :
    la courbe d'acceleration joue entre chaque paire de reperes."""
    for a, b in zip(pts, pts[1:]):
        if p <= b[0] or b[0] >= 1.0:
            q = ease(0 if b[0] == a[0] else min(1, max(0, (p - a[0]) / (b[0] - a[0]))))
            return [x + (y - x) * q for x, y in zip(a[1:], b[1:])]
    return list(pts[-1][1:])


def redimensionne(rgb, echelle, dx, dy):
    """L'image, mise a l'echelle autour du centre du verre, puis decalee."""
    if abs(echelle - 1) < 1e-4:
        src = rgb
        ox, oy = 0, 0
    else:
        w, h = int(round(W * echelle)), int(round(H * echelle))
        src = np.array(Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")
                       .resize((w, h), Image.LANCZOS), np.float32)
        ox, oy = CX * (1 - echelle), CY * (1 - echelle)
    out = np.zeros((H, W, 3), np.float32); out[:, :, :] = rgb[0, 0]
    x0, y0 = int(round(ox + dx)), int(round(oy + dy))
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    ww = min(src.shape[1] - sx0, W - dx0); hh = min(src.shape[0] - sy0, H - dy0)
    if ww > 0 and hh > 0:
        out[dy0:dy0 + hh, dx0:dx0 + ww] = src[sy0:sy0 + hh, sx0:sx0 + ww]
    return out


def fabrique(nom_scenario):
    S = SCENARIOS[nom_scenario]

    def ville(t, fond):
        """Les batiments a l'echelle 1, sur un canvas deja teinte du fond : sans
        cela les pixels a demi couverts seraient melanges avec du noir."""
        cv = np.zeros((H, W, 4), np.float32); cv[:, :, :3] = np.array(fond[:3], np.float32)
        for i in range(7):
            p = base.prog(t, 0.10 + (6 - i) * 0.075, 0.5, base.EASE_M)
            if p > 0:
                base.pose(cv, "esc%d" % i, -90 * (1 - p), 34 * (1 - p),
                          min(1, p * 2.2), clip_sol=True)
        p = base.prog(t, .45, .9, base.EASE_P)
        if p > 0: base.pose(cv, "tour-cyan", 0, 880 * (1 - p), 1, clip_sol=True)
        p = base.prog(t, .62, .75, base.EASE_P)
        if p > 0: base.pose(cv, "tour-orange", 0, 430 * (1 - p), 1, clip_sol=True)
        return cv

    def frame(t, fond=(255, 255, 255, 255)):
        cv = np.zeros((H, W, 4), np.float32); cv[:, :, :] = fond
        p = base.prog(t, S["t_trajet"], S["d_trajet"], lambda x: x)
        lx, ly = etape(S["trajet"], p, EASE_TRAJET)
        k = C.K
        if S.get("zoom"):
            q = base.prog(t, S["t_zoom"], S["d_zoom"], lambda x: x)
            k = 1 + (C.K - 1) * etape(S["zoom"], q, EASE_ZOOM)[0]
        v = ville(t, fond)[:, :, :3]
        dist = np.hypot(XX - CX - lx, YY - CY - ly)
        dehors = (dist > C.R_VERRE).astype(np.float32)[:, :, None]
        dedans = 1 - dehors

        # les batiments en petit, partout ou le verre ne passe pas
        petit = redimensionne(v, C.ECH, 0, 0)
        cv[:, :, :3] = petit * dehors + cv[:, :, :3] * (1 - dehors)
        # sous le verre : les memes, grossis, cales sur le centre du verre
        gros = redimensionne(v, C.ECH * k, (1 - k) * lx, (1 - k) * ly)
        cv[:, :, :3] = gros * dedans + cv[:, :, :3] * (1 - dedans)

        base.reflet(cv, t, S["t_reflet"], lx, ly)

        # la loupe : anneau, puis le manche qui la prolonge
        if S["trace"]:
            pr = base.prog(t, S["trace"][0], S["trace"][1], base.EASE_T)
            if pr > 0:
                m = ((base.ANG <= pr * 360.0) & (base.RAD <= 540)).astype(np.float32)
                att = base.prog(t, S["trace"][0] + S["trace"][1] - .08, .08, base.EASE_O)
                if att > 0: m = np.maximum(m, base.ATTACHE * att)
                base.pose(cv, "anneau", mask=m)
        else:
            base.pose(cv, "anneau", lx, ly)

        nom = base.prog(t, S["nom"][0], S["nom"][1], base.EASE_W)
        visible = 1.0
        if S["manche"]:
            visible = base.prog(t, S["manche"][0], S["manche"][1], base.EASE_O)
        if visible > 0:
            dec = lambda m: np.roll(np.roll(m, int(round(ly)), 0), int(round(lx)), 1)
            avance = (YY <= 1042 + visible * (1490 - 1042) + C.MARGE_Y + ly).astype(np.float32)
            base.pose_couleur(cv, C.ENCRE,
                              dec(base.M_HAUT) * avance * (XX > nom * C.LOGO_W + C.MARGE_X))
            base.pose_couleur(cv, C.ENCRE, dec(base.M_BAS) * avance)

        if nom > 0:
            base.pose(cv, "texte", mask=(XX <= nom * C.LOGO_W + C.MARGE_X).astype(np.float32))
        return Image.fromarray(np.clip(cv, 0, 255).astype(np.uint8), "RGBA")

    return frame, S


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    nom = args[0] if args and args[0] in SCENARIOS else "balayage"
    mode = args[-1] if args and args[-1] in ("planche", "frames", "diff") else "planche"
    frame, S = fabrique(nom)
    ICI = os.path.dirname(os.path.abspath(__file__))
    if mode == "planche":
        d = S["duree"]
        base.planche(frame, [d * i / 12.0 for i in range(1, 13)],
                     os.path.join(ICI, "_planche-%s.png" % nom))
        print("planche ok", nom)
    elif mode == "diff":
        base.controle_diff(frame, S["duree"])
    else:
        base.sortir_frames(frame, S["duree"], os.path.join(ICI, "frames-" + nom))
