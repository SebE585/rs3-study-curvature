# TODO — Étude de la courbure routière

## 📊 Analyses statistiques
- [x] Implémenter des tests statistiques (t-test, KS-test, Mann-Whitney) pour comparer OSM vs BD TOPO.
- [x] Générer les distributions par métrique (longueur, rayon, courbure).
- [ ] Calculer les écarts moyens et écarts-types par classe de route.

## 🛣️ Analyse par classe
- [x] Quantifier les écarts pour chaque classe normalisée (motorway, trunk, primary, secondary, etc.).
- [x] Visualiser les distributions avec boxplots et violon plots.
- [ ] Identifier les classes présentant des écarts systématiques.

## 🔍 Exploration des biais
- [x] Vérifier l’impact de la distance max d’appariement (20m / 30m / 50m).
- [ ] Étudier la couverture spatiale (zones urbaines vs rurales).
- [x] Croiser avec d’autres attributs (vitesses, typologie, pente).

## 📝 Rédaction scientifique
- [ ] Résumer les résultats quantitatifs avec tableaux et figures.
- [ ] Mettre en avant les points de divergence majeurs.
- [ ] Proposer des interprétations possibles (sources de biais, qualité des données).
- [ ] Préparer une première version d’article (introduction, méthodes, résultats, discussion).

## 🚀 Étapes suivantes
- [ ] Définir le plan de soumission (revues / conférences pertinentes).
- [ ] Étendre l’analyse à d’autres régions pour valider la robustesse.
- [ ] Explorer la généralisation à d’autres bases de données routières.