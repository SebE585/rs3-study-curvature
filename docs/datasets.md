# 📚 Jeux de données

## BD TOPO® — Transport
Tronçons de route fournis par l'IGN, comprenant des informations détaillées sur les segments routiers telles que la largeur, la vitesse autorisée, et la nature de la voie (route principale, secondaire, chemin, etc.). Ces données sont utilisées dans l’étude pour modéliser précisément le réseau routier et analyser les caractéristiques physiques des routes en lien avec la courbure.

## OpenStreetMap (OSM)
Données extraites au format `.osm.pbf` provenant de la source Geofabrik, couvrant la région Haute-Normandie. Le filtrage a été réalisé avec pyrosm pour isoler les tronçons routiers pertinents. Cette source offre une couverture ouverte et régulièrement mise à jour, bien que la précision et la complétude puissent varier localement. L’utilisation de ce format permet une intégration efficace dans les traitements SIG.

## MNT (RGE ALTI / Copernicus)
Modèles numériques de terrain avec différentes résolutions : 5 mètres pour le RGE ALTI de l’IGN, 25 mètres et 90 mètres pour les données Copernicus. Ces données sont essentielles pour calculer la pente et l’altitude des segments routiers, permettant ainsi une analyse topographique fine. Le RGE ALTI offre une précision plus élevée tandis que Copernicus fournit une couverture globale avec une résolution moindre.

## Jeux dérivés
Fichiers produits à partir des données brutes incluant des segments routiers enrichis avec des attributs topographiques, des profils de pente détaillés, ainsi que des statistiques agrégées par classe de route ou type de segment. Ces jeux facilitent l’analyse et la visualisation des résultats de l’étude.

## Métadonnées
Les métadonnées comprennent les millésimes des données, la taille des fichiers, ainsi que les hash SHA256 stockés pour assurer l’intégrité et la traçabilité des fichiers utilisés. Ces informations sont essentielles pour garantir la reproductibilité des analyses, comme détaillé dans [reproducibility.md](reproducibility.md).
