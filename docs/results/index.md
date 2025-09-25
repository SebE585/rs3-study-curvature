# Résultats

Cette section présente une synthèse des résultats obtenus dans l’étude, ainsi que des liens directs vers les analyses détaillées.
Les résultats sont organisés par grands axes : comparaison de sources (OSM vs IGN), distributions statistiques, et détection de cas particuliers (hotspots).

---

## Points saillants

- **OSM vs IGN**
  Analyse comparative entre OpenStreetMap et la BD TOPO IGN.
  → Différences notables dans les distributions de courbure, en particulier pour les routes locales.
  → Résultats disponibles dans [OSM vs IGN](osm-vs-ign.md).

- **Distributions par classes**
  Étude des distributions de courbure par typologie de route (motorway, trunk, primary, etc.).
  → Mise en évidence de queues lourdes et de sous-populations atypiques.
  → Voir [Distributions par classes](distributions-classes.md).

- **Comparaisons locales**
  Comparaisons rapides entre OSM et IGN sur des segments ou zones spécifiques.
  → Voir [Comparaison rapide](../compare_quick.md) et [Comparaison par plus proche voisin](../compare_nearest.md).

- **Hotspots**
  Identification de zones où la courbure est particulièrement concentrée (virages serrés répétés, zones sinueuses).
  → Voir [Hotspots](../hotspots.md).

---

## Figures récentes

Quelques exemples de visualisations issues des dernières expériences :

- Distribution globale des longueurs de segments :
  ![Global histogram](../../out/plots/global_20250924_171227/length_m__hist_kde.png)

- Distribution par classe (motorway) :
  ![Motorway violin](../../out/plots/by_class_20250924_173611/motorway/length_m__violin.png)

- Exemple de carte de validation (Rue Blingue, IGN) :
  ![Carte IGN Rue Blingue](../../out/plots/linkedin_ign/linkedin_map.png)

---
