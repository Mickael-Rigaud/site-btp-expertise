# -*- coding: utf-8 -*-
"""Génère la carte SVG des zones d'intervention à partir des contours IGN.

Les contours communaux (geo.api.gouv.fr) sont projetés, simplifiés puis écrits
dans contenu.py sous forme de tracés SVG. Script à usage unique : relancer
uniquement si les contours doivent être régénérés.
"""
import io
import json
import math

FICHIERS = {"06": "_geo06.json", "83": "_geo83.json"}
LARGEUR = 1000.0          # largeur du viewBox
TOLERANCE = 1.1          # simplification, en unites du viewBox


def charger():
    communes = []
    for dept, fichier in FICHIERS.items():
        data = json.load(io.open(fichier, encoding="utf-8"))
        for f in data["features"]:
            g = f["geometry"]
            anneaux = []
            if g["type"] == "Polygon":
                anneaux = [g["coordinates"][0]]
            elif g["type"] == "MultiPolygon":
                anneaux = [p[0] for p in g["coordinates"]]
            communes.append({
                "dept": dept,
                "nom": f["properties"]["nom"],
                "code": f["properties"]["code"],
                "anneaux": anneaux,
            })
    return communes


def bornes(communes):
    xs, ys = [], []
    for c in communes:
        for a in c["anneaux"]:
            for lon, lat in a:
                xs.append(lon)
                ys.append(lat)
    return min(xs), max(xs), min(ys), max(ys)


def simplifier_anneau(points, tol):
    """Simplifie un contour fermé.

    Douglas-Peucker s'applique à une ligne ouverte : sur un anneau, le premier
    et le dernier point coïncident, la droite de référence est dégénérée et
    tous les écarts valent zéro. On coupe donc l'anneau en deux arcs.
    """
    if len(points) > 1 and points[0] == points[-1]:
        points = points[:-1]
    if len(points) < 4:
        return points
    milieu = len(points) // 2
    a = simplifier(points[:milieu + 1], tol)
    b = simplifier(points[milieu:], tol)
    return a[:-1] + b[:-1]


def simplifier(points, tol):
    """Douglas-Peucker itératif, sur une ligne ouverte."""
    if len(points) < 3:
        return points
    garde = [False] * len(points)
    garde[0] = garde[-1] = True
    pile = [(0, len(points) - 1)]
    while pile:
        d, f = pile.pop()
        if f <= d + 1:
            continue
        x1, y1 = points[d]
        x2, y2 = points[f]
        dx, dy = x2 - x1, y2 - y1
        norme = math.hypot(dx, dy) or 1e-9
        pire, rang = 0.0, -1
        for i in range(d + 1, f):
            x, y = points[i]
            ecart = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / norme
            if ecart > pire:
                pire, rang = ecart, i
        if pire > tol:
            garde[rang] = True
            pile.append((d, rang))
            pile.append((rang, f))
    return [p for p, g in zip(points, garde) if g]


def main():
    communes = charger()
    lon_min, lon_max, lat_min, lat_max = bornes(communes)

    # Projection équirectangulaire corrigée par la latitude moyenne : à cette
    # échelle, elle est fidèle et évite d'embarquer une bibliothèque.
    lat_moy = math.radians((lat_min + lat_max) / 2)
    k = math.cos(lat_moy)
    l_geo = (lon_max - lon_min) * k
    h_geo = lat_max - lat_min
    echelle = LARGEUR / l_geo
    hauteur = round(h_geo * echelle, 1)

    def projeter(lon, lat):
        return ((lon - lon_min) * k * echelle,
                (lat_max - lat) * echelle)

    sortie = []
    for c in communes:
        tracés = []
        for anneau in c["anneaux"]:
            pts = [projeter(lon, lat) for lon, lat in anneau]
            pts = simplifier_anneau(pts, TOLERANCE)
            if len(pts) < 3:
                continue
            d = "M" + " ".join("%.1f %.1f" % p for p in pts) + "Z"
            tracés.append(d)
        if tracés:
            sortie.append((c["dept"], c["nom"], c["code"], "".join(tracés)))

    total = sum(len(t[3]) for t in sortie)
    print("%d communes, %d Ko de trace, viewBox 0 0 %d %.0f"
          % (len(sortie), total / 1024, LARGEUR, hauteur))

    lignes = ["CARTE_VIEWBOX = \"0 0 %d %.0f\"" % (LARGEUR, hauteur), "", "CARTE_COMMUNES = ["]
    for dept, nom, code, d in sortie:
        lignes.append('    ("%s", "%s", "%s",\n     "%s"),'
                      % (dept, nom.replace('"', "'"), code, d))
    lignes.append("]")

    # Position des villes mises en avant
    villes = {
        "Nice": (7.2620, 43.7102), "Cannes": (7.0174, 43.5528),
        "Antibes": (7.1251, 43.5808), "Grasse": (6.9225, 43.6591),
        "Menton": (7.5027, 43.7765), "Cagnes-sur-Mer": (7.1487, 43.6637),
        "Toulon": (5.9280, 43.1242), "Hyères": (6.1286, 43.1205),
        "Fréjus": (6.7370, 43.4331), "Draguignan": (6.4666, 43.5404),
        "Saint-Tropez": (6.6407, 43.2677), "Brignoles": (6.0611, 43.4064),
    }
    lignes += ["", "CARTE_VILLES = ["]
    for nom, (lon, lat) in villes.items():
        x, y = projeter(lon, lat)
        dept = "06" if lon > 6.65 else "83"
        lignes.append('    ("%s", "%s", %.1f, %.1f),' % (nom, dept, x, y))
    lignes.append("]")

    io.open("_carte_donnees.py", "w", encoding="utf-8").write("\n".join(lignes) + "\n")
    print("donnees ecrites dans _carte_donnees.py")


main()
