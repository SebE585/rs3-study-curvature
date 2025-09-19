# rs3-study-curvature

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
