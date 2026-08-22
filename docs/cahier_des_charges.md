# Cahier des charges — Système d'aide à la décision maintenance & pièces de rechange

*Projet fictif individuel — voir README.md. Compétence C14.*

## 1. Contexte et objectif

Un service de maintenance automobile (fictif) souhaite passer d'une gestion réactive à une gestion prédictive : anticiper les pannes de véhicules et optimiser la disponibilité des pièces de rechange associées, afin de réduire les coûts opérationnels et les délais d'immobilisation.

## 2. Personas / utilisateurs cibles

| Persona | Rôle applicatif | Besoin principal |
|---|---|---|
| **Amine, technicien de maintenance** | `technicien` | Vérifier rapidement si un véhicule présente un risque de panne avant intervention |
| **Sophie, gestionnaire de stock** | `gestionnaire_stock` | Anticiper la demande de pièces et éviter les ruptures de stock |
| **Karim, administrateur système** | `admin` | Superviser l'ensemble (utilisateurs, données, monitoring) |

## 3. User stories et critères d'acceptation

### US-1 — Consulter les indicateurs clés
**En tant que** gestionnaire de stock, **je veux** voir en un coup d'œil le taux de panne, le nombre d'interventions et le coût cumulé, **afin de** évaluer rapidement l'état du parc.
- Critère 1 : les KPI se chargent en moins de 2 secondes après connexion.
- Critère 2 : chaque indicateur a un intitulé explicite et lisible sans jargon technique.
- Critère 3 (accessibilité) : chaque carte KPI est identifiable par un lecteur d'écran (`role="group"` + `aria-label`, voir `KpiCard.jsx`).

### US-2 — Prédire le risque de panne d'un véhicule
**En tant que** technicien, **je veux** saisir les mesures capteur d'un véhicule et obtenir une probabilité de panne, **afin de** décider si une intervention préventive est nécessaire.
- Critère 1 : le formulaire refuse les valeurs hors plage physique plausible (ex. température négative) avant envoi.
- Critère 2 : le résultat affiche la probabilité, un niveau de risque (faible/moyen/élevé) et un code couleur.
- Critère 3 : en cas d'erreur serveur, un message clair est affiché (pas d'écran blanc).

### US-3 — Prévoir la demande d'une pièce de rechange
**En tant que** gestionnaire de stock, **je veux** sélectionner une pièce et connaître la demande prévue pour le mois suivant, **afin de** décider s'il faut commander.
- Critère 1 : la liste des pièces provient des données réelles de la base (pas de valeurs codées en dur).
- Critère 2 : si aucun historique n'existe pour la pièce, l'utilisateur est prévenu explicitement (pas de faux chiffre présenté comme fiable).

### US-4 — Recevoir une recommandation en langage naturel
**En tant que** gestionnaire de stock, **je veux** une phrase de synthèse actionnable plutôt que des chiffres bruts, **afin de** gagner du temps de lecture.
- Critère 1 : la recommandation reste disponible même si le service IA externe est indisponible (repli par règles).
- Critère 2 : la source de la recommandation (IA générative ou règles) est indiquée à l'utilisateur.

### US-5 — Se connecter de façon sécurisée
**En tant qu'**utilisateur, **je veux** m'authentifier avec un compte personnel, **afin de** protéger l'accès aux données de l'entreprise.
- Critère 1 : mot de passe d'au moins 8 caractères exigé à l'inscription.
- Critère 2 : les routes de données refusent tout accès non authentifié (401).
- Critère 3 : les jetons d'accès expirent (1h) et sont renouvelables sans ressaisir le mot de passe.

### US-6 — Superviser l'état du système
**En tant qu'**administrateur, **je veux** consulter la santé du système et les statistiques d'usage des modèles IA, **afin de** détecter un problème avant qu'il n'affecte les utilisateurs.
- Critère 1 : `/api/health/` répond en moins de 500 ms.
- Critère 2 : `/api/ml/monitoring/` indique le taux d'échec et la latence moyenne par modèle.

## 4. Parcours utilisateur

Pas de wireframes graphiques (l'application est déjà codée, pas en phase de maquettage) : parcours utilisateur réel, ancré dans les écrans et rôles effectivement implémentés.

**Amine (technicien)**
1. `LoginPage` → authentification (JWT).
2. Redirection vers `DashboardPage` → lecture des KPI (taux de panne, interventions, coût cumulé).
3. Panneau *Prédiction de panne* (`PredictFailureForm`) → saisie des mesures capteur d'une machine → clic *Analyser le risque* → résultat coloré (probabilité + niveau de risque) affiché immédiatement.

**Sophie (gestionnaire de stock)**
1. `LoginPage` → `DashboardPage`.
2. Panneau *Prévision de demande de pièces* (`PredictDemandPanel`) → sélection d'une pièce → clic *Prévoir la demande* → demande prévue affichée.
3. Formulaire *Ajuster le stock* — visible uniquement pour son rôle (`gestionnaire_stock`/`admin`) — nouvelle valeur → confirmation.
4. Panneau *Recommandation* (`RecommendationPanel`) → lecture de la synthèse en langage naturel.

**Karim (administrateur)**
1. `LoginPage` → `DashboardPage` complet (accès à tous les panneaux, y compris l'ajustement de stock).
2. Supervision via `/api/health/` et `/api/ml/monitoring/` (statistiques d'usage des modèles).

Chaque étape correspond à un composant React réel et à un endpoint API réel — aucune étape de ce parcours n'est une intention non implémentée.

## 5. Exigences non fonctionnelles

- **Accessibilité** : labels explicites sur tous les champs de formulaire, régions nommées (`aria-labelledby`), messages d'erreur exposés via `role="alert"` (voir `src/frontend/src/pages` et `components`).
- **Sécurité** : voir `docs/rgpd.md` et top 10 OWASP pris en compte dans la conception de l'API (authentification obligatoire, validation stricte des entrées, pas de secret en dur).
- **Performance** : pagination systématique des listes (`PAGE_SIZE=20`).
- **Éco-conception** : choix d'un service IA gratuit et à faible latence (voir `docs/benchmark_ia.md`) plutôt qu'un modèle surdimensionné.

## 6. Hors périmètre (Phase A)

- Gestion multi-langue.
- Application mobile native.
- Paiement / facturation.
- Ces éléments ne sont pas nécessaires pour démontrer les compétences visées et sont explicitement exclus pour rester réaliste sur le temps disponible.
