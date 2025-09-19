# Résultats

## Comptages et longueurs
| Source | # segments | Longueur moyenne (m) | Médiane (m) | Somme (km) |
|---|---:|---:|---:|---:|
| OSM | 653 548 | ~51,3 | ~35,3 | ~33 493 |
| BD TOPO | 456 874 | ~172,2 | ~107,4 | ~78 654 |

> OSM est **plus segmenté** (explode de `MultiLineString`) → longueurs moyennes inférieures.

## Distributions (clippées à q=0,99)
- `compare__hist_length_m.png`
- `compare__hist_radius_min_m.png`
- `compare__hist_curv_mean_1perm.png`

> Note : `--drop-inf` retire les rayons \(\infty\) (segments très rectilignes) dans les statistiques.

## Appariement par plus proche voisin
Résumé (OSM − BD), avec `--max-dist 30` et `--match-class` :
- **Δ longueur (m)** : médiane ≈ -81 m
- **Δ courbure moyenne (1/m)** : moyenne ≈ -0,012 (OSM légèrement plus « souple »)
- **Δ rayon min (m)** : très dispersé (forte hétérogénéité, valeurs extrêmes)

Les chiffres détaillés sont dans `compare__nearest_diffs.csv`.

## Cartographie des « hotspots »
Le fichier **GPKG** `compare__hotspots.gpkg` contient les \(N\) plus gros écarts (par \(|\text{metric}|\)).  
Utilisation typique : `--metric diff_curv_mean_1perm --top-n 5000`.

## Limites & suites
- Matching **spatial** (pas de topologie).  
- Classes de route hétérogènes entre sources.  
- Pente non activée dans cette passe.  

**Prochaines étapes** : activer la pente (DEM homogène), contraindre davantage le matching, et produire des cartes thématiques (1/R).