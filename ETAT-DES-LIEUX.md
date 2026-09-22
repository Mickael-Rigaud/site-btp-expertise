# BTP Expertise — état des lieux du site existant

Capture réalisée le 2026-08-24 depuis `contactbtpexpertiseriviera-pcoxq.wpcomstaging.com`.

## Ce qui a été récupéré

| Élément | Où | Détail |
|---|---|---|
| Pages HTML rendues | `capture/pages/` | 8 pages + 1 article, telles qu'affichées |
| Contenu structuré | `capture/content/_pages.json`, `_posts.json` | titres, contenus Elementor rendus, métadonnées |
| Textes lisibles | `capture/texte/` | un `.txt` par page |
| Médias | `capture/assets/` | 101 fichiers en pleine résolution |
| Inventaire médias | `capture/content/_media_manifest.json` | nom, URL d'origine, texte alternatif |
| Feuilles de style | `capture/raw/` | CSS Elementor par page (`post-19.css`, etc.) |
| Zone DNS | `DNS-SAUVEGARDE-btpexpertise.fr.md` | état avant bascule |

L'export XML de WordPress.com n'est plus nécessaire : l'API REST a donné mieux (rendu final + médias d'origine).

## Structure du site

| Page | ID | URL actuelle |
|---|---|---|
| Accueil | 19 | `/` |
| Qui sommes-nous | 68 | `/?page_id=68` |
| Expertises | 64 | `/?page_id=64` |
| Maîtrise d'œuvre | 602 | `/?page_id=602` |
| Nos conseils (blog) | 99 | `/?page_id=99` |
| FAQ | 105 | `/?page_id=105` |
| Demandez une expertise | 108 | `/?page_id=108` |
| *About* (page WordPress par défaut) | 1 | `/?page_id=1` — à supprimer |
| Article : fissures / retrait-gonflement des argiles en PACA | 384 | `/?p=384` |

Les permaliens « jolis » ne sont pas activés : toutes les URLs sont en `?page_id=`. Comme le site n'a jamais été public, aucune URL n'est à préserver — on repart sur des adresses propres (`/expertises/`, `/faq/`…).

## Technique actuelle

Thème **Hello Biz** + **Elementor** et **Elementor Pro**, plus Essential Addons for Elementor, 3r Elementor Timeline Widget, Rich Event Timeline, Jetpack, Gutenberg. Elementor Pro impose un plan WordPress.com Business/Creator : c'est le poste de coût à supprimer.

## Les cinq prestations

Avis technique · Recherche de malfaçons et contrôle qualité · Maîtrise d'œuvre et coordination de travaux · Expertise avant achat immobilier · Réception de travaux.

Compétences mises en avant : maîtrise d'œuvre et suivi de chantier, malfaçons et non-conformités, infiltrations et étanchéité, fissures et atteintes structurelles.

## Points à corriger — relevés à la capture

1. **Adresse non renseignée** : le pied de page affiche `11 rue adresse 06000 NICE`. Texte de remplissage jamais remplacé, visible sur toutes les pages.
2. **Incohérence de ville** : la page *Qui sommes-nous* annonce un cabinet « basé à Antibes », le pied de page indique Nice.
3. **E-mail à l'ancien nom** : `contact@btpexpertiseriviera.fr` — domaine différent de `btpexpertise.fr`. À remplacer par une adresse sur le bon domaine (le compte mail 5 Go inclus chez OVH suffit).
4. **Titre de remplissage Elementor** : « Ajoutez votre titre ici » en tête de *Qui sommes-nous*.
5. **Bloc dupliqué** : « Zone d'intervention » et les trois piliers apparaissent deux fois sur *Qui sommes-nous*.
6. **Mentions légales et Politique de confidentialité absentes** : présentes en pied de page mais sans lien, les pages n'existent pas. Obligatoires pour un site professionnel français (et le formulaire collecte des données personnelles).
7. **Le Var (83) n'apparaît nulle part** : le site parle de Côte d'Azur, Alpes-Maritimes et PACA. Si le Var est une zone cible, il faut le dire explicitement, y compris pour le référencement local.
8. **Poids des images** : environ 1,2 Mo par image en moyenne, non optimisées. À convertir en WebP — indispensable pour tenir dans les 100 Mo de l'hébergement OVH, et pour la vitesse d'affichage.
9. **Formulaire Elementor Pro** avec upload de photos : à reconstruire sans WordPress (service externe ou petit service d'envoi maison).
10. **Page *About*** par défaut de WordPress, à supprimer.

## À confirmer

- Adresse postale réelle du cabinet.
- Adresse e-mail définitive à utiliser.
- Le Var (83) fait-il bien partie de la zone d'intervention à afficher ?
