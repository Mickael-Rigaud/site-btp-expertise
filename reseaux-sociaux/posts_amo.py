# -*- coding: utf-8 -*-
"""Quatre publications hors serie : deux pour vendre l'AMO, deux pour recruter.

Meme gabarit que posts_carte.py — meme grille, meme pied de marque, memes
themes nuit / papier — mais tenues a part : le feed de PUBLICATIONS.md est
calcule case par case, et ces quatre-la s'inserent quand Mickael le decide,
pas dans la serie de lancement.

    python reseaux-sociaux/posts_amo.py

Sortent en carre 1080, en 1080 x 1920 et en PDF vectoriel pour Canva, dans
visuels/planches/ et visuels/planches/pdf/.

Deux precautions de redaction, reprises de contenu.py :
  - l'AMO conseille et verifie, elle ne dirige pas les travaux, ne donne pas
    d'ordres aux entreprises et ne garantit ni delai ni budget ;
  - le cabinet travaille avec un reseau de professionnels **independants**,
    jamais des salaries : les annonces de recrutement le disent telles quelles.
"""

import os
import sys

DOSSIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DOSSIER)

from posts_carte import composer, SORTIE  # noqa: E402

MAIL = "contact@btpexpertise.fr"

CARTES = [
    # --- Vendre l'AMO ----------------------------------------------------
    # 1. Le declencheur. Le client n'est pas du batiment, l'entreprise si :
    #    c'est ce desequilibre-la que l'AMO corrige.
    {"cle": "amo-devis", "genre": "phrase", "entete": "Assistance à maîtrise d’ouvrage",
     "titre": "Trois devis, trois prix, trois solutions différentes.",
     "phrase": "En face, des professionnels du bâtiment. De votre côté, un professionnel "
               "du bâtiment aussi — qui compare, explique et vérifie. Vous décidez."},

    # 2. La mission, concretement. Les quatre lignes reprennent AMO[] de
    #    contenu.py sans jamais glisser vers la direction de travaux.
    {"cle": "amo-mission", "genre": "liste", "theme": "papier",
     "entete": "Assistance à maîtrise d’ouvrage",
     "titre": "Ce qu’on fait à vos côtés",
     "items": ["Définir précisément les travaux",
               "Consulter et comparer les entreprises",
               "Analyser les devis, ligne à ligne",
               "Visiter le chantier, assister à la réception"],
     "phrase": "Le cabinet conseille et vérifie. Vous restez décisionnaire et contractez "
               "directement avec les entreprises."},

    # --- Recruter --------------------------------------------------------
    # Independants deja installes, sur le 06 et le 83. Ne pas ecrire « poste »,
    # « CDI » ni « rejoignez l'equipe » : ce serait un autre statut.
    {"cle": "recrutement-amo", "genre": "liste", "entete": "Recrutement · 06 & 83",
     "titre": "Le cabinet cherche un AMO indépendant",
     "items": ["Dix ans de chantier derrière vous",
               "À l’aise avec un devis et un CCTP",
               "Déjà installé à votre compte",
               "Alpes-Maritimes ou Var"],
     "phrase": "Missions confiées par le cabinet, au sein d’un réseau de professionnels "
               "indépendants. Écrivez à " + MAIL},

    {"cle": "recrutement-expertise", "genre": "liste", "theme": "papier",
     "entete": "Recrutement · 06 & 83",
     "titre": "Le cabinet cherche un expert bâtiment indépendant",
     "items": ["Formation bâtiment et expérience terrain",
               "Fissures, humidité, malfaçons : la pathologie du bâti",
               "Un rapport écrit clair et défendable",
               "Statut indépendant, RC professionnelle à jour"],
     "phrase": "Interventions en Alpes-Maritimes et dans le Var. Écrivez à " + MAIL},
]


def pdf():
    """Les memes quatre cartes en PDF vectoriel, texte modifiable dans Canva."""
    import fitz
    import planches_pdf

    dossier = os.path.join(SORTIE, "pdf")
    tempo = os.path.join(dossier, "_tempo")
    os.makedirs(tempo, exist_ok=True)
    planches_pdf.TEMPO = tempo

    for taille, suffixe in (((1080, 1080), "-1080"), ((1080, 1920), "-story")):
        for carte in CARTES:
            document = fitz.open()
            planches_pdf.page_carte(document, carte, taille)
            document.save(os.path.join(dossier, "%s%s.pdf" % (carte["cle"], suffixe)),
                          garbage=3, deflate=True)
            document.close()

    for reste in os.listdir(tempo):
        os.remove(os.path.join(tempo, reste))
    os.rmdir(tempo)


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    for carte in CARTES:
        composer(carte, (1080, 1080), "-1080")
        composer(carte, (1080, 1920), "-story")
        print("%-22s carré + story" % carte["cle"])
    pdf()
    print("\nPDF Canva dans %s" % os.path.join(SORTIE, "pdf"))
