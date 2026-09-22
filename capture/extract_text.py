# -*- coding: utf-8 -*-
"""Extrait le texte visible de chaque page capturée -> capture/texte/*.txt"""
import io, os, re, html, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "texte")
os.makedirs(OUT, exist_ok=True)

def strip(h):
    h = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?is)<!--.*?-->", " ", h)
    h = re.sub(r"(?i)<(br|/p|/div|/h[1-6]|/li|/tr|/section)[^>]*>", "\n", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    h = html.unescape(h)
    h = re.sub(r"[ \t\xa0]+", " ", h)
    h = re.sub(r"\n\s*\n\s*\n+", "\n\n", h)
    return "\n".join(l.strip() for l in h.split("\n") if l.strip())

for f in sorted(glob.glob(os.path.join(ROOT, "pages", "*.html"))):
    h = io.open(f, encoding="utf-8", errors="replace").read()
    body = re.search(r"(?is)<body[^>]*>(.*)</body>", h)
    txt = strip(body.group(1) if body else h)
    name = os.path.splitext(os.path.basename(f))[0]
    io.open(os.path.join(OUT, name + ".txt"), "w", encoding="utf-8").write(txt)
    print("%-40s %6d caracteres" % (name[:40], len(txt)))
