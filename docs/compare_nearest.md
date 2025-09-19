# 🔍 Comparaison par plus proches voisins — OSM vs BD TOPO

Analyse produite avec `tools/compare_nearest.py`.

| Metric              | count   | mean     | std     | min     | 25%     | 50%     | 75%     | max     |
|---------------------|---------|----------|---------|---------|---------|---------|---------|---------|
| diff_length_m       | 653 548 | -158.9 m | 230.9 m | -9933 m | -208 m  | -81 m   | -21 m   | 2145 m  |
| diff_radius_min_m   | 138 046 | 7.41e+07 | 4.73e+07| -5.33e9 | 6.79e+07| 9.04e+07| 9.37e+07| 9.37e+07|
| diff_curv_mean_1perm| 653 548 | -0.012   | 0.012   | -0.067  | -0.017  | -0.009  | -0.003  | 3.4e-07 |

- BD TOPO → longueurs plus grandes
- BD TOPO → courbure moyenne légèrement plus forte
- Rayons de courbure très différents (écarts énormes liés à la modélisation)

📂 Résultats CSV : `compare__nearest_diffs.csv`