# Ajouter l'étape « RDV 1 » à la pipeline BTP Expertise

Deux modifications, **dans cet ordre**. L'inverse ferait arriver des affaires
dans une colonne que le CRM ne connaît pas encore : elles n'apparaîtraient
nulle part sur le tableau.

---

## 1. Dans le CRM — déclarer l'étape

Fichier : **`js/data/schema.js`** du dépôt `CRM-Groupe`, bloc `btp:`.

Ajouter **une seule ligne**, entre « Nouveau lead » et « Qualifié » :

```js
    stages: [
      { key: 'lead', label: 'Nouveau lead', p: 5 },
      { key: 'rdv1', label: 'RDV 1', p: 10 },          // ← la ligne à ajouter
      { key: 'qualifie', label: 'Qualifié', p: 15 },
      { key: 'rdv', label: 'RDV / visite planifié', p: 35 },
      { key: 'proposition', label: 'Proposition envoyée', p: 60 },
      { key: 'mission_planifiee', label: 'Mission planifiée', p: 100, delivery: true },
      { key: 'mission_realisee', label: 'Mission réalisée', p: 100, delivery: true },
      { key: 'rapport_remis', label: 'Rapport remis', p: 100, delivery: true },
    ],
```

Le `p: 10` est la probabilité de conversion associée à l'étape : elle sert aux
prévisions du CRM. 10 % s'intercale logiquement entre les 5 % d'un lead brut et
les 15 % d'un lead qualifié — à ajuster selon l'expérience réelle.

Rien d'autre n'est à changer : le tableau, les filtres et les statistiques lisent
tous cette liste.

### Un point à trancher

La ligne `rdvStage: 'rdv'`, juste au-dessus, indique au CRM quelle étape
correspond à « un rendez-vous est prévu ». Elle désigne aujourd'hui la visite
sur site. Avec deux étapes de rendez-vous, il faut décider laquelle doit
alimenter les vues de planning — la laisser sur `'rdv'` si c'est la visite qui
compte, la passer à `'rdv1'` si c'est le premier échange.

---

## 2. Dans Supabase — y déposer les nouveaux prospects

Exécuter le fichier **`crm-supabase.sql`** à nouveau : il contient
`create or replace`, donc il remplace la fonction existante sans rien casser
ni perdre les données déjà enregistrées.

La seule différence : une prise de rendez-vous crée désormais l'affaire à
l'étape **`rdv1`** au lieu de `rdv`.

---

## Ce que deviennent les affaires déjà créées

Elles **ne bougent pas**. Celles qui sont à l'étape « RDV / visite planifié » y
restent — y compris le prospect d'essai, s'il n'a pas encore été supprimé.
Seules les nouvelles arriveront dans « RDV 1 ».

Si vous voulez déplacer les anciennes, faites-le à la main depuis le tableau :
elles sont peu nombreuses, et un déplacement manuel conserve l'historique.
