# Direction visuelle des publications — sans photo

La première série reposait sur les photos du site, qui viennent d'une banque
d'images : mêmes visuels que des centaines d'autres entreprises, et rien qui
distingue le cabinet. Cette direction-ci n'utilise aucune photo.

## Deux gabarits qui alternent

**Planche technique** — `posts_planche.py`, fond papier quadrillé clair.
Un schéma dessiné au trait, avec repères numérotés et cotes, comme une pièce
de rapport ; un cartouche en pied, comme sur un plan. Neuf sujets : fissures
(élévation d'un mur, fissure en escalier), humidité (coupe de mur, trois
origines), réception (extrait de procès-verbal avec ses réserves), plomberie
(chute et branchement, désordre au raccord), électricité (tableau
divisionnaire, module par module), avant achat (élévation d'une maison, cinq
points de contrôle), sécheresse (coupe de terrain argileux), toiture-terrasse
(coupe d'étanchéité au droit du relevé) et le déroulé d'une mission (frise en
cinq étapes).

**Carte** — `posts_carte.py`, en version bleu nuit ou papier. Pas de schéma :
un chiffre qui se lit de loin, une position du cabinet en grand, une liste, ou
deux colonnes comparées. Onze sujets : honoraires, indépendance, expertise
avant achat, ce que l'AMO n'est pas, malfaçons, visite technique, expert
bâtiment ou expert immobilier, litiges travaux, réunion contradictoire, le
rapport, zone d'intervention. Plus la **publication d'ouverture**, qui présente
le cabinet et ses dix prestations sur deux colonnes.

Les deux partagent la même grille, la même typographie et le même pied de
marque. Chaque sujet sort en carré 1080 et en 1080 × 1920.

## Le feed comme un tout

`feed.py` produit `visuels/apercu-feed.png` : l'en-tête du profil et les
vingt et une cases telles qu'elles apparaîtront. L'ordre alterne clair et sombre
case par case — le damier se maintient à mesure que les publications
s'ajoutent, trois par trois.

Pour garder ce rythme, suivre l'ordre de publication de
[PUBLICATIONS.md](PUBLICATIONS.md) : il est calculé pour cela — présentation
d'abord, puis les services un par un, en alternant planche claire et carte
sombre. Une série de trois
cartes sombres d'affilée casse la grille.

Seule exception : la publication d'ouverture, la toute première publiée, donc
la dernière case. Elle rompt l'alternance et sortira de toute façon de la
grille visible dès les publications suivantes.

## Ce que ces visuels ne sont pas

Les valeurs qu'ils portent — « ouverture ≈ 4 mm », « façade sud · 6,40 m »,
« ressaut de 12 mm », les quatre réserves du procès-verbal — sont des
**schémas de principe**, pas des relevés réels. Ils illustrent une méthode.

Ne jamais les présenter comme un dossier traité, ni comme une étude de cas :
ce serait une référence client inventée. Le jour où Mickael fournit un cas
réel avec l'accord écrit du client, il remplacera avantageusement n'importe
quel schéma.

## Régénérer

```
python reseaux-sociaux/posts_planche.py
python reseaux-sociaux/posts_carte.py
python reseaux-sociaux/planches_pdf.py
python reseaux-sociaux/feed.py
```

Les textes, les valeurs des schémas et l'ordre du feed sont en tête de chaque
fichier.

## Hors serie : vendre l'AMO, recruter

`posts_amo.py` sort quatre cartes de plus, sur le meme gabarit : deux pour
l'assistance a maitrise d'ouvrage (le declencheur, puis le contenu de la
mission) et deux annonces de recrutement d'independants sur le 06 et le 83.
Elles ne sont pas dans l'ordre du feed : elles s'intercalent quand Mickael le
decide, en gardant l'alternance clair / sombre. Les legendes sont dans
[TEXTES-AMO-RECRUTEMENT.md](TEXTES-AMO-RECRUTEMENT.md).

```
python reseaux-sociaux/posts_amo.py
```

## Les PDF pour Canva

`planches_pdf.py` sort les vingt et une publications dans
`visuels/planches/pdf/` :
un PDF par sujet, plus `planches-carre.pdf` et `planches-story.pdf`, qui les
ouvrent comme un document multipage.

Sont vectoriels — donc modifiables dans Canva — le quadrillage, les aplats, le
cartouche et **tous les textes** : en-tête, titre, phrase, listes, chiffres,
pied. Reste en image le schéma dessiné des planches, avec ses repères : éclaté
en centaines d'objets, il serait ingérable, alors que le texte est justement ce
qu'on veut pouvoir corriger.

Les positions viennent des fonctions `mesures()` et `mesures_carte()`, partagées
avec le rendu PNG : une retouche de gabarit vaut pour les deux sorties.
