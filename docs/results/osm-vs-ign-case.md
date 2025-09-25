# Étude de cas : Rue Blingue – comparaison OSM vs IGN

## Contexte

La Rue Blingue, située en zone urbaine dense, a été choisie comme terrain d’étude pour comparer la qualité et la précision des données issues de deux référentiels géographiques majeurs : OpenStreetMap (OSM) et l’IGN BDTopo. Cette comparaison vise à évaluer la pertinence de chaque source dans l’analyse des virages, un élément clé pour la modélisation de la géométrie routière et des dynamiques de trafic.

## Méthodologie

L’approche méthodologique adoptée comprend plusieurs étapes détaillées :

- Extraction des réseaux routiers OSM et IGN pour la zone d’étude, en veillant à harmoniser les formats et projections géographiques.
- Filtrage des données pour ne conserver que les segments routiers pertinents, notamment ceux accessibles aux véhicules légers.
- Identification des virages à partir des géométries linéaires, en appliquant une méthode basée sur la décomposition en clothoïdes pour modéliser la variation progressive de la courbure.
- Calcul des métriques de courbure et des angles de virage à chaque point critique détecté, en utilisant des algorithmes adaptés pour réduire le bruit et les erreurs de mesure.
- Application d’un buffer spatial autour des segments pour permettre la comparaison spatiale des virages détectés entre les deux sources, en tenant compte des décalages géométriques possibles.
- Analyse statistique descriptive des virages extraits, suivie d’une cartographie comparative pour visualiser les zones de concordance et de divergence.

## Résultats

### Statistiques descriptives

| Source | Nombre de virages | Courbure moyenne (°) | Écart-type |
|--------|-------------------|---------------------|------------|
| OSM    | 45                | 23.5                | 7.8        |
| IGN    | 52                | 25.1                | 6.2        |

Les résultats montrent que l’IGN détecte un nombre plus élevé de virages, avec une courbure moyenne légèrement supérieure et une variabilité plus faible. Cela suggère une meilleure capture des détails géométriques, notamment dans les zones complexes.

### Cartographie

- Cartes superposées présentant les virages détectés par chaque source, permettant de visualiser les correspondances et les écarts.
- Identification des zones de divergence, où certains virages sont absents ou mal localisés dans OSM, probablement en raison de mises à jour moins fréquentes ou d’une moindre précision collaborative.

### Illustrations

Pour illustrer ces résultats, plusieurs graphiques et cartes ont été générés :

- Les figures issues d’OSM sont disponibles dans le répertoire `out/plots/linkedin_osm`, incluant des cartes de densité de virages et des visualisations des angles mesurés.
- Les figures correspondantes pour l’IGN se trouvent dans `out/plots/linkedin_ign`, montrant notamment la finesse de la détection des courbures et la localisation précise des virages.
- Des cartes combinées superposant les deux sources permettent d’apprécier visuellement les différences et les complémentarités.

## Interprétation

- L’IGN détecte plus de virages, notamment dans les zones complexes ou récemment aménagées, ce qui reflète la qualité et la mise à jour régulière de ses données officielles.
- OSM, bien que très utile grâce à sa couverture collaborative étendue, présente quelques omissions et imprécisions géométriques, en particulier dans les secteurs moins fréquentés ou moins édités.
- La fusion des données issues des deux sources permet de corriger ces lacunes, offrant ainsi un référentiel hybride plus complet et fiable pour les analyses géométriques routières.

## Limites et perspectives

Cette étude comporte certaines limites qu’il convient de souligner :

- L’absence de noms de rues dans les données IGN utilisées complique parfois l’identification précise des segments, limitant certaines analyses contextuelles.
- Les différences de granularité entre OSM et IGN, notamment dans la représentation des petites voies ou des aménagements récents, introduisent des biais dans la comparaison.
- Les décalages spatiaux et les différences dans les méthodologies de collecte impactent la superposition exacte des virages.
- À l’avenir, le développement d’un référentiel hybride intégrant automatiquement les mises à jour collaboratives et les données officielles pourrait améliorer la qualité et la couverture des analyses.
- Des travaux complémentaires pourraient également explorer l’intégration de données temporelles pour suivre l’évolution des infrastructures et des virages dans le temps.

## Conclusion

Cette étude de cas illustre l’intérêt du référentiel hybride pour améliorer la qualité des analyses de virages, en combinant la couverture collaborative d’OSM et la précision officielle de l’IGN. En enrichissant les données par une méthodologie rigoureuse et des outils d’analyse adaptés, il est possible d’obtenir un référentiel plus complet et fiable, essentiel pour les applications en urbanisme, mobilité et sécurité routière.
