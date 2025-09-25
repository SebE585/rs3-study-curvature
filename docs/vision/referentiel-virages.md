# Référentiel de virages hybride : OSM + IGN + mesures terrain

## Introduction

Le référentiel de virages hybride est une approche innovante combinant plusieurs sources de données géographiques pour améliorer la précision et la fiabilité des analyses de courbure routière. En intégrant les données d’OpenStreetMap (OSM), de l’IGN (BDTopo), et des mesures terrain, ce référentiel vise à pallier les limites de chaque source prise isolément.

## Enjeux scientifiques et industriels

La création d’un référentiel de virages précis et fiable répond à des enjeux majeurs dans plusieurs domaines. En sécurité routière, une meilleure connaissance des caractéristiques géométriques des routes permet d’identifier les zones à risque et d’adapter les dispositifs de prévention. Pour les systèmes avancés d’aide à la conduite (ADAS), ce référentiel offre une base solide pour la cartographie haute définition, essentielle à la navigation autonome. Dans le secteur de l’assurance, la modélisation fine des virages contribue à une meilleure évaluation des risques liés à la sinuosité des itinéraires. Enfin, les gestionnaires d’infrastructures peuvent optimiser la maintenance et la planification des travaux grâce à une meilleure compréhension des configurations routières.

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

### 1. Collecte des données

La collecte repose sur l’extraction des données OSM via la bibliothèque OSMnx, qui permet de récupérer facilement les graphes routiers selon des critères géographiques précis. Les données IGN BDTopo sont téléchargées à partir des portails officiels, offrant une couverture précise des réseaux routiers français. Enfin, les mesures terrain sont acquises via des dispositifs GPS haute précision ou des capteurs embarqués, fournissant des données géométriques fines et des informations contextuelles comme les conditions de la chaussée.

### 2. Prétraitement

Cette étape consiste à filtrer les données brutes pour éliminer les erreurs, à nettoyer les attributs et à harmoniser les formats entre les différentes sources. Par exemple, les données OSM sont souvent nettoyées pour supprimer les segments redondants ou mal géoréférencés. Les données IGN sont converties dans un système de coordonnées commun. Les mesures terrain sont corrigées pour compenser les erreurs de signal GPS. L’utilisation de bibliothèques comme GeoPandas facilite ces opérations de traitement spatial.

### 3. Fusion

La fusion des données vise à aligner géométriquement les différents réseaux routiers et à intégrer les attributs complémentaires. Cela implique la correspondance des segments proches entre OSM et IGN, la résolution des conflits d’attributs, et l’incorporation des corrections issues des mesures terrain. Des algorithmes de matching spatial et des techniques de géotraitement sont utilisés pour garantir une intégration cohérente. GeoPandas et Shapely sont souvent employés pour ces opérations.

### 4. Extraction des variables

Une fois le référentiel fusionné, diverses métriques sont calculées pour caractériser les virages : courbure, angle de virage, rayon de courbure, dénivelé, etc. Ces variables sont essentielles pour les analyses ultérieures. Des méthodes géométriques et statistiques sont appliquées pour extraire ces caractéristiques à partir des géométries des segments routiers.

### 5. Validation

La validation consiste à comparer les données fusionnées avec les mesures terrain, considérées comme la référence la plus fiable. Des indicateurs de qualité sont calculés, tels que l’écart moyen des positions, la cohérence des angles, ou la concordance des classes de virages. Cette étape permet d’évaluer la fiabilité du référentiel et d’identifier les zones nécessitant des corrections supplémentaires.

## Illustrations et résultats préliminaires

Les premières analyses ont permis de générer des cartes comparatives entre les données OSM et IGN, mettant en évidence les différences de précision et de couverture. Des statistiques par classe de virages ont été produites, illustrant la distribution des courbures et des angles sur différents territoires. Ces résultats préliminaires démontrent la valeur ajoutée de la fusion des sources et la pertinence du référentiel hybride pour des applications variées.

## Étapes futures

- **Automatisation du pipeline** : développement d’outils pour automatiser la fusion et l’analyse.
- **Extension géographique** : application à d’autres régions et pays.
- **Intégration de nouvelles sources** : comme les images satellites ou les données LIDAR.
- **Amélioration de la précision** : par des algorithmes de correction avancés et apprentissage machine.
- **Publication et partage** : mise à disposition du référentiel et des outils pour la communauté scientifique et les acteurs territoriaux.

## Perspectives applicatives

Le référentiel de virages hybride ouvre de nombreuses perspectives d’application. Il peut alimenter des simulateurs de conduite réalistes, en offrant des données géométriques précises pour la modélisation des trajectoires. En cartographie des risques, il permet d’identifier les zones à forte sinuosité susceptibles d’engendrer des accidents. En urbanisme, il contribue à la planification des infrastructures routières en intégrant des données fines sur la géométrie des routes. Enfin, dans le cadre des jumeaux numériques, ce référentiel constitue une base fiable pour la modélisation et la simulation des réseaux routiers dans un environnement virtuel.

## Conclusion

Le référentiel de virages hybride constitue une avancée majeure dans la modélisation géographique des routes, en combinant la richesse des données collaboratives, la précision des données officielles, et la finesse des mesures terrain. Cette approche permet de produire un référentiel robuste, adapté aux besoins croissants des domaines de la sécurité routière, de la conduite assistée, et de la gestion des infrastructures. Intégré dans le projet RoadSimulator3, ce référentiel joue un rôle clé pour améliorer la simulation et l’analyse des comportements routiers, contribuant ainsi à des routes plus sûres et mieux gérées.
