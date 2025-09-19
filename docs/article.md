# Comparaison de la courbure routière : BD TOPO vs OSM (Haute-Normandie)

## Résumé
Nous comparons des métriques de courbure et de pente dérivées de deux sources routières (BD TOPO® et OpenStreetMap) en Haute-Normandie (Eure + Seine-Maritime). Nous décrivons la chaîne de calcul, analysons les distributions et quantifions les écarts par appariement spatial.

## Données
- **Emprise** : bbox WGS84 (0.0, 48.9, 1.8, 50.1), reprojetée en EPSG:2154.
- **BD TOPO®** : `troncon_de_route.gpkg`, couche `troncon_de_route`.
- **OSM** : PBF régional Haute-Normandie filtré conduite (« driving ») via `pyrosm`.
- **MNT** : non utilisé dans cette passe (pente désactivée).

## Méthodes
1. **Nettoyage & chargement**
   - OSM : construction du réseau `pyrosm` → explode sur `MultiLineString`, filtrage type de voies, reprojection EPSG:2154.
   - BD TOPO® : lecture `pyogrio` avec bbox en L93.

2. **Pré-traitement géométrique**
   - Simplification (tolérance 0,5 m), densification (pas 5 m), longueur minimale 15 m.

3. **Métriques**
   - Profil de courbure (rayons locaux par triplets), statistiques par tronçon : `radius_min_m`, `radius_p85_m`, `curv_mean_1perm`.
   - (Optionnel) Pente depuis MNT.

4. **Comparaisons**
   - **Résumé global** des distributions (avec clipping au quantile 0,99 pour les figures).
   - **Appariement spatial** : plus proche voisin OSM→BD TOPO via centroïdes en EPSG:2154, écarts par métrique.

## Résultats

### Comptages et longueurs
| Source | # segments | Longueur moyenne (m) | Médiane (m) | Somme (km) |
|---|---:|---:|---:|---:|
| OSM | 653 548 | 51,25 | 35,32 | 33 493 |
| BD TOPO | 456 874 | 172,16 | 107,44 | 78 654 |

> Remarque : OSM est **plus segmenté** (explode) → longueurs moyennes plus faibles.

### Distributions (clippées à q=0,99)
![](../rs3-data/ref/roadinfo/compare__hist_length_m.png)
![](../rs3-data/ref/roadinfo/compare__hist_radius_min_m.png)
![](../rs3-data/ref/roadinfo/compare__hist_curv_mean_1perm.png)

### Appariement « nearest neighbor »
Résumé des différences OSM − BD TOPO (par centroïde, 1 voisin) :

- **Δ longueur (m)** : moyenne ≈ −159, médiane ≈ −81 (OSM plus court par segment).
- **Δ curv_mean (1/m)** : moyenne ≈ −0,012 (OSM plus “souple” en moyenne).
- **Δ radius_min (m)** : fortement hétérogène, avec valeurs extrêmes (inf / très grands rayons). Les infinis sont liés aux segments quasi rectilignes.

(Chiffres détaillés dans `compare__nearest_diffs.csv`.)

## Discussion
- La segmentation fine d’OSM amplifie les différences de longueur segmentaire, sans forcément refléter une différence réelle de linéaire.
- Les statistiques de courbure montrent une tendance à des rayons minimaux plus grands côté OSM (segments souvent plus courts et simplifiés).
- Les valeurs infinies pour `radius_min_m` doivent être traitées (p. ex. censure à `clip_radius_min_m`, exclusion des infinis pour certaines analyses).

## Limites
- **Pas de matching topologique** (uniquement le plus proche voisin spatial).
- **Pas de contrainte de classe** (motorway vs motorway, etc.) dans l’appariement actuel.
- **Pente** non activée (pas de MNT sérialisé pour cette passe).

## Travaux futurs
- Appariement avec contrainte de classe + distance max (ex. ≤ 30 m).
- Production d’un **GPKG hotspots** des plus gros écarts pour inspection terrain.
- Activation de la pente avec MNT homogène (EPSG:2154).
- Benchmarks de performance (pyrosm, explode, profil de courbure).

## Reproductibilité
- `configs/config.yaml` (multi-run OSM + BDTOPO).
- `tools/compare_quick.py` → `compare__summary_segments.csv` + PNG.
- `tools/compare_nearest.py` → `compare__nearest_diffs.csv`.