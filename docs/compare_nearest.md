# 🔍 Comparaison par plus proches voisins — OSM vs BD TOPO

Cette analyse compare les données de OpenStreetMap (OSM) avec celles de BD TOPO en utilisant une méthode de plus proches voisins pour évaluer les différences sur plusieurs métriques.

| Metric               | Count    | Mean       | Std        | Min        | 25%         | 50%         | 75%         | Max         |
|----------------------|----------|------------|------------|------------|-------------|-------------|-------------|-------------|
| diff_length_m (m)    | 653 548  | -158.9     | 230.9      | -9933      | -208        | -81         | -21         | 2145        |
| diff_radius_min_m (m)| 138 046  | 7.41e+07   | 4.73e+07   | -5.33e9    | 6.79e+07    | 9.04e+07    | 9.37e+07    | 9.37e+07    |
| diff_curv_mean_1perm  | 653 548  | -0.012     | 0.012      | -0.067     | -0.017      | -0.009      | -0.003      | 3.4e-07     |

### Explication des métriques

- **diff_length_m (m)** : différence de longueur entre les segments appariés OSM et BD TOPO, en mètres. Une valeur négative indique que le segment BD TOPO est plus long que son homologue OSM.
- **diff_radius_min_m (m)** : différence du rayon minimal de courbure entre les segments appariés, en mètres. Des valeurs très grandes ou négatives peuvent indiquer des divergences importantes dans la modélisation des courbures.
- **diff_curv_mean_1perm** : différence de la courbure moyenne normalisée (permettant une comparaison sur une même échelle) entre les segments appariés.

---

**Points clés de l'analyse :**

- **BD TOPO** → longueurs plus grandes
- **BD TOPO** → courbure moyenne légèrement plus forte
- Rayons de courbure très différents (écarts énormes liés à la modélisation)

---

### 📊 Visualisations disponibles

Les graphiques suivants sont disponibles dans le dossier `out/plots` et illustrent les différences entre OSM et BD TOPO selon la méthode des plus proches voisins :

- Histogrammes des différences de longueur (`diff_length_hist.png`)
- Histogrammes des différences de rayon minimal de courbure (`diff_radius_min_hist.png`)
- Histogrammes des différences de courbure moyenne (`diff_curv_mean_hist.png`)
- Graphiques des quantiles des différences (`diff_length_quantiles.png`, `diff_radius_min_quantiles.png`, `diff_curv_mean_quantiles.png`)

---

### Interprétation

La tendance des segments BD TOPO à présenter des longueurs plus grandes peut s'expliquer par une segmentation plus fine ou des méthodes de cartographie différentes, où BD TOPO privilégie une représentation plus détaillée des axes routiers. La différence dans la courbure moyenne reflète aussi ces choix de modélisation, BD TOPO capturant des variations plus subtiles de la géométrie.

Les écarts importants sur les rayons minimaux de courbure traduisent des divergences dans la façon dont les courbures sont calculées ou modélisées, ainsi que la sensibilité aux petites erreurs de géométrie ou aux différences topologiques.

La méthode des plus proches voisins présente des limites : elle est sensible à la topologie locale et peut souffrir d'erreurs de "snapping" (appairage incorrect), ainsi que de différences dans la segmentation des axes entre les deux bases. Ces facteurs peuvent introduire des biais dans l'interprétation des différences.

---

### Perspectives

Cette comparaison constitue une première étape vers la construction d'une référence hybride de courbure combinant les forces des deux sources de données. Elle alimentera également les travaux de modélisation des clothoïdes et la production de statistiques globales sur les géométries routières. Une meilleure compréhension des différences permettra d'améliorer la qualité des données et des analyses ultérieures.

📂 Résultats CSV :
```
compare__nearest_diffs.csv
```
