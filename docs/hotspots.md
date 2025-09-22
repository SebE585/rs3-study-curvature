# Hotspots d’écarts OSM vs BD TOPO 📊

## Méthodologie 🛠️

Nous avons extrait les **5000 segments les plus divergents** entre **OSM** et **BD TOPO** selon la métrique **`diff_curv_mean_1perm`** (courbure moyenne).  
Les résultats sont exportés en **GeoPackage (`compare__hotspots.gpkg`)** et visualisés dans **QGIS**.

## Carte 🗺️

📍 Exemple de visualisation des **hotspots** dans **QGIS** :  
*(capture d’écran à insérer ici)*

Nous pouvons aussi intégrer quelques **captures locales** illustrant des cas extrêmes :
- Segment de type *motorway* avec forte différence de courbure (OSM rectiligne vs BD TOPO sinueux).
- Tronçon urbain court, où OSM a sur-segmenté et sous-estimé la courbure.
- Route secondaire rurale absente ou trop lissée dans l’une des deux bases.

*(captures ou extraits cartographiques à insérer pour chaque cas)*

## Top 10 des écarts (illustratif) 🔝

| Rank | ID OSM  | ID BD  | Δ longueur (m) | Δ courbure (1/m) |
|:-----|:--------|:-------|---------------:|-----------------:|
| 1    | osm_123 | bd_456 |         -210.5 |           -0.045 |
| 2    | osm_789 | bd_101 |         -180.3 |           -0.037 |
| 3    | osm_234 | bd_567 |         -155.9 |           -0.031 |
| …    | …       | …      |            …   |              …   |

Ces exemples peuvent être détaillés individuellement sous forme de **fiches de cas** avec carte, métriques et capture terrain (photo/StreetView).

## Utilisation 🚀

- **Diagnostic terrain** : cibler les tronçons où **OSM** est trop rectiligne ou trop fragmenté.  
- **Amélioration RS3** : enrichir les simulations inertielle avec un mix **OSM+IGN**.  
- **Feedback communauté OSM** : corriger manuellement certains tracés.

---

Ces **hotspots d’écarts** représentent des zones clés où l’analyse et la correction peuvent significativement améliorer la qualité des données géographiques et la précision des simulations. Leur identification est donc essentielle pour un travail ciblé et efficace.

---

## Perspectives
- Sélectionner automatiquement quelques hotspots emblématiques pour la documentation publique.
- Créer des liens interactifs vers les vues OSM / Géoportail IGN pour validation rapide.
- Utiliser ces cas comme **jeu d’entraînement** pour détecter automatiquement d’autres anomalies.