# Pipeline opérationnel de fusion OSM + IGN pour l’analyse de virages

Ce pipeline est désormais opérationnel pour fusionner les données issues d’OpenStreetMap (OSM) et de l’IGN BDTopo. Toutefois, l’utilisation des données IGN nécessite une attention particulière, notamment concernant le choix de la colonne de nom des routes et la reprojection des données de EPSG:2154 vers EPSG:4326.

## Variables d’environnement utilisées

Le comportement du pipeline est contrôlé par plusieurs variables d’environnement, détaillées dans le tableau ci-dessous :

| Variable                 | Description                                                                                          | Exemple / Valeur par défaut                      |
|--------------------------|--------------------------------------------------------------------------------------------------|-------------------------------------------------|
| `RS3_STREETS_SOURCE`     | Source des données de rue à utiliser (`osm` ou `ign`).                                           | `osm`                                           |
| `RS3_OSM_PATH`           | Chemin vers le fichier GeoJSON OSM nettoyé.                                                      | `data/osm_clean.geojson`                         |
| `RS3_IGN_PATH`           | Chemin vers le fichier vectoriel IGN BDTopo.                                                     | `data/ign_raw`                                  |
| `RS3_IGN_LAYER`          | Nom de la couche IGN à charger.                                                                  | `BDTOPO_V3_ROUTE`                               |
| `RS3_IGN_COL_NAME`       | Nom de la colonne contenant le nom des routes dans la couche IGN. Si non défini, aucun filtre n’est appliqué sur les noms. | `cpx_toponyme_route_nommee`                      |
| `RS3_STREETS_KEEP_SEGMENTS` | Critère de filtrage des segments à conserver (ex : `True` pour garder tous les segments).       | `False`                                          |

### Remarque sur `RS3_IGN_COL_NAME`

Si `RS3_IGN_COL_NAME` n’est pas défini, le pipeline n’applique pas de filtre sur la colonne nom des routes dans les données IGN, ce qui conduit à conserver un grand nombre de segments, souvent verbeux et redondants. Il est donc recommandé de définir cette variable pour cibler précisément les routes d’intérêt.

## Exemples pratiques

### Exemple OSM

Pour générer une carte basée uniquement sur les données OSM, utilisez la commande suivante :

```bash
make linkedin-map
```

Cette commande exploite les données OSM nettoyées et génère les fichiers nécessaires à l’analyse des virages.

### Exemple IGN

Pour travailler avec les données IGN, il est conseillé de définir la variable d’environnement suivante afin de filtrer les segments par nom de route :

```bash
export RS3_IGN_COL_NAME="cpx_toponyme_route_nommee"
```

Puis lancer le pipeline en utilisant les données IGN. Ce paramétrage permet de réduire la verbosité des données et de se concentrer sur les segments pertinents.

## Observations

- Les données OSM sont généralement plus légères et moins détaillées, ce qui facilite le traitement rapide.
- Les données IGN sont plus riches en informations mais aussi plus verbeuses, nécessitant un filtrage adapté pour éviter la surcharge.

## Conclusion

Ce pipeline permet désormais de construire un référentiel hybride des virages, combinant la légèreté et la couverture d’OSM avec la richesse et la précision des données IGN. Cette fusion ouvre la voie à des analyses plus robustes et complètes des caractéristiques des routes.
