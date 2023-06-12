# GIO2-HeatMaps
Calcul parallèle de heatmap de traces GPX randonnée et sports de montagne

## Organisation
Le dossier Scheduler contient deux versions de Scheduler
La première permet le calcul des tuiles au niveau de zoom maximal puis la fusion des tuiles
La deuxième permet le calcul des tuiles par niveaux indépendamment
Nous avons opté pour la deuxième solution à cause de problèmes dans la première version de Scheduler

Le dossier Nodes contient le code et les différentes librairies à installer sur chaque machine qui sera un Node pour le calcul

## Etat du projet
En cet état le Scheduler contient un blocage lors de la fusion des tuiles qui n'a pas pu être résolu et le visualisateur Web n'a pas été résolu.
