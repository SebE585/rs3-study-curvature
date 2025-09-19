# Hotspots d’écarts OSM vs BD TOPO

## Méthodologie

Nous avons extrait les **5000 segments les plus divergents** entre OSM et BD TOPO selon la métrique `diff_curv_mean_1perm` (courbure moyenne).  
Les résultats sont exportés en **GeoPackage (`compare__hotspots.gpkg`)** et visualisés dans QGIS.

## Carte

📍 Exemple de visualisation des hotspots dans QGIS :  
*(capture d’écran à insérer ici)*

## Top 10 des écarts (illustratif)

| Rank | ID OSM | ID BD | Δ longueur (m) | Δ courbure (1/m) |
|------|--------|-------|----------------|------------------|
| 1    | osm_123 | bd_456 | -210.5 | -0.045 |
| 2    | osm_789 | bd_101 | -180.3 | -0.037 |
| 3    | osm_234 | bd_567 | -155.9 | -0.031 |
| …    | …       | …     | …              | …                |

## Utilisation

- **Diagnostic terrain** : cibler les tronçons où OSM est trop rectiligne ou trop fragmenté.  
- **Amélioration RS3** : enrichir les simulations inertielle avec un mix OSM+IGN.  
- **Feedback communauté OSM** : corriger manuellement certains tracés.  