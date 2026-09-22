# Logo anime BTP Expertise

Le logo d'origine (`identite/logo-principal.png`) decoupe en calques, puis reconstruit
en animation. Aucun pixel n'a ete redessine : les calques sont des morceaux exacts du
PNG, et l'image finale redonne le logo au pixel pres (`python rendu.py diff` le verifie).

Une seule chose a ete ajoutee : **le manche de la loupe est prolonge**. Le fichier
d'origine le coupe net a son bord inferieur, ce qui empeche de reconnaitre une loupe
tant qu'elle bouge. Le prolongement est un polygone (`commun.py`), pose dans le
prolongement exact du manche existant et termine par une coupe perpendiculaire.
Le cadre des animations est donc plus large que le logo : 1820 x 1700 au lieu de
1600 x 1303, ce qui laisse aussi a la loupe la place de se deplacer sans etre coupee.

## Les quatre animations

| Nom | Ce qui se passe | Duree |
|---|---|---|
| **construction** | Les etages montent, les tours poussent, le cercle se trace, le manche descend, le nom se revele. | 3,5 s |
| **balayage** | Les batiments sont poses a 72 % ; la loupe entre par la gauche et grossit x1,39 ce qui passe sous le verre. | 3,3 s |
| **inspection** | Meme principe, mais la loupe s'arrete sur chaque batiment avant de se caler. | 4,4 s |
| **mise-au-point** | La loupe ne bouge pas : c'est le grossissement qui monte de x1 a x1,39. | 3,8 s |

Le grossissement tombe juste : les batiments sont a 72 % et le verre grossit de
1 / 0,72 = 1,39. Quand la loupe est au centre, les deux facteurs s'annulent et on
retrouve exactement le logo.

## Fichiers livres

Pour chaque animation :

| Fichier | Usage |
|---|---|
| `logo-anime<-nom>.svg` | Le site. Net a toute taille, ~550 ko. Fond clair + fond sombre inclus. |
| `logo-anime<-nom>.mp4` | 1080x1008, 30 i/s. Reseaux, intro de video. |
| `logo-anime<-nom>-carre.mp4` | 1080x1080. Instagram, LinkedIn. |
| `logo-anime<-nom>.gif` | 640 px, en boucle. Signature mail, message. |
| `apercu<-nom>.html` | Page de test : rejouer, ralenti, fond sombre, curseur image par image. |

(l'animation `construction` n'a pas de suffixe : `logo-anime.svg`, `logo-anime.mp4`...)

## Fond sombre

Le SVG contient les deux versions. Par defaut il s'affiche en bleu nuit (fond clair).
Pour la version blanche, ajouter la classe `sur-sombre` sur la balise `<svg>` :

```js
document.querySelector('.logo-anime').classList.add('sur-sombre');
```

## Poser le SVG sur le site

Deux facons :
- `<img src="logo-anime.svg" alt="BTP Expertise">` — simple, mais l'animation part
  au chargement de l'image et le fond sombre n'est pas pilotable.
- Coller le contenu du fichier directement dans la page (SVG inline) — permet de
  rejouer l'animation et de basculer en fond sombre depuis le JS de la page.

## Regenerer

```
python decouper-calques.py               # refait les calques depuis les PNG du logo
python faire-anime.py                    # logo-anime.svg + apercu.html
python faire-anime-loupe.py              # les trois SVG de la famille loupe
python rendu.py planche                  # planche de controle (12 images cles)
python rendu.py diff                     # l'image finale contre le logo d'origine
python rendu.py frames                   # les PNG dans frames/
python rendu-loupe.py inspection frames  # idem pour une variante
python exporter.py                       # assemble tous les MP4 et GIF avec ffmpeg
```

## A savoir avant de modifier

La choregraphie est decrite deux fois : en CSS dans `faire-anime*.py` (pour le SVG)
et en Python dans `rendu*.py` (pour les videos). Modifier un timing demande de le
changer aux deux endroits, puis de relancer `rendu.py diff` pour verifier que
l'image finale colle toujours au logo d'origine.

Pieges rencontres, a ne pas reintroduire :

- **le manche n'est pas separable du texte.** Dans l'image d'origine il passe derriere
  le R de EXPERTISE et les deux formes sont soudees, le R creuse en negatif dans le
  manche. Le manche affiche pendant l'animation est donc redessine, et il est retire
  au fur et a mesure que le balayage du nom passe dessus (`cWipeInv`).
- **les pixels de transition entre deux couleurs** (la ou un batiment touche l'anneau)
  doivent aller dans un calque, sinon un cheveu blanc apparait a la recomposition :
  `decouper-calques.py` attribue chaque pixel a la couleur la plus proche, sans seuil.
- **Pillow 12 premultiplie l'alpha** quand on redimensionne une image RGBA : les zones
  transparentes virent au noir. `rendu-loupe.py` reduit donc les couleurs seules, sur
  un canvas deja teinte de la couleur du fond.
- **l'attache du manche sort du cercle.** Le masque qui trace l'anneau est un cercle :
  il ne la couvre pas, et elle doit etre revelee a part, a la fin du trace.
- **`transform-box`** : les clips animes utilisent `fill-box`, pas `view-box`, parce
  que le viewBox ne commence plus a (0,0).
