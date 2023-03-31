# deploy-flask
# Les étapes de configuration de projet
## Etape1: Telechargement d'Anaconda 

 ```
https://www.anaconda.com/products/distribution
 ```
## Etape2: creation d'un nouvel environnement
Avant de commancer il faut telecharger le projet present sur ce repo github.
Dans cette étape il faut ovrir le terminal d'anaconda, puis naviguer vers le repertoire du projet et creer l'environnement python avec la commande suivante:

```
conda create -n myenv python=3.7
 ```
 
Puis l'activer la commande suivante:

```
conda activate myenv
 ```
 
 ## Etape3: installation des bibiotheques 
 
 Comme on peut remarquer il y a un fichier requirements.txt qu'on va utilisé pour telecharger toute les bibliotheques python dont on aura besoin avec la commande suivante 
 
 ```
pip install -r requirements.txt
 ```
 
  ## Etape4: demarrer le serveur flask
  
  C'est la dernier étape dans laquel on va demarrer le serveur de notre projet avec la commande suivante:
  
 ```
flask run
 ```
 
 puis vous pouvez consulter la page sur un navigateur (preferablement firefox) en utilisant  localhost:5000/
