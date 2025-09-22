# Étude comparative de la courbure routière entre OSM et BD TOPO
## Introduction
- Contexte de la qualité des données routières pour la simulation et la mobilité.
- Intérêt de la courbure routière (sécurité, modélisation, télématique).
- Objectif : comparer OSM et BD TOPO sur plusieurs métriques (longueur, rayon, courbure) en France.

*À développer : contexte scientifique, état de l’art, enjeux pratiques.*

## Méthodes
### Jeux de données
- OSM (extraction nationale)
- BD TOPO (IGN)
### Prétraitement et appariement
- Segmentation en tronçons homogènes.
- Appariement spatial (20 / 30 / 50 m).
### Métriques étudiées
- Longueur de segment.
- Rayon minimal et rayon au 85e centile.
- Courbure moyenne.
### Analyses statistiques
- Tests statistiques : Welch t-test, Kolmogorov–Smirnov, Mann–Whitney.
- Tailles d’effet (Cohen’s d, Cliff’s delta).
- Analyses par classe de route.
- Exploration des biais (distance d’appariement, vitesses, pente).

*À compléter avec schémas, équations, détails techniques (matching, filtres, pipeline RS3).*

## Résultats
### Comparaison globale
- Différences significatives entre OSM et BD TOPO.
- Distribution des longueurs et rayons.

*À insérer : tableau des tests globaux / distributions par classe / bias sweep.*

### Par classe de route
- Résultats des boxplots et violon plots.
- Classes montrant des écarts systématiques (motorway, trunk, etc.).

*Figure X à insérer*

### Sensibilité à la distance d’appariement
- Impact de 20 m vs 30 m vs 50 m.
- Taux d’appariements réussis.

*Figure Y à insérer*

### Autres biais explorés
- Influence de la pente et des vitesses.

*Figure Z à insérer*

## Discussion
- Interprétation des divergences observées.
- Qualité et granularité des bases de données.
- Biais urbain/rural (à compléter).
- Limites de l’étude (zone restreinte, métriques simplifiées).
- Perspectives (autres régions, autres bases de données).

*À développer : interprétation des résultats, comparaison avec littérature, implications scientifiques.*

## Conclusion
- Synthèse des principaux résultats.
- Intérêt pour la simulation et la mobilité.
- Perspectives de soumission.

*À finaliser : messages clés, perspectives de soumission (conférence/journal ciblé).*