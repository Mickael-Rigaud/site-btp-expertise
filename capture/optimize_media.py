# -*- coding: utf-8 -*-
"""Optimise les medias reellement utilises -> site/assets/"""
import io, json, os, re, glob, subprocess, sys
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "capture", "assets")
IMG = os.path.join(ROOT, "site", "assets", "img")
VID = os.path.join(ROOT, "site", "assets", "video")
for d in (IMG, VID):
    os.makedirs(d, exist_ok=True)

man = json.load(io.open(os.path.join(ROOT, "capture", "content", "_media_manifest.json"), encoding="utf-8"))
blob = ""
for f in glob.glob(os.path.join(ROOT, "capture", "pages", "*.html")) + \
         glob.glob(os.path.join(ROOT, "capture", "raw", "wp-content__uploads__elementor__css__*.html")):
    blob += io.open(f, encoding="utf-8", errors="replace").read()

MAXW = 1920
report, tot_in, tot_out = [], 0, 0

for m in man:
    name = m["file"]
    base, ext = os.path.splitext(name)
    if base not in blob:
        continue
    src = os.path.join(SRC, name)
    if not os.path.exists(src):
        continue
    size_in = os.path.getsize(src)
    tot_in += size_in
    e = ext.lower()
    try:
        if e in (".jpg", ".jpeg", ".png", ".webp"):
            im = Image.open(src)
            if im.mode in ("P", "LA"):
                im = im.convert("RGBA")
            elif im.mode == "CMYK":
                im = im.convert("RGB")
            if im.width > MAXW:
                im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
            dest = os.path.join(IMG, base + ".webp")
            im.save(dest, "WEBP", quality=82, method=6)
            kind = "image"
        elif e == ".svg":
            dest = os.path.join(IMG, name)
            io.open(dest, "wb").write(io.open(src, "rb").read())
            kind = "svg"
        elif e == ".mp4":
            dest = os.path.join(VID, base + ".mp4")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src,
                            "-vf", "scale='min(1280,iw)':-2", "-c:v", "libx264", "-crf", "27",
                            "-preset", "slow", "-movflags", "+faststart",
                            "-c:a", "aac", "-b:a", "96k", dest], check=True)
            kind = "video"
        else:
            dest = os.path.join(IMG, name)
            io.open(dest, "wb").write(io.open(src, "rb").read())
            kind = "autre"
    except Exception as exc:
        print("ECHEC %s : %s" % (name, exc), flush=True)
        continue
    size_out = os.path.getsize(dest)
    tot_out += size_out
    report.append({"source": name, "sortie": os.path.basename(dest), "type": kind,
                   "octets_avant": size_in, "octets_apres": size_out,
                   "alt": m.get("alt", ""), "titre": m.get("title", "")})
    print("%-9s %7.2f Mo -> %6.2f Mo  %s" % (kind, size_in/1048576, size_out/1048576, os.path.basename(dest)), flush=True)

io.open(os.path.join(ROOT, "site", "assets", "_optimisation.json"), "w", encoding="utf-8").write(
    json.dumps(report, ensure_ascii=False, indent=2))
print("\n%d fichiers : %.1f Mo -> %.1f Mo (%.0f %% economises)" % (
    len(report), tot_in/1048576, tot_out/1048576,
    100 * (1 - tot_out/tot_in) if tot_in else 0), flush=True)
