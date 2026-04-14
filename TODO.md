# TODO — Étude de la courbure routière

> **Sub-TODO étude courbure.** Vue transverse :
> [`../ROADMAP.md`](../ROADMAP.md). Logique IP/publi :
> [`../WORKFLOW.md`](../WORKFLOW.md).

## 📊 Analyses statistiques
- [x] Implémenter des tests statistiques (t-test, KS-test, Mann-Whitney) pour comparer OSM vs BD TOPO.
- [x] Générer les distributions par métrique (longueur, rayon, courbure).
- [x] Calculer les écarts moyens et écarts-types par classe de route.

## 🛣️ Analyse par classe
- [x] Quantifier les écarts pour chaque classe normalisée (motorway, trunk, primary, secondary, etc.).
- [x] Visualiser les distributions avec boxplots et violon plots.
- [x] Identifier les classes présentant des écarts systématiques.

## 🔍 Exploration des biais
- [x] Vérifier l’impact de la distance max d’appariement (20m / 30m / 50m).
- [x] Étudier la couverture spatiale (zones urbaines vs rurales).
- [x] Croiser avec d’autres attributs (vitesses, typologie, pente).

## 📝 Rédaction scientifique
- [x] Résumer les résultats quantitatifs avec tableaux et figures.
- [x] Mettre en avant les points de divergence majeurs.
- [x] Proposer des interprétations possibles (sources de biais, qualité des données).
- [x] Préparer une première version d’article (introduction, méthodes, résultats, discussion).
- [ ] Intégrer les résultats sur la courbure (profils, KPIs globaux et par classe) dans l’article.
- [ ] Rédiger une discussion approfondie sur les biais observés (longueur, rayon, courbure).

## 🚀 Étapes suivantes
- [ ] Définir le plan de soumission (revues / conférences pertinentes) et soumettre l'article.
- [ ] Étendre l’analyse à d’autres régions pour valider la robustesse (extension géographique).
- [ ] Explorer la généralisation à d’autres bases de données routières.
- [ ] Finaliser la rédaction et soumettre un draft interne pour relecture.
- [ ] Automatiser la génération complète (curves-all) et valider la reproductibilité des rapports.
- [ ] Compléter l’analyse des hotspots (cas locaux extrêmes) si pertinent.

---
_Statut des grandes étapes déjà réalisées :_
- [x] Analyses statistiques
- [x] Analyse par classe
- [x] Exploration biais
- [x] Rédaction scientifique partielle
