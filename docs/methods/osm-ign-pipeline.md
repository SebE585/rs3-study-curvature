

# Pipeline technique de fusion OSM + IGN pour l’analyse de virages

## Introduction

Ce document détaille le pipeline technique permettant de fusionner les données OSM et IGN BDTopo, enrichies par des mesures terrain, pour créer un référentiel de virages hybride.

## Étapes du pipeline

### 1. Acquisition des données

- **OSM** : extraction via la bibliothèque Python [OSMnx](https://osmnx.readthedocs.io/en/stable/).
- **IGN BDTopo** : téléchargement des fichiers vectoriels depuis le portail officiel.
- **Mesures terrain** : import des fichiers GPS ou données capteurs au format standard.

### 2. Prétraitement

- Nettoyage des données (suppression des segments erronés, doublons).
- Projection dans un système de coordonnées commun (ex : Lambert 93).
- Filtrage spatial et thématique (ex : uniquement routes, exclusion des chemins piétonniers).

### 3. Fusion des données

- Alignement géométrique des réseaux via snapping et matching spatial.
- Fusion des attributs selon une hiérarchie de confiance (mesures terrain > IGN > OSM).
- Résolution des conflits et interpolation des segments manquants.

### 4. Extraction des variables d’environnement

- Calcul des courbures et angles de virage.
- Intégration des données contextuelles (pente, revêtement, visibilité).
- Génération de fichiers de sortie au format GeoJSON ou Shapefile.

## Commandes Makefile principales

```makefile
# Téléchargement des données OSM
download-osm:
	python scripts/download_osm.py --area "Nom_de_la_zone"

# Prétraitement des données IGN
preprocess-ign:
	python scripts/preprocess_ign.py --input data/ign_raw --output data/ign_clean

# Fusion des données
fuse-data:
	python scripts/fuse_osm_ign.py --osm data/osm_clean.geojson --ign data/ign_clean.geojson --output data/fused_network.geojson

# Extraction des variables
extract-variables:
	python scripts/extract_variables.py --input data/fused_network.geojson --output results/variables.csv
```

## Conclusion

Ce pipeline permet une exploitation optimale des données disponibles pour l’étude des virages, en combinant la richesse et la précision des différentes sources.
