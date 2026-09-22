# -*- coding: utf-8 -*-
"""Controle du site genere : liens, ressources, balises SEO."""
import io, os, re, json, urllib.request, urllib.error
from urllib.parse import urljoin, urlparse

BASE = "http://127.0.0.1:8124"
RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")

pages, erreurs, avertissements = [], [], []

for dossier, _, fichiers in os.walk(RACINE):
    if "assets" in dossier.replace(RACINE, ""):
        continue
    for f in fichiers:
        if f.endswith(".html"):
            chemin = os.path.join(dossier, f)
            url = "/" + os.path.relpath(chemin, RACINE).replace("\\", "/")
            url = url.replace("/index.html", "/")
            pages.append((url, chemin))

print("%d pages HTML\n" % len(pages))

liens_internes, ressources = set(), set()

for url, chemin in sorted(pages):
    h = io.open(chemin, encoding="utf-8").read()

    titre = re.search(r"<title>(.*?)</title>", h, re.S)
    desc = re.search(r'<meta name="description" content="(.*?)">', h, re.S)
    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    canon = re.search(r'<link rel="canonical" href="(.*?)">', h)

    t = titre.group(1) if titre else ""
    d = desc.group(1) if desc else ""

    if not t:
        erreurs.append("%s : pas de <title>" % url)
    elif len(t) > 70:
        avertissements.append("%s : title de %d caracteres (>70)" % (url, len(t)))
    if not d:
        erreurs.append("%s : pas de meta description" % url)
    elif not (110 <= len(d) <= 175):
        avertissements.append("%s : description de %d caracteres (viser 120-165)" % (url, len(d)))
    if len(h1) != 1:
        erreurs.append("%s : %d balises h1" % (url, len(h1)))
    if not canon:
        erreurs.append("%s : pas de canonical" % url)

    for bloc in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            json.loads(bloc)
        except Exception as e:
            erreurs.append("%s : JSON-LD invalide (%s)" % (url, e))

    for href in re.findall(r'href="(/[^"#?]*)"', h):
        liens_internes.add(href)
    for src in re.findall(r'src="(/[^"?]*)"', h):
        ressources.add(src)

    if "A COMPLETER" in h or "À COMPLÉTER" in h:
        avertissements.append("%s : contient des champs a completer" % url)
    for mot in ("Riviera", "11 rue adresse", "Ajoutez votre titre"):
        if mot in re.sub(r'src="[^"]*"', "", h):
            avertissements.append("%s : contient encore \"%s\"" % (url, mot))

def verifie_url(u):
    try:
        req = urllib.request.Request(BASE + u, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0

print("Liens internes : %d" % len(liens_internes))
for u in sorted(liens_internes):
    code = verifie_url(u)
    if code != 200:
        erreurs.append("lien mort %s -> HTTP %s" % (u, code))

print("Ressources     : %d" % len(ressources))
for u in sorted(ressources):
    code = verifie_url(u)
    if code != 200:
        erreurs.append("ressource manquante %s -> HTTP %s" % (u, code))

print()
if erreurs:
    print("ERREURS (%d)" % len(erreurs))
    for e in erreurs:
        print("   " + e)
else:
    print("Aucune erreur bloquante.")
print()
if avertissements:
    print("A VERIFIER (%d)" % len(avertissements))
    for a in avertissements:
        print("   " + a)
