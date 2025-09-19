# rs3-study-curvature

[![CI](https://github.com/SebE585/rs3-study-curvature/actions/workflows/ci.yml/badge.svg)](https://github.com/SebE585/rs3-study-curvature/actions/workflows/ci.yml)
[![Deploy Docs](https://github.com/SebE585/rs3-study-curvature/actions/workflows/pages.yml/badge.svg)](https://github.com/SebE585/rs3-study-curvature/actions/workflows/pages.yml)
[![Docs – en ligne](https://img.shields.io/badge/docs-online-brightgreen)](https://sebe585.github.io/rs3-study-curvature/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue.svg)](https://www.python.org/)
[![Status: prototype](https://img.shields.io/badge/status-research%20prototype-orange)](#)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-sebastienedet-blue?logo=linkedin)](https://www.linkedin.com/in/sebastienedet/)


## 🚀 Présentation

RoadSimulator3 est une solution avancée de simulation de trajets véhicules intégrant GPS,
IMU et gyroscope pour générer des données réalistes à haute fréquence (10 Hz). Unique
sur le marché, elle fusionne les technologies de navigation, l'inertie et les profils de
conduite comportementale pour créer des trajets synthétiques hyper-réalistes.

Conçu pour les industriels de la mobilité, les chercheurs en IA embarquée et les startups
en conduite autonome, RoadSimulator3 permet de prototyper, tester et valider des
algorithmes sans coûts logistiques réels.

Étude amont sur les **rayons de courbure routiers** (BD TOPO + DEM) et impact sur la simulation inertielle (\(a_\text{lat}=v^2/r\)) dans RoadSimulator3. Repo prêt pour GitHub : code Python (ETL + stats), tests, et **article scientifique** avec **MkDocs**.

## ⚙️ Installation rapide
```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
```

## 🏗️ Construire le jeu dérivé (curvature)
1. Placez vos fichiers dans `data/raw/` :
   - `bdtopo_transport.gpkg`
   - `dem.tif` (optionnel)
2. Copiez et éditez `configs/config.example.yaml`.
3. Lancez l'ETL :
```bash
python -m rs3_study_curvature.cli.build_curvature --config configs/config.yaml
```

## 🧪 Tests
```bash
pytest -q
```

## 📝 Paper (MkDocs)
```bash
mkdocs serve  # preview local
```
Déploiement GitHub Pages automatisé via GitHub Actions (`.github/workflows/pages.yml`).

## Licence
MIT (code) — citez ce dépôt si vous réutilisez les scripts.

## 📊 Business Model Canvas

**Partenaires clés**  
- Instituts de recherche / universités  
- Fournisseurs de données (IGN, OpenWeatherMap)  
- Plateformes cloud et IA  
- Éditeurs de logiciels télématiques  

**Activités clés**  
- Développement logiciel (simulateur, API, UI web)  
- R&D sur la simulation inertielle  
- Création de datasets synthétiques  
- Maintenance Docker / API  
- Support et consulting  

**Propositions de valeur**  
- Simulateur inertiel réaliste unique  
- API modulable pour intégration data science  
- Simulation haute fréquence avec événements calibrés  
- Outils de visualisation prêts à l'emploi  
- Tests de robustesse pour algorithmes embarqués  

**Relations clients**  
- Support technique personnalisé  
- Documentation complète  
- Accès Git privé / SaaS  
- Formations et workshops  

**Canaux**  
- Marketplace logiciels  
- GitHub / GitLab  
- Conférences et publications scientifiques  
- Webinars, démonstrations  

**Segments clients**  
- Constructeurs automobiles  
- Éditeurs de logiciels télématiques  
- Équipes R&D en mobilité  
- Sociétés d’assurance  
- Acteurs smart city  

**Ressources clés**  
- Expertise scientifique et algorithmique  
- Infrastructure cloud  
- Code source et pipelines Docker  
- Base de données réalistes synthétiques  

**Structure de coûts**  
- Développement logiciel  
- Coût des données tierces (IGN, météo)  
- Maintenance infrastructure cloud  
- R&D et salaires  

**Flux de revenus**  
- Licences / abonnements  
- Accès API payant (SaaS)  
- Consulting / formation  
- Jeux de données synthétiques premium  
