# -*- coding: utf-8 -*-
"""Fabrique logo-anime.svg et apercu.html : l'animation "construction".

Les timings sont ceux de rendu.py, qui produit les videos. Toute modification
doit etre reportee dans les deux fichiers.
"""
import json, os, base64
import commun as C

ICI = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(ICI, "calques")
meta = json.load(open(os.path.join(D, "meta.json")))
CAL = {c["name"]: c for c in meta["calques"]}
BATS = ["esc%d" % i for i in range(7)] + ["tour-cyan", "tour-orange"]


def b64(n):
    with open(os.path.join(D, n + ".png"), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def images():
    return "\n      ".join(
        '<image id="i-%s" x="%d" y="%d" width="%d" height="%d" href="%s"/>'
        % (n, CAL[n]["x"], CAL[n]["y"], CAL[n]["w"], CAL[n]["h"], b64(n))
        for n in BATS + ["anneau", "anneau-b", "texte", "texte-b"])


def ville():
    out = ['<use class="esc" href="#i-esc%d" style="--d:%.2fs"/>' % (i, 0.15 + (6 - i) * 0.085)
           for i in range(7)]
    out.append('<use class="cyan" href="#i-tour-cyan"/>')
    out.append('<use class="tourO" href="#i-tour-orange"/>')
    return "\n      ".join(out)


CSS = """
svg { --encre:#262c42; }
svg.sur-sombre { --encre:#ffffff; }
svg:not(.sur-sombre) .var-sombre { display:none; }
svg.sur-sombre .var-clair { display:none; }
svg.sur-sombre .reflet { opacity:.28; }

.esc   { opacity:0; transform:translate(-90px,34px);
         animation:monte .55s cubic-bezier(.2,.9,.25,1) var(--d) forwards; }
@keyframes monte { to { opacity:1; transform:translate(0,0); } }
.cyan  { transform:translateY(880px); animation:pousse .95s cubic-bezier(.16,.85,.3,1) .62s forwards; }
.tourO { transform:translateY(430px); animation:pousse .80s cubic-bezier(.16,.85,.3,1) .86s forwards; }
@keyframes pousse { to { transform:translateY(0); } }

.trace   { stroke-dashoffset:1000; animation:trace 1.15s cubic-bezier(.55,.05,.25,1) 1.05s forwards; }
@keyframes trace { to { stroke-dashoffset:0; } }
.attache { opacity:0; animation:appar .08s linear 2.12s forwards; }
@keyframes appar { to { opacity:1; } }

/* le manche descend, puis le nom vient reprendre sa partie haute */
.manche-rev { transform:scaleY(0); transform-box:fill-box; transform-origin:0 0;
              animation:manche .45s cubic-bezier(0,0,.58,1) 2.15s forwards; }
@keyframes manche { to { transform:scaleY(1); } }

.wipe     { transform:scaleX(0); transform-box:fill-box; transform-origin:0 0;
            animation:wipe .9s cubic-bezier(.3,.8,.2,1) 2.55s forwards; }
@keyframes wipe { to { transform:scaleX(1); } }
.wipe-inv { transform:translateX(0); transform-box:fill-box; transform-origin:0 0;
            animation:wipeinv .9s cubic-bezier(.3,.8,.2,1) 2.55s forwards; }
@keyframes wipeinv { to { transform:translateX(1600px); } }

.reflet { transform:translateX(-1500px); animation:reflet 5.2s cubic-bezier(.4,0,.3,1) 3.3s infinite; }
@keyframes reflet { 0%{transform:translateX(-1500px)} 22%{transform:translateX(600px)}
                    100%{transform:translateX(600px)} }
"""

SVG = """<svg class="logo-anime" xmlns="http://www.w3.org/2000/svg"
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
    <clipPath id="cWipe"><rect class="wipe" x="0" y="1030" width="1600" height="290"/></clipPath>
    <clipPath id="cWipeInv"><rect class="wipe-inv" x="0" y="1030" width="1600" height="290"/></clipPath>
    <clipPath id="cManche"><rect class="manche-rev" x="900" y="1042" width="500" height="450"/></clipPath>
    <clipPath id="cVerre"><circle cx="{CX}" cy="{CY}" r="452"/></clipPath>
    <linearGradient id="gRef" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/>
      <stop offset=".45" stop-color="#fff" stop-opacity=".55"/>
      <stop offset=".55" stop-color="#fff" stop-opacity=".55"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <g clip-path="url(#cSol)">
      {VILLE}
  </g>

  <g clip-path="url(#cVerre)" style="mix-blend-mode:screen">
    <rect class="reflet" x="0" y="-180" width="210" height="1500" fill="url(#gRef)"
          transform-origin="150 518" style="rotate:-18deg"/>
  </g>

  <g mask="url(#mTrace)">
    <use class="var-clair" href="#i-anneau"/>
    <use class="var-sombre" href="#i-anneau-b"/>
  </g>

  <g clip-path="url(#cManche)" fill="var(--encre)">
    <g clip-path="url(#cWipeInv)"><path d="{MHAUT}"/></g>
    <path d="{MBAS}"/>
  </g>

  <g clip-path="url(#cWipe)">
    <use class="var-clair" href="#i-texte"/>
    <use class="var-sombre" href="#i-texte-b"/>
  </g>
</svg>""".format(VX=C.VUE_X, VY=C.VUE_Y, VW=C.VUE_W, VH=C.VUE_H, CSS=CSS, IMAGES=images(),
                 CX=C.CX, CY=C.CY, SOLH=C.SOL - C.VUE_Y, VILLE=ville(),
                 MHAUT=C.chemin(C.MANCHE_HAUT), MBAS=C.chemin(C.MANCHE_BAS))

open(os.path.join(ICI, "logo-anime.svg"), "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n' + SVG)

HTML = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><title>Logo anime - BTP Expertise</title>
<style>
 body{margin:0;font-family:system-ui,sans-serif;background:#f4f6f9;color:#262c42;
      display:flex;flex-direction:column;align-items:center;gap:18px;padding:30px}
 .scene{width:min(760px,90vw);background:#fff;border-radius:18px;padding:20px 26px;
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
  <label>Parcourir : <input type="range" id="curseur" min="0" max="5000" value="5000" step="10" oninput="seek(this.value)"></label>
  <span id="tlabel">5.00 s</span>
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
open(os.path.join(ICI, "apercu.html"), "w", encoding="utf-8").write(HTML)
print("svg %.0f ko" % (os.path.getsize(os.path.join(ICI, "logo-anime.svg")) / 1024))
