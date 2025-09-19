# Méthodologie

## Sources & emprise
- **Emprise** : WGS84 bbox (0.0, 48.9, 1.8, 50.1) → reprojetée en **EPSG:2154**.
- **Réseaux** : **BD TOPO® (troncon_de_route)** et **OSM** (réseau `driving` via `pyrosm`).
- **Option** : MNT pour la pente (désactivée dans cette passe).

## Pré-traitement géométrique
- **Simplification** (tolérance : 0.5 m)
- **Densification** (pas : 5 m)
- **Seuil longueur** (min_seg_len : 15 m)

## Courbure (par tronçon)
On construit un **profil de courbure** en parcourant la ligne densifiée, et pour chaque triplet de points \((p_{i-1}, p_i, p_{i+1})\), on calcule le **rayon** \(R_i\) du cercle circonscrit ; puis:
- `radius_min_m` : \(\min_i R_i\) (censuré par `clip_radius_min_m`)  
- `radius_p85_m` : \(P_{85}(R_i)\)  
- `curv_mean_1perm` : moyenne de \(1/R_i\) (avec capping par `clip_radius_min_m`)

Rappels :
\[
a_{lat}=\frac{v^2}{r}, \qquad \omega_z=\frac{v}{r}.
\]

## Appariement OSM ↔ BD TOPO
Pour comparer localement, on matche **au plus proche voisin** (centroïdes en EPSG:2154) côté BD :
- **Grille** carrée (cellule = `--max-dist`) pour accélérer la recherche.
- Option `--match-class` : seule la **même classe** (si disponible) peut matcher (`road_class` / `class` / `highway` / `nature`).

## Outils
- `tools/compare_quick.py` : résumé global + histogrammes (`--q`, `--drop-inf`).
- `tools/compare_nearest.py` : plus proche voisin (`--max-dist`, `--match-class`).
- `tools/make_gpkg_hotspots.py` : **GPKG** des plus gros écarts (`--metric`, `--top-n`).