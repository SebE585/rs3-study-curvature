# Discussion et perspectives

## Biais observés

### Segmentation OSM 📊

- **OpenStreetMap** fournit beaucoup plus de segments (**653k** vs **457k** pour BD TOPO), ce qui réduit artificiellement les longueurs moyennes.  
- → Cela impacte la mesure de courbure car chaque petit segment peut sembler plus rectiligne.  
- Impact de la granularité OSM (segmentation liée aux contributions collaboratives, hétérogénéité selon les zones urbaines/rurales).  
- Limites de la précision IGN (géométrie captée mais parfois généralisée sur petites routes rurales).  

### Précision BD TOPO (IGN) 🎯

- Les rayons minimaux et les courbures moyennes montrent que **BD TOPO** capte mieux les détails géométriques, surtout sur les routes sinueuses.  


## Implications pour RS3

### Assurance / Risque routier ⚠️

- Les différences de courbure peuvent modifier la probabilité d’un freinage brutal ou d’une perte d’adhérence simulée.  
  - Un mauvais rayon influence les modèles actuariels en modifiant la probabilité d’accidents liés aux virages serrés.

### Smart city / Mobilité 🚦

- Les modèles énergétiques ou de sécurité basés sur **OSM** risquent de sous-estimer les contraintes liées aux courbes serrées.  
  - Cela peut entraîner une sous-estimation des émissions et de la consommation énergétique si la courbure est mal représentée.

### ADAS / Conduite autonome 🚗

- Pour calibrer des algorithmes inertiels, il est préférable d’utiliser **BD TOPO** (plus précis), ou au minimum un hybride **OSM+BDTOPO**.  
  - Des erreurs dans l’estimation de la courbure peuvent causer une sur- ou sous-estimation des corrections inertielle nécessaires.

## Limites de l’étude

- Pas de **matching topologique** (uniquement nearest neighbor par centroïde).  
- Pas de **contrainte de classe routière** dans l’appariement.  
- **Pente désactivée** (MNT pas encore intégré).  
- Les différences d’emprise spatiale (zones non couvertes de la même manière par OSM et BD TOPO).  
- Effet possible des tags OSM (maxspeed, surface, lanes) non exploités.  

## Travaux futurs

- Appariement **OSM ↔ BD TOPO** avec contrainte de **classe** et **distance max** (ex. ≤ 30 m).  
- Production d’un **GPKG hotspots** des écarts les plus importants.  
- Activation de la **pente** via MNT homogène (EPSG:2154).  
- **Validation terrain** sur un échantillon (mesures GNSS).  
- Analyse par **zone géographique** (urbain, périurbain, rural).  
- Intégration d’attributs supplémentaires (vitesse limite, largeur, trafic).  
- Génération automatique de **rapports comparatifs régionaux**.  
- Intégration dans un pipeline RS3 pour simulation directe.