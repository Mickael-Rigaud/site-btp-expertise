# Back-office du formulaire — installation

Le formulaire du site envoie chaque demande à un service qui :

1. **enregistre la demande** et la fait apparaître dans l'espace de gestion ;
2. **range les photos** dans un dossier privé, un sous-dossier par demande ;
3. **envoie le mail de notification** au cabinet ;
4. **envoie un accusé de réception** au prospect.

Vous consultez et suivez les demandes dans une **interface web dédiée** : liste,
recherche, fiche détaillée avec photos, statuts, notes internes.

Tout tourne sur le compte Google `contact.btpexpertiseriviera@gmail.com`.
Aucun autre compte, aucun abonnement, aucun tableur à manipuler.

L'installation prend une dizaine de minutes, une seule fois.

---

## Voir l'interface avant d'installer

Ouvrez `backoffice/apercu.html` dans votre navigateur — code d'accès **`demo`**.
C'est l'interface réelle, avec quatre demandes fictives.

---

## 1. Créer le projet

1. Connectez-vous à Google avec **le compte du cabinet**.
2. Allez sur [script.new](https://script.new) — un éditeur s'ouvre sur un projet vierge.
3. Renommez le projet en haut à gauche : **BTP Expertise — Demandes**.

## 2. Coller les deux fichiers

**Le code :**

1. Effacez tout le contenu du fichier `Code.gs` affiché.
2. Ouvrez `backoffice/Code.gs`, copiez **tout** son contenu, collez-le à la place.

**L'interface :**

3. À gauche, à côté de « Fichiers », cliquez sur **+** puis **HTML**.
4. Nommez-le exactement **`Admin`** (Google ajoutera `.html` tout seul).
5. Effacez le contenu proposé, puis collez **tout** le contenu de `backoffice/Admin.html`.
6. Enregistrez (icône disquette).

## 3. Régler les deux mots de passe

En haut de `Code.gs`, le bloc `REGLAGES` :

| Réglage | Rôle |
|---|---|
| `codeAcces` | **le code qui ouvre l'espace de gestion — à changer** |
| `jeton` | mot de passe partagé avec le site, **doit rester identique** à `jeton_formulaire` dans `contenu.py` |
| `destinataire` | l'adresse qui reçoit les demandes (plusieurs possibles, séparées par des virgules) |
| `emailAffiche` | l'adresse affichée dans l'accusé de réception |
| `telephone` | le numéro donné au prospect en cas d'urgence |
| `accuseReception` | `false` pour ne plus envoyer d'accusé au prospect |

Changez `codeAcces` : c'est lui qui protège l'accès aux demandes de vos clients.

## 4. Publier

1. En haut à droite : **Déployer → Nouveau déploiement**.
2. Engrenage à gauche de « Sélectionner un type » → **Application web**.
3. Remplissez :
   - **Description** : `Formulaire et espace de gestion`
   - **Exécuter en tant que** : `Moi`
   - **Qui a accès** : **Tout le monde** ← indispensable, sinon le site ne peut pas envoyer
4. **Déployer**.
5. Google demande une autorisation : **Autoriser l'accès**, choisissez votre compte, puis sur
   l'écran « Google n'a pas validé cette application », cliquez sur **Paramètres avancés**
   puis **Accéder à BTP Expertise — Demandes (non sécurisé)**. C'est normal : l'application, c'est vous.
6. **Autoriser**.

Google affiche une **URL d'application web** :

```
https://script.google.com/macros/s/AKfycb...../exec
```

Cette adresse sert aux deux usages :

- **le site** l'utilise pour envoyer les demandes — envoyez-la-moi, je la place dans `contenu.py` ;
- **vous** l'ouvrez dans votre navigateur pour accéder à l'espace de gestion.

Mettez-la en favori sur votre ordinateur et sur votre téléphone.

## 5. Vérifier

1. Dans la liste déroulante des fonctions, choisissez **`testerInstallation`**, puis **Exécuter**.
2. Vérifiez : vous recevez le mail de notification, puis l'accusé de réception.
3. Ouvrez l'URL d'application web, saisissez votre code d'accès :
   la demande de test doit apparaître dans la liste.
4. Ouvrez-la, changez son statut, écrivez une note, puis supprimez-la.

---

## Au quotidien

**La liste** affiche les demandes, la plus récente en haut, avec une pastille de couleur par
statut. Les compteurs en haut donnent le nombre à traiter, en cours, gagné.

**La recherche** porte sur tout : nom, ville, e-mail, téléphone, description, note interne.
Les boutons filtrent par statut.

**La fiche** s'ouvre au clic. Elle contient les coordonnées, la description complète, les
photos en vignettes cliquables, le statut, et une zone de note interne pour vos comptes
rendus d'appel. Deux boutons : **Répondre par e-mail** ouvre votre messagerie avec l'objet
prérempli, **Appeler** lance l'appel depuis un téléphone.

**Les statuts** : À traiter → En cours → Devis envoyé → Gagné ou Perdu. Un clic suffit,
l'enregistrement est immédiat.

**Sur téléphone** l'interface s'adapte : c'est utilisable depuis un chantier.

---

## Bon à savoir

**Les photos sont réduites avant l'envoi.** Le site les redimensionne à 1600 pixels et les
convertit en JPEG : une photo de 4 Mo arrive à environ 300 Ko. L'envoi reste rapide même en
4G depuis un chantier.

**Les photos ne sont pas partagées publiquement.** Elles s'affichent dans l'interface, et
restent invisibles pour qui n'a pas le code d'accès.

**Limite d'envoi Gmail : 100 destinataires par jour** sur un compte gratuit. Chaque demande
en consomme deux, soit 50 demandes par jour. Large.

**Le code d'accès est votre seule protection.** Choisissez-le sérieusement et ne diffusez pas
l'URL. Pour le changer plus tard : modifiez `codeAcces` puis redéployez.

**Si vous modifiez le script**, il faut redéployer pour que le changement prenne effet :
**Déployer → Gérer les déploiements → crayon → Version : Nouvelle version → Déployer**.
L'URL ne change pas.

**En cas de problème**, l'historique se trouve dans l'éditeur, menu **Exécutions**.

---

## Et plus tard ?

Cette solution couvre le besoin sans rien coûter. Elle montrera ses limites le jour où il
faudra des relances automatiques, des statistiques ou plusieurs utilisateurs avec des droits
distincts. On migrera alors vers un Worker Cloudflare avec une base D1 et Resend, sans rien
changer au site : seule l'adresse d'envoi du formulaire sera à remplacer dans `contenu.py`.

Une chose à prévoir dès que la boîte `contact@btpexpertise.fr` existera chez OVH : la
déclarer dans Gmail comme adresse d'envoi (**Paramètres → Comptes → Ajouter une autre
adresse e-mail**). Les accusés de réception partiront alors au nom du domaine.

---

## Mise à jour du 3 septembre 2026 — l'agenda de rendez-vous

Le script gère désormais la prise de rendez-vous du site : il calcule les créneaux
libres, enregistre les réservations et les inscrit dans l'agenda. **Aucun service
extérieur** n'intervient.

### Ce qu'il faut faire une fois

1. Ouvrez l'éditeur du projet **BTP Expertise — Demandes**.
2. Effacez tout le contenu de `Code.gs` et collez celui de `backoffice/Code.gs`.
3. **Déployer → Gérer les déploiements → crayon → Version : Nouvelle version → Déployer**.
4. Google demande une **nouvelle autorisation** : le script accède maintenant à
   votre agenda. Acceptez-la (Paramètres avancés → Accéder au projet).

L'URL du service ne change pas. Rien à modifier dans le site.

### Vérifier que tout fonctionne

Dans la liste des fonctions, choisissez **`testerAgenda`** puis **Exécuter** : le
journal affiche les premiers créneaux proposés. S'il est vide, c'est que les
règles ci-dessous ne laissent aucune disponibilité dans les trente jours.

### Régler les disponibilités

Tout est en haut du fichier, dans le bloc `AGENDA` :

| Réglage | Rôle | Valeur actuelle |
|---|---|---|
| `jours` | jours travaillés (1 = lundi) | lundi à vendredi |
| `plages` | heures d'ouverture | 9h-13h30 (dernier créneau à 13h) |
| `durees` | durée par format | 30 min au téléphone comme en visio |
| `pas` | écart entre deux créneaux proposés | 60 minutes |
| `delaiJours` | délai de prévenance | 2 jours |
| `fenetreJours` | profondeur du calendrier | 30 jours |
| `agendas` | agenda qui reçoit le rendez-vous, par activité | « BTP Expertise - Expertise » et « BTP Expertise - AMO » |
| `agendasBloquants` | agendas qui bloquent un créneau sans rien recevoir | `primary` |
| `couleurs` | couleur imposée à l'événement, par activité | vide : chaque agenda donne la sienne |

**Pour bloquer une journée ou une semaine**, créez simplement un événement dans
votre agenda Google : les créneaux correspondants disparaissent du site.

### Deux agendas, un par activité

Les rendez-vous ne vont pas dans le même agenda selon l'activité :

| Activité | Agenda |
|---|---|
| Expertise bâtiment | **BTP Expertise - Expertise** |
| Assistance à Maîtrise d'Ouvrage | **BTP Expertise - AMO** |

Les deux sont des agendas secondaires du compte qui héberge le script. Ils ont
été créés pour que le CRM Groupe puisse lire chaque activité séparément.

**Les créneaux libres tiennent compte des deux**, plus de l'agenda personnel
(`agendasBloquants`) : un rendez-vous d'expertise ferme donc le créneau à une
demande d'AMO, et l'inverse. Sans cela, deux personnes pourraient réserver la
même heure.

Le script **n'efface jamais rien dans l'agenda personnel**. Les suppressions
(`supprimerTests`, refus d'un rendez-vous) ne cherchent que dans les deux
agendas d'activité.

Pour changer un agenda, remplacez son identifiant dans `AGENDA.agendas`.
L'identifiant se lit dans Google Agenda : *Paramètres de l'agenda → Intégrer
l'agenda → ID de l'agenda*. Lancez ensuite **`testerAgenda`** : il affiche
chaque agenda, son nom, le nombre d'événements et son rôle. Une ligne `ECHEC`
signale un identifiant faux ou un agenda auquel le compte n'a pas accès.

### Reconnaître une AMO d'une expertise

Chaque rendez-vous entre dans l'agenda avec l'activité en tête de son titre :
**Expertise · Visio — Nom (Fissures)**, **AMO · Appel — Nom (Suivi de
chantier)**. La couleur, elle, est celle de l'agenda, réglée depuis Google
Agenda — les deux activités ayant chacune le sien, il n'y a plus de raison de
l'imposer depuis le script.

Le titre porte l'activité parce que la couleur ne suit pas partout : elle vit
dans Google Agenda, et ne passe ni dans le fichier que reçoit Outlook, ni dans
les affichages en liste.

Pour imposer malgré tout une couleur, écrivez un nom dans `AGENDA.couleurs`.
Les noms acceptés sont ceux de Google : `PALE_BLUE`, `PALE_GREEN`, `MAUVE`,
`PALE_RED`, `YELLOW`, `ORANGE`, `CYAN`, `GRAY`, `BLUE`, `GREEN`, `RED`.
Attention : une couleur posée sur l'événement recouvre celle de son agenda.

**Pour voir le rendu sans prendre de vrai rendez-vous** : lancez
**`testerCouleurs`**. Deux rendez-vous d'essai se posent dans deux mois, un de
chaque activité — aucun courriel, aucune ligne dans le classeur, rien dans le
CRM. **`supprimerCouleurs`** les efface ensuite.

### Où sont les rendez-vous

Une feuille **Rendez-vous** est créée automatiquement dans le classeur, à côté des
demandes. Chaque ligne porte le début, la fin, le format et les coordonnées.
Les rendez-vous apparaissent aussi dans la liste habituelle de l'espace de gestion,
avec le type « Rendez-vous téléphonique » ou « Rendez-vous visio ».

### Deux points techniques

**Doubles réservations.** Un verrou empêche deux personnes de prendre le même
créneau simultanément, et le créneau est revérifié au moment de l'enregistrement.
Si un autre visiteur vient de le prendre, le site l'annonce et recharge la liste.

**Agenda Outlook.** Apps Script ne sait pas lire un agenda Microsoft. Si les
rendez-vous doivent un jour vivre dans Outlook plutôt que dans Google, il faudra
publier cet agenda en lien ICS et ajouter sa lecture au script.

---

## Le rappel mensuel par e-mail

Le script envoie, le **1er de chaque mois vers 9 h**, un rappel invitant à publier
l'article de conseils. L'envoi part des serveurs de Google : il arrive même si
l'ordinateur du cabinet est éteint.

### Installation

Une seule fois, après avoir collé le nouveau `Code.gs` et redéployé :

1. Dans la liste des fonctions, choisissez **`installerRappelMensuel`**.
2. Cliquez sur **Exécuter**.
3. Le journal confirme : *« Rappel installé : le 1 de chaque mois vers 9h ».*

Pour voir tout de suite à quoi ressemble le message, lancez **`rappelArticleMensuel`** :
il part immédiatement vers l'adresse du cabinet.

### Modifier ou arrêter

| Pour | Faire |
|---|---|
| changer le jour, l'heure ou le destinataire | modifier le bloc `RAPPEL` en tête du fichier, puis relancer `installerRappelMensuel` |
| arrêter les rappels | lancer `retirerRappelMensuel` |

Relancer `installerRappelMensuel` ne crée pas de doublon : les anciens
déclencheurs sont retirés d'abord.

### Ce que fait le rappel, et ce qu'il ne fait pas

Il **rappelle**, il ne publie rien. L'article est préparé côté Claude, relu par
Mickael Rigaud, puis mis en ligne avec `python publier.py`. Aucun contenu
technique n'est publié sans relecture humaine — c'est ce que déclarent les
mentions légales du site.

---

## Faire partir les courriels depuis contact@btpexpertise.fr

Par défaut, Apps Script envoie depuis l'adresse du compte Google qui héberge le
script. Le prospect voit donc `contact.btpexpertiseriviera@gmail.com`, ce qui
fait moins sérieux et dessert la délivrabilité.

Le script sait utiliser l'adresse du domaine **dès qu'elle est déclarée comme
alias d'envoi**. Tant qu'elle ne l'est pas, il continue d'envoyer normalement :
aucun formulaire ne casse pendant la mise en place.

### Ce qu'il faut sous la main

Le **mot de passe de la boîte** `contact@btpexpertise.fr`. Il reste chez vous :
il se saisit uniquement dans l'écran de Gmail, jamais ailleurs.

### La manipulation, une seule fois

1. Ouvrez **Gmail** avec `contact.btpexpertiseriviera@gmail.com`.
2. Roue dentée → **Voir tous les paramètres** → onglet **Comptes et importation**.
3. Ligne « Envoyer des e-mails en tant que » → **Ajouter une autre adresse e-mail**.
4. Nom : **BTP Expertise** — Adresse : **contact@btpexpertise.fr** → Étape suivante.
5. Renseignez le serveur d'envoi :

   | Si la boîte est… | Serveur | Port | Sécurité |
   |---|---|---|---|
   | une boîte OVH (MX Plan) | `ssl0.ovh.net` | 465 | SSL |
   | une boîte Microsoft 365 | `smtp.office365.com` | 587 | TLS |

   Identifiant : l'adresse complète. Mot de passe : celui de la boîte.
6. Google envoie un **code de confirmation** à `contact@btpexpertise.fr`.
   Ouvrez-le dans Outlook, saisissez le code.
7. De retour dans Gmail, cochez l'adresse comme **expéditeur par défaut** si
   vous le souhaitez — le script, lui, n'en a pas besoin.

### Vérifier

Dans l'éditeur Apps Script, lancez **`testerExpediteur`**. Le journal doit
afficher :

```
Alias declares : contact@btpexpertise.fr
OK : les courriels partiront de contact@btpexpertise.fr
```

S'il affiche « n'est pas un alias d'envoi », l'étape 6 n'a pas abouti.

### Si Microsoft 365 refuse

Les comptes Microsoft 365 bloquent souvent l'authentification SMTP par défaut.
Il faut alors l'activer pour cette boîte dans la console d'administration
(« SMTP AUTH »). Si ce n'est pas possible, le script continue de fonctionner
depuis l'adresse Gmail, et l'adresse du domaine reste affichée dans la
signature et en adresse de réponse.
