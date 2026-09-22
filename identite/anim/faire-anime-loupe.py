# -*- coding: utf-8 -*-
"""Variante "loupe" : les batiments sont poses en petit, la loupe entre par la
gauche et grossit ce qui passe sous le verre. Quand elle se pose au centre, le
grossissement ramene exactement l'echelle du logo d'origine.

Produit logo-anime-loupe.svg et apercu-loupe.html.
"""
import json, os, base64, re

ICI = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(ICI, "calques")
meta = json.load(open(os.path.join(D, "meta.json")))
W, H = meta["W"], meta["H"]
C = {c["name"]: c for c in meta["calques"]}

CX, CY = 863, 518          # centre du verre
R_VERRE = 505              # legerement plus grand que le rayon interieur de l anneau,
                           # qui le recouvre : sinon le verre rogne le bas des batiments
SOL = 977                  # ligne de base des batiments
ECH = 0.72                 # echelle des batiments en fond
K = 1 / ECH                # grossissement du verre : ramene le fond a l'echelle 1
# trajet de la loupe : (pourcentage, dx, dy). Elle entre par la gauche, balaie
# les batiments, depasse un peu a droite puis revient se caler sur le centre.
TRAJET = [(0, -520, -80), (42, -130, 34), (72, 96, -28), (100, 0, 0)]
DUR, DEL = 1.95, 0.40      # duree et depart du deplacement
EASE = "cubic-bezier(.45,.05,.3,1)"
BATS = ["esc%d" % i for i in range(7)] + ["tour-cyan", "tour-orange"]


def b64(n):
    with open(os.path.join(D, n + ".png"), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def defs_images():
    out = []
    for n in BATS + ["anneau", "anneau-b", "texte", "texte-b"]:
        c = C[n]
        out.append('<image id="i-%s" x="%d" y="%d" width="%d" height="%d" href="%s"/>'
                   % (n, c["x"], c["y"], c["w"], c["h"], b64(n)))
    return "\n      ".join(out)


def ville():
    """Les neuf morceaux de batiment, avec leur animation de construction."""
    out = ['<use class="esc" href="#i-esc%d" style="--d:%.2fs"/>' % (i, 0.10 + (6 - i) * 0.075)
           for i in range(7)]
    out.append('<use class="cyan" href="#i-tour-cyan"/>')
    out.append('<use class="tourO" href="#i-tour-orange"/>')
    return "\n        ".join(out)


# Le manche de la loupe n'est pas separable : dans l'image d'origine il est soude
# au R de EXPERTISE. Il reste donc dans le calque du texte et arrive avec lui.

def etapes(facteur):
    """Le meme trajet, multiplie par un facteur.

    Le contenu du verre recoit -K fois le deplacement de la loupe : c'est ce qui
    garde le grossissement cale sur le centre du verre a chaque instant."""
    return "\n  ".join("%d%% { transform:translate(%.1fpx,%.1fpx); }"
                       % (p, facteur * x, facteur * y) for p, x, y in TRAJET)

CSS = """
:root, svg { --encre:#262c42; }
svg.sur-sombre { --encre:#ffffff; }
svg:not(.sur-sombre) .var-sombre { display:none; }
svg.sur-sombre .var-clair { display:none; }

.esc   { opacity:0; transform:translate(-90px,34px);
         animation:monte .5s cubic-bezier(.2,.9,.25,1) var(--d) forwards; }
@keyframes monte { to { opacity:1; transform:translate(0,0); } }
.cyan  { transform:translateY(880px); animation:pousse .9s cubic-bezier(.16,.85,.3,1) .45s forwards; }
.tourO { transform:translateY(430px); animation:pousse .75s cubic-bezier(.16,.85,.3,1) .62s forwards; }
@keyframes pousse { to { transform:translateY(0); } }

/* la loupe, le trou dans le fond et le contre-deplacement du contenu du verre
   partagent exactement le meme timing : le contenu grossi reste cale sur le verre */
.loupe, .troue { transform:translate(__LX__px,__LY__px);
                 animation:entre __DUR__s __EASE__ __DEL__s forwards; }
@keyframes entre {
  __ETAPES_L__
}
.contre { transform:translate(__CXX__px,__CYY__px);
          animation:contre __DUR__s __EASE__ __DEL__s forwards; }
@keyframes contre {
  __ETAPES_C__
}

.wipe    { transform:scaleX(0); transform-box:view-box; transform-origin:0 0;
           animation:wipe .9s cubic-bezier(.3,.8,.2,1) 2.35s forwards; }
@keyframes wipe { to { transform:scaleX(1); } }

.reflet { transform:translateX(-1500px); animation:reflet 5.2s cubic-bezier(.4,0,.3,1) 2.9s infinite; }
@keyframes reflet { 0%{transform:translateX(-1500px)} 22%{transform:translateX(600px)}
                    100%{transform:translateX(600px)} }
svg.sur-sombre .reflet { opacity:.28; }
""".replace("__LX__", "%.0f" % TRAJET[0][1]).replace("__LY__", "%.0f" % TRAJET[0][2]) \
   .replace("__CXX__", "%.1f" % (-K * TRAJET[0][1])).replace("__CYY__", "%.1f" % (-K * TRAJET[0][2])) \
   .replace("__ETAPES_L__", etapes(1)).replace("__ETAPES_C__", etapes(-K)) \
   .replace("__DUR__", "%.2f" % DUR).replace("__DEL__", "%.2f" % DEL).replace("__EASE__", EASE)

SVG = """<svg class="logo-anime" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="BTP Expertise">
  <defs>
    <style>{CSS}</style>
      {IMAGES}
    <clipPath id="LcSol"><rect x="0" y="0" width="{W}" height="{SOL}"/></clipPath>
    <clipPath id="LcVerre"><circle cx="{CX}" cy="{CY}" r="{RV}"/></clipPath>
    <clipPath id="LcHors" clipPathUnits="userSpaceOnUse">
      <path class="troue" clip-rule="evenodd" d="M-2400,-2400 H4800 V4800 H-2400 Z
            M{CX},{CYT} a{RV},{RV} 0 1,0 .1,0 Z"/>
    </clipPath>
    <clipPath id="LcWipe"><rect class="wipe" x="0" y="1030" width="{W}" height="290"/></clipPath>
    <linearGradient id="LgRef" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/>
      <stop offset=".45" stop-color="#fff" stop-opacity=".55"/>
      <stop offset=".55" stop-color="#fff" stop-opacity=".55"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <!-- les batiments en petit : masques partout ou le verre passe -->
  <g clip-path="url(#LcHors)">
    <g transform="translate({CX},{CY}) scale({ECH}) translate(-{CX},-{CY})">
      <g clip-path="url(#LcSol)">
        {VILLE}
      </g>
    </g>
  </g>

  <!-- la loupe : sous le verre, les memes batiments a l'echelle 1 -->
  <g class="loupe">
    <g clip-path="url(#LcVerre)">
      <g class="contre">
        <g clip-path="url(#LcSol)">
          {VILLE}
        </g>
      </g>
      <g style="mix-blend-mode:screen">
        <rect class="reflet" x="0" y="-180" width="210" height="1500" fill="url(#LgRef)"
              transform-origin="150 518" style="rotate:-18deg"/>
      </g>
    </g>
    <use class="var-clair" href="#i-anneau"/>
    <use class="var-sombre" href="#i-anneau-b"/>
  </g>

  <g clip-path="url(#LcWipe)">
    <use class="var-clair" href="#i-texte"/>
    <use class="var-sombre" href="#i-texte-b"/>
  </g>
</svg>""".format(W=W, H=H, CSS=CSS, IMAGES=defs_images(), SOL=SOL, CX=CX, CY=CY,
                 CYT=CY - R_VERRE, RV=R_VERRE, ECH=ECH, VILLE=ville())

# Les deux animations peuvent se retrouver dans la meme page : on prefixe les
# classes et les keyframes de celle-ci pour qu'elles n'ecrasent pas les autres.
for nom in ["esc", "cyan", "tourO", "monte", "pousse", "loupe", "troue", "entre",
            "contre", "wipe", "reflet", "var-clair", "var-sombre"]:
    SVG = re.sub(r"\b%s\b" % nom, "L" + nom, SVG)

open(os.path.join(ICI, "logo-anime-loupe.svg"), "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n' + SVG)

HTML = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><title>Logo anime loupe - BTP Expertise</title>
<style>
 body{margin:0;font-family:system-ui,sans-serif;background:#f4f6f9;color:#262c42;
      display:flex;flex-direction:column;align-items:center;gap:18px;padding:30px}
 .scene{width:min(820px,90vw);background:#fff;border-radius:18px;padding:28px 34px;
        box-shadow:0 12px 40px rgba(38,44,66,.10)}
 .scene.sombre{background:#1a1f30}
 .logo-anime{width:100%;height:auto;display:block}
 .barre{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
 button{font:inherit;padding:9px 16px;border-radius:10px;border:1px solid #d5dae4;background:#fff;cursor:pointer}
 input[type=range]{width:240px}
</style></head><body>
<div class="scene" id="scene">__SVG__</div>
<div class="barre">
  <button onclick="rejouer()">Rejouer</button>
  <button onclick="vitesse(.5)">Ralenti</button>
  <button onclick="vitesse(1)">Vitesse normale</button>
  <button onclick="document.getElementById('scene').classList.toggle('sombre');svg.classList.toggle('sur-sombre')">Fond sombre</button>
</div>
<div class="barre">
  <label>Parcourir : <input type="range" id="curseur" min="0" max="3600" value="3600" step="10" oninput="seek(this.value)"></label>
  <span id="tlabel">3.60 s</span>
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
</script></body></html>""".replace("__SVG__", SVG)
open(os.path.join(ICI, "apercu-loupe.html"), "w", encoding="utf-8").write(HTML)
print("svg  %.0f ko" % (os.path.getsize(os.path.join(ICI, "logo-anime-loupe.svg")) / 1024))
