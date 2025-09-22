---
title: Rapport comparatif OSM vs BD TOPO
date: 2025-09-22 10:31:01
---

# Rapport comparatif OSM vs BD TOPO

_Généré automatiquement le 2025-09-22 10:31:01_

## Points saillants
- **length_m** : effet fort (Cohen d=-0.82), KS=0.465, Δmoy=-120.226 ↓

Ces résultats illustrent les premiers écarts globaux mesurés entre OSM et BD TOPO.
Ils doivent être interprétés à la lumière des analyses par classe et des explorations de biais
(détaillées dans les autres rapports : [Rapport par classe](curvature_by_class.md), [Bias sweep](bias_sweep.md)).

## Résultats statistiques globaux

| metric   |   n_osm |   n_bd |   mean_osm |   mean_bd |   diff_mean |   t_welch |   p_t_welch |   ks_stat |   p_ks |     mw_stat |   p_mw |   cohens_d |   cliffs_delta |
|:---------|--------:|-------:|-----------:|----------:|------------:|----------:|------------:|----------:|-------:|------------:|-------:|-----------:|---------------:|
| length_m |  456874 | 456874 |    51.9304 |   172.157 |    -120.226 |  -393.335 |           0 |  0.465397 |      0 | 4.20483e+10 |      0 |  -0.822962 |      -0.597111 |

## Distributions graphiques

Les figures suivantes montrent les distributions de la longueur des segments (OSM vs BD TOPO).
On observe une différence systématique de moyenne et de dispersion, confirmée par les tests statistiques.

### Longueur (m)

![length_m hist](../assets/reports/global_20250922_095722/length_m__hist_kde.png)
![length_m box](../assets/reports/global_20250922_095722/length_m__box.png)
![length_m violin](../assets/reports/global_20250922_095722/length_m__violin.png)
