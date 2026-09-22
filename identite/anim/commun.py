# -*- coding: utf-8 -*-
"""Geometrie et reglages partages par les animations du logo BTP Expertise.

Repere : celui du logo d'origine (1600 x 1303), coin haut-gauche a (0,0).
Le cadre des animations est plus large, pour que la loupe reste entiere a
l'image pendant ses deplacements et que son manche ne soit pas coupe.
"""

# --- cadre ------------------------------------------------------------------
LOGO_W, LOGO_H = 1600, 1303
VUE_X, VUE_Y = -110, -110          # coin haut-gauche du cadre, dans le repere du logo
VUE_W, VUE_H = 1820, 1700
MARGE_X, MARGE_Y = -VUE_X, -VUE_Y  # a ajouter aux coordonnees du logo

# --- loupe ------------------------------------------------------------------
CX, CY = 863, 518        # centre du verre
R_VERRE = 505            # deborde sous l'anneau, qui le recouvre
SOL = 977                # ligne de base des batiments
ECH = 0.72               # taille des batiments hors du verre
K = 1 / ECH              # grossissement du verre : ECH * K = 1

# --- manche -----------------------------------------------------------------
# Le manche du logo est un parallelogramme incline (pente 0,4) que l'image
# d'origine coupe net a son bord inferieur. On le redessine pour l'animation :
#   HAUT   : de la sortie du cercle jusqu'a la ligne de base du texte. Cette
#            portion n'existe pas dans le logo (le mot passe par-dessus), elle
#            n'est donc affichee que tant que le nom n'est pas encore revele.
#   BAS    : le prolongement, toujours visible. Il recouvre exactement le bout
#            de manche du logo entre 1240 et 1303, puis continue jusqu'a une
#            coupe perpendiculaire a l'axe.
def _bord(y, x0):
    return x0 + 0.4 * (y - 1040)


MANCHE_HAUT = [(_bord(1042, 986), 1042), (_bord(1042, 1117), 1042),
               (_bord(1244, 1117), 1244), (_bord(1244, 986), 1244)]
MANCHE_BAS = [(_bord(1240, 986), 1240), (_bord(1240, 1117), 1240),
              (1279, 1445), (1166, 1490)]

ENCRE = (38, 44, 66)          # bleu nuit du logo
ENCRE_SOMBRE = (255, 255, 255)  # sa contrepartie sur fond sombre


def chemin(points):
    """Les points d'un polygone, en commande de path SVG."""
    return "M" + " L".join("%.0f,%.0f" % p for p in points) + " Z"
