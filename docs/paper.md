## 1. Problème & hypothèse

On cherche à évaluer la cohérence géométrique des courbes routières entre OSM et BD TOPO® en Haute-Normandie, car ces différences impactent la simulation inertielle (RS3) via :  
$$a_{lat}=\frac{v^2}{r}, \qquad \omega_z = \frac{v}{r}.$$  
Hypothèse : la segmentation et la généralisation de chaque base induisent (i) des écarts systématiques de longueur par segment et (ii) des écarts de courbure (OSM tendant à être plus « lissé »).

## 2. Méthodes (condensé)
- Appariement nearest neighbor OSM→BD (centroïdes, EPSG:2154), distance $d \in \{20,30,50\}\,\mathrm{m}$.
- Contrainte de classe optionnelle après normalisation et mapping BD→OSM (cf. configs/class_map.yml).
- Écarts $\Delta m$ pour $m \in \{\texttt{length\_m}, \texttt{radius\_min\_m}, \texttt{curv\_mean\_1perm}\}$; ±∞ censurés sur `radius_min_m`.

## 3. Résultats principaux
- Couverture : 206k (d=20 m) → 291k (30 m) → 418k (50 m) appariements.
- Biais de longueur : $\Delta \texttt{length\_m}$ moyen ~ −63 → −76 → −94 m quand d augmente.
- Courbure moyenne : $\Delta \texttt{curv\_mean\_1perm}$ ~ −0,012–−0,013 (OSM plus « souple »).
- Contrainte de classe (d=30 m, ~9,3k matchs) :
  - $\Delta \texttt{length\_m}$ −106,7 m,
  - $\Delta \texttt{curv\_mean\_1perm}$ −0,0066 → l’hétérogénéité fonctionnelle expliquait une partie de l’écart de courbure.

## 4. Interprétation & implications RS3
- OSM sur-segmente le réseau (tronçons plus courts), ce qui réduit la courbure moyenne calculée par tronçon (souvent plus rectiligne localement).
- BD TOPO modélise des géométries plus continues — rayons minimaux plus « fins », expliquant $\Delta \texttt{curv\_mean} < 0$.
- Pour RS3, la vitesse sûre en courbe $v_{\max}=\sqrt{a_{lat,\max}\, r}$ dépend directement de $r$ : l’écart de courbure peut biaiser les profils inertiels synthétiques (a_lat, yaw-rate).
- La contrainte de classe rapproche les comportements (moins d’écart de courbure), utile pour des comparaisons à usage applicatif (ex. validation perception/localisation).

## 5. Limites
- Appariement spatial seul (pas de continuité topologique ni direction).
- Classes partiellement mappées (résidus : junction, steps, ferry…), à affiner.
- `radius_min_m` reste instable sur les tronçons quasi-rectilignes (valeurs très grandes / infinies).

## 6. Travaux à venir
- Matching topo-constrain : même classe + tolérance directionnelle + distance max stricte.
- Affinage mapping BD→OSM (éclater route principale/secondaire/tertiaire ; relier bretelle↔motorway_link, chemin/piste↔track…) et échantillons par classe équilibrés.
- Hotspots : audit visuel des écarts extrêmes via compare__nearest_links.gpkg et hotspots (déjà dispo).
- Pente (activer slope_mean_pct) et croisements avec maxspeed pour lier courbure ↔ vitesse.
- Sensibilités (pas de densification, tolérance de simplification) + intervalle de confiance par bootstrap.