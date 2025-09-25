# TODO — Étude de la courbure routière

## Prochaines étapes scientifiques

- [ ] **Quantification rigoureuse des écarts**
  - Appliquer des tests statistiques (Kolmogorov–Smirnov, t-test, ANOVA si nécessaire).
  - Calculer des intervalles de confiance sur les écarts moyens par métrique.
  - Vérifier la robustesse selon les distances d’appariement (20, 30, 50 m).

- [ ] **Analyse par classe de route**
  - Comparer les distributions des métriques (longueur, rayon minimal, courbure moyenne) par classe.
  - Identifier les classes de routes présentant les écarts les plus marqués.
  - Visualiser les résultats via boxplots / CDFs par classe.

- [ ] **Exploration des biais potentiels**
  - Évaluer l’influence des erreurs de segmentation sur les métriques.
  - Contrôler l’impact du filtrage des valeurs infinies ou aberrantes.

- [ ] **Mise en perspective scientifique**
  - Formuler une discussion sur la qualité relative d’OSM et de la BD TOPO.
  - Identifier les limites des bases de données routières actuelles.
  - Dégager des pistes pour améliorer la modélisation géométrique routière.

- [ ] **Préparation à publication**
  - Rédiger un premier draft de section "Résultats et discussion".
  - Mettre en forme figures et tableaux de synthèse pour un article.
  - Cibler un support de publication (conférence, revue).

---
_Mis à jour automatiquement à partir des discussions de recherche._


## Vers un référentiel de virages hybride

- **Fusion des sources OSM et IGN**
  - Croisement et consolidation des géométries issues d’OpenStreetMap et de la BD TOPO de l’IGN pour une couverture et une précision optimales.
- **Intégration des clothoïdes**
  - Calcul et modélisation des transitions de courbure (clothoïdes) pour une représentation fidèle des virages routiers.
- **Stockage et formats de diffusion**
  - Export et archivage des données de virages en formats Parquet (pour l’analyse à grande échelle) et GeoJSON (pour la visualisation et l’intégration SIG).
- **Cas d’usage**
  - Applications dans les systèmes avancés d’aide à la conduite (ADAS).
  - Exploitation par le secteur de l’assurance (évaluation du risque routier).
  - Valorisation par les gestionnaires d’infrastructures pour la maintenance et la sécurité.

## Suivi et gouvernance du projet

- **Mise à jour régulière**
  - Synchronisation périodique avec les dernières versions d’OSM et de la BD TOPO.
- **Automatisation et CI/CD**
  - Mise en place de pipelines d’intégration continue pour le traitement, la validation et la publication des données.
- **Documentation**
  - Rédaction et maintenance de la documentation technique et utilisateur via MkDocs.
- **Diffusion open data**
  - Publication régulière des jeux de données sous licence ouverte.
- **Interaction avec l’IGN**
  - Collaboration continue pour l’amélioration des référentiels et la remontée de corrections.

---
_Ces étapes sont alignées avec le projet RoadSimulator3 et la perspective d’un référentiel national des virages._
