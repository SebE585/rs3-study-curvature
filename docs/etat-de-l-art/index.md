# État de l’art

Panorama des approches pertinentes pour la modélisation, la mesure et l’analyse de la courbure du réseau routier.

## Contenu
- **Introduction** : positionnement, définitions et objectif d’étude.
- **Modèles géométriques** : courbure, lissage, approximation.
- **Méthodes géospatiales** : segmentation, topologie, graphes.
- **Méthodes de vision** : extraction de forme, courbure sur raster.
- **Méthodes capteurs** : GNSS/IMU, trajectoires et bruit.
- **Applications** : qualité des données, sécurité, planification.

> Chaque page résume la littérature clé, les **hypothèses**, les **forces/faiblesses** et propose des **références**.

# État de l’art

Ce chapitre propose un panorama structuré des approches existantes pour la **modélisation**, la **mesure** et l’**analyse** de la courbure du réseau routier.
Il vise à situer notre étude dans le contexte scientifique et industriel actuel, en soulignant les avancées, les limites et les opportunités.

## Contenu
- **Introduction** : définitions clés (courbure, rayon, clothoïde), enjeux et objectif de l’étude.
- **Modèles géométriques** :
  - Définition mathématique de la courbure et du rayon.
  - Lissage et approximation par splines / clothoïdes.
  - Avantages : précision théorique.
  - Limites : dépendance à la qualité des données géométriques.

- **Méthodes géospatiales** :
  - Segmentation du réseau routier à partir de données vectorielles (OSM, IGN, HERE).
  - Construction de graphes et extraction de métriques topologiques.
  - Points forts : applicabilité à grande échelle, faible coût.
  - Faiblesses : hétérogénéité des sources, précision limitée.

- **Méthodes de vision** :
  - Détection de formes et calcul de courbure à partir d’images raster (satellite, lidar).
  - Utilisation de CNN et de méthodes de segmentation.
  - Atouts : richesse d’information, couverture étendue.
  - Inconvénients : besoin de calcul intensif, dépendance à la résolution.

- **Méthodes capteurs** :
  - Exploitation de données GNSS/IMU, enregistrements embarqués, traces véhicules.
  - Reconstruction de trajectoires avec bruit et filtrage (Kalman, particules).
  - Avantages : mesure in situ, sensibilité locale.
  - Limites : dépendance au matériel, bruit et dérive.

- **Applications** :
  - **Qualité des données** : contrôle de cohérence cartographique.
  - **Sécurité routière** : identification des zones à risque.
  - **Planification et gestion d’infrastructures** : choix de tracés, maintenance préventive.
  - **Conduite assistée et autonome** : intégration de la courbure dans les systèmes ADAS.
  - **Recherche scientifique** : étude des liens entre géométrie, mobilité et sécurité.

## Références
Chaque section renvoie vers les travaux de référence (articles, rapports techniques, standards) afin de fournir une base solide pour la suite de l’étude.

> Cet état de l’art met en lumière les **forces**, les **faiblesses** et les **lacunes** des approches actuelles, et prépare le terrain pour la construction d’un **référentiel hybride de la courbure routière**.
