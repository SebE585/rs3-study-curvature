# Référentiel de virages hybride : OSM + IGN + mesures terrain

## Introduction

Le référentiel de virages hybride est une approche innovante combinant plusieurs sources de données géographiques pour améliorer la précision et la fiabilité des analyses de courbure routière. En intégrant les données d’OpenStreetMap (OSM), de l’IGN (BDTopo), et des mesures terrain, ce référentiel vise à pallier les limites de chaque source prise isolément.

## Concept et intérêt

### Sources de données

- **OpenStreetMap (OSM)** : base collaborative mondiale, riche en informations mais parfois inégale en qualité et en précision.
- **IGN BDTopo** : données officielles françaises, précises et détaillées, mais moins fréquemment mises à jour.
- **Mesures terrain** : données collectées sur le terrain via GPS ou capteurs spécifiques, offrant une précision fine et des informations contextuelles.

### Avantages du référentiel hybride

- **Complémentarité** : OSM apporte une couverture large, IGN une précision topographique, et les mesures terrain une validation et correction locale.
- **Robustesse** : la fusion réduit les erreurs et les incohérences présentes dans chaque source.
- **Richesse des variables** : permet d’extraire des variables d’environnement plus fiables pour les études de courbure et de virages.

## Méthodologie

1. **Collecte des données** : récupération des données OSM via OSMnx, téléchargement des données IGN BDTopo, et acquisition des mesures terrain.
2. **Prétraitement** : filtrage des données, nettoyage, et harmonisation des formats.
3. **Fusion** : alignement géométrique des réseaux, intégration des attributs, et résolution des conflits.
4. **Extraction des variables** : calcul des courbures, angles, et autres métriques pertinentes.
5. **Validation** : comparaison avec données terrain pour évaluer la qualité du référentiel.

## Étapes futures

- **Automatisation du pipeline** : développement d’outils pour automatiser la fusion et l’analyse.
- **Extension géographique** : application à d’autres régions et pays.
- **Intégration de nouvelles sources** : comme les images satellites ou les données LIDAR.
- **Amélioration de la précision** : par des algorithmes de correction avancés et apprentissage machine.
- **Publication et partage** : mise à disposition du référentiel et des outils pour la communauté scientifique et les acteurs territoriaux.
