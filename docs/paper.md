# 📄 Paper — Étude scientifique

## Contexte
La simulation réaliste de trajets véhicules exige une représentation fiable du réseau routier.  
Nous avons comparé deux sources majeures : **OpenStreetMap (OSM)** et **BD TOPO® (IGN)**.  
Les données ont été traitées avec le pipeline RS3 (courbure, pente, densification).

## Contributions
- Pipeline reproductible pour extraire des métriques de courbure.
- Comparaison OSM vs BD TOPO en Haute-Normandie.
- Analyse globale et locale (nearest neighbor).
- Liens avec les usages inertiels (accélération latérale, vitesse sûre en virage).

## Résultats (teasers)
- OSM → segments courts (~50 m en moyenne).  
- BD TOPO → segments plus longs (~170 m en moyenne).  
- Les rayons de courbure sont plus fins côté BD TOPO.

👉 Voir [Méthodes](method.md), [Résultats](results.md), et [Produit](product.md).