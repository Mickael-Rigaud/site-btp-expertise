/* BTP Expertise - comportements du site */
(function () {
  "use strict";

  /* --- Menu mobile --- */
  var burger = document.querySelector(".burger");
  var nav = document.getElementById("navigation");
  if (burger && nav) {
    burger.addEventListener("click", function () {
      var ouvert = nav.getAttribute("data-ouvert") === "true";
      nav.setAttribute("data-ouvert", ouvert ? "false" : "true");
      burger.setAttribute("aria-expanded", ouvert ? "false" : "true");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        nav.setAttribute("data-ouvert", "false");
        burger.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* --- Ombre de l'en-tete au defilement --- */
  var entete = document.querySelector(".entete");
  if (entete) {
    var majEntete = function () {
      entete.classList.toggle("entete--defile", window.scrollY > 8);
    };
    majEntete();
    window.addEventListener("scroll", majEntete, { passive: true });
  }

  /* --- Apparition au defilement des blocs marques data-anim --- */
  var animables = [].slice.call(document.querySelectorAll("[data-anim]"));
  if (animables.length &&
      "IntersectionObserver" in window &&
      !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    /* L'attribut n'est pose que si le script tourne : sans JavaScript,
       les blocs restent visibles. */
    document.documentElement.setAttribute("data-anim-actif", "");
    var vigie = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (entree) {
        if (!entree.isIntersecting) return;
        entree.target.classList.add("visible");
        vigie.unobserve(entree.target);
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -80px 0px" });
    animables.forEach(function (el) { vigie.observe(el); });
  }

  /* ---- Boutons d'appel sur ordinateur et tablette ----
     Sur un telephone, "tel:" lance l'appel. Ailleurs il n'aboutit a rien
     d'utile : le premier clic affiche donc le numero au lieu de suivre le
     lien. Le lien reste un "tel:", donc un second clic fonctionne encore si
     un logiciel de telephonie est installe. */
  var surTelephone = window.matchMedia("(pointer: coarse) and (max-width: 820px)").matches;
  if (!surTelephone) {
    var lisible = function (href) {
      var chiffres = (href || "").replace(/[^0-9+]/g, "").replace(/^\+33/, "0");
      return chiffres.length === 10
        ? chiffres.replace(/(\d\d)(?=\d)/g, "$1 ").trim()
        : chiffres;
    };

    [].slice.call(document.querySelectorAll('a[href^="tel:"]')).forEach(function (lien) {
      // Les liens qui montrent deja le numero (mentions legales) sont laisses tels quels.
      if (/\d/.test(lien.textContent)) return;

      var numero = lisible(lien.getAttribute("href"));
      if (!numero) return;

      lien.addEventListener("click", function (e) {
        if (lien.classList.contains("est-devoile")) return;   // 2e clic : on laisse passer
        e.preventDefault();
        lien.classList.add("est-devoile");
        lien.setAttribute("aria-label", "Appeler le " + numero);
        var texte = lien.querySelector(".bouton__texte");
        if (texte) { texte.textContent = numero; }
        else { lien.textContent = numero; }
      });
    });
  }

  /* ---- Panneau de confirmation ----
     Une ligne de texte se remarque mal apres un formulaire : on remplace le
     formulaire par un panneau qui dit ce qui vient de se passer, et surtout
     ce qui va suivre. */
  var echapperHtml = function (t) {
    return String(t == null ? "" : t)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  };

  var afficherConfirmation = function (cible, titre, vedette, suites) {
    /* Le conteneur est en display:none tant qu'il ne porte pas de classe
       d'etat : sans cette ligne, le panneau existe mais reste invisible. */
    cible.className = "formulaire__message formulaire__message--panneau";
    cible.innerHTML =
      '<div class="confirmation" role="status" tabindex="-1">' +
        '<span class="confirmation__coche" aria-hidden="true">' +
          '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" ' +
               'stroke="currentColor" stroke-width="3" stroke-linecap="round" ' +
               'stroke-linejoin="round"><path d="M4 12.5l5.5 5.5L20 7"/></svg>' +
        '</span>' +
        '<h3 class="confirmation__titre">' + echapperHtml(titre) + '</h3>' +
        (vedette ? '<p class="confirmation__vedette">' + echapperHtml(vedette) + '</p>' : "") +
        '<ul class="confirmation__suite">' +
          suites.map(function (t) { return "<li>" + t + "</li>"; }).join("") +
        '</ul>' +
      '</div>';
    cible.hidden = false;
    var panneau = cible.querySelector(".confirmation");
    if (panneau) {
      panneau.focus({ preventScroll: true });
      panneau.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  };

  /* ---- Prise de rendez-vous en deux etapes ----
     1. le projet ; 2. le format, le creneau et les coordonnees.
     Les creneaux libres sont calcules par le back-office (script Google) a
     partir des horaires du cabinet, des rendez-vous deja pris et de l'agenda
     du cabinet. La reservation s'y inscrit directement. Aucun service tiers. */
  var rdv = document.getElementById("form-rdv");
  if (rdv) {
    var etapes = [].slice.call(rdv.querySelectorAll(".etape"));
    var jalons = [].slice.call(document.querySelectorAll(".jalon"));
    var msg = document.getElementById("rdv-message");
    var recap = document.getElementById("rdv-recap");
    var courante = 1;

    var dire = function (texte, ok) {
      if (!msg) return;
      msg.textContent = texte;
      msg.className = "formulaire__message formulaire__message--" + (ok ? "ok" : "ko");
      msg.scrollIntoView({ behavior: "smooth", block: "center" });
    };

    var val = function (id) {
      var el = document.getElementById(id);
      return el ? el.value.trim() : "";
    };

    /* Delai de prevenance : pas de rendez-vous avant J+2. La borne est calculee
       au chargement et non a la generation du site, sinon elle serait perimee
       des le lendemain. Date locale : toISOString() renverrait de l'UTC et
       decalerait d'un jour en soiree. */
    var champJour = document.getElementById("rdv-jour");
    if (champJour) {
      var deuxJours = new Date();
      deuxJours.setDate(deuxJours.getDate() + 2);
      var deuxChiffres = function (n) { return n < 10 ? "0" + n : "" + n; };
      champJour.min = deuxJours.getFullYear() + "-" +
        deuxChiffres(deuxJours.getMonth() + 1) + "-" +
        deuxChiffres(deuxJours.getDate());
    }

    var coche = function (nom) {
      var el = rdv.querySelector('input[name="' + nom + '"]:checked');
      return el ? el.value : "";
    };

    /* ---- La demande depend du besoin ----
       Les options de tous les besoins sont dans le HTML ; on ne laisse que
       celles du besoin coche. Si le besoin n'en propose aucune (l'AMO), le
       champ disparait entierement — et son "required" avec lui, sinon la
       validation bloquerait sur un champ invisible. */
    var champDemande = document.getElementById("champ-demande");
    var selDemande = document.getElementById("objet");
    if (champDemande && selDemande) {
      var toutesOptions = [].slice.call(selDemande.querySelectorAll("option[data-besoin]"));

      var accorderDemande = function () {
        var besoin = coche("Besoin");
        var gardees = toutesOptions.filter(function (o) {
          return o.getAttribute("data-besoin") === besoin;
        });

        toutesOptions.forEach(function (o) {
          if (gardees.indexOf(o) === -1) { o.remove(); }
          else if (!o.parentNode) { selDemande.appendChild(o); }
        });

        var utile = gardees.length > 0;
        champDemande.hidden = !utile;
        selDemande.required = utile;
        if (!utile) { selDemande.value = ""; }
      };

      rdv.querySelectorAll('input[name="Besoin"]').forEach(function (r) {
        r.addEventListener("change", accorderDemande);
      });
      accorderDemande();
    }

    /* ---- Photos et documents joints ----
       Les fichiers partent en base64 dans le meme envoi que le rendez-vous :
       le back-office les range dans un dossier Drive prive. Les bornes sont
       volontairement basses, l'envoi devant tenir dans une seule requete. */
    var MAX_FICHIERS = 5;
    var MAX_OCTETS = 5 * 1024 * 1024;
    var champFichiers = document.getElementById("photos");
    var listeFichiers = document.getElementById("fichiers-liste");
    var fichiersRetenus = [];

    var poids = function (o) {
      return o < 1024 * 1024 ? Math.round(o / 1024) + " Ko"
                             : (o / 1024 / 1024).toFixed(1) + " Mo";
    };

    var dessinerFichiers = function () {
      if (!listeFichiers) return;
      listeFichiers.innerHTML = fichiersRetenus.map(function (f, i) {
        return '<li><span class="fichiers-liste__nom">' + f.nom + "</span>" +
               '<span class="fichiers-liste__poids">' + poids(f.octets) + "</span>" +
               '<button type="button" class="fichiers-liste__retirer" data-i="' + i +
               '" aria-label="Retirer ' + f.nom + '">&times;</button></li>';
      }).join("");
    };

    if (champFichiers) {
      champFichiers.addEventListener("change", function () {
        var refuses = [];
        [].slice.call(champFichiers.files).forEach(function (f) {
          if (fichiersRetenus.length >= MAX_FICHIERS) {
            refuses.push(f.name + " (au-delà de " + MAX_FICHIERS + " fichiers)");
            return;
          }
          if (f.size > MAX_OCTETS) {
            refuses.push(f.name + " (" + poids(f.size) + ", trop lourd)");
            return;
          }
          var lecteur = new FileReader();
          lecteur.onload = function () {
            fichiersRetenus.push({
              nom: f.name,
              type: f.type || "application/octet-stream",
              octets: f.size,
              donnees: String(lecteur.result).split(",")[1]
            });
            dessinerFichiers();
          };
          lecteur.readAsDataURL(f);
        });
        champFichiers.value = "";       // permet de rechoisir le meme fichier
        if (refuses.length) {
          dire("Non joint : " + refuses.join(", ") + ".", false);
        }
      });
    }

    if (listeFichiers) {
      listeFichiers.addEventListener("click", function (e) {
        var b = e.target.closest(".fichiers-liste__retirer");
        if (!b) return;
        fichiersRetenus.splice(parseInt(b.getAttribute("data-i"), 10), 1);
        dessinerFichiers();
      });
    }

    /* Verifie les champs requis de l'etape avant d'avancer : la validation
       native ne porte que sur la soumission, pas sur un changement d'etape. */
    var etapeValide = function (n) {
      var bloc = etapes[n - 1];
      var champs = [].slice.call(bloc.querySelectorAll("input[required], select[required], textarea[required]"));
      for (var i = 0; i < champs.length; i++) {
        if (!champs[i].checkValidity()) {
          champs[i].reportValidity();
          return false;
        }
      }
      return true;
    };

    var afficher = function (n) {
      courante = n;
      etapes.forEach(function (e, i) {
        var actif = i + 1 === n;
        e.classList.toggle("est-active", actif);
        if (actif) { e.removeAttribute("hidden"); } else { e.setAttribute("hidden", ""); }
      });
      jalons.forEach(function (j, i) {
        j.classList.toggle("est-courant", i + 1 === n);
        j.classList.toggle("est-fait", i + 1 < n);
      });
      if (n === etapes.length) { preparerFinale(); }
      rdv.scrollIntoView({ behavior: "smooth", block: "start" });
    };

    /* Le format n'est plus recapitule : il se choisit dans cette etape meme,
       juste en dessous. On rappelle ce qui vient de l'etape precedente. */
    var preparerFinale = function () {
      if (recap) {
        recap.innerHTML =
          '<span class="recap__ligne"><b>Besoin</b> ' + coche("Besoin") + "</span>" +
          '<span class="recap__ligne"><b>Demande</b> ' + val("objet") + "</span>" +
          '<span class="recap__ligne"><b>Bien</b> ' + val("type-bien") + " à " + val("ville") + "</span>";
      }
    };

    rdv.addEventListener("click", function (e) {
      if (e.target.closest("[data-suivant]")) {
        if (etapeValide(courante)) { afficher(Math.min(courante + 1, etapes.length)); }
      } else if (e.target.closest("[data-precedent]")) {
        afficher(Math.max(courante - 1, 1));
      }
    });

    jalons.forEach(function (j, i) {
      j.addEventListener("click", function () {
        if (i + 1 < courante) { afficher(i + 1); }
      });
    });

    /* ---- Agenda : creneaux servis par le back-office ----
       Le script Google calcule les creneaux libres a partir des horaires du
       cabinet, des rendez-vous deja pris et de l'agenda du cabinet. Aucun
       service exterieur : c'est le meme point d'entree que le formulaire. */
    var agenda = document.getElementById("agenda");
    if (agenda) {
      var coordonnees = rdv.querySelector(".agenda__coordonnees");
      var service = agenda.getAttribute("data-service");
      var choisi = null;      // date ISO du creneau retenu
      var formatCharge = null;

      var deuxChiffres = function (n) { return n < 10 ? "0" + n : "" + n; };

      var chargerCreneaux = function () {
        var el = rdv.querySelector('input[name="Format"]:checked');
        var format = el ? el.getAttribute("data-cle") : "telephone";
        if (formatCharge === format) return;
        formatCharge = format;
        choisi = null;
        if (coordonnees) coordonnees.hidden = true;

        agenda.innerHTML = '<p class="agenda__attente">Chargement des créneaux disponibles…</p>';

        if (!service || service.indexOf("A_CONFIGURER") !== -1) {
          agenda.innerHTML = '<p class="agenda__erreur">L’agenda n’est pas encore relié. ' +
            'Merci de nous appeler pour convenir d’un rendez-vous.</p>';
          return;
        }

        fetch(service + "?action=creneaux&format=" + encodeURIComponent(format))
          .then(function (r) { return r.json(); })
          .then(function (data) {
            if (!data || !data.success || !data.jours || !data.jours.length) {
              agenda.innerHTML = '<p class="agenda__erreur">Aucun créneau disponible ' +
                'pour le moment. Appelez-nous, nous trouverons une date.</p>';
              return;
            }
            dessinerAgenda(data);
          })
          .catch(function () {
            agenda.innerHTML = '<p class="agenda__erreur">Les créneaux n’ont pas pu être ' +
              'chargés. Vérifiez votre connexion ou appelez-nous.</p>';
          });
      };

      var dessinerAgenda = function (data) {
        var jours = data.jours;
        var listeJours = jours.map(function (j, i) {
          var d = j.jour.split("-");
          return '<button type="button" class="agenda__jour' + (i === 0 ? " est-actif" : "") +
            '" data-jour="' + j.jour + '">' +
            '<span class="agenda__jour-nom">' + j.libelle.split(" ")[0].slice(0, 3) + '</span>' +
            '<span class="agenda__jour-num">' + d[2] + "</span></button>";
        }).join("");

        agenda.innerHTML =
          /* La duree est deja portee par le format selectionne juste au-dessus :
             la repeter ici ferait doublon dans le meme bloc. */
          '<p class="agenda__duree">Premier créneau sous 48 heures</p>' +
          '<div class="agenda__jours">' + listeJours + "</div>" +
          '<div class="agenda__heures"></div>';

        var afficherHeures = function (jour) {
          var j = jours.filter(function (x) { return x.jour === jour; })[0];
          if (!j) return;
          var zone = agenda.querySelector(".agenda__heures");
          zone.innerHTML = '<p class="agenda__libelle">' + j.libelle + "</p>" +
            '<div class="agenda__grille">' +
            j.heures.map(function (h) {
              return '<button type="button" class="agenda__heure" data-heure="' + h + '">' +
                h + "</button>";
            }).join("") + "</div>";
        };

        afficherHeures(jours[0].jour);

        agenda.addEventListener("click", function (e) {
          var bJour = e.target.closest(".agenda__jour");
          if (bJour) {
            agenda.querySelectorAll(".agenda__jour").forEach(function (b) {
              b.classList.toggle("est-actif", b === bJour);
            });
            choisi = null;
            if (coordonnees) coordonnees.hidden = true;
            afficherHeures(bJour.getAttribute("data-jour"));
            return;
          }

          var bHeure = e.target.closest(".agenda__heure");
          if (bHeure) {
            agenda.querySelectorAll(".agenda__heure").forEach(function (b) {
              b.classList.toggle("est-actif", b === bHeure);
            });
            var jour = agenda.querySelector(".agenda__jour.est-actif").getAttribute("data-jour");
            var heure = bHeure.getAttribute("data-heure");
            /* Date locale explicite : "2026-09-05T09:00" est interprete dans le
               fuseau du visiteur, ce qui correspond aux heures affichees. */
            choisi = jour + "T" + heure + ":00";
            if (coordonnees) {
              coordonnees.hidden = false;
              coordonnees.scrollIntoView({ behavior: "smooth", block: "nearest" });
            }
          }
        });
      };

      /* Le format est choisi dans la meme etape que le calendrier : changer de
         format doit donc recharger les creneaux tout de suite, la duree n'etant
         pas la meme (20 minutes au telephone, 30 en visio). */
      rdv.querySelectorAll('input[name="Format"]').forEach(function (r) {
        r.addEventListener("change", function () {
          formatCharge = null;
          chargerCreneaux();
        });
      });

      var afficherSansAgenda = afficher;
      afficher = function (n) {
        afficherSansAgenda(n);
        if (n === etapes.length) { chargerCreneaux(); }
      };

      var boutonRdv = rdv.querySelector("button[type=submit]");
      var libelleRdv = boutonRdv ? boutonRdv.textContent : "";

      rdv.addEventListener("submit", function (e) {
        e.preventDefault();
        if (!choisi) {
          dire("Merci de choisir un créneau avant de confirmer.", false);
          return;
        }

        if (boutonRdv) { boutonRdv.disabled = true; boutonRdv.textContent = "Enregistrement…"; }

        fetch(service, {
          method: "POST",
          body: JSON.stringify({
            jeton: rdv.getAttribute("data-jeton") || "",
            action: "reserver",
            piege: val("rdv-piege"),
            debut: choisi,
            format: rdv.querySelector('input[name="Format"]:checked').getAttribute("data-cle"),
            besoin: coche("Besoin"),
            objet: val("objet"),
            typeBien: val("type-bien"),
            description: val("description"),
            prenom: val("rdv-prenom"),
            nom: val("rdv-nom"),
            email: val("rdv-email"),
            telephone: val("rdv-telephone"),
            ville: val("ville"),
            consentement: document.getElementById("rdv-consentement").checked,
            photos: fichiersRetenus.map(function (f) {
              return { nom: f.nom, type: f.type, donnees: f.donnees };
            })
          }),
          headers: { "Content-Type": "text/plain;charset=utf-8" }
        })
          .then(function (r) { return r.json().catch(function () { return { success: r.ok }; }); })
          .then(function (data) {
            if (data && data.success) {
              rdv.querySelectorAll(".etape").forEach(function (et) { et.setAttribute("hidden", ""); });
              var jalonsRdv = document.querySelector(".jalons");
              if (jalonsRdv) { jalonsRdv.hidden = true; }

              var enVisio = rdv.querySelector('input[name="Format"]:checked')
                               .getAttribute("data-cle") === "visio";
              afficherConfirmation(
                msg,
                "Votre rendez-vous est confirmé",
                data.quand || "au créneau choisi",
                [
                  "Un e-mail de confirmation vient de vous être envoyé à <strong>" +
                    echapperHtml(val("rdv-email")) + "</strong>.",
                  enVisio
                    ? "Le lien de visioconférence vous sera transmis avant l’entretien."
                    : "Mickael Rigaud vous appellera au <strong>" +
                      echapperHtml(val("rdv-telephone")) + "</strong>.",
                  "Votre demande est enregistrée : nous la préparons avant l’échange, " +
                    "documents joints compris.",
                  "Pour décaler ou annuler, répondez à cet e-mail ou appelez-nous au " +
                    "<strong>06 81 65 15 91</strong>."
                ]
              );
            } else {
              /* Creneau pris entre-temps : on recharge la liste. */
              dire((data && data.message) || "L’enregistrement a échoué. Merci de nous appeler.", false);
              formatCharge = null;
              chargerCreneaux();
            }
          })
          .catch(function () {
            dire("L’enregistrement a échoué. Merci de nous appeler directement.", false);
          })
          .then(function () {
            if (boutonRdv) { boutonRdv.disabled = false; boutonRdv.textContent = libelleRdv; }
          });
      });
    }
  }

  /* ---- Carte des zones d'intervention ----
     Survol d'une commune : son nom s'affiche dans une bulle qui suit le
     curseur. Survol d'une ville dans les listes : le repere correspondant
     s'anime sur la carte et le departement passe au premier plan. */
  var carte = document.querySelector(".zone-carte");
  if (carte) {
    var bulle = carte.querySelector(".zone-carte__bulle");
    var plan = carte.querySelector(".zone-carte__plan");

    plan.addEventListener("mousemove", function (e) {
      var cible = e.target.closest(".commune");
      if (!cible) { bulle.hidden = true; return; }
      var cadre = plan.getBoundingClientRect();
      bulle.textContent = cible.getAttribute("data-nom");
      bulle.style.left = (e.clientX - cadre.left) + "px";
      bulle.style.top = (e.clientY - cadre.top) + "px";
      bulle.hidden = false;
    });
    plan.addEventListener("mouseleave", function () { bulle.hidden = true; });

    /* Clic sur une commune : elle s'anime et son nom reste affiche. Sur
       telephone c'est aussi le seul moyen de lire un nom, faute de survol. */
    var choisirCommune = function (commune, x, y) {
      if (!commune) return;
      var deja = plan.querySelector(".commune.est-choisie");
      if (deja) { deja.classList.remove("est-choisie"); }
      if (deja === commune) { bulle.hidden = true; return; }   // second clic : on eteint

      // Forcer un recalcul relance l'animation quand on enchaine les clics.
      void commune.getBoundingClientRect();
      commune.classList.add("est-choisie");

      var cadre = plan.getBoundingClientRect();
      var r = commune.getBoundingClientRect();
      bulle.textContent = commune.getAttribute("data-nom");
      // Sans position de clic — appel depuis la liste laterale — on pose
      // l'etiquette sur la commune elle-meme.
      bulle.style.left = ((x == null ? r.left + r.width / 2 : x) - cadre.left) + "px";
      bulle.style.top = ((y == null ? r.top + r.height / 2 : y) - cadre.top) + "px";
      bulle.hidden = false;
    };

    var communeNommee = function (nom) {
      return plan.querySelector('.commune[data-nom="' + String(nom).replace(/"/g, '\\"') + '"]');
    };

    plan.addEventListener("click", function (e) {
      /* Le repere d'une ville est teste en premier : viser le milieu de
         Cannes ou d'Hyeres tombe dans la mer, celui de Frejus ou de
         Brignoles dans la commune voisine. Le point, lui, ne se trompe pas. */
      var marque = e.target.closest(".repere");
      if (marque) {
        choisirCommune(communeNommee(marque.getAttribute("data-ville")),
                       e.clientX, e.clientY);
        return;
      }
      choisirCommune(e.target.closest(".commune"), e.clientX, e.clientY);
    });

    /* Les noms des communes sont sur les traces : on annonce le departement
       survole aux lecteurs d'ecran plutot que chaque commune. */
    var reperes = [].slice.call(carte.querySelectorAll(".repere"));
    var boutons = [].slice.call(carte.querySelectorAll(".zone-dept__villes button"));

    var eclairer = function (ville, dept) {
      reperes.forEach(function (r) {
        r.classList.toggle("est-actif", r.getAttribute("data-ville") === ville);
      });
      boutons.forEach(function (b) {
        b.classList.toggle("est-actif", b.getAttribute("data-ville") === ville);
      });
      if (dept) { carte.setAttribute("data-actif", dept); }
      else { carte.removeAttribute("data-actif"); }
    };

    boutons.forEach(function (b) {
      var ville = b.getAttribute("data-ville");
      var dept = b.closest(".zone-dept--06") ? "06" : "83";
      var montrer = function () { eclairer(ville, dept); };
      b.addEventListener("mouseenter", montrer);
      b.addEventListener("focus", montrer);
      b.addEventListener("click", function () {
        montrer();
        // La commune s'anime aussi : cliquer un nom dans la liste et cliquer
        // la ville sur la carte doivent produire le meme effet.
        choisirCommune(communeNommee(ville), null, null);
      });
    });

    carte.querySelector(".zone-carte__listes")
      .addEventListener("mouseleave", function () { eclairer(null, null); });
  }

  /* --- Video du hero : lecture uniquement si l'utilisateur ne demande pas moins d'animations --- */
  var video = document.querySelector(".hero__media video");
  if (video && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    video.removeAttribute("autoplay");
    video.pause();
  }

  /* ---- Candidature au reseau d'experts (page Rejoignez-nous) ----
     Sans ce script, le navigateur postait le formulaire en natif, donc en
     donnees de formulaire la ou le back-office attend du JSON : la demande
     etait perdue et le visiteur atterrissait sur une page d'erreur brute. */
  var reseau = document.getElementById("form-reseau");
  if (reseau) {
    var msgReseau = document.getElementById("reseau-message");
    var champ = function (id) {
      var e = document.getElementById(id);
      return e ? e.value.trim() : "";
    };
    var bouton = reseau.querySelector("button[type=submit]");
    var libelle = bouton ? bouton.textContent : "";

    var annoncer = function (texte, ok) {
      if (!msgReseau) return;
      msgReseau.textContent = texte;
      msgReseau.className = "formulaire__message formulaire__message--" + (ok ? "ok" : "ko");
      msgReseau.scrollIntoView({ behavior: "smooth", block: "center" });
    };

    reseau.addEventListener("submit", function (e) {
      e.preventDefault();

      /* Un groupe de cases a cocher ne peut pas etre rendu obligatoire par le
         HTML seul : on verifie ici qu'au moins un departement est retenu. */
      var departements = [].slice
        .call(reseau.querySelectorAll('input[name="Departements"]:checked'))
        .map(function (c) { return c.value; });
      if (!departements.length) {
        annoncer("Merci d’indiquer au moins un département d’intervention.", false);
        return;
      }

      if (bouton) { bouton.disabled = true; bouton.textContent = "Envoi…"; }

      fetch(reseau.getAttribute("action"), {
        method: "POST",
        body: JSON.stringify({
          jeton: reseau.getAttribute("data-jeton") || "",
          piege: champ("r-piege"),
          type: "Candidature au réseau d’experts",
          objet: champ("r-specialites"),
          nom: champ("r-nom"),
          prenom: "",
          email: champ("r-email"),
          telephone: champ("r-telephone"),
          ville: champ("r-societe"),
          /* Les champs partent aussi un a un : le courriel interne les
             presente en fiche, plutot qu'en bloc de texte. */
          candidature: {
            departements: departements.join(", "),
            societe: champ("r-societe"),
            siret: champ("r-siret"),
            experience: champ("r-experience"),
            specialites: champ("r-specialites"),
            qualifications: champ("r-qualifications"),
            rcpro: champ("r-rcpro"),
            message: champ("r-message")
          },
          description: [
            "Départements : " + departements.join(", "),
            "Société : " + champ("r-societe"),
            "SIRET : " + champ("r-siret"),
            "Expérience : " + champ("r-experience"),
            "Spécialités : " + champ("r-specialites"),
            "Qualifications : " + champ("r-qualifications"),
            "RC professionnelle : " + champ("r-rcpro"),
            "", champ("r-message")
          ].join("\n"),
          consentement: document.getElementById("r-consentement").checked
        }),
        headers: { "Content-Type": "text/plain;charset=utf-8" }
      })
        .then(function (r) {
          return r.json().catch(function () { return { success: r.ok }; });
        })
        .then(function (data) {
          if (data && data.success) {
            var courriel = champ("r-email");
            reseau.reset();
            [].slice.call(reseau.querySelectorAll(".champ, .etape__actions, button"))
              .forEach(function (el) { el.hidden = true; });
            afficherConfirmation(
              msgReseau,
              "Votre candidature est bien envoyée",
              "",
              [
                "Un accusé de réception vient de vous être envoyé à <strong>" +
                  echapperHtml(courriel) + "</strong>.",
                "Le cabinet étudie votre dossier — expérience, spécialités et " +
                  "assurance professionnelle — et revient vers vous.",
                "Une question d’ici là&nbsp;? Appelez-nous au " +
                  "<strong>06 81 65 15 91</strong>."
              ]
            );
          } else {
            annoncer((data && data.message) ||
                     "L’envoi a échoué. Merci de nous écrire directement.", false);
          }
        })
        .catch(function () {
          annoncer("L’envoi a échoué. Vérifiez votre connexion, ou écrivez-nous " +
                   "directement.", false);
        })
        .then(function () {
          if (bouton) { bouton.disabled = false; bouton.textContent = libelle; }
        });
    });
  }

  /* ---- Carte des trois villes (page zones d'intervention) ----
     La commune sur la carte et le bouton a cote designent la meme ville :
     survoler l'un allume l'autre. Le clic mene a la page dans les deux cas,
     c'est le lien HTML qui s'en charge, pas ce script. */
  var carteVilles = document.querySelector(".carte-villes");
  if (carteVilles) {
    var cibles = [].slice.call(
      carteVilles.querySelectorAll("[data-ville]"));

    var allumer = function (ville) {
      cibles.forEach(function (c) {
        c.classList.toggle("est-active", ville !== null &&
                           c.getAttribute("data-ville") === ville);
      });
    };

    cibles.forEach(function (c) {
      var ville = c.getAttribute("data-ville");
      var montrer = function () { allumer(ville); };
      var eteindre = function () { allumer(null); };
      c.addEventListener("mouseenter", montrer);
      c.addEventListener("focus", montrer);
      c.addEventListener("mouseleave", eteindre);
      c.addEventListener("blur", eteindre);
    });
  }
})();
