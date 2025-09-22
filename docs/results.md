# Couverture des appariements sans contrainte de classe 📊

| Distance (m) | Nombre d’appariements | Total segments OSM |
|-------------:|---------------------:|-------------------:|
|          20  |              206 264 |           653 548  |
|          30  |              291 090 |           653 548  |
|          50  |              417 688 |           653 548  |

---

# Écarts globaux OSM − BDTOPO sans contrainte de classe (`--drop-inf`) 📈

## Résumé des écarts par distance

| Distance (m) | Δ longueur moyenne (m) | Δ longueur médiane (m) | Δ courbure moyenne (1/m) | Δ rayon minimal moyen (×10^7 m) |
|-------------:|-----------------------:|-----------------------:|-------------------------:|-------------------------------:|
|          20  |                −62,88  |                −26,66  |                 −0,01223 |                          6,88  |
|          30  |                −75,58  |                −36,71  |                 −0,01262 |                          7,03  |
|          50  |                −93,86  |                −49,82  |                 −0,01268 |                          7,17  |

### Synthèse

Augmenter la distance d’appariement augmente nettement le nombre de segments couverts. Cependant, cela engendre un biais croissant sur la longueur (OSM plus court) et une courbure moyenne plus faible côté OSM, indiquant une simplification ou une rectilinéarité accrue des segments.

---

# Effet de la contrainte de classe avec `--match-class` et `--class-map` 🎯

| Indicateur            | Moyenne          |
|----------------------|-----------------:|
| Nombre d’appariements |           9 282  |
| Δ longueur (m)        |      −106,73     |
| Δ courbure moyenne    |       −0,00662   |
| Δ rayon minimal (×10^7 m) |      6,59     |

### Synthèse

La contrainte de classe améliore l’homogénéité fonctionnelle entre réseaux, réduisant l’écart de courbure. En revanche, le biais sur la longueur s’accentue, reflétant des différences dans la segmentation et la modélisation.

---

# Sensibilité à la distance d 🔍

Les fichiers de quantiles générés (*nearest_quants_d20.csv*, *nearest_quants_d30.csv*, *nearest_quants_d50.csv*) montrent que :

- Les médianes de Δ longueur sont toujours négatives (OSM plus court).
- Les distributions présentent des queues asymétriques, avec des valeurs négatives importantes dues à des découpages BDTOPO moins segmentés.
- Le nombre d’appariements augmente avec la distance d (de 206 264 à 417 688).
- Les quantiles utilisés sont 0.10, 0.25, 0.50, 0.75 et 0.90, configurables selon les besoins, offrant une meilleure granularité dans l’interprétation.

---

# Fichiers produits (exemples) 📁

- [x] Résumés (sans contrainte) : *nearest_diffs_d20.csv*, *nearest_diffs_d30.csv*, *nearest_diffs_d50.csv*  
- [x] Quantiles : *nearest_quants_d{20,30,50}.csv*  
- [x] Contraintes de classe (d=30 m) : *compare__nearest_diffs.csv*, *compare__nearest_quantiles.csv*, *compare__nearest_matches.csv*, *compare__nearest_byclass.csv*, *compare__nearest_links.gpkg*  
- [x] Diagnostics classes : *compare__class_stats.csv*  

---

# Bandes de quantiles selon la distance de rapprochement 📉

![Différence de longueur en fonction de la distance d](assets/img/quantiles/quantiles_diff_length_m.png)  
*Figure 1 : Différence de longueur*

![Différence du rayon minimal en fonction de la distance d](assets/img/quantiles/quantiles_diff_radius_min_m.png)  
*Figure 2 : Différence du rayon minimal*

![Différence de la courbure moyenne en fonction de la distance d](assets/img/quantiles/quantiles_diff_curv_mean_1perm.png)  
*Figure 3 : Différence de la courbure moyenne*

---

# Implications produit et marché 🚀

Les résultats renforcent la valeur du simulateur **RoadSimulator3**, illustrant sa capacité à quantifier objectivement les écarts entre bases de données routières. Cette analyse structurelle soutient la validation, l’alignement et l’amélioration des données cartographiques utilisées dans de nombreux secteurs.

### Applications directes

- Validation et alignement de bases cartographiques hétérogènes (OSM, BD TOPO, autres)  
- Génération de jeux de données synthétiques pour entraîner des algorithmes de navigation  
- Benchmark indépendant pour assureurs, collectivités et start-ups mobilité  
- Support scientifique pour publications et communications  

### Documents associés

- *Elevator Speech - RoadSimulator3.pdf* : simulateur inertiel réaliste, fusion GPS/IMU, génération de trajectoires synthétiques à 10 Hz  
- *Business Model Canvas* : création de valeur pour assureurs, constructeurs et smart cities

---

# Résultats statistiques globaux 📊

Les tests statistiques (Welch t-test, Kolmogorov–Smirnov, Mann–Whitney) ont été appliqués aux métriques principales.

| Metric      | n_osm   | n_bd    | mean_osm | mean_bd | std_osm | std_bd | diff_mean | t_welch | p_t_welch | ks_stat | p_ks | mw_stat | p_mw | cohens_d | cliffs_delta |
|-------------|--------:|--------:|---------:|--------:|--------:|-------:|----------:|--------:|----------:|--------:|-----:|--------:|-----:|---------:|-------------:|
| length_m    | 456 874 | 456 874 | 51.93    | 172.16  | 53.57   | 199.54 | −120.23   | −393.34 | 0.0       | 0.465   | 0.0  | 4.20e10  | 0.0  | −0.82    | −0.60        |

*Tableau 1 : Exemple de résultats statistiques globaux.*

---

# Distributions globales 📈

![Distribution globale des longueurs](assets/reports/global_20250922_095722/length_m__hist_kde.png)
*Figure 4 : Distribution des longueurs (OSM vs BD TOPO).*  

![Boxplot global des longueurs](assets/reports/global_20250922_095722/length_m__box.png)
*Figure 5 : Boxplot des longueurs.*

---

# Résultats par classe 🛣️

Les distributions et statistiques sont également produites par classe normalisée de route.

Exemple :
- motorway, trunk, primary, secondary…

Voir toutes les figures par classe dans le **Rapport par classe** : [reports/curvature_by_class.md](reports/curvature_by_class.md).

---

# Bias sweep (distance max d’appariement) 🔍

Les analyses de sensibilité montrent l’effet de la distance max sur les écarts observés.

![Bias sweep longueur](assets/reports/bias_sweep/quantiles_diff_length_m.png)
*Figure 7 : Bias sweep — longueur.*

![Bias sweep rayon minimal](assets/reports/bias_sweep/quantiles_diff_radius_min_m.png)
*Figure 8 : Bias sweep — rayon minimal.*

![Bias sweep courbure](assets/reports/bias_sweep/quantiles_diff_curv_mean_1perm.png)
*Figure 9 : Bias sweep — courbure.*