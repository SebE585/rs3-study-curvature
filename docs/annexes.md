Balayage en distance d\in\{20,30,50\}

for d in 20 30 50; do
  python tools/compare_nearest.py \
    --in-dir "/Users/sebastien.edet/rs3-data/ref/roadinfo" \
    --osm-name roadinfo_segments_osm.parquet \
    --bd-name  roadinfo_segments_bdtopo.parquet \
    --max-dist $d \
    --metrics "length_m,radius_min_m,curv_mean_1perm" \
    --drop-inf \
    --out-summary "/Users/sebastien.edet/rs3-data/ref/roadinfo/nearest_diffs_d${d}.csv" \
    --out-quantiles "/Users/sebastien.edet/rs3-data/ref/roadinfo/nearest_quants_d${d}.csv"
done

Diagnostics classes + comparaison contrainte (d=30 m)

# Diagnostics classes
python tools/compare_nearest.py \
  --in-dir "/Users/sebastien.edet/rs3-data/ref/roadinfo" \
  --osm-name roadinfo_segments_osm.parquet \
  --bd-name  roadinfo_segments_bdtopo.parquet \
  --max-dist 30 \
  --class-map configs/class_map.yml \
  --diag-classes \
  --out-class-stats "/Users/sebastien.edet/rs3-data/ref/roadinfo/compare__class_stats.csv"

# Contrainte de classe + exports
python tools/compare_nearest.py \
  --in-dir "/Users/sebastien.edet/rs3-data/ref/roadinfo" \
  --osm-name roadinfo_segments_osm.parquet \
  --bd-name  roadinfo_segments_bdtopo.parquet \
  --max-dist 30 \
  --match-class \
  --class-col-osm class \
  --class-col-bd  class \
  --class-map configs/class_map.yml \
  --metrics "length_m,radius_min_m,curv_mean_1perm" \
  --drop-inf \
  --out-summary  "/Users/sebastien.edet/rs3-data/ref/roadinfo/compare__nearest_diffs.csv" \
  --out-quantiles "/Users/sebastien.edet/rs3-data/ref/roadinfo/compare__nearest_quantiles.csv" \
  --out-matches  "/Users/sebastien.edet/rs3-data/ref/roadinfo/compare__nearest_matches.csv" \
  --keep-cols "highway_left,highway_right,maxspeed_left,maxspeed_right" \
  --per-class \
  --out-byclass  "/Users/sebastien.edet/rs3-data/ref/roadinfo/compare__nearest_byclass.csv" \
  --export-geo "/Users/sebastien.edet/rs3-data/ref/roadinfo/compare__nearest_links.gpkg"