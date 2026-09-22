# -*- coding: utf-8 -*-
"""Publie le contenu de site/ sur l'hebergement OVH par FTP.

Identifiants lus dans ftp.ini (jamais affiches, jamais versionnes) :

    [ovh]
    hote = ftp.clusterXXX.hosting.ovh.net
    login = btpexpxxx
    motdepasse = ...
    dossier = /www

Usage :
    python publier.py            envoie les fichiers modifies
    python publier.py --tout     renvoie tout, meme l'identique
    python publier.py --essai    n'envoie rien, affiche ce qui serait fait
"""
import configparser
import ftplib
import hashlib
import io
import json
import os
import ssl
import sys

RACINE = os.path.dirname(os.path.abspath(__file__))
LOCAL = os.path.join(RACINE, "site")
CONFIG = os.path.join(RACINE, "ftp.ini")
EMPREINTES = os.path.join(RACINE, ".publie.json")

# Fichiers OVH par defaut a effacer lors de la premiere publication.
PARASITES = ("index.html.ovh", "cgi-bin", ".ovhconfig")

# Pages retirees du site : la generation les efface en local, mais le serveur
# garderait sinon l'ancien fichier, avec ses anciens tarifs.
RETIREES = ("honoraires/index.html",)


def sortie(message):
    print(message, flush=True)


def lire_config():
    if not os.path.exists(CONFIG):
        sortie("Fichier ftp.ini absent. Creez-le a partir de ftp.ini.exemple.")
        sys.exit(1)
    cp = configparser.ConfigParser()
    cp.read(CONFIG, encoding="utf-8")
    if "ovh" not in cp:
        sortie("ftp.ini : la section [ovh] est absente.")
        sys.exit(1)
    s = cp["ovh"]
    manquants = [c for c in ("hote", "login", "motdepasse") if not s.get(c, "").strip()]
    if manquants:
        sortie("ftp.ini : a completer -> " + ", ".join(manquants))
        sys.exit(1)
    return (s["hote"].strip(), s["login"].strip(), s["motdepasse"],
            s.get("dossier", "/www").strip() or "/www")


def empreinte(chemin):
    h = hashlib.md5()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(65536), b""):
            h.update(bloc)
    return h.hexdigest()


def inventaire():
    """Tous les fichiers de site/, en chemins relatifs a separateur /."""
    fichiers = {}
    for dossier, _, noms in os.walk(LOCAL):
        for nom in noms:
            complet = os.path.join(dossier, nom)
            relatif = os.path.relpath(complet, LOCAL).replace("\\", "/")
            fichiers[relatif] = complet
    return fichiers


def connexion(hote, login, motdepasse):
    """FTPS explicite si le serveur l'accepte, FTP simple sinon."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ftp = ftplib.FTP_TLS(context=ctx, timeout=45)
        ftp.connect(hote, 21)
        ftp.login(login, motdepasse)
        ftp.prot_p()
        sortie("Connecte a %s (FTPS, chiffre)" % hote)
    except Exception:
        # L'offre 100M d'OVH n'accepte pas FTPS explicite : on retombe en FTP
        # simple, seul canal disponible sans SSH.
        sortie("FTPS indisponible sur ce serveur, passage en FTP simple.")
        try:
            ftp = ftplib.FTP(timeout=45)
            ftp.connect(hote, 21)
            ftp.login(login, motdepasse)
            sortie("Connecte a %s (FTP)" % hote)
        except ftplib.error_perm as e:
            if "530" in str(e):
                sortie("")
                sortie("Identifiants refuses par OVH (530).")
                sortie("  - Verifiez le login dans OVH > Web Cloud > Hebergements >")
                sortie("    btpexpertise.fr > onglet FTP-SSH, colonne Login.")
                sortie("    Ce n'est pas le nom de domaine : c'est le nom du compte")
                sortie("    d'hebergement, souvent tronque (ex. btpexpe).")
                sortie("  - Si vous venez de changer le mot de passe, OVH met")
                sortie("    quelques minutes a le propager : reessayez plus tard.")
                sys.exit(1)
            raise
    ftp.set_pasv(True)
    return ftp


def assurer_dossier(ftp, chemin, connus):
    """Cree l'arborescence distante au besoin."""
    if not chemin or chemin in connus:
        return
    parent = chemin.rsplit("/", 1)[0] if "/" in chemin else ""
    assurer_dossier(ftp, parent, connus)
    try:
        ftp.mkd(chemin)
    except ftplib.error_perm:
        pass  # existe deja
    connus.add(chemin)


def nettoyer_parasites(ftp, base):
    for nom in PARASITES:
        try:
            ftp.delete(base + "/" + nom)
            sortie("  supprime  %s" % nom)
        except ftplib.all_errors:
            pass


def retirer_pages(ftp, base):
    """Efface les pages retirees du site.

    A chaque publication, et non seulement a la premiere : une page peut
    disparaitre longtemps apres la mise en ligne, et son ancien fichier
    resterait sinon servi avec son contenu perime.
    """
    for nom in RETIREES:
        try:
            ftp.delete(base + "/" + nom)
            sortie("  supprime  %s" % nom)
        except ftplib.all_errors:
            pass


def main():
    tout = "--tout" in sys.argv
    essai = "--essai" in sys.argv

    if not os.path.isdir(LOCAL):
        sortie("Dossier site/ introuvable. Lancez d'abord : python build.py")
        sys.exit(1)

    fichiers = inventaire()
    if not fichiers:
        sortie("Dossier site/ vide.")
        sys.exit(1)

    anciennes = {}
    if os.path.exists(EMPREINTES) and not tout:
        try:
            with io.open(EMPREINTES, encoding="utf-8") as f:
                anciennes = json.load(f)
        except Exception:
            anciennes = {}

    nouvelles = {}
    a_envoyer = []
    for relatif, complet in sorted(fichiers.items()):
        e = empreinte(complet)
        nouvelles[relatif] = e
        if anciennes.get(relatif) != e:
            a_envoyer.append((relatif, complet))

    poids = sum(os.path.getsize(c) for _, c in a_envoyer)
    total = sum(os.path.getsize(c) for c in fichiers.values())
    sortie("%d fichiers dans site/ (%.1f Mo au total)" % (len(fichiers), total / 1048576.0))

    if not a_envoyer and not RETIREES:
        sortie("Rien de nouveau : le site en ligne est deja a jour.")
        return
    if not a_envoyer:
        sortie("Aucun fichier a envoyer ; reste le retrait des pages supprimees.")

    sortie("%d fichier(s) a envoyer (%.1f Mo)" % (len(a_envoyer), poids / 1048576.0))

    if essai:
        for relatif, _ in a_envoyer:
            sortie("  enverrait  %s" % relatif)
        sortie("Essai termine, rien n'a ete envoye.")
        return

    hote, login, motdepasse, base = lire_config()
    base = base.rstrip("/")
    ftp = connexion(hote, login, motdepasse)

    connus = set()
    envoyes = 0
    try:
        if not anciennes:
            nettoyer_parasites(ftp, base)
        retirer_pages(ftp, base)
        for relatif, complet in a_envoyer:
            distant = base + "/" + relatif
            dossier = distant.rsplit("/", 1)[0]
            if dossier != base:
                assurer_dossier(ftp, dossier, connus)
            with open(complet, "rb") as f:
                ftp.storbinary("STOR " + distant, f, blocksize=131072)
            envoyes += 1
            sortie("  [%d/%d] %s" % (envoyes, len(a_envoyer), relatif))
    finally:
        try:
            ftp.quit()
        except ftplib.all_errors:
            ftp.close()

    with io.open(EMPREINTES, "w", encoding="utf-8") as f:
        f.write(json.dumps(nouvelles, indent=1, sort_keys=True))

    sortie("")
    sortie("%d fichier(s) publie(s)." % envoyes)
    sortie("Le site est en ligne sur https://btpexpertise.fr/")


if __name__ == "__main__":
    main()
