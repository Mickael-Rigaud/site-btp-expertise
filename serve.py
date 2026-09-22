# -*- coding: utf-8 -*-
"""Serveur local de previsualisation : python serve.py [port]"""
import functools, mimetypes, os, sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

for ext, mime in ((".webp", "image/webp"), (".svg", "image/svg+xml"),
                  (".mp4", "video/mp4"), (".json", "application/json"),
                  (".woff2", "font/woff2")):
    mimetypes.add_type(mime, ext)


class Handler(SimpleHTTPRequestHandler):
    """Sert le site sans cache : chaque rechargement montre la derniere version."""

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        SimpleHTTPRequestHandler.end_headers(self)


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8123
racine = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
handler = functools.partial(Handler, directory=racine)
# ThreadingHTTPServer : la video du hero garde sa connexion ouverte en permanence.
# Avec un serveur mono-thread elle bloque tout le reste (images, CSS, pages).
serveur = ThreadingHTTPServer(("127.0.0.1", port), handler)
serveur.daemon_threads = True
print("Site servi sur http://127.0.0.1:%d/ depuis %s" % (port, racine), flush=True)
serveur.serve_forever()
