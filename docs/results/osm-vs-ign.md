# Résultats — OSM vs IGN

Comparaison des courbures estimées à partir d’OpenStreetMap et des données IGN.
Mise en évidence des écarts de précision et de couverture.

## Méthodologie

L'extraction des segments a été réalisée à partir des données OpenStreetMap (OSM) et des données IGN. Chaque segment correspond à une portion de route ou de voie. Pour chaque segment, le rayon de courbure a été calculé en utilisant des clothoïdes, qui permettent de modéliser la variation progressive de la courbure le long des segments. Afin d'assurer la qualité des estimations, plusieurs filtres ont été appliqués : un rayon minimal (R_min) a été fixé pour exclure les courbures trop faibles ou bruitées, et un seuil de coefficient de détermination (R²) a été utilisé pour ne conserver que les segments présentant une bonne adéquation à la modélisation par clothoïde.

## Résultats globaux

Le nombre total de segments retenus après filtrage est de plusieurs milliers, couvrant une large plage de rayons de courbure, allant de quelques mètres à plusieurs centaines de mètres. Cette diversité permet d'analyser finement la géométrie des routes.
Les cartes comparatives (OSM et IGN) sont générées automatiquement et disponibles dans le répertoire `out/plots` du dépôt.

## Comparaison OSM vs IGN

La comparaison entre les données OSM et IGN révèle plusieurs différences notables :
- **Couverture** : OSM présente une couverture plus étendue dans les zones urbaines, tandis que IGN est plus complet en zones rurales et sur certains axes principaux.
- **Bruit** : Les données IGN montrent généralement moins de bruit dans les mesures de courbure grâce à une meilleure précision des levés, alors que OSM peut contenir des segments plus irréguliers.
- **Attributs de nommage** : Les noms et identifiants des segments sont plus cohérents dans IGN, ce qui facilite le regroupement et l'analyse, contrairement à OSM où l'hétérogénéité est plus importante.
- **Cohérence spatiale** : La continuité spatiale des segments est meilleure dans IGN, avec des transitions plus fluides entre segments, alors que OSM peut présenter des discontinuités ou des chevauchements.

## Illustrations

Les résultats sont illustrés par plusieurs types de graphiques :
- Cartes thématiques montrant la distribution des rayons de courbure sur le territoire.
- Boxplots comparant la distribution des rayons entre OSM et IGN.
- Histogrammes des fréquences des différents intervalles de rayons.
Ces fichiers sont disponibles dans les dossiers de sortie et permettent une analyse visuelle approfondie des différences et similitudes.

## Limites et perspectives

Plusieurs difficultés ont été rencontrées lors de cette étude :
- Le nommage des segments dans les données IGN est parfois complexe à exploiter en raison de conventions variées.
- Les différences de systèmes de coordonnées (CRS) entre OSM et IGN ont nécessité des transformations précises pour assurer la comparabilité.
- La performance du traitement des grands volumes de données reste un enjeu, notamment pour les calculs de courbure sur des réseaux étendus.
En perspective, ces travaux ouvrent la voie à la création d'un référentiel hybride des virages, combinant la couverture et la précision des deux sources, afin d'améliorer la qualité des analyses géométriques des réseaux routiers.
