# RAPPORT 2 : VEILLE TECHNIQUE, RÉGLEMENTAIRE ET BENCHMARK DE SERVICES IA
## Maintenance Prédictive & Optimisation des Pièces de Rechange Automobile

**Auteur** : Candidate Titre RNCP "Développeur en IA"  
**Établissement** : Simplon / ECE  
**Projet** : `predictive-maintenance-parts`  
**Évaluation** : Bloc 2 — Mise en situation E2 (Compétences C6, C7, C8)  
**Format** : Rapport thématique spécialisé (10 pages maximum)  

---

## TABLE DES MATIÈRES

1. **Organisation et Réalisation de la Veille Technique et Réglementaire (C6)**
   1.1. Thématique et méthode de suivi  
   1.2. Grille de fiabilité des sources  
   1.3. Synthèse des résultats et impacts sur le projet  
   1.4. Considérations réglementaires et transverses (AI Act, RGPD, Sécurité, Accessibilité)  
2. **Reformulation du Besoin IA & Spécifications Fonctionnelles (C7)**
   2.1. Contexte et expression du besoin reformulé  
   2.2. Entrées, Sorties et Contraintes  
   2.3. Critères de réussite  
3. **Matrice de Benchmark & Justification des Choix (C7)**
   3.1. Matrice comparative des services IA  
   3.2. Analyse approfondie du choix retenu (Groq / Llama 3.3 70B)  
   3.3. Justification explicite des solutions écartées (Non-choix : OpenAI & Mistral)  
   3.4. Évaluation éco-responsable  
4. **Paramétrage, Test et Résilience du Service IA (C8)**
   4.1. Environnement d'exécution et dépendances  
   4.2. Configuration et variables d'environnement  
   4.3. Sécurité des accès et minimisation des données  
   4.4. Procédure de test et résultat minimal réel (JSON HTTP 200 OK)  
   4.5. Mécanisme de résilience et de repli par règles (Fallback)  
   4.6. Chaîne de monitoring des appels  

---

## 1. ORGANISATION ET RÉALISATION DE LA VEILLE TECHNIQUE ET RÉGLEMENTAIRE (C6)

### 1.1. Thématique et Méthode de Suivi
Dans le cadre de la préparation du projet, une démarche de veille structurée a été mise en place sur la thématique suivante : **"Applications du Machine Learning à la maintenance prédictive industrielle et à l'optimisation des stocks de pièces détachées"**.

- **Organisation et Fréquence** : Recherche hebdomadaire planifiée d'une heure (chaque lundi), avec une mise à jour systématique du document de synthèse ([`docs/veille.md`](file:///d:/predictive-maintenance-parts/docs/veille.md)) à chaque évolution majeure.
- **Outils d'agrégation** : Consultation des bases scientifiques et industrielles (ArXiv, IEEE Xplore, rapports d'associations professionnelles et publications spécialisées).

### 1.2. Grille de Fiabilité des Sources
Pour éviter le piège d'une accumulation passive de liens sans évaluation, chaque source a été soumise à une grille d'analyse rigoureuse (Auteur, Date, Source primaire, Convergence, Accessibilité, Biais commercial) :

| Source | Auteur / Organisation | Date | Fiabilité | Motif de qualification & Conservation |
|---|---|---|---|---|
| **Industrial AI in Action** | A3 – Association for Advancing Automation (États-Unis) | 2026 | **Élevée** | Association professionnelle internationale du secteur. Contenu de référence sans intérêt commercial direct à vendre une solution spécifique. |
| **Machine Learning in Predictive Maintenance Guide** | AI Superior (Cabinet de conseil en IA) | 2026 | **Moyenne** | Contenu technique détaillé et de bonne qualité. Biais commercial identifié (cabinet de conseil) ➜ Nécessité de recouper les chiffres. |
| **How AI is Used in Predictive Maintenance** | Neural Concept (Éditeur de logiciels IA) | 2026 | **Moyenne** | Contenu spécialisé. Conservé car ses résultats recoupent exactement les deux autres sources (indice de convergence). |

### 1.3. Synthèse des Résultats & Impacts sur le Projet
La synthèse des publications étudiées a permis de fixer des repères réalistes pour calibrer le projet :
- **Transition réactif ➜ prédictif** : Confirmation de l'évolution du secteur vers l'anticipation pilotée par les données capteurs.
- **Performances cibles du modèle ML** : Les études démontrent que les modèles de détection de panne atteignent couramment **80 % à 97 % de précision**. Cela fixe un intervalle de validation strict pour nos propres modèles (XGBoost / RandomForest) : un score inférieur à 80 % signalerait un modèle insuffisant, tandis qu'un score supérieur à 97 % sur le dataset AI4I 2020 indiquerait un sur-apprentissage (overfitting).
- **Réduction des coûts de stock** : L'optimisation des pièces par IA permet une réduction de consommation de **10 à 20 %** et une économie globale de maintenance de **20 à 30 %**.

### 1.4. Considérations Réglementaires et Transverses
- **AI Act Européen (Règlement UE 2024/1689)** : Entré en vigueur en août 2024. Le système développé est un outil d'aide à la décision pour la maintenance et la gestion des stocks à usage interne, sans prise de décision autonome irréversible affectant une personne physique. Il relève d'une classification en **"Risque limité à minimal"**.
- **RGPD** : Les données capteurs industrielles et télémesures de machines sont des données techniques non personnelles, hors du périmètre du RGPD. Seuls les comptes d'accès utilisateurs (`User`) relèvent du RGPD (traité dans [`docs/rgpd.md`](file:///d:/predictive-maintenance-parts/docs/rgpd.md)).
- **Accessibilité & Sécurité** : Intégration dès la conception des critères WCAG (`aria-label`, `role="alert"`) et sécurisation des API par jetons JWT.

---

## 2. REFORMULATION DU BESOIN IA & SPÉCIFICATIONS FONCTIONNELLES (C7)

### 2.1. Contexte et Expression du Besoin
Le tableau de bord de maintenance restitue des métriques chiffrées et des indicateurs de stock. Cependant, les utilisateurs opérationnels (gestionnaire de stock, technicien) ont besoin de **recommandations décisionnelles synthétiques en langage naturel** (ex: *"Attention : Stock d'alternateurs sous le seuil critique. Commander 5 unités sous 48h"*), plutôt que d'analyser manuellement des tableaux de chiffres bruts.

### 2.2. Entrées, Sorties et Contraintes

- **Entrées transmises au service IA** : Les agrégats techniques calculés par l'API (`/api/data/interventions/kpi/`, `/api/data/pieces/sous_seuil/`) et le taux de défaillance global.
- **Sorties attendues** : Un texte court en français, directement exploitable dans le panneau de recommandation du tableau de bord.
- **Contraintes strictes du projet** :
  1. **Budget nul (0 €)** : Projet d'examen étudiant, aucune dépense d'API récurrente n'est possible.
  2. **Latence faible (< 5 secondes)** : L'inférence doit être rapide pour un affichage fluide sur le tableau de bord React.
  3. **Protection des données** : Aucune donnée personnelle ne doit être envoyée au service externe.
  4. **Accessibilité** : Le texte généré doit être lisible par un lecteur d'écran (texte brut sans balisage markdown complexe non vocalisable).

### 2.3. Critères de Réussite
- Réponse générée en moins de 5 secondes.
- Texte en français, strictement cohérent avec les chiffres transmis (0 hallucination).
- En cas d'indisponibilité du service réseau, une réponse de repli par règles déterministes est renvoyée sans jamais générer d'erreur HTTP 500.

---

## 3. MATRICE DE BENCHMARK & JUSTIFICATION DES CHOIX (C7)

### 3.1. Matrice Comparative des Services IA
Trois services d'IA générative ont été évalués selon 6 critères (Fonctionnel, Technique, Coût, Risque, Monitoring, Décision) :

| Service étudié | Qualité Fonctionnelle | Performance Technique | Coût & Quota | Risque & Sécurité | Monitoring | Décision |
|---|---|---|---|---|---|---|
| **Groq (Llama 3.3 70B)** | **Fort** (Respect du format et consignes) | **Fort** (Puces LPU, latence < 1s) | **Gratuit** (Offre dev généreuse) | **Faible** (API stable) | Oui (Logs HTTP) | **RETENU** |
| **OpenAI (GPT-4o-mini)** | **Fort** (Excellente qualité) | **Fort** (Large écosystème) | **Payant** (Facturation dès la 1ère requête) | **Moyen** (Risque budgétaire) | Oui (Dashboards natifs) | *Écarté (Payant)* |
| **Mistral AI (mistral-small)** | **Fort** (Excellente qualité en français) | **Fort** (Hébergement UE) | **Quota gratuit trop bas** | **Moyen** (Blocage dev) | Oui (API HTTP) | *Écarté (Quota)* |

### 3.2. Analyse Approfondie du Choix Retenu (Groq / Llama 3.3 70B)
Le service **Groq** a été retenu pour 3 raisons techniques majeures documentées dans [`docs/benchmark_ia.md`](file:///d:/predictive-maintenance-parts/docs/benchmark_ia.md) :
1. **Coût nul (0 €)** : Respect strict de la contrainte budgétaire du projet.
2. **Latence ultra-faible** : Grâce à l'architecture matérielle LPU (Language Processing Unit) dédiée à l'inférence, la réponse est obtenue en moins de 1 seconde.
3. **Portabilité et API compatible OpenAI** : Le client Python développé ([`src/backend/recommendations/groq_client.py`](file:///d:/predictive-maintenance-parts/src/backend/recommendations/groq_client.py)) utilise la structure standard OpenAI. Migrer vers un autre fournisseur ne demanderait qu'un changement d'URL de base et de clé d'API, sans réécriture de code.

### 3.3. Justification Explicite des Solutions Écartées (Non-Choix)
Le jury d'évaluation attend une justification explicite des solutions non retenues :
- **OpenAI (GPT-4o-mini)** : Écarté car la facturation au token est incompatible avec un budget d'examen à zéro euro. Solution à reconsidérer si le projet évoluait vers un produit commercial financé.
- **Mistral AI** : Pris en considération pour son ancrage européen et sa conformité RGPD native. Écarté uniquement pour une raison pratique : le quota de l'offre gratuite était trop rapidement épuisé lors des phases de tests itératifs intensifs.

### 3.4. Évaluation Éco-responsable
Aucun des trois fournisseurs ne publiant de bilan carbone détaillé et indépendant par requête au moment du benchmark, Groq met en avant l'efficacité énergétique des puces LPU par rapport aux GPU génériques. Cette donnée provenant du constructeur lui-même, elle a été prise en compte avec réserve et transparence.

---

## 4. PARAMÉTRAGE, TEST ET RÉSILIENCE DU SERVICE IA (C8)

### 4.1. Environnement d'Exécution & Dépendances
Le service est intégré au backend Django / Python 3.11. Il s'exécute lors des appels HTTP sortants vers `api.groq.com`, déclenchés par l'endpoint `GET /api/recommendations/`. Aucune dépendance surdimensionnée n'a été ajoutée (`requests` déjà présent dans `requirements.txt`).

### 4.2. Configuration & Variables d'Environnement
Conformément au fichier de configuration exemple [`src/backend/.env.example`](file:///d:/predictive-maintenance-parts/src/backend/.env.example), la clé d'accès est isolée :
```ini
GROQ_API_KEY=votre_cle_api_securisee
```
La clé d'API est exclue du gestionnaire de version Git pour éviter toute fuite de secret.

### 4.3. Sécurité des Accès & Minimisation des Données
- **Accès restreint** : L'endpoint `/api/recommendations/` exige une authentification par jeton JWT (`Bearer <access_token>`).
- **Minimisation des données** : Seuls des agrégats numériques anonymes (taux de panne, coût total, liste des noms de pièces sous seuil) sont transmis à Groq. **Aucune donnée personnelle n'est envoyée au service externe**.

### 4.4. Procédure de Test & Résultat Minimal Réel
Test effectué avec succès via commande HTTP :
```bash
curl -H "Authorization: Bearer <token_jwt>" http://localhost:8000/api/recommendations/
```

**Réponse HTTP 200 OK obtenue en environnement de test** :
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

### 4.5. Mécanisme de Résilience et de Repli par Règles (Fallback)
Pour garantir la continuité de service en cas de panne de réseau, d'épuisement de quota ou d'absence de la clé `GROQ_API_KEY`, l'application embarque un mécanisme de repli gracieux dans `recommendations/views.py` :
- Si l'appel à Groq échoue, l'exception est interceptée et la fonction `_recommandation_repli()` génère une recommandation déterministe par règles.
- **Résultat** : L'endpoint ne renvoie **jamais d'erreur HTTP 500**. L'attribut `"source": "repli_regles"` indique en toute transparence l'origine de la recommandation.

### 4.6. Monitoring des Appels
Chaque appel à l'API de recommandation (qu'il s'agisse d'un succès LLM ou d'un basculement sur le mode repli) est journalisé via le logger Python `recommendations.views` (configuré dans `config/settings.py` et documenté dans [`docs/monitoring.md`](file:///d:/predictive-maintenance-parts/docs/monitoring.md)).
