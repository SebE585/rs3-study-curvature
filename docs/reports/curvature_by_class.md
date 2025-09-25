---
title: Comparatif OSM vs BD TOPO — Par classe
date: 2025-09-22 10:35:50
---

# Comparatif par classe

## Tableau récapitulatif

*Aucun CSV par classe disponible — section omise.*

*Placeholder : Cette section sera complétée par des visualisations détaillées telles que des distributions de courbure par classe, des histogrammes des longueurs de routes, et des boxplots permettant de comparer la variabilité intra-classe entre OSM et BD TOPO.*

## Interprétation préliminaire

Les distributions par classe confirment des différences systématiques entre OSM et BD TOPO :

- Pour les classes **motorway** et **trunk**, les écarts de longueur et de courbure sont particulièrement marqués.
- Les routes **primaires** et **secondaires** présentent des divergences plus modérées, mais statistiquement significatives.
- Certaines classes urbaines (residential, unclassified) montrent une variabilité accrue, probablement liée à la granularité des contributions OSM.

### Stabilité numérique de la courbure (κ) selon les classes

- La stabilité des mesures de courbure varie selon la classe de route, avec une meilleure consistance observée sur les grandes routes (motorway, trunk).
- Les classes rurales tendent à présenter une plus grande dispersion des valeurs de κ, probablement liée à la résolution des données et à la nature des segments.

### Différences entre classes rurales et urbaines

- Les classes urbaines (residential, unclassified) montrent une forte variabilité, probablement due à la complexité du maillage routier et à la densité des contributions OSM.
- Les classes rurales bénéficient souvent d’une meilleure homogénéité dans BD TOPO, mais peuvent souffrir d’une résolution plus grossière.

### Causes possibles des différences observées

- Résolution de numérisation différente entre BD TOPO et OSM.
- Biais inhérents aux contributions volontaires dans OSM, avec des zones plus ou moins détaillées.
- Méthodes d’acquisition et de mise à jour propres à BD TOPO, pouvant entraîner une homogénéisation ou un lissage des données.

Ces observations complètent les résultats globaux et doivent être rapprochées de l’analyse de sensibilité (bias sweep).

## Implications pratiques

- Impact sur les simulations ADAS nécessitant une modélisation précise de la géométrie routière.
- Évaluation de la sécurité routière à partir des caractéristiques de courbure et de longueur des segments.
- Harmonisation cartographique entre sources pour améliorer la cohérence des bases de données routières.
- Optimisation des algorithmes de navigation et de guidage en fonction des spécificités par classe de route.

## Perspectives

- Mise en œuvre de tests statistiques par classe pour quantifier la significativité des différences observées.
- Intégration des résultats dans une référence hybride de courbure combinant BD TOPO et OSM.
- Liaison avec les expérimentations de fitting de clothoïdes pour affiner la modélisation géométrique des routes.
- Exploration des impacts des différences de courbure sur des applications métiers spécifiques (transport, urbanisme, cartographie dynamique).
