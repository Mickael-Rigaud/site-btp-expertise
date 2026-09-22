-- ============================================================================
--  CRM Groupe — suppression des prospects d'essai BTP Expertise
--
--  À exécuter dans Supabase : SQL Editor → New query.
--  Écrit le 2026-09-14, après les tests de mise en service du formulaire.
-- ============================================================================
--
--  IMPORTANT — une précaution à comprendre avant de lancer :
--
--  La fonction d'inscription réutilise un contact existant quand l'adresse
--  e-mail est déjà connue. Un de mes essais a utilisé adresse.dessai@exemple.fr :
--  si ce contact existait déjà pour RGD Renova, il n'a pas été créé mais
--  complété, et le supprimer détruirait une fiche légitime.
--
--  Ce fichier ne supprime donc un contact que s'il ne reste attaché à aucune
--  affaire. Les autres sont simplement détachés de l'activité BTP.
--
--  Marche à suivre : exécuter l'étape 1, lire le résultat, puis l'étape 2.
-- ============================================================================


-- ============================================================================
-- ÉTAPE 1 — Voir ce qui sera supprimé (ne modifie rien)
-- ============================================================================

with essais as (
  select id, first_name, last_name, email, activities, created_at
  from public.contacts
  where lower(email) in (
          'essai@btpexpertise.fr',
          'sonde@btpexpertise.fr',
          'adresse.dessai@exemple.fr',
          'adresse.dessai@exemple.fr',   -- adresse saisie par erreur
          'adresse.dessai@exemple.fr'
        )
     or upper(coalesce(last_name, ''))  like 'A SUPPRIMER%'
     or upper(coalesce(first_name, '')) in ('TEST', 'ESSAI', 'SONDE')
)
select
  c.first_name, c.last_name, c.email,
  c.activities,
  (select count(*) from public.deals d where d.contact_id = c.id) as affaires_total,
  (select count(*) from public.deals d
    where d.contact_id = c.id and d.activity <> 'btp')            as affaires_autres_activites
from essais c
order by c.created_at;


-- ============================================================================
-- ÉTAPE 2 — Supprimer
-- ============================================================================
-- À exécuter d'un bloc. Si la colonne « affaires_autres_activites » de
-- l'étape 1 est supérieure à 0 pour une ligne, ce contact sera conservé :
-- seule son affaire BTP disparaîtra.

begin;

-- 2a. Les affaires BTP d'essai
with essais as (
  select id from public.contacts
  where lower(email) in (
          'essai@btpexpertise.fr',
          'sonde@btpexpertise.fr',
          'adresse.dessai@exemple.fr',
          'adresse.dessai@exemple.fr',
          'adresse.dessai@exemple.fr'
        )
     or upper(coalesce(last_name, ''))  like 'A SUPPRIMER%'
     or upper(coalesce(first_name, '')) in ('TEST', 'ESSAI', 'SONDE')
)
delete from public.deals
where activity = 'btp'
  and contact_id in (select id from essais);

-- 2b. Les contacts devenus orphelins — ceux qui n'ont plus aucune affaire
with essais as (
  select id from public.contacts
  where lower(email) in (
          'essai@btpexpertise.fr',
          'sonde@btpexpertise.fr',
          'adresse.dessai@exemple.fr',
          'adresse.dessai@exemple.fr',
          'adresse.dessai@exemple.fr'
        )
     or upper(coalesce(last_name, ''))  like 'A SUPPRIMER%'
     or upper(coalesce(first_name, '')) in ('TEST', 'ESSAI', 'SONDE')
)
delete from public.contacts c
where c.id in (select id from essais)
  and not exists (select 1 from public.deals d where d.contact_id = c.id);

-- 2c. Les contacts conservés perdent leur rattachement à l'activité BTP
with essais as (
  select id from public.contacts
  where lower(email) in (
          'essai@btpexpertise.fr',
          'sonde@btpexpertise.fr',
          'adresse.dessai@exemple.fr',
          'adresse.dessai@exemple.fr',
          'adresse.dessai@exemple.fr'
        )
)
update public.contacts
set activities = array_remove(activities, 'btp'),
    updated_at = now()
where id in (select id from essais)
  and 'btp' = any(activities);

commit;


-- ============================================================================
-- ÉTAPE 3 — Vérifier qu'il ne reste rien
-- ============================================================================

select count(*) as affaires_essai_restantes
from public.deals
where activity = 'btp'
  and (upper(title) like '%A SUPPRIMER%'
    or upper(title) like '%TEST%'
    or upper(title) like '%ESSAI%'
    or upper(title) like '%SONDE%');
