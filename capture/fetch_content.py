# -*- coding: utf-8 -*-
"""Récupère proprement pages, articles, contenus et médias de BTP Expertise."""
import io, json, os, re, time
import urllib.request, urllib.error

BASE = "https://contactbtpexpertiseriviera-pcoxq.wpcomstaging.com"
ROOT = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
DELAY = 2.5

for d in ("pages", "content", "raw"):
    os.makedirs(os.path.join(ROOT, d), exist_ok=True)

def get(url, tries=4):
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr-FR,fr;q=0.9"})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                w = 20 * (i + 1); print("   429 -> %ss" % w, flush=True); time.sleep(w); continue
            print("   HTTP %s sur %s" % (e.code, url), flush=True); return None
        except Exception as e:
            print("   %s" % e, flush=True); time.sleep(8)
    return None

def api(path):
    return get(BASE + "/index.php?rest_route=" + path)

def collect(kind):
    out, page = [], 1
    while True:
        raw = api("/wp/v2/%s&per_page=100&page=%d" % (kind, page))
        time.sleep(DELAY)
        if not raw:
            break
        try:
            data = json.loads(raw)
        except Exception:
            break
        if not isinstance(data, list) or not data:
            break
        out.extend(data)
        if len(data) < 100:
            break
        page += 1
    return out

print("== Pages ==", flush=True)
pages = collect("pages")
print("== Articles ==", flush=True)
posts = collect("posts")
print("== Medias ==", flush=True)
media = collect("media")

io.open(os.path.join(ROOT, "content", "_pages.json"), "w", encoding="utf-8").write(
    json.dumps(pages, ensure_ascii=False, indent=2))
io.open(os.path.join(ROOT, "content", "_posts.json"), "w", encoding="utf-8").write(
    json.dumps(posts, ensure_ascii=False, indent=2))
io.open(os.path.join(ROOT, "content", "_media.json"), "w", encoding="utf-8").write(
    json.dumps(media, ensure_ascii=False, indent=2))

print("\n%d pages, %d articles, %d medias\n" % (len(pages), len(posts), len(media)), flush=True)

for item in pages + posts:
    slug = item.get("slug") or ("id-%s" % item.get("id"))
    link = item.get("link") or ""
    print("[html] %s -> %s" % (slug, link), flush=True)
    html = get(link)
    if html:
        io.open(os.path.join(ROOT, "pages", slug + ".html"), "w", encoding="utf-8").write(html)
    time.sleep(DELAY)

print("\nFini.", flush=True)
