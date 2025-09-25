# 📊 Résultats rapides — Comparaison OSM vs BD TOPO

Cette analyse rapide a pour objectif de comparer les caractéristiques principales des segments issus des données OSM et BD TOPO, en mettant en évidence leurs différences en termes de longueur et de courbure.

## 📐 Métriques comparées

Le tableau présente plusieurs métriques clés utilisées pour comparer les segments issus des deux sources de données :

- **Longueur** : mesure la distance linéaire du segment en mètres. Les valeurs moyenne, médiane et totale permettent d'appréhender la distribution et l'ampleur des segments.
- **Rayon Min P10, P50, P90** : représentent les percentiles 10, 50 (médian) et 90 du rayon minimal de courbure des segments, exprimés en mètres. Un rayon plus petit indique une courbure plus prononcée.
- **Courbure Moyenne Médiane** : valeur médiane de la courbure moyenne des segments, exprimée en inverse de mètres, qui donne une idée de la sinuosité générale des segments.

| Source | N° Segments | Longueur Moyenne (m) | Longueur Médiane (m) | Longueur Totale (km) | Rayon Min P10 (m) | Rayon Min P50 (m) | Rayon Min P90 (m) | Courbure Moyenne Médiane |
|--------|-------------|----------------------|----------------------|---------------------|-------------------|-------------------|-------------------|--------------------------|
| osm    |   653 548   |               51.25  |               35.32  |           33 493    |    5.10e+07       |    9.37e+07       |    9.37e+07       |                   0.0000 |
| bdtopo |   456 874   |              172.16  |              107.44  |           78 653    |         15.0       |         29.9       |    6.99e+07       |                   0.0087 |

## 🔍 Observations clés

- **Différences de granularité** : Les segments BD TOPO sont globalement plus longs, ce qui suggère une segmentation moins fine comparée à OSM.
- **Effets sur les statistiques de courbure** : La courbure moyenne médiane plus élevée dans BD TOPO reflète une meilleure capture des variations géométriques fines, tandis que les très grands rayons dans OSM indiquent des segments souvent quasi-linéaires.
- **Biais potentiels** : La différence dans la méthodologie de collecte et de traitement des données peut introduire des biais dans la comparaison, notamment en termes de précision géométrique et de définition des segments.

## 📈 Visualisations

Les figures disponibles dans `assets/img/` permettent d’illustrer ces différences et comprennent notamment :

- `compare__hist_length_m.png` : Histogramme des longueurs de segments, montrant la distribution et la granularité des données.
- `compare__hist_curv_mean_1perm.png` : Histogramme de la courbure moyenne, mettant en évidence la sinuosité des segments.
- `compare__hist_radius_min.png` : Distribution des rayons minimaux, illustrant les courbures extrêmes.
- `compare__scatter_length_vs_curv.png` : Nuage de points longueur vs courbure, pour analyser la relation entre ces deux métriques.

Ces visualisations apportent un éclairage complémentaire sur la nature des segments et leurs caractéristiques géométriques.

```
📂 Résultats CSV : compare__summary_segments.csv
📊 Figures histogrammes dans : assets/img/
```

## 📝 Conclusion et perspectives

L’analyse met en lumière des différences structurelles importantes entre les segments issus de BD TOPO et ceux d’OSM. En pratique, l’utilisation de BD TOPO est préférable lorsque la précision géométrique et la représentation fine de la sinuosité sont essentielles, notamment pour des applications nécessitant une modélisation détaillée des courbures. OSM, avec sa granularité plus fine mais des segments souvent plus linéaires, peut être adapté pour des analyses à plus grande échelle ou moins sensibles aux détails géométriques.

La suite de cette étude portera sur l’exploration des clothoïdes comme modèle pour la représentation des courbures continues, la réalisation de tests statistiques pour valider les différences observées, ainsi que le développement d’un référentiel hybride combinant les forces des deux sources pour une meilleure qualité des données géométriques.
