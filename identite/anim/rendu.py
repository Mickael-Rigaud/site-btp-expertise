# -*- coding: utf-8 -*-
"""Rendu image par image de l'animation "construction" du logo BTP Expertise.

Sert aussi de moteur commun : rendu-loupe.py importe d'ici le chargement des
calques, la pose sur le canvas et les courbes d'acceleration.

    python rendu.py planche   # 12 images cles, pour controler
    python rendu.py frames    # les PNG que ffmpeg assemble
    python rendu.py diff      # compare l'image finale au logo d'origine
"""
import numpy as np, json, os, sys
from PIL import Image, ImageDraw
import commun as C

ICI = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(ICI, "calques")
meta = json.load(open(os.path.join(D, "meta.json")))
CAL = {c["name"]: c for c in meta["calques"]}
IMG = {n: np.array(Image.open(os.path.join(D, n + ".png")).convert("RGBA")).astype(np.float32)
       for n in CAL}

W, H = C.VUE_W, C.VUE_H
CX, CY = C.CX + C.MARGE_X, C.CY + C.MARGE_Y
SOL = C.SOL + C.MARGE_Y
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
RAD = np.hypot(XX - CX, YY - CY)
ANG = (np.degrees(np.arctan2(YY - CY, XX - CX)) - 73.0) % 360.0


def bezier(x1, y1, x2, y2):
    def cx(t): return 3*x1*t*(1-t)**2 + 3*x2*t*t*(1-t) + t**3
    def cy(t): return 3*y1*t*(1-t)**2 + 3*y2*t*t*(1-t) + t**3
    def f(p):
        lo, hi = 0.0, 1.0
        for _ in range(28):
            m = (lo + hi) / 2
            if cx(m) < p: lo = m
            else: hi = m
        return cy((lo + hi) / 2)
    return f


EASE_M = bezier(.2, .9, .25, 1)      # les etages qui montent
EASE_P = bezier(.16, .85, .3, 1)     # les tours qui poussent
EASE_T = bezier(.55, .05, .25, 1)    # le trace du cercle
EASE_W = bezier(.3, .8, .2, 1)       # le balayage du nom
EASE_O = bezier(0, 0, .58, 1)        # sortie douce


def prog(t, delay, dur, ease):
    if t <= delay: return 0.0
    if t >= delay + dur: return 1.0
    return ease((t - delay) / dur)


def masque_polygone(points, sur=2):
    """Masque flottant (0..1) d'un polygone donne dans le repere du logo."""
    im = Image.new("L", (W * sur, H * sur), 0)
    ImageDraw.Draw(im).polygon(
        [((x + C.MARGE_X) * sur, (y + C.MARGE_Y) * sur) for x, y in points], fill=255)
    return np.array(im.resize((W, H), Image.LANCZOS), np.float32) / 255.0


M_HAUT = masque_polygone(C.MANCHE_HAUT)
M_BAS = masque_polygone(C.MANCHE_BAS)
# l'attache du manche sort du cercle : elle est hors de portee du trace, et se
# revele donc d'un coup quand celui-ci boucle
ATTACHE = np.hypot(XX - (1052 + C.MARGE_X), YY - (1030 + C.MARGE_Y)) <= 130


def pose(canvas, name, dx=0.0, dy=0.0, alpha=1.0, clip_sol=False, mask=None):
    """Compose un calque sur le canvas, decale de (dx,dy) dans le repere logo."""
    if alpha <= 0.003: return
    c = CAL[name]; src = IMG[name]
    x0 = int(round(c["x"] + dx + C.MARGE_X)); y0 = int(round(c["y"] + dy + C.MARGE_Y))
    h, w = src.shape[:2]
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    ww = min(w - sx0, W - dx0); hh = min(h - sy0, H - dy0)
    if ww <= 0 or hh <= 0: return
    s = src[sy0:sy0 + hh, sx0:sx0 + ww]
    a = s[:, :, 3:4] / 255.0 * alpha
    if clip_sol:
        a = a * (np.arange(dy0, dy0 + hh)[:, None, None] < SOL)
    if mask is not None:
        a = a * mask[dy0:dy0 + hh, dx0:dx0 + ww, None]
    d = canvas[dy0:dy0 + hh, dx0:dx0 + ww]
    d[:, :, :3] = s[:, :, :3] * a + d[:, :, :3] * (1 - a)
    d[:, :, 3:4] = a * 255 + d[:, :, 3:4] * (1 - a)


def pose_couleur(canvas, couleur, masque):
    """Aplat de couleur (le manche) sous un masque."""
    a = masque[:, :, None]
    canvas[:, :, :3] = np.array(couleur, np.float32) * a + canvas[:, :, :3] * (1 - a)
    canvas[:, :, 3:4] = np.maximum(canvas[:, :, 3:4], a * 255)


def reflet(canvas, t, depart, lx=0.0, ly=0.0, cycle=5.2):
    """L'eclat qui traverse le verre, en boucle."""
    c = (t - depart) % cycle
    if not (0 <= c <= 1.30): return
    q = EASE_T(c / 1.30)
    th = np.radians(-18.0)
    u = (XX - (CX + lx - 700 + q * 2400)) * np.cos(th) + (YY - CY - ly) * np.sin(th)
    g = np.clip(1 - np.abs(u) / 105.0, 0, 1) ** 1.5
    inten = (g * (np.hypot(XX - CX - lx, YY - CY - ly) <= C.R_VERRE) * 0.55)[:, :, None]
    canvas[:, :, :3] = 255 - (255 - canvas[:, :, :3]) * (1 - inten)


# --- scenario "construction" -------------------------------------------------
DUREE = 5.0
T_TRACE, D_TRACE = 1.05, 1.15
T_MANCHE, D_MANCHE = 2.15, 0.45
T_NOM, D_NOM = 2.55, 0.90
T_REFLET = 3.30


def frame(t, fond=(255, 255, 255, 255)):
    cv = np.zeros((H, W, 4), np.float32); cv[:, :, :] = fond
    # 1. les etages montent, du bas vers le haut
    for i in range(7):
        p = prog(t, 0.15 + (6 - i) * 0.085, 0.55, EASE_M)
        if p > 0: pose(cv, "esc%d" % i, -90 * (1 - p), 34 * (1 - p), min(1, p * 2.2), clip_sol=True)
    # 2. les tours poussent
    p = prog(t, .62, .95, EASE_P)
    if p > 0: pose(cv, "tour-cyan", 0, 880 * (1 - p), 1, clip_sol=True)
    p = prog(t, .86, .80, EASE_P)
    if p > 0: pose(cv, "tour-orange", 0, 430 * (1 - p), 1, clip_sol=True)
    # 3. le cercle se trace
    p = prog(t, T_TRACE, D_TRACE, EASE_T)
    if p > 0:
        m = ((ANG <= p * 360.0) & (RAD <= 540)).astype(np.float32)
        att = prog(t, T_TRACE + D_TRACE - 0.08, 0.08, EASE_O)
        if att > 0: m = np.maximum(m, ATTACHE * att)
        pose(cv, "anneau", mask=m)
    # 4. le manche descend
    p = prog(t, T_MANCHE, D_MANCHE, EASE_O)
    if p > 0:
        bas = 1042 + p * (1490 - 1042) + C.MARGE_Y
        avance = (YY <= bas).astype(np.float32)
        nom = prog(t, T_NOM, D_NOM, EASE_W)          # le nom reprend le haut du manche
        pose_couleur(cv, C.ENCRE, M_HAUT * avance * (XX > nom * C.LOGO_W + C.MARGE_X))
        pose_couleur(cv, C.ENCRE, M_BAS * avance)
    # 5. le nom se revele
    if prog(t, T_NOM, D_NOM, EASE_W) > 0:
        p = prog(t, T_NOM, D_NOM, EASE_W)
        pose(cv, "texte", mask=(XX <= p * C.LOGO_W + C.MARGE_X).astype(np.float32))
    reflet(cv, t, T_REFLET)
    return Image.fromarray(np.clip(cv, 0, 255).astype(np.uint8), "RGBA")


def planche(fabrique, ts, chemin_sortie):
    cw, ch = W // 3, H // 3
    pl = Image.new("RGB", (4 * cw, 3 * ch), (222, 227, 234))
    for i, t in enumerate(ts):
        pl.paste(fabrique(t).convert("RGB").resize((cw, ch), Image.LANCZOS),
                 ((i % 4) * cw, (i // 4) * ch))
    pl.save(chemin_sortie)


def controle_diff(fabrique, t):
    """L'image finale doit redonner le logo d'origine, manche prolonge mis a part."""
    a = np.array(fabrique(t).convert("RGB"), int)
    ref = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    ref.alpha_composite(Image.open(os.path.join(os.path.dirname(ICI), "logo-principal.png"))
                        .convert("RGBA"), (C.MARGE_X, C.MARGE_Y))
    d = np.abs(a - np.array(ref.convert("RGB"), int)).sum(axis=2)
    d = d * (M_BAS < 0.02)          # le prolongement du manche n'est pas dans le logo
    print("pixels differents > 30 :", int((d > 30).sum()), "/", W * H,
          " ecart max :", int(d.max()))


def sortir_frames(fabrique, duree, dossier, fps=30, largeur=1080):
    os.makedirs(dossier, exist_ok=True)
    haut = int(round(largeur * H / W / 2)) * 2
    for k in range(int(fps * duree)):
        fabrique(k / fps).convert("RGB").resize((largeur, haut), Image.LANCZOS)\
            .save(os.path.join(dossier, "f%04d.png" % k))
    print("frames ok", int(fps * duree), "%dx%d" % (largeur, haut))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "planche"
    if mode == "planche":
        planche(frame, [0.3, 0.7, 1.1, 1.4, 1.7, 2.0, 2.3, 2.5, 2.7, 3.0, 3.3, 4.0],
                os.path.join(ICI, "_planche-construction.png"))
        print("planche ok")
    elif mode == "diff":
        controle_diff(frame, DUREE)
    else:
        sortir_frames(frame, DUREE, os.path.join(ICI, "frames"))
