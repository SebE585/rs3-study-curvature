# Résultats — Distributions par classe


Distribution des rayons de courbure par classe de route (autoroutes, routes principales, secondaires, locales).

## Méthodologie

Les distributions des rayons de courbure sont générées à partir des données issues d'OSM et de l'IGN. Les segments routiers sont classés selon les catégories principales (autoroute, trunk, primaire, secondaire, locale), en s'appuyant sur les attributs de classe OSM ou IGN. Des seuils sont appliqués pour filtrer les valeurs aberrantes (par exemple, rayons trop faibles ou trop élevés). Les statistiques sont calculées pour chaque classe, en utilisant l'ensemble des segments valides.

## Figures

- [Histogrammes par classe](../../out/plots/by_class_20250924_173611/histograms_by_class.png)
- [Boxplots par classe](../../out/plots/by_class_20250924_173611/boxplots_by_class.png)
- [Violin plots par classe](../../out/plots/by_class_20250924_173611/violinplots_by_class.png)

## Analyse par classe

- **Autoroutes** : Les rayons de courbure sont globalement élevés, ce qui reflète la géométrie conçue pour la sécurité et la vitesse. La distribution est resserrée autour de grandes valeurs.
- **Trunk / Routes primaires** : Rayons intermédiaires, avec une variabilité modérée. Ces routes présentent des courbures plus prononcées que les autoroutes, mais restent relativement rectilignes.
- **Secondaires et locales** : Forte variabilité des rayons. On observe à la fois des segments très rectilignes et des courbes serrées, typiques des routes rurales ou urbaines.

## Comparaison OSM vs IGN

Les distributions issues d'OSM et de l'IGN sont globalement cohérentes pour les grandes classes (autoroutes, primaires). Quelques différences apparaissent pour les classes secondaires et locales, probablement liées à des divergences de classification ou à la précision du tracé. Globalement, la tendance des rayons reste similaire entre les deux sources.

## Implications

Ces résultats permettent de mieux caractériser la géométrie routière par classe, ce qui est pertinent pour la modélisation ADAS, l'évaluation de la sécurité ou la simulation de scénarios de conduite. Les distributions renseignent sur la difficulté potentielle des trajectoires et sur les exigences en matière d'assistance à la conduite.

## Perspectives

- Raffiner l'analyse par des tests statistiques pour quantifier les différences entre classes ou sources.
- Proposer des zooms géographiques (urbain/rural, régions spécifiques).
- Valider les résultats par des campagnes terrain ou des comparaisons avec d'autres bases de données.
