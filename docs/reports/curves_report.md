# Courbure — Analyse des virages

Ce rapport se concentre sur les courbes détectées (séquences à forte courbure/faible rayon) et leur comparaison OSM vs BD TOPO.

## Indicateurs clés (KPIs)

|                |   count |          mean |        median |          std |          q25 |           q75 |          iqr |
|:---------------|--------:|--------------:|--------------:|-------------:|-------------:|--------------:|-------------:|
| diff_r_min     |    5677 |   5.08358e+07 |   5.44279e+07 |  1.80566e+07 |   3.7993e+07 |   6.69628e+07 |  2.89698e+07 |
| diff_kappa_max |    5677 |  -0.0209203   |  -0.0167141   |  0.0160313   |  -0.0301382  |  -0.00818493  |  0.0219532   |
| alat50_diff    |    5677 |  -7.32115     |  -6.74745     |  4.28331     | -12.8601     |  -3.34716     |  9.5129      |
| alat80_diff    |    5677 | -18.7422      | -17.2735      | 10.9653      | -32.9218     |  -8.56873     | 24.353       |
| alat110_diff   |    5677 | -35.4344      | -32.6577      | 20.7312      | -62.2427     | -16.2003      | 46.0424      |

## Figures

![Profil moyen de courbure](../assets/reports/curves_20250922_174247/mean_kappa_profile.png)
