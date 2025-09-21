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