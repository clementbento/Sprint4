# -*- coding: utf-8 -*-
from threading import Thread
from Agent import *
import time
from math import pi
import Ihm


import Transmission

class AGV(Agent):
    '''
    classdocs
    '''
    def __init__(self,ihm,ide,pos,postes,tps,type):
        '''
        Constructor
        '''
        self.presPorte=False            # Boolean présence de porte
        self.pos=pos                    # Tableau de la position
        self.id=ide                     # Identifiant de la porte
        self.ihm=ihm                    # Ihm associé
        self.stop=1                     # Variable qui indique si la porte est arretée ou en mouvement
        self.etat="En attente"          # Etat de la porte
        self.type=type                  # Porte avant(AV) ou arriere(AR)
        self.modifs=[]                  # Liste des modif recues par la porte
        self.postes=postes              # Liste des postes par lesquels la porte doit passer
        self.xd,self.xg1,self.xg2=0,0,0 # Variables utiles pour le déplacement le long des cercles
        self.timeur=0                   # Timeur qui demarre le chrono pour le temps de production de la porte
        self.v=0                        # Vitesse de l'AGV
        self.p=self.ihm.p               # Integer qui multiplie ou divise la vitesse
        self.edit = False               # Mode edition ou non 
        self.tpsArret = 0               # Temps d'arret lors d'une opération sur un poste
        self.tpsScenar = tps            # Tps d'attente d'une porte pour pouvoir partir lors d'un sénario
        self.tpsCourse = 135/0.015      # Tps en seconde d'un tour de ligne sans arret
        self.timer = None
        Thread.__init__(self)           # Lancement de la fonction run
  

    def run(self):                                                  # fonction d’activité du thread

        time.sleep((self.id-1)*self.getTpsScenar()/self.getProp())
        self.etat = "En attente "
        print("Lancement de la porte n° ",self.id)
        self.Timer()
        #Transmission.StockageDonnees("Lancement de la porte n°",self.id,":")
        Transmission.EnvoiDonneeDirect(self.Temps(),self.id,self.type,"Lancement de la porte","")
        self.etat="Sur la ligne"
        print("Etat de la porte n°",self.id,"=",self.etat)
        #Transmission.StockageDonnees("La porte",self.id,"est en mouvement")
        Transmission.EnvoiDonneeDirect(self.Temps(),self.id,self.type,"Porte en mouvement","")
        self.timeur = time.time()
        self.circule()
        self.terminate()
        
    def circule(self):                          # Fonction qui fait avanver l'AGV pas à pas le long de la ligne

        while self.stop!=0 :
            self.setVitesse(self.getTpsCourse())
            while self.edit == True :               # Se met en pause lorsque le mode edition est activé
                time.sleep(0.01)
            if self.edit == False :  
                self.pos=self.ihm.deplacement(self.pos,self.id,self)
                self.ihm.detectionTags(self)
                time.sleep(0.01)
        
    def interuption(self):                                    # Détruit le canva et mets fin au Thread AGV
        self.stop=0
        del self.ihm.pep[self.ihm.pep.index(self)]
        #self.ihm.FenetrePrincipale.delete(self.ihm.ovales[self.id-1])



    def changeEtat(self,newetat) : 
        self.etat=newetat
    
        
    def ajoutModif(self,poste) :
        self.modifs.append(poste)   

    def setVitesse(self, tpscourse) :               # Renvoi la vitesse d'un AGV
        dc=(4*pi/3)*(self.ihm.h*2/10)               # Distance cercle -> distance a parcourir le long d'un cercle
        dl=self.ihm.w*6/10-0.173*self.ihm.h         # Distance ligne -> longueur a parcourir le long d'une ligne 
        self.v=((2*dc+2*dl)/tpscourse)*self.getProp()

    def modeEdition(self, bool):                    # Change en fonction de si la simulation est en mode etidion ou non 
        self.edit = bool

    def Timer(self):
        self.timer = time.time()

    def Temps(self):
        return round((time.time()-self.timer),3)

    
# Getters   
    def getTpsCourse(self):
        return self.tpsCourse

    def isPorte(self):
        return self.presPorte


    def getPosition(self):
        return self.pos

    def getId(self):
        return self.id

    def getIhm(self):
        return self.ihm

    def getEtat(self):
        return self.etat

    def getPostes(self):
        return self.postes
    

    def getType(self):
        return self.type

    def getModifs(self):
        return self.modifs

    def getVitesse(self):
        return self.v
    
    def getEdit(self):
        return self.edit

    def getXd(self):
        return self.xd

    def getXg1(self):
        return self.xg1

    def getXg2(self):
        return self.xg2

    def getProp(self):
        return self.ihm.p

    def getTpsArret(self):
        return self.tpsArret

    def getTpsScenar(self):
        return self.tpsScenar