/**
 * BTP EXPERTISE — réception des demandes et espace de gestion
 * -----------------------------------------------------------
 * Deux rôles dans un seul script :
 *
 *   doPost  → reçoit le formulaire du site, range les photos, envoie les mails
 *   doGet   → affiche l'espace de gestion (interface web, fichier Admin.html)
 *
 * Le stockage est un classeur créé automatiquement au premier lancement :
 * vous n'avez jamais à l'ouvrir, tout se pilote depuis l'interface.
 *
 * Installation : voir INSTALLATION.md
 */

// =====================================================================
//  RÉGLAGES — les seules lignes à modifier
// =====================================================================

var REGLAGES = {
  // Adresse qui reçoit les demandes (plusieurs adresses séparées par des virgules)
  destinataire: "contact@btpexpertise.fr",

  // Nom affiché comme expéditeur des mails
  nomExpediteur: "BTP Expertise",

  // Adresse qui doit apparaître comme expéditeur.
  // Elle n'est utilisée que si elle est déclarée comme alias d'envoi dans le
  // Gmail du compte qui héberge le script (Paramètres → Comptes et importation
  // → « Envoyer des e-mails en tant que »). Tant que ce n'est pas fait, les
  // messages partent de l'adresse du compte, sans rien casser.
  // Voir backoffice/INSTALLATION.md.
  expediteur: "contact@btpexpertise.fr",

  // Adresse et téléphone affichés dans l'accusé de réception
  emailAffiche: "contact@btpexpertise.fr",
  telephone: "06 81 65 15 91",

  // Code d'accès à l'espace de gestion. À CHANGER avant la mise en service.
  codeAcces: "btp-1qfx-1ts7",

  // Mot de passe partagé avec le site. À recopier à l'identique dans contenu.py.
  jeton: "btpx-2026-a7f3",

  // Envoyer un accusé de réception au prospect
  accuseReception: true,

  // ---- CRM Groupe (Supabase) ----
  // Chaque prise de rendez-vous crée un contact et une affaire dans la
  // pipeline BTP Expertise. L'écriture passe par une fonction dédiée de la
  // base, qui n'autorise que ça : la clé ci-dessous ne donne aucun autre
  // droit, et ne permet de lire aucune donnée du groupe.
  // Mettre crmActif à false pour suspendre l'envoi sans rien décâbler.
  crmActif: true,
  crmUrl: "https://qnidmkufauzguultdmky.supabase.co",
  crmCle: "",
  crmCanal: "Site internet direct",

  // Noms des espaces de rangement créés automatiquement
  dossierPhotos: "BTP Expertise - photos des demandes",
  nomClasseur: "BTP Expertise - donnees des demandes"
};

// Habillage des courriels envoyés au prospect.
// Le logo est servi par le site : en PNG, et non en WebP, que plusieurs
// clients de messagerie (dont Outlook) ne savent pas afficher.
var MAIL = {
  logo: "https://btpexpertise.fr/assets/img/logo-btp-expertise-mail.png",
  site: "https://btpexpertise.fr",
  bleuNuit: "#262C42",
  orange: "#FF8A00",
  bleu: "#0BBBF6",
  gris: "#6B7186",
  grisFond: "#F4F4F4",
  bordure: "#E3E7ED"
};

var STATUTS = ["À traiter", "En cours", "Devis envoyé", "Gagné", "Perdu"];

var COLONNES = [
  "Date", "Type", "Objet", "Nom", "Prenom", "Email",
  "Telephone", "Ville", "Description", "Photos", "Consentement",
  "Statut", "Note"
];

// =====================================================================
//  Stockage — créé tout seul, jamais à ouvrir à la main
// =====================================================================

function classeur() {
  var proprietes = PropertiesService.getScriptProperties();
  var id = proprietes.getProperty("idClasseur");

  if (id) {
    try {
      return SpreadsheetApp.openById(id);
    } catch (e) {
      // le classeur a été supprimé : on en recrée un
    }
  }
  var nouveau = SpreadsheetApp.create(REGLAGES.nomClasseur);
  proprietes.setProperty("idClasseur", nouveau.getId());
  return nouveau;
}

function feuille() {
  var c = classeur();
  var f = c.getSheets()[0];
  if (f.getLastRow() === 0) {
    f.appendRow(COLONNES);
    f.getRange(1, 1, 1, COLONNES.length).setFontWeight("bold");
    f.setFrozenRows(1);
  }
  return f;
}

function dossierPhotos() {
  var dossiers = DriveApp.getFoldersByName(REGLAGES.dossierPhotos);
  return dossiers.hasNext() ? dossiers.next() : DriveApp.createFolder(REGLAGES.dossierPhotos);
}

// =====================================================================
//  Réception du formulaire du site
// =====================================================================

function doPost(e) {
  try {
    var donnees = JSON.parse(e.postData.contents);

    if (donnees.jeton !== REGLAGES.jeton) {
      return reponse({ success: false, message: "Jeton invalide" });
    }
    if (donnees.piege) {
      return reponse({ success: true });   // robot : on ignore en silence
    }

    // Prise de rendez-vous : l'agenda enregistre lui-meme la demande.
    if (donnees.action === "reserver") {
      return reponse(apiReserver(donnees));
    }

    var champs = {
      type: nettoyer(donnees.type),
      objet: nettoyer(donnees.objet),
      nom: nettoyer(donnees.nom),
      prenom: nettoyer(donnees.prenom),
      email: nettoyer(donnees.email),
      telephone: nettoyer(donnees.telephone),
      ville: nettoyer(donnees.ville),
      description: nettoyer(donnees.description),
      consentement: donnees.consentement ? "Oui" : "Non"
    };

    if (!champs.email || !champs.nom || !champs.description) {
      return reponse({ success: false, message: "Champs obligatoires manquants" });
    }

    var photos = enregistrerPhotos(donnees.photos, champs);
    enregistrerLigne(champs, photos);
    envoyerAuCabinet(champs, photos, donnees);
    if (REGLAGES.accuseReception) {
      envoyerAuProspect(champs);
    }
    return reponse({ success: true });

  } catch (erreur) {
    journaliserErreur(erreur, e);
    return reponse({ success: false, message: "Erreur interne" });
  }
}

function reponse(objet) {
  return ContentService
    .createTextOutput(JSON.stringify(objet))
    .setMimeType(ContentService.MimeType.JSON);
}

function nettoyer(valeur) {
  if (!valeur) return "";
  var texte = String(valeur);
  var sortie = "";
  for (var i = 0; i < texte.length; i++) {
    var code = texte.charCodeAt(i);
    if (code === 9 || code === 10 || code === 13 || (code >= 32 && code !== 127)) {
      sortie += texte.charAt(i);
    }
  }
  return sortie.trim().slice(0, 5000);
}

function enregistrerPhotos(liste, champs) {
  if (!liste || !liste.length) return [];

  var parent = dossierPhotos();
  var horodatage = Utilities.formatDate(new Date(), "Europe/Paris", "yyyy-MM-dd HH'h'mm");
  var nomDossier = horodatage + " - " + (champs.nom || "sans nom") +
                   (champs.ville ? " (" + champs.ville + ")" : "");
  var dossier = parent.createFolder(nomDossier);

  var resultat = [];
  for (var i = 0; i < liste.length && i < 5; i++) {
    try {
      var photo = liste[i];
      var blob = Utilities.newBlob(
        Utilities.base64Decode(photo.donnees),
        photo.type || "image/jpeg",
        photo.nom || ("photo-" + (i + 1) + ".jpg")
      );
      var fichier = dossier.createFile(blob);
      resultat.push({ id: fichier.getId(), nom: fichier.getName() });
    } catch (err) {
      journaliserErreur(err, null);
    }
  }
  return resultat;
}

function enregistrerLigne(champs, photos) {
  feuille().appendRow([
    new Date(), champs.type, champs.objet, champs.nom, champs.prenom,
    champs.email, champs.telephone, champs.ville, champs.description,
    JSON.stringify(photos), champs.consentement, STATUTS[0], ""
  ]);
}

// =====================================================================
//  CRM Groupe — inscription des prospects
// =====================================================================

/* Le CRM a ses propres listes de valeurs : on y fait correspondre celles du
   site plutôt que d'envoyer du texte libre, sinon les filtres et les
   statistiques du CRM ne retrouvent pas leurs petits. */
var CRM_PROBLEMATIQUE = {
  "Fissures": "Fissures",
  "Humidité / infiltration": "Humidité",
  "Malfaçons / non-conformités": "Malfaçons",
  "Plomberie": "Plomberie",
  "Électricité": "Électricité",
  "Litige travaux": "Litige travaux",
  "Avant achat": "Avant achat",
  "Réception de travaux": "Réception de travaux"
};

var CRM_TYPE_BIEN = {
  "Appartement": "Appartement",
  "Maison individuelle": "Maison",
  "Villa": "Maison",
  "Immeuble / copropriété": "Immeuble",
  "Local professionnel": "Local pro"
};


/**
 * Crée le prospect dans la pipeline BTP Expertise du CRM.
 *
 * Ne bloque jamais la prise de rendez-vous : si le CRM est indisponible, la
 * demande reste enregistrée et le cabinet prévenu. L'échec est consigné.
 */
function inscrireAuCrm(donnees, debut, format) {
  if (!REGLAGES.crmActif || !REGLAGES.crmUrl || !REGLAGES.crmCle) return false;

  var demande = nettoyer(donnees.objet);
  var besoin = nettoyer(donnees.besoin);
  // Les missions d'AMO n'ont pas d'équivalent un à un dans le CRM : elles
  // entrent toutes sous « AMO / accompagnement », le détail restant dans la
  // description.
  var problematique = CRM_PROBLEMATIQUE[demande] ||
                      (estAmo(donnees) ? "AMO / accompagnement" : "Autre");

  var charge = {
    p_prenom: nettoyer(donnees.prenom),
    p_nom: nettoyer(donnees.nom),
    p_email: nettoyer(donnees.email),
    p_telephone: nettoyer(donnees.telephone),
    p_ville: nettoyer(donnees.ville),
    p_probleme: problematique,
    p_type_bien: CRM_TYPE_BIEN[nettoyer(donnees.typeBien)] || "Autre",
    p_description: [
      "Besoin : " + besoin,
      "Demande : " + demande,
      "Format : " + (enLigne(format) ? "Visioconférence" : "Échange téléphonique"),
      "", nettoyer(donnees.description)
    ].join("\n"),
    p_canal: REGLAGES.crmCanal,
    p_consentement: donnees.consentement ? true : false,
    p_rdv: debut ? debut.toISOString() : null,
    // Le besoin tel quel : c'est lui qui range l'affaire dans la pipeline
    // Expertise ou AMO cote CRM. Sans ce champ, le tri retombe sur la
    // demande, ce qui marche mais devine au lieu de savoir.
    p_besoin: besoin
  };

  try {
    var reponse = UrlFetchApp.fetch(
      REGLAGES.crmUrl + "/rest/v1/rpc/creer_prospect_btp",
      {
        method: "post",
        contentType: "application/json",
        headers: {
          apikey: REGLAGES.crmCle,
          Authorization: "Bearer " + REGLAGES.crmCle
        },
        payload: JSON.stringify(charge),
        muteHttpExceptions: true
      });

    var code = reponse.getResponseCode();
    if (code >= 200 && code < 300) return true;

    journaliserErreur(
      new Error("CRM : HTTP " + code + " — " + reponse.getContentText().slice(0, 300)),
      null);
    return false;

  } catch (erreur) {
    journaliserErreur(erreur, null);
    return false;
  }
}


/**
 * Vérifie la liaison avec le CRM. À lancer depuis l'éditeur.
 * Crée un prospect d'essai, à supprimer ensuite dans le CRM.
 */
function testerCrm() {
  Logger.log("CRM actif   : %s", String(REGLAGES.crmActif));
  Logger.log("Adresse     : %s", REGLAGES.crmUrl);
  if (!REGLAGES.crmActif) { Logger.log("Envoi suspendu (crmActif = false)."); return; }

  var demain = new Date();
  demain.setDate(demain.getDate() + 3);
  demain.setHours(10, 0, 0, 0);

  var ok = inscrireAuCrm({
    prenom: "ESSAI", nom: "A SUPPRIMER",
    email: "essai@btpexpertise.fr", telephone: "0600000000",
    ville: "Nice", besoin: "Expertise bâtiment", objet: "Fissures",
    typeBien: "Villa", description: "Prospect d'essai créé par testerCrm().",
    consentement: true
  }, demain, "telephone");

  Logger.log("");
  if (ok) {
    Logger.log("OK : le prospect ESSAI A SUPPRIMER est dans la pipeline BTP.");
    Logger.log("Pensez à le supprimer depuis le CRM.");
  } else {
    Logger.log("Échec. Le détail est dans l'onglet « Erreurs » du classeur.");
    Logger.log("Causes habituelles : la fonction creer_prospect_btp n'existe pas");
    Logger.log("encore dans Supabase, ou son exécution n'est pas ouverte au rôle anon.");
  }
}


/**
 * Diagnostic complet des courriels. À lancer depuis l'éditeur.
 *
 * Envoie les deux messages réellement utilisés en production — celui du
 * cabinet et celui du prospect — et dit par quelle voie chacun est parti,
 * avec quelle adresse d'expéditeur. C'est le seul moyen de distinguer un
 * courriel qui n'a pas été envoyé d'un courriel qui n'est pas arrivé.
 *
 * Les deux partent vers REGLAGES.destinataire, pour être comparés côte à côte.
 */
function testerMails() {
  _traceEnvois = [];

  var compte = "";
  try { compte = Session.getEffectiveUser().getEmail(); } catch (e) { compte = "(inconnu)"; }

  Logger.log("Compte du script     : %s", compte);
  Logger.log("Expediteur souhaite  : %s", REGLAGES.expediteur);
  Logger.log("Alias utilisable     : %s", aliasDisponible() ? "oui" : "NON");
  Logger.log("Destinataire interne : %s", REGLAGES.destinataire);
  Logger.log("Service Gmail API    : %s",
             (typeof Gmail === "undefined") ? "ABSENT" : "present");
  Logger.log("Mails restants       : %s", String(MailApp.getRemainingDailyQuota()));
  Logger.log("");

  var quand = new Date();
  quand.setDate(quand.getDate() + 3);
  quand.setHours(10, 0, 0, 0);

  var donnees = {
    prenom: "ESSAI", nom: "COURRIEL", email: REGLAGES.destinataire,
    telephone: "0600000000", ville: "Nice", besoin: "Expertise bâtiment",
    objet: "Fissures", typeBien: "Villa",
    description: "Message d'essai envoyé par testerMails().",
    consentement: true
  };
  var champs = {
    type: "Rendez-vous téléphonique", objet: donnees.objet,
    nom: donnees.nom, prenom: donnees.prenom, email: donnees.email,
    telephone: donnees.telephone, ville: donnees.ville,
    description: "RENDEZ-VOUS : essai\nFormat : Échange téléphonique\n\n" +
                 donnees.description,
    consentement: "Oui"
  };

  try {
    envoyerAuCabinet(champs, [], donnees,
                     inviteRendezVous(donnees, champs, quand,
                                      new Date(quand.getTime() + 30 * 60000),
                                      "telephone", "PUBLISH"),
                     "");
  } catch (erreur) {
    Logger.log("Courriel du cabinet : ERREUR — %s", erreur.message);
  }

  try {
    envoyerConfirmationRdv(donnees, champs, quand, "telephone", []);
  } catch (erreur) {
    Logger.log("Courriel du prospect : ERREUR — %s", erreur.message);
  }

  Logger.log("Envois tentés : %s", String(_traceEnvois.length));
  for (var i = 0; i < _traceEnvois.length; i++) {
    var t = _traceEnvois[i];
    Logger.log("  %s. %s", String(i + 1), t.voie);
    Logger.log("     a  : %s", t.a);
    Logger.log("     de : %s", t.de);
    if (t.erreur) Logger.log("     ERREUR : %s", t.erreur);
  }

  Logger.log("");
  Logger.log("Les deux messages partent vers %s.", REGLAGES.destinataire);
  Logger.log("S'ils arrivent sur la boite Gmail du script au lieu d'Outlook,");
  Logger.log("c'est que l'adresse est declaree « alias » dans Gmail : decochez");
  Logger.log("« Traiter comme un alias » dans Parametres > Comptes et importation.");
}


// =====================================================================
//  Entretien — à lancer depuis l'éditeur
// =====================================================================

/**
 * Liste les rendez-vous à venir, avec leur numéro.
 *
 * C'est ce numéro que prend supprimerRdv(). La feuille « Rendez-vous » n'est
 * pas visible depuis l'espace de gestion : cette fonction est le moyen le plus
 * simple de voir ce qu'elle contient.
 */
function listerRdv() {
  var f = feuilleRdv();
  if (f.getLastRow() < 2) {
    Logger.log("Aucun rendez-vous enregistré.");
    return;
  }

  var valeurs = f.getRange(2, 1, f.getLastRow() - 1, COL_RDV.cle).getValues();
  var maintenant = new Date();
  var aVenir = 0;

  Logger.log("N°  QUAND                            QUI                  STATUT");
  Logger.log("--------------------------------------------------------------------");

  for (var i = 0; i < valeurs.length; i++) {
    var v = valeurs[i];
    var debut = v[COL_RDV.debut - 1];
    if (!(debut instanceof Date)) continue;

    var qui = [v[COL_RDV.prenom - 1], v[COL_RDV.nom - 1]]
                .filter(function (x) { return x; }).join(" ");
    var quand = Utilities.formatDate(debut, AGENDA.fuseau, "EEE dd/MM/yyyy 'a' HH'h'mm");
    var passe = debut < maintenant ? " (passé)" : "";
    if (!passe) aVenir++;

    Logger.log("%s   %s   %s   %s%s",
               pad(String(i + 2), 3), pad(quand, 30), pad(qui, 20),
               v[COL_RDV.statut - 1], passe);
    Logger.log("      %s", v[COL_RDV.email - 1]);
  }

  Logger.log("");
  Logger.log("%s rendez-vous à venir.", aVenir);
  Logger.log("Pour en supprimer : supprimerRdv(\"3\") ou supprimerRdv(\"3,5,8\")");
}


function pad(texte, n) {
  texte = String(texte);
  while (texte.length < n) texte += " ";
  return texte;
}


/**
 * Supprime tous les rendez-vous d'essai : ligne du classeur et événement
 * de l'agenda.
 *
 * Un rendez-vous est considéré comme un essai si son nom ou son prénom
 * commence par TEST, ESSAI ou SONDE. Les vraies demandes ne sont jamais
 * touchées, et la fonction affiche ce qu'elle supprime avant de le faire.
 */
function supprimerTests() {
  var MARQUEURS = ["TEST", "ESSAI", "SONDE"];

  var estUnEssai = function (v) {
    var t = String(v || "").trim().toUpperCase();
    for (var i = 0; i < MARQUEURS.length; i++) {
      if (t.indexOf(MARQUEURS[i]) === 0) return true;
    }
    return false;
  };

  var f = feuilleRdv();
  if (f.getLastRow() < 2) {
    Logger.log("Aucun rendez-vous enregistré.");
    return;
  }

  var valeurs = f.getRange(2, 1, f.getLastRow() - 1, COL_RDV.cle).getValues();
  var aSupprimer = [];

  for (var i = 0; i < valeurs.length; i++) {
    var v = valeurs[i];
    if (!estUnEssai(v[COL_RDV.nom - 1]) && !estUnEssai(v[COL_RDV.prenom - 1])) {
      continue;
    }
    aSupprimer.push({ rang: i + 2, v: v });
  }

  if (!aSupprimer.length) {
    Logger.log("Aucun rendez-vous d'essai trouvé.");
    Logger.log("Les essais se reconnaissent à un nom commençant par TEST, ESSAI ou SONDE.");
    return;
  }

  Logger.log("%s rendez-vous d'essai :", String(aSupprimer.length));
  for (var k = 0; k < aSupprimer.length; k++) {
    var v = aSupprimer[k].v;
    var d = v[COL_RDV.debut - 1];
    Logger.log("  %s — %s %s (%s)",
               d instanceof Date
                 ? Utilities.formatDate(d, AGENDA.fuseau, "EEE dd/MM 'a' HH'h'mm")
                 : "?",
               v[COL_RDV.prenom - 1], v[COL_RDV.nom - 1], v[COL_RDV.email - 1]);
  }
  Logger.log("");

  // Du bas vers le haut : supprimer une ligne décale toutes celles du dessous.
  aSupprimer.sort(function (a, b) { return b.rang - a.rang; });

  var faits = 0;
  for (var j = 0; j < aSupprimer.length; j++) {
    var e = aSupprimer[j];
    var qui = [e.v[COL_RDV.prenom - 1], e.v[COL_RDV.nom - 1]]
                .filter(function (x) { return x; }).join(" ");
    var debut = e.v[COL_RDV.debut - 1];
    if (debut instanceof Date) {
      supprimerEvenementRdv(debut, e.v[COL_RDV.fin - 1], qui);
    }
    f.deleteRow(e.rang);
    faits++;
  }

  Logger.log("%s rendez-vous supprimés, agenda compris.", String(faits));
  Logger.log("Les créneaux correspondants sont de nouveau proposés sur le site.");
  Logger.log("");
  Logger.log("Restent à supprimer à la main : les contacts et affaires d'essai");
  Logger.log("dans le CRM (voir backoffice/crm-menage.sql).");
}


/**
 * Supprime un ou plusieurs rendez-vous, par leur numéro donné par listerRdv().
 *
 * Retire la ligne de la feuille ET l'événement de l'agenda : les deux comptent
 * pour bloquer un créneau, en oublier un le laisserait indisponible.
 * Exemple : supprimerRdv("4,5,7")
 */
function supprimerRdv(numeros) {
  var liste = String(numeros || "").split(",")
    .map(function (n) { return parseInt(String(n).trim(), 10); })
    .filter(function (n) { return n >= 2; });

  if (!liste.length) {
    Logger.log("Aucun numéro valide. Exemple : supprimerRdv(\"4,5\")");
    return;
  }

  var f = feuilleRdv();
  // Du bas vers le haut : supprimer une ligne décale toutes celles du dessous.
  liste.sort(function (a, b) { return b - a; });

  var faits = 0;
  for (var i = 0; i < liste.length; i++) {
    var rang = liste[i];
    if (rang > f.getLastRow()) {
      Logger.log("Ligne %s : inexistante.", rang);
      continue;
    }

    var v = f.getRange(rang, 1, 1, COL_RDV.cle).getValues()[0];
    var qui = [v[COL_RDV.prenom - 1], v[COL_RDV.nom - 1]]
                .filter(function (x) { return x; }).join(" ");
    var debut = v[COL_RDV.debut - 1];
    var quand = debut instanceof Date
      ? Utilities.formatDate(debut, AGENDA.fuseau, "dd/MM 'a' HH'h'mm") : "?";

    if (debut instanceof Date) {
      supprimerEvenementRdv(debut, v[COL_RDV.fin - 1], qui);
    }
    f.deleteRow(rang);
    faits++;
    Logger.log("Supprimé : %s — %s", quand, qui);
  }

  Logger.log("");
  Logger.log("%s rendez-vous supprimé(s). Les créneaux sont de nouveau libres.", faits);
  Logger.log("Vérifiez l'agenda Outlook : les rendez-vous déjà acceptés y restent.");
}


// =====================================================================
//  Envoi des courriels
// =====================================================================

/**
 * Point d'envoi unique.
 *
 * Apps Script envoie par défaut depuis l'adresse du compte qui exécute le
 * script. Pour que les messages partent de l'adresse du domaine, celle-ci doit
 * être déclarée comme alias d'envoi dans Gmail ; on la vérifie une fois par
 * exécution, et on retombe silencieusement sur l'envoi ordinaire si elle ne
 * l'est pas — un formulaire ne doit jamais échouer pour une question
 * d'en-tête d'expéditeur.
 */
var _aliasVerifie = null;

function aliasDisponible() {
  if (_aliasVerifie !== null) return _aliasVerifie;
  _aliasVerifie = false;
  try {
    var voulu = (REGLAGES.expediteur || "").toLowerCase();
    if (voulu) {
      var alias = GmailApp.getAliases();
      for (var i = 0; i < alias.length; i++) {
        if (String(alias[i]).toLowerCase() === voulu) { _aliasVerifie = true; break; }
      }
    }
  } catch (erreur) {
    // Autorisation Gmail absente : on se contentera de l'envoi ordinaire.
    _aliasVerifie = false;
  }
  return _aliasVerifie;
}

// Journal des envois de l'exécution en cours, pour testerMails().
var _traceEnvois = [];

function tracer(voie, destinataire, expediteur, erreur) {
  _traceEnvois.push({
    voie: voie, a: destinataire, de: expediteur,
    erreur: erreur ? String(erreur.message || erreur) : ""
  });
}


function envoyerMail(options) {
  if (aliasDisponible()) {
    try {
      GmailApp.sendEmail(options.to, options.subject, "", {
        htmlBody: options.htmlBody,
        name: options.name || REGLAGES.nomExpediteur,
        from: REGLAGES.expediteur,
        replyTo: options.replyTo || REGLAGES.expediteur,
        attachments: options.attachments
      });
      tracer("Gmail (alias)", options.to, REGLAGES.expediteur, null);
      return;
    } catch (erreur) {
      journaliserErreur(erreur, null);   // et on bascule sur la voie ordinaire
      tracer("Gmail (alias) ECHEC", options.to, REGLAGES.expediteur, erreur);
    }
  }
  try {
    MailApp.sendEmail(options);
    tracer("envoi ordinaire", options.to, "(compte du script)", null);
  } catch (erreur) {
    journaliserErreur(erreur, null);
    tracer("envoi ordinaire ECHEC", options.to, "(compte du script)", erreur);
    throw erreur;              // un courriel perdu ne doit pas passer inaperçu
  }
}


/**
 * Vérifie d'où partent les courriels. À lancer depuis l'éditeur.
 */
function testerExpediteur() {
  var compte = "";
  try { compte = Session.getEffectiveUser().getEmail(); } catch (e) { compte = "(inconnu)"; }
  Logger.log("Compte qui execute le script : %s", compte);
  Logger.log("Expediteur souhaite           : %s", REGLAGES.expediteur);

  var alias = [];
  try { alias = GmailApp.getAliases(); } catch (e) {
    Logger.log("");
    Logger.log("Impossible de lire les alias : %s", e.message);
    Logger.log("Relancez une autorisation depuis l'editeur.");
    return;
  }

  Logger.log("Alias declares                : %s",
             alias.length ? alias.join(", ") : "aucun");
  Logger.log("");
  if (aliasDisponible()) {
    Logger.log("OK : les courriels partiront de %s", REGLAGES.expediteur);
  } else {
    Logger.log("L'adresse %s n'est pas un alias d'envoi.", REGLAGES.expediteur);
    Logger.log("Les courriels partiront de %s.", compte);
    Logger.log("Pour y remedier : Gmail > Parametres > Comptes et importation");
    Logger.log("> Envoyer des e-mails en tant que > Ajouter une autre adresse.");
  }
}


// =====================================================================
//  Courriels
// =====================================================================

/**
 * Courriel interne : celui que le cabinet reçoit.
 *
 * Il ne reprend pas l'habillage des courriels prospect — pas de logo, pas de
 * formule de politesse. C'est une fiche de travail : ce qu'il faut savoir en
 * un coup d'oeil, le rendez-vous en tête s'il y en a un, et un bouton pour
 * ouvrir le dossier. Répondre au message écrit directement au demandeur.
 */
function envoyerAuCabinet(champs, photos, donnees, invitation, cle) {
  if (champs.type && champs.type.indexOf("Candidature") === 0) {
    return envoyerCandidatureAuCabinet(champs, donnees);
  }

  var estRdv = champs.type && champs.type.indexOf("Rendez-vous") === 0;
  var qui = [champs.prenom, champs.nom].filter(function (v) { return v; }).join(" ");

  var sujet = (estRdv ? "RDV " : "Demande ") +
              (champs.objet ? champs.objet + " " : "") +
              "\u2014 " + (qui || "sans nom") +
              (champs.ville ? " (" + champs.ville + ")" : "");

  // La premiere ligne de la description porte le creneau pour un rendez-vous.
  var lignes = String(champs.description || "").split("\n");
  var bandeau = "";
  if (estRdv && lignes.length && lignes[0].indexOf("RENDEZ-VOUS") === 0) {
    bandeau =
      '<div style="margin:0 0 22px;padding:16px 20px;border-radius:10px;' +
          'background:#FFF4E6;border-left:4px solid ' + MAIL.orange + '">' +
        '<div style="font-size:12px;font-weight:700;letter-spacing:.05em;' +
            'text-transform:uppercase;color:#A35C00">Rendez-vous confirm\u00e9</div>' +
        '<div style="margin-top:5px;font-size:17px;font-weight:700">' +
          echapper(lignes[0].replace("RENDEZ-VOUS : ", "")) + '</div>' +
        (lignes[1] ? '<div style="margin-top:3px;font-size:14px;color:' + MAIL.gris +
                     '">' + echapper(lignes[1]) + '</div>' : "") +
      '</div>';
    lignes = lignes.slice(2);
  }

  var libre = lignes.join("\n").replace(/^\n+|\n+$/g, "");

  var joints = "aucun";
  if (photos && photos.length) {
    joints = photos.map(function (p) {
      return '<a href="https://drive.google.com/file/d/' + p.id + '/view" ' +
             'style="color:' + MAIL.bleu + '">' + echapper(p.nom) + "</a>";
    }).join("<br>");
  }

  var corps =
    '<div style="margin:0;padding:24px 12px;background:' + MAIL.grisFond + '">' +
      '<table role="presentation" cellpadding="0" cellspacing="0" border="0" ' +
             'style="max-width:640px;margin:0 auto;width:100%;background:#FFFFFF;' +
             'border-radius:12px;overflow:hidden;font-family:Helvetica,Arial,sans-serif;' +
             'color:' + MAIL.bleuNuit + '">' +

        '<tr><td style="padding:20px 26px;background:' + MAIL.bleuNuit + ';color:#FFFFFF">' +
          '<div style="font-size:12px;letter-spacing:.06em;text-transform:uppercase;' +
              'color:#B9BFCE">' + (estRdv ? "Nouveau rendez-vous" : "Nouvelle demande") +
          '</div>' +
          '<div style="margin-top:4px;font-size:19px;font-weight:700">' +
            echapper(qui || "Demandeur sans nom") + '</div>' +
          '<div style="margin-top:2px;font-size:13px;color:#B9BFCE">Re\u00e7u le ' +
            Utilities.formatDate(new Date(), "Europe/Paris",
                                 "dd/MM/yyyy '\u00e0' HH'h'mm") + '</div>' +
        '</td></tr>' +

        '<tr><td style="padding:24px 26px 6px">' + bandeau +
          '<table role="presentation" cellpadding="0" cellspacing="0" border="0" ' +
                 'style="width:100%;border-collapse:collapse;font-size:14px">' +
            rangee("Type", echapper(champs.type)) +
            rangee("Demande", echapper(champs.objet)) +
            rangee("Ville du bien", echapper(champs.ville)) +
            rangee("T\u00e9l\u00e9phone", '<a href="tel:' +
                   String(champs.telephone).replace(/\s/g, "") + '" style="color:' +
                   MAIL.bleu + '">' + echapper(champs.telephone) + "</a>") +
            rangee("E-mail", '<a href="mailto:' + champs.email + '" style="color:' +
                   MAIL.bleu + '">' + echapper(champs.email) + "</a>") +
            rangee("Pi\u00e8ces jointes", joints) +
            rangee("Consentement", echapper(champs.consentement)) +
          '</table>' +
        '</td></tr>' +

        (libre
          ? '<tr><td style="padding:14px 26px 0">' +
              '<div style="font-size:12px;font-weight:700;letter-spacing:.05em;' +
                  'text-transform:uppercase;color:' + MAIL.gris + ';margin-bottom:8px">' +
                'Ce que le demandeur \u00e9crit</div>' +
              '<div style="padding:16px 18px;background:' + MAIL.grisFond + ';' +
                  'border-radius:8px;white-space:pre-wrap;font-size:14px;' +
                  'line-height:1.6">' + echapper(libre) + '</div>' +
            '</td></tr>'
          : "") +

        (cle
          ? '<tr><td style="padding:6px 26px 0">' +
              '<div style="padding:18px 20px;border-radius:10px;' +
                  'background:' + MAIL.grisFond + ';text-align:center">' +
                '<div style="font-size:14px;color:' + MAIL.gris + ';margin-bottom:14px">' +
                  'Le rendez-vous est joint \u00e0 ce message : votre agenda le ' +
                  'r\u00e9cup\u00e8re tout seul. Il est confirm\u00e9 au demandeur.</div>' +
                '<a href="' + lienReponse("non", cle) + '" ' +
                   'style="display:inline-block;background:#FFFFFF;' +
                   'color:#C0392B;border:2px solid #E7B9B3;padding:11px 26px;' +
                   'border-radius:8px;text-decoration:none;font-weight:700;font-size:14px">' +
                  'Je ne peux pas assurer ce rendez-vous</a>' +
                '<div style="margin-top:10px;font-size:12px;color:' + MAIL.gris + '">' +
                  'Le cr\u00e9neau sera lib\u00e9r\u00e9 et vous devrez rappeler ' +
                  'le demandeur.</div>' +
              '</div>' +
            '</td></tr>'
          : "") +

        '<tr><td style="padding:20px 26px 26px">' +
          '<div style="font-size:12px;color:' + MAIL.gris + '">' +
            'R\u00e9pondre \u00e0 ce message \u00e9crit directement \u00e0 ' +
            echapper(champs.email) + '.</div>' +
        '</td></tr>' +

      '</table>' +
    '</div>';

  // Courriel ordinaire, le rendez-vous simplement joint. Pas de demande de
  // réunion : elle affichait un bandeau d'agenda en tête du message, pour un
  // agenda Outlook qui n'est de toute façon pas celui qu'utilise le cabinet.
  // L'agenda Google, lui, est alimenté directement par le script — voir
  // creerEvenementDepuisDemande() — et n'a rien à voir avec ce fichier.
  envoyerMail({
    to: REGLAGES.destinataire,
    subject: sujet,
    htmlBody: corps,
    replyTo: champs.email,
    name: REGLAGES.nomExpediteur,
    attachments: invitation ? [invitation] : undefined
  });
}


/** Adresse d'un bouton de réponse. La clé est tirée au hasard, donc non devinable. */
function lienReponse(reponse, cle) {
  return adresseEspace() + "?action=rdv&r=" + reponse +
         "&cle=" + encodeURIComponent(cle);
}

/**
 * Courriel interne d'une candidature au réseau d'experts.
 *
 * Une candidature ne se lit pas comme une demande de client : ce qui compte
 * est ce qui permet de décider — expérience, spécialités, qualifications et
 * surtout la RC professionnelle, sans laquelle le cabinet ne peut pas confier
 * de mission. Elle est donc mise en évidence, et signalée quand elle manque.
 */
function envoyerCandidatureAuCabinet(champs, donnees) {
  var c = (donnees && donnees.candidature) || {};
  var val = function (v) { return nettoyer(v || ""); };

  var rcpro = val(c.rcpro);
  var blocRc = rcpro
    ? '<div style="margin:0 0 22px;padding:15px 20px;border-radius:10px;' +
          'background:#E8F7EF;border-left:4px solid #2E9E6B">' +
        '<div style="font-size:12px;font-weight:700;letter-spacing:.05em;' +
            'text-transform:uppercase;color:#1E6E49">RC professionnelle d\u00e9clar\u00e9e</div>' +
        '<div style="margin-top:4px;font-size:15px;font-weight:700">' +
          echapper(rcpro) + '</div>' +
      '</div>'
    : '<div style="margin:0 0 22px;padding:15px 20px;border-radius:10px;' +
          'background:#FDECEC;border-left:4px solid #C0392B">' +
        '<div style="font-size:12px;font-weight:700;letter-spacing:.05em;' +
            'text-transform:uppercase;color:#8E2B20">RC professionnelle non renseign\u00e9e</div>' +
        '<div style="margin-top:4px;font-size:14px">\u00c0 demander avant toute mission.</div>' +
      '</div>';

  var message = val(c.message);

  var corps =
    '<div style="margin:0;padding:24px 12px;background:' + MAIL.grisFond + '">' +
      '<table role="presentation" cellpadding="0" cellspacing="0" border="0" ' +
             'style="max-width:640px;margin:0 auto;width:100%;background:#FFFFFF;' +
             'border-radius:12px;overflow:hidden;font-family:Helvetica,Arial,sans-serif;' +
             'color:' + MAIL.bleuNuit + '">' +

        '<tr><td style="padding:20px 26px;background:' + MAIL.bleuNuit + ';color:#FFFFFF">' +
          '<div style="font-size:12px;letter-spacing:.06em;text-transform:uppercase;' +
              'color:#B9BFCE">Candidature au r\u00e9seau</div>' +
          '<div style="margin-top:4px;font-size:19px;font-weight:700">' +
            echapper(champs.nom || "Candidat sans nom") + '</div>' +
          (val(c.societe)
            ? '<div style="margin-top:2px;font-size:14px;color:#B9BFCE">' +
              echapper(val(c.societe)) + '</div>'
            : "") +
          '<div style="margin-top:2px;font-size:13px;color:#B9BFCE">Re\u00e7ue le ' +
            Utilities.formatDate(new Date(), "Europe/Paris",
                                 "dd/MM/yyyy '\u00e0' HH'h'mm") + '</div>' +
        '</td></tr>' +

        '<tr><td style="padding:24px 26px 6px">' + blocRc +
          '<table role="presentation" cellpadding="0" cellspacing="0" border="0" ' +
                 'style="width:100%;border-collapse:collapse;font-size:14px">' +
            rangee("D\u00e9partements", echapper(val(c.departements))) +
            rangee("Exp\u00e9rience", echapper(val(c.experience))) +
            rangee("Sp\u00e9cialit\u00e9s", echapper(val(c.specialites))) +
            rangee("Qualifications", echapper(val(c.qualifications)) || "non renseign\u00e9es") +
            rangee("SIRET", echapper(val(c.siret)) || "non renseign\u00e9") +
            rangee("T\u00e9l\u00e9phone", '<a href="tel:' +
                   String(champs.telephone).replace(/\s/g, "") + '" style="color:' +
                   MAIL.bleu + '">' + echapper(champs.telephone) + "</a>") +
            rangee("E-mail", '<a href="mailto:' + champs.email + '" style="color:' +
                   MAIL.bleu + '">' + echapper(champs.email) + "</a>") +
            rangee("Consentement", echapper(champs.consentement)) +
          '</table>' +
        '</td></tr>' +

        (message
          ? '<tr><td style="padding:14px 26px 0">' +
              '<div style="font-size:12px;font-weight:700;letter-spacing:.05em;' +
                  'text-transform:uppercase;color:' + MAIL.gris + ';margin-bottom:8px">' +
                'Message du candidat</div>' +
              '<div style="padding:16px 18px;background:' + MAIL.grisFond + ';' +
                  'border-radius:8px;white-space:pre-wrap;font-size:14px;' +
                  'line-height:1.6">' + echapper(message) + '</div>' +
            '</td></tr>'
          : "") +

        '<tr><td style="padding:20px 26px 26px">' +
          '<div style="font-size:12px;color:' + MAIL.gris + '">' +
            'R\u00e9pondre \u00e0 ce message \u00e9crit directement \u00e0 ' +
            echapper(champs.email) + '.</div>' +
        '</td></tr>' +

      '</table>' +
    '</div>';

  envoyerMail({
    to: REGLAGES.destinataire,
    subject: "Candidature \u2014 " + (champs.nom || "sans nom") +
             (val(c.societe) ? " (" + val(c.societe) + ")" : ""),
    htmlBody: corps,
    replyTo: champs.email,
    name: REGLAGES.nomExpediteur
  });
}


// =====================================================================
//  Validation d'un rendez-vous par le cabinet
// =====================================================================

/** Retrouve la ligne d'un rendez-vous à partir de sa clé. */
function ligneRdv(cle) {
  if (!cle) return null;
  var f = feuilleRdv();
  if (f.getLastRow() < 2) return null;

  var valeurs = f.getRange(2, 1, f.getLastRow() - 1, COL_RDV.cle).getValues();
  for (var i = 0; i < valeurs.length; i++) {
    if (String(valeurs[i][COL_RDV.cle - 1]) === String(cle)) {
      return { feuille: f, rang: i + 2, valeurs: valeurs[i] };
    }
  }
  return null;
}


/**
 * Réponse du cabinet : oui, le rendez-vous entre dans l'agenda ; non, le
 * créneau est libéré et il faudra rappeler le demandeur.
 *
 * Le rendez-vous reste confirmé auprès du demandeur dans les deux cas : c'est
 * l'agenda qui se décide ici, pas le rendez-vous lui-même.
 */
function pageReponseRdv(reponse, cle) {
  var l = ligneRdv(cle);
  if (!l) {
    return pageSimple("Lien expiré",
      "Ce rendez-vous est introuvable. Il a peut-être été supprimé.", "#C0392B");
  }

  var v = l.valeurs;
  var debut = v[COL_RDV.debut - 1];
  var fin = v[COL_RDV.fin - 1];
  var qui = [v[COL_RDV.prenom - 1], v[COL_RDV.nom - 1]]
              .filter(function (x) { return x; }).join(" ");
  var quand = libelleJour(debut) + " à " +
              Utilities.formatDate(debut, AGENDA.fuseau, "HH'h'mm");
  var telephone = String(v[COL_RDV.telephone - 1] || "");
  var statut = String(v[COL_RDV.statut - 1] || "");

  if (statut === RDV_REFUSE) {
    return pageSimple("Déjà refusé",
      "Le créneau du " + quand + " a été libéré. " +
      (telephone ? "Rappelez " + qui + " au " + telephone + "." : ""), "#C0392B");
  }

  if (reponse === "non") {
    l.feuille.getRange(l.rang, COL_RDV.statut).setValue(RDV_REFUSE);
    supprimerEvenementRdv(debut, fin, qui);

    return pageSimple("Créneau libéré",
      "Le créneau du <strong>" + echapper(quand) + "</strong> est de nouveau " +
      "proposé sur le site. Pensez à supprimer le rendez-vous dans votre " +
      "agenda Outlook, où il a été ajouté automatiquement." +
      (telephone
        ? "<div style=\"margin-top:22px;padding:18px 20px;background:#FFF4E6;" +
          "border-left:4px solid #FF8A00;border-radius:8px;text-align:left\">" +
          "<strong>À faire maintenant</strong><br>" +
          echapper(qui) + " a reçu une confirmation pour ce créneau. " +
          "Appelez-le pour convenir d’une autre date.<br><br>" +
          "<a href=\"tel:" + telephone.replace(/\s/g, "") + "\" " +
          "style=\"display:inline-block;background:#FF8A00;color:#fff;padding:12px 26px;" +
          "border-radius:8px;text-decoration:none;font-weight:700\">Appeler le " +
          echapper(telephone) + "</a></div>"
        : ""),
      "#C0392B");
  }

  // Seul le désistement mène ici : le rendez-vous entre dans l'agenda tout
  // seul, il n'y a rien à confirmer.
  return pageSimple("Rendez-vous maintenu",
    "Le rendez-vous avec <strong>" + echapper(qui) + "</strong> le <strong>" +
    echapper(quand) + "</strong> reste programmé. Vous pouvez fermer cette page.",
    "#2E9E6B");
}


/**
 * Ouvre un agenda à partir de son identifiant.
 *
 * Renvoie null au lieu de lever : un identifiant mal recopié ne doit jamais
 * coûter un rendez-vous, il doit se voir dans l'onglet « Erreurs ».
 */
function ouvrirAgenda(identifiant) {
  if (!identifiant) return null;
  try {
    return identifiant === "primary"
      ? CalendarApp.getDefaultCalendar()
      : CalendarApp.getCalendarById(identifiant);
  } catch (erreur) {
    journaliserErreur(erreur, { agenda: identifiant });
    return null;
  }
}


/** L'agenda où doit atterrir un rendez-vous, selon l'activité. */
function agendaDeLActivite(donnees) {
  return AGENDA.agendas[estAmo(donnees) ? "amo" : "expertise"] || "";
}


/**
 * Les agendas où le script écrit. Ce sont les seuls où il s'autorise à
 * supprimer : effacer par correspondance de titre dans l'agenda personnel
 * reviendrait à jouer avec les rendez-vous privés.
 */
function agendasDuSite() {
  var liste = [];
  var noms = ["expertise", "amo"];
  for (var i = 0; i < noms.length; i++) {
    var id = AGENDA.agendas[noms[i]];
    if (id && liste.indexOf(id) === -1) liste.push(id);
  }
  return liste;
}


/** Tous les agendas consultés pour savoir si un créneau est déjà pris. */
function agendasConsultes() {
  var liste = agendasDuSite();
  var autres = AGENDA.agendasBloquants || [];
  for (var i = 0; i < autres.length; i++) {
    if (autres[i] && liste.indexOf(autres[i]) === -1) liste.push(autres[i]);
  }
  return liste;
}


/**
 * Titre d'un rendez-vous, le même dans l'agenda et dans le fichier joint.
 *
 * L'activité ouvre le titre parce que la couleur ne suit pas partout : elle
 * vit dans l'agenda Google, et ne passe ni dans le fichier qu'Outlook range,
 * ni dans les vues qui affichent les rendez-vous en liste.
 */
function titreRendezVous(donnees, format) {
  var qui = (nettoyer(donnees.prenom) + " " + nettoyer(donnees.nom)).trim();
  var objet = nettoyer(donnees.objet);
  return activite(donnees) + " · " +
         (enLigne(format) ? "Visio" : "Appel") + " — " + qui +
         (objet ? " (" + objet + ")" : "");
}


/**
 * Pose le rendez-vous dans l'agenda du script, dès la réservation.
 *
 * Cet agenda-là ne sert qu'à bloquer les créneaux : l'agenda du cabinet, lui,
 * reçoit le rendez-vous par la pièce jointe de la fiche.
 */
function creerEvenementDepuisDemande(donnees, debut, fin, format) {
  var identifiant = agendaDeLActivite(donnees);
  if (!identifiant) return false;

  try {
    var cal = ouvrirAgenda(identifiant);
    if (!cal) return false;

    var evenement = cal.createEvent(
      titreRendezVous(donnees, format),
      debut, fin,
      {
        sendInvites: false,
        location: enLigne(format) ? "Visioconférence" : "Par téléphone",
        description: [
          "Besoin : " + nettoyer(donnees.besoin),
          "Demande : " + nettoyer(donnees.objet),
          "Type de bien : " + nettoyer(donnees.typeBien),
          "Ville : " + nettoyer(donnees.ville),
          "Téléphone : " + nettoyer(donnees.telephone),
          "E-mail : " + nettoyer(donnees.email),
          "", nettoyer(donnees.description)
        ].join("\n")
      }
    );

    // Couleur imposée seulement si AGENDA.couleurs en demande une. Sinon,
    // et c'est le réglage courant, l'événement garde celle de son agenda.
    // Un nom mal saisi ne doit pas coûter le rendez-vous : on l'ignore.
    var couleur = CalendarApp.EventColor[
      AGENDA.couleurs[estAmo(donnees) ? "amo" : "expertise"]];
    if (couleur) {
      try { evenement.setColor(couleur); } catch (ignoree) {}
    }
    return true;
  } catch (erreur) {
    // Le rendez-vous reste enregistré même si l'agenda refuse l'écriture.
    journaliserErreur(erreur, donnees);
    return false;
  }
}


/** Retire l'événement de l'agenda quand le cabinet refuse le créneau. */
function supprimerEvenementRdv(debut, fin, qui) {
  // Le classeur ne dit pas dans quel agenda le rendez-vous est parti : on
  // cherche dans les deux, jamais dans l'agenda personnel.
  var agendas = agendasDuSite();
  for (var a = 0; a < agendas.length; a++) {
    try {
      var cal = ouvrirAgenda(agendas[a]);
      if (!cal) continue;
      var evts = cal.getEvents(debut, fin);
      for (var i = 0; i < evts.length; i++) {
        if (evts[i].getTitle().indexOf(qui) !== -1) { evts[i].deleteEvent(); }
      }
    } catch (erreur) {
      journaliserErreur(erreur, { agenda: agendas[a] });
    }
  }
}


/** Page de réponse, sobre et lisible sur téléphone. */
function pageSimple(titre, corps, couleur) {
  var html =
    '<!doctype html><html lang="fr"><head><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1">' +
    '<title>' + echapper(titre) + ' — BTP Expertise</title></head>' +
    '<body style="margin:0;padding:28px 14px;background:#F4F4F4;' +
        'font-family:Helvetica,Arial,sans-serif;color:#262C42">' +
      '<div style="max-width:520px;margin:0 auto;background:#fff;border-radius:14px;' +
          'padding:34px 30px;text-align:center;border-top:5px solid ' + couleur + '">' +
        '<img src="' + MAIL.logo + '" width="140" alt="BTP Expertise" ' +
             'style="display:block;margin:0 auto 22px;max-width:140px;height:auto">' +
        '<h1 style="margin:0 0 14px;font-size:21px;color:' + couleur + '">' +
          echapper(titre) + '</h1>' +
        '<div style="font-size:15px;line-height:1.65">' + corps + '</div>' +
      '</div>' +
    '</body></html>';

  return HtmlService.createHtmlOutput(html)
    .addMetaTag("viewport", "width=device-width, initial-scale=1")
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}


// =====================================================================
//  Gabarit des courriels envoyés au prospect
// =====================================================================

/** Nom complet, prénom d'abord, sans espace parasite si l'un des deux manque. */
function nomComplet(champs) {
  return [champs.prenom, champs.nom]
    .filter(function (v) { return v; })
    .join(" ");
}

/**
 * Enveloppe commune : bandeau au logo, corps blanc, pied de page sombre.
 * Tout est en styles en ligne et en tableaux : c'est la seule mise en forme
 * que les clients de messagerie respectent de façon fiable.
 */
function gabaritMail(titre, contenu) {
  return '' +
  '<div style="margin:0;padding:26px 12px;background:' + MAIL.grisFond + ';">' +
    '<table role="presentation" cellpadding="0" cellspacing="0" border="0" ' +
           'style="max-width:620px;margin:0 auto;width:100%;background:#FFFFFF;' +
           'border-radius:14px;overflow:hidden;' +
           'font-family:Helvetica,Arial,sans-serif;color:' + MAIL.bleuNuit + '">' +

      '<tr><td style="padding:26px 32px 22px;text-align:center;' +
          'border-bottom:3px solid ' + MAIL.orange + '">' +
        '<img src="' + MAIL.logo + '" width="170" alt="BTP Expertise" ' +
             'style="display:block;margin:0 auto;border:0;max-width:170px;height:auto">' +
      '</td></tr>' +

      '<tr><td style="padding:30px 32px 8px">' +
        '<h1 style="margin:0 0 20px;font-size:20px;line-height:1.3;' +
            'color:' + MAIL.bleuNuit + '">' + titre + '</h1>' +
      '</td></tr>' +

      '<tr><td style="padding:0 32px 30px;font-size:15px;line-height:1.65">' +
        contenu +
      '</td></tr>' +

      '<tr><td style="padding:22px 32px;background:' + MAIL.bleuNuit + ';color:#FFFFFF;' +
          'font-size:13px;line-height:1.6">' +
        '<strong style="font-size:15px">BTP Expertise</strong><br>' +
        '<span style="color:#B9BFCE">Cabinet d\u2019expertise en b\u00e2timent ' +
        '&amp; d\u2019Assistance \u00e0 Ma\u00eetrise d\u2019Ouvrage</span><br>' +
        '<span style="color:#B9BFCE">Alpes-Maritimes (06) et Var (83)</span><br><br>' +
        '<a href="tel:+33681651591" style="color:#FFFFFF;text-decoration:none">' +
          echapper(REGLAGES.telephone) + '</a>' +
        '<span style="color:#6B7186"> &nbsp;·&nbsp; </span>' +
        '<a href="mailto:' + REGLAGES.emailAffiche + '" style="color:#FFFFFF;' +
           'text-decoration:none">' + echapper(REGLAGES.emailAffiche) + '</a>' +
        '<span style="color:#6B7186"> &nbsp;·&nbsp; </span>' +
        '<a href="' + MAIL.site + '" style="color:#FFFFFF;text-decoration:none">' +
          'btpexpertise.fr</a>' +
      '</td></tr>' +

    '</table>' +
    '<p style="max-width:620px;margin:16px auto 0;font-family:Helvetica,Arial,sans-serif;' +
        'font-size:11px;line-height:1.5;color:#9AA0AC;text-align:center">' +
      'Ce message confirme la r\u00e9ception de votre demande. Il ne constitue ni un ' +
      'avis technique, ni un engagement contractuel.</p>' +
  '</div>';
}

/** Une ligne du récapitulatif ; ignorée si la valeur est vide. */
function ligneRecap(intitule, valeur) {
  if (!valeur) return "";
  return '<tr>' +
    '<td style="padding:9px 0;width:38%;vertical-align:top;font-size:13px;' +
        'color:' + MAIL.gris + '">' + intitule + '</td>' +
    '<td style="padding:9px 0;vertical-align:top;font-size:14px;font-weight:600">' +
        valeur + '</td>' +
  '</tr>';
}

/** Bloc encadré « Récapitulatif de votre demande ». */
function blocRecap(lignes, texteLibre) {
  var corps = lignes.join("");
  if (!corps && !texteLibre) return "";

  return '<div style="margin:24px 0;border:1px solid ' + MAIL.bordure + ';' +
             'border-radius:10px;overflow:hidden">' +
    '<div style="padding:12px 18px;background:' + MAIL.grisFond + ';font-size:13px;' +
        'font-weight:700;letter-spacing:.04em;text-transform:uppercase;' +
        'color:' + MAIL.gris + '">R\u00e9capitulatif de votre demande</div>' +
    '<div style="padding:6px 18px 14px">' +
      '<table role="presentation" cellpadding="0" cellspacing="0" border="0" ' +
             'style="width:100%;border-collapse:collapse">' + corps + '</table>' +
      (texteLibre
        ? '<div style="margin-top:12px;padding-top:14px;border-top:1px solid ' +
          MAIL.bordure + ';font-size:14px;line-height:1.6;white-space:pre-wrap;' +
          'color:#3A3F52">' + texteLibre + '</div>'
        : "") +
    '</div>' +
  '</div>';
}

function envoyerAuProspect(champs) {
  var recap = blocRecap([
    ligneRecap("Votre demande", echapper(champs.objet)),
    ligneRecap("Bien concern\u00e9", echapper(champs.ville)),
    ligneRecap("T\u00e9l\u00e9phone", echapper(champs.telephone))
  ], echapper(champs.description));

  var contenu =
    "<p style=\"margin:0 0 16px\">Bonjour " + echapper(nomComplet(champs)) + ",</p>" +
    "<p style=\"margin:0 0 16px\">Nous avons bien re\u00e7u votre demande" +
      (champs.ville ? " concernant un bien \u00e0 " + echapper(champs.ville) : "") +
      ", et nous vous en remercions.</p>" +
    "<p style=\"margin:0 0 16px\">Un expert du cabinet l\u2019\u00e9tudie et revient vers " +
      "vous <strong>sous 24 \u00e0 48 heures ouvr\u00e9es</strong> avec la mission " +
      "adapt\u00e9e et nos disponibilit\u00e9s d\u2019intervention.</p>" +
    recap +
    "<p style=\"margin:16px 0 0\">Si votre situation \u00e9volue \u2014 une fissure qui " +
      "s\u2019aggrave, une infiltration active \u2014 appelez-nous directement au " +
      "<strong>" + echapper(REGLAGES.telephone) + "</strong>.</p>";

  envoyerMail({
    to: champs.email,
    subject: (champs.type && champs.type.indexOf("Candidature") === 0
              ? "Votre candidature \u2014 BTP Expertise"
              : "Votre demande d\u2019expertise \u2014 BTP Expertise"),
    htmlBody: gabaritMail(
      champs.type && champs.type.indexOf("Candidature") === 0
        ? "Votre candidature est bien re\u00e7ue"
        : "Votre demande est bien enregistr\u00e9e", contenu),
    name: REGLAGES.nomExpediteur
  });
}

function rangee(intitule, valeur) {
  return '<tr>' +
    '<td style="border-bottom:1px solid #E3E7ED;color:#6B7186;width:170px">' + intitule + "</td>" +
    '<td style="border-bottom:1px solid #E3E7ED;font-weight:600">' + (valeur || "-") + "</td></tr>";
}

function echapper(texte) {
  if (!texte) return "";
  return String(texte)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function adresseEspace() {
  try {
    return ScriptApp.getService().getUrl();
  } catch (e) {
    return "";
  }
}

// =====================================================================
//  Espace de gestion — interface web
// =====================================================================

function doGet(e) {
  // Le site interroge les creneaux libres ; le reste ouvre l'espace de gestion.
  var p = (e && e.parameter) || {};
  if (p.action === "rdv") {
    return pageReponseRdv(p.r, p.cle);
  }
  if (p.action === "creneaux") {
    var sortie = ContentService
      .createTextOutput(JSON.stringify(apiCreneaux(p.format || "telephone")))
      .setMimeType(ContentService.MimeType.JSON);
    return sortie;
  }

  return HtmlService.createTemplateFromFile("Admin")
    .evaluate()
    .setTitle("BTP Expertise - Demandes")
    .addMetaTag("viewport", "width=device-width, initial-scale=1")
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function verifierCode(code) {
  if (code !== REGLAGES.codeAcces) {
    throw new Error("Code d'accès incorrect");
  }
}

/** Liste complète des demandes, la plus récente en premier. */
function apiListe(code) {
  verifierCode(code);
  var f = feuille();
  if (f.getLastRow() < 2) return [];

  var valeurs = f.getRange(2, 1, f.getLastRow() - 1, COLONNES.length).getValues();
  var demandes = [];

  for (var i = 0; i < valeurs.length; i++) {
    var v = valeurs[i];
    var photos = [];
    try { photos = JSON.parse(v[9] || "[]"); } catch (e) { photos = []; }

    demandes.push({
      ligne: i + 2,
      date: v[0] instanceof Date ? v[0].toISOString() : String(v[0]),
      type: String(v[1] || ""),
      objet: String(v[2] || ""),
      nom: String(v[3] || ""),
      prenom: String(v[4] || ""),
      email: String(v[5] || ""),
      telephone: String(v[6] || ""),
      ville: String(v[7] || ""),
      description: String(v[8] || ""),
      photos: photos,
      consentement: String(v[10] || ""),
      statut: String(v[11] || STATUTS[0]),
      note: String(v[12] || "")
    });
  }
  return demandes.reverse();
}

function apiStatut(code, ligne, statut) {
  verifierCode(code);
  if (STATUTS.indexOf(statut) === -1) throw new Error("Statut inconnu");
  feuille().getRange(ligne, 12).setValue(statut);
  return true;
}

function apiNote(code, ligne, note) {
  verifierCode(code);
  feuille().getRange(ligne, 13).setValue(String(note || "").slice(0, 5000));
  return true;
}

function apiSupprimer(code, ligne) {
  verifierCode(code);
  feuille().deleteRow(ligne);
  return true;
}

/** Renvoie une vignette de photo en base64, pour l'affichage dans l'interface. */
function apiVignette(code, id) {
  verifierCode(code);
  try {
    var fichier = DriveApp.getFileById(id);
    var vignette = fichier.getThumbnail();
    var blob = vignette || fichier.getBlob();
    return "data:" + blob.getContentType() + ";base64," +
           Utilities.base64Encode(blob.getBytes());
  } catch (e) {
    return "";
  }
}

/** Photo en pleine résolution, pour l'affichage en grand. */
function apiPhoto(code, id) {
  verifierCode(code);
  try {
    var blob = DriveApp.getFileById(id).getBlob();
    return "data:" + blob.getContentType() + ";base64," +
           Utilities.base64Encode(blob.getBytes());
  } catch (e) {
    return "";
  }
}

function apiStatuts(code) {
  verifierCode(code);
  return STATUTS;
}

// =====================================================================
//  Journal des erreurs
// =====================================================================

function journaliserErreur(erreur, e) {
  try {
    var c = classeur();
    var f = c.getSheetByName("Erreurs") || c.insertSheet("Erreurs");
    if (f.getLastRow() === 0) {
      f.appendRow(["Date", "Message", "Detail"]);
      f.getRange(1, 1, 1, 3).setFontWeight("bold");
    }
    f.appendRow([
      new Date(),
      erreur && erreur.message ? erreur.message : String(erreur),
      e && e.postData ? String(e.postData.contents).slice(0, 800) : ""
    ]);
  } catch (ignore) {}
}

// =====================================================================
//  Vérification après installation — à lancer depuis l'éditeur
// =====================================================================

function testerInstallation() {
  var faux = {
    postData: {
      contents: JSON.stringify({
        jeton: REGLAGES.jeton,
        type: "Avis technique",
        objet: "Fissures et desordres structurels",
        nom: "Dupont",
        prenom: "Test",
        email: Session.getActiveUser().getEmail(),
        telephone: "06 00 00 00 00",
        ville: "Nice",
        description: "Demande de test creee depuis l'editeur Apps Script.",
        consentement: true,
        photos: []
      })
    }
  };
  Logger.log(doPost(faux).getContent());
  Logger.log("Espace de gestion : " + adresseEspace());
  Logger.log("Ouvrez cette adresse, saisissez le code d'acces, la demande de test doit apparaitre.");
}


// =====================================================================
//  Agenda de prise de rendez-vous
// =====================================================================
// Tout est calculé ici, sans service extérieur : les créneaux ouverts
// viennent des règles ci-dessous, on retire ceux déjà réservés par le site
// et, si un agenda Google est indiqué, ceux où le cabinet est déjà occupé.

var AGENDA = {
  // Jours travaillés : 1 = lundi ... 5 = vendredi
  jours: [1, 2, 3, 4, 5],

  // Plages d'ouverture, en heures pleines ou demies.
  // "fin" est l'heure a laquelle le dernier rendez-vous doit etre termine,
  // pas celle du dernier creneau : 13.5 laisse donc proposer 13h00, qui
  // s'acheve a 13h30. Pour arreter les rendez-vous a 12h00, mettre 12.5.
  plages: [
    { debut: 9.0, fin: 13.5 }
  ],

  // Durée d'un rendez-vous, en minutes, selon le format demandé
  durees: { telephone: 30, visio: 30 },

  // Pas entre deux créneaux proposés, en minutes
  pas: 60,

  // Délai de prévenance : aucun rendez-vous avant J+2
  delaiJours: 2,

  // Nombre de jours proposés à partir du premier créneau ouvert
  fenetreJours: 30,

  // Agenda où s'écrit le rendez-vous, selon l'activité demandée. Les deux
  // sont des agendas secondaires du compte qui héberge ce script ; ils ont
  // été créés pour que le CRM Groupe puisse lire chaque activité à part.
  // Laisser "" pour qu'une activité n'écrive nulle part.
  agendas: {
    expertise: "f0c504d0a5fb879a58221be8ba5dea096c06b14a894115b78e9b17e9123fe17b@group.calendar.google.com",
    amo: "eae5e6ec1c532c9c57343bea04c04589f4bb79940413b47966656d8d5b5b98c7@group.calendar.google.com"
  },

  // Agendas dont les événements bloquent un créneau sans jamais recevoir de
  // rendez-vous : l'agenda personnel du compte, typiquement, où se trouvent
  // aussi les rendez-vous pris avant la séparation en deux agendas.
  // Les deux agendas ci-dessus sont toujours consultés : inutile de les
  // répéter ici.
  agendasBloquants: ["primary"],

  // Organisateur affiché dans le rendez-vous joint à la fiche. C'est aussi
  // l'adresse à laquelle le cabinet répondra depuis son agenda.
  organisateur: "contact@btpexpertise.fr",

  // Couleur imposée à l'événement, par activité. Vide : chaque rendez-vous
  // prend alors la couleur de son agenda, réglée depuis Google Agenda —
  // c'est ce qu'on veut depuis que les deux activités ont chacune le sien.
  // Pour reprendre la main ici, écrire un nom de CalendarApp.EventColor :
  // PALE_BLUE, PALE_GREEN, MAUVE, PALE_RED, YELLOW, ORANGE, CYAN, GRAY,
  // BLUE, GREEN, RED.
  couleurs: { expertise: "", amo: "" },

  // Fuseau utilisé pour tous les calculs
  fuseau: "Europe/Paris",

  // Feuille où sont consignés les rendez-vous
  feuille: "Rendez-vous"
};

var COLONNES_RDV = [
  "Debut", "Fin", "Format", "Nom", "Prenom", "Email",
  "Telephone", "Ville", "Besoin", "Objet", "Description", "Statut", "Cle"
];

// Position des colonnes utilisées par la validation (1 = première colonne).
var COL_RDV = { debut: 1, fin: 2, format: 3, nom: 4, prenom: 5, email: 6,
                telephone: 7, statut: 12, cle: 13 };

var RDV_CONFIRME = "Confirmé";
var RDV_REFUSE = "Refusé";


function feuilleRdv() {
  var c = classeur();
  var f = c.getSheetByName(AGENDA.feuille);
  if (!f) {
    f = c.insertSheet(AGENDA.feuille);
    f.appendRow(COLONNES_RDV);
    f.getRange(1, 1, 1, COLONNES_RDV.length).setFontWeight("bold");
    f.setFrozenRows(1);
  }
  return f;
}


/**
 * Créneaux libres pour un format donné, à partir de J+2.
 * Renvoie [{ jour: "2026-09-05", libelle: "vendredi 5 septembre",
 *            heures: ["09:00", "09:30", ...] }, ...]
 */
function apiCreneaux(format) {
  var duree = AGENDA.durees[format] || AGENDA.durees.telephone;
  var maintenant = new Date();

  var depart = new Date(maintenant);
  depart.setDate(depart.getDate() + AGENDA.delaiJours);
  depart.setHours(0, 0, 0, 0);

  var fin = new Date(depart);
  fin.setDate(fin.getDate() + AGENDA.fenetreJours);

  var occupes = creneauxOccupes(depart, fin);
  var jours = [];

  for (var d = new Date(depart); d < fin; d.setDate(d.getDate() + 1)) {
    if (AGENDA.jours.indexOf(d.getDay()) === -1) continue;

    var heures = [];
    for (var p = 0; p < AGENDA.plages.length; p++) {
      var plage = AGENDA.plages[p];
      for (var h = plage.debut; h + duree / 60 <= plage.fin + 0.001; h += AGENDA.pas / 60) {
        var debut = new Date(d);
        debut.setHours(Math.floor(h), Math.round((h % 1) * 60), 0, 0);
        var termine = new Date(debut.getTime() + duree * 60000);

        if (debut <= maintenant) continue;
        if (chevauche(debut, termine, occupes)) continue;

        heures.push(Utilities.formatDate(debut, AGENDA.fuseau, "HH:mm"));
      }
    }

    if (heures.length) {
      jours.push({
        jour: Utilities.formatDate(d, AGENDA.fuseau, "yyyy-MM-dd"),
        libelle: libelleJour(d),
        heures: heures
      });
    }
  }

  return { success: true, duree: duree, jours: jours };
}


/** Périodes déjà occupées : rendez-vous du site et événements de l'agenda. */
function creneauxOccupes(depart, fin) {
  var occupes = [];

  var f = feuilleRdv();
  if (f.getLastRow() > 1) {
    // On lit jusqu'au statut : un rendez-vous refusé libère son créneau, un
    // rendez-vous en attente de validation le garde réservé.
    var valeurs = f.getRange(2, 1, f.getLastRow() - 1, COL_RDV.statut).getValues();
    for (var i = 0; i < valeurs.length; i++) {
      var d = valeurs[i][0], t = valeurs[i][1];
      var statut = valeurs[i][COL_RDV.statut - 1];
      if (statut === RDV_REFUSE) continue;
      if (d instanceof Date && t instanceof Date) {
        occupes.push({ debut: d, fin: t });
      }
    }
  }

  // Les deux agendas du site, plus ceux qui bloquent sans rien recevoir :
  // un rendez-vous d'expertise doit fermer le créneau à une demande d'AMO,
  // et l'inverse. Sinon deux personnes réserveraient la même heure.
  var agendas = agendasConsultes();
  for (var a = 0; a < agendas.length; a++) {
    try {
      var cal = ouvrirAgenda(agendas[a]);
      if (!cal) continue;
      var evts = cal.getEvents(depart, fin);
      for (var j = 0; j < evts.length; j++) {
        if (evts[j].isAllDayEvent()) {
          occupes.push({ debut: evts[j].getAllDayStartDate(),
                         fin: evts[j].getAllDayEndDate() });
        } else {
          occupes.push({ debut: evts[j].getStartTime(), fin: evts[j].getEndTime() });
        }
      }
    } catch (erreur) {
      // Agenda inaccessible : on continue avec les autres. Mieux vaut un
      // créneau proposé en trop qu'un agenda entier ignoré en silence.
      journaliserErreur(erreur, { agenda: agendas[a] });
    }
  }

  return occupes;
}


function chevauche(debut, fin, periodes) {
  for (var i = 0; i < periodes.length; i++) {
    if (debut < periodes[i].fin && fin > periodes[i].debut) return true;
  }
  return false;
}


var JOURS_FR = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];
var MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
               "août", "septembre", "octobre", "novembre", "décembre"];

function libelleJour(d) {
  return JOURS_FR[d.getDay()] + " " + d.getDate() + " " + MOIS_FR[d.getMonth()];
}


/**
 * Enregistre un rendez-vous. Vérifie une dernière fois que le créneau est
 * libre : entre l'affichage et la validation, quelqu'un a pu le prendre.
 */
function enLigne(format) { return format === "visio"; }


/**
 * Vrai lorsque la demande relève de l'Assistance à Maîtrise d'Ouvrage.
 *
 * On cherche un fragment du libellé plutôt que l'égalité stricte : le texte
 * exact vient du site, où il peut être reformulé sans que ce fichier bouge.
 */
function estAmo(donnees) {
  return nettoyer(donnees && donnees.besoin).indexOf("Ma\u00eetrise d\u2019Ouvrage") !== -1;
}


/** Intitulé court de l'activité, pour les titres de rendez-vous. */
function activite(donnees) {
  return estAmo(donnees) ? "AMO" : "Expertise";
}


function apiReserver(donnees) {
  var format = donnees.format === "visio" ? "visio" : "telephone";
  var duree = AGENDA.durees[format];

  var debut = new Date(donnees.debut);
  if (isNaN(debut.getTime())) {
    return { success: false, message: "Créneau invalide" };
  }
  var fin = new Date(debut.getTime() + duree * 60000);

  var limite = new Date();
  limite.setDate(limite.getDate() + AGENDA.delaiJours);
  limite.setHours(0, 0, 0, 0);
  if (debut < limite) {
    return { success: false, message: "Ce créneau est trop proche" };
  }

  var cle = "";
  var verrou = LockService.getScriptLock();
  try {
    verrou.waitLock(10000);
  } catch (e) {
    return { success: false, message: "Réessayez dans quelques secondes" };
  }

  try {
    var large = new Date(debut); large.setHours(0, 0, 0, 0);
    var largeFin = new Date(debut); largeFin.setHours(23, 59, 59, 0);
    if (chevauche(debut, fin, creneauxOccupes(large, largeFin))) {
      return { success: false, message: "Ce créneau vient d'être pris" };
    }

    cle = Utilities.getUuid();
    feuilleRdv().appendRow([
      debut, fin, format,
      nettoyer(donnees.nom), nettoyer(donnees.prenom), nettoyer(donnees.email),
      nettoyer(donnees.telephone), nettoyer(donnees.ville),
      nettoyer(donnees.besoin), nettoyer(donnees.objet),
      nettoyer(donnees.description), RDV_CONFIRME, cle
    ]);

  } finally {
    verrou.releaseLock();
  }

  var champs = {
    type: "Rendez-vous " + (format === "visio" ? "visio" : "téléphonique"),
    objet: nettoyer(donnees.objet),
    nom: nettoyer(donnees.nom),
    prenom: nettoyer(donnees.prenom),
    email: nettoyer(donnees.email),
    telephone: nettoyer(donnees.telephone),
    ville: nettoyer(donnees.ville),
    description: [
      "RENDEZ-VOUS : " + libelleJour(debut) + " à " +
        Utilities.formatDate(debut, AGENDA.fuseau, "HH'h'mm"),
      "Format : " + (format === "visio" ? "Visioconférence" : "Échange téléphonique"),
      "Besoin : " + nettoyer(donnees.besoin),
      "Type de bien : " + nettoyer(donnees.typeBien),
      "", nettoyer(donnees.description)
    ].join("\n"),
    consentement: donnees.consentement ? "Oui" : "Non"
  };

  var photos = enregistrerPhotos(donnees.photos, champs);
  enregistrerLigne(champs, photos);

  // Rien n'entre dans l'agenda avant que le cabinet ait dit oui : la fiche
  // porte les deux boutons, et c'est la réponse qui décide.
  // Le rendez-vous entre dans l'agenda du script, et la fiche emporte le
  // fichier d'agenda : Outlook le range seul si l'acceptation automatique est
  // activée. Aucun message supplémentaire, aucun clic.
  creerEvenementDepuisDemande(donnees, debut, fin, format);
  envoyerAuCabinet(champs, photos, donnees,
                   inviteRendezVous(donnees, champs, debut, fin, format,
                                    "PUBLISH"), cle);

  if (REGLAGES.accuseReception) {
    envoyerConfirmationRdv(donnees, champs, debut, format, photos);
  }

  // Le CRM en dernier : une panne de son côté ne doit jamais empêcher un
  // rendez-vous d'être pris, ni les courriels de partir.
  inscrireAuCrm(donnees, debut, format);

  return {
    success: true,
    quand: libelleJour(debut) + " à " +
           Utilities.formatDate(debut, AGENDA.fuseau, "HH'h'mm")
  };
}


/**
 * Crée le rendez-vous dans l'agenda et invite la boîte du cabinet.
 *
 * La description reprend l'intégralité de la demande, liens vers les fichiers
 * compris : l'invitation se suffit à elle-même, et remplace le courriel de
 * notification. Renvoie true si l'invitation est bien partie.
 */
/**
 * Le rendez-vous au format iCalendar, à joindre à la fiche du cabinet.
 *
 * Apps Script ne sait écrire que dans un agenda Google. Plutôt qu'une
 * invitation envoyée à part — un second message pour le même rendez-vous — le
 * rendez-vous voyage dans la fiche : Outlook le reconnaît et le range dans
 * l'agenda, automatiquement si l'acceptation automatique est activée.
 */
/**
 * Lien « Ajouter à Google Agenda », pour le courriel du demandeur.
 *
 * Ouvre un agenda pré-rempli dans son navigateur : il n'a qu'à enregistrer.
 * Le fichier joint au même message couvre les autres agendas.
 */
function lienGoogleAgenda(titre, debut, fin, details, lieu) {
  var utc = function (d) {
    return Utilities.formatDate(d, "UTC", "yyyyMMdd'T'HHmmss'Z'");
  };
  return "https://calendar.google.com/calendar/render?action=TEMPLATE" +
         "&text=" + encodeURIComponent(titre) +
         "&dates=" + utc(debut) + "/" + utc(fin) +
         "&details=" + encodeURIComponent(details) +
         "&location=" + encodeURIComponent(lieu);
}


function inviteRendezVous(donnees, champs, debut, fin, format, methode) {
  // REQUEST : une invitation, qu'Outlook range dans l'agenda du cabinet.
  // PUBLISH : un simple rendez-vous à ajouter, sans réponse attendue — c'est
  // ce qu'on envoie au demandeur, à qui l'on ne demande pas de confirmer.
  methode = methode || "PUBLISH";
  // Heure locale plutot qu'heure universelle : Outlook affichait 07h00 pour un
  // rendez-vous de 09h00, faute de convertir. On ecrit donc l'heure telle
  // qu'elle doit apparaitre, accompagnee de la definition du fuseau ci-dessous,
  // qui leve toute ambiguite quel que soit le logiciel d'agenda.
  var local = function (d) {
    return Utilities.formatDate(d, AGENDA.fuseau, "yyyyMMdd'T'HHmmss");
  };
  var utc = function (d) {
    return Utilities.formatDate(d, "UTC", "yyyyMMdd'T'HHmmss'Z'");
  };
  // Les virgules, points-virgules et retours à la ligne ont un sens dans le
  // format : ils doivent être neutralisés.
  var texte = function (v) {
    return String(v || "")
      .replace(/\\/g, "\\\\")
      .replace(/;/g, "\\;")
      .replace(/,/g, "\\,")
      .replace(/\r?\n/g, "\\n");
  };

  var detail = [
    (enLigne(format) ? "Visioconférence" : "Échange téléphonique") +
      " — " + AGENDA.durees[format] + " minutes",
    "",
    "Besoin : " + nettoyer(donnees.besoin),
    "Demande : " + nettoyer(donnees.objet),
    "Type de bien : " + nettoyer(donnees.typeBien),
    "Ville du bien : " + nettoyer(donnees.ville),
    "",
    "Téléphone : " + nettoyer(donnees.telephone),
    "E-mail : " + nettoyer(donnees.email),
    "",
    nettoyer(donnees.description),
    "",
    "Le dossier : " + adresseEspace()
  ].join("\n");

  var titre = titreRendezVous(donnees, format);

  var lignes = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//BTP Expertise//Prise de rendez-vous//FR",
    "CALSCALE:GREGORIAN",
    "METHOD:" + methode,
    "BEGIN:VTIMEZONE",
    "TZID:Europe/Paris",
    "BEGIN:DAYLIGHT",
    "TZOFFSETFROM:+0100",
    "TZOFFSETTO:+0200",
    "TZNAME:CEST",
    "DTSTART:19700329T020000",
    "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU",
    "END:DAYLIGHT",
    "BEGIN:STANDARD",
    "TZOFFSETFROM:+0200",
    "TZOFFSETTO:+0100",
    "TZNAME:CET",
    "DTSTART:19701025T030000",
    "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU",
    "END:STANDARD",
    "END:VTIMEZONE",
    "BEGIN:VEVENT",
    "UID:" + utc(debut) + "-" + Utilities.getUuid() + "@btpexpertise.fr",
    "DTSTAMP:" + utc(new Date()),
    "DTSTART;TZID=Europe/Paris:" + local(debut),
    "DTEND;TZID=Europe/Paris:" + local(fin),
    "SUMMARY:" + texte(titre),
    "DESCRIPTION:" + texte(detail),
    "LOCATION:" + texte(enLigne(format) ? "Visioconférence" : "Par téléphone"),
    // Ni organisateur ni participants : ce fichier n'invite personne, il
    // propose un rendez-vous à ajouter. Les mentionner faisait afficher à
    // Outlook « vous vous êtes invité vous-même ».
    "STATUS:CONFIRMED",
    "SEQUENCE:0",
    "BEGIN:VALARM",
    "TRIGGER:-PT30M",
    "ACTION:DISPLAY",
    "DESCRIPTION:" + texte(titre),
    "END:VALARM",
    "END:VEVENT",
    "END:VCALENDAR"
  ];

  // Le type annoncé doit suivre la méthode : laisser REQUEST ici ferait
  // réapparaître le bandeau de demande de réunion, alors que le contenu
  // n'est qu'un rendez-vous à ajouter.
  return Utilities.newBlob(lignes.join("\r\n"),
                           "text/calendar; charset=UTF-8; method=" + methode,
                           "rendez-vous.ics");
}

/**
 * Les pièces qui rendent le premier échange utile.
 *
 * On ne demande rien AVANT le rendez-vous : reunir des pieces par courriel
 * avant meme le premier echange decourage, et personne ne les lira d'ici la.
 * Le demandeur les rassemble simplement pour l'entretien.
 *
 * La liste n'est pas une exigence : beaucoup de demandeurs n'ont qu'une photo,
 * et se croiraient hors sujet s'ils pensaient devoir tout fournir. La phrase
 * qui suit la liste compte donc autant que la liste elle-même.
 */
function documentsUtiles() {
  var pieces = [
    "photographies",
    "devis ou factures",
    "plans",
    "diagnostics",
    "échanges avec une entreprise ou un autre intervenant",
    "procès-verbal de réception",
    "rapport ou constat déjà réalisé",
    "tout autre document éclairant votre situation"
  ];

  var items = "";
  for (var i = 0; i < pieces.length; i++) {
    items += '<li style="margin:0 0 5px">' + pieces[i] + '</li>';
  }

  return '' +
    '<div style="margin:22px 0 0;padding:18px 20px;border-radius:10px;' +
        'background:#FFFFFF;border:1px solid ' + MAIL.bordure + '">' +
      '<div style="font-size:15px;font-weight:700;margin:0 0 8px">' +
        'Pour préparer notre échange</div>' +
      '<p style="margin:0 0 10px;font-size:14px">Si vous disposez déjà de documents ' +
        'utiles, rassemblez-les pour notre rendez-vous :</p>' +
      '<ul style="margin:0 0 12px;padding-left:20px;font-size:14px;line-height:1.6">' +
        items +
      '</ul>' +
      '<p style="margin:0;font-size:14px;color:' + MAIL.gris + '">' +
        'Vous n\u2019avez pas besoin de tous ces éléments : ayez simplement ' +
        'sous la main ceux que vous possédez déjà.</p>' +
    '</div>';
}


function envoyerConfirmationRdv(donnees, champs, debut, format, photos) {
  var quand = libelleJour(debut) + " \u00e0 " +
              Utilities.formatDate(debut, AGENDA.fuseau, "HH'h'mm");
  var duree = AGENDA.durees[format];
  var enVisio = format === "visio";

  var recap = blocRecap([
    ligneRecap("Votre besoin", echapper(nettoyer(donnees.besoin))),
    ligneRecap("Votre demande", echapper(nettoyer(donnees.objet))),
    ligneRecap("Type de bien", echapper(nettoyer(donnees.typeBien))),
    ligneRecap("Ville du bien", echapper(champs.ville)),
    ligneRecap("T\u00e9l\u00e9phone", echapper(champs.telephone)),
    ligneRecap("Documents joints",
               photos && photos.length
                 ? String(photos.length) + (photos.length > 1 ? " fichiers" : " fichier")
                 : "")
  ], echapper(nettoyer(donnees.description)));

  var contenu =
    "<p style=\"margin:0 0 18px\">Bonjour " + echapper(nomComplet(champs)) + ",</p>" +
    "<p style=\"margin:0 0 18px\">Votre demande auprès de BTP Expertise a bien " +
      "été enregistrée, et votre rendez-vous est confirmé. " +
      "Voici les informations utiles :</p>" +

    '<div style="margin:0 0 4px;padding:18px 20px;border-radius:10px;' +
        'background:' + MAIL.grisFond + ';border-left:4px solid ' + MAIL.orange + '">' +
      '<div style="font-size:18px;font-weight:700;line-height:1.35">' +
        echapper(quand) + "</div>" +
      '<div style="margin-top:6px;font-size:14px;color:' + MAIL.gris + '">' +
        (enVisio ? "Visioconf\u00e9rence" : "\u00c9change t\u00e9l\u00e9phonique") +
        " \u00b7 " + duree + " minutes</div>" +
      '<div style="margin-top:10px;font-size:14px">' +
        (enVisio
          ? "Le lien de connexion vous sera transmis avant l\u2019entretien."
          : "Nous vous appelons au <strong>" + echapper(champs.telephone) +
            "</strong>.") +
      "</div>" +
    "</div>" +

    "<p style=\"margin:22px 0 0\">Ce premier échange nous permettra de comprendre " +
      "votre situation, de reprendre avec vous les éléments importants de votre " +
      "demande et de déterminer la mission la plus adaptée.</p>" +

    recap +

    documentsUtiles() +

    '<div style="margin:26px 0 4px;text-align:center">' +
      '<a href="' + lienGoogleAgenda(
          "Rendez-vous BTP Expertise",
          debut, new Date(debut.getTime() + duree * 60000),
          (enVisio ? "Visioconf\u00e9rence" : "\u00c9change t\u00e9l\u00e9phonique") +
            " avec BTP Expertise, " + duree + " minutes." +
            (enVisio ? "" : " Nous vous appelons au " + champs.telephone + ".") +
            " Une question : " + REGLAGES.telephone + ".",
          enVisio ? "Visioconf\u00e9rence" : "Par t\u00e9l\u00e9phone") + '" ' +
         'style="display:inline-block;background:' + MAIL.bleu + ';color:#FFFFFF;' +
         'padding:13px 28px;border-radius:8px;text-decoration:none;' +
         'font-weight:700;font-size:14px">Ajouter \u00e0 Google Agenda</a>' +
      '<div style="margin-top:10px;font-size:12px;color:' + MAIL.gris + '">' +
        'Vous utilisez un autre agenda\u00a0? Le rendez-vous est aussi joint ' +
        '\u00e0 ce message.</div>' +
    '</div>' +

    "<p style=\"margin:24px 0 0\">Pour d\u00e9caler ou annuler ce rendez-vous, " +
      "r\u00e9pondez simplement \u00e0 ce message ou appelez-nous au " +
      "<strong>" + echapper(REGLAGES.telephone) + "</strong>.</p>";

  envoyerMail({
    to: champs.email,
    subject: "Votre rendez-vous du " + quand + " \u2014 BTP Expertise",
    htmlBody: gabaritMail("Votre rendez-vous est confirm\u00e9", contenu),
    name: REGLAGES.nomExpediteur,
    // PUBLISH et non REQUEST : on ne lui demande pas de répondre, le
    // rendez-vous est déjà confirmé.
    attachments: [inviteRendezVous(donnees, champs, debut,
                                   new Date(debut.getTime() + duree * 60000),
                                   format, "PUBLISH")]
  });
}


// Marqueur des rendez-vous d'essai créés par testerCouleurs(). Il sert aussi
// à les retrouver pour les effacer : ne pas le changer d'un côté seulement.
var ESSAI_COULEUR = "ESSAI COULEUR";


/**
 * Pose deux rendez-vous d'essai, un par activité, pour voir les couleurs.
 *
 * N'envoie aucun courriel et n'écrit ni dans le classeur ni dans le CRM :
 * seuls deux événements apparaissent dans l'agenda, dans deux mois, à une
 * heure où rien d'autre n'est prévu. Ils s'effacent avec supprimerCouleurs().
 */
function testerCouleurs() {
  if (!agendasDuSite().length) {
    Logger.log("Aucun agenda relié (AGENDA.agendas est vide).");
    return;
  }

  var quand = new Date();
  quand.setDate(quand.getDate() + 60);
  quand.setHours(9, 0, 0, 0);

  var essais = [
    { besoin: "Expertise bâtiment", objet: "Fissures" },
    { besoin: "Assistance à Maîtrise d\u2019Ouvrage", objet: "Suivi de chantier" }
  ];

  Logger.log("Les rendez-vous d'essai sont poses le %s %s.",
             libelleJour(quand), String(quand.getFullYear()));
  Logger.log("");

  for (var i = 0; i < essais.length; i++) {
    var debut = new Date(quand.getTime() + i * 60 * 60000);
    var donnees = {
      prenom: ESSAI_COULEUR, nom: "A SUPPRIMER",
      email: "essai@btpexpertise.fr", telephone: "0600000000",
      ville: "Nice", typeBien: "Villa",
      besoin: essais[i].besoin, objet: essais[i].objet,
      description: "Rendez-vous d'essai créé par testerCouleurs()."
    };

    // On ouvre l'agenda ici, en plus de l'ecriture, pour pouvoir dire son
    // nom : « rien dans l'agenda » vient presque toujours de ce qu'on
    // regarde ailleurs que la ou le script a ecrit.
    var identifiant = agendaDeLActivite(donnees);
    var cal = ouvrirAgenda(identifiant);
    var ou = cal ? cal.getName() : "INACCESSIBLE";

    var pose = creerEvenementDepuisDemande(
      donnees, debut, new Date(debut.getTime() + 30 * 60000), "telephone");

    Logger.log("%s  %s  %s",
               pose ? "OK   " : "ECHEC",
               Utilities.formatDate(debut, AGENDA.fuseau, "dd/MM HH'h'mm"),
               titreRendezVous(donnees, "telephone"));
    Logger.log("       agenda : %s", ou);
    if (!cal) {
      Logger.log("       identifiant : %s", identifiant || "(vide)");
      Logger.log("       Le compte du script n'y a pas acces, ou l'identifiant est faux.");
    }
    Logger.log("");
  }

  Logger.log("Couleurs : %s", decrireCouleurs());
  Logger.log("Dans Google Agenda, cochez les deux agendas dans la colonne de");
  Logger.log("gauche, allez a la date ci-dessus, puis lancez supprimerCouleurs().");
}


/** Ce que le journal doit annoncer au sujet des couleurs. */
function decrireCouleurs() {
  var e = AGENDA.couleurs.expertise, a = AGENDA.couleurs.amo;
  if (!e && !a) return "celle de chaque agenda (AGENDA.couleurs est vide)";
  return (e || "celle de l'agenda") + " pour l'expertise, " +
         (a || "celle de l'agenda") + " pour l'AMO";
}


/** Efface les rendez-vous d'essai laissés par testerCouleurs(). */
function supprimerCouleurs() {
  // Fenêtre large autour de la date d'essai : un décalage de quelques jours
  // ne doit pas laisser un rendez-vous d'essai derrière lui.
  var depuis = new Date();
  var jusqua = new Date();
  jusqua.setDate(jusqua.getDate() + 120);

  var agendas = agendasDuSite();
  var effaces = 0;

  // Chaque agenda dans son propre filet : une erreur sur le second ne doit
  // pas passer pour un travail termine parce que le premier a reussi.
  for (var a = 0; a < agendas.length; a++) {
    var nom = agendas[a];
    try {
      var cal = ouvrirAgenda(nom);
      if (!cal) {
        Logger.log("ECHEC  agenda inaccessible : %s", nom);
        continue;
      }
      nom = cal.getName();
      var evenements = cal.getEvents(depuis, jusqua);
      var ici = 0;
      for (var i = 0; i < evenements.length; i++) {
        if (evenements[i].getTitle().indexOf(ESSAI_COULEUR) !== -1) {
          Logger.log("   supprime  %s", evenements[i].getTitle());
          evenements[i].deleteEvent();
          ici++;
          effaces++;
        }
      }
      Logger.log("%s : %s evenement(s) lus, %s supprime(s).",
                 nom, String(evenements.length), String(ici));
    } catch (erreur) {
      Logger.log("ECHEC  %s : %s", nom, erreur.message);
      Logger.log("       Les autres agendas sont quand meme traites.");
      journaliserErreur(erreur, { agenda: nom });
    }
    Logger.log("");
  }

  Logger.log("%s rendez-vous d'essai supprime(s) en tout.", String(effaces));
  if (!effaces) {
    Logger.log("Aucun trouve : soit ils sont deja partis et l'affichage de");
    Logger.log("Google Agenda retarde, soit ils sont hors de la fenetre de");
    Logger.log("120 jours balayee a partir d'aujourd'hui.");
  }
}


/**
 * Vérification de l'agenda, à lancer depuis l'éditeur après un déploiement.
 * Affiche les premiers créneaux proposés dans le journal d'exécution.
 */
function testerAgenda() {
  // 1. L'agenda Google repond-il ? Un echec d'autorisation est silencieux
  //    en production : on le rend visible ici.
  var compte = "";
  try { compte = Session.getEffectiveUser().getEmail(); } catch (e) { compte = "(inconnu)"; }
  Logger.log("Compte du script : %s", compte || "(inconnu)");
  Logger.log("Les agendas ci-dessous doivent lui appartenir ou lui etre partages.");
  Logger.log("");

  var consultes = agendasConsultes();
  if (consultes.length) {
    var jusqua = new Date();
    jusqua.setDate(jusqua.getDate() + AGENDA.fenetreJours);
    for (var a = 0; a < consultes.length; a++) {
      var role = agendasDuSite().indexOf(consultes[a]) === -1
        ? "bloque seulement" : "recoit les rendez-vous";
      var cal = ouvrirAgenda(consultes[a]);
      if (cal) {
        Logger.log("OK     %s %s evenements sur %s jours  [%s]",
                   pad(cal.getName(), 26),
                   String(cal.getEvents(new Date(), jusqua).length),
                   String(AGENDA.fenetreJours), role);
      } else {
        Logger.log("ECHEC  agenda introuvable ou inaccessible  [%s]", role);
        Logger.log("       %s", consultes[a]);
        Logger.log("       Verifiez l'identifiant, et que le compte du script y a acces.");
      }
    }
  } else {
    Logger.log("Aucun agenda relie : seuls les rendez-vous du site bloquent.");
  }
  Logger.log("");

  var resultat = apiCreneaux("telephone");
  if (!resultat.jours.length) {
    Logger.log("Aucun créneau disponible dans les %s prochains jours.", AGENDA.fenetreJours);
    Logger.log("Vérifiez les réglages AGENDA (jours, plages) ou votre agenda.");
    return;
  }

  Logger.log("Rendez-vous téléphonique de %s minutes", resultat.duree);
  Logger.log("%s jours proposés, à partir du %s",
             resultat.jours.length, resultat.jours[0].libelle);
  Logger.log("");
  for (var i = 0; i < Math.min(5, resultat.jours.length); i++) {
    var j = resultat.jours[i];
    Logger.log("%s : %s", j.libelle, j.heures.join("  "));
  }

  var visio = apiCreneaux("visio");
  Logger.log("");
  Logger.log("En visio (%s minutes) : %s jours proposés",
             visio.duree, visio.jours.length);
}


// =====================================================================
//  Rappel mensuel : l'article de conseils
// =====================================================================
// Envoyé par les serveurs de Google, indépendamment de l'ordinateur du
// cabinet : le rappel arrive même si personne n'ouvre son poste ce jour-là.
// À installer une fois avec installerRappelMensuel().

var RAPPEL = {
  // Jour et heure d'envoi
  jour: 1,
  heure: 9,

  // Destinataire du rappel. Volontairement distinct des demandes : c'est un
  // rappel de travail, pas un message client.
  destinataire: "contact.btpexpertiseriviera@gmail.com"
};


function rappelArticleMensuel() {
  var mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
              "août", "septembre", "octobre", "novembre", "décembre"];
  var maintenant = new Date();
  var nomMois = mois[maintenant.getMonth()];

  var corps =
    '<div style="font-family:Helvetica,Arial,sans-serif;font-size:15px;color:#262C42;max-width:620px">' +
      '<h2 style="color:#FF8A00;margin:0 0 6px">L’article de ' + nomMois + '</h2>' +
      '<p style="color:#6B7186;margin:0 0 22px">Rappel automatique du ' +
        Utilities.formatDate(maintenant, "Europe/Paris", "d MMMM yyyy") + "</p>" +

      "<p>C’est le moment de publier l’article de conseils du mois sur " +
      '<a href="https://btpexpertise.fr/conseils/">btpexpertise.fr</a>. ' +
      "Un article par mois entretient le référencement local et donne des raisons " +
      "de revenir sur le site.</p>" +

      '<p style="background:#F4F4F4;padding:16px 20px;border-radius:8px;line-height:1.7">' +
        "<strong>La marche à suivre</strong><br>" +
        "1. Ouvrir le dossier <code>BTP-Expertise\\articles</code> : le brouillon " +
        "du mois y est déposé, daté du " +
        Utilities.formatDate(maintenant, "Europe/Paris", "d MMMM") + ".<br>" +
        "2. Le relire, et le faire valider par Mickael.<br>" +
        "3. Supprimer la ligne <code>\"brouillon\": True,</code> en haut du fichier.<br>" +
        "4. Publier avec <code>python build.py</code> puis <code>python publier.py</code>." +
      "</p>" +

      '<p style="font-size:14px;color:#6B7186">Tant que la ligne <code>brouillon</code> ' +
      "est là, l’article n’existe pas sur le site : rien ne part sans relecture. " +
      "Le mode d’emploi complet est dans <code>articles\\A-LIRE.md</code>.</p>" +

      '<p style="font-size:14px;color:#6B7186">Quelques sujets qui marchent bien selon ' +
      "la saison : sécheresse et fissures en été, infiltrations et étanchéité après les " +
      "pluies d’automne, réception de chantier au printemps, et à tout moment les " +
      "évolutions de réglementation ou les arrêtés de catastrophe naturelle dans le 06 " +
      "et le 83.</p>" +

      '<p style="color:#6B7186;font-size:13px;margin-top:26px;padding-top:16px;' +
        'border-top:1px solid #E3E7ED">Rappel envoyé automatiquement par l’espace de ' +
        "gestion BTP Expertise. Pour l’arrêter, lancer <code>retirerRappelMensuel</code> " +
        "depuis l’éditeur du script.</p>" +
    "</div>";

  envoyerMail({
    to: RAPPEL.destinataire,
    subject: "Article de " + nomMois + " — à préparer et publier",
    htmlBody: corps,
    name: REGLAGES.nomExpediteur
  });

  Logger.log("Rappel envoyé à %s", RAPPEL.destinataire);
}


/**
 * Installe le rappel mensuel. À lancer une seule fois depuis l'éditeur.
 * Les anciens déclencheurs sont retirés d'abord, pour ne pas recevoir
 * plusieurs rappels si la fonction est relancée.
 */
function installerRappelMensuel() {
  retirerRappelMensuel();

  ScriptApp.newTrigger("rappelArticleMensuel")
    .timeBased()
    .onMonthDay(RAPPEL.jour)
    .atHour(RAPPEL.heure)
    .create();

  Logger.log("Rappel installé : le %s de chaque mois vers %sh, vers %s",
             String(RAPPEL.jour), String(RAPPEL.heure), RAPPEL.destinataire);
  Logger.log("Pour vérifier tout de suite : lancer rappelArticleMensuel.");
}


function retirerRappelMensuel() {
  var declencheurs = ScriptApp.getProjectTriggers();
  var retires = 0;
  for (var i = 0; i < declencheurs.length; i++) {
    if (declencheurs[i].getHandlerFunction() === "rappelArticleMensuel") {
      ScriptApp.deleteTrigger(declencheurs[i]);
      retires++;
    }
  }
  if (retires) Logger.log("%s ancien(s) rappel(s) retiré(s)", retires);
  return retires;
}


