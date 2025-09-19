# 🚗 RoadSimulator3 — Étude comparative OSM vs BD TOPO

## 1. Contexte

La simulation réaliste de trajets véhicules exige une représentation fiable du réseau routier.  
Nous avons comparé deux sources majeures : **OpenStreetMap (OSM)** et **BD TOPO (IGN)**.  
Les données ont été traitées avec le pipeline RS3 (courbure, pente, densification).

## 2. Résultats principaux

- OSM → plus dense, segments courts (~50 m en moyenne).  
- BD TOPO → moins dense, mais segments longs (~170 m en moyenne).  
- Les statistiques montrent que la courbure extraite de BD TOPO est plus fine.  

Voir [compare_quick.md](compare_quick.md) pour les statistiques globales et [compare_nearest.md](compare_nearest.md) pour l’analyse locale.

## 3. Elevator Speech

> RoadSimulator3 est une solution avancée de simulation de trajets véhicules intégrant GPS, IMU et gyroscope pour générer des données réalistes à haute fréquence (10 Hz).  
> Unique sur le marché, elle fusionne les technologies de navigation, l'inertie et les profils de conduite comportementale pour créer des trajets synthétiques hyper-réalistes.  
> Conçue pour les industriels de la mobilité, les chercheurs en IA embarquée et les startups en conduite autonome, RoadSimulator3 permet de prototyper, tester et valider des algorithmes sans coûts logistiques réels.  

## 4. Business Model Canvas

### Partenaires Clés
- Instituts de recherche / universités  
- Fournisseurs de données (IGN, OpenWeatherMap)  
- Plateformes cloud et IA  
- Éditeurs de logiciels télématiques  

### Activités Clés
- Développement logiciel (simulateur, API, UI web)  
- R&D sur la simulation inertielle  
- Création de datasets synthétiques  
- Maintenance Docker / API  
- Support et consulting  

### Propositions de valeur
- Simulateur inertiel réaliste unique  
- API modulable pour intégration data science  
- Simulation haute fréquence avec événements calibrés  
- Outils de visualisation prêts à l'emploi  
- Validation de la robustesse des algorithmes embarqués  

### Relations clients
- Support technique personnalisé  
- Documentation complète  
- Accès Git privé / SaaS  
- Formations et workshops  

### Canaux
- Marketplace logiciels  
- GitHub / GitLab  
- Conférences / publications scientifiques  
- Webinars, démonstrations  

### Segments clients
- Constructeurs automobiles  
- Éditeurs de logiciels télématiques  
- Équipes R&D en mobilité  
- Sociétés d'assurance  
- Acteurs smart city  

### Ressources Clés
- Expertise scientifique et algorithmique  
- Infrastructure cloud  
- Code source et pipelines Docker  
- Base de données réalistes synthétiques  

### Structure de coûts
- Développement logiciel  
- Coût des données tierces (IGN, météo)  
- Maintenance infrastructure cloud  
- R&D et salaires  

### Flux de revenus
- Licences / abonnements  
- Accès API payant (SaaS)  
- Consulting / formation  
- Jeux de données synthétiques premium  

---

✍️ **Étapes suivantes** :  
- Intégrer les graphiques générés (`compare__hist_*.png`) dans la doc.  
- Rédiger une **discussion scientifique** sur les écarts observés (origine des biais, cas d’usage).  