# Paramétrage du service IA — Groq (C8)

## Besoin couvert

Transformer les indicateurs de stock/panne en recommandation lisible pour le gestionnaire (mission 7 du cahier des charges). Voir le choix argumenté dans [`benchmark_ia.md`](benchmark_ia.md).

## Environnement d'exécution

Backend Django/Python 3.11 (même environnement que le reste de l'API — pas de service séparé). Appel HTTP sortant vers `api.groq.com` via la librairie `requests`, déclenché par `GET /api/recommendations/`. Fichier de configuration exemple : [`src/backend/.env.example`](../src/backend/.env.example).

## Procédure d'installation

1. Créer un compte sur [console.groq.com](https://console.groq.com/) (gratuit).
2. Générer une clé API.
3. La renseigner dans `src/backend/.env` :
   ```
   GROQ_API_KEY=votre_cle
   ```
4. Aucune dépendance supplémentaire à installer (`requests` est déjà dans `requirements.txt`).

## Variables d'environnement

| Variable | Description | Obligatoire |
|---|---|---|
| `GROQ_API_KEY` | Clé API Groq | Non — si absente, l'endpoint bascule automatiquement sur une recommandation par règles (voir ci-dessous) |

## Procédure de test

```bash
curl -H "Authorization: Bearer <token JWT>" http://localhost:8000/api/recommendations/
```

**Résultat réel** (test exécuté le 04/08/2026, `GROQ_API_KEY` vide dans cet environnement — démontre le repli documenté ci-dessous) :
```json
{
  "source": "repli_regles",
  "contexte": {
    "taux_panne_pct": 3.39,
    "cout_total_interventions": 123105.04,
    "pieces_sous_seuil": []
  },
  "recommandation": "Aucune piece sous le seuil de reapprovisionnement. Taux de panne actuel : 3.39%. Situation stable."
}
```

## Données envoyées / reçues

- **Envoyées à Groq** : uniquement des agrégats numériques (taux de panne, coût cumulé, liste des pièces sous seuil avec leur nom). **Aucune donnée personnelle** n'est transmise au service tiers.
- **Reçues** : un texte libre en français (recommandation), aucune donnée structurée sensible.

## Limites, risques, coûts

- **Coût** : nul (offre gratuite Groq au moment du choix — à revérifier si le projet perdure, les conditions peuvent changer).
- **Risque de disponibilité** : si Groq est indisponible ou la clé absente, `recommendations/views.py` intercepte l'erreur et bascule sur `_recommandation_repli()`, une recommandation déterministe par règles — **l'endpoint ne renvoie jamais d'erreur 500 pour cette raison**, il dégrade proprement (`source: "repli_regles"` dans la réponse, journalisé en `logger.warning`).
- **Monitoring disponible** : chaque appel (succès ou repli) est loggé via le logger Python `recommendations` (config dans `config/settings.py`, voir aussi `docs/monitoring.md`).
- **Limite connue** : le modèle peut occasionnellement reformuler au-delà des chiffres fournis malgré la consigne système ("n'invente rien") — à vérifier manuellement avant utilisation en contexte réel non fictif.
