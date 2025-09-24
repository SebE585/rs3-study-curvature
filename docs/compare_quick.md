# 📊 Résultats rapides — Comparaison OSM vs BD TOPO

Cette analyse rapide a pour objectif de comparer les caractéristiques principales des segments issus des données OSM et BD TOPO, en mettant en évidence leurs différences en termes de longueur et de courbure.

Analyse produite avec `tools/compare_quick.py`.

| Source | N° Segments | Longueur Moyenne (m) | Longueur Médiane (m) | Longueur Totale (km) | Rayon Min P10 (m) | Rayon Min P50 (m) | Rayon Min P90 (m) | Courbure Moyenne Médiane |
|--------|-------------|----------------------|----------------------|---------------------|-------------------|-------------------|-------------------|--------------------------|
| osm    |   653 548   |               51.25  |               35.32  |           33 493    |    5.10e+07       |    9.37e+07       |    9.37e+07       |                   0.0000 |
| bdtopo |   456 874   |              172.16  |              107.44  |           78 653    |         15.0       |         29.9       |    6.99e+07       |                   0.0087 |

```
📂 Résultats CSV : compare__summary_segments.csv
📊 Figures histogrammes dans : assets/img/
```

En conclusion, les segments BD TOPO sont en moyenne plus longs et présentent une courbure moyenne plus élevée que ceux issus d'OSM, soulignant des différences notables dans la représentation géométrique des données.
