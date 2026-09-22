# Identité visuelle — BTP Expertise

Déclinaisons du logo, demandées au §1 du cahier des charges. Ces fichiers ne
servent pas au site (qui utilise ses propres versions WebP, plus légères) mais
aux documents, signatures de courriel, réseaux sociaux et supports imprimés.

Format PNG avec fond transparent, accepté partout.

| Fichier | Usage |
|---|---|
| `logo-principal.png` | fonds clairs — documents, papier à en-tête, site |
| `logo-fond-sombre.png` | fonds sombres — le texte et la loupe passent en blanc |
| `logo-compact.png` | pictogramme seul, carré — avatar, favicon, réseaux sociaux |
| `logo-compact-fond-sombre.png` | pictogramme seul sur fond sombre |
| `logo-source.svg` | fichier d'origine fourni par Mickael Rigaud |

Les bâtiments gardent toujours leurs couleurs (bleu `#0BBBF6`, orange `#FF8A00`).
Seuls le texte « BTP EXPERTISE » et le cercle de la loupe changent : bleu nuit
`#262C42` sur fond clair, blanc sur fond sombre.

Pour un fond de couleur intermédiaire, prendre la version qui offre le plus de
contraste avec le texte, jamais un fond qui rend le nom illisible.

## Regénérer

Les versions du site sont produites par `build.py` à partir de
`site/assets/img/logo-btp-expertise-v2.webp`. Ce dossier-ci est indépendant :
si le logo change, repartir de `logo-source.svg`.
