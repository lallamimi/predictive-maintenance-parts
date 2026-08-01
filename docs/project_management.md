# Suivi de projet (C16)

## Méthode retenue

Projet individuel : pas de méthode agile en équipe (Scrum/rituels collectifs) au sens strict, mais une **conduite de projet structurée et tracée**, transposition solo des principes agiles pertinents :

- **Backlog priorisé** : liste de tâches explicite, une tâche = une compétence ou un sous-ensemble cohérent de compétences.
- **Incrément livré à chaque tâche terminée** : chaque tâche se conclut par un commit Git nommé, vérifié fonctionnellement avant d'être marqué "fini" (jamais de commit sur du code non testé).
- **État du backlog visible à tout moment** : statut `à faire / en cours / terminé` tenu à jour tâche par tâche (voir historique ci-dessous).
- **Revue continue** : chaque incrément est testé de bout en bout (requêtes HTTP réelles, interactions navigateur réelles) avant validation, pas seulement relu.

## Backlog réel du projet (extrait, ordre chronologique)

| # | Tâche | Compétence(s) | Statut |
|---|---|---|---|
| 1 | Structure du projet, dépôt Git | — | Terminé |
| 2 | Scripts de collecte (dataset public + génération synthétique) | C1 | Terminé |
| 3 | Schéma SQL, requêtes d'analyse, nettoyage, validation | C2, C3 | Terminé |
| 4 | Modèles Django, API données, JWT, RGPD | C4, C5 | Terminé |
| 5 | Veille, benchmark, intégration Groq | C6, C7, C8 | Terminé |
| 6 | Entraînement des modèles (panne, demande), SHAP | — (base C9-C13) | Terminé |
| 7 | API modèle IA + intégration dashboard React | C9, C10 | Terminé |
| 8 | Monitoring modèle, tests automatisés, CI | C11, C12, C13 | Terminé |
| 9 | Cahier des charges, architecture, suivi de projet | C14, C15, C16 | Terminé |
| 10 | Rôles, permissions, tests d'accès | C17 | À faire |
| 11 | CI étendue, Docker, livraison continue | C18, C19 | À faire |
| 12 | Monitoring applicatif, incident réel documenté | C20, C21 | À faire |
| 13 | Vérification finale de bout en bout | Toutes | À faire |

*(Statuts à la date de rédaction de ce document — voir l'historique Git pour la trace exacte datée de chaque livraison.)*

## Décisions prises en cours de route (traçabilité)

- **Choix de repartir sur un projet individuel** plutôt que de retravailler un projet de groupe existant : élimine toute ambiguïté d'attribution pour un examen individuel.
- **Combinaison dataset public + données synthétiques** (plutôt que 100 % synthétique ou un dataset non adapté) : décision prise pour maximiser le réalisme tout en couvrant un besoin (pièces de rechange) qu'aucun dataset public ne couvre.
- **Django plutôt que FastAPI** pour le backend : réutilisation d'un pattern déjà maîtrisé, réduction du risque technique, au prix d'un peu plus de code de configuration initial.
- **Deux modèles IA distincts** (modèle maison + service tiers Groq) plutôt qu'un seul : permet de démontrer à la fois le Bloc 2 "construire son propre modèle" et "intégrer un service IA existant", qui sont deux compétences séparées du référentiel.

## Pour aller plus loin (Phase B, si un vrai suivi visuel est souhaité)

Un board **GitHub Projects** peut être créé en un clic depuis l'onglet "Projects" du dépôt [predictive-maintenance-parts](https://github.com/lallamimi/predictive-maintenance-parts), avec les colonnes `À faire / En cours / Terminé` et une carte par ligne du tableau ci-dessus — utile pour une capture d'écran de soutenance si le jury demande un outil visuel en plus de ce document.
