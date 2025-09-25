# Hotspots d’écarts OSM vs BD TOPO 📊

## Introduction

Dans le cadre de la comparaison entre les données géographiques d’OpenStreetMap (OSM) et de la BD TOPO de l’IGN, un **hotspot** désigne une zone géographique présentant des écarts significatifs entre les deux bases, notamment en termes de géométrie des segments routiers. Ces écarts peuvent refléter des différences dans la précision, la mise à jour, ou la méthodologie de modélisation des routes. Identifier ces hotspots est crucial pour cibler les zones nécessitant une correction ou une analyse approfondie, afin d’améliorer la qualité des données et la fiabilité des simulations basées sur ces données.

## Méthodologie 🛠️

Nous avons extrait les **5000 segments les plus divergents** entre **OSM** et **BD TOPO** selon la métrique **`diff_curv_mean_1perm`**, qui mesure la différence moyenne de courbure normalisée par mètre entre les deux bases. Cette métrique est calculée en comparant la courbure moyenne de chaque segment dans OSM et BD TOPO, puis en normalisant cette différence par la longueur du segment pour obtenir une valeur comparable entre segments de tailles variées. Cette approche permet de détecter non seulement les écarts de longueur, mais aussi les différences dans la forme et la sinuosité des tronçons, ce qui est essentiel pour des applications comme la modélisation inertielle ou la navigation.

Les résultats sont exportés en **GeoPackage (`compare__hotspots.gpkg`)** et visualisés dans **QGIS**.

## Carte 🗺️

📍 Pour reproduire la visualisation des **hotspots** dans **QGIS** :
- Charger le fichier GeoPackage `compare__hotspots.gpkg`.
- Appliquer un style basé sur la métrique `diff_curv_mean_1perm` pour mettre en évidence les segments avec les plus fortes divergences.
- Utiliser des couches de fond OSM et BD TOPO pour comparer visuellement les tracés.
- Exporter des captures d’écran pour documentation.

Il est également recommandé de générer des visualisations complémentaires avec **Matplotlib** en Python, par exemple des cartes de densité des hotspots ou des graphiques comparant les distributions des métriques. Ces captures peuvent être intégrées dans les rapports pour une analyse plus complète.

Nous pouvons aussi intégrer quelques **captures locales** illustrant des cas extrêmes :
- Segment de type *motorway* avec forte différence de courbure (OSM rectiligne vs BD TOPO sinueux).
- Tronçon urbain court, où OSM a sur-segmenté et sous-estimé la courbure.
- Route secondaire rurale absente ou trop lissée dans l’une des deux bases.

*(captures ou extraits cartographiques à insérer pour chaque cas)*

## Top 10 des écarts (illustratif) 🔝

Le classement des segments est réalisé en triant les 5000 hotspots selon la valeur absolue de la métrique `diff_curv_mean_1perm`, en priorité, puis en affinant selon la différence de longueur. Ce classement permet de cibler les écarts les plus marqués en termes de forme et de taille.

| Rank | ID OSM  | ID BD  | Δ longueur (m) | Δ courbure (1/m) |
|:-----|:--------|:-------|---------------:|-----------------:|
| 1    | osm_123 | bd_456 |         -210.5 |           -0.045 |
| 2    | osm_789 | bd_101 |         -180.3 |           -0.037 |
| 3    | osm_234 | bd_567 |         -155.9 |           -0.031 |
| …    | …       | …      |            …   |              …   |

Cette table est à titre illustratif et peut être enrichie avec des informations supplémentaires telles que la classe de route, le contexte géographique, ou les indicateurs de qualité.

Ces exemples peuvent être détaillés individuellement sous forme de **fiches de cas** avec carte, métriques et capture terrain (photo/StreetView).

## Analyses complémentaires

- **Clustering des hotspots** : regrouper les segments proches géographiquement présentant des écarts similaires pour identifier des zones problématiques étendues.
- **Filtrage par classe de route** : analyser séparément les écarts selon les types de routes (autoroutes, routes secondaires, urbaines) pour adapter les stratégies de correction.
- **Identification de motifs récurrents** : détecter des patterns géographiques ou topologiques récurrents, comme des zones urbaines denses ou des secteurs ruraux mal cartographiés, pour prioriser les interventions.

## Utilisation 🚀

- **Diagnostic terrain** : cibler les tronçons où **OSM** est trop rectiligne ou trop fragmenté.
- **Amélioration RS3** : enrichir les simulations inertielle avec un mix **OSM+IGN**.
- **Feedback communauté OSM** : corriger manuellement certains tracés.

---

Ces **hotspots d’écarts** représentent des zones clés où l’analyse et la correction peuvent significativement améliorer la qualité des données géographiques et la précision des simulations. Leur identification est donc essentielle pour un travail ciblé et efficace.

---

## Perspectives

- Sélectionner automatiquement quelques hotspots emblématiques pour la documentation publique.
- Créer des liens interactifs vers les vues OSM / Géoportail IGN pour validation rapide.
- Utiliser ces cas comme **jeu d’entraînement** pour détecter automatiquement d’autres anomalies.
- Développer des workflows semi-automatisés de validation et correction, combinant analyses automatiques et interventions humaines.
- Intégrer directement les résultats dans la chaîne de traitement RS3 pour améliorer la qualité des données en amont des simulations.
- Publier un jeu de données benchmark des hotspots pour la communauté, afin de favoriser la recherche et la collaboration sur la qualité des données géographiques.
