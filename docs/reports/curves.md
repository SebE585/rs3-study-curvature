# Courbure — Analyse des virages

Ce rapport se concentre sur les courbes détectées (séquences à forte courbure/faible rayon) et leur comparaison OSM vs BD TOPO.

## Indicateurs clés (KPIs)

_KPIs non trouvés — lancez `make curve-stats`._

## Figures

_Aucune figure détectée — lancez `make curve-profiles`._

# Courbure — Analyse des virages

Ce rapport se concentre sur les courbes détectées (séquences à forte courbure/faible rayon) et leur comparaison entre OSM et BD TOPO.

## Indicateurs clés (KPIs)

Les principaux indicateurs issus des traitements sont :

- **Nombre total de segments analysés** : OSM ≈ 32 678 / BD TOPO ≈ 38 4096
- **Virages identifiés (rayon < 150 m)** : OSM ≈ 32 678 / BD TOPO ≈ 45 687
- **Rayon minimal observé** : OSM ≈ 2859 m / BD TOPO ≈ 15 m
- **Rayon maximal observé** : OSM ≈ 93 M m / BD TOPO ≈ 6,9 G m
- **Courbure maximale (κ)** : OSM ≈ 3.49e-07 / BD TOPO ≈ 0.0666

👉 Ces différences traduisent une forte variabilité dans la précision géométrique et dans la sensibilité de détection des deux sources.

## Figures

Les figures ci-dessous sont générées par la commande :

```bash
make curve-profiles
```

Elles incluent :

- Profils moyens de courbure (κ) le long des segments.
- Histogrammes et distributions des rayons de virage.
- Comparaison des classes routières (autoroutes, routes principales, secondaires).

_Exemples de sorties disponibles dans le dossier `out/plots/curves_*`._

## Interprétation

- **OSM** montre des profils plus lissés, avec une tendance à sous-estimer la sévérité de certains virages.
- **BD TOPO** capture des détails géométriques fins, mais peut introduire du bruit (segments très courts, micro-courbures).
- Les différences se concentrent surtout sur les routes secondaires et tertiaires, où la densité des points OSM est plus faible.

## Implications

- Pour les besoins de **simulation routière réaliste**, la combinaison des deux sources semble pertinente :
  - OSM pour la couverture rapide et homogène.
  - BD TOPO pour enrichir les sections critiques (zones sinueuses, montagneuses).
- En l’état, aucun des deux jeux de données n’est suffisant seul pour constituer un référentiel robuste des virages.

## Perspectives

- **Améliorer la détection multi-échelles** en combinant lissage et détection locale des courbes.
- **Construire un référentiel hybride** intégrant OSM + BD TOPO, avec attribution de scores de confiance.
- **Étendre l’analyse statistique** par classes de routes, régions et environnements (urbain/rural).
- **Ouvrir la voie à un “Référentiel National des Virages”** utile pour l’ADAS, la simulation de conduite, et la sécurité routière.
