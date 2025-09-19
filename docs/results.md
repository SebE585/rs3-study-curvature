# 📊 Résultats

## Comptages et longueurs
| Source | # segments | Longueur moyenne (m) | Médiane (m) | Somme (km) |
|--------|------------|----------------------|-------------|------------|
| OSM    | 653 548    | 51,25                | 35,32       | 33 493     |
| BD TOPO| 456 874    | 172,16               | 107,44      | 78 654     |

## Distributions
![](assets/img/compare__hist_length_m.png)  
![](assets/img/compare__hist_radius_min_m.png)  
![](assets/img/compare__hist_curv_mean_1perm.png)

## Appariement « nearest neighbor »
- Δ longueur ≈ −159 m (OSM plus court)
- Δ courbure moyenne ≈ −0,012 1/m (OSM plus souple)
- Δ rayon minimal → valeurs extrêmes (segments rectilignes)

👉 Détails : [compare_quick.md](compare_quick.md) et [compare_nearest.md](compare_nearest.md).