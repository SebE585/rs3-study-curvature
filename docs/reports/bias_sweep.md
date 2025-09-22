---
title: Sensibilité à la distance d’appariement
---

# Sensibilité à la distance d’appariement


## Résultats

L’analyse de sensibilité a évalué l’effet de la distance maximale d’appariement (20 m, 30 m, 50 m) sur les métriques comparées.

- **Taux d’appariement** :
  - 20 m → ~206k tronçons appariés.
  - 30 m → ~291k tronçons appariés.
  - 50 m → ~418k tronçons appariés.

- **Tendances observées** :
  - Plus la distance augmente, plus le nombre d’appariements croît, mais les écarts mesurés deviennent également plus importants.
  - La moyenne des différences de longueur s’accentue (−63 m à 20 m, −76 m à 30 m, −94 m à 50 m).
  - Les métriques de courbure et de rayon restent stables dans leur tendance mais montrent un bruit croissant.

## Visualisations

![Bias sweep longueur](../assets/reports/bias_sweep/quantiles_diff_length_m.png)
*Figure : évolution des quantiles des différences de longueur selon la distance d’appariement.*

![Bias sweep rayon](../assets/reports/bias_sweep/quantiles_diff_radius_min_m.png)
*Figure : évolution des quantiles des différences de rayon.*

![Bias sweep courbure](../assets/reports/bias_sweep/quantiles_diff_curv_mean_1perm.png)
*Figure : évolution des quantiles des différences de courbure.*

## Interprétation

Ces résultats montrent que :
- Une distance stricte (20 m) produit des comparaisons plus fiables mais sur un échantillon réduit.
- Une distance plus large (50 m) augmente la couverture mais introduit davantage de bruit et de faux positifs.
- Le compromis optimal dépend de l’objectif : précision locale vs couverture statistique.
