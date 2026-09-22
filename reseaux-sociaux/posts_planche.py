# -*- coding: utf-8 -*-
"""Direction « planche d'expertise » — visuels dessines, sans photo.

Le probleme des visuels precedents : ils reposaient sur les photos de banque
du site, que tout le monde utilise. Ici, rien n'est photographie. Chaque
publication est une planche technique : papier quadrille, schema au trait,
reperes annotes, et un cartouche en pied comme sur un plan.

    python reseaux-sociaux/posts_planche.py

Le dessin de chaque sujet est une fonction dediee, listee dans PLANCHES.
Formats : carre 1080 pour le fil, 1080 x 1920 pour les stories.
"""

import os
import sys

from PIL import Image, ImageDraw

DOSSIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DOSSIER)

from visuels import NUIT, BLEU, ORANGE, BLANC, GRAS, DEMI, NORMAL, logo, police, poser  # noqa: E402

SORTIE = os.path.join(DOSSIER, "visuels", "planches")

PAPIER = (238, 243, 248)
CARREAU = (214, 226, 237)
CARREAU_FORT = (196, 212, 227)
TRAIT = NUIT
GRIS = (110, 122, 145)


# ---------------------------------------------------------------------------
# Fond : papier quadrille et cartouche
# ---------------------------------------------------------------------------

def quadrillage(dessin, largeur, hauteur, pas=27):
    for i, x in enumerate(range(0, largeur + 1, pas)):
        dessin.line([(x, 0), (x, hauteur)], fill=CARREAU_FORT if i % 5 == 0 else CARREAU, width=1)
    for i, y in enumerate(range(0, hauteur + 1, pas)):
        dessin.line([(0, y), (largeur, y)], fill=CARREAU_FORT if i % 5 == 0 else CARREAU, width=1)


def lettrage(dessin, xy, texte, fonte, teinte, ecart=3.0):
    x, y = xy
    for lettre in texte:
        dessin.text((x, y), lettre, font=fonte, fill=teinte)
        x += dessin.textlength(lettre, font=fonte) + ecart
    return x


def couper(dessin, texte, fonte, largeur_max):
    lignes, ligne = [], ""
    for mot in texte.split():
        essai = (ligne + " " + mot).strip()
        if dessin.textlength(essai, font=fonte) <= largeur_max or not ligne:
            ligne = essai
        else:
            lignes.append(ligne)
            ligne = mot
    if ligne:
        lignes.append(ligne)
    return lignes


def repere(dessin, centre, numero, rayon=21):
    """Pastille numerotee, comme les renvois d'un rapport."""
    x, y = centre
    dessin.ellipse([x - rayon, y - rayon, x + rayon, y + rayon], fill=ORANGE)
    fonte = police(GRAS, 24)
    l = dessin.textlength(numero, font=fonte)
    dessin.text((x - l / 2, y - 15), numero, font=fonte, fill=NUIT)


def cote(dessin, depart, arrivee, texte, fonte):
    """Ligne de cote a double fleche, avec sa valeur au-dessus."""
    (x0, y), (x1, _) = depart, arrivee
    dessin.line([depart, arrivee], fill=GRIS, width=2)
    for x, sens in ((x0, 1), (x1, -1)):
        dessin.polygon([(x, y), (x + 12 * sens, y - 6), (x + 12 * sens, y + 6)], fill=GRIS)
    l = dessin.textlength(texte, font=fonte)
    dessin.rectangle([(x0 + x1) / 2 - l / 2 - 8, y - 17, (x0 + x1) / 2 + l / 2 + 8, y + 17],
                     fill=PAPIER)
    dessin.text(((x0 + x1) / 2 - l / 2, y - 13), texte, font=fonte, fill=GRIS)


def cartouche(dessin, fond, largeur, bas, marge):
    """Pied de planche : le cartouche d'un plan, avec ses cases."""
    haut = bas - 92
    dessin.rectangle([marge, haut, largeur - marge, bas], outline=TRAIT, width=2, fill=BLANC)

    picto = logo("picto.png")
    picto = picto.crop(picto.getbbox())
    poser(fond, picto, marge + 58, (haut + bas) / 2, 52)

    f_nom = police(GRAS, 27)
    f_petit = police(NORMAL, 21)
    dessin.text((marge + 100, haut + 22), "BTP EXPERTISE", font=f_nom, fill=NUIT)
    dessin.text((marge + 100, haut + 54), "Expertise bâtiment & AMO", font=f_petit, fill=GRIS)

    x_case = largeur - marge - 250
    dessin.line([(x_case, haut), (x_case, bas)], fill=TRAIT, width=2)
    dessin.text((x_case + 26, haut + 22), "Alpes-Maritimes · Var", font=f_petit, fill=GRIS)
    dessin.text((x_case + 26, haut + 50), "btpexpertise.fr", font=police(DEMI, 24), fill=BLEU)


# ---------------------------------------------------------------------------
# Schemas — un par sujet, dessines dans le cadre (x0, y0, x1, y1)
# ---------------------------------------------------------------------------

def schema_fissures(dessin, cadre):
    """Elevation d'un mur de blocs, fissure en escalier suivant les joints."""
    x0, y0, x1, y1 = cadre
    bloc_l, bloc_h = 118, 58
    rangees = int((y1 - y0) // bloc_h)
    haut_mur = y1 - rangees * bloc_h

    # Les joints, pas des blocs : rien ne peut deborder du mur.
    joint = (168, 182, 200)
    for r in range(1, rangees):
        y = haut_mur + r * bloc_h
        dessin.line([(x0, y), (x1, y)], fill=joint, width=2)
    for r in range(rangees):
        y = haut_mur + r * bloc_h
        x = x0 + (bloc_l / 2 if r % 2 else bloc_l)
        while x < x1 - 4:
            dessin.line([(x, y), (x, y + bloc_h)], fill=joint, width=2)
            x += bloc_l
    dessin.rectangle([x0, haut_mur, x1, y1], outline=TRAIT, width=3)

    # Fissure : elle monte en escalier depuis le pied, en s'ouvrant
    x, y = x0 + (x1 - x0) * 0.28, y1
    points = [(x, y)]
    for r in range(rangees - 1):
        y -= bloc_h
        points.append((x, y))
        x += bloc_l / 2 * (1 if r % 2 == 0 else 0.62)
        points.append((x, y))
    for i in range(len(points) - 1):
        epaisseur = 3 + int(7 * i / max(1, len(points) - 2))
        dessin.line([points[i], points[i + 1]], fill=ORANGE, width=epaisseur)

    f_note = police(NORMAL, 23)

    def annoter(ancre, numero, texte, dx=34):
        repere(dessin, ancre, numero)
        largeur = dessin.textlength(texte, font=f_note)
        cx = min(ancre[0] + dx, x1 - largeur)
        dessin.rectangle([cx - 8, ancre[1] - 17, cx + largeur + 8, ancre[1] + 17], fill=PAPIER)
        dessin.text((cx, ancre[1] - 13), texte, font=f_note, fill=NUIT)

    haut_fissure = points[-1]
    annoter((haut_fissure[0] + 44, haut_fissure[1] - 4), "1", "ouverture ≈ 4 mm")
    annoter((points[0][0] - 46, y1 - 34), "2", "amorce en pied")

    cote(dessin, (x0, y1 + 42), (x1, y1 + 42), "façade sud · 6,40 m", f_note)


def schema_humidite(dessin, cadre):
    """Coupe de mur : les trois origines possibles d'une meme tache."""
    x0, y0, x1, y1 = cadre
    sol = y1 - 90
    mur_x = x0 + (x1 - x0) * 0.38
    ep = 112

    # Terrain, en hachures
    dessin.rectangle([x0, sol, x1, sol + 60], outline=TRAIT, width=2)
    for x in range(int(x0), int(x1), 26):
        dessin.line([(x, sol + 60), (x + 26, sol)], fill=(178, 192, 209), width=1)

    # Mur en coupe et sa semelle
    dessin.rectangle([mur_x, y0 + 46, mur_x + ep, sol], outline=TRAIT, width=3, fill=(226, 234, 243))
    dessin.rectangle([mur_x - 34, sol, mur_x + ep + 34, sol + 42], outline=TRAIT, width=3,
                     fill=(226, 234, 243))

    f_note = police(NORMAL, 23)
    f_petit = police(DEMI, 21)
    dessin.text((x0, y0 - 6), "EXTÉRIEUR", font=f_petit, fill=GRIS)
    interieur = "INTÉRIEUR"
    dessin.text((x1 - dessin.textlength(interieur, font=f_petit), y0 - 6), interieur,
                font=f_petit, fill=GRIS)

    # 1 · infiltration par la façade
    y_inf = y0 + 96
    dessin.line([(mur_x - 150, y_inf), (mur_x + 6, y_inf + 26)], fill=BLEU, width=6)
    dessin.polygon([(mur_x + 16, y_inf + 30), (mur_x - 12, y_inf + 18), (mur_x - 6, y_inf + 40)],
                   fill=BLEU)
    repere(dessin, (mur_x - 186, y_inf - 8), "1")
    dessin.text((x0, y_inf + 26), "infiltration en façade", font=f_note, fill=NUIT)

    # 2 · remontee capillaire
    for i in range(3):
        x = mur_x + 20 + i * 34
        dessin.line([(x, sol - 12), (x, sol - 128)], fill=BLEU, width=5)
        dessin.polygon([(x, sol - 142), (x - 9, sol - 122), (x + 9, sol - 122)], fill=BLEU)
    repere(dessin, (mur_x + ep + 58, sol - 58), "2")
    dessin.text((mur_x + ep + 92, sol - 72), "remontée capillaire", font=f_note, fill=NUIT)

    # 3 · condensation cote interieur
    for i, dy in enumerate((0, 34, 68)):
        x = mur_x + ep + 24
        dessin.ellipse([x, y0 + 128 + dy, x + 16, y0 + 152 + dy], fill=BLEU)
    repere(dessin, (mur_x + ep + 92, y0 + 172), "3")
    dessin.text((mur_x + ep + 126, y0 + 158), "condensation", font=f_note, fill=NUIT)


def schema_reception(dessin, cadre):
    """Extrait de proces-verbal : les reserves, telles qu'elles sont ecrites."""
    x0, y0, x1, y1 = cadre
    entete_h = 52
    lignes = [
        ("1", "Séjour", "Jeu d’ouvrant sur la fenêtre ouest"),
        ("2", "Entrée", "Seuil non aligné, ressaut de 12 mm"),
        ("3", "Séjour", "Plinthe décollée sur 1,20 m"),
        ("4", "Chambre 1", "Fissure d’angle en plafond"),
    ]
    ligne_h = (y1 - y0 - entete_h) / len(lignes)

    dessin.rectangle([x0, y0, x1, y1], outline=TRAIT, width=3, fill=BLANC)
    dessin.rectangle([x0, y0, x1, y0 + entete_h], fill=NUIT)
    lettrage(dessin, (x0 + 26, y0 + 14), "PROCÈS-VERBAL DE RÉCEPTION · RÉSERVES",
             police(DEMI, 21), BLANC, 2.4)

    col_num = x0 + 70
    col_lieu = x0 + 300
    col_case = x1 - 78
    f_lieu = police(DEMI, 24)
    f_texte = police(NORMAL, 25)
    f_num = police(GRAS, 25)

    for i, (numero, lieu, reserve) in enumerate(lignes):
        haut = y0 + entete_h + i * ligne_h
        if i % 2:
            dessin.rectangle([x0 + 3, haut, x1 - 3, min(haut + ligne_h, y1 - 3)],
                             fill=(243, 246, 250))
        if i:
            dessin.line([(x0 + 3, haut), (x1 - 3, haut)], fill=(214, 226, 237), width=2)
        milieu = haut + ligne_h / 2

        dessin.text((x0 + 32, milieu - 16), numero, font=f_num, fill=ORANGE)
        dessin.text((col_num + 20, milieu - 16), lieu, font=f_lieu, fill=NUIT)
        dessin.text((col_lieu, milieu - 17), reserve, font=f_texte, fill=GRIS)

        # Case a cocher : la reserve reste ouverte tant qu'elle n'est pas levee
        dessin.rectangle([col_case, milieu - 15, col_case + 30, milieu + 15],
                         outline=(150, 164, 184), width=2)

    dessin.line([(col_num, y0 + entete_h), (col_num, y1)], fill=(214, 226, 237), width=2)
    dessin.line([(col_lieu - 26, y0 + entete_h), (col_lieu - 26, y1)], fill=(214, 226, 237), width=2)


def schema_plomberie(dessin, cadre):
    """Chute et branchement : la ou les desordres se lisent, aux raccords."""
    x0, y0, x1, y1 = cadre
    col_x = x0 + (x1 - x0) * 0.24
    ep = 46
    metal = (150, 164, 184)

    # Chute verticale
    dessin.rectangle([col_x, y0 + 20, col_x + ep, y1 - 20], outline=TRAIT, width=3,
                     fill=(226, 234, 243))
    for y in range(int(y0 + 90), int(y1 - 40), 120):      # colliers
        dessin.rectangle([col_x - 12, y, col_x + ep + 12, y + 16], outline=metal, width=2,
                         fill=BLANC)

    # Branchement horizontal, avec sa pente
    y_bran = y0 + (y1 - y0) * 0.42
    pente = 26
    dessin.polygon([(col_x + ep, y_bran), (x1 - 40, y_bran + pente),
                    (x1 - 40, y_bran + pente + ep), (col_x + ep, y_bran + ep)],
                   outline=TRAIT, fill=(226, 234, 243))
    dessin.line([(col_x + ep, y_bran), (x1 - 40, y_bran + pente)], fill=TRAIT, width=3)
    dessin.line([(col_x + ep, y_bran + ep), (x1 - 40, y_bran + pente + ep)], fill=TRAIT, width=3)

    # Fuite au raccord : quelques gouttes
    for i, dy in enumerate((0, 26, 52)):
        dessin.ellipse([col_x + ep + 16, y_bran + ep + 18 + dy,
                        col_x + ep + 32, y_bran + ep + 40 + dy], fill=BLEU)

    f_note = police(NORMAL, 23)

    def annoter(ancre, numero, texte):
        repere(dessin, ancre, numero)
        largeur = dessin.textlength(texte, font=f_note)
        cx = min(ancre[0] + 34, x1 - largeur)
        dessin.rectangle([cx - 8, ancre[1] - 17, cx + largeur + 8, ancre[1] + 17], fill=PAPIER)
        dessin.text((cx, ancre[1] - 13), texte, font=f_note, fill=NUIT)

    # Les deux renvois se posent hors du tuyau, sinon ils le masquent.
    annoter((col_x + ep + 30, y_bran - 62), "1", "raccord suintant")
    annoter((x1 - 340, y_bran + pente + ep + 62), "2", "pente insuffisante")
    dessin.line([(col_x + ep + 30, y_bran - 40), (col_x + ep + 30, y_bran - 4)],
                fill=GRIS, width=2)
    dessin.text((x0, y0 + 20), "chute EU / EV", font=police(DEMI, 21), fill=GRIS)


def schema_electricite(dessin, cadre):
    """Tableau divisionnaire : ce qu'on regarde d'abord, rangee par rangee."""
    x0, y0, x1, y1 = cadre
    cadre_h = min(y1 - y0 - 40, 300)
    haut = y0 + (y1 - y0 - cadre_h) / 2
    dessin.rectangle([x0 + 60, haut, x1 - 60, haut + cadre_h], outline=TRAIT, width=3, fill=BLANC)

    rail_y = haut + 60
    dessin.line([(x0 + 84, rail_y - 14), (x1 - 84, rail_y - 14)], fill=(178, 192, 209), width=3)

    module_l, module_h, ecart = 52, 108, 12
    x = x0 + 100
    manquants = {5}
    for i in range(9):
        if i in manquants:
            dessin.rectangle([x, rail_y, x + module_l, rail_y + module_h],
                             outline=(178, 192, 209), width=2)
            for d in range(0, int(module_h), 18):        # emplacement libre, hachure
                dessin.line([(x, rail_y + d), (x + module_l, rail_y + d + 18)],
                            fill=(214, 226, 237), width=1)
        else:
            teinte = ORANGE if i == 0 else (226, 234, 243)
            dessin.rectangle([x, rail_y, x + module_l, rail_y + module_h],
                             outline=TRAIT, width=2, fill=teinte)
            dessin.rectangle([x + 14, rail_y + 24, x + module_l - 14, rail_y + 62],
                             outline=TRAIT, width=2, fill=BLANC)
        x += module_l + ecart

    f_note = police(NORMAL, 23)
    f_petit = police(DEMI, 21)
    dessin.text((x0 + 60, haut - 34), "TABLEAU DIVISIONNAIRE", font=f_petit, fill=GRIS)

    def annoter(ancre, numero, texte):
        repere(dessin, ancre, numero)
        largeur = dessin.textlength(texte, font=f_note)
        cx = min(ancre[0] + 34, x1 - largeur)
        dessin.rectangle([cx - 8, ancre[1] - 17, cx + largeur + 8, ancre[1] + 17], fill=PAPIER)
        dessin.text((cx, ancre[1] - 13), texte, font=f_note, fill=NUIT)

    annoter((x0 + 126, rail_y + module_h + 46), "1", "différentiel en tête")
    # Le renvoi 2 pointe un module en service, pas l'emplacement libre :
    # ce qu'on releve, c'est l'absence de reperage.
    annoter((x0 + 100 + 6 * (module_l + ecart) + 26, rail_y + module_h + 46), "2",
            "circuit non repéré")


def legende(dessin, x, y, entrees, pas=52):
    """Colonne de renvois numerotes, posee a cote du dessin."""
    f_note = police(NORMAL, 24)
    for i, texte in enumerate(entrees):
        repere(dessin, (x, y + i * pas), str(i + 1), rayon=18)
        dessin.text((x + 32, y + i * pas - 14), texte, font=f_note, fill=NUIT)


def schema_avant_achat(dessin, cadre):
    """Elevation d'une maison : les cinq points regardes avant une signature."""
    x0, y0, x1, y1 = cadre
    large = (x1 - x0) * 0.40
    haut = y1 - y0 - 40
    mx = x0 + 30
    sol = y1 - 20

    corps_h = haut * 0.58
    toit_h = haut * 0.32
    corps_y = sol - corps_h

    dessin.polygon([(mx - 26, corps_y), (mx + large / 2, corps_y - toit_h),
                    (mx + large + 26, corps_y)], outline=TRAIT, fill=(226, 234, 243))
    dessin.line([(mx - 26, corps_y), (mx + large / 2, corps_y - toit_h)], fill=TRAIT, width=3)
    dessin.line([(mx + large / 2, corps_y - toit_h), (mx + large + 26, corps_y)],
                fill=TRAIT, width=3)

    dessin.rectangle([mx, corps_y, mx + large, sol], outline=TRAIT, width=3, fill=BLANC)
    dessin.line([(x0, sol), (mx + large + 60, sol)], fill=TRAIT, width=3)

    f_l, f_h = large * 0.20, corps_h * 0.28
    for i in (0, 1):
        fx = mx + large * (0.10 + i * 0.56)
        fy = corps_y + corps_h * 0.16
        dessin.rectangle([fx, fy, fx + f_l, fy + f_h], outline=TRAIT, width=2)
        dessin.line([(fx + f_l / 2, fy), (fx + f_l / 2, fy + f_h)], fill=TRAIT, width=2)
    px = mx + large * 0.40
    dessin.rectangle([px, sol - corps_h * 0.44, px + large * 0.20, sol],
                     outline=TRAIT, width=2)

    # Fissure d'angle : le motif qui revient le plus souvent
    dessin.line([(mx + large * 0.88, corps_y + 16), (mx + large * 0.96, corps_y + corps_h * 0.36)],
                fill=ORANGE, width=5)

    for numero, point in (("1", (mx + large / 2, corps_y - toit_h * 0.45)),
                          ("2", (mx + large * 0.92, corps_y + corps_h * 0.26)),
                          ("3", (mx + large * 0.18, corps_y + corps_h * 0.30)),
                          ("4", (px + large * 0.10, sol - corps_h * 0.22)),
                          ("5", (mx + large * 0.06, sol - 24))):
        repere(dessin, point, numero, rayon=18)

    legende(dessin, x0 + (x1 - x0) * 0.58, y0 + 14, [
        "Toiture et couverture",
        "Fissures et structure",
        "Menuiseries et étanchéité",
        "Réseaux et installations",
        "Humidité en pied de mur",
    ])


def schema_argiles(dessin, cadre):
    """Retrait-gonflement des argiles : premiere cause de fissures dans le 06 et le 83."""
    x0, y0, x1, y1 = cadre
    sol = y0 + (y1 - y0) * 0.52
    mx = x0 + 40
    large = (x1 - x0) * 0.30
    corps_h = (sol - y0) * 0.62

    dessin.rectangle([mx, sol - corps_h, mx + large, sol], outline=TRAIT, width=3, fill=BLANC)
    dessin.polygon([(mx - 22, sol - corps_h), (mx + large / 2, sol - corps_h - 58),
                    (mx + large + 22, sol - corps_h)], outline=TRAIT, fill=(226, 234, 243))
    dessin.line([(mx - 22, sol - corps_h), (mx + large / 2, sol - corps_h - 58)],
                fill=TRAIT, width=3)
    dessin.line([(mx + large / 2, sol - corps_h - 58), (mx + large + 22, sol - corps_h)],
                fill=TRAIT, width=3)

    points = [(mx + large * 0.60, sol), (mx + large * 0.60, sol - corps_h * 0.32),
              (mx + large * 0.74, sol - corps_h * 0.32), (mx + large * 0.74, sol - corps_h * 0.62),
              (mx + large * 0.88, sol - corps_h * 0.62)]
    for i in range(len(points) - 1):
        dessin.line([points[i], points[i + 1]], fill=ORANGE, width=6)

    # Terrain argileux, en hachures
    dessin.rectangle([x0, sol, x1 - 300, y1], outline=TRAIT, width=2, fill=(240, 234, 224))
    for x in range(int(x0), int(x1 - 300), 30):
        dessin.line([(x, y1), (min(x + 40, x1 - 300), sol)], fill=(208, 196, 180), width=1)
    dessin.text((x0 + 10, sol + 12), "ARGILE", font=police(DEMI, 21), fill=(150, 132, 106))

    # Le sol se derobe sous une partie de la maison
    creux = [(mx + large * 0.36, sol + 8), (mx + large * 0.78, sol + 74),
             (mx + large * 1.30, sol + 8)]
    dessin.line([creux[0], creux[1]], fill=BLEU, width=5)
    dessin.line([creux[1], creux[2]], fill=BLEU, width=5)
    for x, dy in ((mx + large * 0.62, 0), (mx + large * 0.86, 0)):
        dessin.line([(x, sol + 16), (x, sol + 52)], fill=BLEU, width=4)
        dessin.polygon([(x, sol + 66), (x - 9, sol + 46), (x + 9, sol + 46)], fill=BLEU)

    legende(dessin, x1 - 280, y0 + 10, [
        "Été sec : l’argile se rétracte",
        "Le sol se dérobe d’un côté",
        "Fissures en escalier",
    ])
    dessin.text((x1 - 280, y0 + 10 + 3 * 52 + 6),
                "L’hiver, le sol regonfle :",
                font=police(NORMAL, 23), fill=GRIS)
    dessin.text((x1 - 280, y0 + 10 + 3 * 52 + 36),
                "la fissure « respire ».",
                font=police(NORMAL, 23), fill=GRIS)


def schema_etancheite(dessin, cadre):
    """Coupe d'une toiture-terrasse : l'eau passe presque toujours par le releve."""
    x0, y0, x1, y1 = cadre
    gauche = x0 + 20
    droite = x0 + (x1 - x0) * 0.56          # le tiers droit est reserve a la legende
    haut = y0 + 118                          # place laissee a l'acrotere, qui monte

    dalle, isolant = 56, 34
    dessin.rectangle([gauche, haut, droite, haut + dalle],
                     outline=TRAIT, width=2, fill=(222, 228, 238))
    dessin.rectangle([gauche, haut + dalle, droite, haut + dalle + isolant],
                     outline=TRAIT, width=2, fill=(240, 236, 226))
    bas = haut + dalle + isolant
    milieu_isolant = haut + dalle + isolant / 2

    acro_x = droite
    dessin.rectangle([acro_x, haut - 100, acro_x + 42, bas],
                     outline=TRAIT, width=3, fill=(222, 228, 238))

    # L'etancheite court sur la terrasse puis remonte le long de l'acrotere
    dessin.line([(gauche + 4, haut - 3), (acro_x, haut - 3)], fill=NUIT, width=7)
    dessin.line([(acro_x, haut - 3), (acro_x, haut - 82)], fill=NUIT, width=7)
    # Le releve se decolle : c'est par la que l'eau entre
    dessin.line([(acro_x - 4, haut - 36), (acro_x - 34, haut - 84)], fill=ORANGE, width=6)

    for dy in (0, 28, 56):
        dessin.ellipse([acro_x - 96, bas + 22 + dy, acro_x - 80, bas + 44 + dy], fill=BLEU)

    dessin.text((gauche, haut - 148), "TOITURE-TERRASSE", font=police(DEMI, 21), fill=GRIS)
    for numero, point in (("1", (acro_x - 54, haut - 76)),
                          ("2", (gauche + 80, milieu_isolant)),
                          ("3", (acro_x - 132, bas + 62))):
        repere(dessin, point, numero, rayon=18)

    legende(dessin, x0 + (x1 - x0) * 0.68, haut - 40, [
        u"Relevé décollé",
        u"Isolant gorgé d’eau",
        u"Tache au plafond",
    ])


def schema_parcours(dessin, cadre):
    """Ce qui se passe entre l'appel et le rapport."""
    x0, y0, x1, y1 = cadre
    milieu = (y0 + y1) / 2 - 16
    etapes = ["Prise de contact", "Devis et périmètre", "Visite sur site",
              "Analyse technique", "Rapport remis"]
    pas = (x1 - x0 - 80) / (len(etapes) - 1)

    dessin.line([(x0 + 40, milieu), (x1 - 40, milieu)], fill=(178, 192, 209), width=4)
    f_note = police(DEMI, 23)
    for i, texte in enumerate(etapes):
        x = x0 + 40 + i * pas
        repere(dessin, (x, milieu), str(i + 1), rayon=26)
        mots = texte.split(" ")
        lignes = [texte] if dessin.textlength(texte, font=f_note) <= pas - 16 else \
            [" ".join(mots[:len(mots) // 2 or 1]), " ".join(mots[len(mots) // 2 or 1:])]
        yy = milieu + 48
        for ligne in lignes:
            l = dessin.textlength(ligne, font=f_note)
            dessin.text((x - l / 2, yy), ligne, font=f_note, fill=NUIT)
            yy += 30


SCHEMAS = {
    "fissures": schema_fissures,
    "humidite": schema_humidite,
    "reception": schema_reception,
    "plomberie": schema_plomberie,
    "electricite": schema_electricite,
    "avant-achat-planche": schema_avant_achat,
    "argiles": schema_argiles,
    "etancheite": schema_etancheite,
    "parcours": schema_parcours,
}

# cle, entete de planche, titre, phrase
PLANCHES = [
    ("fissures", "Relevé technique · fissures",
     "Toutes les fissures ne se valent pas",
     "Forme, orientation, évolution : c’est l’analyse qui dit s’il faut surveiller ou reprendre."),
    ("humidite", "Coupe de principe · humidité",
     "Trois origines, une seule tache",
     "Infiltration, remontée capillaire ou condensation : même mur, traitements très différents."),
    ("reception", "Extrait de PV · réception de travaux",
     "Le jour de la réception, tout se joue",
     "Ce qui n’est pas noté en réserve devient beaucoup plus difficile à faire reprendre ensuite."),
    ("plomberie", "Schéma de principe · plomberie",
     "Les désordres se lisent aux raccords",
     "Alimentations, évacuations, pentes, fuites : l’origine est rarement là où l’eau apparaît."),
    ("electricite", "Relevé · installation électrique",
     "Un tableau se lit avant d’être touché",
     "Protections, circuits, repérage, mise à la terre : anomalies apparentes et défauts de mise en œuvre."),
    ("avant-achat-planche", "Points de contrôle · avant achat",
     "Cinq points avant de signer",
     "Une visite avec un agent immobilier n’est pas un examen technique du bâtiment."),
    ("argiles", "Coupe de terrain · sécheresse",
     "Quand c’est le sol qui bouge",
     "Retrait-gonflement des argiles : la cause la plus fréquente de fissures dans le 06 et le 83."),
    ("etancheite", "Coupe · toiture-terrasse",
     "L’eau passe presque toujours par le relevé",
     "Étanchéité, relevé contre acrotère, isolant : le trajet de l’eau se remonte, il ne se devine pas."),
    ("parcours", "Déroulé · mission d’expertise",
     "De votre appel au rapport",
     "Cinq étapes, et un périmètre défini par devis avant toute intervention."),
]


def mesures(taille, titre, phrase, dessin):
    """Positions de la planche, sans rien dessiner.

    Partagee avec planches_pdf.py : les PNG et les PDF se calent ainsi sur les
    memes reperes, et une retouche de gabarit vaut pour les deux.
    """
    largeur, hauteur = taille
    story = hauteur > largeur
    marge = 64 if not story else 76

    m = {
        "largeur": largeur, "hauteur": hauteur, "marge": marge,
        "corps": {"entete": 23 if not story else 25,
                  "titre": 58 if not story else 64,
                  "phrase": 29 if not story else 33},
        "inter_titre": 1.2, "inter_phrase": 1.45,
        "y_entete": marge + (0 if not story else 120),
        "bas_cartouche": hauteur - marge - (0 if not story else 150),
    }
    f_titre = police(GRAS, m["corps"]["titre"])
    f_phrase = police(NORMAL, m["corps"]["phrase"])
    utile = largeur - 2 * marge
    m["lignes_titre"] = couper(dessin, titre, f_titre, utile)
    m["lignes_phrase"] = couper(dessin, phrase, f_phrase, utile)

    m["haut_texte"] = (m["bas_cartouche"] - 92 - 46
                       - len(m["lignes_phrase"]) * m["corps"]["phrase"] * m["inter_phrase"]
                       - 22
                       - len(m["lignes_titre"]) * m["corps"]["titre"] * m["inter_titre"])
    m["cadre_schema"] = (marge + 30, m["y_entete"] + m["corps"]["entete"] + 74,
                         largeur - marge - 30, m["haut_texte"] - 86)
    return m


def calque_schema(cle, taille, m):
    """Le schema seul, sur fond transparent — pour la version PDF."""
    calque = Image.new("RGBA", taille, (0, 0, 0, 0))
    SCHEMAS[cle](ImageDraw.Draw(calque), m["cadre_schema"])
    return calque


def composer(cle, entete, titre, phrase, taille, suffixe):
    largeur, hauteur = taille
    fond = Image.new("RGBA", (largeur, hauteur), PAPIER + (255,))
    dessin = ImageDraw.Draw(fond)
    quadrillage(dessin, largeur, hauteur)

    m = mesures(taille, titre, phrase, dessin)
    marge = m["marge"]
    f_entete = police(DEMI, m["corps"]["entete"])
    f_titre = police(GRAS, m["corps"]["titre"])
    f_phrase = police(NORMAL, m["corps"]["phrase"])

    y = m["y_entete"]
    x = lettrage(dessin, (marge, y), entete.upper(), f_entete, NUIT)
    dessin.line([(marge, y + f_entete.size + 16), (x - 3, y + f_entete.size + 16)],
                fill=ORANGE, width=4)

    yy = m["haut_texte"]
    for ligne in m["lignes_titre"]:
        dessin.text((marge, yy), ligne, font=f_titre, fill=NUIT)
        yy += m["corps"]["titre"] * m["inter_titre"]
    yy += 22
    for ligne in m["lignes_phrase"]:
        dessin.text((marge, yy), ligne, font=f_phrase, fill=GRIS)
        yy += m["corps"]["phrase"] * m["inter_phrase"]

    SCHEMAS[cle](dessin, m["cadre_schema"])
    cartouche(dessin, fond, largeur, m["bas_cartouche"], marge)

    chemin = os.path.join(SORTIE, "%s%s.png" % (cle, suffixe))
    fond.convert("RGB").save(chemin)
    return chemin


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    for cle, entete, titre, phrase in PLANCHES:
        composer(cle, entete, titre, phrase, (1080, 1080), "-1080")
        composer(cle, entete, titre, phrase, (1080, 1920), "-story")
        print("%-12s carre + story" % cle)
