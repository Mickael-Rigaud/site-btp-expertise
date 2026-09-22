# Sauvegarde zone DNS — btpexpertise.fr

Relevé le 2026-08-24 via `nslookup ... 8.8.8.8` (source faisant foi : les DNS WordPress.com).

## Serveurs de noms (NS)

    ns1.wordpress.com
    ns2.wordpress.com
    ns3.wordpress.com

## Enregistrements

| Type  | Nom   | Valeur                        |
|-------|-------|-------------------------------|
| A     | @     | 192.0.78.24                   |
| A     | @     | 192.0.78.25                   |
| CNAME | www   | btpexpertise.fr               |

- **Aucun enregistrement MX** : aucune messagerie n'est active sur le domaine.
- **Aucun enregistrement TXT** : pas de SPF, pas de DKIM, pas de vérification Google.
- TTL par défaut de la zone : 300 s (5 min). SOA serial 2026052104.

Les IP `192.0.78.24/25` sont celles de l'infrastructure WordPress.com.

## État du site au 2026-08-24

`https://btpexpertise.fr` redirige vers `https://contactbtpexpertiseriviera-pcoxq.wpcomstaging.com`
et affiche la page « Une idée brillante, bientôt disponible » de WordPress.com :
le site est en mode **privé / bientôt disponible**, donc **pas public et pas indexé**.

Conséquence : aucune continuité de service à préserver lors de la bascule vers OVH
(ni site en production, ni e-mail). Pas de redirections 301 à prévoir.

## Pour restaurer l'état actuel

Recréer dans la zone DNS OVH : `A @ 192.0.78.24`, `A @ 192.0.78.25`, `CNAME www btpexpertise.fr`.
