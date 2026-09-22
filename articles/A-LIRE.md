# Les articles de conseils

Un fichier = un article. Le nom du fichier commence par la date, donc le dossier
est toujours rangé du plus ancien au plus récent.

Le site les affiche sur **btpexpertise.fr/conseils/**, du plus récent au plus
ancien — l'ordre vient de la date écrite dans le fichier, pas de son nom.

---

## Le rythme mensuel

Le **1er de chaque mois vers 9h**, un rappel arrive sur
`contact.btpexpertiseriviera@gmail.com`. Le déroulé est toujours le même :

1. **L'article du mois est déposé ici**, en brouillon, par Claude.
2. **Vous le relisez**, Mickael valide.
3. **Vous supprimez la ligne `"brouillon": True,`** en haut du fichier.
4. `python build.py` puis `python publier.py`.

Rien n'est jamais publié sans cette validation.

---

## Le filet de sécurité : `brouillon`

Tant que cette ligne est présente en haut du fichier :

```python
"brouillon": True,
```

l'article **n'existe pas sur le site** : pas de page, pas de vignette dans la
liste des conseils, pas de mention dans le plan du site. Il reste sur votre
ordinateur, même si vous publiez d'autres modifications entre-temps.

C'est ce qui permet de publier une correction de tarif un 3 du mois sans
emmener au passage un article que personne n'a relu.

Pour mettre l'article en ligne, **supprimez cette ligne**. C'est tout.

---

## Écrire ou corriger un article

Ouvrez le fichier avec le **Bloc-notes** (clic droit → Ouvrir avec), modifiez le
texte entre les guillemets, enregistrez avec **Ctrl+S** — jamais « Enregistrer
sous », qui ajouterait `.txt` et rendrait le fichier invisible pour le site.

Pour en créer un de zéro : copiez `_modele.py`, renommez la copie
`AAAA-MM-JJ-titre-avec-des-tirets.py`, et remplissez. Le modèle liste tous les
champs et tous les types de blocs disponibles.

`_modele.py` commence par un souligné : il est ignoré par le site, il ne sera
jamais publié.

---

## Changer l'image

Le champ `"image"` nomme un fichier de `site/assets/img/`. Pour en changer,
déposez la nouvelle image dans ce dossier et écrivez son nom ici. Format `.webp`
de préférence, 1600 pixels de large environ.

---

## Si quelque chose casse

Une virgule oubliée suffit à rendre un fichier illisible. Dans ce cas
`python build.py` s'arrête et **nomme le fichier fautif** — il ne publie pas un
site amputé en silence. Rouvrez le fichier cité, la faute est à la ligne
indiquée.

En dernier recours, remettez `"brouillon": True,` : l'article sort du site et
vous laisse le temps de le reprendre.
