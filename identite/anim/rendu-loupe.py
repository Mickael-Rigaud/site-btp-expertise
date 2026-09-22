# -*- coding: utf-8 -*-
"""Rendu image par image de la variante "loupe" (logo-anime-loupe.svg).

Meme principe que rendu.py : la choregraphie est celle du SVG, rejouee ici en
numpy pour sortir des PNG que ffmpeg assemble en MP4 et en GIF.
"""
import numpy as np, os, sys
from PIL import Image
import rendu as base

W, H = base.W, base.H
CX, CY = base.CX, base.CY
R_VERRE = 505
ECH, SOL = 0.72, base.SOL
K = 1 / ECH
TRAJET = [(0.0, -520, -80), (0.42, -130, 34), (0.72, 96, -28), (1.0, 0, 0)]
DUR, DEL = 1.95, 0.40
EASE = base.bezier(.45, .05, .3, 1)
EASE_M = base.bezier(.2, .9, .25, 1)
EASE_P = base.bezier(.16, .85, .3, 1)
EASE_W = base.bezier(.3, .8, .2, 1)

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def position(t):
    """Position de la loupe. Comme en CSS, l'easing joue sur chaque segment."""
    p = base.prog(t, DEL, DUR, lambda x: x)      # avancement lineaire 0..1
    for (p0, x0, y0), (p1, x1, y1) in zip(TRAJET, TRAJET[1:]):
        if p <= p1 or p1 == 1.0:
            q = EASE(0 if p1 == p0 else min(1, max(0, (p - p0) / (p1 - p0))))
            return x0 + (x1 - x0) * q, y0 + (y1 - y0) * q
    return 0.0, 0.0


def ville(t, fond=(255, 255, 255)):
    """Les batiments a l'echelle 1, a l'instant t, sur fond transparent.

    Les canaux de couleur portent deja la teinte du fond (avec alpha 0) : sans
    cela, les pixels a demi couverts seraient melanges avec du noir puis
    recomposes sur le fond, ce qui cerne chaque forme d'un liseré sombre."""
    cv = np.zeros((H, W, 4), np.float32)
    cv[:, :, :3] = np.array(fond, np.float32)
    for i in range(7):
        p = base.prog(t, 0.10 + (6 - i) * 0.075, 0.5, EASE_M)
        if p > 0:
            base.pose(cv, "esc%d" % i, -90 * (1 - p), 34 * (1 - p), min(1, p * 2.2), clip_sol=True)
    p = base.prog(t, .45, .9, EASE_P)
    if p > 0: base.pose(cv, "tour-cyan", 0, 880 * (1 - p), 1, clip_sol=True)
    p = base.prog(t, .62, .75, EASE_P)
    if p > 0: base.pose(cv, "tour-orange", 0, 430 * (1 - p), 1, clip_sol=True)
    return cv


def colle(dst, src, dx=0, dy=0, masque=None):
    """Recopie src (deja compose sur le fond) dans dst, decale, sous un masque.

    src porte la couleur du fond dans ses zones vides : on l'applique donc en
    opaque. Repasser par son alpha melangerait une deuxieme fois les pixels de
    bord avec le fond et delaverait chaque contour."""
    if dx or dy:
        src = np.roll(np.roll(src, int(round(dy)), 0), int(round(dx)), 1)
    a = np.ones((H, W, 1), np.float32) if masque is None else masque[:, :, None]
    dst[:, :, :3] = src[:, :, :3] * a + dst[:, :, :3] * (1 - a)
    dst[:, :, 3:4] = np.maximum(dst[:, :, 3:4], a * 255)


def frame(t, fond=(255, 255, 255, 255)):
    cv = np.zeros((H, W, 4), np.float32); cv[:, :, :] = fond
    lx, ly = position(t)
    v = ville(t, fond[:3])
    dist = np.hypot(XX - (CX + lx), YY - (CY + ly))

    # les batiments en petit, masques partout ou le verre passe
    # on reduit les couleurs seules : Pillow premultiplie l'alpha au
    # redimensionnement, ce qui noircirait toutes les zones transparentes
    petit = Image.fromarray(np.clip(v[:, :, :3], 0, 255).astype(np.uint8), "RGB").resize(
        (int(W * ECH), int(H * ECH)), Image.LANCZOS)
    fondv = np.zeros((H, W, 4), np.float32); fondv[:, :, :3] = np.array(fond[:3], np.float32)
    ox, oy = int(round(CX * (1 - ECH))), int(round(CY * (1 - ECH)))
    fondv[oy:oy + petit.height, ox:ox + petit.width, :3] = np.array(petit, np.float32)
    colle(cv, fondv, masque=(dist > R_VERRE).astype(np.float32))

    # sous le verre : les memes batiments a l'echelle 1, cales sur le centre du verre
    colle(cv, v, (1 - K) * lx, (1 - K) * ly, masque=(dist <= R_VERRE).astype(np.float32))

    # reflet sur le verre
    cyc = (t - 2.90) % 5.2
    if 0 <= cyc <= 1.30:
        q = base.EASE_T(cyc / 1.30)
        th = np.radians(-18.0)
        u = (XX - (lx - 700 + q * 2400)) * np.cos(th) + (YY - CY - ly) * np.sin(th)
        g = np.clip(1 - np.abs(u) / 105.0, 0, 1) ** 1.5
        inten = (g * (dist <= R_VERRE) * 0.55)[:, :, None]
        cv[:, :, :3] = 255 - (255 - cv[:, :, :3]) * (1 - inten)

    base.pose(cv, "anneau", lx, ly)

    p = base.prog(t, 2.35, .9, EASE_W)
    if p > 0:
        base.pose(cv, "texte", mask=(XX <= p * W).astype(np.float32))
    return Image.fromarray(np.clip(cv, 0, 255).astype(np.uint8), "RGBA")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "planche"
    ICI = os.path.dirname(os.path.abspath(__file__))
    if mode == "planche":
        ts = [0.3, 0.7, 1.0, 1.3, 1.6, 1.9, 2.2, 2.5, 2.8, 3.1, 3.4, 3.7]
        cw, ch = W // 3, H // 3
        pl = Image.new("RGB", (4 * cw, 3 * ch), (222, 227, 234))
        for i, t in enumerate(ts):
            pl.paste(frame(t).convert("RGB").resize((cw, ch), Image.LANCZOS),
                     ((i % 4) * cw, (i // 4) * ch))
        pl.save(os.path.join(ICI, "_planche-loupe.png"))
        print("planche ok")
    elif mode == "diff":
        # l'image finale doit redonner le logo d'origine
        a = np.array(frame(4.6).convert("RGB"), int)
        ref = Image.new("RGBA", (W, H), (255, 255, 255, 255))
        ref.alpha_composite(Image.open(os.path.join(os.path.dirname(ICI),
                                                    "logo-principal.png")).convert("RGBA"))
        d = np.abs(a - np.array(ref.convert("RGB"), int)).sum(axis=2)
        print("pixels differents > 30 :", int((d > 30).sum()), "/", W * H,
              " ecart max :", int(d.max()))
    else:
        fps, dur = 30, 4.6
        fd = os.path.join(ICI, "frames-loupe"); os.makedirs(fd, exist_ok=True)
        for k in range(int(fps * dur)):
            frame(k / fps).convert("RGB").resize((1080, 880), Image.LANCZOS)\
                .save(os.path.join(fd, "f%04d.png" % k))
        print("frames ok", int(fps * dur))
