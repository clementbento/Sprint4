#Ce code permet d'afficher et de naviguer sur l'interface liés au simulateur de la ligne de production Excelcar
#L'executable associé est InterfaceGlobal.exe

#La première page s'affichange au lancement du code est l'Interface de connexion
#Cette interface de conenxion permet de se connecter à l'interface à partir d'un nom d'Utilisateur
#Ajouter un nom d'Utilisateur est obligatoire pour continuer.
#En ajoutant un nom d'utilisateur et en cliquant sur le bouton Connexion une nouvelle page apparait : La page de choix

#La Page de choix permet de choisir entre trois boutons :
#Nouvelle simulation 
    #Cela lancera le simulateur de la ligne de production Excelcar et une interface de suivie en direct
#Ancienne simulation
    #Cela lancera l'interface de suivi des anciennes simulation
#Changer d'utilisateur

#L'interface Ancienne simulation permet de voir les différentes simulation stockées dans la base de données.
#La base de données utilisée est Firebase (voir le guide Firebase pour plus d'explication)
#Sur cette interface il est possible de :
    #Retourner à la page de choix
    #Voir des informations sur les anciennens simulations
    #Ouvrir un récapitulatif sur une simulation en particulier
    #Trier les anciennes simulations par rapport au nom d'utilisateur et en fonction de la date de la simulation

#L'interface Récapitulatif permet de voir plus d'information sur une simulation choisie
#Il est possible depuis cette interface 
    #de lancer la Vidéo de la simulation choisie (non fonctionnel)
    #de lancer le scénario de la simulation choisie (non fonctionnel)


#Quand une nouvelle simulation est lancée le simulateur et une interface Nouvelle simulation se lance
#Le simulateur est géré par les codes :  Main.py, Ihm.py, AGV.py, Agent.py, Ligne.py, Poste.py
#La transmission des données du simulateur vers notre interface est géré par Transmissions.py
#L'interface de Nouvelle simulation permet de voir différentes informations de la ligne de production et des portes en cours.
#Quand l'utilisateur a fini de produire sur la ligne de production il est possible de :
    #Terminer la simulation et de voir toutes les informations obtenues
    #Retourner à la page de choix
    #Lancer une nouvelle simulation (non fonctionnel)

#Les différents améliorations non réalisés :
    #rendre fonctionnel la vidéo
    #rendre fonctionnel le scénario des anciennes simulations
    #pouvoir lancer deux simulations l'une après l'autre (problème liés au serveur crée et au thread lancé)


import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import platform
import subprocess
import socket
import firebase_admin
import datetime
from datetime import timezone
from datetime import timedelta
import firebase_admin
from firebase_admin import credentials, firestore
from psutil import users
import sys
import json
import threading
import subprocess  
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import pyqtSignal
from tkinter import font
import re
import time

from tkinter import ttk

# Variables globales utilisées dans les différentes fonctions
fenetre_accueil = None
fenetre_choix = None
trier_par_label = None
fenetre_NouvelleSimulation = None
fenetre_recapitulatif = None
fenetre_ancienneSimulation = None
fenetre_choix = None
fenetre_accueil = None
simulateur_process = None
firebase_initialized = False
nom = None
user = None
session = 1
date_formattee = None
CompteurPorte = 0
CompteurPorteAR = 0
CompteurPorteAV = 0
TempsMoyen = 0
TempsTotal = 0
n = 0
x = 0
y = 0
info1 = 0
info2 = 0
info3 = 0
info4 = 0
tableau_frame = None
db = None
initialiser = True
TempsTotalRAVAR = 0
TempsTotalMC = 0
TempsTotalLV = 0
TempsTotalC = 0
chronoD = 0
chronoD2 = 0
h ="vide"
h2 = "vide"

logo_ecam = Image.open("Image/LogoEcam.jpg")
logo_excelcar = Image.open("Image/LogoExcelcar.jpg")

#Fonction qui initialise Firebase
def InitialiserFirebase():
    global db
    global initialiser
    if initialiser :
        # Initialisez Firebase avec votre fichier de configuration
        #cred = credentials.Certificate("C:/Users/USER/Desktop/ECAM_Rennes/ECAM5/PAM/Sprint_2/Private_key.json")
        cred = credentials.Certificate("Private_key.json") 
        firebase_admin.initialize_app(cred)
        # Accédez à la base de données Firestore
        db = firestore.client()
        initialiser = False
        #print("initialiser")

#Fonction qui lance le simulateur
def lancer_simulateur() :
    global simulateur_process
    #simulateur_process = subprocess.Popen(["python", "C:/Users/USER/Desktop/ECAM_Rennes/ECAM5/PAM/Sprint_2/Main.py"])
    simulateur_process = subprocess.Popen(["python", "Main.py"])


# Transition de page :
#Ces fonctions gère la fermeture, l'ouverture des différentes pages de l'interface et la remise à zero de certaines valeurs 
def Transition_PageAccueil_PageChoix(nomf): 
    global nom
    #if nomf: 
    if (nomf and nomf != "Utilisateur :") :
        fenetre_accueil.destroy()  # Ferme la fenêtre de connexion
        nom = nomf
        PageChoix()

def Transition_PageChoix_PageAccueil():
    fenetre_choix.destroy()
    PageAccueil()

def Transition_PageChoix_PageAncienneSimulation():
    global nom
    fenetre_choix.destroy()
    PageAncienneSimulation()

def Transition_AncienneSimulation_PageChoix():
    global nom
    fenetre_ancienneSimulation.destroy()
    PageChoix()

def Transition_AncienneSimulation_PageRecapitulatif(collection_name,collections) :
    fenetre_ancienneSimulation.destroy() 
    PageRecapitulatif(collection_name,collections)  

def Transition_PageRecapitulatif_AncienneSimulation():
    global nom
    fenetre_recapitulatif.destroy()
    PageAncienneSimulation()

def Transition_PageChoix_NouvelleSimulation():
    global nom
    
    fenetre_choix.destroy()
    PageNouvelleSimulation()
    ResetCompteurPorteTerminee()
    ResetCompteurPorteAVAR()
    ResetCompteurTempsMoyen()

def Transition_NouvelleSimulation_NouvelleSimulation(frame,frame2,frame3):
    
    donnees = [
        ["ID Porte", "Type", "Etat", "Vitesse"],
        ["--", "--", "--", "--"],
        ["--", "--", "--", "--"]
    ]
    create_table_2(frame,donnees)
    fermer_simulateur()
    lancer_simulateur()
    updateSession()
    nameCollection()
    ResetCompteurPorteTerminee()
    ResetCompteurPorteAVAR()
    ResetCompteurTempsMoyen()
    Reset(frame2,frame3)

def Transition_NouvelleSimulation_PageChoix():
    global nom
    global x,y,info1,info2,info3,info4
    global TempsTotalRAVAR, TempsTotalMC, TempsTotalLV, TempsTotalC
    fermer_simulateur()
    x = 0
    y = 0 
    info1 = 0 
    info2 = 0 
    info3 = 0 
    info4 = 0
    TempsTotalRAVAR = 0
    TempsTotalMC = 0
    TempsTotalLV = 0
    TempsTotalC = 0
    fenetre_NouvelleSimulation.destroy()
    PageChoix()

# Fonctions :
#Fonctions qui gère le tri des anciennes simulations 
#Ces fonctions sont appelés dans la fonction PageAncienneSimulation
def option_selected(selected_option, nombre_lignes, collection_names, num_docs, list_management, collections):
    if selected_option == "Trier par Utilisateur":
        option1_selected(nombre_lignes, collection_names, num_docs, list_management, collections)
    elif selected_option == "Trier par Plus récent":
        option2_selected(nombre_lignes, collection_names, num_docs, list_management, collections)
    elif selected_option == "Trier par Plus ancien":
        option3_selected(nombre_lignes, collection_names, num_docs, list_management, collections)

def option1_selected(nombre_lignes,collection_names,num_docs,list_management,collections):
    global fenetre_ancienneSimulation, tableau_frame
    tableau_frame.destroy()
    # Liste de noms au format "xxx-xx-Nom"
    # Fonction pour extraire le nom à partir de chaque élément
    def extraire_nom(element):
        # En utilisant le dernier segment de la chaîne (après le dernier tiret '-')
        return element.split("-")[-1].lower()  # Convertir en minuscules
    # Zip des deux listes
    noms_et_identifiants = list(zip(collection_names, list_management))
    # Trier la liste zippée par ordre alphabétique des noms
    noms_et_identifiants.sort(key=lambda x: extraire_nom(x[0]))
    # Séparer les listes triées
    liste_noms_tries, identifiants_tries = zip(*noms_et_identifiants)
    create_table(fenetre_ancienneSimulation,nombre_lignes,liste_noms_tries,num_docs,identifiants_tries,collections)

def option2_selected(nombre_lignes,collection_names,num_docs,list_management,collections):
    from datetime import datetime
    global fenetre_ancienneSimulation, tableau_frame
    tableau_frame.destroy()
    def extraire_et_convertir_date(element):
        date_str = element.split("-")[0]  # Extrait la partie de date
        date_obj = datetime.strptime(date_str, '%d%m%Y')  # Convertit en objet datetime
        return date_obj
    # Zip des trois listes
    donnees_combinees = list(zip(collection_names, list_management))
    # Trier la liste zippée par ordre chronologique des dates (du plus récent au plus ancien)
    donnees_combinees.sort(key=lambda x: extraire_et_convertir_date(x[0]), reverse=True)
    # Séparer les listes triées
    liste_noms_tries, identifiants_tries = zip(*donnees_combinees)
    create_table(fenetre_ancienneSimulation,nombre_lignes,liste_noms_tries,num_docs,identifiants_tries,collections)

def option3_selected(nombre_lignes,collection_names,num_docs,list_management,collections):
    from datetime import datetime
    global fenetre_ancienneSimulation, tableau_frame
    tableau_frame.destroy()
# Fonction pour extraire et convertir la date en objet datetime
    def extraire_et_convertir_date(element):
        date_str = element.split("-")[0]  # Extrait la partie de date
        date_obj = datetime.strptime(date_str, '%d%m%Y')  # Convertit en objet datetime
        return date_obj
    # Zip des trois listes
    donnees_combinees = list(zip(collection_names, list_management))
    # Trier la liste zippée par ordre chronologique des dates
    donnees_combinees.sort(key=lambda x: extraire_et_convertir_date(x[0]))
    # Séparer les listes triées
    liste_noms_tries, identifiants_tries = zip(*donnees_combinees)
    create_table(fenetre_ancienneSimulation,nombre_lignes,liste_noms_tries,num_docs,identifiants_tries,collections)

#Fonction qui gère le tableau des anciennes simulations, appelé dans la fonction PageAncienneSimulation
def create_table(fenetre, nombre_lignes,collection_names,num_docs,list_management,collections): 
    global nom, tableau_frame
    # Crée une frame pour le tableau
    tableau_frame = tk.Frame(fenetre)
    tableau_frame.pack()
    # Crée les libellés pour les en-têtes de colonnes avec des styles améliorés
    header_style = {"background": "lightgray", "font": ("Helvetica", 12, "bold")}
    col1_label = tk.Label(tableau_frame, text="Session", **header_style)
    col2_label = tk.Label(tableau_frame, text="Utilisateur", **header_style)
    col3_label = tk.Label(tableau_frame, text="Information", **header_style)
    # Place les en-têtes de colonnes
    col1_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    col2_label.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
    col3_label.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
    # Donne un poids aux lignes et aux colonnes pour un espacement uniforme
    tableau_frame.grid_rowconfigure(0, weight=1)
    tableau_frame.grid_columnconfigure(0, weight=1)
    tableau_frame.grid_columnconfigure(1, weight=1)
    tableau_frame.grid_columnconfigure(2, weight=1)
    # Affiche les données dans le tableau avec des styles améliorés
    cell_style = {"background": "white", "font": ("Helvetica", 12)}
    bouton_style = {"background": "blue", "font": ("Helvetica", 12), "fg": "white"}
    boutons = []
    for i in range(nombre_lignes):
        # Utilisez les valeurs de nom_collections
        parts = collection_names[i % len(collection_names)].split('-')
        
        # Première colonne (Partie 1)
        col1 = tk.Label(tableau_frame, text=f"{parts[0]} - {parts[1]}", **cell_style)
        col1.grid(row=i + 1, column=0, padx=5, pady=5, sticky="nsew")
        # Deuxième colonne (Partie 2)
        col2 = tk.Label(tableau_frame, text=parts[2], **cell_style)
        col2.grid(row=i + 1, column=1, padx=5, pady=5, sticky="nsew")
        # Troisième colonne (Partie 3)
        col3 = tk.Label(tableau_frame, text=list_management[i], font=("Helvetica",8))
        col3.grid(row=i + 1, column=2, padx=5, pady=5, sticky="nsew")
        bouton = tk.Button(tableau_frame, text=f"Ouvrir", command=lambda i=i: on_button_click(i,collection_names[i % len(collection_names)],collections), **bouton_style)
        bouton.grid(row=i + 1, column=3, padx=5, pady=5, sticky="nsew")
        boutons.append(bouton)
    return boutons
#Fonction qui gère le bouton ouvrant le récapitulatif d'une ancienne simulation choisi,appelé dans la fonction PageAncienneSimulation
def on_button_click(row_index,collection_name,collections):
    Transition_AncienneSimulation_PageRecapitulatif(collection_name,collections)  
#Fonction qui gère les différents tableaux, appelé dans la fonction PageAncienneSimulation et PageRécapitulatif
def create_table_2(frame, donnees):
    for i, ligne in enumerate(donnees):
        for j, valeur in enumerate(ligne):
            cellule = tk.Label(frame, text=valeur, borderwidth=1, relief="solid", width=15)
            cellule.grid(row=i, column=j, padx=5, pady=5)
#Fonction qui ouvre le scénario
def ouvrir_fichier_txt():
    # Spécifiez le chemin du fichier .txt que vous souhaitez ouvrir
    chemin_fichier_txt = "Scenario.txt"
    
    # Utilisez 'start' pour ouvrir le fichier .txt sur Windows
    if platform.system() == "Windows":
        subprocess.Popen(["start", chemin_fichier_txt], shell=True)
    else:
        subprocess.Popen(["open", chemin_fichier_txt], shell=True)
#Fonction qui ferme le simulateur
def fermer_simulateur():
    global simulateur_process
    global info1,info2,info3,info4
    global TempsTotalRAVAR, TempsTotalMC, TempsTotalLV, TempsTotalC
    
    doc_ref = db.collection(user).document("Management")
    List = ["Temps Total : {}".format(TempsTotal),
        "Temps Moyen : {}".format(TempsMoyen),
        "Nombre de porte : {}".format(CompteurPorte),
        "Nombre de porte AR : {}".format(CompteurPorteAR),
        "Nombre de porte AV : {}".format(CompteurPorteAV)]
    data = {'var': List}
    doc_ref.set(data)
    if (info1 == 0 ) :
        info1 = 1
    if (info2 == 0 ) :
        info2 = 1
    if (info3 == 0 ) :
        info3 = 1
    if (info4 == 0 ) :
        info4 = 1
    
    doc_ref = db.collection(user).document("Poste")
    List = ["Reconnaissance : {} : {}".format(info1,round((TempsTotalRAVAR/info1),2)),
        "Montage Coulisse : {}: {}".format(info2,round((TempsTotalMC/info2),2)),
        "Lève vitre : {}: {}".format(info3,round((TempsTotalLV/info3),2)),
        "Contrôle : {}: {}".format(info4,round((TempsTotalC/info4),2))]
    data = {'var': List}
    doc_ref.set(data)
    #print(List)
    simulateur_process.terminate()
#Fonctions qui gère le nombre de porte
def CompteurPorteTerminee():
    global CompteurPorte 
    CompteurPorte = CompteurPorte +1
def ResetCompteurPorteTerminee():
    global CompteurPorte
    CompteurPorte = 0
def CompteurPorteAVAR(type):
    global CompteurPorteAV
    global CompteurPorteAR
    if type == "AR" :
        CompteurPorteAR += 1 
    else :
        CompteurPorteAV += 1
def ResetCompteurPorteAVAR():
    global CompteurPorteAV
    global CompteurPorteAR
    CompteurPorteAR = 0
    CompteurPorteAV = 0
#Fonction qui gère le temps moyen
def CompteurTempsMoyen(temps):
    global TempsMoyen 
    global n
    global TempsTotal
    n = n+1
    TempsTotal = round(TempsTotal + temps,2)
    TempsMoyen = round((TempsTotal)/n,2)
def ResetCompteurTempsMoyen():
    global TempsMoyen
    TempsMoyen = 0
#Fonction qui gère le serveur
def serveur(utilisateur,frame,frame3,frame4,var):
    global user
    global date_formattee
    global CompteurPorte
    #client_socket = None
    #server_socket = None
    while var:
        # Créez un socket serveur TCP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Obligatoire pour la communication avec Firebase
        # Liez le socket à une adresse et un port
        server_address = ('localhost', 8080)
        #print(server_address)
        server_socket.bind(server_address)
        # Écoutez les connexions entrantes (maximum de connexions en attente : 5)
        server_socket.listen(100)
        serveurIdentifie = True
        #print("Le serveur écoute sur {}:{}".format(*server_address))
        # Chaque porte aura un nom, ces noms sont listés dans lists
        nomList = []
        lists = {}
        while True:
            # Attendez une connexion entrante
            client_socket, client_address = server_socket.accept()
            # Recevez des données du client (mises à jour du tableau)
            data = client_socket.recv(1024)
            # Désérialisez les données JSON en tableau
            tableau_recu = json.loads(data.decode())
            #print(datetime.now(timezone(timedelta(hours=2))), "Timer : ", tableau_recu[0], "s; Id :",tableau_recu[1], "; Type de la porte :", tableau_recu[2], " >> ", tableau_recu[3])
            #print(date_formattee, "Timer : ", tableau_recu[0], "s; Id :",tableau_recu[1], "; Type de la porte :", tableau_recu[2], " >> ", tableau_recu[3])
            if (tableau_recu[3] == "La porte est terminée"):
                CompteurPorteTerminee()
                CompteurPorteAVAR(tableau_recu[2])
                CompteurTempsMoyen(tableau_recu[0])
            elif (tableau_recu[3] == "Porte à l arrêt" or tableau_recu[3] == "Porte en mouvement"):
                update_poste(tableau_recu[1],tableau_recu[4],frame4)
            
            # Mettez à jour le tableau sur le serveur avec les nouvelles données reçues
            # Spécifiez le chemin du document (collection/nom du document)
            nom = ''.join(map(str, [tableau_recu[1],tableau_recu[2]]))
            var = ' '.join(map(str,[tableau_recu[0],tableau_recu[3]]))
            if nom not in nomList:
                nomList.append(nom)
                lists[nom] = [var]
            else:
                lists[nom].append(var)
            #doc_ref = db.collection(utilisateur).document(nom)
            doc_ref = db.collection(user).document(nom)
            data = {'var': lists[nom]}
            doc_ref.set(data)
            # Update
            update_tableau1(tableau_recu[0],tableau_recu[1],tableau_recu[2],tableau_recu[3],frame)
            update_management(frame3)
#Fonction qui mettent à jour les valeurs des tableaux en direct
def update_tableau1(a,b,c,d,frame):
    if (b%2)== 1 : 
        ligne = 1
    else :
        ligne = 2
        
    cellule = tk.Label(frame, text=b, borderwidth=1, relief="solid", width=15)
    cellule.grid(row=ligne, column=0, padx=5, pady=5)
    cellule = tk.Label(frame, text=c, borderwidth=1, relief="solid", width=15)
    cellule.grid(row=ligne, column=1, padx=5, pady=5)
    cellule = tk.Label(frame, text=d, borderwidth=1, relief="solid", width=15)
    cellule.grid(row=ligne, column=2, padx=5, pady=5)
    cellule = tk.Label(frame, text=a, borderwidth=1, relief="solid", width=15)
    cellule.grid(row=ligne, column=3, padx=5, pady=5)

def update_poste(id,poste,frame):
    global x
    global y
    global info1, info2, info3, info4
    global TempsTotalRAVAR, TempsTotalMC, TempsTotalLV, TempsTotalC
    global chronoD, chronoD2,h,h2
    if (id%2)== 1 : 
        if  poste == "Reconnaissance AV/AR":
            x = 1
            text = "Occupé"
            h = poste
            chronoD = time.time()
            info1 = info1 + 1 
        elif poste == "Montage Coulisse":
            x = 2
            text = "Occupé"
            h = poste
            chronoD = time.time()
            info2 = info2 + 1 
        elif poste == "Lève vitre":
            x = 3
            text = "Occupé"
            h = poste
            chronoD = time.time()
            info3 = info3 + 1 
        elif poste == "Contrôle":
            x = 4
            text = "Occupé"
            h = poste
            chronoD = time.time()
            info4 = info4 + 1 
        else :
            text = "Libre"
            chronoF = time.time()
            tps = chronoF - chronoD
            if h == "Reconnaissance AV/AR":
                TempsTotalRAVAR += tps
                cellule = tk.Label(frame, text=round((TempsTotalRAVAR/info1),2), borderwidth=1, relief="solid", width=15)
                cellule.grid(row=1, column=2, padx=5, pady=5)
            elif h == "Montage Coulisse":
                TempsTotalMC += tps
                cellule = tk.Label(frame, text=round((TempsTotalMC/info2),2), borderwidth=1, relief="solid", width=15)
                cellule.grid(row=2, column=2, padx=5, pady=5)
            elif h == "Lève vitre":
                TempsTotalLV += tps
                cellule = tk.Label(frame, text=round((TempsTotalLV/info3),2), borderwidth=1, relief="solid", width=15)
                cellule.grid(row=3, column=2, padx=5, pady=5)
            elif h == "Contrôle":
                TempsTotalC += tps
                cellule = tk.Label(frame, text=round((TempsTotalC/info4),2), borderwidth=1, relief="solid", width=15)
                cellule.grid(row=4, column=2, padx=5, pady=5)
            

            
        cellule = tk.Label(frame, text=text, borderwidth=1, relief="solid", width=15)
        cellule.grid(row=x, column=1, padx=5, pady=5)
    else :
        if  poste == "Reconnaissance AV/AR":
            y = 1
            text = "Occupé"
            h2 = poste
            chronoD2 = time.time()
            info1 = info1 + 1 
        elif poste == "Montage Coulisse":
            y = 2
            text = "Occupé"
            h2 = poste
            chronoD2 = time.time()
            info2 = info2 + 1 
        elif poste == "Lève vitre":
            y = 3
            text = "Occupé"
            h2 = poste
            chronoD2 = time.time()
            info3 = info3 + 1 
        elif poste == "Contrôle":
            y = 4
            text = "Occupé"
            h2 = poste
            chronoD2 = time.time()
            info4 = info4 + 1 
        else :
            text = "Libre"
            chronoF2 = time.time()
            tps2 = chronoF2 - chronoD2
            if h2 == "Reconnaissance AV/AR":
                TempsTotalRAVAR += tps2
                cellule = tk.Label(frame, text=round((TempsTotalRAVAR/info1),2), borderwidth=1, relief="solid", width=15)
                cellule.grid(row=1, column=2, padx=5, pady=5)
            elif h2 == "Montage Coulisse":
                TempsTotalMC += tps2
                cellule = tk.Label(frame, text=round((TempsTotalMC/info2),2), borderwidth=1, relief="solid", width=15)
                cellule.grid(row=2, column=2, padx=5, pady=5)
            elif h2 == "Lève vitre":
                TempsTotalLV += tps2
                cellule = tk.Label(frame, text=round((TempsTotalLV/info3),2), borderwidth=1, relief="solid", width=15)
                cellule.grid(row=3, column=2, padx=5, pady=5)
            elif h2 == "Contrôle":
                TempsTotalC += tps2
                cellule = tk.Label(frame, text=round((TempsTotalC/info4),2), borderwidth=1, relief="solid", width=15)
                cellule.grid(row=4, column=2, padx=5, pady=5)

        cellule = tk.Label(frame, text=text, borderwidth=1, relief="solid", width=15)
        cellule.grid(row=y, column=1, padx=5, pady=5)
    cellule = tk.Label(frame, text=info1, borderwidth=1, relief="solid", width=15)
    cellule.grid(row=1, column=3, padx=5, pady=5)
    cellule = tk.Label(frame, text=info2, borderwidth=1, relief="solid", width=15)
    cellule.grid(row=2, column=3, padx=5, pady=5)
    cellule = tk.Label(frame, text=info3, borderwidth=1, relief="solid", width=15)
    cellule.grid(row=3, column=3, padx=5, pady=5)
    cellule = tk.Label(frame, text=info4, borderwidth=1, relief="solid", width=15)
    cellule.grid(row=4, column=3, padx=5, pady=5)

def update_management(frame):
    cellule = tk.Label(frame, text=CompteurPorte, borderwidth=1, relief="solid", width=15)
    cellule.grid(row=0, column=1, padx=5, pady=5)
    cellule = tk.Label(frame, text=CompteurPorteAV, borderwidth=1, relief="solid", width=15)
    cellule.grid(row=2, column=1, padx=5, pady=5)
    cellule = tk.Label(frame, text=CompteurPorteAR, borderwidth=1, relief="solid", width=15)
    cellule.grid(row=3, column=1, padx=5, pady=5)
    cellule = tk.Label(frame, text=TempsMoyen, borderwidth=1, relief="solid", width=15)
    cellule.grid(row=6, column=1, padx=5, pady=5)
#Fonctionq qui gère le nom de la collection 
def nameCollection():
    global user
    global nom
    global session
    global date_formattee
    # Obtenez la date actuelle
    date_actuelle = datetime.date.today()
    # Formatez la date au format "dd/mm/aaaa"
    date_formattee = date_actuelle.strftime("%d%m%Y")
    user = f"{date_formattee}-S{session}-{nom}"

def updateSession():
    global session 
    session = session + 1
#Fonction qui reset le tableau
def Reset(frame,frame2):
    global x,y,info1,info2,info3,info4
    x = 0
    y = 0 
    info1 = 0 
    info2 = 0 
    info3 = 0 
    info4 = 0
    donnees_tableau2 = [
        ["Poste", "Etat", "Temps moyen", "Nb d action"],
        ["Reconnaissance", "Libre", "--", "--"],
        ["Montage Coulisse", "Libre", "--", "--"],
        ["Lève vitre", "Libre", "--", "--"],
        ["Contrôle", "Libre", "--", "--"]
    ]
    donnees_tableau3 = [
        ["Qtt total", "Valeur"],
        ["TRS", "--"],
        ["Qtt AV", "--"],
        ["Qtt AR", "--"],
        ["Rebut AV", "--"],
        ["Rebut AR", "--"],
        ["Temps moyen", "--"]
    ]
    # Crée le deuxième tableau dans le cadre du deuxième cadre
    create_table_2(frame, donnees_tableau2)
    # Crée le troisième tableau dans le cadre du troisième cadre
    create_table_2(frame2, donnees_tableau3)

    
# Pages

def PageAccueil():#Fonction qui gère la page d'Accueil
    global fenetre_accueil
    global nom
    global logo_ecam
    global logo_excelcar
    
    InitialiserFirebase()
    fenetre_accueil = tk.Tk()

    width= 800
    height = 600
    fenetre_accueil.geometry(str(width)+"x"+str(height))
    fenetre_accueil.config(bg= "#D9D9D9")

    fenetre_accueil.title("Interface de Connexion")
 
    logo_ecam_tk = ImageTk.PhotoImage(logo_ecam)
    logo_excelcar_tk = ImageTk.PhotoImage(logo_excelcar)
    label_gauche = tk.Label(fenetre_accueil, image=logo_ecam_tk,borderwidth=0)
    label_droite = tk.Label(fenetre_accueil, image=logo_excelcar_tk,borderwidth=0)
    label_gauche.place(x=0, y=height - logo_ecam_tk.height())
    label_droite.place(x=width - logo_excelcar_tk.width() - 5, y=height - logo_excelcar_tk.height() - 50)
    
    #titre
    nom_label = tk.Label(fenetre_accueil, text="Interface de connexion ", font= ("Verdana" , 30), bg= "#D9D9D9")
    taille_nom_interface = len("Interface de connexion") * 10   
    nom_label.place(x= 1*( width/2) - (1*taille_nom_interface) , y= 1*(height / 5) )
    
    #fenêtre insertion utilisateur
    nom_entree = tk.Entry(fenetre_accueil, font=("Verdana", 20), fg= "#000000", justify="center") # fg = couleur texte
    nom_entree.place(x=(width/4), y=((height/2)-75), width=width/2, height=50) 
    nom_entree.insert(0, "Utilisateur :")  # Ajoutez le texte d'arrière-plan initial  
    nom_entree.bind("<FocusIn>", lambda event: event.widget.delete(0, tk.END) if event.widget.get() == "Utilisateur :" else None)
    
    #bouton connection
    bouton_connecter = tk.Button(fenetre_accueil, text="Connexion", background= "#A6A6A6",command=lambda: Transition_PageAccueil_PageChoix(nom_entree.get()),padx=width/8, pady= 15,relief= "sunken")
    bouton_connecter.place(x=(width/2) - (width/6), y=((2*height/3)-75))
   
    # run
    fenetre_accueil.mainloop()  
    
class ToolTip: #Class qui gère l'affichage des bulles de texte pour la page de Choix
    def __init__(self, master, delay=50):
        self.master = master
        self.delay = delay
        self._schedule_id = None
        self.tooltip_toplevel = None

    def show_tooltip(self, widget, text):  
        #Cette méthode crée une nouvelle fenêtre (info-bulle) et l'attache à la position actuelle 
        # de la souris sur le widget. Le texte spécifié est affiché dans cette fenêtre.
        if self.tooltip_toplevel:
            self.tooltip_toplevel.destroy()
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25

        self.tooltip_toplevel = tk.Toplevel(self.master)
        self.tooltip_toplevel.wm_overrideredirect(True)
        self.tooltip_toplevel.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_toplevel, text=text, justify="left", background="#FFFFDD", relief="solid", borderwidth=1)
        label.pack(ipadx=1)

               
    def hide_tooltip(self): # Cette méthode masque l'info-bulle en détruisant sa fenêtre.
        if self.tooltip_toplevel:
            self.tooltip_toplevel.destroy()

    def set_tooltip(self, widget, text):
        #Cette méthode associe les événements <Enter> et <Leave> 
        # au widget aux méthodes schedule_tooltip et hide_tooltip respectivement.
        widget.bind("<Enter>", lambda event: self.schedule_tooltip(widget, text))
        widget.bind("<Leave>", lambda event: self.hide_tooltip())

    def schedule_tooltip(self, widget, text):
        # Cette méthode planifie l'affichage de l'info-bulle après un 
        # délai spécifié (500 millisecondes dans cet exemple) en utilisant after de tkinter.
        # Cela permet d'éviter un affichage immédiat de l'info-bulle lorsqu'un utilisateur 
        # survole rapidement plusieurs widgets.
        if self._schedule_id:
            self.master.after_cancel(self._schedule_id)
        self._schedule_id = self.master.after(self.delay, lambda: self.show_tooltip(widget, text))
        
def PageChoix():#Fonction qui gère la page de Choix
    
    global fenetre_choix
    global nom
    global bouton_changer_utilisateur
    
    nameCollection()
    
    fenetre_choix = tk.Tk()
    fenetre_choix.title("Page de choix")

    width=800
    height = 600    
    fenetre_choix.geometry(str(width)+"x"+str(height))
    fenetre_choix.configure(bg="#D9D9D9")

    logo_ecam = Image.open("Image/LogoEcam.jpg")
    logo_excelcar = Image.open("Image/LogoExcelcar.jpg")
    logo_ecam_tk = ImageTk.PhotoImage(logo_ecam)
    logo_excelcar_tk = ImageTk.PhotoImage(logo_excelcar)
    label_gauche = tk.Label(fenetre_choix, image=logo_ecam_tk,borderwidth=0)
    label_droite = tk.Label(fenetre_choix, image=logo_excelcar_tk,borderwidth=0)

    
    label_gauche.place(x=0, y=height - logo_ecam_tk.height())
    label_droite.place(x=width - logo_excelcar_tk.width()-5, y=height - logo_excelcar_tk.height() - 50)  

    bienvenue_label = tk.Label(fenetre_choix, text=f"Bienvenue, {nom} !", font= (" Verdana", 20), background="#D9D9D9")
    bienvenue_label.place(relx=0.5, rely=1/9, anchor="center")  #calcule compliqué afin de garder titre centrée. # Coefficient choisi arbitrairement
      
    
    bouton_nouvelle_sim = tk.Button(fenetre_choix, text="Nouvelle simulation",relief= "sunken",command=lambda:Transition_PageChoix_NouvelleSimulation())
    bouton_nouvelle_sim.place( x =(( 1 * width/4 )- len("Nouvelle simulation")*2)-50, y=  1 * height/3 , width= len("Changer d'utilisateur")*8, height= 50 )
    bouton_ancienne_sim = tk.Button(fenetre_choix, text="Ancienne simulation", relief= "sunken" ,command=lambda: Transition_PageChoix_PageAncienneSimulation())
    bouton_ancienne_sim.place( x =(( 2 * width/4 )-len("Ancienne simulation")*2)-50, y=  1 * height/3 , width= len("Changer d'utilisateur")*8, height= 50 )
    bouton_changer_utilisateur = tk.Button(fenetre_choix, text="Changer d'utilisateur", relief= "sunken",command=Transition_PageChoix_PageAccueil)
    bouton_changer_utilisateur.place( x = ((3 * width/4)-len("Changer d'utilisateur")*2)-50 , y=  1 * height/3  , width=len("Changer d'utilisateur")*8 , height= 50)
    
  
    tooltip = ToolTip(fenetre_choix)   # Créer un widget Tooltip qui s'affiche quand on passe la souris dessus
    tooltip.set_tooltip(bouton_changer_utilisateur, "Changer d'utilisateur") # Associer le Tooltip au bouton
    tooltip.set_tooltip( bouton_nouvelle_sim, "Lancer l'interface de simulation") # Associer le Tooltip au bouton
    tooltip.set_tooltip(  bouton_ancienne_sim , "Obtenir les anciennes simulations " ) # Associer le Tooltip au bouton
    
    
    
    fenetre_choix.mainloop()

def PageAncienneSimulation():#Fonction qui gère la page d'Ancienne Simulation
    global fenetre_ancienneSimulation
    global trier_par_label  # Utiliser la variable globale
    global nom
    global trier_par_combobox
    # Récupérez les noms de toutes les collections
    collections = db.collections()
    
    # Créez une liste pour stocker les noms des collections
    collection_names = []
    num_docs=[]
    list_management = []
    for collection in collections:
        #print("----------------------------------------")
        #print(f"Nom de la collection : {collection.id}")
        collection_names.append(collection.id)
        # Récupérez tous les documents de cette collection
        docs = collection.stream()
        # Imprimez la liste des documents
        #print("Liste des documents dans cette collection:")
        for doc in docs:
            #print(doc.id)
            if doc.id == "Management":
                doc_data = doc.to_dict()
                #print("Données du document 'Management':")
                result = ["{} : {}".format(item.split(':')[0].strip(), float(re.search(r'\d+\.\d+|\d+', item).group()) if re.search(r'\d+\.\d+|\d+', item) else 0) for item in doc_data['var']]
                list_management.append(result)
        # Rechargez la liste des documents pour compter
        docs = collection.stream()
        num_docs.append(len(list(docs)))
        
    nombre_lignes = len(collection_names)
    fenetre_ancienneSimulation = tk.Tk()
    fenetre_ancienneSimulation.title("Ancienne simulation")
    fenetre_ancienneSimulation.geometry("1000x600")
    fenetre_ancienneSimulation.config(bg= "#D9D9D9")
    logo_ecam = Image.open("Image/LogoEcam.jpg")
    logo_excelcar = Image.open("Image/LogoExcelcar.jpg")
    logo_ecam_tk = ImageTk.PhotoImage(logo_ecam)
    logo_excelcar_tk = ImageTk.PhotoImage(logo_excelcar)
    label_gauche = tk.Label(fenetre_ancienneSimulation, image=logo_ecam_tk,borderwidth=0)
    label_droite = tk.Label(fenetre_ancienneSimulation, image=logo_excelcar_tk,borderwidth=0)
    label_gauche.place(x=0, y=600 - logo_ecam_tk.height())
    label_droite.place(x=950 - logo_excelcar_tk.width()-5, y=600 - logo_excelcar_tk.height()- 50)

    nom_label = tk.Label(fenetre_ancienneSimulation, text="Ancienne simulation", font=("Helvetica", 16, "bold"))
    nom_label.pack()
    bouton_retour = tk.Button(fenetre_ancienneSimulation, text="Retour", command=lambda : Transition_AncienneSimulation_PageChoix())
    bouton_retour.pack()
    
    # Créez une liste déroulante pour trier les données
    trier_par_combobox = ttk.Combobox(fenetre_ancienneSimulation, values=["","Trier par Utilisateur", "Trier par Plus récent", "Trier par Plus ancien"])
    trier_par_combobox.set("Trier par : Sélectionnez une option")
    trier_par_combobox.pack(pady=10)
    trier_par_combobox.bind("<<ComboboxSelected>>", lambda event: option_selected(trier_par_combobox.get(), nombre_lignes, collection_names, num_docs, list_management, collections))

    # Appelle la fonction pour créer le tableau de 3 colonnes
    create_table(fenetre_ancienneSimulation,nombre_lignes,collection_names,num_docs,list_management,collections)
    fenetre_ancienneSimulation.mainloop()
    
def PageRecapitulatif(collection_name,collections):#Fonction qui gère la page Recapitulatif
    global fenetre_recapitulatif
    global nom
    fenetre_recapitulatif = tk.Tk()
    fenetre_recapitulatif.title("Récapitulatif : Utilisateur - Session")
    fenetre_recapitulatif.geometry("1000x600")
    fenetre_recapitulatif.configure(bg="#D9D9D9")
    #print("_______________________________")
    #print(collection_name)
    # Crée un cadre en haut à droite pour les boutons
    bouton_frame = tk.Frame(fenetre_recapitulatif)
    bouton_frame.pack(side="top", anchor="ne", padx=10, pady=10)
    # Boutons
    bouton1 = tk.Button(bouton_frame, text="Retour", command=lambda : Transition_PageRecapitulatif_AncienneSimulation())
    bouton1.pack(side="right", padx=5)
    bouton2 = tk.Button(bouton_frame, text="Scénario", command=ouvrir_fichier_txt)
    bouton2.pack(side="right", padx=5)
    bouton3 = tk.Button(bouton_frame, text="Vidéo")
    bouton3.pack(side="right", padx=5)
    nom_label = tk.Label(fenetre_recapitulatif, text="Récapitulatif : Utilisateur - Session")
    nom_label.pack()
    collection = db.collection(collection_name)
    donnees_tableau = [
    ["Temps total", "--"],
    ["TRS", "--"],
    ["Qtt AV", "--"],
    ["Qtt AR", "--"],
    ["Rebut AV", "--"],
    ["Rebut AR", "--"],
    ["Temps moyen", "--"]]
    donnees_tableau_2 = [
        ["Poste", "Nb actions", "Temps Moyen"],
        ["Reconnaissance", "--", "--"],
        ["Montage coulisse", "--", "--"],
        ["Lève vitre", "--", "--"],
        ["Contrôle", "--", "--"]]
    
    donnees_tableau_3 = [
        ["Porte", "Type", "Temps Total"]
    ]
    # Parcourez les collections
    
    #print("----------------------------------------")
    #print(f"Nom de la collection : {collection.id}")
    # Récupérez tous les documents de cette collection
    docs = collection.stream()
    # Parcourez les documents dans cette collection
    for doc in docs:
        doc_data = doc.to_dict()
        #print(f"ID du document : {doc.id}")
        #print(f"Données du document : {doc_data}")
        if doc.id == "Management":
            # Si le document a l'ID "Management", mettez à jour donnees_tableau3
            # Mettez à jour les valeurs appropriées dans donnees_tableau3
            management_data = doc_data.get("var", [])
            for item in management_data:
                key, value = item.split(" : ")
                if key == "Temps Total":
                    donnees_tableau[0][1] = value
                elif key == "Temps Moyen":
                    donnees_tableau[6][1] = value
                elif key == "Nombre de porte AV":
                    donnees_tableau[2][1] = value
                elif key == "Nombre de porte AR":
                    donnees_tableau[3][1] = value
        elif doc.id == "Poste":
            porte_data = doc_data.get("var", [])
            for item in porte_data:
                key, value, value2 = item.split(":")
                if key == "Reconnaissance ":
                    donnees_tableau_2[1][1] = value
                    donnees_tableau_2[1][2] = value2
                elif key == "Montage Coulisse ":
                    donnees_tableau_2[2][1] = value
                    donnees_tableau_2[2][2] = value2
                elif key == "Lève vitre ":
                    donnees_tableau_2[3][1] = value
                    donnees_tableau_2[3][2] = value2
                elif key == "Contrôle ":
                    donnees_tableau_2[4][1] = value
                    donnees_tableau_2[4][2] = value2
        else :
            chiffre = doc.id[0]
            lettres = doc.id[1:]
            derniere_valeur = float(doc_data["var"][-1].split(" ")[0])
            # Ajouter une nouvelle ligne avec le chiffre et les lettres à donnees_tableau_3
            donnees_tableau_3.append([chiffre, lettres, derniere_valeur])

    # Crée un cadre principal pour les tableaux
    tableau_principal_frame = tk.Frame(fenetre_recapitulatif)
    tableau_principal_frame.pack(padx=10, pady=10)


    
    tableau_principal_frame2 = tk.Frame(fenetre_recapitulatif)
    tableau_principal_frame2.pack(padx=10, pady=10)
    

    tableau_principal_frame3 = tk.Frame(fenetre_recapitulatif)
    tableau_principal_frame3.pack(padx=10, pady=10)
    
    

    create_table_2(tableau_principal_frame, donnees_tableau)
    create_table_2(tableau_principal_frame2, donnees_tableau_2)
    create_table_2(tableau_principal_frame3, donnees_tableau_3)
    

    fenetre_recapitulatif.mainloop()

def PageNouvelleSimulation():#Fonction qui gère la page Nouvelle simulation
    global nom
    global fenetre_NouvelleSimulation
    fenetre_NouvelleSimulation = tk.Tk()
    fenetre_NouvelleSimulation.title("Nouvelle simulation")
    fenetre_NouvelleSimulation.geometry("1000x700")
    fenetre_NouvelleSimulation.config(bg= "#D9D9D9")
    # Crée un cadre en haut à droite pour les boutons
    bouton_frame = tk.Frame(fenetre_NouvelleSimulation)
    bouton_frame.pack(side="top", anchor="ne", padx=10, pady=10)
    
    nom_label = tk.Label(fenetre_NouvelleSimulation, text="Nouvelle simulation")
    nom_label.pack()
    # Données pour les tableaux (exemple)
    donnees_tableau1 = [
        ["ID Porte", "Type", "Etat", "Temps"],
        ["--", "--", "--", "--"],
        ["--", "--", "--", "--"]
    ]
    donnees_tableau2 = [
        ["Poste", "Etat", "Temps moyen", "Nb d action"],
        ["Reconnaissance", "Libre", "--", "--"],
        ["Montage Coulisse", "Libre", "--", "--"],
        ["Lève vitre", "Libre", "--", "--"],
        ["Contrôle", "Libre", "--", "--"]
    ]
    donnees_tableau3 = [
        ["Qtt total", "--"],
        ["TRS", "--"],
        ["Qtt AV", "--"],
        ["Qtt AR", "--"],
        ["Rebut AV", "--"],
        ["Rebut AR", "--"],
        ["Temps moyen", "--"]
    ]
    


    # Crée un cadre principal pour les tableaux
    tableau_principal_frame = tk.Frame(fenetre_NouvelleSimulation)
    tableau_principal_frame.pack(padx=10, pady=10)
    # Crée un espace vide à gauche du premier tableau pour le décalage
    espace_vide = tk.Label(tableau_principal_frame, text="", width=10)
    espace_vide.grid(row=0, column=0, padx=10, pady=10)
    # Crée le premier tableau dans le cadre principal
    create_table_2(tableau_principal_frame, donnees_tableau1)
    # Crée un cadre pour le deuxième tableau en bas
    tableau2_frame = tk.Frame(fenetre_NouvelleSimulation)
    tableau2_frame.pack(padx=10, pady=10)
    # Crée le deuxième tableau dans le cadre du deuxième cadre
    create_table_2(tableau2_frame, donnees_tableau2)
    # Crée un cadre pour le troisième tableau en bas
    tableau3_frame = tk.Frame(fenetre_NouvelleSimulation)
    tableau3_frame.pack(padx=10, pady=10)
    # Crée le troisième tableau dans le cadre du troisième cadre
    create_table_2(tableau3_frame, donnees_tableau3)
    logo_ecam = Image.open("Image/LogoEcam.jpg")
    logo_excelcar = Image.open("Image/LogoExcelcar.jpg")
    logo_ecam_tk = ImageTk.PhotoImage(logo_ecam)
    logo_excelcar_tk = ImageTk.PhotoImage(logo_excelcar)
    label_gauche = tk.Label(fenetre_NouvelleSimulation, image=logo_ecam_tk,borderwidth=0)
    label_droite = tk.Label(fenetre_NouvelleSimulation, image=logo_excelcar_tk,borderwidth=0)
    label_gauche.place(x=0, y=700 - logo_ecam_tk.height())
    label_droite.place(x=950 - logo_excelcar_tk.width(), y=700 - logo_excelcar_tk.height())
    bouton_nouvelle_sim = tk.Button(fenetre_NouvelleSimulation, text="Nouvelle simulation", command = lambda : Transition_NouvelleSimulation_NouvelleSimulation(tableau_principal_frame,tableau2_frame,tableau3_frame))
    bouton_nouvelle_sim.pack()
    bouton_fin_sim = tk.Button(fenetre_NouvelleSimulation, text="Fin simulation",command = fermer_simulateur)
    bouton_fin_sim.pack()
    bouton_fin_sim = tk.Button(fenetre_NouvelleSimulation, text="Retour", command= lambda :Transition_NouvelleSimulation_PageChoix())
    bouton_fin_sim.pack()
    # Lancez la fonction `launch_server` dans un thread
    server_thread = threading.Thread(target=serveur, args=(nom,tableau_principal_frame,tableau3_frame,tableau2_frame,True))
    server_thread.start()
    lancer_simulateur()
    fenetre_NouvelleSimulation.mainloop()



PageAccueil()