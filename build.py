# -*- coding: utf-8 -*-
"""
Générateur du site statique BTP Expertise.

    python build.py

Produit l'ensemble du site dans site/ à partir des textes de contenu.py.
Les fichiers site/assets/ (CSS, JS, images, vidéos) ne sont pas touchés.
"""

import hashlib
import io
import json
import os
import re
import shutil

from carte_donnees import CARTE_VIEWBOX, CARTE_COMMUNES, CARTE_VILLES
from contenu import (
    SITE, DESCRIPTION_COURTE, DESCRIPTION_PIED, PAIEMENT, IA, VILLES_06, VILLES_83, EXPERTISES, RAISONS,
    COMPETENCES, FAQ, TYPES_DEMANDE, BESOINS_DEMANDE, DEMANDES_PAR_BESOIN, PROBLEMATIQUES, TYPES_BIEN,
    ARTICLES, LEGAL,
    FORMATS_RDV,
    AMO, AMO_TITRE, AMO_ACCROCHE, AMO_PRINCIPE,
    HERO, BESOINS, REASSURANCE, ENGAGEMENT, AMO_PROJETS, VILLES_PRIORITAIRES,
    PARCOURS, PARCOURS_TITRE, PARCOURS_CHAPO, PARCOURS_PIED,
    HONORAIRES_MENTION, AMO_MENTION, HONORAIRES_ACCUEIL,
    RESEAU_CHAPO, RESEAU_PROFILS, RESEAU_DEPARTEMENTS, RESEAU_EXPERIENCE,
)

# Les articles marqués "brouillon" ne sont ni générés, ni listés, ni annoncés
# dans le plan du site : ils restent sur le poste tant qu'ils ne sont pas
# validés, même si le site est publié entre-temps.
ARTICLES_PUBLIES = [a for a in ARTICLES if not a.get("brouillon")]


RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "site")

ADRESSE_COMPLETE = "%s, %s %s" % (SITE["adresse_rue"], SITE["adresse_cp"], SITE["adresse_ville"])

# Ce que le pied de page annonce à la place de l'adresse : le cabinet se
# déplace, il ne reçoit pas.
ZONE_PIED = "Nice — Alpes-Maritimes (06) et Var (83)"

LOGO = "logo-btp-expertise-v2.webp"
ICONE = "icone-v2-512.webp"
ICONE_TOUCH = "icone-v2-180.webp"
IMAGE_CTA = "Expertise-batiment-PACA.webp"


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

# Ordre repris du cahier des charges. « Honoraires » et « Rejoignez-nous »
# viendront s'intercaler quand les pages existeront (lot 4).
NAV = [
    ("Expertises", "/expertises/"),
    ("AMO", "/amo/"),
    ("Zones d’intervention", "/zones-intervention/"),
    ("Le cabinet", "/qui-sommes-nous/"),
    ("Conseils", "/conseils/"),
    ("FAQ", "/faq/"),
    ("Rejoignez-nous", "/rejoignez-nous/"),
]

# Repris dans le pied de page, en complement du menu.
NAV_PIED = [
    ("Prendre rendez-vous", "/contact/"),
    ("Nos tarifs", "/reglement/"),
    ("Règlement de mon dossier", "/reglement/"),
]

# Lien mis en avant à droite du menu, à côté de « Demander une étude »
LIEN_REGLEMENT = ("Règlement", "/reglement/")


# ---------------------------------------------------------------------------
# Briques communes
# ---------------------------------------------------------------------------

def version(chemin):
    """Ajoute une empreinte du fichier a son adresse, pour que le navigateur
    recharge la feuille de style ou le script des qu'ils changent."""
    absolu = os.path.join(SORTIE, chemin.lstrip("/"))
    if os.path.exists(absolu):
        empreinte = hashlib.md5(io.open(absolu, "rb").read()).hexdigest()[:8]
        return "%s?v=%s" % (chemin, empreinte)
    return chemin


def img(fichier, alt, classe="", lazy=True, largeur=None, hauteur=None):
    attrs = ['src="/assets/img/%s"' % fichier, 'alt="%s"' % alt]
    if classe:
        attrs.append('class="%s"' % classe)
    if largeur:
        attrs.append('width="%s"' % largeur)
    if hauteur:
        attrs.append('height="%s"' % hauteur)
    attrs.append('loading="%s"' % ("lazy" if lazy else "eager"))
    attrs.append('decoding="async"')
    return "<img %s>" % " ".join(attrs)


def carte_conseil(a):
    """Carte d'article : image en haut, texte dessous."""
    return """      <a class="carte-conseil" href="/conseils/%s/">
        <div class="carte-conseil__media">%s</div>
        <div class="carte-conseil__corps">
          <p class="article__meta">%s</p>
          <h3>%s</h3>
          <p>%s</p>
          <span class="carte__lien">Lire la suite</span>
        </div>
      </a>""" % (a["slug"],
                 img(a["image"], a["titre_court"], largeur=420, hauteur=262),
                 a["date_affichee"], a["titre"], a["resume"])


def entete_bloc(kicker, titre, chapo=None, gauche=False):
    """En-tete de section : petit intitule, titre, et chapo facultatif."""
    classe = "entete-bloc entete-bloc--gauche" if gauche else "entete-bloc"
    morceaux = ['<span class="kicker">%s</span>' % kicker,
                '<h2 class="titre-section">%s</h2>' % titre]
    if chapo:
        morceaux.append('<p class="chapo">%s</p>' % chapo)
    return '<div class="%s">\n      %s\n    </div>' % (classe, "\n      ".join(morceaux))


def entete(url_courante):
    liens = []
    for libelle, url in NAV:
        courant = ' aria-current="page"' if url == url_courante else ""
        liens.append('<a href="%s"%s>%s</a>' % (url, courant, libelle))
    return """  <header class="entete">
    <div class="entete__carte">
      <a class="entete__logo" href="/" aria-label="BTP Expertise, retour à l’accueil">
        %s
      </a>
      <nav class="nav" id="navigation" data-ouvert="false" aria-label="Navigation principale">
        %s
        <a class="nav__reglement" href="/reglement/">Règlement de mon dossier</a>
        <a class="bouton nav__action" href="/contact/">Demander une étude</a>
      </nav>
      <div class="entete__actions">
        <a class="bouton bouton--bleu" href="%s">%s</a>
        <a class="bouton" href="/contact/">Demander une étude</a>
        <button class="burger" type="button" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="navigation"><span></span></button>
      </div>
    </div>
  </header>""" % (
        img(LOGO, "BTP Expertise, expertise bâtiment et assistance à maîtrise d’ouvrage",
            lazy=False, largeur=900, hauteur=733),
        "\n        ".join(liens),
        LIEN_REGLEMENT[1], LIEN_REGLEMENT[0],
    )


def lignes_societe():
    """Lignes du tableau des mentions legales propres a une societe.

    Vides tant que l'activite est exercee en entreprise individuelle : il suffit
    de renseigner "capital" et "rcs" dans LEGAL pour qu'elles apparaissent.
    """
    lignes = []
    if LEGAL.get("capital", "").strip():
        lignes.append("            <tr><th>Capital social</th><td>%s</td></tr>"
                      % LEGAL["capital"].strip())
    if LEGAL.get("rcs", "").strip():
        lignes.append("            <tr><th>Immatriculation</th><td>%s</td></tr>"
                      % LEGAL["rcs"].strip())
    return "".join(l + "\n" for l in lignes)


def clause_assurance():
    """Article 12 des CGV, accordé à la réalité du contrat.

    Les CGV sont contractuelles : tant qu'aucune police n'est souscrite, elles
    ne peuvent pas affirmer que le cabinet est assuré. La clause se remet
    d'elle-même en affirmatif dès que LEGAL["assurance_contrat"] est renseigné.
    """
    plafond = ("Sa responsabilité ne peut excéder, sauf faute lourde, le montant "
               "des honoraires perçus au titre de la mission concernée.")

    if not LEGAL.get("assurance_contrat"):
        return ("La souscription d’une assurance de responsabilité civile "
                "professionnelle est en cours ; ses références seront publiées "
                "dans les <a href=\"/mentions-legales/\">mentions légales</a> dès "
                "son entrée en vigueur. " + plafond)

    return ("Le cabinet est titulaire d’une assurance de responsabilité civile "
            "professionnelle dont les références figurent dans les "
            "<a href=\"/mentions-legales/\">mentions légales</a>. Sa responsabilité "
            "est plafonnée aux montants garantis par ce contrat et ne peut excéder, "
            "sauf faute lourde, le montant des honoraires perçus au titre de la "
            "mission concernée.")


def mention_capital():
    """Phrase sur le capital social, adaptee a la forme juridique.

    Uniquement pour une entreprise individuelle, qui n'a pas de capital.
    Pour une societe, le capital est une mention obligatoire : il figure dans
    le tableau via lignes_societe(), et aucune phrase ne le remplace.
    """
    forme = LEGAL.get("forme_juridique", "").lower()
    if "individuelle" not in forme:
        return ""
    return ("        <p>L’activité étant exercée sous forme d’entreprise individuelle, "
            "elle ne dispose pas de capital social.</p>")


def banniere(titre, chapeau, image, alt):
    return """  <section class="banniere">
    <div class="banniere__media">%s</div>
    <div class="banniere__voile"></div>
    <div class="banniere__contenu">
      <h1>%s</h1>
      <p>%s</p>
    </div>
  </section>""" % (img(image, alt, lazy=False, largeur=1920, hauteur=1080), titre, chapeau)


def bandeau_appel(titre=None, texte=None):
    titre = titre or "Un accompagnement technique pour vos travaux"
    texte = texte or ("Nous vous accompagnons dans le suivi, la coordination et la bonne "
                      "réalisation de vos travaux afin de garantir le bon déroulement de "
                      "votre chantier.")
    return """  <section class="appel">
    <div class="appel__media">%s</div>
    <div class="appel__voile"></div>
    <div class="appel__contenu">
      <h2>%s</h2>
      <p>%s</p>
      <div class="appel__actions">
        <a class="bouton" href="/contact/">Parlez-nous de votre projet</a>
        <a class="bouton bouton--contour bouton--appel" href="tel:%s">Appelez-nous</a>
      </div>
    </div>
  </section>""" % (img(IMAGE_CTA, "Expertise en bâtiment en région PACA", largeur=1920, hauteur=1080),
                   titre, texte, SITE["telephone_lien"])


def pied():
    return """  <footer class="pied">
    <div class="pied__interieur">
      <div class="pied__logo">%s</div>
      <p class="pied__phrase">%s</p>
      <ul class="pied__contact">
        <li>%s</li>
        <li><a href="tel:%s">Appelez-nous</a></li>
        <li><a href="mailto:%s">%s</a></li>
        <li>%s</li>
      </ul>
      <ul class="pied__secondaire">
%s
      </ul>
    </div>
    <div class="pied__bas">
      <span>&copy; 2026 BTP Expertise — Expertise bâtiment et assistance à maîtrise d’ouvrage, Alpes-Maritimes et Var.</span>
      <ul>
        <li><a href="/mentions-legales/">Mentions légales</a></li>
        <li><a href="/conditions-generales-de-vente/">CGV</a></li>
        <li><a href="/politique-de-confidentialite/">Politique de confidentialité</a></li>
      </ul>
    </div>
  </footer>""" % (
        img(LOGO, "BTP Expertise", largeur=900, hauteur=733),
        DESCRIPTION_PIED,
        # Le siège est une domiciliation : personne n'y reçoit. L'afficher à
        # côté du téléphone et des horaires laissait croire à un bureau où se
        # rendre. L'adresse complète reste dans les mentions légales, où elle
        # est obligatoire.
        ZONE_PIED,
        SITE["telephone_lien"],
        SITE["email"], SITE["email"],
        SITE["horaires"],
        "\n".join('        <li><a href="%s">%s</a></li>' % (u, t) for t, u in NAV_PIED),
    )


# ---------------------------------------------------------------------------
# Données structurées
# ---------------------------------------------------------------------------

def jsonld_cabinet():
    return {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "@id": SITE["url"] + "/#cabinet",
        "name": SITE["nom"],
        "description": DESCRIPTION_COURTE.replace("&amp;", "&"),
        "url": SITE["url"] + "/",
        "telephone": SITE["telephone_lien"],
        "email": SITE["email"],
        "image": SITE["url"] + "/assets/img/" + LOGO,
        "logo": SITE["url"] + "/assets/img/" + LOGO,
        "priceRange": "$$",
        "founder": {"@type": "Person", "name": SITE["fondateur"]},
        "vatID": LEGAL["tva"],
        # Pas de "streetAddress" : le siège est une domiciliation, le cabinet
        # se déplace et ne reçoit pas. Déclarer une rue à Google contredirait
        # la fiche d'établissement, créée en zone de chalandise sans adresse
        # visible. La ville et la région suffisent au référencement local ;
        # c'est "areaServed", plus bas, qui porte le périmètre réel.
        "address": {
            "@type": "PostalAddress",
            "postalCode": SITE["adresse_cp"],
            "addressLocality": SITE["adresse_ville"],
            "addressRegion": "Provence-Alpes-Côte d’Azur",
            "addressCountry": "FR",
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": SITE["latitude"],
            "longitude": SITE["longitude"],
        },
        "areaServed": (
            [{"@type": "AdministrativeArea", "name": "Alpes-Maritimes (06)"},
             {"@type": "AdministrativeArea", "name": "Var (83)"}]
            + [{"@type": "City", "name": v.split(" – ")[0]} for v in VILLES_06 + VILLES_83]
        ),
        "knowsAbout": [
            "Expertise bâtiment", "Fissures et désordres structurels",
            "Infiltrations et étanchéité", "Malfaçons et non-conformités",
            "Expertise avant achat immobilier", "Réception de travaux",
            "Assistance à maîtrise d’ouvrage", "Retrait-gonflement des argiles",
        ],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Prestations d’expertise en bâtiment",
            "itemListElement": [
                {"@type": "Offer",
                 "itemOffered": {"@type": "Service",
                                 "name": e["titre"].replace("&amp;", "&"),
                                 "description": e["resume"]}}
                for e in EXPERTISES
            ],
        },
    }


def jsonld_fil(elements):
    items = [{"@type": "ListItem", "position": 1, "name": "Accueil", "item": SITE["url"] + "/"}]
    for i, (libelle, url) in enumerate(elements, start=2):
        item = {"@type": "ListItem", "position": i, "name": libelle}
        if url:
            item["item"] = SITE["url"] + url
        items.append(item)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


# ---------------------------------------------------------------------------
# Gabarit de page
# ---------------------------------------------------------------------------

GABARIT = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titre}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonique}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="BTP Expertise">
<meta name="geo.region" content="FR-PAC">
<meta name="geo.placename" content="Nice, Alpes-Maritimes">
<meta name="geo.position" content="{lat};{lon}">
<meta name="ICBM" content="{lat}, {lon}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="BTP Expertise">
<meta property="og:locale" content="fr_FR">
<meta property="og:title" content="{titre}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonique}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{titre}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image}">
<meta name="theme-color" content="#262C42">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/assets/img/{icone}" type="image/webp">
<link rel="apple-touch-icon" href="/assets/img/{icone_touch}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&family=Poppins:wght@300;400;500&family=Roboto:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css}">
{prechargement}
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<a class="sr-only" href="#contenu">Aller au contenu principal</a>
{entete}
<main id="contenu">
{corps}
</main>
{pied}
<script src="{js}" defer></script>
</body>
</html>
"""


def page(chemin, titre, description, corps, url, jsonld=None, fil=None,
         og_image=None, og_type="website", prechargement=""):
    blocs = [jsonld_cabinet()]
    if fil:
        blocs.append(jsonld_fil(fil))
    if jsonld:
        blocs.append(jsonld)
    donnees = blocs[0] if len(blocs) == 1 else {"@context": "https://schema.org", "@graph": blocs}

    html = GABARIT.format(
        titre=titre,
        description=description,
        canonique=SITE["url"] + url,
        lat=SITE["latitude"], lon=SITE["longitude"],
        og_type=og_type,
        og_image=og_image or (SITE["url"] + "/assets/img/BTP-Expertise-RIviera-Nice.webp"),
        logo=LOGO,
        icone=ICONE,
        icone_touch=ICONE_TOUCH,
        prechargement=prechargement,
        jsonld=json.dumps(donnees, ensure_ascii=False, separators=(",", ":")),
        entete=entete(url),
        corps=corps,
        pied=pied(),
        css=version("/assets/css/style.css"),
        js=version("/assets/js/site.js"),
    )

    dossier = os.path.join(SORTIE, chemin)
    if not os.path.isdir(dossier):
        os.makedirs(dossier)
    io.open(os.path.join(dossier, "index.html"), "w", encoding="utf-8").write(html)
    return url


PAGES = []


# ---------------------------------------------------------------------------
# Accueil
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Parcours en deux colonnes : pictogrammes
# ---------------------------------------------------------------------------
# Tracés SVG inline : pas de requête réseau, et la couleur suit celle du texte
# (currentColor), donc bleu côté expertise et orange côté AMO.

PICTOS = {
    "loupe": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "casque": '<path d="M3 16a9 9 0 0 1 18 0"/><path d="M2 16h20v2H2z"/><path d="M9 8.5V5.5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3"/>',
    "dialogue": '<path d="M3 6a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2H8l-4 3V6z"/>'
                '<path d="M18 9h1a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-1l-3 3v-3"/>',
    "liste": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/>',
    "maison": '<path d="M4 11 12 4l8 7"/><path d="M6 10v9h12v-9"/><path d="M10 19v-5h4v5"/>',
    "diagnostic": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>'
                  '<path d="M8 11h1.6l1.2-2.4 1.6 4.4 1.2-2h1.4"/>',
    "rapport": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/><path d="M9 12h6M9 16h6"/>',
    "personnes": '<circle cx="9" cy="9" r="3"/><path d="M3 19a6 6 0 0 1 12 0"/>'
                 '<path d="M16 7.5a2.8 2.8 0 0 1 0 5.4"/><path d="M17 15.5a5.5 5.5 0 0 1 4 3.5"/>',
    "poignee": '<path d="M3 12 7 8l3 2.5L13 8l4 4"/><path d="m11 15 2 2 3-2 2 1.5"/>'
               '<path d="M2 10h2M20 10h2"/>',
    "cible": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3.5"/>'
             '<path d="M12 4V2M12 22v-2M4 12H2M22 12h-2"/>',
    "calcul": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8"/>'
              '<path d="M9 12h.01M12 12h.01M15 12h.01M9 16h.01M12 16h.01M15 16h.01"/>',
    "balance": '<path d="M12 4v16M7 20h10"/><path d="M5 8h14"/>'
               '<path d="m5 8-2.5 5h5zM19 8l-2.5 5h5z"/>',
    "presse-papier": '<rect x="6" y="4" width="12" height="17" rx="2"/>'
                     '<path d="M9 4V3h6v1"/><path d="m9.5 12 1.8 1.8L15 10"/>',
    "crayon": '<path d="M5 19h4l10-10a2.1 2.1 0 0 0-3-3L6 16v3z"/><path d="m14 6 3 3"/>',
    "valide": '<circle cx="12" cy="12" r="8.5"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    # Pictogrammes des dix missions d'expertise
    "loupe-defaut": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>'
                    '<path d="M11 7.5v4M11 14.3v.2"/>',
    "fissure": '<rect x="4" y="3" width="16" height="18" rx="2"/>'
               '<path d="M13 3.5 10.5 9l3 2.5-2 4 2.2 2.2-1.2 3.6"/>',
    "goutte": '<path d="M12 3.5c3.2 3.6 5.5 6.4 5.5 9a5.5 5.5 0 0 1-11 0c0-2.6 2.3-5.4 5.5-9z"/>'
              '<path d="M9.5 13.2a2.7 2.7 0 0 0 2.2 3.1"/>',
    "robinet": '<path d="M4 13h6v3H4z"/><path d="M10 14.5h4a3 3 0 0 0 3-3V8"/>'
               '<path d="M14.5 5.5h5M17 5.5v2.5"/><path d="M7 16v4"/>',
    "eclair": '<path d="M13.5 3 6 13.5h5L10 21l7.5-10.5h-5z"/>',
    "cles": '<circle cx="8" cy="14" r="4"/><path d="m11 11 8-8"/>'
            '<path d="m16.5 5.5 2 2M19 3l2 2"/>',
}


def picto(nom, taille=24):
    """Pictogramme SVG en trait, décoratif (invisible pour les lecteurs d'écran)."""
    return ('<svg class="picto" width="%d" height="%d" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true" focusable="false">%s</svg>'
            % (taille, taille, PICTOS.get(nom, "")))


def parcours_double():
    """Les deux parcours cote a cote, repris du visuel de Mickael Rigaud."""
    colonnes = []
    for voie in PARCOURS:
        etapes = "\n".join("""          <li class="etape" data-anim>
            <span class="etape__numero">%02d</span>
            <div class="etape__carte">
              <div class="etape__corps">
                <h4 class="etape__titre">%s</h4>
                <p class="etape__texte">%s</p>
              </div>
              <span class="etape__picto">%s</span>
            </div>
          </li>""" % (i + 1, titre, texte, picto(ic))
                           for i, (titre, texte, ic) in enumerate(voie["etapes"]))

        colonnes.append("""      <div class="voie voie--%s">
        <div class="voie__tete" data-anim>
          <span class="voie__pastille">%s</span>
          <div>
            <h3 class="voie__titre">%s</h3>
            <p class="voie__verbes">%s</p>
            <p class="voie__phrase">%s</p>
          </div>
        </div>
        <ol class="voie__etapes">
%s
        </ol>
      </div>""" % (voie["cle"], picto(voie["icone"], 26), voie["titre"],
                   voie["verbes"], voie["phrase"], etapes))

    return """  <section class="section section--gris">
    <div class="conteneur">
      <div class="entete-bloc">
        <h2 class="titre-section">%s</h2>
        <p class="chapo">%s</p>
      </div>
      <div class="parcours-double">
%s
      </div>
      <div class="parcours-pied" data-anim>
        <span class="parcours-pied__bouclier">%s</span>
        <div>
          <p class="parcours-pied__titre">%s</p>
          <p class="parcours-pied__texte">%s</p>
        </div>
      </div>
    </div>
  </section>
""" % (PARCOURS_TITRE, PARCOURS_CHAPO, "\n".join(colonnes),
       '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
       'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
       '<path d="M12 3l7 3v6c0 4-3 7-7 9-4-2-7-5-7-9V6z"/><path d="m9 12 2 2 4-4.5"/></svg>',
       PARCOURS_PIED[0], PARCOURS_PIED[1])


def page_accueil():
    besoins = "\n".join("""        <article class="besoin besoin--%s" data-anim>
          <span class="besoin__intitule">%s</span>
          <h3 class="besoin__metier">%s</h3>
          <p class="besoin__verbes">%s</p>
          <p class="besoin__texte">%s</p>
          <a class="besoin__lien" href="%s">%s <span aria-hidden="true">&rarr;</span></a>
        </article>""" % (b["teinte"], b["besoin"], b["metier"], b["verbes"],
                         b["texte"], b["url"], b["action"]) for b in BESOINS)

    tarifs_resume = "\n".join("""        <article class="tarif-carte" data-anim>
          <span class="tarif-carte__mission">%s</span>
          <span class="tarif-carte__prix">%s</span>
        </article>""" % (m, prix) for m, prix in HONORAIRES_ACCUEIL)

    reassurance = "\n".join("""        <article class="atout" data-anim>
          <h3>%s</h3>
          <p>%s</p>
        </article>""" % (t, d) for t, d in REASSURANCE)

    flips = "\n".join("""        <article class="flip">
          <div class="flip__interieur">
            <div class="flip__face flip__avant">
              %s
              <h3>%s</h3>
            </div>
            <div class="flip__face flip__arriere">
              <p>%s</p>
              <a class="bouton" href="/expertises/#%s">En savoir plus</a>
            </div>
          </div>
        </article>""" % (img(s["icone"], s["titre"].replace("&amp;", "et"), largeur=250, hauteur=250),
                         s["titre"], s["resume"], s["id"])
                      for s in EXPERTISES if s["accueil"])

    raisons = "\n".join("""        <article class="carte carte--gris">
          %s
          <h3>%s</h3>
          <p>%s</p>
        </article>""" % (img(ic, t.replace("&amp;", "et"), classe="carte__icone",
                             largeur=250, hauteur=250), t, d)
                        for t, d, ic in RAISONS)

    competences = "\n".join("""        <article class="competence">
          <div class="competence__media">%s</div>
          <div class="competence__corps">
            <h3>%s</h3>
            <p>%s</p>
          </div>
        </article>""" % (img(i, t.replace("&amp;", "et"), largeur=900, hauteur=675), t, d)
                            for i, t, d in COMPETENCES)

    art = ARTICLES_PUBLIES[0]

    corps = """  <section class="hero">
    <div class="hero__media">
      <video autoplay muted loop playsinline preload="metadata"
             poster="/assets/img/BTP-Expertise-RIviera-Nice.webp"
             aria-hidden="true" tabindex="-1">
        <source src="/assets/video/btp-expertise-riviera-nice-2.mp4" type="video/mp4">
      </video>
    </div>
    <div class="hero__voile"></div>
    <div class="hero__contenu">
      <span class="hero__label">%s</span>
      <h1 class="hero__titre">%s</h1>
      <p class="hero__accroche">%s</p>
      <div class="hero__actions">
        <a class="bouton" href="/expertises/">%s</a>
        <a class="bouton bouton--bleu" href="/amo/">%s</a>
      </div>
      <div class="hero__zones">
        <span>Nice</span><span>Cannes</span><span>Antibes</span><span>Toulon</span><span>Fréjus</span><span>Draguignan</span>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="conteneur">
    %s
      <div class="grille grille--5">
%s
      </div>
    </div>
  </section>

  <section class="section section--besoins">
    <div class="conteneur">
      <div class="besoins">
%s
      </div>
    </div>
  </section>

%s

  <section class="section">
    <div class="conteneur">
    %s
      <div class="atouts">
%s
      </div>
      <p class="engagement" data-anim>%s</p>
    </div>
  </section>

  <section class="section">
    <div class="conteneur">
    %s
      <div class="tarifs-resume">
%s
      </div>
      <div class="centre saut">
        <a class="bouton bouton--bleu" href="/reglement/">Consulter nos tarifs</a>
      </div>
    </div>
  </section>

  <section class="section section--gris">
    <div class="conteneur">
    %s
      <div class="grille grille--4">
%s
      </div>
      <p class="precision-role"><strong>Aucun suivi de chantier, aucune direction de travaux,
      aucune coordination d’entreprises.</strong> Notre rôle est d’observer, d’analyser et de vous
      conseiller : vous restez décisionnaire et contractez directement avec les entreprises.</p>
    </div>
  </section>

%s

  <section class="section">
    <div class="conteneur">
    %s
      <div class="grille grille--3">
%s
      </div>
    </div>
  </section>

%s
""" % (
        HERO["label"], HERO["titre"], HERO["accroche"],
        HERO["action_expertise"], HERO["action_amo"],
        entete_bloc("Expertise bâtiment &amp; AMO",
                    "Cinq missions pour <em>sécuriser</em> votre projet",
                    "Expertise bâtiment et assistance à maîtrise d’ouvrage pour particuliers et professionnels"),
        flips,
        besoins,
        parcours_double(),
        entete_bloc("Pourquoi nous choisir",
                    "Une expertise <em>issue du terrain</em>",
                    "Quatre raisons de nous confier votre dossier."),
        reassurance,
        ENGAGEMENT,
        entete_bloc("Honoraires",
                    "Des tarifs <em>annoncés d’avance</em>",
                    "Un devis précisant le périmètre et le montant est établi avant "
                    "toute intervention."),
        tarifs_resume,
        entete_bloc("Nos compétences",
                    "Les désordres que nous <em>traitons au quotidien</em>"),
        competences,
        carte_zones(lien=True),
        entete_bloc("Nos conseils",
                    "Comprendre les <em>désordres du bâtiment</em>"),
        "\n".join(carte_conseil(a) for a in ARTICLES_PUBLIES[:3]),
        bandeau_appel(),
    )

    PAGES.append(page(
        "",
        "Expert bâtiment Nice, Cannes, Antibes | BTP Expertise",
        "Expert en bâtiment à Nice, Cannes et Antibes : fissures, humidité, "
        "malfaçons, réception de travaux dans le 06 et le 83.",
        corps, "/",
        prechargement='<link rel="preload" as="image" href="/assets/img/BTP-Expertise-RIviera-Nice.webp">',
    ))


# ---------------------------------------------------------------------------
# Qui sommes-nous
# ---------------------------------------------------------------------------

def page_qui_sommes_nous():
    fil = [("Qui sommes-nous", None)]
    corps = """%s

  <section class="section">
    <div class="conteneur">
      <div class="duo">
        <div class="duo__media">%s</div>
        <div class="duo__texte">
          <h2>Une expertise issue du terrain</h2>
          <p>BTP Expertise est un cabinet d’expertise en bâtiment et d’Assistance à Maîtrise d’Ouvrage (AMO), basé à Nice. Nous accompagnons particuliers et professionnels dans l’analyse des désordres du bâtiment ainsi que dans la sécurisation de leurs projets de travaux sur l’ensemble de la Côte d’Azur et plus largement en région Provence-Alpes-Côte d’Azur.</p>
          <p>Le cabinet a été fondé par <strong>%s</strong>, expert en bâtiment issu du terrain et entrepreneur expérimenté dans le secteur de la rénovation.</p>
          <p>Titulaire de formations professionnelles en électricité, plomberie et maçonnerie, il a créé et dirigé une entreprise de rénovation tous corps d’état. Cette expérience opérationnelle lui a permis d’intervenir sur des projets faisant appel à de nombreux corps de métier et de développer une connaissance concrète des techniques de mise en œuvre, des problématiques de chantier, des malfaçons et des désordres pouvant affecter un bâtiment.</p>
          <p>Cette expérience du terrain constitue aujourd’hui le socle de l’approche de BTP Expertise : <strong>observer, comprendre et analyser avant de préconiser</strong>.</p>
          <p>Qu’il s’agisse d’identifier l’origine d’un désordre, d’évaluer la qualité de travaux réalisés ou d’accompagner un maître d’ouvrage dans son projet, notre objectif reste le même : apporter un regard technique indépendant, compréhensible et directement exploitable pour permettre à nos clients de prendre les bonnes décisions.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section section--gris">
    <div class="conteneur">
      <div class="duo duo--inverse">
        <div class="duo__media">%s</div>
        <div class="duo__texte">
          <h2>Nos trois engagements</h2>
          <ul class="liste-check">
            <li><strong>Neutralité</strong> — l’expert n’est le porte-parole de personne. Ni du client, ni de l’assureur, ni de l’entreprise de travaux. Son analyse ne dépend pas de qui la commande.</li>
            <li><strong>La vérité technique du chantier</strong> — ce que nous défendons, c’est l’ouvrage : ce qui a réellement été fait, ce qui est conforme, ce qui ne l’est pas. Un constat qui tient debout devant toutes les parties, y compris devant un juge.</li>
            <li><strong>Rigueur et clarté</strong> — une analyse méthodique appuyée sur les normes, les DTU et les règles de l’art, restituée dans un rapport lisible, avec des préconisations concrètes et un interlocuteur unique.</li>
          </ul>
          <p>Cette neutralité n’est pas une posture : c’est ce qui donne du poids à nos conclusions. Un rapport qui vous donnerait systématiquement raison ne vaudrait rien face à un assureur ou devant un tribunal. C’est parce que notre analyse est indépendante qu’elle protège réellement vos intérêts.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="conteneur">
    %s
      <div class="grille grille--3">
        <article class="carte carte--gris"><h3>Analyse de fissures</h3><p>Détermination de l’origine et de la gravité des fissurations et désordres structurels.</p></article>
        <article class="carte carte--gris"><h3>Expertise après sinistre</h3><p>Dégât des eaux, incendie, sécheresse : constat technique et assistance face à l’assurance.</p></article>
        <article class="carte carte--gris"><h3>Constat de malfaçons</h3><p>Relevé des défauts d’exécution et des non-conformités aux règles de l’art.</p></article>
        <article class="carte carte--gris"><h3>Assistance en cas de litige</h3><p>Appui technique dans les échanges amiables comme dans les procédures.</p></article>
        <article class="carte carte--gris"><h3>Réception de chantier</h3><p>Contrôle de conformité et rédaction des réserves avant validation des travaux.</p></article>
        <article class="carte carte--gris"><h3>Expertise avant achat</h3><p>Évaluation de l’état réel d’un bien avant compromis ou signature.</p></article>
      </div>
      <div class="centre saut"><a class="bouton" href="/zones-intervention/">Voir toutes les villes couvertes</a></div>
    </div>
  </section>

%s
""" % (
        banniere("Qui sommes-nous ?",
                 "Un cabinet d’expertise en bâtiment et d’assistance à maîtrise "
                    "d’ouvrage indépendant, au service des "
                 "particuliers et des professionnels des Alpes-Maritimes et du Var.",
                 "BTP-Expertise-Riviera-Antibes.webp",
                 "Le cabinet BTP Expertise sur la Côte d’Azur"),
        img("Expertise-batiment-a-Antibes-et-Nice.webp",
            "Expertise en bâtiment à Nice et Antibes", largeur=760, hauteur=507),
        SITE["fondateur"],
        img("hand-construction-plans-with-yellow-helmet-drawing-tool.webp",
            "Plans de construction, casque de chantier et outils de traçage", largeur=760, hauteur=507),
        entete_bloc("Nos interventions",
                    "Une connaissance <em>concrète</em> du bâtiment",
                    "Notre double compétence — entrepreneur et expert — nous permet d’apporter un regard "
                    "précis, pragmatique et indépendant sur chaque situation."),
        bandeau_appel(),
    )

    PAGES.append(page(
        "qui-sommes-nous",
        "Le cabinet — Expert bâtiment indépendant à Nice | BTP Expertise",
        "Cabinet d’expertise en bâtiment et d’AMO indépendant basé à Nice, fondé par "
        "Mickael Rigaud. Une expertise issue du terrain, dans le 06 et le 83.",
        corps, "/qui-sommes-nous/", fil=fil,
    ))


# ---------------------------------------------------------------------------
# Expertises
# ---------------------------------------------------------------------------

def page_expertises():
    fil = [("Expertises", None)]

    cartes = []
    for rang, e in enumerate(EXPERTISES, 1):
        points = "\n".join("              <li>%s</li>" % p for p in e["points"])
        avertissement = ""
        if e.get("avertissement"):
            avertissement = ('\n            <p class="expertise__reserve">%s</p>'
                             % e["avertissement"])
        cartes.append("""      <article class="expertise" id="%s" data-anim>
        <div class="expertise__media">
          %s
          <span class="expertise__rang">%02d</span>
        </div>
        <div class="expertise__contenu">
          <div class="expertise__tete">
            <span class="expertise__picto">%s</span>
            <h3 class="expertise__titre">%s</h3>
          </div>
          <p class="expertise__resume">%s</p>
          <ul class="expertise__points">
%s
          </ul>%s
          <a class="expertise__lien" href="/contact/">Demander cette expertise <span aria-hidden="true">&rarr;</span></a>
        </div>
      </article>""" % (e["id"],
                       img(e["image"], e["image_alt"], largeur=900, hauteur=675),
                       rang, picto(e["picto"], 24), e["titre"], e["resume"],
                       points, avertissement))

    corps = """%s

  <section class="section">
    <div class="conteneur">
    %s
      <div class="expertises">
%s
      </div>
    </div>
  </section>

  <section class="section section--gris">
    <div class="conteneur">
      <div class="cadre-amo" data-anim>
        <p class="cadre-amo__intitule">Vous avez un projet plutôt qu’un problème&nbsp;?</p>
        <p class="cadre-amo__texte">Pour la définition de vos travaux, l’analyse des devis et
        le choix des entreprises, découvrez notre mission d’assistance à maîtrise d’ouvrage.</p>
        <a class="bouton bouton--bleu" href="/amo/">Découvrir notre accompagnement AMO</a>
      </div>
    </div>
  </section>

%s
""" % (
        banniere("Nos expertises",
                 "Dix missions pour comprendre, constater et défendre vos intérêts.",
                 "15.webp", "Expertise en bâtiment dans les Alpes-Maritimes et le Var"),
        entete_bloc("Expertise bâtiment",
                    "Comprendre, constater, <em>préconiser</em>",
                    "Fissures, humidité, malfaçons, plomberie, électricité, litiges, réception "
                    "ou projet d’acquisition : BTP Expertise analyse votre situation et vous "
                    "apporte un regard technique indépendant."),
        "\n".join(cartes),
        bandeau_appel(),
    )

    services_jsonld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Missions d’expertise en bâtiment",
        "itemListElement": [
            {"@type": "ListItem", "position": i,
             "item": {"@type": "Service",
                      "name": e["titre"].replace("&amp;", "&"),
                      "description": e["resume"],
                      "url": SITE["url"] + "/expertises/#" + e["id"],
                      "areaServed": ["Alpes-Maritimes", "Var"],
                      "provider": {"@id": SITE["url"] + "/#cabinet"}}}
            for i, e in enumerate(EXPERTISES, 1)
        ],
    }

    PAGES.append(page(
        "expertises",
        "Expertise bâtiment à Nice, Cannes et Antibes | BTP Expertise",
        "Expertise fissures, humidité, malfaçons, plomberie et électricité à Nice, Cannes "
        "et Antibes. Expertise avant achat et assistance à réception dans le 06 et le 83.",
        corps, "/expertises/", jsonld=services_jsonld, fil=fil,
    ))


# ---------------------------------------------------------------------------
# Assistance à Maîtrise d'Ouvrage (AMO)
# ---------------------------------------------------------------------------

def page_amo():
    fil = [(AMO_TITRE, None)]

    missions = "\n".join("""        <article class="mission" data-anim>
          <span class="mission__numero">%02d</span>
          <h3>%s</h3>
          <p>%s</p>
        </article>""" % (i + 1, titre, texte)
                         for i, (titre, texte) in enumerate(AMO))


    projets = "\n".join("""        <figure class="projet" data-anim>
          %s
          <figcaption>
            <span class="projet__titre">%s</span>
            <span class="projet__mission">%s</span>
          </figcaption>
        </figure>""" % (img(fichier, alt, largeur=700, hauteur=470), titre, mission)
                        for fichier, titre, mission, alt in AMO_PROJETS)

    corps = """%s

  <section class="section section--gris">
    <div class="conteneur">
    %s
      <div class="missions">
%s
      </div>
    </div>
  </section>

  <section class="section">
    <div class="conteneur">
    %s
      <div class="projets">
%s
      </div>
    </div>
  </section>

  <section class="section section--nuit">
    <div class="conteneur">
      <div class="decision" data-anim>
        <p class="decision__accroche">Vous restez maître de votre projet</p>
        <p class="decision__texte">%s</p>
        <p class="decision__note">Notre rôle : vous donner les éléments techniques pour
        choisir en connaissance de cause, à chaque étape.</p>
      </div>
    </div>
  </section>

%s
""" % (
        banniere(AMO_TITRE, AMO_ACCROCHE,
                 "Expertise-batiment-PACA.webp",
                 "Assistance à maîtrise d’ouvrage par BTP Expertise en région PACA"),
        entete_bloc("Nos missions",
                    "Vous accompagner à <em>chaque étape</em> de votre projet",
                    "Assistance à maîtrise d’ouvrage à Nice, Cannes, Antibes et dans tout "
                    "le Var : de la définition du besoin à la réception des travaux, nous "
                    "vous apportons un regard technique indépendant pour décider en "
                    "connaissance de cause."),
        missions,
        entete_bloc("Nos interventions",
                    "Des projets que nous <em>accompagnons</em>",
                    "Quelques exemples de projets sur lesquels le cabinet intervient "
                    "en assistance à maîtrise d’ouvrage."),
        projets,
        AMO_PRINCIPE,
        bandeau_appel(),
    )

    PAGES.append(page(
        "amo",
        "AMO Nice — Assistance à maîtrise d’ouvrage | BTP Expertise",
        "Assistance à maîtrise d’ouvrage à Nice, Cannes et Antibes : analyse de devis, choix "
        "des entreprises, accompagnement des travaux et assistance à réception.",
        corps, "/amo/", fil=fil,
    ))


# ---------------------------------------------------------------------------
# Rejoignez-nous : réseau de professionnels indépendants
# ---------------------------------------------------------------------------

def page_reseau():
    fil = [("Rejoignez-nous", None)]

    profils = "\n".join('          <li>%s</li>' % p for p in RESEAU_PROFILS)
    departements = "\n".join(
        """              <label class="case"><input type="checkbox" name="Departements" value="%s"> <span>%s</span></label>"""
        % (d, d) for d in RESEAU_DEPARTEMENTS)
    experience = "\n".join('              <option value="%s">%s</option>' % (e, e)
                           for e in RESEAU_EXPERIENCE)

    corps = """%s

  <section class="section">
    <div class="conteneur">
    %s
      <div class="reseau">
        <div class="reseau__texte">
          <p class="chapo" style="margin-top:0">%s</p>
          <p><strong>Premier échange téléphonique sans engagement.</strong></p>
        </div>
        <div class="reseau__profils">
          <h3>Profils recherchés</h3>
          <ul class="liste-check">
%s
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section class="section section--gris">
    <div class="conteneur">
    %s
      <div class="formulaire-zone">
        <form class="formulaire" id="form-reseau" action="%s" method="POST" data-jeton="%s">
          <div class="formulaire__message" id="reseau-message" role="status" aria-live="polite"></div>

          <div class="champ champ--duo">
            <div class="champ">
              <label for="r-nom">Nom et prénom <span class="obligatoire">*</span></label>
              <input type="text" id="r-nom" required autocomplete="name">
            </div>
            <div class="champ">
              <label for="r-societe">Société <span class="champ__facultatif">(facultatif)</span></label>
              <input type="text" id="r-societe" autocomplete="organization">
            </div>
          </div>

          <div class="champ champ--duo">
            <div class="champ">
              <label for="r-siret">SIRET <span class="champ__facultatif">(facultatif)</span></label>
              <input type="text" id="r-siret" inputmode="numeric" placeholder="14 chiffres">
            </div>
            <div class="champ">
              <label for="r-experience">Années d’expérience <span class="obligatoire">*</span></label>
              <select id="r-experience" required>
                <option value="">Choisissez</option>
%s
              </select>
            </div>
          </div>

          <div class="champ champ--duo">
            <div class="champ">
              <label for="r-telephone">Téléphone <span class="obligatoire">*</span></label>
              <input type="tel" id="r-telephone" required autocomplete="tel">
            </div>
            <div class="champ">
              <label for="r-email">E-mail <span class="obligatoire">*</span></label>
              <input type="email" id="r-email" required autocomplete="email">
            </div>
          </div>

          <div class="champ">
            <label for="r-specialites">Spécialités <span class="obligatoire">*</span></label>
            <input type="text" id="r-specialites" required placeholder="Structure, humidité, thermique, électricité…">
          </div>

          <div class="champ">
            <span class="champ__intitule">Départements d’intervention <span class="obligatoire">*</span></span>
            <div class="cases">
%s
            </div>
          </div>

          <div class="champ champ--duo">
            <div class="champ">
              <label for="r-qualifications">Qualifications et certifications</label>
              <input type="text" id="r-qualifications" placeholder="Diplômes, OPQIBI, certifications…">
            </div>
            <div class="champ">
              <label for="r-rcpro">Assurance RC professionnelle <span class="obligatoire">*</span></label>
              <input type="text" id="r-rcpro" required placeholder="Assureur et n° de contrat">
            </div>
          </div>

          <div class="champ">
            <label for="r-message">Message <span class="champ__facultatif">(facultatif)</span></label>
            <textarea id="r-message" rows="4" placeholder="Parcours, types de dossiers traités, disponibilités."></textarea>
          </div>

          <div class="champ champ--case">
            <input type="checkbox" id="r-consentement" required>
            <label for="r-consentement">J’accepte que mes données soient utilisées pour être recontacté(e) au sujet de ma candidature. Voir la <a href="/politique-de-confidentialite/">politique de confidentialité</a>. <span class="obligatoire">*</span></label>
          </div>

          <input type="text" id="r-piege" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">

          <button class="bouton" type="submit">Envoyer ma candidature</button>
          <p class="formulaire__pied">Votre CV peut être envoyé par e-mail à
          <a href="mailto:%s">%s</a> après ce premier contact.</p>
        </form>
      </div>
    </div>
  </section>
""" % (
        banniere("Rejoignez-nous",
                 "Un réseau de professionnels indépendants du bâtiment sur la Côte d’Azur.",
                 "BTP-Expertise-Riviera-Antibes.webp",
                 "Professionnels du bâtiment sur la Côte d’Azur"),
        entete_bloc("Notre réseau",
                    "Rejoignez le réseau <em>BTP Expertise</em>"),
        RESEAU_CHAPO,
        profils,
        entete_bloc("Candidature",
                    "Présentez-nous <em>votre profil</em>",
                    "Nous revenons vers vous pour un premier échange téléphonique, "
                    "sans engagement."),
        SITE["form_action"], SITE["jeton_formulaire"],
        experience,
        departements,
        SITE["email"], SITE["email"],
    )

    PAGES.append(page(
        "rejoignez-nous",
        "Rejoignez notre réseau de professionnels | BTP Expertise",
        "BTP Expertise développe un réseau de professionnels indépendants du bâtiment "
        "dans les Alpes-Maritimes et le Var : experts, ingénieurs, thermiciens, spécialistes.",
        corps, "/rejoignez-nous/", fil=fil,
    ))


# ---------------------------------------------------------------------------
# Carte interactive des zones d'intervention
# ---------------------------------------------------------------------------

def carte_zones(lien=False):
    """Carte SVG des deux départements, commune par commune.

    Les tracés viennent du découpage administratif officiel (carte_donnees.py).
    Chaque commune porte son nom : le survol l'affiche, et les villes
    principales sont repérées par un point animé.
    """
    communes = []
    for dept, nom, code, trace in CARTE_COMMUNES:
        communes.append(
            '<path class="commune commune--%s" d="%s" data-nom="%s" data-dept="%s"/>'
            % (dept, trace, nom.replace('"', "&quot;"), dept))

    reperes = []
    for nom, dept, x, y in CARTE_VILLES:
        reperes.append(
            """<g class="repere repere--%s" data-ville="%s" transform="translate(%.1f %.1f)">
        <circle class="repere__onde" r="7"/>
        <circle class="repere__point" r="4.5"/>
        <text class="repere__nom" x="0" y="-12">%s</text>
      </g>""" % (dept, nom, x, y, nom))

    villes_06 = "\n".join(
        '            <li><button type="button" data-ville="%s">%s</button></li>' % (v, v)
        for v in VILLES_06[:12])
    villes_83 = "\n".join(
        '            <li><button type="button" data-ville="%s">%s</button></li>' % (v, v)
        for v in VILLES_83[:12])

    return """  <section class="section section--gris">
    <div class="conteneur">
    %s
      <div class="zone-carte" data-anim>

        <div class="zone-carte__plan">
          <svg viewBox="%s" role="img" aria-label="Carte des Alpes-Maritimes et du Var, zones d’intervention de BTP Expertise">
            <g class="communes">
%s
            </g>
            <g class="reperes">
%s
            </g>
          </svg>
          <div class="zone-carte__bulle" hidden></div>
        </div>

        <div class="zone-carte__listes">
          <div class="zone-dept zone-dept--06">
            <h3><span class="zone-dept__puce"></span> Alpes-Maritimes <span>06</span></h3>
            <ul class="zone-dept__villes">
%s
            </ul>
          </div>
          <div class="zone-dept zone-dept--83">
            <h3><span class="zone-dept__puce"></span> Var <span>83</span></h3>
            <ul class="zone-dept__villes">
%s
            </ul>
          </div>
          <p class="zone-carte__note">Survolez une commune pour la situer. Le cabinet
          intervient sur l’ensemble des deux départements.</p>%s
        </div>

      </div>
    </div>
  </section>
""" % (
        entete_bloc("Zones d’intervention",
                    "Alpes-Maritimes <em>&amp; Var</em>",
                    "Deux départements, %d communes couvertes, de Menton à Saint-Cyr-sur-Mer."
                    % len(CARTE_COMMUNES)),
        CARTE_VIEWBOX,
        "\n".join("              " + c for c in communes),
        "\n".join("              " + r for r in reperes),
        villes_06,
        villes_83,
        ('\n          <a class="bouton bouton--bleu zone-carte__bouton"'
         ' href="/zones-intervention/">Voir toutes les villes couvertes</a>')
        if lien else "",
    )


# ---------------------------------------------------------------------------
# Villes prioritaires : Nice, Cannes, Antibes
# ---------------------------------------------------------------------------

def carte_villes():
    """Petite carte des trois villes qui ont leur propre page.

    Distincte de celle de l'accueil, qui reste une carte d'exploration commune
    par commune. Ici le dessin est muet — aucune infobulle, aucun survol de
    commune — et ne sert que de fond aux trois repères, seuls éléments
    cliquables.
    """
    # On ne dessine que l'agglomération : les communes dont le centre est à
    # moins de RAYON des trois villes. Le département entier, presque carré,
    # noyait Nice, Cannes et Antibes dans une grande zone vide au nord.
    RAYON = 65

    ancres = [(x, y) for nom, dept, x, y in CARTE_VILLES
              if nom in {v["nom"] for v in VILLES_PRIORITAIRES}]

    def centre(trace):
        v = [float(z) for z in re.findall(r"-?\d+\.?\d*", trace)]
        return sum(v[0::2]) / len(v[0::2]), sum(v[1::2]) / len(v[1::2]), v

    par_slug = {v["nom"]: v for v in VILLES_PRIORITAIRES}

    voisines, coords, zones = [], [], {}
    for dept, nom, code, trace in CARTE_COMMUNES:
        if dept != "06":
            continue
        cx, cy, points = centre(trace)
        if not any((cx - ax) ** 2 + (cy - ay) ** 2 <= RAYON ** 2 for ax, ay in ancres):
            continue
        coords += points
        if nom in par_slug:
            zones[nom] = (trace, cx, cy)   # commune cliquable, dessinée à part
        else:
            voisines.append(trace)

    # Le cadrage épouse la sélection : rien n'est coupé, et il se recalcule
    # tout seul si le fond de carte ou le rayon changent.
    xs, ys = coords[0::2], coords[1::2]
    marge = 16
    viewbox = "%.1f %.1f %.1f %.1f" % (
        min(xs) - marge, min(ys) - marge,
        max(xs) - min(xs) + 2 * marge, max(ys) - min(ys) + 2 * marge)

    fond = "\n".join(
        '            <path class="commune-muette" d="%s"/>' % trace
        for trace in voisines)

    # C'est la commune elle-même qui s'allume, plus un point posé dessus :
    # on survole la ville, pas une pastille à côté.
    reperes = []
    for v in VILLES_PRIORITAIRES:
        if v["nom"] not in zones:
            continue
        trace, cx, cy = zones[v["nom"]]
        reperes.append(
            """<a href="/expert-batiment-%s/" class="zone-ville" data-ville="%s"
               aria-label="Expert bâtiment à %s">
              <path class="zone-ville__forme" d="%s"/>
              <text class="zone-ville__nom" x="%.1f" y="%.1f">%s</text>
            </a>""" % (v["slug"], v["nom"], v["nom"], trace, cx, cy, v["nom"]))

    liens = "\n".join(
        """        <a class="ville-puce" data-ville="%s" href="/expert-batiment-%s/">
          <span class="ville-puce__tete">
            <span class="ville-puce__nom">%s</span>
            <span class="ville-puce__cp">%s</span>
          </span>
          <span class="ville-puce__plus">En savoir plus <span aria-hidden="true">&rarr;</span></span>
        </a>""" % (v["nom"], v["slug"], v["nom"], v["cp"])
        for v in VILLES_PRIORITAIRES)

    return """      <div class="carte-villes" data-anim>
        <div class="carte-villes__plan">
          <svg viewBox="%s" role="img"
               aria-label="Nice, Cannes et Antibes sur la Côte d’Azur, dans les Alpes-Maritimes">
            <g class="fond">
%s
            </g>
            <g class="villes-reperes">
%s
            </g>
          </svg>
        </div>
        <div class="carte-villes__liens">
%s
        </div>
      </div>
""" % (viewbox, fond, "\n".join(reperes), liens)


def villes_prioritaires():
    """La carte des trois villes principales (§23, §24).

    Le détail de chaque ville — désordres, quartiers, contexte — vit désormais
    sur sa propre page. Le répéter ici créait un doublon de contenu entre
    /zones-intervention/ et les trois pages villes, ce qui les affaiblit
    mutuellement aux yeux des moteurs.
    """
    return """  <section class="section">
    <div class="conteneur">
    %s
%s
    </div>
  </section>
""" % (
        entete_bloc("Nos secteurs principaux",
                    "Nice, Cannes <em>et Antibes</em>",
                    "Le cabinet intervient sur l’ensemble des Alpes-Maritimes et du Var, "
                    "avec une présence quotidienne sur ces trois villes. "
                    "Cliquez sur une ville pour découvrir son parc immobilier "
                    "et les désordres qu’on y rencontre."),
        carte_villes(),
    )


# ---------------------------------------------------------------------------
# Zones d'intervention
# ---------------------------------------------------------------------------

def page_zones():
    fil = [("Zones d’intervention", None)]

    corps = """%s

%s

  <section class="section">
    <div class="conteneur">
    %s
      <div class="zones">
        <div>
          <div class="zone__titre"><h3>Alpes-Maritimes</h3><span>06</span></div>
          <p>De Menton à Théoule-sur-Mer, littoral et moyen pays : copropriétés du bord de mer, villas des collines, maisons de village et constructions récentes de la technopole.</p>
          <ul class="villes">%s</ul>
        </div>
        <div>
          <div class="zone__titre"><h3>Var</h3><span>83</span></div>
          <p>De Saint-Raphaël à Saint-Cyr-sur-Mer, en passant par le centre Var : maisons individuelles, lotissements des années 70-90 particulièrement exposés au retrait-gonflement des argiles, et résidences secondaires.</p>
          <ul class="villes">%s</ul>
        </div>
      </div>
      <p class="centre saut">Votre commune n’apparaît pas dans cette liste ? Nous intervenons plus largement en région Provence-Alpes-Côte d’Azur. <a href="/contact/">Contactez-nous</a> pour vérifier notre disponibilité sur votre secteur.</p>
    </div>
  </section>

  <section class="section section--gris">
    <div class="conteneur">
    %s
      <div class="grille grille--3">
        <article class="carte">
          <h3>Fissures et sécheresse</h3>
          <p>Le retrait-gonflement des sols argileux touche fortement les maisons individuelles du Var et de l’arrière-pays niçois. Les épisodes de sécheresse de 2022 et 2023 ont multiplié les sinistres.</p>
          <a class="carte__lien" href="/conseils/%s/">Lire notre analyse</a>
        </article>
        <article class="carte">
          <h3>Infiltrations en bord de mer</h3>
          <p>Embruns, vents violents et fortes pluies méditerranéennes mettent à l’épreuve les terrasses, toitures-terrasses et menuiseries du littoral azuréen et varois.</p>
        </article>
        <article class="carte">
          <h3>Malfaçons en rénovation</h3>
          <p>La forte activité de rénovation sur la Côte d’Azur s’accompagne de chantiers mal exécutés. Un contrôle indépendant avant réception protège vos garanties.</p>
        </article>
      </div>
    </div>
  </section>

%s
""" % (
        banniere("Expert bâtiment dans le Var et les Alpes-Maritimes",
                 "Le cabinet se déplace sur l’ensemble des deux départements pour vos expertises et "
                 "vos missions d’assistance à maîtrise d’ouvrage.",
                 "Ville-de-Nice.webp", "Vue de la ville de Nice"),
        villes_prioritaires(),
        entete_bloc("Deux départements",
                    "Le 06 et le 83, <em>sans exception</em>",
                    "Basés à Nice, nous intervenons quotidiennement sur le littoral comme dans "
                    "l’arrière-pays. Les désordres évolutifs — fissures qui s’aggravent, infiltrations "
                    "actives — sont traités en priorité."),
        "".join("<li>%s</li>" % v for v in VILLES_06),
        "".join("<li>%s</li>" % v for v in VILLES_83),
        entete_bloc("Sur le terrain",
                    "Les désordres les plus <em>fréquents</em> ici"),
        ARTICLES_PUBLIES[0]["slug"],
        bandeau_appel(
            "Une question sur votre secteur ?",
            "Dites-nous où se situe votre bien et la nature du désordre : nous vous indiquons "
            "sous 24 à 48 heures ouvrées la mission adaptée et nos disponibilités."),
    )

    PAGES.append(page(
        "zones-intervention",
        "Expert bâtiment Nice, Cannes, Antibes, Var | BTP Expertise",
        "Expertise en bâtiment à Nice, Cannes, Antibes, Grasse, Toulon, Hyères, Fréjus, Draguignan et "
        "dans toutes les communes du 06 et du 83.",
        corps, "/zones-intervention/", fil=fil,
    ))


def page_ville(v):
    """Une page par ville prioritaire (§23, §24).

    Le cahier des charges interdit les pages jumelles où seul le nom change :
    le contexte, les désordres, les quartiers et la FAQ sont propres à chaque
    ville. Le siège étant une domiciliation, aucune adresse postale n'est
    affichée ici — c'est la zone d'intervention qui fait foi.
    """
    url = "/expert-batiment-%s/" % v["slug"]
    fil = [("Zones d’intervention", "/zones-intervention/"), (v["nom"], None)]

    contexte = "\n".join("        <p>%s</p>" % p for p in v["contexte"])

    desordres = "\n".join("""        <article class="carte">
          <h3>%s</h3>
          <p>%s</p>
        </article>""" % (t, d) for t, d in v["desordres"])

    quartiers = "\n".join(
        "          <li>%s</li>" % q for q in v["quartiers"])

    faq = "\n".join("""        <details%s>
          <summary>%s</summary>
          <div class="faq__reponse"><p>%s</p></div>
        </details>""" % (" open" if i == 0 else "", q, r)
        for i, (q, r) in enumerate(v["faq"]))

    # Les missions mises en avant sur la page d'accueil, présentées ici sous
    # l'angle de la ville : le détail complet reste sur /expertises/.
    missions = "\n".join(
        '          <li><a href="/expertises/#%s">%s</a></li>' % (e["id"], e["titre"])
        for e in EXPERTISES if e.get("accueil"))

    corps = """%s

  <section class="section">
    <div class="conteneur">
    %s
      <div class="ville-contexte">
%s
      </div>
    </div>
  </section>

  <section class="section section--gris">
    <div class="conteneur">
    %s
      <div class="grille grille--3">
%s
      </div>
    </div>
  </section>

  <section class="section">
    <div class="conteneur">
      <div class="ville-detail">
        <div>
          <h2>Nos missions à %s</h2>
          <ul class="ville-missions">
%s
          </ul>
          <a class="bouton bouton--contour-nuit" href="/expertises/">Voir les dix missions</a>
        </div>
        <div>
          <h2>Quartiers couverts</h2>
          <ul class="ville-quartiers">
%s
          </ul>
          <p class="ville-detail__note">Cette liste n’est pas limitative : le cabinet
          intervient sur l’ensemble de la commune et des communes voisines.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section section--gris">
    <div class="conteneur">
    %s
      <div class="faq">
%s
      </div>
      <p class="centre saut"><a href="/faq/">Voir toutes les questions fréquentes</a></p>
    </div>
  </section>

%s
""" % (
        banniere(v["titre"], v["chapo"],
                 "Ville-de-Nice-e1770393940931.webp",
                 "Alpes-Maritimes, zone d’intervention de BTP Expertise"),
        entete_bloc(v["nom"],
                    "Le bâti de <em>%s</em>" % v["nom"],
                    "Ce que l’on rencontre sur le terrain, et pourquoi cela change "
                    "la façon de conduire une expertise."),
        contexte,
        entete_bloc("Sur le terrain",
                    "Les désordres les plus <em>fréquents</em>",
                    "Trois situations qui reviennent régulièrement à %s." % v["nom"]),
        desordres,
        v["nom"],
        missions,
        quartiers,
        entete_bloc("Questions fréquentes",
                    "À %s, on nous demande <em>souvent</em>" % v["nom"],
                    ""),
        faq,
        bandeau_appel("Un doute sur votre bien à %s ?" % v["nom"],
                      "Décrivez votre situation : nous vous répondons sous 48 heures "
                      "avec la mission adaptée et nos disponibilités."),
    )

    jsonld = {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": r}}
            for q, r in v["faq"]
        ],
    }

    PAGES.append(page(
        "expert-batiment-%s" % v["slug"],
        "%s — %s | BTP Expertise" % (v["titre"], v["seo"]),
        v["meta"],
        corps, url, jsonld=jsonld, fil=fil,
    ))


# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------

def page_faq():
    fil = [("FAQ", None)]
    blocs = "\n".join("""        <details%s>
          <summary>%s</summary>
          <div class="faq__reponse">%s</div>
        </details>""" % (" open" if i == 0 else "", q,
                         "".join("<p>%s</p>" % p for p in r))
                      for i, (q, r) in enumerate(FAQ))

    corps = """%s

  <section class="section">
    <div class="conteneur">
    %s
      <div class="faq">
%s
      </div>
    </div>
  </section>

%s
""" % (
        banniere("FAQ", "Les questions les plus fréquentes sur l’expertise en bâtiment.",
                 "Ville-de-Nice-e1770393940931.webp", "Vue de Nice depuis la colline du Château"),
        entete_bloc("FAQ",
                    "Les questions les plus <em>fréquentes</em>",
                    "Tout ce qu’il faut savoir avant de faire appel à un expert en bâtiment indépendant."),
        blocs,
        bandeau_appel(
            "Vous ne trouvez pas votre réponse ?",
            "Décrivez-nous votre situation : nous vous répondons sous 24 à 48 heures ouvrées."),
    )

    faq_jsonld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": " ".join(r)}}
            for q, r in FAQ
        ],
    }

    PAGES.append(page(
        "faq",
        "FAQ — Expertise en bâtiment | BTP Expertise",
        "Quand faire appel à un expert en bâtiment ? Quelle différence avec un expert d’assurance ? "
        "Nos réponses pour le Var et les Alpes-Maritimes.",
        corps, "/faq/", jsonld=faq_jsonld, fil=fil,
    ))


# ---------------------------------------------------------------------------
# Conseils : liste et article
# ---------------------------------------------------------------------------

def page_conseils():
    fil = [("Nos conseils", None)]
    cartes = ('<div class="grille grille--3">\n%s\n      </div>'
              % "\n".join(carte_conseil(a) for a in ARTICLES_PUBLIES))

    corps = """%s

  <section class="section">
    <div class="conteneur">
    %s
%s
    </div>
  </section>

%s
""" % (
        banniere("Nos conseils", "Comprendre les désordres du bâtiment.",
                 "Reception-de-travaux-Antibes.webp", "Réception de travaux sur la Côte d’Azur"),
        entete_bloc("Nos conseils",
                    "Comprendre les <em>désordres du bâtiment</em>",
                    "Analyses techniques et repères pratiques pour les propriétaires des "
                    "Alpes-Maritimes et du Var."),
        cartes,
        bandeau_appel(),
    )

    PAGES.append(page(
        "conseils",
        "Nos conseils — Désordres du bâtiment | BTP Expertise",
        "Analyses techniques du cabinet : fissures, sécheresse et retrait-gonflement des argiles, "
        "infiltrations, malfaçons, pour les propriétaires du 06 et du 83.",
        corps, "/conseils/", fil=fil,
    ))


def page_article(art):
    fil = [("Nos conseils", "/conseils/"), (art["titre_court"], None)]
    morceaux = []
    for genre, valeur in art["corps"]:
        if genre == "p":
            morceaux.append("<p>%s</p>" % valeur)
        elif genre == "h2":
            morceaux.append("<h2>%s</h2>" % valeur)
        elif genre == "h3":
            morceaux.append("<h3>%s</h3>" % valeur)
        elif genre == "ul":
            morceaux.append('<ul class="liste-check">%s</ul>'
                            % "".join("<li>%s</li>" % e for e in valeur))
        elif genre == "citation":
            morceaux.append("<blockquote><p>%s</p></blockquote>" % valeur)
        elif genre == "image":
            fichier = art.get(valeur)
            if fichier:
                morceaux.append(img(fichier, art["titre_court"], largeur=820, hauteur=460))

    corps = """%s

  <article class="section">
    <div class="conteneur">
      <div class="article">
        <p class="article__meta">Publié le %s — BTP Expertise</p>
        %s
        <div class="saut centre">
          <a class="bouton" href="/contact/">Demander une expertise fissures</a>
        </div>
      </div>
    </div>
  </article>

%s
""" % (
        banniere(art["titre"], art["resume"], art["image"], art["titre_court"]),
        art["date_affichee"],
        "\n        ".join(morceaux),
        bandeau_appel(),
    )

    article_jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": art["titre"],
        "description": art["resume"],
        "image": SITE["url"] + "/assets/img/" + art["image"],
        "datePublished": art["date"],
        "dateModified": art["date"],
        "author": {"@type": "Organization", "name": SITE["nom"], "url": SITE["url"] + "/"},
        "publisher": {"@id": SITE["url"] + "/#cabinet"},
        "mainEntityOfPage": SITE["url"] + "/conseils/%s/" % art["slug"],
        "about": ["Fissures", "Retrait-gonflement des argiles", "Sécheresse",
                  "Expertise bâtiment", "Catastrophe naturelle"],
    }

    PAGES.append(page(
        os.path.join("conseils", art["slug"]),
        art["titre_court"] + " | BTP Expertise",
        art["meta_description"],
        corps, "/conseils/%s/" % art["slug"],
        jsonld=article_jsonld, fil=fil, og_type="article",
        og_image=SITE["url"] + "/assets/img/" + art["image"],
    ))


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

def page_contact():
    fil = [("Prendre rendez-vous", None)]

    formats = "\n              ".join(
        """<label class="format" for="fmt-%s">
                  <input type="radio" id="fmt-%s" name="Format" value="%s" data-cle="%s"%s>
                  <span class="format__corps">
                    <span class="format__titre">%s <em>· %s</em></span>
                    <span class="format__detail">%s</span>
                  </span>
                </label>""" % (cle, cle, libelle, cle, " checked" if i == 0 else "",
                               libelle, duree, detail)
        for i, (cle, libelle, duree, detail) in enumerate(FORMATS_RDV))

    # Chaque demande porte le besoin auquel elle se rattache : le script
    # n'affiche que celles du besoin coché, et masque le champ entier quand le
    # besoin n'en propose aucune — c'est le cas de l'AMO.
    problematiques = "\n              ".join(
        '<option value="%s" data-besoin="%s">%s</option>' % (o, besoin, o)
        for besoin, liste in DEMANDES_PAR_BESOIN.items() for o in liste)
    biens = "\n              ".join(
        '<option value="%s">%s</option>' % (b, b) for b in TYPES_BIEN)
    besoins = "\n              ".join(
        """<label class="besoin-choix" for="bes-%d">
                  <input type="radio" id="bes-%d" name="Besoin" value="%s"%s>
                  <span>%s</span>
                </label>""" % (i, i, b, " checked" if i == 0 else "", b)
        for i, b in enumerate(BESOINS_DEMANDE))

    # L'agenda est calculé par le back-office : le site lui demande les
    # créneaux libres, puis y enregistre la réservation. Rien d'extérieur.
    bloc_agenda = """              <div class="agenda" id="agenda" data-service="%s" data-jeton="%s">
                <p class="agenda__attente">Chargement des créneaux disponibles…</p>
              </div>
            </div>

            <div class="agenda__coordonnees" hidden>
              <div class="champ champ--duo">
                <div class="champ">
                  <label for="rdv-prenom">Prénom <span class="obligatoire">*</span></label>
                  <input type="text" id="rdv-prenom" required autocomplete="given-name">
                </div>
                <div class="champ">
                  <label for="rdv-nom">Nom <span class="obligatoire">*</span></label>
                  <input type="text" id="rdv-nom" required autocomplete="family-name">
                </div>
              </div>

              <div class="champ champ--duo">
                <div class="champ">
                  <label for="rdv-telephone">Téléphone <span class="obligatoire">*</span></label>
                  <input type="tel" id="rdv-telephone" required autocomplete="tel">
                </div>
                <div class="champ">
                  <label for="rdv-email">E-mail <span class="obligatoire">*</span></label>
                  <input type="email" id="rdv-email" required autocomplete="email">
                </div>
              </div>

              <div class="champ champ--case">
                <input type="checkbox" id="rdv-consentement" required>
                <label for="rdv-consentement">J’accepte que mes données soient utilisées pour être recontacté(e). Voir la <a href="/politique-de-confidentialite/">politique de confidentialité</a>. <span class="obligatoire">*</span></label>
              </div>

              <input type="text" id="rdv-piege" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">

              <button class="bouton" type="submit">Confirmer le rendez-vous</button>
              <p class="etape__note">Le rendez-vous est enregistré immédiatement dans l’agenda
              du cabinet. Vous recevez la confirmation par e-mail.</p>
            </div>""" % (SITE["form_action"], SITE["jeton_formulaire"])

    corps = """%s

  <section class="section">
    <div class="conteneur">
    %s
      <div class="rdv">

        <ol class="jalons" aria-label="Progression">
          <li class="jalon est-courant" data-jalon="1"><span>1</span> Votre projet</li>
          <li class="jalon" data-jalon="2"><span>2</span> Le rendez-vous</li>
        </ol>

        <form class="formulaire rdv__form" id="form-rdv" action="%s" method="POST" data-jeton="%s">
          <div class="formulaire__message" id="rdv-message" role="status" aria-live="polite"></div>

          <fieldset class="etape est-active" data-etape="1">
            <legend class="etape__titre">Parlez-nous de votre projet</legend>

            <div class="champ">
              <span class="champ__intitule">Votre besoin <span class="obligatoire">*</span></span>
              <div class="besoins-choix">
              %s
              </div>
            </div>

            <div class="champ" id="champ-demande">
              <label for="objet">Votre demande <span class="obligatoire">*</span></label>
              <select id="objet" required>
                <option value="">Choisissez votre demande</option>
              %s
              </select>
            </div>

            <div class="champ champ--duo">
              <div class="champ">
                <label for="type-bien">Type de bien <span class="obligatoire">*</span></label>
                <select id="type-bien" required>
                  <option value="">Choisissez</option>
              %s
                </select>
              </div>
              <div class="champ">
                <label for="ville">Ville du bien <span class="obligatoire">*</span></label>
                <input type="text" id="ville" required placeholder="Nice, Cannes, Antibes…" autocomplete="address-level2">
              </div>
            </div>

            <div class="champ">
              <label for="description">Description de la situation <span class="obligatoire">*</span></label>
              <textarea id="description" required rows="5" placeholder="Décrivez les désordres constatés, leur ancienneté, l’année de construction si vous la connaissez, et ce que vous attendez de notre intervention."></textarea>
            </div>

            <div class="champ champ--fichiers">
              <label for="photos">Photos et documents <span class="facultatif">facultatif</span></label>
              <input type="file" id="photos" multiple
                     accept="image/jpeg,image/png,image/webp,image/heic,application/pdf">
              <p class="champ__aide">Photos des désordres, devis, rapport existant, plans.
              5 fichiers au maximum, 5 Mo chacun. Formats acceptés : JPEG, PNG, WebP, HEIC et PDF.</p>
              <ul class="fichiers-liste" id="fichiers-liste"></ul>
            </div>

            <div class="etape__actions">
              <button class="bouton" type="button" data-suivant>Continuer</button>
            </div>
          </fieldset>

          <fieldset class="etape" data-etape="2" hidden>
            <legend class="etape__titre">Votre rendez-vous</legend>
            <div class="recap" id="rdv-recap"></div>

            <div class="agenda-bloc">
              <div class="agenda__formats" role="radiogroup" aria-label="Format du rendez-vous">
              %s
              </div>
%s
            <div class="etape__actions etape__actions--retour">
              <button class="bouton bouton--contour-nuit" type="button" data-precedent>Retour</button>
            </div>
          </fieldset>
        </form>

        <div class="rdv__urgence">
          <p>Situation urgente — fissure qui évolue, infiltration active, réception imminente ?</p>
          <a class="bouton bouton--appel bouton--contour-nuit" href="tel:%s">Appelez-nous</a>
        </div>

      </div>
    </div>
  </section>
""" % (
        banniere("Prendre rendez-vous",
                 "Un premier échange sans engagement, pour cerner votre situation.",
                 "6-e1770394485690.webp", "Prendre rendez-vous avec BTP Expertise"),
        entete_bloc("Rendez-vous",
                    "Parlons de <em>votre situation</em>",
                    "Deux étapes, deux minutes. Vous décrivez votre situation, "
                    "puis vous choisissez le créneau qui vous arrange."),
        SITE["form_action"], SITE["jeton_formulaire"],
        besoins,
        problematiques,
        biens,
        formats,
        bloc_agenda,
        SITE["telephone_lien"],
    )

    PAGES.append(page(
        "contact",
        "Prendre rendez-vous — Expert bâtiment Nice | BTP Expertise",
        "Prenez rendez-vous avec un expert en bâtiment à Nice, Cannes ou Antibes. Échange "
        "téléphonique ou visioconférence sous 48 heures, sans engagement.",
        corps, "/contact/",
        jsonld={"@context": "https://schema.org", "@type": "ContactPage",
                "name": "Prendre rendez-vous", "url": SITE["url"] + "/contact/"},
        fil=fil,
    ))

# ---------------------------------------------------------------------------
# Pages légales
# ---------------------------------------------------------------------------

def page_mentions():
    fil = [("Mentions légales", None)]
    corps = """%(banniere)s

  <section class="section">
    <div class="conteneur">
      <div class="legal">
        <p>Dernière mise à jour : %(date_maj)s</p>

        <h2>Éditeur du site</h2>
        <table>
          <tbody>
            <tr><th>Éditeur</th><td>%(raison_sociale)s</td></tr>
            <tr><th>Forme juridique</th><td>%(forme_juridique)s</td></tr>
            <tr><th>Adresse</th><td>%(adresse)s</td></tr>
            <tr><th>SIREN</th><td>%(siren)s</td></tr>
            <tr><th>N° TVA intracommunautaire</th><td>%(tva)s</td></tr>
%(lignes_societe)s            <tr><th>Téléphone</th><td><a href="tel:%(tel_lien)s">%(tel)s</a></td></tr>
            <tr><th>E-mail</th><td><a href="mailto:%(email)s">%(email)s</a></td></tr>
            <tr><th>Directeur de la publication</th><td>%(directeur)s</td></tr>
          </tbody>
        </table>
%(mention_capital)s

        <h2>Activité et assurance professionnelle</h2>
        <p>BTP Expertise exerce une activité d’expertise en bâtiment et d’assistance à maîtrise d’ouvrage (AMO). Le cabinet intervient en qualité d’expert indépendant : il ne représente ni compagnie d’assurance, ni entreprise de travaux.</p>
        <table>
          <tbody>
            <tr><th>Assureur responsabilité civile professionnelle</th><td>%(assurance_nom)s</td></tr>
%(ligne_contrat)s            <tr><th>Couverture géographique</th><td>%(assurance_couverture)s</td></tr>
          </tbody>
        </table>

        <h2>Hébergement</h2>
        <table>
          <tbody>
            <tr><th>Hébergeur</th><td>%(hebergeur_nom)s</td></tr>
            <tr><th>Adresse</th><td>%(hebergeur_adresse)s</td></tr>
            <tr><th>Téléphone</th><td>%(hebergeur_tel)s</td></tr>
            <tr><th>Site web</th><td><a href="%(hebergeur_site)s" rel="noopener">%(hebergeur_site)s</a></td></tr>
          </tbody>
        </table>

        <h2>Propriété intellectuelle</h2>
        <p>L’ensemble des contenus présents sur ce site — textes, photographies, vidéos, logos, éléments graphiques et mise en page — est la propriété de %(raison_sociale)s ou fait l’objet d’une autorisation d’utilisation. Toute reproduction, représentation, modification ou exploitation, totale ou partielle, sans autorisation écrite préalable est interdite et constituerait une contrefaçon au sens des articles L.335-2 et suivants du Code de la propriété intellectuelle.</p>

        <h2>Nature des informations diffusées</h2>
        <p>Les informations techniques publiées sur ce site ont une vocation informative générale. Elles ne constituent en aucun cas un avis technique personnalisé, un diagnostic ni une préconisation applicable à une situation particulière.</p>
        <p>Seul un rapport d’expertise établi après visite sur site, dans le cadre d’une mission contractuelle, engage le cabinet. Aucune décision technique, juridique ou financière ne doit être prise sur la seule base du contenu de ce site.</p>

        <h2>Responsabilité</h2>
        <p>%(raison_sociale)s s’efforce d’assurer l’exactitude et la mise à jour des informations diffusées, sans pouvoir en garantir l’exhaustivité. L’éditeur ne saurait être tenu responsable des erreurs ou omissions, ni des dommages résultant de l’utilisation des informations mises à disposition.</p>
        <p>Le site peut comporter des liens vers des sites tiers. L’éditeur n’exerce aucun contrôle sur ces sites et décline toute responsabilité quant à leur contenu.</p>

        <h2>Données personnelles et cookies</h2>
        <p>Le traitement des données personnelles collectées via le formulaire de demande d’expertise est détaillé dans notre <a href="/politique-de-confidentialite/">politique de confidentialité</a>.</p>
        <p>Ce site ne dépose aucun cookie publicitaire ni traceur de mesure d’audience.</p>

        <h2>Recours à l’intelligence artificielle</h2>
        <p>Le cabinet utilise des outils d’intelligence artificielle pour l’assister dans la gestion administrative des dossiers, à savoir :</p>
        <ul class="liste-check">
          %(ia_usages)s
        </ul>
        <p><strong>Ces outils n’interviennent jamais dans :</strong></p>
        <ul class="liste-check">
          %(ia_jamais)s
        </ul>
        <p>Toute production assistée par un outil d’intelligence artificielle est <strong>relue, corrigée et validée par l’expert</strong> avant transmission. L’analyse technique, les conclusions et les préconisations demeurent le fait d’un professionnel identifié, seul responsable du contenu du rapport qu’il signe.</p>
        <p>Les informations transmises à ces outils le sont dans le cadre de contrats professionnels excluant leur réutilisation à des fins d’entraînement de modèles. Vous pouvez demander à tout moment qu’aucun outil d’intelligence artificielle ne soit employé dans le traitement de votre dossier, en écrivant à <a href="mailto:%(email)s">%(email)s</a>.</p>

        <h2>Médiation de la consommation</h2>
        <p>Conformément à l’article L.612-1 du Code de la consommation, tout consommateur a le droit de recourir gratuitement à un médiateur de la consommation en vue de la résolution amiable d’un litige l’opposant à un professionnel. Les coordonnées du médiateur compétent sont communiquées sur demande et figurent dans les conditions de mission.</p>

        <h2>Droit applicable</h2>
        <p>Les présentes mentions légales sont soumises au droit français. En cas de litige, et à défaut de résolution amiable, les tribunaux français seront seuls compétents.</p>
      </div>
    </div>
  </section>
""" % {
        "banniere": banniere("Mentions légales", "Informations légales relatives au site btpexpertise.fr.",
                             "12.webp", "Côte d’Azur"),
        "date_maj": LEGAL["date_maj"],
        "raison_sociale": LEGAL["raison_sociale"],
        "forme_juridique": LEGAL["forme_juridique"],
        "adresse": ADRESSE_COMPLETE,
        "siren": LEGAL["siren"],
        "tva": LEGAL["tva"],
        "lignes_societe": lignes_societe(),
        "mention_capital": mention_capital(),
        "tel_lien": SITE["telephone_lien"],
        "tel": SITE["telephone"],
        "email": SITE["email"],
        "directeur": LEGAL["directeur_publication"],
        "assurance_nom": LEGAL["assurance_nom"],
        # Tant qu'aucun contrat n'existe, la ligne disparait plutot que
        # d'afficher une case vide sous un intitule officiel.
        "ligne_contrat": ("            <tr><th>N° de contrat</th><td>%s</td></tr>\n"
                          % LEGAL["assurance_contrat"]) if LEGAL["assurance_contrat"] else "",
        "assurance_couverture": LEGAL["assurance_couverture"],
        "hebergeur_nom": LEGAL["hebergeur_nom"],
        "hebergeur_adresse": LEGAL["hebergeur_adresse"],
        "hebergeur_tel": LEGAL["hebergeur_tel"],
        "hebergeur_site": LEGAL["hebergeur_site"],
        "ia_usages": "\n          ".join("<li>%s</li>" % u for u in IA["usages"]),
        "ia_jamais": "\n          ".join("<li>%s</li>" % u for u in IA["jamais"]),
    }

    PAGES.append(page(
        "mentions-legales",
        "Mentions légales | BTP Expertise",
        "Mentions légales du site btpexpertise.fr : éditeur, assurance professionnelle, hébergeur, "
        "propriété intellectuelle et responsabilité.",
        corps, "/mentions-legales/", fil=fil,
    ))


def page_confidentialite():
    fil = [("Politique de confidentialité", None)]
    corps = """%(banniere)s

  <section class="section">
    <div class="conteneur">
      <div class="legal">
        <p>Dernière mise à jour : %(date_maj)s</p>
        <p>La présente politique explique quelles données personnelles sont collectées sur ce site, pourquoi, pendant combien de temps elles sont conservées, et quels droits vous pouvez exercer. Elle s’applique au site %(domaine)s.</p>

        <h2>Responsable du traitement</h2>
        <p>Le responsable du traitement est %(raison_sociale)s, %(forme_juridique)s, dont l’adresse est %(adresse)s.</p>
        <p>Pour toute question relative à vos données : <a href="mailto:%(email)s">%(email)s</a>.</p>

        <h2>Données collectées</h2>
        <p>Nous ne collectons que les données que vous nous transmettez volontairement via le formulaire de demande d’expertise :</p>
        <ul class="liste-check">
          <li>Nom et prénom</li>
          <li>Adresse e-mail</li>
          <li>Numéro de téléphone</li>
          <li>Ville du bien concerné</li>
          <li>Type et objet de la demande</li>
          <li>Description du problème rencontré, ainsi que les photographies que vous choisissez de nous transmettre</li>
        </ul>
        <p>Aucune donnée n’est collectée à votre insu. Ce site ne pratique ni profilage, ni décision automatisée, ni revente de données.</p>

        <h2>Finalité et base légale</h2>
        <p>Ces données sont utilisées uniquement pour <strong>traiter votre demande</strong> : vous recontacter, qualifier votre besoin, établir une proposition d’intervention et, le cas échéant, assurer le suivi de la mission.</p>
        <p>La base légale du traitement est votre <strong>consentement</strong> (article 6.1.a du RGPD), recueilli par la case à cocher du formulaire, ainsi que l’exécution de mesures précontractuelles prises à votre demande (article 6.1.b).</p>

        <h2>Destinataires</h2>
        <p>Vos données sont destinées au seul cabinet BTP Expertise. Elles ne sont ni vendues, ni louées, ni transmises à des tiers à des fins commerciales.</p>
        <p>Les demandes et les photos transmises sont enregistrées sur les services Google Workspace du cabinet (Google Sheets et Google Drive), Google agissant en qualité de sous-traitant au sens du RGPD. Les photos que vous joignez sont stockées dans un espace privé du cabinet et ne sont pas rendues publiques.</p>
        <p>Dans le cadre d’une mission, certains éléments techniques peuvent être communiqués aux parties concernées (assureur, entreprise, avocat) avec votre accord préalable.</p>

        <h2>Durée de conservation</h2>
        <ul class="liste-check">
          <li><strong>Demande sans suite</strong> : 12 mois à compter du dernier échange.</li>
          <li><strong>Mission réalisée</strong> : 10 ans à compter de la fin de la mission, conformément aux obligations légales de conservation et aux délais de garantie applicables en matière de construction.</li>
        </ul>

        <h2>Sécurité</h2>
        <p>Le site est intégralement servi en HTTPS. Les échanges depuis le formulaire sont chiffrés en transit. L’accès aux demandes reçues est limité aux seules personnes habilitées du cabinet.</p>

        <h2>Cookies et mesure d’audience</h2>
        <p>Ce site ne dépose <strong>aucun cookie publicitaire</strong> et n’utilise aucun traceur de mesure d’audience. Aucun bandeau de consentement n’est donc nécessaire.</p>
        <p>Les polices de caractères sont chargées depuis Google Fonts ; à cette occasion, votre adresse IP est transmise à ce service pour permettre l’affichage.</p>

        <h2>Vos droits</h2>
        <p>Conformément au Règlement général sur la protection des données et à la loi Informatique et Libertés, vous disposez des droits suivants :</p>
        <ul class="liste-check">
          <li>Droit d’accès à vos données</li>
          <li>Droit de rectification des données inexactes</li>
          <li>Droit à l’effacement, dans les limites des obligations légales de conservation</li>
          <li>Droit à la limitation du traitement</li>
          <li>Droit à la portabilité de vos données</li>
          <li>Droit d’opposition au traitement</li>
          <li>Droit de retirer votre consentement à tout moment</li>
        </ul>
        <p>Pour exercer ces droits, écrivez à <a href="mailto:%(email)s">%(email)s</a> en précisant votre demande. Une réponse vous sera apportée dans un délai d’un mois.</p>

        <h2>Réclamation</h2>
        <p>Si vous estimez, après nous avoir contactés, que vos droits ne sont pas respectés, vous pouvez adresser une réclamation à la Commission nationale de l’informatique et des libertés (CNIL), 3 place de Fontenoy, TSA 80715, 75334 Paris Cedex 07, ou en ligne sur <a href="https://www.cnil.fr" rel="noopener">cnil.fr</a>.</p>
      </div>
    </div>
  </section>
""" % {
        "banniere": banniere("Politique de confidentialité",
                             "Traitement de vos données personnelles sur btpexpertise.fr.",
                             "12.webp", "Côte d’Azur"),
        "date_maj": LEGAL["date_maj"],
        "domaine": SITE["domaine"],
        "raison_sociale": LEGAL["raison_sociale"],
        "forme_juridique": LEGAL["forme_juridique"],
        "adresse": ADRESSE_COMPLETE,
        "email": SITE["email"],
        "tel_lien": SITE["telephone_lien"],
        "tel": SITE["telephone"],
    }

    PAGES.append(page(
        "politique-de-confidentialite",
        "Politique de confidentialité | BTP Expertise",
        "Traitement des données personnelles collectées sur btpexpertise.fr : finalité, durée de conservation, "
        "destinataires et exercice de vos droits RGPD.",
        corps, "/politique-de-confidentialite/", fil=fil,
    ))


def page_cgv():
    fil = [("Conditions générales de vente", None)]
    corps = """%(banniere)s

  <section class="section">
    <div class="conteneur">
      <div class="legal">
        <p>Dernière mise à jour : %(date_maj)s</p>

        <h2>Préambule</h2>
        <p>Les présentes conditions générales régissent les prestations d’expertise en bâtiment et d’assistance à maîtrise d’ouvrage réalisées par %(raison_sociale)s, %(forme_juridique)s, dont l’adresse est %(adresse)s, ci-après « le cabinet ».</p>
        <p>Toute commande de prestation implique l’acceptation sans réserve des présentes conditions. Elles prévalent sur tout autre document du client, sauf dérogation expresse et écrite figurant sur la lettre de mission.</p>

        <h2>Article 1 — Objet du contrat</h2>
        <p>Le contrat a pour objet la réalisation d’une mission technique définie dans une <strong>lettre de mission</strong> ou un devis, précisant la nature de l’intervention, son périmètre, son prix et ses délais. La signature de ce document par le client vaut acceptation de la mission et des présentes conditions.</p>

        <h2>Article 2 — Nature des prestations</h2>
        <p>Le cabinet intervient en qualité d’<strong>expert technique indépendant</strong>. Il n’est ni expert judiciaire commis par un tribunal, ni expert d’assurance mandaté par une compagnie, sauf mention contraire expresse.</p>
        <p>Ses missions couvrent notamment l’avis technique, la recherche de malfaçons et le contrôle qualité, l’assistance en réunion contradictoire, l’expertise préalable à une acquisition immobilière, la réception de travaux et l’assistance à maîtrise d’ouvrage. Dans le cadre d’une mission d’assistance à maîtrise d’ouvrage, le cabinet conseille et assiste le maître d’ouvrage, qui demeure décisionnaire et contracte directement avec les entreprises. Le cabinet n’assure ni la direction des travaux, ni la direction de l’exécution, ni une mission d’ordonnancement, pilotage et coordination, et ne garantit ni les délais, ni le budget final, ni la bonne exécution des entreprises.</p>
        <p>Le cabinet exerce une <strong>obligation de moyens</strong> et non de résultat. Il ne garantit aucune issue favorable à une procédure amiable ou judiciaire.</p>

        <h2>Article 3 — Tarifs et conditions de paiement</h2>
        <p>Les prix figurent sur la lettre de mission ou le devis, exprimés en euros. Sauf stipulation contraire, ils s’entendent frais de déplacement inclus dans les Alpes-Maritimes et le Var ; toute intervention hors de cette zone fait l’objet d’un complément indiqué au devis.</p>
        <p>Le règlement s’effectue en deux temps : un <strong>acompte</strong> à la validation de la mission, qui déclenche la programmation de l’intervention, et le <strong>solde</strong> à la remise du rapport. Les paiements s’effectuent par virement bancaire ou en ligne depuis la page <a href="/reglement/">Règlement de votre dossier</a>.</p>
        <p>Le rapport n’est remis qu’après encaissement complet du prix convenu.</p>

        <h2>Article 4 — Retard de paiement</h2>
        <p>Toute somme non réglée à l’échéance porte de plein droit, sans mise en demeure préalable, des pénalités de retard calculées au taux d’intérêt appliqué par la Banque centrale européenne à son opération de refinancement la plus récente, majoré de 10 points de pourcentage.</p>
        <p>S’y ajoute une indemnité forfaitaire de recouvrement de 40 euros, conformément aux articles L.441-10 et D.441-5 du Code de commerce. Lorsque les frais de recouvrement exposés dépassent ce montant, une indemnisation complémentaire peut être réclamée sur justificatifs.</p>

        <h2>Article 5 — Demande d’intervention</h2>
        <p>La demande est formulée par le client via le formulaire du site, par courriel ou par téléphone. Le cabinet accuse réception, qualifie le besoin et adresse une lettre de mission. Aucune intervention n’est engagée avant retour de ce document signé et encaissement de l’acompte.</p>
        <p>Le client s’engage à fournir des informations exactes et complètes sur la situation, l’ouvrage et les parties concernées. Toute omission susceptible de modifier l’analyse engage sa seule responsabilité.</p>

        <h2>Article 6 — Validité des échanges électroniques</h2>
        <p>Les parties conviennent que les échanges par courriel, ainsi que la signature électronique de la lettre de mission, ont valeur probante entre elles au sens des articles 1366 et suivants du Code civil.</p>

        <h2>Article 7 — Déroulement de la mission</h2>
        <p>Le client s’engage à rendre l’ouvrage accessible à la date convenue et à réunir les documents utiles : plans, permis, devis, marchés, procès-verbaux, correspondances, rapports antérieurs.</p>
        <p>Le rapport est remis au format numérique dans le délai indiqué sur la lettre de mission, courant à compter de la visite sur site et sous réserve de la réception de l’ensemble des pièces demandées.</p>

        <h2>Article 8 — Confidentialité</h2>
        <p>Le cabinet est tenu à une stricte confidentialité sur l’ensemble des informations et documents portés à sa connaissance. Le rapport est établi pour le seul client et ne peut être communiqué à un tiers qu’à sa demande ou sur réquisition judiciaire.</p>
        <p>Le client s’interdit d’en diffuser des extraits isolés susceptibles d’en dénaturer le sens.</p>

        <h2>Article 9 — Limites de la prestation</h2>
        <p>Sauf mission spécifique, l’expertise porte sur les <strong>éléments visibles et accessibles</strong> au jour de la visite. Elle n’a pas valeur de diagnostic réglementaire (amiante, plomb, termites, performance énergétique) ni d’étude de sol ou de calcul de structure.</p>
        <p>Le cabinet ne saurait être tenu responsable des désordres non décelables sans investigation destructive, ni de l’évolution ultérieure de désordres constatés à un instant donné.</p>

        <h2>Article 10 — Investigations complémentaires</h2>
        <p>Lorsque l’analyse requiert des sondages destructifs, une étude de sol, un essai en laboratoire ou l’intervention d’un tiers spécialisé, ces prestations font l’objet d’un devis distinct et de l’autorisation écrite du propriétaire. Leur coût n’est pas compris dans la mission initiale.</p>

        <h2>Article 11 — Force majeure</h2>
        <p>Le cabinet ne peut être tenu responsable d’un retard ou d’une inexécution résultant d’un événement de force majeure au sens de l’article 1218 du Code civil, notamment intempéries rendant la visite impossible, sinistre, ou impossibilité d’accès du fait du client ou d’un tiers.</p>

        <h2>Article 12 — Assurance</h2>
        <p>%(clause_assurance)s</p>

        <h2>Article 13 — Qualifications</h2>
        <p>Les missions sont conduites par un professionnel justifiant d’une expérience opérationnelle du bâtiment et de la conduite de travaux tous corps d’état, dans le respect des normes en vigueur, des DTU et des règles de l’art.</p>

        <h2>Article 14 — Propriété intellectuelle</h2>
        <p>Le rapport, ses annexes et les photographies qu’il contient demeurent la propriété intellectuelle du cabinet. Le client en reçoit un droit d’usage personnel pour les besoins du litige ou du projet concerné, à l’exclusion de toute exploitation commerciale ou publication.</p>

        <h2>Article 15 — Droit de rétractation</h2>
        <p>Conformément à l’article L.221-18 du Code de la consommation, le client consommateur dispose d’un délai de quatorze jours à compter de la conclusion du contrat à distance ou hors établissement pour se rétracter, sans motif ni pénalité.</p>
        <p>Lorsque le client demande expressément que la mission débute avant l’expiration de ce délai, il reste redevable des prestations déjà accomplies. La mission entièrement exécutée pendant ce délai, avec son accord préalable exprès, met fin au droit de rétractation.</p>
        <p>La rétractation s’exerce par déclaration écrite adressée à <a href="mailto:%(email)s">%(email)s</a>.</p>

        <h2>Article 16 — Incessibilité du contrat</h2>
        <p>La mission est conclue en considération de la personne du client. Elle ne peut être cédée à un tiers sans l’accord écrit du cabinet.</p>

        <h2>Article 17 — Médiation et litiges</h2>
        <p>En cas de difficulté, le client s’adresse d’abord au cabinet afin de rechercher une solution amiable.</p>
        <p>Conformément à l’article L.612-1 du Code de la consommation, le client consommateur peut recourir gratuitement à un médiateur de la consommation. Les coordonnées du médiateur compétent sont communiquées sur demande et figurent sur la lettre de mission.</p>
        <p>À défaut de résolution amiable, le litige relève des juridictions françaises compétentes. Le contrat est soumis au droit français.</p>
      </div>
    </div>
  </section>
""" % {
        "banniere": banniere("Conditions générales de vente",
                             "Le cadre contractuel de nos missions d’expertise et d’AMO.",
                             "12.webp", "Côte d’Azur"),
        "date_maj": LEGAL["date_maj"],
        "raison_sociale": LEGAL["raison_sociale"],
        "forme_juridique": LEGAL["forme_juridique"],
        "adresse": ADRESSE_COMPLETE,
        "email": SITE["email"],
        "clause_assurance": clause_assurance(),
    }

    PAGES.append(page(
        "conditions-generales-de-vente",
        "Conditions générales de vente | BTP Expertise",
        "Cadre contractuel des missions d’expertise en bâtiment et d’AMO : "
        "objet, tarifs, déroulement, limites, assurance et rétractation.",
        corps, "/conditions-generales-de-vente/", fil=fil,
    ))


def page_reglement():
    """Le paiement en ligne des missions.

    La page Honoraires a ete supprimee et la grille des tarifs avec elle :
    les montants de depart ne subsistent que dans le tableau ci-dessous et
    dans le resume de l'accueil. L'ancienne adresse /honoraires/ est
    redirigee ici par le .htaccess.
    """
    fil = [("Règlement de votre dossier", None)]

    def ligne(p):
        # Un montant fixe se règle en ligne ; une part des travaux ou un devis
        # ne se prépaient pas : ni « TTC », ni bouton, mais le renvoi au
        # règlement à montant libre, expliqué juste au-dessus.
        fixe = "€" in p["tarif"]
        devis = p["tarif"] == "Sur devis"

        montant = ("" if devis else '<span class="regler__depuis">à partir de</span>') \
                  + p["tarif"] + (' <span>TTC</span>' if fixe else "")

        if not fixe:
            action = '<span class="regler__libre">Montant de votre lettre de mission</span>'
        elif p["lien"] != "A_CONFIGURER":
            action = ('<a class="bouton bouton--bleu" href="%s" rel="noopener">Régler</a>'
                      % p["lien"])
        else:
            action = '<span class="bouton bouton--inactif" aria-disabled="true">Bientôt disponible</span>'

        # Le livrable ferme la description : c'est ce que le client garde.
        # Une mission d'AMO n'en a pas d'unique, la ligne s'arrête alors sur
        # ce qu'elle recouvre.
        contenu = " &middot; ".join(p["etapes"])
        if p.get("livrable"):
            contenu += " &middot; <strong>" + p["livrable"] + "</strong>"

        return """            <tr>
              <th scope="row">
                <span class="regler__mission">%s</span>
                <span class="regler__contenu">%s</span>
              </th>
              <td class="regler__montant">%s</td>
              <td class="regler__action">%s</td>
            </tr>""" % (p["nom"], contenu, montant, action)

    familles = []
    for titre, prestations in PAIEMENT["prestations"]:
        familles.append("""        <div class="regler__famille" data-anim>
          <h3>%s</h3>
          <table class="regler__table">
            <tbody>
%s
            </tbody>
          </table>
        </div>""" % (titre, "\n".join(ligne(p) for p in prestations)))

    libre_pret = PAIEMENT["lien_libre"] != "A_CONFIGURER"
    bouton_libre = ('<a class="bouton bouton--bleu" href="%s" rel="noopener">Payer en ligne</a>'
                    % PAIEMENT["lien_libre"] if libre_pret else
                    '<span class="bouton bouton--inactif" aria-disabled="true">Bientôt disponible</span>')

    corps = """%s

  <section class="section">
    <div class="conteneur">
      %s

      <div class="procedure">
        <div class="procedure__texte">
          <h3>Avant le règlement</h3>
          <p>Les règlements en ligne interviennent <strong>après un premier échange avec le cabinet</strong>. Vous devez être en possession d’une lettre de mission ou d’un devis, et nous l’avoir retourné signé.</p>
          <p>Si vous n’avez pas encore reçu votre lettre de mission, <a href="/contact/">prenez rendez-vous</a> : nous revenons vers vous sous 24 à 48 heures ouvrées.</p>
        </div>
        <div class="procedure__paiement">
          <h3>Règlement d’un autre montant</h3>
          <p>Pour un montant convenu qui ne figure pas dans la liste, saisissez vous-même la somme indiquée sur votre lettre de mission.</p>
          %s
          <p class="procedure__note">Le cabinet n’a jamais accès à vos données bancaires.</p>
        </div>
      </div>

      <div class="regler">
%s
      </div>

      <p class="regler__mention">%s</p>

      <p class="regler__mention">%s</p>

      <p class="centre saut" style="color:var(--texte-clair);font-size:.9rem">
        Un doute sur le montant à régler ? <a href="/contact/">Écrivez-nous</a>,
        nous vérifions votre dossier avant tout paiement.
        Conditions détaillées dans nos <a href="/conditions-generales-de-vente/">conditions générales de vente</a>.
      </p>
    </div>
  </section>

%s
""" % (
        banniere("Règlement de votre dossier",
                 "Réglez votre mission d’expertise en ligne, en paiement sécurisé.",
                 "6-e1770394485690.webp", "Règlement d’une mission d’expertise"),
        entete_bloc("Paiement en ligne",
                    "Règlement de <em>votre mission</em> en toute sécurité",
                    "Paiement par carte bancaire, traité par <img class=\"logo-stripe\" src=\"/assets/img/stripe.svg\" alt=\"Stripe\" width=\"41\" height=\"17\" loading=\"lazy\" decoding=\"async\">."),
        bouton_libre,
        "\n".join(familles),
        HONORAIRES_MENTION,
        AMO_MENTION,
        bandeau_appel(
            "Une question sur votre dossier ?",
            "Nous vérifions avec vous le montant et le contenu de votre mission."),
    )

    PAGES.append(page(
        "reglement",
        "Règlement de votre mission d’expertise | BTP Expertise",
        "Réglez votre mission d’expertise en ligne par carte bancaire. Paiement sécurisé Stripe, "
        "après réception de votre lettre de mission.",
        corps, "/reglement/", fil=fil,
    ))


# ---------------------------------------------------------------------------
# Fichiers techniques
# ---------------------------------------------------------------------------

def fichiers_techniques():
    urls = []
    for url in PAGES:
        priorite = "1.0" if url == "/" else (
            "0.9" if url in ("/expertises/", "/contact/", "/zones-intervention/") else "0.7")
        if url in ("/mentions-legales/", "/politique-de-confidentialite/",
                   "/conditions-generales-de-vente/"):
            priorite = "0.3"
        urls.append("""  <url>
    <loc>%s%s</loc>
    <changefreq>monthly</changefreq>
    <priority>%s</priority>
  </url>""" % (SITE["url"], url, priorite))

    sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
%s
</urlset>
""" % "\n".join(urls)
    io.open(os.path.join(SORTIE, "sitemap.xml"), "w", encoding="utf-8").write(sitemap)

    robots = """User-agent: *
Allow: /

Sitemap: %s/sitemap.xml
""" % SITE["url"]
    io.open(os.path.join(SORTIE, "robots.txt"), "w", encoding="utf-8").write(robots)

    # Favicon : genere depuis le pictogramme du logo, car build.py vide le
    # dossier de sortie a chaque passage (un fichier depose a la main serait perdu).
    from PIL import Image
    source = os.path.join(SORTIE, "assets", "img", ICONE)
    if os.path.exists(source):
        icone = Image.open(source).convert("RGBA")
        icone.resize((64, 64), Image.LANCZOS).save(
            os.path.join(SORTIE, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

    htaccess = """# BTP Expertise - configuration Apache (hebergement OVH)

Options -Indexes
DirectoryIndex index.html

# --- Redirection vers HTTPS et suppression du www ---
<IfModule mod_rewrite.c>
  RewriteEngine On

  RewriteCond %{HTTPS} !=on
  RewriteCond %{HTTP:X-Forwarded-Proto} !https
  RewriteRule ^(.*)$ https://btpexpertise.fr/$1 [R=301,L]

  RewriteCond %{HTTP_HOST} ^www\\.btpexpertise\\.fr$ [NC]
  RewriteRule ^(.*)$ https://btpexpertise.fr/$1 [R=301,L]

  # L'offre de maitrise d'oeuvre est devenue de l'assistance a maitrise
  # d'ouvrage : l'ancienne adresse est redirigee definitivement.
  # URL absolue : en relatif, OVH reconstruit l'adresse avec le port (:443).
  RewriteRule ^maitrise-doeuvre/?$ https://btpexpertise.fr/amo/ [R=301,L]

  # La page Honoraires a ete fondue dans la page Reglement. La regle couvre
  # aussi /honoraires/index.html : le fichier reste sur le serveur apres la
  # publication, la redirection passe avant lui.
  RewriteRule ^honoraires(/.*)?$ https://btpexpertise.fr/reglement/ [R=301,L]
</IfModule>

# --- Page 404 ---
ErrorDocument 404 /404.html

# --- Types MIME ---
<IfModule mod_mime.c>
  AddType image/webp .webp
  AddType image/svg+xml .svg
  AddType video/mp4 .mp4
  AddType font/woff2 .woff2
</IfModule>

# --- Compression ---
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css text/plain text/xml
  AddOutputFilterByType DEFLATE application/javascript application/json
  AddOutputFilterByType DEFLATE image/svg+xml
</IfModule>

# --- Cache navigateur ---
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus 1 hour"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType image/webp "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
  ExpiresByType video/mp4 "access plus 1 year"
</IfModule>

# --- En-tetes de securite ---
<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
  Header set X-Frame-Options "SAMEORIGIN"
</IfModule>
"""
    io.open(os.path.join(SORTIE, ".htaccess"), "w", encoding="utf-8").write(htaccess)


def page_404():
    corps = """%s

  <section class="section">
    <div class="conteneur centre">
      <h2>Que souhaitez-vous faire ?</h2>
      <div class="grille grille--3 saut">
        <a class="carte carte--gris" href="/expertises/"><h3>Nos expertises</h3><p>Les cinq missions du cabinet.</p></a>
        <a class="carte carte--gris" href="/zones-intervention/"><h3>Zones d’intervention</h3><p>Alpes-Maritimes et Var.</p></a>
        <a class="carte carte--gris" href="/contact/"><h3>Demander une étude</h3><p>Réponse sous 24 à 48 heures ouvrées.</p></a>
      </div>
    </div>
  </section>
""" % banniere("Cette page n’existe pas",
               "La page que vous cherchez a peut-être été déplacée, ou l’adresse comporte une erreur.",
               "12.webp", "Côte d’Azur")

    html = GABARIT.format(
        titre="Page introuvable | BTP Expertise",
        description="La page demandée n’existe pas sur btpexpertise.fr. Retrouvez nos expertises en "
                    "bâtiment dans les Alpes-Maritimes et le Var.",
        canonique=SITE["url"] + "/404.html",
        lat=SITE["latitude"], lon=SITE["longitude"],
        og_type="website",
        og_image=SITE["url"] + "/assets/img/BTP-Expertise-RIviera-Nice.webp",
        logo=LOGO,
        icone=ICONE,
        icone_touch=ICONE_TOUCH,
        prechargement="",
        jsonld=json.dumps(jsonld_cabinet(), ensure_ascii=False, separators=(",", ":")),
        entete=entete("/404"),
        corps=corps,
        pied=pied(),
        css=version("/assets/css/style.css"),
        js=version("/assets/js/site.js"),
    ).replace('<meta name="robots" content="index, follow, max-image-preview:large">',
              '<meta name="robots" content="noindex, follow">')
    io.open(os.path.join(SORTIE, "404.html"), "w", encoding="utf-8").write(html)


# ---------------------------------------------------------------------------
# Génération
# ---------------------------------------------------------------------------

def nettoyer():
    """Supprime les pages générées précédemment, sans toucher aux assets."""
    for entree in os.listdir(SORTIE):
        chemin = os.path.join(SORTIE, entree)
        if entree == "assets":
            continue
        if os.path.isdir(chemin):
            shutil.rmtree(chemin)
        else:
            os.remove(chemin)


def main():
    if not os.path.isdir(SORTIE):
        os.makedirs(SORTIE)
    nettoyer()

    page_accueil()
    page_qui_sommes_nous()
    page_expertises()
    page_amo()
    page_reseau()
    page_zones()
    for v in VILLES_PRIORITAIRES:
        page_ville(v)
    page_conseils()
    for art in ARTICLES_PUBLIES:
        page_article(art)
    page_faq()
    page_contact()
    page_mentions()
    page_confidentialite()
    page_cgv()
    page_reglement()

    page_404()
    fichiers_techniques()

    print("%d pages generees dans %s" % (len(PAGES), SORTIE))
    for url in PAGES:
        print("   %s" % url)


if __name__ == "__main__":
    main()
