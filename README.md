# Apprentissage de trombinoscope

## Auteur 

Vincent GRENARD (vince.grenard@laposte.net)

## But du programme 

Apprendre une liste de nom correspondant � des images 
                   (trombinoscope d'�l�ves par exemple)

## Biblioth�ques requises 

* PyQt4 pour l'aspect graphique, 
* numpy

## Fichiers requis 

* ok.jpg/pas_ok.jpg pour afficher si l'on se trompe (ou pas)
* les images dont on veut apprendre les noms en .jpg dans un sous r�pertoire `Photos/` par rapport au .py
* un fichier liste_eleve.txt contenant les noms/pr�noms. La liste doit �tre pr�sent�e sous la forme :

```
nom1[tabulation]pr�nom1[tabulation]nom_image1
nom2[tabulation]pr�nom2[tabulation]nom_image2
...
```

Il est possible de rajouter des noms et des images, mais il faut le faire � la
fin du fichier `.txt`

Le programme cr�e un fichier de "score" pour m�moriser les erreurs pour chaque 
image.

## Fonctionnement  

Le programme affiche une image et attend que l'on rentre le nom correspondant 
et appuye sur entr�e. En cas d'erreur, il faut recopier le bon nom pour pouvoir
passer � la suite.
Les noms sont accept�s sous la forme "pr�nom nom" ou "nom pr�nom" sans tenir 
compte des accents, caract�res sp�ciaux ni des majuscules.

## Versionning

v3 : Tentative d'am�lioration de l'algorithme pour poser des questions en tenant 
    compte du temps : http://en.wikipedia.org/wiki/Spaced_repetition
v5 : Tentative d'am�lioration en 
    mettant une liste de noms pour les photos
    comme troisi�me colonne du fichier liste_el�ves
