## 🌍 Données & périmètre

| Élément                | Description                                                                                      |
|:-----------------------|:------------------------------------------------------------------------------------------------|
| **Emprise**            | bbox WGS84 `(0.0, 48.9, 1.8, 50.1)` reprojetée en `EPSG:2154`.                                |
| **Sources**            | - **OSM** (réseau routier *driving*) : extraction **pyrosm** + `explode` sur `MultiLineString`.<br>- **BD TOPO® (IGN)** : couche `troncon_de_route`. |
| **Colonnes géométriques** | Centroïdes `x_centroid`, `y_centroid` (*E/N en EPSG:2154*) pour appariement et export.          |

---

## 🛠️ Pré-traitement

- **Nettoyage géométrique** :
  - Simplification (*tolérance 0,5 m*)
  - Densification (*pas de 5 m*)
  - Suppression des tronçons < 15 m

| Métrique                | Description                                         |
|:------------------------|:---------------------------------------------------|
| `length_m`              | **Longueur**                                       |
| `radius_min_m`          | **Rayon minimal** (cercle par triplets successifs) |
| `curv_mean_1perm`       | **Courbure moyenne** (*moyenne de 1/r le long du tronçon*) |
| *(Optionnel)* `slope_mean_pct` | **Pente moyenne** (MNT bilinéaire)                  |

---

## 🔗 Appariement spatial (nearest neighbor)

- **Jointure** : `sjoin_nearest` (GeoPandas) **OSM → BD TOPO** par centroïdes
- **Distance max** : **20, 30, 50 m**
- **Contrainte de classe** (`--match-class`) après normalisation :
  - **OSM** : `highway` (normalisé : minuscules, accents retirés)
  - **BD TOPO** : `nature` mappé vers catégories OSM (ex. bretelle → motorway_link, route à 2 chaussées → trunk, chemin → track), puis normalisé
  - **Mapping fusionné** : défaut + `configs/class_map.yml` (**prioritaire**)

---

## 📊 Calcul des écarts

Pour chaque métrique \( m \in \{\texttt{length\_m}, \texttt{radius\_min\_m}, \texttt{curv\_mean\_1perm}\} \) :

\[
\Delta m = m_{\mathrm{OSM}} - m_{\mathrm{BDTOPO}}
\]

- **Option** `--drop-inf` : censure des ±∞ dans `radius_min_m` avant calcul

- **Exports** :

| Export                                | Description                                              |
|:-------------------------------------|:---------------------------------------------------------|
| **📄 Résumé (`describe`)**            | Fichier *_compare__nearest_diffs.csv_* (suffixes *_nearest_diffs_d{20,30,50}.csv_ possibles) |
| **📊 Quantiles**                      | Fichier *_nearest_quants_d{20,30,50}.csv_*              |
| **🗂️ Appariements détaillés** (`--keep-cols`) | Fichier *_compare__nearest_matches.csv_*                |
| **📑 Stats par classe**               | Fichier *_compare__nearest_byclass.csv_*                 |
| **🌐 Segments géo OSM↔BD**           | Fichier *_compare__nearest_links.gpkg_*                  |

---

## 📈 Analyses statistiques

- **Comparaison globale** :
  - Tests de normalité implicites remplacés par des tests robustes non paramétriques.
  - **Welch t-test** (moyennes, distributions à variances différentes).
  - **Kolmogorov–Smirnov (KS)** (différences de distribution).
  - **Mann–Whitney U** (distribution des rangs).

- **Mesures d’effet** :
  - **Cohen’s d** (taille d’effet standardisée, sensible aux distributions normales).
  - **Cliff’s delta** (mesure robuste de dominance entre distributions).

- **Par classe de route** :
  - Analyses répétées pour chaque catégorie normalisée (`motorway`, `trunk`, `primary`, `secondary`, etc.).
  - Visualisations par boxplots et violon plots.

- **Exploration des biais** :
  - Effet de la distance d’appariement (20 m / 30 m / 50 m).
  - Influence potentielle de la typologie (urbain vs rural), vitesses maximales et pente.