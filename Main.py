# -*- coding: utf-8 -*-
from tkinter.messagebox import *
from tkinter import *
import os.path
import Ligne
import Poste
import Ihm

 

# création de la ligne Excelcar 
Excelcar=Ligne.Ligne()

# liste des postes de base
postesDeBase=["\nMontage Coulisse;Manuel;2;Mettre en place la Coulisse;120;80;\n",
"Reconnaissance AV/AR;Automatique;1;Marquer;40;40;\n",
"Lève vitre;Manuel;3;Monter le lève vitre;35;12;\n",
"Contrôle;Manuel;4;Contrôler la qualitée du montage;20;20;\n"]


# Création ou réinitialisation du LogPoste
if os.path.isfile("LogPoste.txt"):
    
    print("#Main/initLogPoste")
    file=open("LogPoste.txt","r")
    lines=file.readlines()
    if os. path. getsize("LogPoste.txt")==0:   # check si LogPoste n'est pas vide
        print("#Main/écritureLogPoste")
        file.close()
        file=open("LogPoste.txt","w")   # Efface le contenu du LogPoste.txt
        file.write("n;")
        file.writelines(postesDeBase)
    elif "n" in lines[0]:
        print("#Main/réécritureLogPoste")
        file.close()
        file=open("LogPoste.txt","w")   # Efface le contenu du LogPoste.txt
        file.write("n;")
        file.writelines(postesDeBase)
    else:
        print("#Main/noChangeLogPoste")
        file.close()
        file=open("LogPoste.txt","w")
        file.write("n;\n")
        file.writelines(lines[1:])
    file.close()
else: 
    print("#Main/créationLogPoste")
    file=open("LogPoste.txt","w+")  # Créer le LogPoste.txt
    file.write("n;")
    file.writelines(postesDeBase)
    file.close()

init=open("InitialLogPoste.txt","w+")# Créé/Recréé InitialLogPoste.txt
init.write("n;")
init.writelines(postesDeBase)
init.close()

file=open("LogPoste.txt","r")       # Créé/Recréé PrevLogPoste.txt
prev=open("prevLogPoste.txt","w+")
lines=file.readlines()
file.close()
prev.writelines(lines)
prev.close()

# création des postes dans la ligne Excelcar
print("#Main/lectureLogPoste")
file=open("LogPoste.txt","r")
lignes=file.readlines()
nb=1
for ligne in lignes:
    if nb!=1:
        mot=ligne.split(";")
        newposte=Poste.Poste(mot[0],mot[1],int(mot[2]),mot[3],int(mot[4]),int(mot[5]))
        Excelcar.start(newposte)
    nb+=1
file.close()


# lancement de l'IHM
ihm=Ihm.IHM(Excelcar)




ihm.mainloop()