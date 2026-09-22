# Logo anime BTP Expertise

Le logo d'origine (`identite/logo-principal.png`) decoupe en calques, puis reconstruit
en animation. Aucun pixel n'a ete redessine : les calques sont des morceaux exacts du PNG,
et l'image finale redonne le logo au pixel pres (verifie par `python rendu-loupe.py diff`).

Deux versions :

- **la construction** — les etages montent, les tours poussent, le cercle de la loupe se
  trace, le nom se revele. Environ 3 s.
- **la loupe** — les batiments sont poses a 72 % de leur taille, la loupe entre par la
  gauche et grossit x1,39 ce qui passe sous le verre. Quand elle se cale au centre, les
  deux facteurs s'annulent et on retrouve exactement le logo. Environ 3,3 s.

## Fichiers livres

| Fichier | Usage |
|---|---|
| `logo-anime.svg` / `logo-anime-loupe.svg` | Le site. Nets a toute taille, ~530 ko. Fond clair + fond sombre inclus. |
| `logo-anime.mp4` / `logo-anime-loupe.mp4` | 1080x880, 30 i/s. Reseaux, intro de video. |
| `logo-anime-carre.mp4` / `logo-anime-loupe-carre.mp4` | 1080x1080. Instagram, LinkedIn. |
| `logo-anime.gif` (800 px) / `logo-anime-loupe.gif` (640 px) | En boucle. Signature mail, message. |
| `apercu.html` / `apercu-loupe.html` | Pages de test : rejouer, ralenti, fond sombre, curseur image par image. |

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
python decouper-calques.py   # refait les calques depuis les PNG du logo
python faire-anime.py        # logo-anime.svg + apercu.html
python faire-anime-loupe.py  # logo-anime-loupe.svg + apercu-loupe.html
python rendu.py planche      # planche de controle (12 images cles)
python rendu.py frames       # les PNG dans frames/, pour ffmpeg
python rendu-loupe.py frames # idem pour la variante, dans frames-loupe/
python rendu-loupe.py diff   # controle : l'image finale contre le logo d'origine
```

Puis, pour les videos (adapter le chemin de ffmpeg) :

```
ffmpeg -y -framerate 30 -i frames/f%04d.png -vf format=yuv420p -c:v libx264 -crf 18 logo-anime.mp4
ffmpeg -y -framerate 30 -i frames/f%04d.png -vf "scale=900:733,pad=1080:1080:90:173:white,format=yuv420p" -c:v libx264 -crf 18 logo-anime-carre.mp4
ffmpeg -y -framerate 25 -i frames/f%04d.png -vf "fps=25,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=120[p];[b][p]paletteuse=dither=bayer:bayer_scale=3" -loop 0 logo-anime.gif
```

La choregraphie est decrite deux fois : en CSS dans `faire-anime*.py` (pour le SVG)
et en Python dans `rendu*.py` (pour les videos). Modifier un timing demande de le
changer aux deux endroits, puis de relancer `rendu-loupe.py diff` pour verifier que
l'image finale colle toujours au logo d'origine.

Deux pieges rencontres, a ne pas reintroduire :

- les pixels de transition entre deux couleurs (la ou un batiment touche l'anneau)
  doivent aller dans un calque, sinon un cheveu blanc apparait a la recomposition :
  `decouper-calques.py` attribue chaque pixel a la couleur la plus proche, sans seuil ;
- Pillow 12 premultiplie l'alpha quand on redimensionne une image RGBA : les zones
  transparentes virent au noir. `rendu-loupe.py` reduit donc les couleurs seules.
