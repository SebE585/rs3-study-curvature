# Méthodes de calcul de la courbure


Présentation des différentes méthodes implémentées dans l’étude RS3 pour le calcul de la courbure d'une trajectoire discrète ou continue.

## 1. Dérivée des coordonnées

### Description
Cette méthode consiste à calculer la courbure à partir des dérivées premières et secondes des coordonnées de la courbe, généralement en paramétrant la courbe par rapport à l'abscisse curviligne ou à un paramètre \( t \).

### Formule
Pour une courbe plane paramétrée par \( t \), avec \( (x(t), y(t)) \), la courbure s'exprime :

$$
\kappa(t) = \frac{|x'(t) y''(t) - y'(t) x''(t)|}{\left( x'(t)^2 + y'(t)^2 \right)^{3/2}}
$$

### Hypothèses
- La courbe est suffisamment régulière pour admettre des dérivées premières et secondes.
- Les points sont suffisamment proches pour que l’approximation numérique soit valide.

### Avantages
- Simple à implémenter numériquement.
- Applicable à tout type de courbe discrétisée.

### Inconvénients
- Sensible au bruit (les dérivées amplifient les erreurs).
- Nécessite un lissage préalable si les données sont bruitées.

### Exemple d’utilisation
Soit une série de points \((x_i, y_i)\) mesurés à intervalles réguliers. On peut approximer les dérivées par différences finies :
$$
x'(t_i) \approx \frac{x_{i+1} - x_{i-1}}{2h}, \quad x''(t_i) \approx \frac{x_{i+1} - 2x_i + x_{i-1}}{h^2}
$$
Puis calculer la courbure en chaque point \(i\) avec la formule ci-dessus.

---

## 2. Ajustement par cercle

### Description
Cette méthode consiste à ajuster un cercle aux points voisins d’un point donné, la courbure étant l’inverse du rayon du cercle obtenu.

### Formule
Pour trois points consécutifs \(A(x_1, y_1)\), \(B(x_2, y_2)\), \(C(x_3, y_3)\), le rayon du cercle passant par ces points est donné par :
$$
R = \frac{|AB| \cdot |BC| \cdot |CA|}{2 | \Delta |}
$$
où \( | \Delta | \) est l’aire du triangle \(ABC\), calculée par :
$$
|\Delta| = \frac{1}{2} | x_1(y_2 - y_3) + x_2(y_3 - y_1) + x_3(y_1 - y_2) |
$$
La courbure en \(B\) est alors \( \kappa = 1/R \).

### Hypothèses
- Les trois points ne sont pas alignés.
- L’écart entre les points doit être adapté à l’échelle de la courbe.

### Avantages
- Moins sensible au bruit que la méthode des dérivées.
- Donne une interprétation géométrique directe.

### Inconvénients
- Dépend du choix des points voisins.
- Peut donner des résultats aberrants si les points sont quasi alignés.

### Exemple d’utilisation
Pour chaque point \(B\) de la trajectoire (sauf aux bords), sélectionner les points voisins \(A\) et \(C\), calculer le rayon du cercle passant par ces trois points, puis en déduire la courbure.

---

## 3. Interpolation par splines

### Description
La courbe discrète est interpolée par une spline (généralement cubique), ce qui permet de calculer analytiquement les dérivées nécessaires à la courbure.

### Formule
Après interpolation spline, la courbe devient une fonction \( (x(t), y(t)) \) régulière. La courbure s'exprime alors comme pour la méthode des dérivées :
$$
\kappa(t) = \frac{|x'(t) y''(t) - y'(t) x''(t)|}{\left( x'(t)^2 + y'(t)^2 \right)^{3/2}}
$$
où les dérivées sont calculées analytiquement à partir des polynômes de la spline.

### Hypothèses
- La spline est une bonne approximation de la trajectoire réelle.
- Les points d'interpolation sont correctement espacés.

### Avantages
- Lissage automatique de la courbe.
- Dérivées analytiques précises.

### Inconvénients
- Plus complexe à mettre en œuvre.
- Peut introduire des artefacts si la spline est mal paramétrée.

### Exemple d’utilisation
Interpoler la trajectoire par une spline cubique, puis calculer la courbure à chaque point d’intérêt en utilisant les dérivées analytiques fournies par la spline.
