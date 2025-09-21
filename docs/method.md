## 🌍 Données & périmètre

- **Emprise** : bbox WGS84 `(0.0, 48.9, 1.8, 50.1)` reprojetée en `EPSG:2154`.
- **Sources** :
  - **OSM** (réseau routier *driving*) → extraction **pyrosm** + `explode` sur `MultiLineString`.
  - **BD TOPO® (IGN)** : couche `troncon_de_route`.
- **Colonnes géométriques** : centroïdes `x_centroid`, `y_centroid` (*E/N en EPSG:2154*) pour l’appariement et l’export des segments.

---

## 🛠️ Pré-traitement

- **Nettoyage géométrique** :
  - simplification (*tolérance 0,5 m*),
  - densification (*pas de 5 m*),
  - suppression des tronçons < 15 m.
- **Calculs métriques (par tronçon)** via notre pipeline :
  - `length_m` → **Longueur**.
  - `radius_min_m` → **Rayon minimal** (cercle par triplets successifs).
  - `curv_mean_1perm` → **Courbure moyenne** (*= moyenne de 1/r le long du tronçon*).
  - *(Optionnel)* `slope_mean_pct` → **Pente moyenne** (MNT bilinéaire).

---

## 🔗 Appariement spatial (nearest neighbor)

- **Jointure** : `sjoin_nearest` (GeoPandas) **OSM → BD TOPO** par centroïdes.
- **Distance max** : `20, 30, 50 m`.
- **Contrainte de classe** (`--match-class`) après normalisation :
  - **OSM** : `highway` → normalisé (*minuscules, accents retirés*).
  - **BD TOPO** : `nature` → mappé vers des catégories OSM  
    *(ex. bretelle → motorway_link, route à 2 chaussées → trunk, chemin → track...)*, puis normalisé.
  - **Mapping fusionné** : défaut + `configs/class_map.yml` (**prioritaire**).

---

## 📊 Calcul des écarts

Pour chaque métrique \( m \in \{\texttt{length\_m}, \texttt{radius\_min\_m}, \texttt{curv\_mean\_1perm}\} \) :

$$
\Delta m = m_{\mathrm{OSM}} - m_{\mathrm{BDTOPO}}
$$

- **Option** `--drop-inf` : censure des ±∞ dans `radius_min_m` avant calcul.
- **Exports** :
  - 📄 Résumé (`describe`) : `compare__nearest_diffs.csv`  
    *(ou suffixes `nearest_diffs_d{20,30,50}.csv`)*.
  - 📊 Quantiles : `nearest_quants_d{20,30,50}.csv`.
  - 🗂️ *Appariements détaillés* (option `--keep-cols`) : `compare__nearest_matches.csv`.
  - 📑 *Stats par classe* : `compare__nearest_byclass.csv`.
  - 🌐 *Segments géo OSM↔BD* : `compare__nearest_links.gpkg`.