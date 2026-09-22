# Modifier le site btpexpertise.fr

Le site est un ensemble de fichiers sur cet ordinateur, publiés chez OVH.
Il n'y a pas d'interface d'administration en ligne : on modifie ici, puis on publie.

---

## La façon la plus simple : demander

Ouvrez **Claude** sur le dossier `C:\Users\elodi\Downloads\BTP-Expertise`, et dites ce
que vous voulez changer, en français, sans vous soucier des fichiers :

> « change le numéro de téléphone »
> « ajoute une question dans la FAQ sur les délais »
> « le titre de la page tarifs ne me plaît pas »
> « publie l'article »

Les modifications sont faites, vérifiées et mises en ligne dans la foulée.

**Pour l'article du mois, vous n'avez rien à rédiger** : il est déposé
automatiquement le 1er dans le dossier `articles/`. Vous le relisez, Mickael
valide, et vous dites « publie ».

---

## En autonomie : les deux commandes

Tout le contenu éditorial tient dans **un seul fichier**, `contenu.py`. Ouvrez-le
avec le Bloc-notes, modifiez le texte entre les guillemets, enregistrez avec
**Ctrl+S** (jamais « Enregistrer sous », qui ajouterait `.txt`).

Puis, dans un terminal ouvert sur le dossier :

```bash
python build.py
```

Regénère les 18 pages du site à partir de vos textes.

```bash
python publier.py
```

Envoie chez OVH ce qui a changé. Quelques secondes pour une modification de texte.

### Voir avant de publier

```bash
python serve.py 8124
```

Ouvre le site sur votre ordinateur à l'adresse http://localhost:8124 — rien n'est
en ligne tant que vous n'avez pas lancé `publier.py`.

---

## Où se trouve quoi

| Ce que vous voulez changer | Où |
|---|---|
| Téléphone, adresse, e-mail | bloc `SITE`, tout en haut de `contenu.py` |
| Les dix expertises | `EXPERTISES` |
| Les missions AMO | `AMO` |
| Les tarifs | `HONORAIRES` et `PAIEMENT` |
| La FAQ | `FAQ` |
| Les articles de conseils | dossier `articles/`, un fichier par article |
| Les villes | `VILLES_06`, `VILLES_83`, `VILLES_PRIORITAIRES` |
| Mentions légales, SIREN, capital | `LEGAL` |
| Les liens de paiement Stripe | `PAIEMENT` |

La mise en page, elle, est dans `build.py` et `site/assets/css/style.css` — mieux
vaut passer par Claude pour y toucher.

---

## Publier un article, ou le garder de côté

Les articles ne sont pas dans `contenu.py` mais dans le dossier **`articles/`**,
un fichier par article, nommé par sa date. Le mode d'emploi détaillé est dans
`articles/A-LIRE.md`.

Chaque fichier commence par un champ `brouillon` :

```python
"brouillon": True,
```

Tant qu'il est là, l'article **n'existe pas sur le site** : pas de page, pas de
vignette dans la liste des conseils, pas de mention dans le plan du site. Il reste
sur votre ordinateur, même si vous publiez d'autres modifications entre-temps.

Pour le mettre en ligne, **supprimez cette ligne**, puis `python build.py` et
`python publier.py`.

C'est le filet de sécurité du rythme mensuel : l'article déposé le 1er reste
invisible jusqu'à la validation de Mickael, sans vous empêcher de publier autre
chose pendant ce temps.

---

## Les demandes reçues et les rendez-vous

Elles n'arrivent pas dans ces fichiers mais dans **l'espace de gestion**, une page
web protégée par un code :

- adresse : celle du script Google, dans `SITE["form_action"]` de `contenu.py`
- code d'accès : `btp-1qfx-1ts7`

Vous y voyez les demandes, les rendez-vous, leurs statuts et vos notes. Détails
dans `backoffice/INSTALLATION.md`.

---

## En cas de doute

Après chaque modification, `python verifie.py` contrôle les liens, les images et
les pages. S'il affiche « Aucune erreur bloquante », c'est bon.

Et si quelque chose s'est mal passé, la publication ne détruit rien
d'irréversible : relancez `python build.py` puis `python publier.py`, la version
correcte repart.
