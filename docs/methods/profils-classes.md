# Profils et classes de courbure

## Introduction

Cette section présente l'analyse des profils moyens de courbure des routes, segmentés par classes (autoroutes, routes primaires, secondaires, non classées). L'objectif est de mieux comprendre les caractéristiques géométriques des virages selon leur classification, en s'appuyant sur des statistiques et des visualisations détaillées.

## Méthodologie

Les profils moyens de courbure sont calculés à partir des données de courbure \(\kappa\) extraites des segments de route. Pour chaque classe, nous déterminons la moyenne des valeurs de \(\kappa\), ainsi que la distribution des rayons de courbure associés. Ces calculs permettent de quantifier l'intensité des virages et d'identifier les tendances spécifiques à chaque type de route. Les statistiques incluent également des indicateurs tels que la médiane, les quartiles, et les extrêmes, afin d'obtenir une vision complète des profils.

## Résultats globaux

Les principales statistiques globales, issues des fichiers `out/stats/curve_kpis_by_class.csv` et `out/stats/curve_kpis.csv`, montrent que :

- La distribution des rayons de courbure varie significativement selon la classe de route.
- Les virages sur autoroutes présentent en moyenne des rayons plus grands et des courbures plus faibles.
- Les routes secondaires et non classées affichent des rayons plus courts et des courbures plus marquées.
- Les indicateurs clés (moyenne, médiane, écart-type) confirment ces tendances générales.

## Résultats par classes

Les profils moyens de courbure ont été analysés pour les classes suivantes :

- Autoroutes
- Routes primaires
- Routes secondaires
- Routes non classées

## Figures

Les graphiques suivants illustrent les distributions et profils de courbure par classe :

- Histogrammes des rayons de courbure : `out/plots/by_class_histogram_radius.png`
- Boxplots des intensités de virage : `out/plots/by_class_boxplot_kappa.png`
- Violins des profils moyens : `out/plots/by_class_violin_profiles.png`

## Interprétation et discussion

L'analyse met en évidence des différences notables entre les classes de routes :

- Les autoroutes se caractérisent par des rayons de courbure généralement grands, traduisant des virages doux adaptés à des vitesses élevées.
- Les routes secondaires présentent des rayons plus courts et des virages plus serrés, correspondant à des conditions de circulation plus variables.
- Les routes non classées montrent une grande variabilité, reflétant leur diversité fonctionnelle et géométrique.
- Ces différences confirment l'importance de considérer la classification routière dans l'étude des profils de courbure.

## Perspectives

Ces profils moyens de courbure serviront de base pour l'élaboration d'un référentiel des virages hybrides combinant les données OSM et IGN. Ce référentiel permettra d'améliorer la modélisation et l'analyse des infrastructures routières pour diverses applications, notamment la sécurité routière et la planification des itinéraires.
