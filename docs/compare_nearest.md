# Comparaison locale par plus proches voisins (OSM vs BD TOPO)

## Méthode
- Centroïdes des segments (EPSG:2154) enregistrés dans les tables ETL.
- Index **grille** (cellule = `--max-dist`) pour récupérer des candidats BD autour d’un point OSM.
- Si `--match-class` est activé, on n’accepte que les candidats de **même classe** (`road_class` / `class` / `highway` / `nature`).

## Commandes
```bash
python tools/compare_nearest.py \
  --in-dir /Users/.../ref/roadinfo \
  --osm-name roadinfo_segments_osm.parquet \
  --bd-name  roadinfo_segments_bdtopo.parquet \
  --max-dist 30 \
  --match-class