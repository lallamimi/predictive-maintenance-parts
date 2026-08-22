# Benchmark de services d'intelligence artificielle (C7)

## Besoin reformulé

**Contexte métier** : le gestionnaire de stock et le technicien ont besoin de recommandations lisibles ("commander telle pièce sous 5 jours, stock critique") plutôt que de chiffres bruts.
**Entrées** : les KPI calculés par l'API (`/api/data/interventions/kpi/`, `/api/data/pieces/sous_seuil/`) et les prédictions du modèle IA.
**Sorties attendues** : un texte court en français, exploitable directement dans le tableau de bord.
**Contraintes** : projet fictif/étudiant → budget nul obligatoire, latence acceptable (< 5s), aucune donnée personnelle envoyée (uniquement des agrégats techniques), hébergement des données de préférence hors UE non recherché en priorité vu le fictif du projet mais évalué par principe, accessibilité (le texte généré doit rester lisible par un lecteur d'écran — texte brut, pas de mise en forme complexe).

**Critères de réussite** : réponse en moins de 5 secondes ; texte en français, cohérent avec les chiffres fournis en entrée (pas de valeur inventée) ; en cas d'indisponibilité du service, une réponse de repli est renvoyée sans jamais d'erreur 500 (vérifié — voir [`service_ia.md`](service_ia.md)).

## Services comparés

| Service | Fonctionnel | Technique | Coût | Risque | Monitoring possible | Décision |
|---|---|---|---|---|---|---|
| **Groq (Llama 3.3 70B)** | Fort — génération de texte de bonne qualité, respecte des consignes de format strictes (JSON, longueur) | Fort — API compatible OpenAI, SDK simple, latence très faible (inférence optimisée matériel LPU) | **Gratuit** (offre développeur généreuse au moment du choix) | Faible — offre gratuite pourrait évoluer, mais API stable et documentée | Oui — appel HTTP standard, facile à logger (implémenté, voir `service_ia.md`) | **Retenu** |
| **OpenAI (GPT-4o-mini)** | Fort — qualité de génération très bonne, large écosystème | Fort — documentation excellente, très utilisé donc bien supporté | Payant dès le premier appel (facturation à l'usage) | Moyen — risque budgétaire pour un projet sans financement | Oui — écosystème mature (dashboards d'usage natifs) | Alternative — écarté pour ce projet étudiant sans budget, à reconsidérer si le projet devient réel |
| **Mistral (mistral-small)** | Moyen à fort — bonne qualité en français (modèle européen), pertinent pour un contexte francophone | Fort — API simple, hébergement européen (avantage RGPD potentiel) | Offre gratuite limitée (quota bas), payant au-delà | Moyen — quota bas risque de bloquer le développement itératif | Oui — API HTTP standard, même principe que Groq | Alternative sérieuse — écarté principalement pour la limite de quota gratuit trop juste pour du test itératif pendant le développement |

## Raisons du choix

Groq est retenu pour trois raisons documentées :
1. **Coût nul**, contrainte non négociable pour ce projet étudiant.
2. **Latence très faible** (architecture LPU dédiée à l'inférence), avantage réel pour un endpoint appelé en direct par le tableau de bord (l'utilisateur ne doit pas attendre plusieurs secondes).
3. **API compatible OpenAI** : le code d'intégration reste portable — migrer vers OpenAI ou un autre fournisseur compatible ne demanderait qu'un changement d'URL de base et de clé, pas une réécriture (voir `src/backend/recommendations/groq_client.py`).

## Raisons d'écarter les autres

- **OpenAI** : qualité au moins équivalente, mais facturation dès le premier appel — incompatible avec un budget étudiant à zéro pour un projet fictif. À reconsidérer sérieusement si le projet devenait un vrai produit (meilleure maturité d'écosystème, support entreprise).
- **Mistral** : le plus proche concurrent sérieux (français/européen, pertinent RGPD), écarté uniquement pour une raison pratique de quota gratuit trop limité pour un développement itératif — pas un problème de qualité du service lui-même.

## Démarche éco-responsable

Aucun des trois fournisseurs ne publie de bilan carbone détaillé par requête accessible publiquement au moment de ce benchmark. Groq met en avant l'efficacité énergétique de son architecture LPU comparée aux GPU génériques, mais cette information provient du fournisseur lui-même (source non indépendante) et n'est donc pas retenue comme argument de poids dans la décision — seulement mentionnée par honnêteté de la démarche de benchmark.

## Suite

Paramétrage effectif documenté dans [`docs/service_ia.md`](service_ia.md) et code dans `src/backend/recommendations/`.
