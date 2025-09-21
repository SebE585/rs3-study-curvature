# 🔍 Comparaison par plus proches voisins — OSM vs BD TOPO

Cette analyse compare les données de OpenStreetMap (OSM) avec celles de BD TOPO en utilisant une méthode de plus proches voisins pour évaluer les différences sur plusieurs métriques.

| Metric               | Count    | Mean       | Std        | Min        | 25%         | 50%         | 75%         | Max         |
|----------------------|----------|------------|------------|------------|-------------|-------------|-------------|-------------|
| diff_length_m (m)    | 653 548  | -158.9     | 230.9      | -9933      | -208        | -81         | -21         | 2145        |
| diff_radius_min_m (m)| 138 046  | 7.41e+07   | 4.73e+07   | -5.33e9    | 6.79e+07    | 9.04e+07    | 9.37e+07    | 9.37e+07    |
| diff_curv_mean_1perm  | 653 548  | -0.012     | 0.012      | -0.067     | -0.017      | -0.009      | -0.003      | 3.4e-07     |

**Points clés de l'analyse :**

- **BD TOPO** → longueurs plus grandes
- **BD TOPO** → courbure moyenne légèrement plus forte
- Rayons de courbure très différents (écarts énormes liés à la modélisation)

📂 Résultats CSV :  
```
compare__nearest_diffs.csv
```