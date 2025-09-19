# 🔬 Méthodologie

## Pré-traitement
- Reprojection EPSG:2154
- Simplification (tolérance 0,5 m)
- Densification (pas de 5 m)
- Longueur minimale 15 m

## Calcul de la courbure
- Cercle par 3 points consécutifs
- Rayon minimal (`radius_min_m`)
- Rayon au 85ᵉ percentile (`radius_p85_m`)
- Courbure moyenne (`curv_mean_1perm`)
- Gestion des infinis (segments rectilignes)

## Option pente
- Échantillonnage MNT bilinéaire
- Pente en %

## Sensibilités
- Étude d’ablation (pas de densification, tolérance de simplification)