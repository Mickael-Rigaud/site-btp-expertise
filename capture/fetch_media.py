# -*- coding: utf-8 -*-
"""Télécharge tous les médias du site dans capture/assets/."""
import io, json, os, time
import urllib.request, urllib.error
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

media = json.load(io.open(os.path.join(ROOT, "content", "_media.json"), encoding="utf-8"))
manifest = []
for i, m in enumerate(media, 1):
    url = m.get("source_url")
    if not url:
        continue
    name = os.path.basename(urlparse(url).path)
    dest = os.path.join(ASSETS, name)
    entry = {"id": m.get("id"), "file": name, "url": url,
             "title": (m.get("title") or {}).get("rendered", ""),
             "alt": m.get("alt_text", ""), "mime": m.get("mime_type", "")}
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        entry["status"] = "deja"
        manifest.append(entry); continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        io.open(dest, "wb").write(data)
        entry["status"] = "ok"; entry["size"] = len(data)
        print("[%3d/%d] %s (%d o)" % (i, len(media), name, len(data)), flush=True)
    except Exception as e:
        entry["status"] = "erreur: %s" % e
        print("[%3d/%d] ECHEC %s : %s" % (i, len(media), name, e), flush=True)
    manifest.append(entry)
    time.sleep(1.2)

io.open(os.path.join(ROOT, "content", "_media_manifest.json"), "w", encoding="utf-8").write(
    json.dumps(manifest, ensure_ascii=False, indent=2))
ok = sum(1 for x in manifest if x["status"] in ("ok", "deja"))
print("\n%d/%d medias recuperes." % (ok, len(manifest)), flush=True)
