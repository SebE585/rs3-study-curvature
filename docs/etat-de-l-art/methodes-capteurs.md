# Méthodes basées sur les capteurs

Les méthodes basées sur les capteurs reposent sur l'utilisation de dispositifs embarqués pour mesurer des grandeurs physiques permettant de caractériser la géométrie et la dynamique d'un système. Ces capteurs fournissent des données brutes qui, après traitement et fusion, permettent d'estimer avec précision des variables d'intérêt telles que la position, la vitesse, ou la forme du terrain.

## IMU (Inertial Measurement Unit)

Les IMU mesurent les accélérations linéaires et les vitesses angulaires à l’aide d’accéléromètres et de gyroscopes intégrés.
- **Précision** : généralement bonne à court terme, mais sujette à la dérive cumulative.
- **Fréquence** : typiquement entre 10 Hz et 200 Hz selon les modèles.
- **Contraintes** : la dérive des mesures impose une fusion avec d’autres capteurs comme le GPS ou l’odométrie pour corriger les erreurs et obtenir une estimation stable.

## Lidar

Le lidar utilise un laser pour mesurer des distances précises en balayant l’environnement.
- **Précision** : centimétrique, adaptée à la détection fine de la géométrie.
- **Fréquence** : généralement entre 5 Hz et 20 Hz.
- **Contraintes** : coût et poids relativement élevés, sensibilité aux conditions météorologiques défavorables (pluie, brouillard, neige).

## Radar

Le radar émet des ondes radio pour détecter la distance et la vitesse des objets.
- **Précision** : moins fine que le lidar, résolution limitée pour la micro-géométrie.
- **Fréquence** : entre 10 Hz et 50 Hz.
- **Contraintes** : très robuste aux conditions météorologiques, mais la résolution spatiale est insuffisante pour certaines applications nécessitant une grande précision.

## Comparaison des capteurs

| Capteur | Précision               | Fréquence typique | Contraintes                                      |
|---------|------------------------|-------------------|-------------------------------------------------|
| IMU     | Bonne à court terme, dérive | 10–200 Hz         | Dérive, nécessite fusion avec GPS/odométrie     |
| Lidar   | Centimétrique          | 5–20 Hz           | Coût, poids, sensibilité météo                   |
| Radar   | Résolution limitée     | 10–50 Hz          | Moins précis, mais robuste aux conditions météo |

## Conclusion

Les méthodes basées sur les capteurs embarqués offrent une solution efficace pour la collecte de données en temps réel. Cependant, pour produire des référentiels robustes et fiables, il est nécessaire de mettre en œuvre des algorithmes complexes de fusion de données et de réaliser des calibrations rigoureuses. Ces contraintes techniques sont indispensables pour compenser les limites propres à chaque capteur et garantir la qualité des mesures dans des environnements variés.
