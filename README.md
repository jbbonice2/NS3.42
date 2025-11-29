# Exécution Automatique des Scénarios NS-3

Ce document décrit comment exécuter automatiquement tous les scripts de
simulation NS-3 correspondant aux scénarios **S1**, **S2**, **S3** et
**S4**.


## 1. Accéder au répertoire NS-3

Depuis la racine du projet, se déplacer vers le dossier NS-3 :

``` bash
cd /NS3.42/ns-3.42
```


## 2. Configurer NS-3

Avant d'exécuter les scripts, configurez NS-3 :

``` bash
./ns3 configure
./ns3 build
```

## 3. Aller dans le dossier `scratch/`

Les scripts d'exécution se trouvent dans le dossier `scratch` :

``` bash
cd scratch/
```


## 4. Exécuter les scénarios

Chaque bloc exécute les scripts d'un scénario donné **en parallèle**.\
La commande `wait` permet d'attendre la fin de tous les scripts du
scénario avant de lancer le suivant.


### Scénario S1

``` bash
for f in run_s1*.sh; do
    chmod +x "$f"
    bash "$f" &
done
wait
```


### Scénario S2

``` bash
for f in run_s2*.sh; do
    chmod +x "$f"
    bash "$f" &
done
wait
```



### Scénario S3

``` bash
for f in run_s3*.sh; do
    chmod +x "$f"
    bash "$f" &
done
wait
```


### Scénario S4

``` bash
for f in run_s4*.sh; do
    chmod +x "$f"
    bash "$f" &
done
wait
```


##  Notes Importantes

-   Les scripts doivent suivre la nomenclature :
    -   `run_s1*.sh`
    -   `run_s2*.sh`
    -   `run_s3*.sh`
    -   `run_s4*.sh`
-   Tous les scripts sont exécutés en parallèle grâce au symbole `&`.
-   `wait` assure que les simulations d'un scénario terminent avant de
    commencer le suivant.
-   L'exécution en parallèle est recommandée pour profiter de machines
    multicœurs.
##  Output    
-   Une fois terminer tu te deplace dans le doissier
  ``` bash
cd /NS3.42/ns-3.42
```
-   Tu verras le dossier nomme resulsfinal qui est le output
-   Tu cree une branche results et push ce dossier dans la branche 



