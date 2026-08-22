# Veille technique et réglementaire (C6)

**Thématique de veille** : usage de l'IA/ML pour la maintenance prédictive industrielle et l'optimisation des pièces de rechange — directement reliée au besoin du projet (mission 3-4 du cahier des charges).

**Fréquence** : recherche hebdomadaire (1h, le lundi), synthèse mise à jour ici à chaque évolution significative. Dernière mise à jour : 2026-08-01.

## Sources retenues

| Source | Auteur / organisation | Date | Fiabilité |
|---|---|---|---|
| [Industrial AI in Action: Predictive Maintenance and Operational Efficiency at Scale](https://www.automate.org/blogs/industrial-ai-in-action-predictive-maintenance-and-operational-efficiency-at-scale) | A3 – Association for Advancing Automation (association professionnelle du secteur automatisation industrielle, États-Unis) | 2026 | **Élevée** — organisation professionnelle identifiée, sans intérêt commercial direct à vendre un produit précis, vocation à informer le secteur. |
| [Machine Learning in Predictive Maintenance: 2026 Guide](https://aisuperior.com/machine-learning-in-predictive-maintenance/) | AI Superior (cabinet de conseil IA) | 2026 | **Moyenne** — contenu technique correct et détaillé, mais provient d'un cabinet de conseil dont l'activité est de vendre des prestations IA : angle commercial à prendre en compte, chiffres à recouper. |
| [How AI is Used in Predictive Maintenance](https://www.neuralconcept.com/post/how-ai-is-used-in-predictive-maintenance) | Neural Concept (éditeur de logiciel de simulation IA) | 2026 | **Moyenne** — même réserve : éditeur logiciel, contenu à visée en partie promotionnelle, mais recoupe les mêmes ordres de grandeur que les deux autres sources (convergence = indice de fiabilité). |

## Synthèse des informations utiles

- Le secteur passe progressivement d'une maintenance **réactive** ("on répare quand ça casse") à une maintenance **prédictive** pilotée par les données — exactement l'objectif de ce projet.
- Les modèles de ML en maintenance prédictive atteignent couramment **80 à 97 % de précision** de détection de panne selon les sources consultées, avec des alertes possibles 60 à 90 jours avant la panne dans les meilleurs cas — utile pour calibrer les attentes réalistes du modèle développé ici (voir `docs/benchmark_ia.md` et les métriques du modèle dans `src/ml/`).
- L'optimisation des pièces de rechange par IA permettrait, selon ces sources, une réduction de consommation de pièces de l'ordre de **10 à 20 %** et des économies globales de maintenance de **20 à 30 %** (planification optimisée, réduction du stock dormant, moins de réparations en urgence) — cohérent avec l'objectif "mission 7" du cahier des charges (recommandations de réduction de coûts).
- Point de vigilance identifié : les trois sources sont des contenus d'entreprises/associations du secteur, donc à recouper avec des publications académiques si le projet devait être approfondi en Phase B (ex. IEEE, journaux de maintenance industrielle).

## Impact sur le projet

Cette veille confirme la pertinence du choix technique du projet (modèle de classification pour la prédiction de panne + prévision de demande de pièces) et fixe un ordre de grandeur réaliste pour l'évaluation du modèle : un taux de détection très supérieur à 97% sur des données aussi simples que AI4I 2020 serait suspect (sur-apprentissage), un taux nettement inférieur à 80% signalerait un modèle insuffisant.

## Réglementation et considérations transverses

*Point de veille, pas un avis juridique : en cas de mise en production réelle, une revue par un juriste spécialisé resterait nécessaire.*

- **RGPD** : traité en détail dans [`docs/rgpd.md`](rgpd.md), rédigé avant la création du modèle `User`. Les données de maintenance/capteurs ne concernent pas des personnes physiques et sont hors périmètre RGPD ; seul le compte utilisateur (authentification, rôle) l'est.
- **AI Act européen (Règlement (UE) 2024/1689)** : entré en vigueur en août 2024, obligations applicables progressivement jusqu'en 2027. Classe les systèmes d'IA par niveau de risque (inacceptable / élevé / limité / minimal). Un outil d'aide à la décision pour la maintenance et la gestion de stock, à usage interne et sans décision automatisée irréversible sur une personne, relève a priori d'un risque limité à minimal — à la différence d'un système de sécurité critique (ex. gestion directe d'infrastructures). Point à surveiller si le périmètre du projet évoluait vers un usage plus critique (ex. arrêt automatique d'une machine sans validation humaine).
- **Sécurité des données** : capteurs et flux applicatifs déjà couverts par [`docs/monitoring.md`](monitoring.md) (journalisation, seuils d'alerte) et [`docs/rgpd.md`](rgpd.md) (secrets hors code, CORS restreint, mots de passe hachés).
- **Accessibilité** : critères intégrés dès la rédaction des user stories ([`docs/cahier_des_charges.md`](cahier_des_charges.md)), pas ajoutés après coup — voir aussi C17 (aria-labels, rôles d'alerte sur le frontend).
