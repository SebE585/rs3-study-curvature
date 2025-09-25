# Méthodes

Cette section détaille la méthodologie de mesure et d’analyse de la **courbure des tronçons routiers** ainsi que la construction de **profils par classes**.

## Objectifs

Ces méthodes sont nécessaires pour comparer les données géométriques issues de différentes sources, notamment OpenStreetMap (OSM) et l'Institut National de l'Information Géographique et Forestière (IGN). Elles permettent de créer un référentiel fiable de virages routiers, essentiel pour des applications variées telles que l'amélioration de la sécurité routière et la simulation de trajets réalistes.

## Contenu
- **Courbure des tronçons** : définition, choix des métriques, paramètres, hypothèses.
- **Profils par classes** : agrégation par catégories (fonctionnelles / hiérarchiques), indicateurs dérivés et visualisations.
- **Comparaison de sources (OSM vs IGN)** : description des différences de géométrie et de complétude.
- **Clothoïdes et filtrage** : importance de l’ajustement par clothoïde pour détecter les virages réels.

## À lire d'abord
- *Méthode (vue d'ensemble)* : `../method.md` — survol rapide avant de plonger dans les détails.

## Liens vers les sorties expérimentales

- `../../out/stats/summary.md` (statistiques globales).
- `../../out/reports/curves.md` (rapport détaillé).
- `../../out/plots` (graphes et visualisations).
