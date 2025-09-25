# Méthodes basées sur la vision

Les méthodes basées sur la vision pour l’estimation de la courbure de la chaussée reposent sur l’analyse d’images ou de séquences vidéo capturées par des caméras embarquées. L’objectif est d’extraire des informations géométriques pertinentes à partir des caractéristiques visuelles de la route, telles que les lignes de marquage, les bords ou les textures, afin de modéliser la forme et la courbure du tracé routier. Ces approches exploitent les avancées en vision par ordinateur et en apprentissage automatique pour fournir des estimations précises et robustes dans des environnements variés.

## Pipeline type

Un pipeline typique pour l’estimation de la courbure à partir de la vision comprend plusieurs étapes clés :

- **Acquisition** : capture d’images ou de vidéos via des caméras embarquées, souvent montées sur un véhicule en mouvement.
- **Prétraitement** : stabilisation vidéo pour réduire les vibrations, correction de la perspective pour obtenir une vue plus frontale de la chaussée.
- **Détection des bords ou lignes de marquage** : application d’algorithmes classiques (Canny, Sobel) ou méthodes d’apprentissage pour identifier les lignes blanches, bandes de signalisation, ou bords de la route.
- **Extraction de la géométrie** : reconstruction des contours et modélisation de la forme de la chaussée à partir des éléments détectés.
- **Calcul de la courbure** : estimation des paramètres géométriques, notamment le rayon de courbure, à partir des données extraites.

## Techniques modernes

Les avancées récentes intègrent des réseaux de neurones profonds pour améliorer la robustesse et la précision :

- **CNN (Convolutional Neural Networks)** pour la détection et la segmentation des lignes et bandes routières.
- **Transformers** adaptés à la vision pour capturer des dépendances spatiales complexes.
- **Réseaux de segmentation** tels que U-Net ou DeepLab, permettant une identification pixel-à-pixel des zones d’intérêt.
- **Apprentissage auto-supervisé** avec des données synthétiques générées par simulation, facilitant l’entraînement sans annotation manuelle exhaustive.

Ces techniques permettent d’adapter les modèles à des environnements variés et d’améliorer la résistance aux perturbations visuelles.

## Benchmarks et résultats connus

Plusieurs datasets standards sont utilisés pour évaluer et comparer les méthodes :

- **KITTI** : dataset de référence pour la vision embarquée en conduite autonome.
- **Cityscapes** : images urbaines annotées pour la segmentation sémantique.
- **nuScenes** : données multimodales incluant vision et lidar.

Les métriques couramment utilisées incluent :

- **Erreur de rayon de courbure** : comparaison entre la courbure estimée et la vérité terrain.
- **IoU (Intersection over Union)** des bandes détectées, mesurant la qualité de la segmentation.

Ces benchmarks fournissent un cadre objectif pour mesurer les performances des différentes approches.

## Limites et perspectives

Malgré leurs avancées, les méthodes basées sur la vision présentent certaines limites :

- Forte dépendance aux conditions météo et luminosité (pluie, nuit, éblouissement).
- Difficultés en cas d’occlusions (véhicules, piétons, végétation).
- Coût computationnel élevé des modèles profonds en temps réel.

Cependant, les perspectives sont prometteuses grâce à :

- La fusion multi-capteurs (vision + lidar + radar) pour compenser les faiblesses individuelles.
- L’utilisation de données hybrides combinant images et informations géométriques.
- L’amélioration continue des architectures et algorithmes pour plus de robustesse et efficacité.
