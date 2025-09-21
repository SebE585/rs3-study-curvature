## Données & périmètre

- Emprise : bbox WGS84 `(0.0, 48.9, 1.8, 50.1)` reprojetée en EPSG:2154.
- Sources :
  - OSM (réseau routier « driving ») → extraction pyrosm + explode sur MultiLineString.
  - BD TOPO® (IGN) : couche troncon_de_route.
- Colonnes géométriques : centroïdes `x_centroid`, `y_centroid` (E/N en EPSG:2154) pour l’appariement et l’export des segments.

## Pré-traitement

- Nettoyage géométrique : simplification (0,5 m), densification (5 m), longueur min. 15 m.
- Calculs métriques (par tronçon) via notre pipeline :
  - Longueur `length_m`.
  - Rayon minimal `radius_min_m` (cercle par triplets successifs).
  - Courbure moyenne `curv_mean_1perm` (= moyenne de 1/r le long du tronçon).
  - *(Option)* Pente `slope_mean_pct` (MNT bilinéaire).

## Appariement spatial (nearest neighbor)

- Jointure `sjoin_nearest` (GeoPandas) OSM→BDTOPO par centroïdes, distance max \(\in \{20,30,50\}\,\mathrm{m}\).
- Contrainte de classe (option `--match-class`) après normalisation :
  - OSM : `highway` → normalisé (minuscules, accents retirés).
  - BD TOPO : `nature` → mappé vers des catégories OSM (ex. bretelle→motorway_link, route à 2 chaussées→trunk, chemin→track, etc.), puis normalisé.
  - Mapping fusionné : défaut + `configs/class_map.yml` (prioritaire).

## Calcul des écarts

Pour chaque métrique \(m \in \{\texttt{length\_m}, \texttt{radius\_min\_m}, \texttt{curv\_mean\_1perm}\}\) :

$$
\Delta m = m_{\mathrm{OSM}} - m_{\mathrm{BDTOPO}}
$$

- Option `--drop-inf` : censure des ±∞ dans `radius_min_m` avant calcul.
- Export :
  - Résumé (`describe`) : `compare__nearest_diffs.csv` (ou suffixes `nearest_diffs_d{20,30,50}.csv`).
  - Quantiles : `nearest_quants_d{20,30,50}.csv`.
  - *Appariements détaillés (facultatif)* : `compare__nearest_matches.csv` (+ `--keep-cols`).
  - *Stats par classe (facultatif)* : `compare__nearest_byclass.csv`.
  - *Segments géo OSM↔BD (facultatif)* : `compare__nearest_links.gpkg`.