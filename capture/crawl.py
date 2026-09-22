# -*- coding: utf-8 -*-
"""Capture lente et polie du site WordPress.com de BTP Expertise."""
import io, json, os, re, sys, time
import urllib.request, urllib.error
from urllib.parse import urljoin, urlparse, urldefrag

BASE = "https://contactbtpexpertiseriviera-pcoxq.wpcomstaging.com"
HOST = urlparse(BASE).netloc
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
DELAY = 2.5

SKIP = re.compile(r"(/wp-admin|/wp-login|\?feed=|/feed/?$|\?replytocom|\?share=|#|/comment-page|"
                  r"\.(png|jpe?g|gif|svg|webp|css|js|ico|woff2?|ttf|pdf|zip|mp4)$)", re.I)

def fetch(url, tries=4):
    for i in range(tries):
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9",
        })
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 15 * (i + 1)
                print("   429 -> pause %ss" % wait, flush=True)
                time.sleep(wait)
                continue
            return e.code, ""
        except Exception as e:
            print("   erreur %s" % e, flush=True)
            time.sleep(8)
    return 429, ""

def slugify(url):
    p = urlparse(url).path.strip("/")
    return (p.replace("/", "__") or "index") + ".html"

seen, queue, index = set(), [BASE + "/"], []
while queue:
    url = urldefrag(queue.pop(0))[0].rstrip("/") + "/"
    if url in seen:
        continue
    seen.add(url)
    status, html = fetch(url)
    print("[%s] %s (%d o)" % (status, url, len(html)), flush=True)
    if status != 200 or not html:
        index.append({"url": url, "status": status, "file": None})
        time.sleep(DELAY)
        continue
    name = slugify(url)
    io.open(os.path.join(OUT, name), "w", encoding="utf-8").write(html)
    title = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    index.append({"url": url, "status": status, "file": name,
                  "title": (title.group(1).strip() if title else "")})
    for href in re.findall(r'href=["\']([^"\']+)["\']', html):
        u = urljoin(url, href)
        if urlparse(u).netloc == HOST and not SKIP.search(u) and urldefrag(u)[0].rstrip("/") + "/" not in seen:
            queue.append(u)
    time.sleep(DELAY)

io.open(os.path.join(OUT, "_index.json"), "w", encoding="utf-8").write(
    json.dumps(index, ensure_ascii=False, indent=2))
print("\nTerminé : %d URLs" % len(index))
