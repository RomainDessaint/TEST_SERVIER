# TEST_SERVIER
Dépôt pour les réponses du test technique de Romain DESSAINT pour SERVIER


Réponses aux questions : 

----------------------------------------------------------------------------------------------------------------

1) Quels sont les éléments à considérer pour faire évoluer votre code afin qu’il puisse gérer de grosses
volumétries de données (fichiers de plusieurs To ou millions de fichiers par exemple) ?


Afin de gérer de grosses volumétries de données, les éléments à prendre en compte sont : 

- Les performances matérielles
- Le temps d'éxécution du traitement de ces volumes
- Les structures de données utilisées pour stocker les données

----------------------------------------------------------------------------------------------------------------

2) Pourriez-vous décrire les modifications qu’il faudrait apporter, s’il y en a, pour prendre en considération de
telles volumétries ?

- Remplacer les moyens de stockages des données dans le code. Utiliser des dataframes Pandas ou Spark afin de garder en mémoire les données.
- Paralléliser le traitement des données avec différents workers.
- Optimiser les lectures et écritures des fichiers sources et résultats.

----------------------------------------------------------------------------------------------------------------
