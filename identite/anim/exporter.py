# -*- coding: utf-8 -*-
"""Assemble les PNG rendus en MP4 (large et carre) et en GIF.

    python exporter.py                 # tous les scenarios deja rendus
    python exporter.py inspection      # un seul

Les images doivent avoir ete produites avant, par :
    python rendu.py frames                    -> frames/
    python rendu-loupe.py <scenario> frames   -> frames-<scenario>/
"""
import os, shutil, subprocess, sys

ICI = os.path.dirname(os.path.abspath(__file__))
SCENARIOS = {
    "construction": "frames",
    "balayage": "frames-balayage",
    "inspection": "frames-inspection",
    "mise-au-point": "frames-mise-au-point",
}


def ffmpeg():
    trouve = shutil.which("ffmpeg")
    if trouve: return trouve
    # installation par winget, hors du PATH
    base = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")
    for racine, _, fichiers in os.walk(base):
        if "ffmpeg.exe" in fichiers:
            return os.path.join(racine, "ffmpeg.exe")
    raise SystemExit("ffmpeg est introuvable")


FF = ffmpeg()


def lance(args):
    subprocess.run([FF, "-y", "-loglevel", "error"] + args, check=True)


def exporte(nom, dossier):
    d = os.path.join(ICI, dossier)
    if not os.path.isdir(d):
        print("%-14s pas d'images rendues" % nom); return
    entree = ["-framerate", "30", "-i", os.path.join(d, "f%04d.png")]
    suffixe = "" if nom == "construction" else "-" + nom
    large = os.path.join(ICI, "logo-anime%s.mp4" % suffixe)
    carre = os.path.join(ICI, "logo-anime%s-carre.mp4" % suffixe)
    gif = os.path.join(ICI, "logo-anime%s.gif" % suffixe)
    lance(entree + ["-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "18",
                    "-movflags", "+faststart", large])
    lance(entree + ["-vf", "scale=900:841,pad=1080:1080:90:120:white,format=yuv420p",
                    "-c:v", "libx264", "-crf", "18", "-movflags", "+faststart", carre])
    lance(entree + ["-vf",
                    "fps=20,scale=640:-1:flags=lanczos,split[a][b];"
                    "[a]palettegen=max_colors=96[p];"
                    "[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle",
                    "-loop", "0", gif])
    print("%-14s %5.2f Mo  %5.2f Mo  %5.2f Mo" % (
        nom, *(os.path.getsize(f) / 1048576 for f in (large, carre, gif))))


if __name__ == "__main__":
    demandes = [a for a in sys.argv[1:] if a in SCENARIOS] or list(SCENARIOS)
    print("%-14s %8s %9s %9s" % ("", "mp4", "carre", "gif"))
    for nom in demandes:
        exporte(nom, SCENARIOS[nom])
