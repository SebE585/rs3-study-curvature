# 📊 Résultats rapides — Comparaison OSM vs BD TOPO

Analyse produite avec `tools/compare_quick.py`.

| source | n_segments | len_m_mean | len_m_median | len_m_sum_km | rmin_p10    | rmin_p50    | rmin_p90    | curv_mean_med |
|--------|------------|------------|--------------|--------------|-------------|-------------|-------------|---------------|
| osm    | 653 548    | 51.25 m    | 35.32 m      | 33 493 km    | 5.10e+07 m  | 9.37e+07 m  | 9.37e+07 m  | 0.000000      |
| bdtopo | 456 874    | 172.16 m   | 107.44 m     | 78 653 km    | 15.0 m      | 29.9 m      | 6.99e+07 m  | 0.008702      |

📂 Résultats CSV : `compare__summary_segments.csv`
📊 Figures histogrammes dans `assets/img/`.