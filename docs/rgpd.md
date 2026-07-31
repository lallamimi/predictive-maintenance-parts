# Registre des traitements de données personnelles (RGPD)

*Compétence C4. Document rédigé avant la création du modèle `User`, conformément à la démarche privacy-by-design.*

## Contexte

Ce projet est **fictif** (voir README) : aucune donnée réelle d'utilisateur, de client ou d'entreprise n'est traitée. Ce registre est néanmoins rédigé **comme si** l'application était mise en production, pour démontrer la compétence de mise en conformité RGPD exigée par le référentiel (C4).

## Données personnelles traitées

| Donnée | Modèle / champ | Finalité | Base légale |
|---|---|---|---|
| Nom d'utilisateur | `accounts.User.username` | Identification, authentification | Exécution du contrat (compte utilisateur) |
| Adresse e-mail | `accounts.User.email` | Communication, récupération de compte | Exécution du contrat |
| Mot de passe (haché) | `accounts.User.password` | Authentification | Exécution du contrat |
| Rôle métier | `accounts.User.role` | Contrôle d'accès (technicien / gestionnaire de stock / admin) | Intérêt légitime (sécurité applicative) |
| Prénom / nom (hérités d'`AbstractUser`) | `accounts.User.first_name`, `last_name` | Personnalisation de l'interface | Exécution du contrat |
| Historique de connexion | `accounts.User.last_login`, `date_joined` | Sécurité, traçabilité | Intérêt légitime |

**Aucune donnée personnelle sensible** (santé, opinions, données biométriques) n'est collectée. Les données de maintenance/pièces de rechange (interventions, capteurs) ne concernent pas des personnes physiques identifiables : elles sont exclues du périmètre RGPD.

## Durée de conservation

- Comptes utilisateurs : conservés tant que le compte est actif. Suppression à la demande de l'utilisateur (`DELETE /api/auth/profile/` — *à implémenter en Phase B*) ou après 3 ans d'inactivité.
- Jetons JWT : durée de vie limitée nativement (`ACCESS_TOKEN_LIFETIME` = 1h, `REFRESH_TOKEN_LIFETIME` = 7 jours, voir `config/settings.py`), révocables via `rest_framework_simplejwt.token_blacklist`.
- Logs applicatifs (`logs/app.log`) : rotation automatique (5 Mo, 3 fichiers max, voir `LOGGING` dans `config/settings.py`) — pas de conservation illimitée.

## Sécurité des données personnelles

- Mots de passe hachés (PBKDF2, comportement par défaut de Django), jamais stockés ni loggés en clair.
- Accès à l'API protégé par JWT (`DEFAULT_PERMISSION_CLASSES = IsAuthenticated`) : aucune donnée personnelle n'est accessible sans authentification.
- `SECRET_KEY` et clés d'API tierces (Groq) chargées depuis l'environnement (`.env`, non versionné), jamais en dur dans le code.
- CORS restreint à une liste blanche explicite d'origines (`CORS_ALLOWED_ORIGINS`), jamais de wildcard.

## Procédure de tri / suppression (à mettre en œuvre en Phase B)

1. Identification trimestrielle des comptes inactifs depuis plus de 3 ans (requête sur `last_login`).
2. Notification préalable à l'utilisateur (e-mail).
3. Anonymisation (username → `utilisateur_supprimé_<id>`, email vidé) plutôt que suppression physique, pour préserver l'intégrité référentielle des interventions historiques.
4. Journalisation de l'opération (qui, quand, quel compte) dans `logs/app.log`.

## Droits des personnes

Dans une mise en production réelle, les utilisateurs disposeraient d'un droit d'accès, de rectification (`PATCH /api/auth/profile/`) et de suppression de leurs données, conformément aux articles 15 à 17 du RGPD. Un point de contact (DPO ou responsable projet) serait désigné pour instruire ces demandes.
