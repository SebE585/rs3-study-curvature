# Discussion et perspectives

## Biais observés

### Segmentation OSM 📊

- **OpenStreetMap** fournit beaucoup plus de segments (**653k** vs **457k** pour BD TOPO), ce qui réduit artificiellement les longueurs moyennes.  
- → Cela impacte la mesure de courbure car chaque petit segment peut sembler plus rectiligne.

### Précision BD TOPO (IGN) 🎯

- Les rayons minimaux et les courbures moyennes montrent que **BD TOPO** capte mieux les détails géométriques, surtout sur les routes sinueuses.  


## Implications pour RS3

### Assurance / Risque routier ⚠️

- Les différences de courbure peuvent modifier la probabilité d’un freinage brutal ou d’une perte d’adhérence simulée.  

### Smart city / Mobilité 🚦

- Les modèles énergétiques ou de sécurité basés sur **OSM** risquent de sous-estimer les contraintes liées aux courbes serrées.  

### ADAS / Conduite autonome 🚗

- Pour calibrer des algorithmes inertiels, il est préférable d’utiliser **BD TOPO** (plus précis), ou au minimum un hybride **OSM+BDTOPO**.


## Limites de l’étude

- Pas de **matching topologique** (uniquement nearest neighbor par centroïde).  
- Pas de **contrainte de classe routière** dans l’appariement.  
- **Pente désactivée** (MNT pas encore intégré).  


## Travaux futurs

- Appariement **OSM ↔ BD TOPO** avec contrainte de **classe** et **distance max** (ex. ≤ 30 m).  
- Production d’un **GPKG hotspots** des écarts les plus importants.  
- Activation de la **pente** via MNT homogène (EPSG:2154).  
- **Validation terrain** sur un échantillon (mesures GNSS).  