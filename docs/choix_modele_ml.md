# Choix de l'algorithme du modèle de prédiction de panne

Rapport dédié à la justification du choix d'algorithme pour le modèle maison de prédiction de panne (`src/ml/train_failure_model.py`), en réponse à une remarque de retour explicite : le choix de XGBoost n'était pas justifié par une comparaison chiffrée. Ce document comble ce manque.

## Lien avec la veille et la bibliographie (C6)

La veille technique ([`docs/veille.md`](veille.md)) documente une fourchette de précision **80 à 97 %** couramment observée pour des modèles de ML en maintenance prédictive, toutes sources confondues. Cette fourchette sert de repère de crédibilité ci-dessous : un résultat très en dehors de cette plage serait suspect (sous-apprentissage si trop bas, sur-apprentissage probable si trop haut sur un dataset aussi simple qu'AI4I 2020).

## Méthodologie de comparaison

Trois algorithmes candidats sont entraînés et évalués **sur exactement le même split train/test (75/25, `random_state=42`, stratifié) et le même préprocessing** (imputation médiane + standardisation des variables numériques, one-hot encoding de `type_produit`), pour que la comparaison soit équitable — pas de biais lié à un traitement différent des données selon l'algorithme :

- **Régression logistique** — modèle linéaire simple, sert de référence basse (baseline).
- **Random Forest** — ensemble d'arbres, robuste, souvent compétitif sans réglage fin.
- **XGBoost** — boosting de gradient, plus coûteux à régler mais généralement plus performant sur données tabulaires déséquilibrées.

Script reproductible : `python src/ml/train_failure_model.py` — génère et persiste automatiquement [`docs/ml_metrics.json`](ml_metrics.json) à chaque exécution (pas de chiffres recopiés à la main).

## Résultats réels (exécution du 08/08/2026, 10 000 lignes, 254 pannes sur 7 500 lignes d'entraînement)

| Algorithme | Accuracy | F1 Score | ROC-AUC | Precision | Recall |
|---|---|---|---|---|---|
| Régression logistique | 0.8252 | 0.2373 | 0.8836 | 0.1393 | 0.8000 |
| Random Forest | 0.9700 | 0.6193 | 0.9670 | 0.5446 | 0.7176 |
| **XGBoost (retenu)** | 0.9692 | **0.6516** | **0.9730** | 0.5294 | **0.8471** |

Les trois résultats se situent dans, ou très proche de, la fourchette 80-97 % de la veille (l'accuracy brute est même au-dessus, attendue sur un problème très déséquilibré où prédire "pas de panne" partout donnerait déjà ~96,6 % — d'où l'importance de juger sur F1/Recall, pas sur l'accuracy seule).

## Pourquoi XGBoost est retenu

L'**accuracy seule est trompeuse** ici : la classe "panne" représente à peine 3,4 % des lignes, donc un modèle qui prédit toujours "pas de panne" obtiendrait déjà ~96,6 % d'accuracy sans aucune valeur métier. Les métriques qui comptent réellement pour ce cas d'usage sont :

- **Recall** (rappel) : proportion de pannes réelles effectivement détectées. **C'est la métrique la plus critique du projet** — une panne non détectée coûte une intervention non planifiée, potentiellement un arrêt machine non anticipé. XGBoost obtient le meilleur recall (0.8471) : il détecte la plus grande part des pannes réelles.
- **F1 Score** : équilibre entre précision et rappel. XGBoost est aussi le meilleur (0.6516) — il ne sacrifie pas excessivement la précision pour obtenir ce recall.
- **ROC-AUC** : capacité de discrimination globale, indépendante du seuil choisi. XGBoost est légèrement en tête (0.9730).

La régression logistique est nettement écartée (F1 = 0.2373, beaucoup de fausses alertes malgré un recall correct) — elle sert uniquement de référence basse. Random Forest est compétitif mais reste derrière XGBoost sur les deux métriques qui comptent le plus pour ce projet (F1 et recall).

## Justification des hyperparamètres XGBoost retenus

| Hyperparamètre | Valeur | Justification |
|---|---|---|
| `n_estimators=300` | 300 arbres | Suffisant pour converger sur un dataset de 10 000 lignes sans temps d'entraînement excessif ; `eval_metric="logloss"` suit la convergence. |
| `learning_rate=0.05` | Faible | Compense le nombre d'arbres élevé — apprentissage progressif, réduit le risque de sur-apprentissage par rapport à un taux plus agressif. |
| `max_depth=4` | Peu profond | Limite la complexité de chaque arbre — avec seulement 5 variables numériques + 1 catégorielle, des arbres profonds sur-apprendraient le bruit plutôt que le signal. |
| `subsample=0.9`, `colsample_bytree=0.9` | 90 % | Sous-échantillonnage léger des lignes et colonnes à chaque arbre — réduit la variance, pratique standard pour limiter le sur-apprentissage sans perdre trop d'information. |
| `scale_pos_weight` | Calculé dynamiquement (`neg/pos`, ≈ 28.5 sur ce run) | **Pas une valeur fixe devinée** : recalculé à chaque entraînement à partir du vrai déséquilibre de classes du jeu d'entraînement (254 pannes sur 7 500 lignes) — pénalise davantage les faux négatifs, cohérent avec la priorité donnée au recall ci-dessus. |
| `random_state=42` | Fixe | Reproductibilité : le même split et le même entraînement redonnent les mêmes résultats. |

Aucun de ces hyperparamètres n'est une valeur par défaut recopiée sans réflexion : chacun répond à une caractéristique connue du dataset (fortement déséquilibré, peu de variables, volume modeste).

## Conclusion

XGBoost est retenu car il maximise le recall et le F1 score — les deux métriques directement liées à l'objectif métier (détecter le plus de pannes réelles possible sans multiplier excessivement les fausses alertes) — tout en restant dans la fourchette de précision documentée par la veille technique. Le choix est reproductible (`python src/ml/train_failure_model.py`) et vérifiable (`docs/ml_metrics.json`, régénéré à chaque exécution), pas une affirmation non sourcée.

## Explicabilité (SHAP) — ce que ça apporte de plus

**Le problème que XGBoost seul ne résout pas** : la probabilité de panne (`0.9989`, par exemple) dit *que* le risque est élevé, mais pas *pourquoi*. Un technicien qui doit décider quoi vérifier sur une machine a besoin de savoir quelle mesure capteur pousse le risque à la hausse — la température, l'usure de l'outil, le couple ? XGBoost ne répond pas à cette question tout seul.

**Ce que XGBoost fournit déjà, et sa limite** : `model.feature_importances_` donne une importance **globale** — "en moyenne, sur tout le dataset, telle variable compte beaucoup". Utile pour comprendre le modèle dans son ensemble, mais inutilisable pour une décision opérationnelle : elle ne dit rien sur *une machine précise, à un instant précis*.

**Ce que SHAP ajoute concrètement** : une explication **locale**, par prédiction individuelle. Pour une lecture capteur donnée, SHAP décompose la probabilité prédite en contribution de chaque variable, positive ou négative, avec un signe et une magnitude — pas juste un classement. Implémenté dans [`src/ml/explain.py`](../src/ml/explain.py) via `shap.TreeExplainer`, optimisé pour les modèles à base d'arbres (XGBoost) — beaucoup plus rapide que l'approche générique `KernelExplainer`.

**Exemple réel** (`python src/ml/explain.py`, référence AI4I #50, 08/08/2026) :
```
Reference AI4I #50 - probabilite de panne predite : 97.80%

Contributions SHAP (du plus au moins influent) :
  num__couple_nm                      +4.3832
  num__vitesse_rotation_rpm           +0.7692
  num__usure_outil_min                -0.6315
  num__temperature_air_k              -0.5740
  num__temperature_process_k          -0.4988
```

Pour **cette machine précise**, le couple (`couple_nm`) domine très largement les autres variables (+4.38, un ordre de grandeur au-dessus du reste) — c'est lui qui pousse la probabilité de panne à 97,8 %, pas la température. Sans SHAP, on saurait seulement "risque élevé" ; avec SHAP, on sait "vérifiez le couple en priorité sur cette machine". C'est cette réponse-là, actionnable et spécifique à un cas, que l'explicabilité apporte au-delà de la seule probabilité — et c'est directement exploitable par le panneau de recommandation (C8) ou par un technicien qui consulte le détail d'une alerte.
