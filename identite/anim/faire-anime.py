# -*- coding: utf-8 -*-
import json, os, base64
# -*- coding: utf-8 -*-
"""Fabrique logo-anime.svg et apercu.html a partir des calques."""
ICI=os.path.dirname(os.path.abspath(__file__))
D=os.path.join(ICI,"calques"); OUT=ICI
meta=json.load(open(os.path.join(D,"meta.json")))
W,H=meta["W"],meta["H"]
C={c["name"]:c for c in meta["calques"]}

def b64(n):
    with open(os.path.join(D,n+".png"),"rb") as f:
        return "data:image/png;base64,"+base64.b64encode(f.read()).decode()

def img(n, cls, extra=""):
    c=C[n]
    return ('<image class="%s" x="%d" y="%d" width="%d" height="%d" href="%s" %s/>'
            %(cls,c["x"],c["y"],c["w"],c["h"],b64(n),extra))

CX,CY,R = 863, 518, 485
SOL = 977

esc = "\n    ".join(
    img("esc%d"%i, "esc", 'style="--d:%.2fs"'%(0.15+(6-i)*0.085)) for i in range(7))

CSS = """
.esc, .cyan, .tourO, .trace, .cap, .reflet, .wipe { will-change: transform, opacity; }

.esc   { opacity:0; transform: translate(-90px, 34px); animation: monte .55s cubic-bezier(.2,.9,.25,1) var(--d) forwards; }
@keyframes monte { to { opacity:1; transform: translate(0,0); } }

.cyan  { transform: translateY(880px); animation: pousse .95s cubic-bezier(.16,.85,.3,1) .62s forwards; }
.tourO { transform: translateY(430px); animation: pousse .8s cubic-bezier(.16,.85,.3,1) .86s forwards; }
@keyframes pousse { to { transform: translateY(0); } }

.trace { stroke-dashoffset: 1000; animation: trace 1.15s cubic-bezier(.55,.05,.25,1) 1.05s forwards; }
@keyframes trace { to { stroke-dashoffset: 0; } }
.cap   { opacity:0; animation: appar .08s linear 2.13s forwards; }
@keyframes appar { to { opacity:1; } }

.wipe  { transform: scaleX(0); transform-box: view-box; transform-origin: 0 0;
         animation: wipe .9s cubic-bezier(.3,.8,.2,1) 2.15s forwards; }
@keyframes wipe { to { transform: scaleX(1); } }

.reflet { transform: translateX(-1500px); animation: reflet 5.2s cubic-bezier(.4,0,.3,1) 2.3s infinite; }
@keyframes reflet {
  0%   { transform: translateX(-1500px); }
  22%  { transform: translateX(600px); }
  100% { transform: translateX(600px); }
}
.fige *, .fige { animation-play-state: paused !important; }
svg:not(.sur-sombre) .var-sombre { display: none; }
svg.sur-sombre .var-clair { display: none; }
svg.sur-sombre .reflet { opacity: .28; }
"""

SVG = """<svg class="logo-anime" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="BTP Expertise">
  <defs>
    <style>{CSS}</style>
    <mask id="mTrace" maskUnits="userSpaceOnUse">
      <circle class="trace" cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="#fff" stroke-width="96"
              stroke-linecap="round" pathLength="1000" stroke-dasharray="1000" transform="rotate(73 {CX} {CY})"/>
      <circle class="cap" cx="1052" cy="1030" r="130" fill="#fff"/>
    </mask>
    <clipPath id="cSol"><rect x="0" y="0" width="{W}" height="{SOL}"/></clipPath>
    <clipPath id="cVerre"><circle cx="{CX}" cy="{CY}" r="452"/></clipPath>
    <clipPath id="cWipe"><rect class="wipe" x="0" y="1030" width="{W}" height="290"/></clipPath>
    <linearGradient id="gRef" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/>
      <stop offset=".45" stop-color="#fff" stop-opacity=".55"/>
      <stop offset=".55" stop-color="#fff" stop-opacity=".55"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <g clip-path="url(#cSol)">
    {ESC}
    {CYAN}
    {TOURO}
  </g>

  <g mask="url(#mTrace)">
    {ANNEAU}
  </g>

  <g clip-path="url(#cVerre)" style="mix-blend-mode:screen">
    <rect class="reflet" x="0" y="-180" width="210" height="1500" fill="url(#gRef)" transform-origin="150 518"
          style="rotate:-18deg"/>
  </g>

  <g clip-path="url(#cWipe)">
    {TXT}
  </g>
</svg>""".format(W=W,H=H,CX=CX,CY=CY,R=R,SOL=SOL,CSS=CSS,
    ESC=esc, CYAN=img("tour-cyan","cyan"), TOURO=img("tour-orange","tourO"),
    ANNEAU=img("anneau","var-clair")+img("anneau-b","var-sombre"),
    TXT=img("texte","var-clair")+img("texte-b","var-sombre"))

open(os.path.join(OUT,"logo-anime.svg"),"w",encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'+SVG)

HTML = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><title>Logo anime - BTP Expertise</title>
<style>
 body{margin:0;font-family:system-ui,sans-serif;background:#f4f6f9;color:#262c42;
      display:flex;flex-direction:column;align-items:center;gap:18px;padding:30px}
 .scene{width:min(820px,90vw);background:#fff;border-radius:18px;padding:28px 34px;
        box-shadow:0 12px 40px rgba(38,44,66,.10)}
 .scene.sombre{background:#1a1f30}
 .logo-anime{width:100%;height:auto;display:block}
 .barre{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
 button{font:inherit;padding:9px 16px;border-radius:10px;border:1px solid #d5dae4;background:#fff;cursor:pointer}
 button:hover{border-color:#ff8a00}
 input[type=range]{width:220px}
 code{background:#e9edf3;padding:2px 6px;border-radius:5px}
</style></head><body>
<div class="scene" id="scene">__SVG__</div>
<div class="barre">
  <button onclick="rejouer()">Rejouer</button>
  <button onclick="vitesse(.6)">Ralenti</button>
  <button onclick="vitesse(1)">Vitesse normale</button>
  <button onclick="document.getElementById('scene').classList.toggle('sombre');svg.classList.toggle('sur-sombre')">Fond sombre</button>
</div>
<div class="barre">
  <label>Parcourir : <input type="range" id="curseur" min="0" max="3400" value="3400" step="10" oninput="seek(this.value)"></label>
  <span id="tlabel">3.40 s</span>
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
open(os.path.join(OUT,"apercu.html"),"w",encoding="utf-8").write(HTML)
print("svg  %.0f ko"%(os.path.getsize(os.path.join(OUT,"logo-anime.svg"))/1024))
print("html %.0f ko"%(os.path.getsize(os.path.join(OUT,"apercu.html"))/1024))
