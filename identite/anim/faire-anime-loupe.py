# -*- coding: utf-8 -*-
"""Fabrique les SVG des animations ou la loupe grossit ce qui est derriere.

    python faire-anime-loupe.py            # les trois scenarios
    python faire-anime-loupe.py balayage   # un seul

Les timings sont ceux de rendu-loupe.py, qui produit les videos. Toute
modification doit etre reportee dans les deux fichiers.
"""
import json, os, base64, re, sys
import commun as C

ICI = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(ICI, "calques")
meta = json.load(open(os.path.join(D, "meta.json")))
CAL = {c["name"]: c for c in meta["calques"]}
BATS = ["esc%d" % i for i in range(7)] + ["tour-cyan", "tour-orange"]

EASE_TRAJET = "cubic-bezier(.45,.05,.3,1)"
EASE_ZOOM = "cubic-bezier(.4,0,.2,1.08)"

SCENARIOS = {
    "balayage": dict(
        titre="La loupe balaie les facades",
        trajet=[(0, -380, -70), (42, -130, 34), (72, 96, -28), (100, 0, 0)],
        t_trajet=0.40, d_trajet=1.95, zoom=None, trace=None, manche=None,
        nom=(2.35, .9), t_reflet=2.90, duree=5.0),
    "inspection": dict(
        titre="La loupe s'arrete sur chaque batiment",
        trajet=[(0, -440, -40), (16, -215, 100), (28, -215, 100),
                (44, -20, -70), (56, -20, -70), (72, 185, 85), (84, 185, 85), (100, 0, 0)],
        t_trajet=0.35, d_trajet=3.00, zoom=None, trace=None, manche=None,
        nom=(3.45, .9), t_reflet=4.00, duree=6.0),
    "mise-au-point": dict(
        titre="La loupe fait le point",
        trajet=[(0, 0, 0), (100, 0, 0)], t_trajet=0.0, d_trajet=0.1,
        zoom=[(0, 1.0), (78, 1.06), (100, 1.0)], t_zoom=2.00, d_zoom=0.85,
        trace=(0.85, 1.05), manche=(1.95, .45),
        nom=(2.85, .9), t_reflet=3.60, duree=5.2),
}


def b64(n):
    with open(os.path.join(D, n + ".png"), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def images():
    return "\n      ".join(
        '<image id="i-%s" x="%d" y="%d" width="%d" height="%d" href="%s"/>'
        % (n, CAL[n]["x"], CAL[n]["y"], CAL[n]["w"], CAL[n]["h"], b64(n))
        for n in BATS + ["anneau", "anneau-b", "texte", "texte-b"])


def ville():
    out = ['<use class="esc" href="#i-esc%d" style="--d:%.2fs"/>' % (i, 0.10 + (6 - i) * 0.075)
           for i in range(7)]
    out.append('<use class="cyan" href="#i-tour-cyan"/>')
    out.append('<use class="tourO" href="#i-tour-orange"/>')
    return "\n          ".join(out)


def keyframes_trajet(pts, facteur):
    return "\n  ".join("%d%% { transform:translate(%.1fpx,%.1fpx); }"
                       % (p, facteur * x, facteur * y) for p, x, y in pts)


def keyframes_zoom(pts):
    """La valeur interpolee va de 1 (pas de grossissement) a K."""
    return "\n  ".join("%d%% { scale:%.4f; }" % (p, C.ECH * (1 + (C.K - 1) * v))
                       for p, v in pts)


def fabrique(nom):
    S = SCENARIOS[nom]
    css = ["""
svg { --encre:#262c42; }
svg.sur-sombre { --encre:#ffffff; }
svg:not(.sur-sombre) .var-sombre { display:none; }
svg.sur-sombre .var-clair { display:none; }
svg.sur-sombre .reflet { opacity:.28; }

.esc   { opacity:0; transform:translate(-90px,34px);
         animation:monte .5s cubic-bezier(.2,.9,.25,1) var(--d) forwards; }
@keyframes monte { to { opacity:1; transform:translate(0,0); } }
.cyan  { transform:translateY(880px); animation:pousse .9s cubic-bezier(.16,.85,.3,1) .45s forwards; }
.tourO { transform:translateY(430px); animation:pousse .75s cubic-bezier(.16,.85,.3,1) .62s forwards; }
@keyframes pousse { to { transform:translateY(0); } }

.wipe     { transform:scaleX(0); transform-box:fill-box; transform-origin:0 0;
            animation:wipe %.2fs cubic-bezier(.3,.8,.2,1) %.2fs forwards; }
@keyframes wipe { to { transform:scaleX(1); } }
.wipe-inv { transform:translateX(0); transform-box:fill-box; transform-origin:0 0;
            animation:wipeinv %.2fs cubic-bezier(.3,.8,.2,1) %.2fs forwards; }
@keyframes wipeinv { to { transform:translateX(1600px); } }

.reflet { transform:translateX(-1500px);
          animation:reflet 5.2s cubic-bezier(.4,0,.3,1) %.2fs infinite; }
@keyframes reflet { 0%%{transform:translateX(-1500px)} 22%%{transform:translateX(600px)}
                    100%%{transform:translateX(600px)} }
""" % (S["nom"][1], S["nom"][0], S["nom"][1], S["nom"][0], S["t_reflet"])]

    # le deplacement : la loupe, le trou dans le fond et le contre-deplacement du
    # contenu du verre partagent le meme timing, au facteur pres
    if S["d_trajet"] > 0.11:
        css.append("""
/* le contenu du verre recoit -K fois le deplacement de la loupe : c'est ce qui
   garde le grossissement cale sur le centre du verre a chaque instant */
.loupe, .troue { transform:translate(%.0fpx,%.0fpx);
                 animation:entre %.2fs %s %.2fs forwards; }
@keyframes entre {
  %s
}
.contre { transform:translate(%.1fpx,%.1fpx);
          animation:contre %.2fs %s %.2fs forwards; }
@keyframes contre {
  %s
}
""" % (S["trajet"][0][1], S["trajet"][0][2], S["d_trajet"], EASE_TRAJET, S["t_trajet"],
       keyframes_trajet(S["trajet"], 1),
       -C.K * S["trajet"][0][1], -C.K * S["trajet"][0][2],
       S["d_trajet"], EASE_TRAJET, S["t_trajet"],
       keyframes_trajet(S["trajet"], -C.K)))

    if S["zoom"]:
        css.append("""
.zoom { scale:%.4f; animation:zoom %.2fs %s %.2fs forwards; }
@keyframes zoom {
  %s
}
""" % (C.ECH * (1 + (C.K - 1) * S["zoom"][0][1]), S["d_zoom"], EASE_ZOOM, S["t_zoom"],
       keyframes_zoom(S["zoom"])))

    if S["trace"]:
        css.append("""
.trace   { stroke-dashoffset:1000; animation:trace %.2fs cubic-bezier(.55,.05,.25,1) %.2fs forwards; }
@keyframes trace { to { stroke-dashoffset:0; } }
.attache { opacity:0; animation:appar .08s linear %.2fs forwards; }
@keyframes appar { to { opacity:1; } }
""" % (S["trace"][1], S["trace"][0], S["trace"][0] + S["trace"][1] - .08))

    if S["manche"]:
        css.append("""
.manche-rev { transform:scaleY(0); transform-box:fill-box; transform-origin:0 0;
              animation:manche %.2fs cubic-bezier(0,0,.58,1) %.2fs forwards; }
@keyframes manche { to { transform:scaleY(1); } }
""" % (S["manche"][1], S["manche"][0]))

    anneau = """<use class="var-clair" href="#i-anneau"/>
    <use class="var-sombre" href="#i-anneau-b"/>"""
    if S["trace"]:
        anneau = """<g mask="url(#mTrace)">
      %s
    </g>""" % anneau

    manche = """<g clip-path="url(#cWipeInv)"><path d="%s"/></g>
      <path d="%s"/>""" % (C.chemin(C.MANCHE_HAUT), C.chemin(C.MANCHE_BAS))
    manche = """<g fill="var(--encre)"%s>
      %s
    </g>""" % (' clip-path="url(#cManche)"' if S["manche"] else "", manche)

    zoom_ouvre = zoom_ferme = ""
    if S["zoom"]:
        zoom_ouvre = ('<g transform="translate(%d,%d)"><g class="zoom">'
                      '<g transform="translate(%d,%d)">' % (C.CX, C.CY, -C.CX, -C.CY))
        zoom_ferme = "</g></g></g>"

    svg = """<svg class="logo-anime" xmlns="http://www.w3.org/2000/svg"
     viewBox="{VX} {VY} {VW} {VH}" role="img" aria-label="BTP Expertise">
  <defs>
    <style>{CSS}</style>
      {IMAGES}
    <mask id="mTrace" maskUnits="userSpaceOnUse">
      <circle class="trace" cx="{CX}" cy="{CY}" r="485" fill="none" stroke="#fff" stroke-width="96"
              stroke-linecap="round" pathLength="1000" stroke-dasharray="1000"
              transform="rotate(73 {CX} {CY})"/>
      <circle class="attache" cx="1052" cy="1030" r="130" fill="#fff"/>
    </mask>
    <clipPath id="cSol"><rect x="{VX}" y="{VY}" width="{VW}" height="{SOLH}"/></clipPath>
    <clipPath id="cVerre"><circle cx="{CX}" cy="{CY}" r="{RV}"/></clipPath>
    <clipPath id="cHors" clipPathUnits="userSpaceOnUse">
      <path class="troue" clip-rule="evenodd" d="M-2400,-2400 H4800 V4800 H-2400 Z
            M{CX},{CYT} a{RV},{RV} 0 1,0 .1,0 Z"/>
    </clipPath>
    <clipPath id="cWipe"><rect class="wipe" x="0" y="1030" width="1600" height="290"/></clipPath>
    <clipPath id="cWipeInv"><rect class="wipe-inv" x="0" y="1030" width="1600" height="290"/></clipPath>
    <clipPath id="cManche"><rect class="manche-rev" x="900" y="1042" width="500" height="450"/></clipPath>
    <linearGradient id="gRef" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/>
      <stop offset=".45" stop-color="#fff" stop-opacity=".55"/>
      <stop offset=".55" stop-color="#fff" stop-opacity=".55"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <!-- les batiments en petit : masques partout ou le verre passe -->
  <g clip-path="url(#cHors)">
    <g transform="translate({CX},{CY}) scale({ECH}) translate(-{CX},-{CY})">
      <g clip-path="url(#cSol)">
          {VILLE}
      </g>
    </g>
  </g>

  <!-- la loupe : sous le verre, les memes batiments, grossis -->
  <g class="loupe">
    <g clip-path="url(#cVerre)">
      <g class="contre">
        {ZOUV}<g clip-path="url(#cSol)">
          {VILLE}
        </g>{ZFER}
      </g>
      <g style="mix-blend-mode:screen">
        <rect class="reflet" x="0" y="-180" width="210" height="1500" fill="url(#gRef)"
              style="rotate:-18deg" transform-origin="150 518"/>
      </g>
    </g>
    {ANNEAU}
    {MANCHE}
  </g>

  <g clip-path="url(#cWipe)">
    <use class="var-clair" href="#i-texte"/>
    <use class="var-sombre" href="#i-texte-b"/>
  </g>
</svg>""".format(VX=C.VUE_X, VY=C.VUE_Y, VW=C.VUE_W, VH=C.VUE_H, CSS="".join(css),
                 IMAGES=images(), CX=C.CX, CY=C.CY, CYT=C.CY - C.R_VERRE, RV=C.R_VERRE,
                 SOLH=C.SOL - C.VUE_Y, ECH=C.ECH, VILLE=ville(),
                 ANNEAU=anneau, MANCHE=manche, ZOUV=zoom_ouvre, ZFER=zoom_ferme)

    # plusieurs animations peuvent cohabiter dans une meme page : on prefixe les
    # classes et les keyframes de chaque scenario
    pref = {"balayage": "B", "inspection": "I", "mise-au-point": "M"}[nom]
    for mot in ["esc", "cyan", "tourO", "monte", "pousse", "loupe", "troue", "entre",
                "contre", "wipe", "wipeinv", "wipe-inv", "reflet", "trace", "attache",
                "appar", "manche", "manche-rev", "zoom", "var-clair", "var-sombre",
                "mTrace", "cSol", "cVerre", "cHors", "cWipe", "cWipeInv", "cManche", "gRef"]:
        svg = re.sub(r"\b%s\b" % mot, pref + mot, svg)
    return svg, S


def page(svg, S, duree_ms):
    return """<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><title>%s</title>
<style>
 body{margin:0;font-family:system-ui,sans-serif;background:#f4f6f9;color:#262c42;
      display:flex;flex-direction:column;align-items:center;gap:18px;padding:30px}
 .scene{width:min(760px,90vw);background:#fff;border-radius:18px;padding:20px 26px;
        box-shadow:0 12px 40px rgba(38,44,66,.10)}
 .scene.sombre{background:#1a1f30}
 .logo-anime{width:100%%;height:auto;display:block}
 .barre{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
 button{font:inherit;padding:9px 16px;border-radius:10px;border:1px solid #d5dae4;background:#fff;cursor:pointer}
 input[type=range]{width:240px}
</style></head><body>
<div class="scene" id="scene">%s</div>
<div class="barre">
  <button onclick="rejouer()">Rejouer</button>
  <button onclick="vitesse(.5)">Ralenti</button>
  <button onclick="vitesse(1)">Vitesse normale</button>
  <button onclick="document.getElementById('scene').classList.toggle('sombre');svg.classList.toggle('sur-sombre')">Fond sombre</button>
</div>
<div class="barre">
  <label>Parcourir : <input type="range" id="curseur" min="0" max="%d" value="%d" step="10" oninput="seek(this.value)"></label>
  <span id="tlabel">%.2f s</span>
</div>
<script>
const svg=document.querySelector('.logo-anime');
function anims(){return svg.getAnimations({subtree:true});}
function rejouer(){anims().forEach(a=>{a.cancel();a.play();});}
function vitesse(v){anims().forEach(a=>a.playbackRate=v);}
function seek(ms){ms=+ms;document.getElementById('tlabel').textContent=(ms/1000).toFixed(2)+' s';
  anims().forEach(a=>{a.pause();a.currentTime=ms;});}
const q=new URLSearchParams(location.search);
if(q.has('sombre')){document.getElementById('scene').classList.add('sombre');svg.classList.add('sur-sombre');}
if(q.has('t')){addEventListener('load',()=>{seek(+q.get('t'));
  document.querySelectorAll('.barre').forEach(e=>e.style.display='none');});}
</script></body></html>""" % (S["titre"], svg, duree_ms, duree_ms, duree_ms / 1000.0)


if __name__ == "__main__":
    demandes = [a for a in sys.argv[1:] if a in SCENARIOS] or list(SCENARIOS)
    for nom in demandes:
        svg, S = fabrique(nom)
        f = os.path.join(ICI, "logo-anime-%s.svg" % nom)
        open(f, "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg)
        open(os.path.join(ICI, "apercu-%s.html" % nom), "w", encoding="utf-8").write(
            page(svg, S, int(S["duree"] * 1000)))
        print("%-14s %.0f ko" % (nom, os.path.getsize(f) / 1024))
