# -*- coding: utf-8 -*-
"""Rendu image par image de l'animation du logo BTP Expertise.
Meme choregraphie que logo-anime.svg. Sort des PNG, puis ffmpeg fait le MP4/GIF."""
import numpy as np, json, os, sys
from PIL import Image

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calques")
meta = json.load(open(os.path.join(D, "meta.json")))
W, H = meta["W"], meta["H"]
CAL = {c["name"]: c for c in meta["calques"]}
IMG = {n: np.array(Image.open(os.path.join(D, n + ".png")).convert("RGBA")).astype(np.float32)
       for n in CAL}
CX, CY, R_EXT, SOL = 863.0, 518.0, 540.0, 977

def bezier(x1, y1, x2, y2):
    def cx(t): return 3*x1*t*(1-t)**2 + 3*x2*t*t*(1-t) + t**3
    def cy(t): return 3*y1*t*(1-t)**2 + 3*y2*t*t*(1-t) + t**3
    def f(p):
        lo, hi = 0.0, 1.0
        for _ in range(28):
            m = (lo+hi)/2
            if cx(m) < p: lo = m
            else: hi = m
        return cy((lo+hi)/2)
    return f
EASE_M = bezier(.2,.9,.25,1); EASE_P = bezier(.16,.85,.3,1)
EASE_T = bezier(.55,.05,.25,1); EASE_W = bezier(.3,.8,.2,1); EASE_O = bezier(0,0,.58,1)

def prog(t, delay, dur, ease):
    if t <= delay: return 0.0
    if t >= delay+dur: return 1.0
    return ease((t-delay)/dur)

# grilles reutilisees
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
RAD = np.hypot(XX-CX, YY-CY)
ANG = (np.degrees(np.arctan2(YY-CY, XX-CX)) - 73.0) % 360.0
CAP = np.hypot(XX-1052, YY-1030) <= 130

def pose(canvas, name, dx=0.0, dy=0.0, alpha=1.0, clip_sol=False, mask=None):
    """Compose le calque sur le canvas RGBA float, decale de (dx,dy)."""
    if alpha <= 0.003: return
    c = CAL[name]; src = IMG[name]
    x0, y0 = int(round(c["x"]+dx)), int(round(c["y"]+dy))
    h, w = src.shape[:2]
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    ww = min(w-sx0, W-dx0); hh = min(h-sy0, H-dy0)
    if ww <= 0 or hh <= 0: return
    s = src[sy0:sy0+hh, sx0:sx0+ww]
    a = s[:, :, 3:4] / 255.0 * alpha
    if clip_sol:
        yb = np.arange(dy0, dy0+hh)[:, None, None]
        a = a * (yb < SOL)
    if mask is not None:
        a = a * mask[dy0:dy0+hh, dx0:dx0+ww, None]
    d = canvas[dy0:dy0+hh, dx0:dx0+ww]
    d[:, :, :3] = s[:, :, :3]*a + d[:, :, :3]*(1-a)
    d[:, :, 3:4] = a*255 + d[:, :, 3:4]*(1-a)

def frame(t, fond=(255, 255, 255, 255)):
    cv = np.zeros((H, W, 4), np.float32); cv[:, :, :] = fond
    # 1. escalier orange, du bas vers le haut
    for i in range(7):
        p = prog(t, 0.15+(6-i)*0.085, 0.55, EASE_M)
        if p > 0: pose(cv, "esc%d" % i, -90*(1-p), 34*(1-p), min(1, p*2.2), clip_sol=True)
    # 2. tours qui poussent
    p = prog(t, .62, .95, EASE_P)
    if p > 0: pose(cv, "tour-cyan", 0, 880*(1-p), 1, clip_sol=True)
    p = prog(t, .86, .80, EASE_P)
    if p > 0: pose(cv, "tour-orange", 0, 430*(1-p), 1, clip_sol=True)
    # 3. trace de l'anneau + attache du manche
    p = prog(t, 1.05, 1.15, EASE_T)
    if p > 0:
        m = ((ANG <= p*360.0) & (RAD <= R_EXT)).astype(np.float32)
        # l'attache du manche sort du cercle : revelee quand le trace boucle
        cap = prog(t, 2.13, .08, EASE_O)
        if cap > 0: m = np.maximum(m, CAP*cap)
        pose(cv, "anneau", mask=m)
    # 4. texte + manche : balayage gauche -> droite
    p = prog(t, 2.15, .9, EASE_W)
    if p > 0:
        m = (XX <= p*W).astype(np.float32)
        pose(cv, "texte", mask=m)
    # 5. reflet sur le verre
    cyc = (t-2.30) % 5.2
    if 0 <= cyc <= 1.30:
        q = EASE_T(cyc/1.30)
        xc = -700 + q*2400
        th = np.radians(-18.0)
        u = (XX-xc)*np.cos(th) + (YY-CY)*np.sin(th)
        g = np.clip(1 - np.abs(u)/105.0, 0, 1)**1.5
        disque = (RAD <= 452)
        inten = (g*disque*0.55)[:, :, None]
        cv[:, :, :3] = 255 - (255-cv[:, :, :3])*(1-inten)
    return Image.fromarray(np.clip(cv, 0, 255).astype(np.uint8), "RGBA")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "planche"
    OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    if mode == "planche":
        ts = [0.25, 0.55, 0.85, 1.15, 1.45, 1.75, 2.05, 2.35, 2.65, 2.95, 3.25, 3.60]
        cw, ch = W//3, H//3
        pl = Image.new("RGB", (4*cw, 3*ch), (222, 227, 234))
        for i, t in enumerate(ts):
            im = frame(t).convert("RGB").resize((cw, ch), Image.LANCZOS)
            pl.paste(im, ((i % 4)*cw, (i//4)*ch))
        pl.save(os.path.join(OUT, "_planche-frames.png"))
        print("planche ok", pl.size)
    else:
        fps, dur = 30, 4.4
        fd = os.path.join(OUT, "frames"); os.makedirs(fd, exist_ok=True)
        for k in range(int(fps*dur)):
            frame(k/fps).convert("RGB").resize((1080, 880), Image.LANCZOS)\
                .save(os.path.join(fd, "f%04d.png" % k))
        print("frames ok", int(fps*dur))
