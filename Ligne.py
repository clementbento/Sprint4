# -*- coding: utf-8 -*-
from tkinter import *
import Poste

class Ligne():
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.postes=[]            # liste de [Poste]
        self.nbPostes=4           # int nombre de postes sur la zone supérieure de la ligne
        self.TagsPostes=[]        # liste de coordonés ==> [[int,int]]
        self.pep=[]               # liste de [AGV] en fonction


    def getAGVbyId(self,id):
        for agv in self.pep:
            if id==agv.id:return agv
        return None

    def getPEP(self):                          # return la liste [pep] d'agv en fonction
        return self.pep
   
    def getPostes(self):                       # return la liste [Poste] postes
        return self.postes

    def getPosteByName(self,nomPoste):         # return un poste ou NONE
        for p in self.postes:
            if p.getNom()==nomPoste:
                return p
        return NONE

    def getPosteByPosition(self,posiPoste):    # return un poste ou NONE
        for p in self.postes:
            if p.getPosition()==posiPoste:
                return p
        return NONE

    def getNbPostes(self):                     # return le int nbPostes (nb de poste sur la ligne supérieure)
        return self.nbPostes

    def getTagsPostes(self):                   # return un eliste [[int,int]]
        return self.TagsPostes

    def postePosi(self,pos):                   # return un poste
        for p in self.postes:
            if p.getPosition()==pos:
                print("\tInfoLigne >>>","poste trouvé:",p.getNom(),"en position",p.getPosition())
                return p
        print("\tInfoLigne >>>","pas de poste à la position",pos)
        return NONE

    def recupInfo(self):                       # DEBUG: Indique les détails des postes dans le terminal
        print("#Ligne/recupInfo")
        print("########################################")
        for p in self.postes:
            print("\n")
            print("nom:  ",p.nom)
            print("type: ",p.type)
            print("etat: ",p.etat)
        print("########################################")

    def start(self,poste):                     # Ajoute la liste [String] postes à la ligne
        print("#Ligne/start")
        mposi=False
        for p in self.postes:
            if poste.getPosition()==p.getPosition():
                mposi=True
                message=poste.getNom(),": Position n°"+str(poste.getPosition())+"deja utilisée par"+p.getNom()
                print("\tInfoLigne >>>",message)     
        if mposi==False :
            self.postes.append(poste)
            print("\tInfoLigne >>> ajout de:",poste.getNom())

    def ajout(self,poste):                     # Ajout d'un poste à la liste [String] postes
        print("#Ligne/ajout")
        mposi=False
        for p in self.postes:
            if poste.getPosition()==p.getPosition():
                mposi=True
                message=poste.getNom(),": Position n°"+str(poste.getPosition())+"deja utilisée par"+p.getNom()
                print("\tInfoLigne >>>",message) 
        if mposi==False :
            self.postes.append(poste)
            file_poste=open("LogPoste.txt","a")
            file_poste.write(str(poste.getNom())+";"+str(poste.getType())+";"+str(poste.getPosition())+";"+str(poste.getAction())+";"+str(poste.getTpsCylceAV())+";"+ str(poste.getTpsCycleAR())+";")
            file_poste.close()
            print("\tInfoLigne >>> ajout de:",poste.getNom())

    def listPosi(self):                        # return la liste [int] de position des postées trié
        posi=[]
        for p in self.postes:
            posi.append(int(p.getPosition()))
        posi.sort()
        return posi
    
    def supprimer(self,Poste):                 # supprime un poste de la liste [String] postes et du fichier LogPoste.txt
        print("#Ligne/supprimer")
        with open("LogPoste.txt","r")as f:
            lines=f.readlines()
            f.close()
        with open("LogPoste.txt","w")as f:
            for line in lines:
                if Poste.getNom() not in line:
                    f.write(line)
        f.close()
        self.lecture()

    def lecture(self):                         # Lecture du LogPoste et maj de la liste de poste de ligne
        print("#Ligne/lecture/LogPoste")
        self.postes.clear()
        file=open("LogPoste.txt","r")
        lignes=file.readlines()
        nb=1
        for ligne in lignes:
            if nb!=1:
                mot=ligne.split(";")
                newposte=Poste.Poste(mot[0],mot[1],int(mot[2]),mot[3],int(mot[4]),int(mot[5]))
                self.postes.append(newposte)
            nb+=1   
        file.close()

    def modifLogPoste(self,*save):             # Lecture de la liste poste pour modif LogPoste
        print("#Ligne/modifLogPoste")
        file=open("LogPoste.txt","w")
        file.write("n;")
        for poste in self.postes:
            file=open("LogPoste.txt","a")
            file.write("\n"+str(poste.getNom())+";"+str(poste.getType())+";"+str(poste.getPosition())+";"+str(poste.getAction())+";"+str(poste.getTpsCycleAV())+";"+ str(poste.getTpsCycleAR())+";")
        file.close()

print("INITIALISATION LIGNE\n")

#liste des var self:
# self.postes            liste de [Poste]
# self.nbPostes          int nombre de postes sur la zone supérieure de la ligne
# self.TagsPostes        liste de coordonés [[int,int]]
    
#ETAT
# getPostes: ok
# getPosteByName: ok
# getPosteByPosition: ok
# getNbPostes: ok
# getTagsPostes: ok
# postePosi: ok
# recupInfo: ok
# start: ok
# ajout: ok
# listPosi: ok
# supprimer: ok
# lecture: ok
# modifLogPoste: pas ok