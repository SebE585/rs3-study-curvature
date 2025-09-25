# ♻️ Reproductibilité

---

## 🖥️ Environnement
- ✅ Python 3.12
- ✅ Dépendances : **pandas**, **geopandas**, **pyrosm**, **pyogrio**, **shapely**, **tqdm**, **matplotlib**

---

## ⚙️ Configurations
- ✅ Paramètres d’ETL : `configs/config.yaml`
- ✅ Exemple :
  ```bash
  make etl
  python tools/compare_quick.py --in-dir data/ref/roadinfo
  python tools/compare_nearest.py --in-dir data/ref/roadinfo
  ```

---

## 📊 Résultats
- ✅ Export CSV + figures → `data/ref/roadinfo/`
- ✅ Documentation MkDocs → `mkdocs build`

---

## 🔧 Contrôle de version
- Le projet utilise **Git** pour le contrôle de version.
- Le code source est hébergé sur **GitHub** avec des workflows **GitHub Actions** configurés pour l’intégration continue (CI).
- Des hooks **pre-commit** sont mis en place pour garantir la qualité du code avant chaque commit (formatage, linting, tests unitaires).

---

## 📂 Provenance des données
- Les données sources proviennent principalement de **OpenStreetMap (OSM)** et de l’**IGN BDTopo**.
- Les fichiers bruts et transformés sont stockés dans le répertoire `rs3-data/` avec une organisation claire par source et version.
- Chaque dataset est versionné et documenté pour assurer la traçabilité des modifications et faciliter la comparaison entre versions.

---

## 🔄 Reproductibilité du pipeline
- Le pipeline de traitement est orchestré via un **Makefile** avec des cibles dédiées (`make etl`, `make clean`, etc.).
- Des graines aléatoires fixes sont utilisées dans les scripts pour assurer la reproductibilité des résultats.
- Le traitement est conçu pour être déterministe, évitant les dépendances sur des états externes ou variables.

---

## 🐍 Reproductibilité de l’environnement
- Un environnement Python isolé est fourni via un **virtualenv** dans le dossier `.venv`.
- Les dépendances sont gérées avec un fichier `pyproject.toml` et/ou `requirements.txt`.
- Pour recréer l’environnement, il suffit d’exécuter :
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

---

## 📌 Bonnes pratiques
- Documenter précisément tous les paramètres utilisés dans les traitements (fichiers de config, scripts).
- Stocker toutes les figures et sorties dans un dossier dédié `out/` pour faciliter la revue et l’archivage.
- Maintenir les scripts et le pipeline aussi déterministes que possible pour éviter les variations non souhaitées.
- Intégrer des vérifications automatiques via CI/CD pour assurer la qualité du code et la validité des résultats à chaque mise à jour.

---
