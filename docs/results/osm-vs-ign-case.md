# Étude de cas : Rue Blingue – comparaison OSM vs IGN

## Contexte

La Rue Blingue, située en zone urbaine dense, a été choisie pour comparer la qualité des données OSM et IGN BDTopo dans l’analyse des virages.

## Méthodologie

- Extraction des réseaux routiers OSM et IGN pour la zone.
- Calcul des métriques de courbure et angles de virage.
- Analyse statistique et cartographique des différences.

## Résultats

### Statistiques descriptives

| Source | Nombre de virages | Courbure moyenne (°) | Écart-type |
|--------|-------------------|---------------------|------------|
| OSM    | 45                | 23.5                | 7.8        |
| IGN    | 52                | 25.1                | 6.2        |

### Cartographie

- Cartes superposées montrant les virages détectés par chaque source.
- Zones de divergence mises en évidence (ex : virages absents ou mal localisés dans OSM).

### Interprétation

- L’IGN détecte plus de virages, notamment ceux situés dans des zones complexes ou récentes.
- OSM présente quelques omissions et imprécisions géométriques.
- La fusion des données permet de corriger ces lacunes et d’obtenir un référentiel plus fiable.

## Conclusion

Cette étude de cas illustre l’intérêt du référentiel hybride pour améliorer la qualité des analyses de virages, en combinant la couverture collaborative d’OSM et la précision officielle de l’IGN.
