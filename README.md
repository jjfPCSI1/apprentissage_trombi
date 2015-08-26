# Apprentissage de trombinoscope

## Auteur 

Vincent GRENARD (vince.grenard@laposte.net)

## But du programme 

Apprendre une liste de nom correspondant à des images 
                   (trombinoscope d'élèves par exemple)

## Bibliothèques requises 

* PyQt4 pour l'aspect graphique, 
* numpy

## Fichiers requis 

* ok.jpg/pas_ok.jpg pour afficher si l'on se trompe (ou pas)
* les images dont on veut apprendre les noms en .jpg dans un sous répertoire `Photos/` par rapport au .py
* un fichier liste_eleve.txt contenant les noms/prénoms. La liste doit être présentée sous la forme :

```
nom1[tabulation]prénom1[tabulation]nom_image1
nom2[tabulation]prénom2[tabulation]nom_image2
...
```

Il est possible de rajouter des noms et des images, mais il faut le faire à la
fin du fichier `.txt`

Le programme crée un fichier de "score" pour mémoriser les erreurs pour chaque 
image.

## Fonctionnement  

Le programme affiche une image et attend que l'on rentre le nom correspondant 
et appuye sur entrée. En cas d'erreur, il faut recopier le bon nom pour pouvoir
passer à la suite.
Les noms sont acceptés sous la forme "prénom nom" ou "nom prénom" sans tenir 
compte des accents, caractères spéciaux ni des majuscules.

## Versionning

v3 : Tentative d'amélioration de l'algorithme pour poser des questions en tenant 
    compte du temps : http://en.wikipedia.org/wiki/Spaced_repetition
v5 : Tentative d'amélioration en 
    mettant une liste de noms pour les photos
    comme troisième colonne du fichier liste_elèves
