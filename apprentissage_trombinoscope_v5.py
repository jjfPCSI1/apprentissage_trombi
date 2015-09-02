# -*- coding: utf-8 -*-
"""
auteur : Vincent GRENARD (vince.grenard@laposte.net)
but du programme : apprendre une liste de nom correspondant à des images 
                   (trombinoscope d'élèves par exemple)
bibliothèques requises : * PyQt4 pour l'aspect graphique, 
                         * numpy
fichiers requis : * ok.jpg/pas_ok.jpg pour afficher si l'on se trompe (ou pas)
                  * les images dont on veut apprendre les noms en .jpg dans un 
                    sous répertoire Photos par rapport au .py
                  * un fichier liste_eleve.txt contenant les noms/prénoms
La liste doit être présentée sous la forme :

nom1[tabulation]prénom1[tabulation]nom_image1
nom2[tabulation]prénom2[tabulation]nom_image2
...

Il est possible de rajouter des noms et des images, mais il faut le faire à la
fin du fichier .txt

Le programme crée un fichier de "score" pour mémoriser les erreurs pour chaque 
image.

fonctionnement : 
Le programme affiche une image et attend que l'on rentre le nom correspondant 
et appuye sur entrée. En cas d'erreur, il faut recopier le bon nom pour pouvoir
passer à la suite.
Les noms sont acceptés sous la forme "prénom nom" ou "nom prénom" sans tenir 
compte des accents, caractères spéciaux ni des majuscules.


v3 : Tentative d'amélioration de l'algorithme pour poser des questions en tennant 
    compte du temps : http://en.wikipedia.org/wiki/Spaced_repetition
v5 : tentative d'amélioration en 
    mettant une liste de noms pour les photos
    comme troisième colonne du fichier liste_elèves

"""


import unicodedata
from PyQt4 import QtGui, QtCore
import sys
import numpy.random as rd
import numpy as np
import time
#pour gérer le temps avec time.mktime(time.gmtime())
#espace entre deux révisions : 
# 5 s ;  25 s ; 2 min ; 10 min ; 1 h ; 5 h ; 1 jour ; 5 jour ; 25 j ; 4 mois ; 2 ans
jour = 3600 * 24
mois = jour * 30.5
annee = jour * 365.25
delta_t = (5, 25, 2*60, 10*60, 1*3600, 5*3600, jour, 5*jour, 25*jour, 4*mois, 2*annee)


def convert_heure(sec):
    '''converti une durée en sec en anne mois jour etc...
    et renvoi une chaine de caractère'''
    duree = [annee, mois, jour, 3600, 60]
    duree_texte = ['an', 'mois', 'j', 'h', 'min']
    date = [0]*len(duree)
    for i,d in enumerate(duree):
        date[i] = sec // d
        sec = sec % d
    texte=''
    for i,d in enumerate(date):
        if d!=0:
            texte += str(int(d)) + ' ' + duree_texte[i] + ' '
    texte += str(sec) + ' s'
    return texte
    
def QtSleep(temps,fonction):
    QtCore.QTimer.singleShot(temps,fonction)


class mainWindow(QtGui.QWidget):
    def __init__(self):
        self.ui_initialise = False
        super(mainWindow,self).__init__()
        self.charge_noms_eleves()
        self.charge_scores()
        self.nombre_aleatoire  = self.tire_nb_aleatoire()
        self.initUI()
    
    def center(self):
        """centre la fenêtre au milieu de l'écran d'ordinateur"""
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def initUI(self):
        taille_dispo = QtGui.QDesktopWidget().availableGeometry()
        font = QtGui.QFont('Serif', 16, QtGui.QFont.Light)
        self.mode_correction = False
                
        
        if self.pas_de_test_a_faire:
            self.nombre_aleatoire = 0
        
        #boite dans laquelle on tape le nom
        self.Dialogue = QtGui.QTextEdit(self)
        self.Dialogue.setMaximumHeight(50)
        self.Dialogue.setText('')
        self.Dialogue.textChanged.connect(self.OnTextChanged)
        self.Dialogue.setFont(font)
            
        #widget contenant l'image        
        self.Image = QtGui.QLabel("",self)
        self.Image.setMaximumHeight(taille_dispo.height()-100)
        self.Image.setMaximumWidth(taille_dispo.width()-50)
        self.Image.setMinimumWidth(taille_dispo.width()//3)
        self.Image.setMinimumHeight(taille_dispo.height()//3)
        self.Image.setAlignment(QtCore.Qt.AlignCenter)
        self.Image.setStyleSheet("border: 3px;")
        self.Image.setFont(font)
        im = QtGui.QPixmap("./Photos/" + self.nom_photos[self.nombre_aleatoire]+".jpg")
        #on agrandit l'image le plus possible tout en gardant le rapport d'aspect
        im = im.scaled(self.Image.width(),self.Image.height(),QtCore.Qt.KeepAspectRatio)
        self.Image.setPixmap(im)
        
        #texte corrigé en cas d'erreur
        #on pourrait faire comme dans memrise et attendre que l'on tape la correction avant de passer à la suite
        #self.TexteCorrection = QtGui.QLabel(self.Image)
        self.TexteCorrection = QtGui.QLabel(self)
        self.TexteCorrection.setAutoFillBackground(True)
        self.TexteCorrection.setAlignment(QtCore.Qt.AlignCenter)
        self.TexteCorrection.setFont(font)
        self.TexteCorrection.setText('  Correction  ')
        self.TexteCorrection.hide()
        
        #layout pour centrer le texte corrigé
        hbox0 = QtGui.QHBoxLayout()
        hbox0.addStretch(1)
        hbox0.addWidget(self.TexteCorrection)
        hbox0.addStretch(1)
        vbox0 = QtGui.QVBoxLayout()
        vbox0.addStretch(20)
        vbox0.addLayout(hbox0)          
        vbox0.addStretch(1)
        self.Image.setLayout(vbox0)

        
        #boite qui indique ce que l'on attend
        self.LabelDialogue = QtGui.QLabel(self)
        self.LabelDialogue.setText('Nom :')
        
        #disposition : une fenêtre en haut et les 2 autres dessous
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addStretch(3)
        hbox1.addWidget(self.Image)
        hbox1.addStretch(3)
        
        hbox2 = QtGui.QHBoxLayout()
        hbox2.addStretch(3)
        hbox2.addWidget(self.LabelDialogue)
        hbox2.addStretch(1)        
        hbox2.addWidget(self.Dialogue)
        hbox2.addStretch(3)
        
        vbox = QtGui.QVBoxLayout()
        #vbox.addStretch(1)
        vbox.addLayout(hbox1)          
        #vbox.addStretch(1)
        vbox.addLayout(hbox2)        
        #vbox.addStretch(1)

        self.setLayout(vbox)
        self.center()
        self.show()#force l'affichage
        

        #si pas de test à faire, on attend un peu et on reregarde plus tard
        self.ui_initialise = True
        if self.pas_de_test_a_faire:
            QtSleep(33,self.pause)
        

#        
    def juste(self):
        """Si le nom a été bien rentré, il faut augmenter le score d'indice"""
        #modifier le score
        self.Liste_score[self.nombre_aleatoire] = self.Liste_score[self.nombre_aleatoire] + [1]
        self.go_on()
    
    def faux(self):
        """Si le nom a été mal rentré, il faut diminuer le score d'indice"""
        self.Liste_score[self.nombre_aleatoire] = self.Liste_score[self.nombre_aleatoire] + [-2]
        self.correction()
    
    def presque_juste(self):
        #self.Liste_score[self.nombre_aleatoire] = self.Liste_score[self.nombre_aleatoire] + [0]
        """Si le nom a été presque bien rentré, on rajoute un 0"""
        self.Liste_score[self.nombre_aleatoire] = self.Liste_score[self.nombre_aleatoire] + [0]
        self.correction()

    def correction(self):
        """ afficher le bon résultat, il faudrait sans doute faire comme memrise 
        et attendre que le bon résultat soit tapé avant de passer à la suite 
        un moyen serait de mettre un booléen correct = True ou false et traiter
        l'évènement différemment en fonction de la valeur du booléen        
        """
        self.TexteCorrection.setText('  Vous avez répondu :  ' + self.nom_propose + '\n La bonne réponse était : ' + self.prenoms[self.nombre_aleatoire].capitalize() + ' ' + self.noms[self.nombre_aleatoire].upper() )
        self.TexteCorrection.show()
        self.TexteCorrection.setAutoFillBackground(True)
        im = QtGui.QPixmap("./Photos/" + self.nom_photos[self.nombre_aleatoire]+".jpg")
        im = im.scaled(self.Image.width(),self.Image.height(),QtCore.Qt.KeepAspectRatio)
        self.Image.setPixmap(im)
        
        self.mode_correction = True
        self.Dialogue.setEnabled(True)
        self.Dialogue.setFocus()
        #on attend que le bon résultat soit rentré pour passer à la suite
    
    def go_on_apres_pause(self):
        """après une pause, on cache la correction et on tire un nouveau nombre 
        aléatoire à tester"""
        self.TexteCorrection.hide()        
        self.nombre_aleatoire  = self.tire_nb_aleatoire()
        if not(self.pas_de_test_a_faire):
            im = QtGui.QPixmap("./Photos/" + self.nom_photos[self.nombre_aleatoire]+".jpg")
            im = im.scaled(self.Image.width(),self.Image.height(),QtCore.Qt.KeepAspectRatio)
            self.Image.setPixmap(im)
            self.Dialogue.setEnabled(True)
            self.Dialogue.setFocus()
        else:#si pas de test à faire, on repause
            QtSleep(33,self.pause)
    
    def go_on(self):
        self.TexteCorrection.hide()
        self.date_dernier_test[self.nombre_aleatoire] = time.mktime(time.gmtime()) 
        #on prend gmtime pour ne pas avoir de problème si je prends l'avion pour aller à l'étranger
        #si on voulait prendre local time, il suffirait de faire time.time()
        self.save_scores()
        self.nombre_aleatoire  = self.tire_nb_aleatoire()
        if not(self.pas_de_test_a_faire):
            im = QtGui.QPixmap("./Photos/" + self.nom_photos[self.nombre_aleatoire]+".jpg")
            im = im.scaled(self.Image.width(),self.Image.height(),QtCore.Qt.KeepAspectRatio)
            self.Image.setPixmap(im)
            self.Dialogue.setEnabled(True)
            self.Dialogue.setFocus()
        else:
            QtSleep(33,self.pause)
    
    def charge_noms_eleves(self):
        """ lit le fichier liste_eleve.txt pour en tirer la liste des élèves et
            les images correspondantes. La liste doit être présentée sous la
            forme
            nom[tabulation]prénom[tabulation]nom_image
            Les images sont supposées en jpg et enregistrée dans un sous-réper-
            -toire Photos
        """
        f = open('liste_eleve.txt')
        liste_eleve = f.read().strip().split('\n')
        f.close()
        self.noms = [m.split('\t')[0] for m in liste_eleve]
        self.prenoms = [m.split('\t')[1] for m in liste_eleve]
        self.nom_photos = [m.split('\t')[2] for m in liste_eleve]
        self.nbEleve = len(self.noms)
        self.PrenomNom = [self.prenoms[i] + " " + self.noms[i] for i in range(self.nbEleve)]
        self.NomPrenom = [self.noms[i] + " " + self.prenoms[i] for i in range(self.nbEleve)]

    
    def charge_scores(self):
        self.proba = [1] * self.nbEleve
        try:
            f = open('tableau_score_et_date','r')
        except:
            #si pas de tableau de score en mémoire
            self.Liste_score = [[0].copy()] * self.nbEleve # à charger
            self.date_dernier_test = [0] * self.nbEleve
            # -1 si juste 1 si faux 0 si petite faute
        else:
            t = f.readlines()
            f.close()
            self.Liste_score = [[]] * self.nbEleve
            self.date_dernier_test = [0] * self.nbEleve
            for ind,lignes in enumerate(t):
                x = lignes.strip().split('\t')
                self.Liste_score[ind] = [int(c) for c in x[:-1]]
                self.date_dernier_test[ind] = float(x[-1])
            for ind in range(self.nbEleve-len(t)):
                self.Liste_score[ind+len(t)] = [0]
        self.calcul_date()
        self.calcul_proba()
    
    def save_scores(self):
        texte=''
        for ind_E in range(self.nbEleve):
            texte += '\t'.join([str(n) for n in self.Liste_score[ind_E]])
            texte += '\t' + str(self.date_dernier_test[ind_E])
            if ind_E != self.nbEleve-1:
                texte += '\n'
        f = open('tableau_score_et_date','w+')
        f.write(texte)
        f.close()
        
    def calcul_proba(self):
        """
        Calcul les probabilités de tirer chaque élève en fonction des erreurs
        et réussite passées.
        """
        date = time.mktime(time.gmtime())
        for num_mot in range(self.nbEleve):
            if date < self.date_prochain_test[num_mot]:
                p = 0
            else:
                p = 1.0 # proba de base qu'on augmente ou diminue en fonction du nombre de succès
                for nb_essai in range( len(self.Liste_score[num_mot]) ):
                    x = -np.sign(self.Liste_score[num_mot][-1-nb_essai]) #je pars par la fin pour mettre plus de poids aux erreurs/succès récents
                    p = p * ( (2*( 1+ 1/(1+nb_essai) ) )**x )  #formule prise "au pif"
            self.proba[num_mot] = p
        
        #normalisation
        s = sum(self.proba)
        #il faut gérer le cas où j'ai tout appris : s = 0
        if s == 0:
            self.pas_de_test_a_faire = True
        else:
            self.pas_de_test_a_faire = False
            for num_mot in range(self.nbEleve):
                self.proba[num_mot] = self.proba[num_mot]/s
    
    def pause(self):
        """ s'il n'y a pas de test à faire, on fait une pause """
        date = time.mktime(time.gmtime())
        duree_avant_prochain = min(self.date_prochain_test) - date
        self.Image.setText('Vous avez assez \n travaillé pour le moment\n Prochain test dans \n' + convert_heure(duree_avant_prochain))
        if duree_avant_prochain >0:        
            QtSleep(33,self.pause)
        else:
            self.go_on_apres_pause()
        

    def calcul_date(self):
        #calcul la date de la prochaine interrogation en fonction des résultats
        #précédents et de la date de la dernière interrogation
        global delta_t
        self.date_prochain_test = [0] * self.nbEleve
        for num_mot in range(self.nbEleve):
            #pour chaque mot
            #si juste, on fait +1 dans les intervals, si faux on fait -2
            #si négatif à la fin, ça donne 0, si plus grand que le nombre d'interval, on mets 2 ans
            t = sum(self.Liste_score[num_mot])
            if t<0:
                t = 0 #le premier
            elif t>=len(delta_t):
                t = -1 #le dernier
            #sinon on garde t
            self.date_prochain_test[num_mot] = self.date_dernier_test[num_mot] + delta_t[t]
            #prochaine interro = dernier interro + le spacing correct
            
            
    
    def tire_nb_aleatoire(self):
        #idée : faire comme dans certains jeux vidéos pour choisir avec un seul
        #nombre aléatoire un "évènement"
        # Si j'ai 3 évènements de proba 35% 50% et 15%
        # alors je tire un nombre aléatoire entre 0 et 1
        # si ce nombre est entre 0 et 0.35, alors je choisis l'évènement 1
        # si ce nombre est entre 0.35 et 0.85, alors je choisis l'évènement 2
        # si ce nombre est entre 0.85 et 1, alors je choisis l'évènement 3
        self.calcul_date()
        self.calcul_proba()
        x = rd.rand()
        #je tire 1 nb aléaoitre
        # si x<proba[0], alors le nb tiré est 0
        # si sum(k=0,k<i-1,proba[k])<x<sum(k=0,k<i-1,proba[k]), alors le nb tiré est i
        # dis autrement, le nombre tiré est le plus petit nombre n tel que
        # x < proba[n]
        p = np.cumsum(self.proba)
        t = x > p
        return np.sum(t)
    
               
    def OnTextChanged(self):
        if self.mode_correction == True:
            #alors on verifie à chaque lettre rentré si c'est la bonne
            self.nom_propose = self.Dialogue.toPlainText()
            #On test sous la forme nom prénom et prénom nom
            note1 = test_complet_unicode(self.nom_propose, self.NomPrenom[self.nombre_aleatoire])
            note2 = test_complet_unicode(self.nom_propose, self.PrenomNom[self.nombre_aleatoire])
            
            if max([note1, note2]) == 1:
                #alors j'ai trouvé le bon nom
                self.mode_correction = False #on sort du mode de correction pour passer au mode test

                im = QtGui.QPixmap("ok.jpg")
                im = im.scaled(self.Image.width(),self.Image.height(),QtCore.Qt.KeepAspectRatio)
                self.Image.setPixmap(im)
                self.Dialogue.setText('')
                self.Dialogue.setDisabled(True)
                
                QtSleep(500,self.go_on)
        #sinon, on n'est pas en mode correction mais en mode test
        #on en prend en compte une fois que quelqu'un appuie sur entrée
        elif len(self.Dialogue.toPlainText())>0 and self.Dialogue.toPlainText()[-1] == '\n':
            #alors c'est que l'on a appuyé sur entré
            #on sauve le nom proposé
            self.Dialogue.setDisabled(True)
            self.nom_propose = self.Dialogue.toPlainText()[:-1]
            #et on vide la boite de dialogue
            self.Dialogue.setText('')
            
            #il faut ensuite comparer le nom proposé avec le bon nom
            #et corriger en cas de problème
            note1 = test_complet_unicode(self.nom_propose, self.NomPrenom[self.nombre_aleatoire])
            note2 = test_complet_unicode(self.nom_propose, self.PrenomNom[self.nombre_aleatoire])
            if max([note1, note2]) == 1:
                #alors j'ai trouvé le bon nom

                im = QtGui.QPixmap("ok.jpg")
                im = im.scaled(self.Image.width(),self.Image.height(),QtCore.Qt.KeepAspectRatio)
                self.Image.setPixmap(im)
                #self.center()
                QtSleep(1000,self.juste)
                
            elif max([note1, note2]) > 0.75:
                #c'est potable
                im = QtGui.QPixmap("ok.jpg")
                im = im.scaled(self.Image.width(),self.Image.height(),QtCore.Qt.KeepAspectRatio)
                self.Image.setPixmap(im)

                #self.center()
                QtSleep(1000,self.presque_juste)
            
                
            else:
                #FAIL !
                im = QtGui.QPixmap("pas_ok.jpg")
                im = im.scaled(self.Image.width(),self.Image.height(),QtCore.Qt.KeepAspectRatio)
                self.Image.setPixmap(im)

                #self.center()
                QtSleep(1000,self.faux)
                

            

    
    def keyPressEvent(self,e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.Dialogue.setText('')
    def resizeEvent(self,size):
        im = QtGui.QPixmap("./Photos/" + self.nom_photos[self.nombre_aleatoire]+".jpg")
        im = im.scaled(self.Image.width(),self.Image.height(),QtCore.Qt.KeepAspectRatio)
        self.Image.setPixmap(im)
        





#reconnaissance de caractère avec faute d'orthographe
#mot_ref='bonjour'
#mots=['bonjjour','bonou','bonhour','tom','bob','bonjour','Alain']
#
#mot_ref_s=mot_ref.lower()
#mots=[m.lower() for m in mots]
#notes=[0]*len(mots)
#
##si les 2 mots ont la même longueur, le moyen naif c'est de comparer lettre à lettre 
#mot_test=mots[1]
#
#
#    
def test_simple(s1,s2):
    #si les deux ont la meme longueurs
    assert len(s1) == len(s2)
    #alors on compare terme à terme
    s1 = np.array([c for c in s1])
    s2 = np.array([c for c in s2])
    return (s1 == s2).sum()/len(s1)

def test_manque_une_lettre(s1,s2):
    #s1 a une lettre de moins que s2
    resultat = 0
    for i in range(len(s2)):
        r = test_simple(s1,np.hstack( (s2[0:i],s2[i+1:]) ))
        if r > resultat:
            resultat = r
    return resultat * (len(s1))/len(s2)#penalité car manque une lettre, on ne peut pas renvoyer 1

def test_manque_deux_lettres(s1,s2):
    #s1 a deux lettres de moins que s2
    resultat=0
    for i in range(len(s2)):
        r = test_manque_une_lettre(s1,np.hstack( (s2[0:i],s2[i+1:]) ))
    if r > resultat:
            resultat = r
    return resultat * (len(s1))/len(s2)#penalité car manque une lettre, on ne peut pas renvoyer 1

def test_complet(s1,s2):
    if abs(len(s1)-len(s2))>2:#alors les deux mots sont vraiment trop différents ! 
        return 0
    r = 0
    s1 = np.array([c for c in s1])
    s2 = np.array([c for c in s2])
    if len(s1)==len(s2):
        r = test_simple(s1,s2)
    elif len(s1) == len(s2)-1:
        r = test_manque_une_lettre(s1,s2)
    elif len(s1) == len(s2)+1:
        r = test_manque_une_lettre(s2,s1)
    elif len(s1) == len(s2)-2:
        r = test_manque_deux_lettres(s1,s2)
    elif len(s1) == len(s2)+2:
        r = test_manque_deux_lettres(s2,s1)
    return r

def test_complet_unicode(s1,s2):
    if abs(len(s1)-len(s2))>2:#alors les deux mots sont vraiment trop différents ! 
        return 0
    s1 = s1.lower()  
    s1 = unicodedata.normalize('NFKD', s1).encode('ASCII', 'ignore').decode('ASCII')#pour enlever les caractères spéciaux
    s2 = s2.lower()  
    s2 = unicodedata.normalize('NFKD', s2).encode('ASCII', 'ignore').decode('ASCII')#pour enlever les caractères spéciaux

    r = 0
    s1 = np.array([c for c in s1])
    s2 = np.array([c for c in s2])
    if len(s1)==len(s2):
        r = test_simple(s1,s2)
    elif len(s1) == len(s2)-1:
        r = test_manque_une_lettre(s1,s2)
    elif len(s1) == len(s2)+1:
        r = test_manque_une_lettre(s2,s1)
    elif len(s1) == len(s2)-2:
        r = test_manque_deux_lettres(s1,s2)
    elif len(s1) == len(s2)+2:
        r = test_manque_deux_lettres(s2,s1)
    return r
    
def trouve_mot_dans_liste(m,liste):
    """ cherche dans la liste de mots liste le mot le plus proche de m
    
    renvoie un tupple avec 
    indice du mot le plus proche dans la liste,
    mot le plus proche dans la liste
    note associée à ce mot en terme de proximité
    """
  
    m = m.lower()  
    m = unicodedata.normalize('NFKD', m).encode('ASCII', 'ignore').decode('ASCII')#pour enlever les caractères spéciaux

    liste2 = [unicodedata.normalize('NFKD',mot.lower()).encode('ASCII', 'ignore').decode('ASCII') for mot in liste]
    notes = np.zeros(len(liste2))
#    for i in range(len(liste)):
#        notes[i] = test_complet(m,liste2[i])
    notes = [test_complet(m,liste2[i]) for i in range(len(liste))]
    ind_max=np.argmax(notes)#trouve l'objet ayant la meilleure "note", donc a priori le plus proche
    #renvoie son indice, l'objet et sa note.
    return ind_max,liste[ind_max],notes[ind_max]

    
        



App = QtGui.QApplication(sys.argv)
mainW = mainWindow()  
App.exec_()
