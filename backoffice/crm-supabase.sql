-- ============================================================================
--  CRM Groupe — inscription automatique des prospects BTP Expertise
--
--  À exécuter dans Supabase : SQL Editor → New query → coller → Run.
--  Écrit pour la structure réelle des tables, vérifiée le 11 septembre 2026.
--  Les prospects arrivent à l'étape « RDV 1 » (voir crm-etape-rdv1.md).
-- ============================================================================
--
--  Ce que ça met en place :
--    une fonction "creer_prospect_btp" qui crée un contact et une affaire
--    dans la pipeline BTP Expertise, et rien d'autre.
--
--  Pourquoi une fonction plutôt qu'un droit d'écriture sur les tables :
--    le site n'obtient ainsi AUCUN accès aux données. Il ne peut rien lire du
--    groupe — ni RGD Renova, ni La Référence Courtage, ni Propulsion — ni
--    modifier, ni supprimer. Il peut uniquement déposer un prospect BTP.
--    La clé publique du CRM suffit : aucun secret à confier au site.
--
--  Le tout est réversible : la dernière ligne du fichier annule l'installation.
-- ============================================================================


create or replace function public.creer_prospect_btp(
  p_prenom        text,
  p_nom           text,
  p_email         text,
  p_telephone     text,
  p_ville         text,
  p_probleme      text,
  p_type_bien     text,
  p_description   text,
  p_canal         text,
  p_consentement  boolean default false,
  p_rdv           timestamptz default null,
  -- Ajoute cote CRM pour les deux pipelines. ATTENTION : ne jamais recreer
  -- une version sans ce parametre. Les deux coexisteraient, le site enverrait
  -- des arguments qui conviennent aux deux, et PostgreSQL refuserait de
  -- choisir — aucune demande n'arriverait plus dans le CRM.
  p_besoin        text default null
)
returns uuid
language plpgsql
security definer                -- s'exécute avec les droits du propriétaire
set search_path = public
as $$
declare
  v_contact uuid;
  v_deal    uuid;
  v_titre   text;
  v_etape   text;
  v_mission text;
begin
  -- Garde-fou : on ne crée rien sans identité exploitable.
  if coalesce(nullif(trim(p_nom), ''), nullif(trim(p_email), '')) is null then
    raise exception 'Nom ou e-mail requis';
  end if;

  -- ---- Le contact ---------------------------------------------------------
  -- Un habitué qui reprend rendez-vous ne doit pas créer un second contact :
  -- on réutilise celui qui porte la même adresse, et on le complète.
  if nullif(trim(p_email), '') is not null then
    select id into v_contact
    from public.contacts
    where lower(email) = lower(trim(p_email))
    limit 1;
  end if;

  if v_contact is null then
    insert into public.contacts
      (first_name, last_name, email, phone, city,
       activities, type, channel, consent, created_at)
    values
      (nullif(trim(p_prenom), ''), nullif(trim(p_nom), ''),
       nullif(trim(p_email), ''), nullif(trim(p_telephone), ''),
       nullif(trim(p_ville), ''),
       array['btp']::text[], 'Prospect', p_canal,
       coalesce(p_consentement, false), now())
    returning id into v_contact;
  else
    update public.contacts
    set phone      = coalesce(phone, nullif(trim(p_telephone), '')),
        city       = coalesce(city, nullif(trim(p_ville), '')),
        first_name = coalesce(first_name, nullif(trim(p_prenom), '')),
        last_name  = coalesce(last_name, nullif(trim(p_nom), '')),
        -- on ajoute l'activité BTP sans toucher aux autres
        activities = case when 'btp' = any(activities)
                          then activities
                          else activities || 'btp' end,
        consent    = consent or coalesce(p_consentement, false),
        updated_at = now()
    where id = v_contact;
  end if;

  -- ---- L'affaire ----------------------------------------------------------
  -- Un créneau déjà fixé entre directement à l'étape « RDV 1 » : le premier
  -- échange est pris, il n'y a pas à requalifier le lead.
  -- Cette étape doit exister dans js/data/schema.js du CRM, sinon l'affaire
  -- n'apparaîtra dans aucune colonne du tableau.
  v_etape := case when p_rdv is null then 'lead' else 'rdv1' end;

  -- La pipeline d'arrivee. On regarde d'abord le besoin, puis la demande :
  -- une installation ancienne du site n'envoie pas encore p_besoin, et le
  -- tri doit quand meme fonctionner.
  v_mission := case
    when coalesce(p_besoin, '')   ~* '(^|[^[:alpha:]])amo([^[:alpha:]]|$)'
      or coalesce(p_besoin, '')   ~* 'ouvrage'
      or coalesce(p_probleme, '') ~* '(^|[^[:alpha:]])amo([^[:alpha:]]|$)'
      or coalesce(p_probleme, '') ~* 'ouvrage'
    then 'amo' else 'expertise' end;

  v_titre := coalesce(nullif(trim(p_probleme), ''), 'Demande') ||
             ' — ' || coalesce(nullif(trim(p_nom), ''), 'sans nom') ||
             case when nullif(trim(p_ville), '') is null
                  then '' else ' (' || trim(p_ville) || ')' end;

  insert into public.deals
    (title, activity, stage, status, contact_id, channel,
     fields, stage_history, created_at, stage_changed_at)
  values
    (v_titre, 'btp', v_etape, 'open', v_contact, p_canal,
     jsonb_build_object(
       'type_mission',  v_mission,
       'besoin',        nullif(trim(coalesce(p_besoin, '')), ''),
       'problematique', p_probleme,
       'type_bien',     p_type_bien,
       'contexte',      'Particulier',
       'adresse',       p_ville,
       'date_visite',   case when p_rdv is null then null
                             else to_char(p_rdv at time zone 'Europe/Paris',
                                          'YYYY-MM-DD') end,
       'origine',       'Formulaire btpexpertise.fr',
       'detail',        p_description
     ),
     -- l'historique alimente les statistiques du CRM : on l'amorce
     case when p_rdv is null
          then jsonb_build_array(jsonb_build_object('stage', 'lead', 'at', now()))
          else jsonb_build_array(
                 jsonb_build_object('stage', 'lead', 'at', now()),
                 jsonb_build_object('stage', 'rdv1', 'at', now()))
     end,
     now(), now())
  returning id into v_deal;

  -- ---- Le rendez-vous dans l'agenda ---------------------------------------
  -- L'agenda du tableau de bord lit public.activities, et non Google Agenda :
  -- sans cette ligne, un rendez-vous pris sur le site n'apparait nulle part
  -- dans le CRM, alors meme que l'affaire est bien creee.
  --
  -- L'heure est ramenee a celle de Paris : p_rdv arrive en temps universel,
  -- et un rendez-vous de 10h00 s'inscrirait sinon a 08h00.
  if p_rdv is not null then
    insert into public.activities
      (activity, type, title, due_date, due_time, done,
       deal_id, contact_id, notes, created_at, updated_at)
    values
      ('btp', 'rdv', v_titre,
       (p_rdv at time zone 'Europe/Paris')::date,
       to_char(p_rdv at time zone 'Europe/Paris', 'HH24:MI'),
       false, v_deal, v_contact,
       nullif(trim(p_description), ''),
       now(), now());
  end if;

  return v_deal;
end;
$$;


-- ---- N'ouvrir que cette fonction, à personne d'autre ------------------------

revoke all on function public.creer_prospect_btp(
  text, text, text, text, text, text, text, text, text, boolean, timestamptz, text
) from public;

grant execute on function public.creer_prospect_btp(
  text, text, text, text, text, text, text, text, text, boolean, timestamptz, text
) to anon;


-- ============================================================================
--  Pour tout annuler, si besoin :
--
--  drop function if exists public.creer_prospect_btp(
--    text, text, text, text, text, text, text, text, text, boolean, timestamptz, text);
-- ============================================================================
