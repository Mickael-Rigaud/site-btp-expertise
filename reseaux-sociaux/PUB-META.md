# Quatre annonces Meta — deux pour l'AMO, deux pour recruter

Visuels produits par `pub_meta.py`, dans `visuels/pub-meta/`. Chaque annonce
existe en trois formats, à téléverser ensemble dans la même publicité :

| fichier | taille | où ça s'affiche |
|---|---|---|
| `…-4x5.jpg` | 1080 × 1350 | fil Facebook et Instagram — le format à fournir en premier |
| `…-1x1.jpg` | 1080 × 1080 | carrousel, colonne de droite, Marketplace |
| `…-9x16.jpg` | 1080 × 1920 | stories et reels |

Dans le gestionnaire, au niveau de la publicité : **Modifier par emplacement**
→ déposer le 4:5 sur le fil, le 9:16 sur les stories/reels, le 1:1 sur le
reste. Une seule image étirée partout perd la moitié de sa lisibilité.

---

## Les fichiers, et lequel prendre

| dossier | fichiers | pour quoi |
|---|---|---|
| `visuels/pub-meta/` | `.jpg` | à téléverser dans le gestionnaire de publicités Meta |
| `visuels/pub-meta/pdf/` | `.pdf` | **à importer dans Canva** — le texte y est modifiable |
| `visuels/pub-meta/svg/` | `.svg` | éditeurs vectoriels (Illustrator, Inkscape, Figma) |

Les PDF et les SVG sont produits par `pub_meta_vectoriel.py` : seule la photo
de fond y est une image — elle porte le recadrage, le voile et les dégradés.
Le sur-titre, le titre, la phrase, le bouton, le filet et le nom du cabinet
sont des objets séparés, modifiables un par un.

Deux recueils multipages, pratiques pour tout reprendre d'un coup :
`pdf/pub-meta.pdf` (les quatre annonces) et `pdf/recrutement-meta.pdf`
(les deux annonces de recrutement).

À savoir : Canva réécrit le texte d'un PDF importé avec ses propres polices.
Il reste modifiable, mais la coupure des lignes peut bouger d'un mot — jeter
un œil à la mise en page après l'import. Le SVG, lui, appelle Segoe UI par son
nom sans l'incorporer : sur une machine qui ne l'a pas, les longueurs de ligne
changent un peu.

---

## À déclarer avant de lancer les deux annonces de recrutement

Meta classe toute annonce d'offre de travail — salariée **ou** indépendante —
en **catégorie spéciale « Emploi »**. Elle se déclare à la création de la
campagne, dans « Catégories spéciales de publicités ».

Ne pas la déclarer, c'est le refus de l'annonce, et la restriction du compte
publicitaire en cas de récidive.

Conséquence sur le ciblage : ni âge, ni sexe, ni centres d'intérêt
professionnels, et un ciblage géographique volontairement large. Viser les
Alpes-Maritimes et le Var en entier, et laisser le texte faire le tri.

Les deux annonces AMO, elles, sont des publicités commerciales ordinaires :
aucune catégorie spéciale, ciblage libre.

---

## 1 · AMO — `pub-amo-devis`

**Texte principal**

> Trois entreprises, trois devis, trois façons de traiter le même problème.
> Sans être du bâtiment, sur quoi décider ?
>
> BTP Expertise vous assiste : définition des travaux, consultation des
> entreprises, analyse des devis ligne à ligne, visites de chantier et
> assistance à la réception.
>
> Le cabinet conseille et vérifie. Vous restez décisionnaire et vous contractez
> directement avec les entreprises.
>
> Alpes-Maritimes et Var.

**Titre** : Un professionnel du bâtiment de votre côté
**Description** : Assistance à maîtrise d'ouvrage · 06 & 83
**Bouton** : En savoir plus → `https://btpexpertise.fr/amo/`

## 2 · AMO — `pub-amo-chantier`

**Texte principal**

> Vous lancez des travaux. En face, des professionnels qui font ça toute
> l'année — et vous, une fois dans votre vie.
>
> L'assistance à maîtrise d'ouvrage met un homme du métier de votre côté :
> il définit les travaux avec vous, compare les offres, passe sur le chantier
> et vous assiste à la réception, réserves comprises.
>
> Devis établi avant toute intervention. Alpes-Maritimes et Var.

**Titre** : Ne restez pas seul face aux entreprises
**Description** : Devis avant intervention
**Bouton** : Envoyer un message, ou formulaire instantané
(`campagne-meta/formulaire-instantane.html`)

## 3 · Recrutement — `pub-recrutement-amo` · catégorie spéciale Emploi

**Texte principal**

> Le cabinet BTP Expertise cherche un professionnel de l'assistance à maîtrise
> d'ouvrage, indépendant, pour intervenir sur les Alpes-Maritimes et le Var.
>
> Le profil : dix ans de chantier derrière vous, à l'aise avec un devis et un
> CCTP, déjà installé à votre compte.
>
> Les missions sont confiées par le cabinet et se mènent au sein d'un réseau de
> professionnels indépendants — chacun garde sa structure et sa responsabilité.
>
> Un mot et votre parcours à contact@btpexpertise.fr

**Titre** : AMO indépendant — 06 & 83
**Description** : Missions confiées par le cabinet
**Bouton** : En savoir plus → page contact, ou formulaire instantané

## 4 · Recrutement — `pub-recrutement-expertise` · catégorie spéciale Emploi

**Texte principal**

> Le cabinet BTP Expertise cherche un expert bâtiment indépendant pour des
> missions en Alpes-Maritimes et dans le Var.
>
> Le profil : une formation bâtiment et de l'expérience terrain, la pathologie
> du bâti — fissures, humidité, malfaçons — et un rapport écrit clair, qui
> tienne face à une entreprise, un assureur ou un juge. Statut indépendant,
> RC professionnelle à jour.
>
> Un mot et votre parcours à contact@btpexpertise.fr

**Titre** : Expert bâtiment indépendant — 06 & 83
**Description** : Réseau de professionnels indépendants
**Bouton** : En savoir plus → page contact, ou formulaire instantané

---

## Ce qui est verrouillé dans les textes

- Côté AMO : jamais « direction des travaux », « pilotage », « OPC », ni une
  garantie de délai, de budget ou de bonne exécution — le cabinet conseille et
  vérifie, le client décide et contracte (`contenu.py`, `AMO_EXCLUSIONS`).
- Côté recrutement : « réseau de professionnels indépendants », jamais
  « rejoignez l'équipe », « poste » ou « CDI ».
- Aucune commune, aucun client, aucun chantier réel nommé sans accord écrit.

## Les photos

Le script cherche chaque image dans trois dossiers, dans cet ordre :
`photos-chantier/` (les vraies photos de Mickael), puis `site/assets/img/`,
puis `reserve-images/`. Une photo de chantier l'emporte donc toujours sur
l'image de banque du même sujet — et c'est elle qui distingue l'annonce de
celles de tous les autres cabinets.

Quand une photo verticale se recadre mal — le centre tombe sur le sol —
ajouter un champ `cadrage` à l'annonce : 0 garde le haut de l'image, 1 le bas,
0.5 est le centre.

Photos utilisées aujourd'hui :

| annonce | photo | |
|---|---|---|
| `pub-amo-devis` | `comp-maitrise-oeuvre.webp` | banque |
| `pub-amo-chantier` | `chantier-renovation-cloisons.jpg` | **photo du cabinet** |
| `pub-recrutement-amo` | `Expertise-avant-achat-immobilier-1.webp` | banque |
| `pub-recrutement-expertise` | `Fissure-maison-PACA.webp` | banque |

Les trois images de banque restantes attendent leur remplaçante : une visite
d'expertise sur une fissure, une réunion de chantier, un expert au travail.
