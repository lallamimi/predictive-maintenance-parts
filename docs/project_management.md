# Suivi de projet (C16)

## Méthode retenue

Projet individuel : pas de méthode agile en équipe (Scrum/rituels collectifs) au sens strict, mais une **conduite de projet structurée et tracée**, transposition solo des principes agiles pertinents :

- **Backlog priorisé** : liste de tâches explicite, une tâche = une compétence ou un sous-ensemble cohérent de compétences.
- **Incrément livré à chaque tâche terminée** : chaque tâche se conclut par un commit Git nommé, vérifié fonctionnellement avant d'être marqué "fini" (jamais de commit sur du code non testé).
- **État du backlog visible à tout moment** : statut `à faire / en cours / terminé` tenu à jour tâche par tâche (voir historique ci-dessous).
- **Revue continue** : chaque incrément est testé de bout en bout (requêtes HTTP réelles, interactions navigateur réelles) avant validation, pas seulement relu.

## Rôles

Projet solo : pas de référents distincts par personne, mais une séparation explicite des responsabilités par domaine, reflétée directement dans l'architecture (`docs/architecture.md`) plutôt que dans un organigramme fictif :

| Domaine (équivalent "référent") | Périmètre réel |
|---|---|
| Données | `src/collect/`, `src/sql/`, `src/clean/` — collecte, SQL, nettoyage (C1-C3) |
| API données | `src/backend/inventory/`, `maintenance/` — modèles, endpoints REST (C4-C5) |
| Modèle IA | `src/ml/`, `src/backend/ml_api/` — entraînement, exposition, monitoring (C9-C13) |
| Interface | `src/frontend/` — dashboard React, tests Vitest (C10, C17) |
| Tests / qualité / CI | `src/backend/tests/`, `.github/workflows/ci.yml` (C12, C13, C18) |

Un seul candidat porte les cinq domaines, mais chacun a sa propre arborescence, ses propres tests et sa propre documentation — pas un code monolithique indifférencié.

## Rituels

Pas de cérémonies Scrum d'équipe (pas de sens à un daily seul), mais des équivalents réels et tracés :

- **Point d'avancement** : au minimum un par machine/session de travail — voir `soutenance_slides_progress.md` (fichier de suivi tenu à jour à chaque compétence traitée, y compris lors d'une reprise sur une autre machine le 05/08/2026).
- **Revue** : chaque tâche est vérifiée fonctionnellement avant d'être marquée terminée (tests, requêtes HTTP réelles, interactions navigateur réelles) — jamais une simple relecture de code.
- **Rétrospective** : appliquée concrètement après chaque incident réel (voir `docs/incident_report.md`) — ex. la leçon tirée de l'incident 1 ("vérifier explicitement plutôt que corriger silencieusement") a été appliquée de façon préventive à un second fichier, avant de se révéler elle-même incomplète et de déclencher l'incident 2 — cycle rétrospective → action → nouvelle rétrospective, documenté sans l'enjoliver.

## Backlog réel du projet (ordre chronologique, statuts corrigés au 05/08/2026)

| # | Tâche | Compétence(s) | Statut | Date |
|---|---|---|---|---|
| 1 | Structure du projet, dépôt Git | — | Terminé | 2026-08-01 |
| 2 | Scripts de collecte (dataset public + génération synthétique) | C1 | Terminé | 2026-08-01 |
| 3 | Schéma SQL, requêtes d'analyse, nettoyage, validation | C2, C3 | Terminé | 2026-08-01 |
| 4 | Modèles Django, API données, JWT, RGPD | C4, C5 | Terminé | 2026-08-01 |
| 5 | Veille, benchmark, intégration Groq | C6, C7, C8 | Terminé | 2026-08-01 |
| 6 | Entraînement des modèles (panne, demande), SHAP | — (base C9-C13) | Terminé | 2026-08-01 |
| 7 | API modèle IA + intégration dashboard React | C9, C10 | Terminé | 2026-08-01 |
| 8 | Monitoring modèle, tests automatisés, CI | C11, C12, C13 | Terminé | 2026-08-01 |
| 9 | Cahier des charges, architecture, suivi de projet | C14, C15, C16 | Terminé | 2026-08-01 |
| 10 | Rôles, permissions, tests d'accès | C17 | Terminé | 2026-08-01 |
| 11 | CI étendue, Docker, livraison continue | C18, C19 | Terminé | 2026-08-01 |
| 12 | Monitoring applicatif, incident réel documenté | C20, C21 | Terminé | 2026-08-01 |
| 13 | Incident réel : crash Docker en CI, diagnostiqué et corrigé en binôme | C21 | Terminé | 2026-08-01 |
| 14 | Refonte du design frontend (inspiration FinCoach, thème clair/sombre, icônes) | C17 | Terminé | 2026-08-01 |
| 15 | Vérification et correction des preuves C1 à C8 | C1-C8 | Terminé | 2026-08-04 |
| 16 | Vérification et correction des preuves C9 à C13 | C9-C13 | Terminé | 2026-08-04 |
| 17 | Vérification et correction des preuves C14, C15 | C14, C15 | Terminé | 2026-08-05 |

*(Corrigé le 05/08/2026 : les lignes 10 à 13 étaient marquées "à faire" alors qu'elles étaient déjà terminées — incohérence trouvée et corrigée. Dates vérifiées par `git log`, pas estimées.)*

## Décisions prises en cours de route (traçabilité)

- **Choix de repartir sur un projet individuel** plutôt que de retravailler un projet de groupe existant : élimine toute ambiguïté d'attribution pour un examen individuel.
- **Combinaison dataset public + données synthétiques** (plutôt que 100 % synthétique ou un dataset non adapté) : décision prise pour maximiser le réalisme tout en couvrant un besoin (pièces de rechange) qu'aucun dataset public ne couvre.
- **Django plutôt que FastAPI** pour le backend : réutilisation d'un pattern déjà maîtrisé, réduction du risque technique, au prix d'un peu plus de code de configuration initial.
- **Deux modèles IA distincts** (modèle maison + service tiers Groq) plutôt qu'un seul : permet de démontrer à la fois le Bloc 2 "construire son propre modèle" et "intégrer un service IA existant", qui sont deux compétences séparées du référentiel.

## Pour aller plus loin (Phase B, si un vrai suivi visuel est souhaité)

Un board **GitHub Projects** peut être créé en un clic depuis l'onglet "Projects" du dépôt [predictive-maintenance-parts](https://github.com/lallamimi/predictive-maintenance-parts), avec les colonnes `À faire / En cours / Terminé` et une carte par ligne du tableau ci-dessus — utile pour une capture d'écran de soutenance si le jury demande un outil visuel en plus de ce document.
