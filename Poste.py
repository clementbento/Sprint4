# -*- coding: utf-8 -*-
from tkinter import *

class Poste():
    '''
    classdocs
    '''

    def __init__(self, nom, type, position, action,tcAV, tcAR):
        '''
        Constructor
        '''
        self.id = 0                #int
        self.nom = nom             #string
        self.type = type           #string
        self.position = position   #int
        self.etat = False          #boolean
        self.action = action       #string
        self.tpscycleAV = tcAV     #Temps necessaire pour effectuer l'action sur une porte Avant
        self.tpscycleAR = tcAR     #Temps necessaire pour effectuer l'action sur une porte Arriere

    def getId(self):
        return self.id

    def getNom(self):
        return self.nom

    def getType(self):
        return self.type

    def getPosition(self):
        return self.position

    def getEtat(self):
        return self.etat
    
    def getAction(self):
        return self.action

    def effectuer(self, porte):
        porte.fait.append(self.action)
    
    def getTpsCycleAV(self) :
        return self.tpscycleAV
        
    def getTpsCycleAR(self):
        return self.tpscycleAR
        
print("INITIALISATION POSTE")