# -*- coding: utf-8 -*-
from tkinter.messagebox import *
from functools import partial
from tkinter import *
import Poste
import AGV
import time
from math import pi
import numpy as np
import threading
import os
import Transmission



#fenetre principale
class IHM(PanedWindow):
    def __init__(self,ligne):

        print("#IHM/init")
        tk=Tk()
        PanedWindow.__init__(self)                                          # Création de la double fenetre
        
        # Initialisation des variables self
        self.master.title("Ligne d'assemblage")
        self.configure(orient=VERTICAL,sashrelief='raised',sashpad=1)
        self.w,self.h=tk.winfo_screenwidth(),tk.winfo_screenheight()        # A n'utiliser que si écran simple
        #self.w,self.h=1680,1050                                            # Si double écran (ou plus) indiquer les dimensions voulues "largeur,hauteur"
        self.ligne=ligne
        self.btnPoste=[]
        self.Tag=[]

        # Dimensions de la fenetre
        tk.geometry("%dx%d"%(self.w,self.h))                                # Taille de la fenetre
        tk.attributes("-fullscreen",True)                                   # On force le fullscreen
        tk.iconphoto(False,PhotoImage(file='Excelcar.png'))  # Petite icone Excelcar sympatique (en PNG en plus!) si ca pose pb, un # devant la ligne et plus de pb
        sas=self.h-150                                                      # Hauteur du séparateur entre les deux fenetre d'affichage

        # Création de la fenetre principale
        self.FenetreValou=Canvas(tk,width=self.w,height=self.h,bg='white')

        # Fonctions de la barre de menu
         # bouton quitter
        def quitter():                                                      # Quitter définitivement la fenetre
            print("#IHM/init/Quitter")
            SaveQuit=askyesnocancel("Quitter","Voulez sauvegarder avent de quitter?")
            if SaveQuit!=None:                                              # Si on veut pas annuler
                self.save(SaveQuit)                                         # On sauvegarde si yes, ou pas si no
                tk.quit()                                                   # On ferme l'instance
       
         
         # bouton Vider
        
        def reinit():
            print("#IHM/init/reinit")
            if askokcancel("Réinitialiser","Voulez vraiment vider la ligne?"):
                self.clear()                                                # On vide la ligne des postes
                self.ligne.postes.clear()                                   # On efface la liste de poste
                file=open("LogPoste.txt","w")                               # On efface le LogPoste
                file.write("n;")                                            # n = pas de sauvegarde (par défaut)
                file.close()

         # bouton reset
        def reset():
            print("#IHM/init/reset")
            if askyesno("RESET","Voulez vous retourner à l'état d'origine?"):
                file=open("LogPoste.txt","w")                               # On efface le LogPoste
                old=open("InitialLogPoste.txt","r")                         # On lit la ligne par défaut (définie dans main) dans Initial LogPoste, ca évite de rappeler Main, ce qui crérait de pb de répétition
                lines=old.readlines()                                       # On récupère tt de InitialLogPoste
                old.close()
                file.writelines(lines)                                      # On écrit tt ce qu'on a récupéré  
                file.close()
                self.charger()                                              # On recharge la ligne

         # bouton edit
        self.edition=False                                                  # On est pas en mode édition
        print("\tModeEdition = False")
        def edit(*event):                                                   # Le * créer un variable optionnelle, cette variable sera par défaut un tuple / event est représente la souris, avec on peut récupérer la position, un click, un mvt, etc...
            temps=0
            def fin():                                                      # Bouton fin ou reclick sur edition: sortie du mode d'edition
                print("#IHM/init/edit/fin")
                yes=askyesnocancel("Edit","Voulez vous enregistrer les modifications?")
                if yes:                                                     # quitter + enregistrer
                    self.edition=False                                      # on quitte le mode édition
                    print("\tModeEdition = False")
                    self.FenetreValou.delete("oui")                         # oui est l'ensemble des représentations des postes ainsi que des textes spécifiques au mode edition | On supprime tout les attributs sous le nom de "oui"
                    self.FenetreValou.configure(bg='white')                 # on repasse la fenetre en blanc
                    self.ligne.modifLogPoste()                              # on enregistre le nouveau LogPoste
                    self.charger()                                          # on recharge la ligne
                    self.sash_place(index=0,x=0,y=sas)                      # on replace la séparation avec la deuxieme fenetre à la hauteur sas
                    for p in self.pep :
                        p.modeEdition(False)
                        p.timeur+=time.time()-temps
                elif yes==False:                                            # quitter + non enregistrer
                    self.edition=False                                      # Onquitte le mode édition
                    self.annuleModifs()                                     # annuler modifs permet de remettre le LogPoste à l'état où il était avant d'entrer en mode édition
                    print("\tModeEdition = False")
                    self.FenetreValou.delete("oui")                         # on supprime tout ce qui as un rapport au mode édition
                    self.FenetreValou.configure(bg='white')                 # on repace en blanc
                    self.charger()                                          # on recharge la ligne
                    self.sash_place(index=0,x=0,y=sas)                      # le séparateur de fenetre reviens à la hauteur de sas
                    for p in self.pep:
                        p.modeEdition(False)
                        p.timeur+=time.time()-temps
                else:print("\t toujours en édition")                        # pas quitter
            def BtnAnnuler():                                               # Bouton annuler: sortie du mode d'édition + annulation des modifs
                print("#IHM/init/edit/annuler")
                self.edition=False                                          # on quitte le mode édition
                print("\tModeEdition = False")
                self.FenetreValou.delete("oui")                             # oui est l'ensemble des représentations de postes en mode edition
                self.FenetreValou.configure(bg='white')                     # on repasse la fenetre en blanc
                self.charger()                                              # on recharge la ligne
                for p in self.pep:
                    p.modeEdition(False)
                    p.timeur+=time.time()-temps
            if self.edition==False:                                         # Si on est pas déja en édition
                print("#IHM/init/edit")
                if askokcancel("Mode Edition","Vous entrez en mode edtition"):
                    self.majPLP()                                           # On copie le LogPoste dans le prevLogPoste dans le cas d'une annulation
                    temps=time.time()
                    self.edition=True                                       # On passe en mode édition
                    print("\tModeEdition = True")
                    self.FenetreValou.configure(bg='#F2E7BF')               # On change la couleur d'arrière plan en #F2E7BF, soit orange clair
                    yolo=self.FenetreValou.create_text(100,100,text="Mode Édition",font=('Times',14,'bold'),fill='black')  # texte "Mode Édition"
                    self.FenetreValou.addtag_withtag("oui",yolo)            # Le texte "Mode Édition" est associé au tag "oui"
                    self.sash_place(index=0,x=0,y=int(round(self.h)))       # Place le séparateur des fenetres au plus bas, soit à la hauteur self.h, qui est la hauteur de la fenetre
                    self.charger()                                          # On recharge la fenetre
                    Button(self.FenetreValou,text="Fin",command=fin).place(x=self.w-150,y=self.h-100) # Boutton Fin du mode édition
                    Button(self.FenetreValou,text="Annuler",command=BtnAnnuler).place(x=self.w-100,y=self.h-100) # bouton annuler du mode édition
                    for p in self.pep:
                        p.modeEdition(True) 
            else: fin()                                                     # si on entre en mode édition alors qu'on y est déja, on retourne dans fin()

        # raccourci pour entrer en mode étdition: click molette
        self.FenetreValou.bind('<Button-2>',edit)
        

         # bouton param
        def param():                                                        # Param, la fonction pour passer du pleine écran au fenétré
            fenetreParam=Tk()                                               # Création d'une fenetre sup
            fenetreParam.title("Paramètres fenêtre")
            Label(fenetreParam,text="Paramètre d'affichage :",font="bold").pack() # les labels sont des zone de texte
            button_frame=Frame(fenetreParam)                                # Les frames sont des zones où comme les Canvas on peu y ajouter des items
            button_frame.pack()
            entree=Frame(fenetreParam)
            Label(entree,text="Longueur: ").grid(row=0,column=0)
            w=StringVar(entree)                                             # Pour tout ce qui est radiobutton, Entry, spinBox, etc... il faut déclarer la variable avant
            w=Entry(entree,width=5)                                         # Les entry sont des items permettant d'entrer du texte
            w.grid(row=0,column=1)
            Label(entree,text="Largeur: ").grid(row=1,column=0)
            h=StringVar(entree)
            h=Entry(entree,width=5)
            h.grid(row=1,column=1)
            def boutPerso():                                                # permet de faire apparaitre les zones de saisi pour les dimension de la fenetre
                entree.pack()
            def NboutPerso():                                               # masque les zones de saisi
                entree.pack_forget()
            x=StringVar(button_frame)                                       # varible des radios boutons
            Radiobutton(button_frame,text="Plein Ecran",variable=x,value="PE",command=NboutPerso).grid(row=0) # Radio bouton plein Ecran
            Radiobutton(button_frame,text="Fenétré",variable=x,value="F",command=NboutPerso).grid(row=1)      # Radio bouton Fenétré
            #Radiobutton(button_frame,text="Personnalisé",variable=x,value="FP",command=boutPerso).grid(row=2)# Radio bouton personalisé
            def act():
                ecran=x.get()                                               # on récupère l'info de radiobuouton
                if ecran=="PE":                                             # si plein écran
                    fenetreParam.destroy()                                  # on ferme la fenetre param
                    tk.attributes("-fullscreen",True)                       # plein écran
                elif ecran=="F":                                            # si fenétré
                    fenetreParam.destroy()                                  # on ferme la fenetre param
                    tk.attributes("-fullscreen",False)                      # fenétré
                    self.w,self.h=tk.winfo_screenwidth()-20,tk.winfo_screenheight()-100 # redéfinition des dimensions | (winfo_screenXXX) retourne l'entiereté de l'écran, sans décompter les bordures ou la barr windows
                    self.w,self.h=self.w-20,self.h-100
                    tk.geometry("%dx%d"%(self.w,self.h))                    # taille de la fenetre
                #elif ecran=="FP":                                          # si fenétré personalisé | pas très probant 
                #    fenetreParam.destroy()                                 # on ferme la fenetre param
                #    self.w,self.h=int(w.get()),int(h.get())            
                #    tk.attributes("-fullscreen",False)
                #    tk.geometry("%dx%d"%(self.w,self.h))
                #    self.FenetreValou.geometry("%dx%d"%(self.w,self.h))
                fenetreParam.destroy()                                      # si on arrive la, ce qui ne devrait pas, on ferme la fenetre param sans rien faire
            Button(fenetreParam,text="Ok",command=act).pack(side=BOTTOM)    # bouton ok

        # faute de temps, les boutons play, pause et stop n'ont pas été implémentés
         #Bouton play
        # def play():
        #     print("#IHM/init/play")
         #Bouton pause
        # def pause():
        #     print("#IHM/init/pause")
         #Bouton stop
        # def stop():
        #     print("#IHM/init/stop")

        # création de la barre de menu
        menubar=Menu(self)
        menu1=Menu(menubar,tearoff=0)
        menu1.add_command(label="Ajouter un nouveau poste",command=self.ajouter)
        menu1.add_command(label="Modifier un poste",command=self.modifier)
        menu1.add_command(label="Supprimer un poste",command=self.suppr)
        menu1.add_command(label="Nombre postes",command=self.cbDeTags)
        menu1.add_separator()
        menu1.add_command(label="Editer sur la ligne",command=edit)
        menu1.add_separator()
        menu1.add_command(label="Supprimer tous les postes",command=reinit)
        menu1.add_separator()
        menu1.add_command(label="Revenir à l'état initial",command=reset)
        menu2=Menu(menubar,tearoff=0)
        menu2.add_command(label="Programmation manuelle",command=self.prog)
        menu3=Menu(menubar,tearoff=0)
        menu3.add_command(label="Fenetre",command=param)
        menubar.add_cascade(label="Ligne",menu=menu1)
        menubar.add_cascade(label="Scénarios",menu=menu2)
        menubar.add_cascade(label="Affichage",menu=menu3)
        menubar.add_command(label="Quitter",command=quitter)
        #play=PhotoImage(file='PRD-Excelcar-main\Versionfinale\play.png',height=10,width=10)
        #menubar.add_command(image=play,compound='left',command=play)
        #pause=PhotoImage(file='PRD-Excelcar-main\Versionfinale\pause.png',height=10,width=10)
        #menubar.add_command(image=pause,compound='left',command=pause)
        #stop=PhotoImage(file='PRD-Excelcar-main\Versionfinale\stop.png',height=10,width=10)
        #menubar.add_command(image=stop,compound='left',command=stop)
        tk.config(menu=menubar)

        # création du titre
        self.FenetreValou.create_text(self.w*5/10,self.h/10,text="Ligne d'assemblage 4.0\nExcelCar",fill='red',font=('Times',20,'bold'),justify='center')
        
        # création du tracé de la ligne
        print("#IHM/init/creationLigne")                                    # Tout les point de coordonées ont été calculés avec des coef et de la trigo afin de représenter au mieu xla ligne sur toutes les dimensions d'écran possible
        def arc(canvas,x,y,r,t0,t1):
            return canvas.create_arc(x-r,y-r,x+r,y+r,start=t0,extent=t1-t0,style='arc',width=3)
        self.IV=[self.w*2/10,self.h*3/10]                                   # le point IV est le point de croisement entre la ligne droite et le cercle du haut gauche
        self.III=[(self.w*8/10)-(self.h*0.173),self.h*3/10]                 # le point IV est le point de croisement entre la ligne droite et le cercle du haut droite
        self.II=[self.w*8/10,self.h*6/10]                                   # le point IV est le point de croisement entre la ligne droite et le cercle du bas gauche
        self.I=[self.w*2/10+(self.h*0.173),self.h*6/10]                     # le point IV est le point de croisement entre la ligne droite et le cercle du bas droite
        self.FenetreValou.create_line(self.IV,self.III,width=3)             # ligneSup
        arc(self.FenetreValou,self.w*8/10,self.h*4/10,self.h*2/10,-90,150)  # cercleDroite
        self.FenetreValou.create_line(self.II,self.I,width=3)               # ligneInf
        arc(self.FenetreValou,self.w*2/10,self.h*5/10,self.h*2/10,90,330)   # cercleGauche
        self.vit_droit=1.2                                                  # multiplicateur de vitesse en ligne droite
        self.vit_virage=0.9                                                 # multiplicateur de vitesse en virage
        
        # création des tags fixes
        print("#IHM/init/creationTags")
        self.TagStart=[(self.w*2/10)-(self.h*0.17),(self.h*4/10)]
        TagAcc1=self.III
        TagAcc2=self.I
        TagFrein1=self.IV
        TagFrein2=self.II
        self.create_circle(self.TagStart[0],self.TagStart[1],10,"grey",self.FenetreValou)
        self.create_circle(TagAcc1[0],TagAcc1[1],10,"green",self.FenetreValou)
        self.create_circle(TagAcc2[0],TagAcc2[1],10,"green",self.FenetreValou)
        self.create_circle(TagFrein1[0],TagFrein1[1],10,"red",self.FenetreValou)
        self.create_circle(TagFrein2[0],TagFrein2[1],10,"red",self.FenetreValou)

        # création de la fenetre FenetreGus
        self.FenetreGus=Canvas(tk,width=self.w,height=self.h,bg='#d2d2d2')  # la couleur #d2d2d2 est un gris plutot clair

        print("\n>>> LAUNCHING IHM\n")

        # Affichage des fenetres
        self.FenetreValou.pack(side=TOP)                                    # Positionnement de le FenetreValou dans la partie supérieure
        self.FenetreGus.pack(side=BOTTOM)                                   # Positionnement de le FenetreGus dans la partie inférieure
        self.add(self.FenetreValou)                                         # Ajout dans le pannedWindow
        self.add(self.FenetreGus)                                           # Ajout dans le pannedWindow
        self.pack(fill=BOTH,expand=True)                                    # Permet au canvas de remplir entièrement la fenetre peut importe la taille de celle ci
        self.sash_place(index=0,x=0,y=sas)                                  # Place le séparateur à la hauteur sas

        # ajout des postes
        self.charger()                                                      # Charge la ligne

         # initialisation des portes
        self.portesprodglob=[]                                              # Ensemble des portes de la production depuis le depart
        self.p=5                                                            # Facteur de proportionalité qui fait varié la vitesse de simulation
        self.ovales=[]                                                      # Ensemble des canvas ovales représentant les portes
        self.ido=0                                                          # id de chaque canvas AGV
        self.pep=[]                                                         # Tableaux avec toutes les portes en production
        self.portesFini=0                                                   # Nombre de portes terminé
        self.tp=[]                                                          # Liste des temps de production
        self.nbAGV=2                                                        # Nombre de portes max sur la ligne
        self.tpsProdAV=350                                                  # Temps moyen pour la production d'une porte AV en s
        self.tpsProdAR=287                                                  # Temps moyen pour la production d'une porte AR en s

        # Affichage en direct de la production
        self.premiercoup=0                                                  # Integer utile a l'utilisation de l'affichage
        thread=threading.Thread(target=self.affichage)                      # Creation du Thread affichage
        thread.start()

# Remplace prevLogPoste par le LogPost actuel
    def majPLP(self):
        print("#IHM/majPLP")
        file=open("LogPoste.txt","r")                                       # Lecture de LogPoste
        lines=file.readlines()                                              # Récupération du contenu
        file.close()
        file=open("prevLogPoste.txt","w")                                   # Ecraser prevLogPoste
        file.writelines(lines)                                              # Recopier le contenu de LogPoste dans prevlogPoste
        file.close()

# Annule les précédentes modifications
    def annuleModifs(self):
        print("#IHM/annuleModifs")
        file=open("prevLogPoste.txt","r")                                   # Lecture de prevLogPoste
        lines=file.readlines()                                              # Récupération du contenu
        file.close()
        file=open("LogPoste.txt","w")                                       # Ecraser LogPoste
        file.writelines(lines)                                              # Recopier le contenu de prevLogPoste dans LogPoste
        file.close()

# Sauvegarde les modif dans le LogPoste
    def save(self,save):
        print("#IHM/save")
        file=open("LogPoste.txt","r")                                       # Lecture de LogPoste
        lines=file.readlines()                                              # Récupération du contenu
        file.close()
        file=open("LogPoste.txt","w")                                       # Ecraser LogPoste
        if save: file.write("o;\n")                                         # si on souhaite sauvegarder, on écrit o; sur la première ligne
        else: file.write("n;\n")                                            # si non, on écrit n;
        file.writelines(lines[1:])                                          # on recopie le contenu de LogPoste sauf la première ligne de sauvegarde
        file.close()

# Modif du nb de tags sur la ligne
    def cbDeTags(self):
        print("#IHM/cbDeTags")
        FenetreInit=Tk()                                                    # Création d'une fentre sup
        FenetreInit.title("Initialisation")
        def act():                                                          # action du bouton
            newNbPoste=int(oui.get())                                       # on lit la valeur entrée
            self.ligne.nbPostes=newNbPoste                                  # on modifie la ligne
            FenetreInit.destroy()                                           # fermeture de la fenetre
            self.charger()                                                  # on recharge la ligne
        Label(FenetreInit,text="Bienvenue sur\nEXCELCAR 3000",fg="#8b0000",font="bold").pack()  # la couleur #8b0000 est un rouge foncé
        Label(FenetreInit,text="Combien de Tags poste sur la ligne?").pack()# texte
        oui=StringVar(FenetreInit)                                          # valeur de la spinbox
        oui.set(str(self.ligne.getNbPostes()))                              # valeur par défaut
        spino=Spinbox(FenetreInit,from_=1,to=20,textvariable=oui)           # Selecteur de valeur avec limitation de valeur
        spino.pack()
        Button(FenetreInit,text="Ok",command=act).pack()                    # bouton de conmande

# Trace les cercles de Tags cercles sur la ligne | cette fonction estplus pratique à utiliser que la create ovale de base
    def create_circle(self,x,y,r,color,canvasName):                         # center coordinates, radius, color, canvas
            x0=x-r
            y0=y-r
            x1=x+r
            y1=y+r
            return canvasName.create_oval(x0,y0,x1,y1,fill=color)
            
# Création d'un Thread AGV ainsi que de son Canva correspondant.
    def ajouterPorte(self,tps,*type):                                       # Tps = temps d'attente d'une porte une fois crée.  
        if tps!=0 :                                                         # Cas d'un scénario
            self.ido+=1
            r=7
            cp=self.FenetreValou.create_oval(self.TagStart[0]-r,self.TagStart[1]-r,self.TagStart[0]+r,self.TagStart[1]+r,fill='red',width=2)
            self.ovales.append(cp)
            postes=[]
            for p in self.ligne.getPostes():
                postes.append(p)
            newAGV=AGV.AGV(self,self.ido,self.TagStart,postes,tps,type[0]) 
            newAGV.start()
            #newAGV.join()
            self.pep.append(newAGV)
            self.portesprodglob.append(newAGV)
        else:                                                               # Cas d'une production avec départ des portes depuis le Bouton start
            if len(self.pep)<self.nbAGV :
                self.ido+=1
                r=7
                cp=self.FenetreValou.create_oval(self.TagStart[0]-r,self.TagStart[1]-r,self.TagStart[0]+r,self.TagStart[1]+r,fill='red',width=2)
                self.ovales.append(cp)
                postes=[]
                for p in self.ligne.getPostes():
                    postes.append(p)
                newAGV=AGV.AGV(self,self.ido,self.TagStart,postes,tps,type[0])
                newAGV.start()
                #newAGV.join()
                self.pep.append(newAGV)
                self.portesprodglob.append(newAGV)
            else: showerror("Surpopulation","Impossible car trop d'AGV sur la ligne. \n Nombre de portes maximum : "+str(self.nbAGV)+".")

# Affichage des postes sur la ligne
    def charger(self):                                                      # permet de recharger la ligne par rapport à ce qui figure dans le LogPoste
        self.clear()                                                        # Vide la ligne et replace les Tags
        if not self.edition:                                                # Si on est pas en mode édition
            self.ligne.lecture()                                            # Charge le LogPoste dans la ligne
        print("#IHM/charger")
        nbPoste=self.ligne.getNbPostes()                                    # renaming des vaiables self pour la praticité
        tagList=self.ligne.getTagsPostes()
        posi=self.ligne.listPosi()
        posAttrib=[]                                                        # liste [int] des position utilisées
        for p in self.ligne.getPostes():
            posAttrib.append(p.getPosition())                               # on rempli la liste avec les postes actuels
        if nbPoste<len(posi) or max(posAttrib)>max(posi):                   # petit message d'erreur si la position n'est pas valable
            print("\n>>>ERREUR: pas assez de Tags\n")
            print("\tnb de poste =",nbPoste,"nb de posi dispo =",len(posi),"insertion des postes:",nbPoste<len(posi))
            print("\tposition la plus élevé des postes =",max(posAttrib),"position max possible =",max(posi),"insertion des postes:",max(posAttrib)<max(posi))
            showerror("Ligne trop petite","Il n'y a pas assez de Tags pour une des positions demandée")
            self.cbDeTags()                                                 # avec possibilité de rajouter des Tags postes s'il en manque
        else:                                                               # si tout va bien:
            # Charger Boutons en mode Classique
            self.btnPoste.clear()                                           # on efface les boutons existants dans les données de l'ihm
            for i in posi:
                p=self.ligne.getPosteByPosition(i)                          # On récupère le poste à la position i
                bouton=Button(self.FenetreValou,text=p.getNom(),font=('Times',14),bg='cyan',command=partial(self.info,p))   # on créé un bouton pour le poste
                posx,posy=tagList[i-1][0],tagList[i-1][1]                   # on le place à la position du tag
                bouton.place(x=posx,y=posy)
                self.btnPoste.append(bouton)                                # on l'enregistre dans la liste des boutons
            # Charger bouton en mode Edition
                if self.edition==True:                                      # si on est en mode edition
                    self.update()                                           # on regarde ( et met à jour tte les positions existantes sur l'ihm)
                    posx1,posy1=bouton.winfo_width(),bouton.winfo_height()  # on récupère les dimensions du bouton créé 
                    bouton.destroy()                                        # on supprime le bouton
                    repBtn=self.FenetreValou.create_rectangle(posx,posy,posx+posx1,posy+posy1,fill='cyan')  # on créé un rectangle de meme dimension que le bouton
                    txtBtn=self.FenetreValou.create_text(posx+posx1/2,posy+posy1/2,text=p.getNom(),font=('Times',14))   # on place le nom du poste en son centre, on vient de créer la représentation du bouton pendant le mode édition
                    tag="bouton-{}".format(p.getNom())                      # on créé un tag spécifique pour chaque bouton (bouton-NomDuPoste)
                    self.FenetreValou.addtag_withtag(tag,repBtn)            # on associe ce tag au rectangle
                    self.FenetreValou.addtag_withtag(tag,txtBtn)            # on associe ce tag au texte
                    self.FenetreValou.addtag_withtag("postes_edit",repBtn)  # on associe le rectangle au tag plus général "postes_edit"
                    self.FenetreValou.addtag_withtag("postes_edit",txtBtn)  # on associe le texte au tag plus général "postes_edit"
                    self.first=True                                         # petite variable pour n'afficher qu'une seule fois le massage de mvt
                    def move(event):                                        # fonction de déplacement du poste sur un mouvement avec click gauche
                        if self.first:print("#IHM/charger/move")
                        def node_center(tag):                               # permet de centrer le poste au centre de la souris lors d'un click+mouvement
                            if len(self.FenetreValou.coords(tag))==4:       # si on click sur le rectangle
                                x1,y1,x2,y2=self.FenetreValou.coords(tag)
                                return(x1+x2)//2,(y1+y2)//2
                            elif len(self.FenetreValou.coords(tag))==2:     # si on click sur le texte
                                x1,y1=self.FenetreValou.coords(tag)
                                return x1,y1
                        x,y=event.x,event.y                                 # position de la souris
                        tags=self.FenetreValou.gettags(CURRENT)             # selection du tag du poste sur lequel on click
                        for tag in tags:
                            if not tag.startswith("bouton"):continue        # si c'est bien un bouton, on continue
                            x1,y1=node_center(tag)                          # on centre
                            if self.first:                                  # lors du premier mvt, affiche un msg console indiquant ce qu'on bouge
                                print("\tmouvement de "+tag)
                                self.first=False                            # pour ne pas a avoir afficher ce message 150 fois pour 1 mvt
                            self.FenetreValou.move(tag,x-x1,y-y1)           # déplacement
                    def release(event):                                     # ce qui se passe lorsqu'on relache le click
                        print("#IHM/charger/release")
                        tags=self.FenetreValou.gettags(CURRENT)             # on selectionne le tag du poste sur lequel on cliquais jusque la
                        for tag in tags:
                            if not tag.startswith("bouton"):continue        # on revérifie que c'est tjrs un bouton
                            oui=self.FenetreValou.coords(tag)               # on récupère ses coordonées
                            hitbox=100                                      # distance de détection autour du tag dans laquelle si un poste est laché, il sera aimenté sur le tag
                            pos=0
                            nom=tag[7:]                                     # récupération du nom du poste au travers du tag nominatif
                            p=self.ligne.getPosteByName(nom)                # on récupère le poste grace au nom
                            for positag in self.ligne.getTagsPostes():
                                pos+=1
                                if oui[0]>=positag[0]-hitbox and oui[0]<=positag[0]+hitbox and oui[1]>=positag[1]-hitbox and oui[1]<=positag[1]+hitbox: #si le poste est relaché dans ces coordonées
                                    print("\t",pos,": posi valide")
                                    newposi=positag                         # les coordonées du tags deviennebt celle du postes, et la position du tag, celle du poste
                                    break                                   # si on est arrivé la, pas besoins de continuer la boucle
                                else: 
                                    newposi=self.ligne.getTagsPostes()[p.getPosition()-1]   # sinon, ca signifie que le poste n'a pas été placé sur une position valide, les nouvelles coordonées seront les mêmes que les anciennes
                            self.first=True                                 # le mvt est fini on repasse first à true pour le prochain mvt
                            self.FenetreValou.move(tag,newposi[0]-oui[0],newposi[1]-oui[1]) # on effectue le mouvement jusqu'au nouvelle coordonées
                            self.modifier("change",p,pos)                   # on enregistre le changement de position du postes
                    def click(event):                                       # lors d'un simple click droit
                        print("#IHM/charger/release")
                        tags=self.FenetreValou.gettags(CURRENT)             # on selectionne le tag du poste sur lequel on clique
                        for tag in tags:
                            if not tag.startswith("bouton"):continue        # on vérifie que c'est bien un bouton qu'on a selectionné
                            self.info(self.ligne.getPosteByName(tag[7:]))   # on récupère me nom du poste et on nous affiche ses infos
                    self.FenetreValou.tag_bind(repBtn,'<B1-Motion>',move)   # on lie le rectangle avec la fonction move sur click droit + mvt
                    self.FenetreValou.tag_bind(txtBtn,'<B1-Motion>',move)   # on lie le texte avec la fonction move sur click droit + mvt
                    self.FenetreValou.tag_bind(repBtn,'<ButtonRelease-1>',release)  # on lie le rectangle avec la fonction release sur relachement du click droit
                    self.FenetreValou.tag_bind(txtBtn,'<ButtonRelease-1>',release)  # on lie le texte avec la fonction release sur relachement du click droit
                    self.FenetreValou.tag_bind(repBtn,'<Button-3>',click)   # on lie le rectangle avec la fonction click sur click droit
                    self.FenetreValou.tag_bind(txtBtn,'<Button-3>',click)   # on lie le texte avec la fonction click sur click droit

# Info du poste selctionné
    def info(self,poste):                                                   # donne les infos sur le poste selectionné
        print("#IHM/Info/"+poste.getNom())
        InfoPoste=Tk()                                                      # création d'une nouvelle fenetre
        InfoPoste.title(str(poste.getNom()))
        labelnom=Label(InfoPoste,text="Nom du Poste: "+str(poste.getNom())) # texte: nom du poste
        labeltype=Label(InfoPoste,text="Type "+str(poste.getType()))        # texte: type du poste
        labelposition=Label(InfoPoste,text="Position n°"+str(poste.getPosition()))  # texte: position du poste
        labelaction=Label(InfoPoste,text="Action: "+str(poste.getAction())) # texte: action du poste
        labeletat=Label(InfoPoste,text="Poste en action: "+str(poste.getEtat())+"\n")   # texte: etat du poste
        labelnom.pack()
        labeltype.pack()
        labelposition.pack()
        labelaction.pack()
        labeletat.pack()
        def act():                                                          # action du bouton modifier
            choice=Tk()                                                     # nouvelle fnetre de modification
            choice.title("Modification")
            Label(choice,text="Quelle modification à apporter sur "+poste.getNom()+"?").pack()
            oui=Listbox(choice, height=3)                                   # Listbox: selecteur parmis les éléments rentrées ci dessous
            oui.insert(1,"Nom")
            oui.insert(2,"Position")
            oui.insert(3,"Action")
            oui.pack()
            def choose():                                                   # action du bouton ok de la fenetre modification
                choix=oui.get(ACTIVE)                                       # récupère l'info selctionnée dans la listbox
                if choix=="Nom":self.modifier("changerNom",poste.getNom())  # réagi en fonction de la selection
                elif choix=="Position":self.modifier("changerPosi",poste.getNom())
                elif choix=="Action":self.modifier("changerAction",poste.getNom())
                choice.destroy()                                            # fin de la fenetre modif
            button_frame=Frame(choice)                                      # groupement des boutons
            button_frame.pack(side=BOTTOM)                                  # en bas de la fenetre
            Button(button_frame,text="Ok",command=choose).grid(row=0,column=0)
            Button(button_frame,text="Annuler",command=choice.destroy).grid(row=0,column=1)
            InfoPoste.destroy()
        def act2():                                                         # action du bouton supprimer
            if askyesno("SUPPRIMER","Voulez vous vraiment SUPPRIMER "+poste.getNom()+"?"):
                self.ligne.supprimer(poste)
                InfoPoste.destroy()
                self.charger()
        button_frame=Frame(InfoPoste)
        button_frame.pack()
        Button(button_frame,text="Modifier",command=act).grid(row=0,column=0)
        Button(button_frame,text="Supprimer",command=act2).grid(row=0,column=1)
        Button(InfoPoste,text="Fermer",command=InfoPoste.destroy).pack()

# Ongelt de création et ajout d'un nouveau poste
    def ajouter(self):                                                      # fonction d'ajout d'un poste
        print("#IHM/ajouter")                                               # la technique de création de fentre et d'insertion de texte/fonctionnalitées est très similaire à ce qu'on a vu précédement
        FenetreAjout=Tk()        
        FenetreAjout.title("Ajouter un Poste")
        labelnom=Label(FenetreAjout,text="Titre du poste :")
        labelnom.pack()
        nom=Entry(FenetreAjout,width=30)
        nom.pack()
        labeltype=Label(FenetreAjout,text="Type de poste : (Défaut: Automatique)")
        labeltype.pack()
        tip=Listbox(FenetreAjout,height=2,selectbackground="Grey",exportselection=False)
        tip.insert(1,"Automatique")
        tip.insert(2,"Manuel")
        tip.width=2
        tip.pack()
        labelposi=Label(FenetreAjout,text="Position du poste : (Max: "+str(self.ligne.getNbPostes())+")")
        labelposi.pack()
        if self.posiDispo()==[0]:posi=Label(FenetreAjout,text="Pas assez de Tags",bg="white",fg="#8b0000",font="bold")
        else:
            var=IntVar(FenetreAjout)
            posi=OptionMenu(FenetreAjout,var,*self.posiDispo())
        posi.pack()
        labelaction=Label(FenetreAjout,text="Action du poste :")
        labelaction.pack()
        action=Entry(FenetreAjout,width=30)
        action.pack()
        def act():                                                          # action du bouton créer
            FenetreAjout.attributes("-topmost",False)                       # topmost est la commande pour mettre au premier plan
            if nom.get()=="" or action.get()=="":                           # cas ou l'utilisateur n'a pas rempli tous les champs
                showwarning("Champs incomplet(s)","Veuillez remplir tous les champs avant de valider le poste")
                FenetreAjout.attributes("-topmost",True)                    # on remet la fenetre d'ajout au premier plan
                pass
            elif askyesno('Créer un Poste','Voulez vous ajouter \"'+nom.get()+'\" à la ligne?'):
                newposte=Poste.Poste(nom.get(),tip.get(ACTIVE),var.get(),action.get())
                self.ligne.ajout(newposte)
                file=open("LogPoste.txt","a")
                file.write("\n"+nom.get()+";"+tip.get(ACTIVE)+";"+str(var.get())+";"+action.get())
                file.close()
                self.charger()
                FenetreAjout.destroy()
                showinfo("Poste Ajouté","le poste "+nom.get()+" à bien été ajouté à la ligne")
            else:FenetreAjout.attributes("-topmost",True)
        def oui():                                                          # action du bouton ajouter des tags
            FenetreAjout.destroy()
            self.cbDeTags()
        Button(FenetreAjout,text="Ajouter des tags",command=oui).pack()
        button_frame=Frame(FenetreAjout)
        button_frame.pack(side=BOTTOM)
        Button(button_frame,text="Créer",command=act).grid(row=0,column=0)
        Button(button_frame,text="Annuler",command=FenetreAjout.destroy).grid(row=0,column=1)

# Deplacement de du Canva d'un AGV le long de la ligne, renvoi la nouvelle position de l'AGV a chaque appel
    def deplacement(self,pos,id,porte):
        r=7
        R=self.h*2/10                                                       # Rayon des cercles
        hd,kd=self.w*8/10,self.h*4/10
        hg,kg=self.w*2/10,self.h*5/10
        x,y=pos[0],pos[1]
        a,b,c,d,e,f=round(self.IV[0]),round(self.IV[1]),round(self.III[0]),round(self.II[1]),round(self.I[0]),round(self.II[0])
        if y==b and x<=c and x>e:                                           # Ligne supérieure entre c et e
            p=1.2*porte.getVitesse()
            x=x-p
            if x<e:
                x=e
            self.FenetreValou.coords(self.ovales[id-1],x-r,y-r,x+r,y+r)
        elif y==d and x<c and x>=e:                                         # Ligne inférieure entre e et c
            p=1.2*porte.getVitesse()
            x=x+p
            if x>c:
                x=c
            self.FenetreValou.coords(self.ovales[id-1],x-r,y-r,x+r,y+r)
        elif x<=e and y>=b-1:                                               # Partie Gauche
            if y>=self.TagStart[1]:                                         # Arc de cercle gauche en dessous du Start
                cercle=np.arange(7*pi/6,pi/6,-0.9*porte.getVitesse()/(self.h*2/10))
                cercle[-1]=pi/6
                x=hg+R*np.cos(cercle[porte.getXg2()])
                y=kg+R*np.sin(cercle[porte.getXg2()])
                porte.xg2+=1
                if cercle[porte.getXg2()]==pi/6:
                    y=d
                    x=e 
                self.FenetreValou.coords(self.ovales[id-1],x-r,y-r,x+r,y+r)  
            if x>a and y==b:                                                # Ligne supérieure entre e et a                          
                p=1.2*porte.getVitesse()
                x=x-p
                if x<a:
                    x=a
            self.FenetreValou.coords(self.ovales[id-1],x-r,y-r,x+r,y+r)
            if x<=a+1 and y<self.TagStart[1]:                               # Arc de cercle gauche au dessus du Start
                cercle=np.arange(3*pi/2,4.7*pi/4,-0.9*porte.getVitesse()/(self.h*2/10))
                cercle[-1]=4.7*pi/4
                x=hg+R*np.cos(cercle[porte.getXg1()])
                y=kg+R*np.sin(cercle[porte.getXg1()])
                self.FenetreValou.coords(self.ovales[id-1],x-r,y-r,x+r,y+r)
                porte.xg1+=1
                if cercle[porte.getXg1()]==4.7*pi/4:                        # Fin de la ligne, suppression de la porte et du Thread
                    Transmission.EnvoiDonneeDirect(porte.Temps(),porte.id,porte.type,"La porte est terminée","")
                    end=time.time()
                    self.tp.append(end-porte.timeur)
                    porte.interuption()
                    self.portesFini+=1
                    print("Sortie de la porte n°",porte.id,". C'est un succes !")
        elif x>=c and y<=d+1:                                               # Partie droite
            if x<f and y==d:                                                # Ligne inférieure entre c et f
                p=1.2*porte.getVitesse()
                x=x+p
                if x>f:
                    x=f
                self.FenetreValou.coords(self.ovales[id-1],x-r,y-r,x+r,y+r)
            else:                                                           # Cercle de Droite
                cercle=np.arange(pi/2,-5*pi/6,-0.9*porte.getVitesse()/(self.h*2/10))
                cercle[-1]=-5*pi/6
                x=hd+R*np.cos(cercle[porte.getXd()])
                y=kd+R*np.sin(cercle[porte.getXd()])
                porte.xd+=1
                if cercle[porte.getXd()]==-5*pi/6:
                    x=c
                    y=b
                self.FenetreValou.coords(self.ovales[id-1],x-r,y-r,x+r,y+r)
        else:                                                               # Si la porte est sortie
            porte.interuption()
            print("Probleme technique : La porte n°",id,"est sortie de la ligne")
        self.update()
        return [x,y]

# Onglet de modification de poste existant | ATTENTION fonction récursive
    def modifier(self,*arg):                                                # permet de changer les attributs d'un poste
        neoDel=[]                                                           # liste qui contiendra les ifos de arg
        for i in arg:                                                       # permet une meilleur manipulation de arg
            neoDel.append(i)                                                # car le argument après * sont forcément des tuples, or je préfère les listes
        arg=neoDel
        if len(arg)==0:                                                     # si il n'y a pas d'info sur ce qu'il faut modifier, typiquement: le modifier du menu Ligne            
            print("#IHM/modifier")                                          # qui permet de choisir ce qu'on modifie
            FenetreModif=Tk()
            FenetreModif.title("Modifier")
            listePostes=Listbox(FenetreModif,height=4,selectbackground="Grey",exportselection=False)
            i=1
            for po in self.ligne.getPostes():
                listePostes.insert(i,po.getNom())
            labelselect=Label(FenetreModif,text="Selectionner le poste à modifier: (Par défaut = "+listePostes.get(ACTIVE)+")")
            labelselect.pack()
            listePostes.pack()
            labelselect=Label(FenetreModif,text="Quel paramètre modifier:")
            labelselect.pack()
            listemodif=Listbox(FenetreModif,height=3,selectbackground="Grey",exportselection=False)
            listemodif.insert(1,"Nom")
            listemodif.insert(2,"Position")
            listemodif.insert(3,"Action")
            labelmodif=Label(FenetreModif,text="Selectionner le paramètre à modifier: (Par défaut = "+listemodif.get(ACTIVE)+")")
            labelmodif.pack()
            listemodif.pack()
            def act():                                                      # action du bouton Selectionner
                nomPoste=listePostes.get(ACTIVE)
                modif=listemodif.get(ACTIVE)
                FenetreModif.attributes("-topmost",False)
                if nomPoste=="" or modif=="":
                    showwarning("Champs incomplet(s)","Veuillez selectionner un poste et une modification")
                    FenetreModif.attributes("-topmost",True)
                    pass
                elif modif=="Nom":
                    FenetreModif.destroy() 
                    self.modifier("changerNom",nomPoste)                    # on rappelle la fonction avec le poste et la modification à effectuer
                elif modif=="Position":
                    FenetreModif.destroy()
                    self.modifier("changerPosi",nomPoste)                   # on rappelle la fonction avec le poste et la modification à effectuer
                elif modif=="Action":
                    FenetreModif.destroy()
                    self.modifier("changerAction",nomPoste)                 # # on rappelle la fonction avec le poste et la modification à effectuer
                else: showwarning("Erreur","Erreur lol\nc'est la merde si ca arrive la: il t'invente des valeurs")  # on ne devrait jamais en arriver la...
            button_frame=Frame(FenetreModif)
            button_frame.pack(side=BOTTOM)
            Button(button_frame,text="Selectionner",command=act).grid(row=0,column=0)
            Button(button_frame,text="Annuler",command=FenetreModif.destroy).grid(row=0,column=1)
        if len(arg)!=0 and arg[0]=="changerNom":                            # Changement du nom d'un poste à partir du poste
            print("#IHM/modifier/ChangerNom")
            NomPoste=arg[1]
            nomModif=Tk()
            nomModif.title("Nom de "+NomPoste)
            Label(nomModif,text="Selectionner le nouveau nom pour "+NomPoste+":").pack()
            Label(nomModif,text="(ancien: "+NomPoste+")").pack()
            nom=Entry(nomModif,width=30)
            nom.pack()
            def act():                                                      # action du bouton modifier
                newNom=str(nom.get())
                if askyesno("Modifier","Voulez vraiment modifier \""+NomPoste+"\"\nen \""+newNom+"\" ?"):
                    nomModif.attributes("-topmost",False)
                    P=self.ligne.getPosteByName(NomPoste)
                    P.Nom=newNom
                    self.ligne.modifLogPoste()
                    self.charger()
                    nomModif.destroy()
                else:nomModif.attributes("-topmost",True)
            button_frame=Frame(nomModif)
            button_frame.pack(side=BOTTOM)
            Button(button_frame,text="Modifier",command=act).grid(row=0,column=0)
            Button(button_frame,text="Annuler",command=nomModif.destroy).grid(row=0,column=1)
        elif len(arg)!=0 and arg[0]=="changerPosi":                         # Changement de la position d'un poste à partir du poste
            print("#IHM/modifier/ChangerPosi")
            NomPoste=arg[1]
            posiModif=Tk()
            posiModif.title("Postion de "+NomPoste)
            Label(posiModif,text="Il y a actuellement "+str(self.ligne.nbPostes)+" Tags pouvant acceuillir les postes").pack()
            Button(posiModif,text="Ajouter des tags",command=self.cbDeTags).pack()
            Label(posiModif,text="Selectionner la nouvelle position pour "+NomPoste+":\n(ancien: "+str(self.ligne.getPosteByName(NomPoste).getPosition())+")").pack()
            selectposi=Spinbox(posiModif,from_=1,to=self.ligne.nbPostes)
            selectposi.pack()
            def act():  # action du bouton modifier
                newposi=int(selectposi.get())
                p1=self.ligne.getPosteByName(NomPoste)
                p2=self.ligne.getPosteByPosition(newposi)
                if p1!=NONE and p2!=NONE:
                    if askyesno("Modifier","Voulez vraiment échanger la position de\n\""+NomPoste+"\" avec \""+p2.getNom()+"\"\n(position "+str(p1.getPosition())+" à "+str(p2.getPosition())+") ?"):
                        posiModif.attributes("-topmost",False)
                        oldposi=p1.getPosition()
                        p1.position=newposi
                        p2.position=oldposi
                        self.ligne.modifLogPoste()
                        self.charger()
                        posiModif.destroy()
                    else:posiModif.attributes("-topmost",True)  
                else: 
                    if askyesno("Modifier","Voulez vraiment modifier la position de \""+NomPoste+"\"\n(position "+str(p1.getPosition())+" à "+str(newposi)+") ?"):
                        posiModif.attributes("-topmost",False)
                        p1.position=newposi
                        self.ligne.modifLogPoste()
                        self.charger()
                        posiModif.destroy()
                    else:posiModif.attributes("-topmost",True)
            button_frame=Frame(posiModif)
            button_frame.pack(side=BOTTOM)
            Button(button_frame,text="Modifier",command=act).grid(row=0,column=0)
            Button(button_frame,text="Annuler",command=posiModif.destroy).grid(row=0,column=1)
        elif len(arg)!=0 and arg[0]=="changerAction":                       # Changement de l'action d'un poste à partir du poste
            print("#IHM/modifier/ChangerAction")
            NomPoste=arg[1]
            actModif=Tk()
            actModif.title("Action de "+NomPoste)
            Label(actModif,text="Selectionner la nouvelle fonction pour "+NomPoste+": ").pack()
            Label(actModif,text="(ancien: "+str(self.ligne.getPosteByName(NomPoste).getAction())+")").pack()
            action=Entry(actModif,width=30)
            action.pack()
            def act():                                                      # action du bouton modifier
                newAction=str(action.get())
                P=self.ligne.getPosteByName(NomPoste)
                if askyesno("Modifier","Voulez vraiment modifier la fonction de \""+NomPoste+"\"\nqui faisait \""+P.getAction()+"\"\net qui fera \""+newAction+"\" ?"):
                    actModif.attributes("-topmost",False)
                    P.action=newAction
                    self.ligne.modifLogPoste()
                    self.charger()
                    actModif.destroy()
                else:actModif.attributes("-topmost",True)
            button_frame=Frame(actModif)
            button_frame.pack(side=BOTTOM)
            Button(button_frame,text="Modifier",command=act).grid(row=0,column=0)
            Button(button_frame,text="Annuler",command=actModif.destroy).grid(row=0,column=1)
        elif len(arg) and arg[0]=="change":                                 # Change la posi d'un poste sans demande (glisser/déposer)
            p1=arg[1]
            newposi=arg[2]
            print("#IHM/modifier/change/"+p1.getNom())
            p2=self.ligne.getPosteByPosition(newposi)
            oldposi=p1.getPosition()
            if p1!=NONE and p2!=NONE:
                p1.position=newposi
                p2.position=oldposi
            else:
                p1.position=newposi
            self.ligne.modifLogPoste()
            self.charger()

# Supprime les bouttons présent sur la fenetre et initiales le start
    def clear(self):                                                        # Fonction de vidage de ligne
        print("#IHM/clear")
        if self.edition:                                                    # si on est mode édition
            for btn in self.btnPoste: btn.destroy()                         # supprime que les boutons postes existants
        else:
            for item in self.FenetreValou.winfo_children():item.destroy()   # sinon supprime tous les items existants sur la ligne (boutons + curseurs + frames + ...)
        for i in self.Tag:self.FenetreValou.delete(i)                       # supprime tous les tags postes (en bleu) situés sur la ligne
        self.FenetreValou.delete("postes_edit")
        #Création des nouveaux Tags
        nbPoste=self.ligne.getNbPostes()
        posteBas=nbPoste//2                                                 # le nombre de postes existants sur la partie du bas de la ligne
        nTag=1
        self.Tag.clear()                                                    # supprime les données sur le tags poste de l'ihm
        self.ligne.TagsPostes.clear()                                       # supprime les données sur le tags poste de la ligne 
        tagList=self.ligne.getTagsPostes()                                  
        while nTag<=nbPoste:                                                # recréé les tags postes
            if nTag<=posteBas:
                coorTag=[self.I[0]+((self.II[0]-self.I[0])*(nTag)/(posteBas+1)),self.I[1]]
                Tag=self.create_circle(coorTag[0],coorTag[1],10,"blue",self.FenetreValou)
                self.Tag.append(Tag)
                tagList.append(coorTag)
            else: 
                coorTag=[self.IV[0]+((self.III[0]-self.IV[0])*(nbPoste-nTag+1)/((nbPoste-posteBas)+1)),self.IV[1]]
                Tag=self.create_circle(coorTag[0],coorTag[1],10,"blue",self.FenetreValou)
                self.Tag.append(Tag)
                tagList.append(coorTag)
            nTag+=1
        # Placement des boutons de départ
        BoutStart=Frame(self.FenetreValou,bg='white')
        Start=Button(self.FenetreValou,text="Start",font=('Times',14),bg='cyan',command=partial(self.ajouterPorte,0,None))
        Button(BoutStart,text="AV",font=('Times',14),bg='#86DC3D',command=partial(self.ajouterPorte,0,"AV")).grid(row=1,column=0)
        Button(BoutStart,text="AR",font=('Times',14),bg='#86DC3D',command=partial(self.ajouterPorte,0,"AR")).grid(row=1,column=1)
        Start.pack()
        self.update()
        x,y=(self.TagStart[0]-(Start.winfo_width()//2)),(self.TagStart[1]-(Start.winfo_height()//2))
        #Start.place(x=x,y=y)                                                # bouton Start qui permet de lancé un agv vide 
        Start.pack_forget()                                                 # Start enlevé pour plus de lisibilité
        BoutStart.place(x=x-20,y=y)
        # création du curseur de vitesse
        if self.edition:                                                    # on créé le curseur dans le mode édition
            slider=Frame(self.FenetreValou,bg="white")
            value_label=Label(slider,text="vitesse d'execution",bg="white")
            def modif_vitesse(event):
                self.p=int(val.get())
            val=DoubleVar()
            vitesseSlider=Scale(slider,from_=1,to=10,orient='horizontal',command=modif_vitesse,variable=val,bg="white")
            vitesseSlider.set(self.p)
            value_label.pack()
            vitesseSlider.pack()
            slider.place(x=self.w*90/100,y=self.h*5/100)

# Onglet de suppression de poste
    def suppr(self):
        print("#IHM/suppr")
        FenetreSupprimer=Tk()
        FenetreSupprimer.title("Supprimer")
        labelselect=Label(FenetreSupprimer,text="Selectionner le poste à modifier: (Par défaut = "+str(self.ligne.getPostes()[0].getNom())+")")
        labelselect.pack()
        listePostes=Listbox(FenetreSupprimer,height=4,selectbackground="Grey",exportselection=False)
        i=1
        for po in self.ligne.getPostes():
            listePostes.insert(i,po.getNom())
        listePostes.pack()
        def act():
            nomPoste=listePostes.get(ACTIVE)
            if askokcancel("Supprimer","Voulez vraiment SUPPRIMER \""+nomPoste+"\" ?"):
                FenetreSupprimer.attributes("-topmost",False)
                self.ligne.supprimer(self.ligne.getPosteByName(nomPoste))
                FenetreSupprimer.destroy()
                self.charger()
            else:FenetreSupprimer.attributes("-topmost",True)
        button_frame=Frame(FenetreSupprimer)
        button_frame.pack(side=BOTTOM)
        Button(button_frame,text="Supprimer",command=act).grid(row=0,column=0)
        Button(button_frame,text="Annuler",command=FenetreSupprimer.destroy).grid(row=0,column=1)

# liste des places disponibles
    def posiDispo(self):
        nbMax=self.ligne.getNbPostes()
        posi=[]
        vide=True
        for i in range(1,nbMax+1):
            ok=True
            for post in self.ligne.getPostes():
                if i==post.getPosition():
                    ok=False
                    break
            if ok==True:
                posi.append(i)
                vide=False
        if vide:posi.append(0)
        return posi

#Fonction d'affichage des infos concernant les portes
    def affichage(self):
        while True:
            x=self.w*2/10
            y=self.h/10-60
            m=0
            portesmax=100
            if self.premiercoup==0:            # Lors d'un premier lancement, création de tous les emplacements de textes.
                textes=[]
                t=self.FenetreGus.create_text(x,y,text="Portes terminées avec succes : "+str(self.portesFini),fill='black',font=('Times',11,'bold'),justify='center')
                tp=self.FenetreGus.create_text(x+250,y)
                tgp=self.FenetreGus.create_text(self.w*8/10,y)
                for i in range(portesmax):
                    y=y+30
                    t1=self.FenetreGus.create_text(x,y,tags="e" + str(i))
                    textes.append(t1)
                self.premiercoup=1
            else:
                self.FenetreGus.itemconfigure(t,text="Portes terminées avec succes : "+str(self.portesFini))
                temps=round(np.mean(self.tp),2)
                tempsglobal=round(np.sum(self.tp),2)
                self.FenetreGus.itemconfigure(tgp, text="Temps global de la production : \n "+str(tempsglobal)+" s.",fill='black', font=('Times',11,'bold'),justify='center')
                
                if temps>10:
                    self.FenetreGus.itemconfigure(tp,text="Temps de production moyen : \n"+str(temps)+" s.",fill='black',font=('Times',11,'bold'),justify='center')

                def infoAGV(p,event):               # Renvoi les infos d'un AGV lorsqu'on clique sur l'id de l'AGV
                    infoAGV=Tk()
                    infoAGV.title("Details agv n°"+str(p.getId()))
                    labelid=Label(infoAGV,text="Identifiant : "+str(p.getId()))
                    labelid.pack()
                    labeletat=Label(infoAGV,text="Etat : "+str(p.getEtat()))
                    labeletat.pack()
                    labeltype=Label(infoAGV,text="Type : "+str(p.getType()))
                    labeltype.pack()
                    labelmodif=Label(infoAGV,text="Liste de modifications reçues : ")
                    labelmodif.pack()
                    for i in p.modifs:
                        modifs=Label(infoAGV,text="      "+str(i))
                        modifs.pack()
                    button_frame=Frame(infoAGV)
                    button_frame.pack()
                    Button(infoAGV,text="Supprimer").pack()
                    Button(infoAGV,text="Fermer",command=infoAGV.destroy).pack()
                for p in self.pep:
                    if p.getTpsArret()==0:
                        self.FenetreGus.itemconfigure(textes[m],text="AGV n°"+str(p.id)+" : "+str(p.type)+" : "+str(p.etat),font=('Times',10))
                    if p.getTpsArret()!=0:
                        self.FenetreGus.itemconfigure(textes[m],text="AGV n°"+str(p.id)+" :  "+str(p.type)+" : "+str(p.etat)+" / Temps d'arret : "+str(round(p.getTpsArret(),2))+"s.",font=('Times',10))
                    self.FenetreGus.tag_bind("e"+str(m),"<ButtonPress-1>",partial(infoAGV,p))
                    m+=1
                for i in range(len(self.pep),portesmax):
                    self.FenetreGus.itemconfigure(textes[i],text="")

# Créé un temps de pause a une porte si un tag est detecté   
    def detectionTags(self,porte):
        r=7
        x,y=porte.getPosition()
        for p in porte.getPostes():
            pos=p.position            
            w,z=round(self.ligne.TagsPostes[pos-1][0]),round(self.ligne.TagsPostes[pos-1][1])
            if y==z and x<w+porte.getProp() and x>w-porte.getProp():
                if porte.type=='AV':
                    #Transmission.StockageDonnees("Arret de", p.tpscycleAV/porte.getProp(),"s")
                    #Transmission.EnvoiDonneeDirect(Transmission.Temps(),": Arret de ",p.tpscycleAV/porte.getProp(),"s")
                    Transmission.EnvoiDonneeDirect(porte.Temps(),porte.id,porte.type,"Porte à l arrêt",str(p.nom))
                    porte.tpsArret=p.tpscycleAV/porte.getProp()
                    print("Arret de ",p.tpscycleAV/porte.getProp(),"s")




                    p.etat=True
                    porte.changeEtat(str(p.nom))
                    print(str(p.nom))
                    porte.pos=[w,z]
                    self.FenetreValou.coords(self.ovales[porte.id-1],w-r,z-r,w+r,z+r)
                    time.sleep(p.tpscycleAV/porte.getProp())
                    porte.postes.remove(p)
                    porte.changeEtat("Sur la ligne")
                    #Transmission.StockageDonnees("La porte",porte.id,"est en mouvement")
                    Transmission.EnvoiDonneeDirect(porte.Temps(),porte.id,porte.type,"Porte en mouvement","")
                    p.etat=False
                    porte.ajoutModif(p.nom)
                if porte.type=='AR':
                    #Transmission.StockageDonnees("Arret de", p.tpscycleAR/porte.getProp(), "s")
                    #Transmission.EnvoiDonneeDirect(Transmission.Temps(),": Arret de ",p.tpscycleAR/porte.getProp(),"s")
                    Transmission.EnvoiDonneeDirect(porte.Temps(),porte.id,porte.type,"Porte à l arrêt",str(p.nom))
                    porte.tpsArret=p.tpscycleAR/porte.getProp()
                    print("Arret de ",p.tpscycleAR/porte.getProp(),"s")
                    p.etat=True
                    porte.changeEtat(str(p.nom))
                    porte.pos=[w,z]
                    self.FenetreValou.coords(self.ovales[porte.id-1],w-r,z-r,w+r,z+r)
                    time.sleep(p.tpscycleAR/porte.getProp())
                    porte.postes.remove(p)
                    porte.changeEtat("Sur la ligne")
                    #Transmission.StockageDonnees("La porte",porte.id,"est en mouvement")
                    Transmission.EnvoiDonneeDirect(porte.Temps(),porte.id,porte.type,"Porte en mouvement","")
                    p.etat=False
                    porte.ajoutModif(p.nom)
            porte.tpsArret=0
    
# Fonction qui lance la programmation manuelle
    def prog(self):
        programmation=Tk()
        programmation.title("Programmation manuelle")
        Label(programmation,text="Nombre de portes demandé : ").pack()
        Label(programmation,text="\n" ).pack()
        Label(programmation,text=("Combien de portière Avant ?")).pack()
        Av=Entry(programmation,width=20)
        Av.pack()
        Label(programmation,text="\n" ).pack()
        Label(programmation,text=("Combien de portière Arrière ?")).pack()
        Ar=Entry(programmation,width=20)
        Ar.pack()
        Label(programmation,text="\n" ).pack()
        Label(programmation,text="Dans quel ordre voulez vous produire les portières avants et arrières ?").pack()
        liste= Listbox(programmation,height=2,selectbackground="Grey",exportselection=False)
        liste.insert(1,"En quinconces")
        liste.insert(2,"Type apres type")
        liste.pack()
        def act():
            nbAV=int(Av.get())
            nbAR=int(Ar.get())
            productionAVAR=liste.get(ACTIVE)
            nbp=nbAV+nbAR
            heures=Tk()
            heures.title("Programmation manuelle")
            Label(heures,text="Temps total de la production souhaité : ").pack()
            frame=Frame(heures)
            frame.pack()
            Label(frame,text="Heures").pack(side=LEFT)
            Label(frame,text="Minutes").pack(side=LEFT)
            Label(frame,text="Secondes").pack(side=LEFT)
            entrees=Frame(heures)
            entrees.pack()
            he=Entry(entrees,width=10)
            mi=Entry(entrees,width=10)
            se=Entry(entrees,width=10)
            he.pack(side=LEFT)
            mi.pack(side=LEFT)
            se.pack(side=LEFT)
            (hh,mm,ss)=self.sec2hms(((nbAV+1)*self.tpsProdAV+nbAR*self.tpsProdAR)/self.nbAGV)
            Label(heures,text="Par default avec vitesse Standard : "+str(hh)+"h "+str(mm)+"min "+str(ss)+"s.").pack()
            def act2():
                #h=int(he.get())
                #m=int(mi.get())
                #s=int(se.get())
                h=int(hh)
                m=int(mm)
                s=int(ss)
                tpsdemande=self.hms2sec(h,m,s)
                tpsstandard=((nbAV+1)*self.tpsProdAV+nbAR*self.tpsProdAR)/self.nbAGV
                if tpsdemande<tpsstandard-self.tpsProdAV or tpsdemande>tpsstandard+self.tpsProdAV:     # Dans le cas ou le temps demandé est trop éloigné du temps par défault
                        print("Impossible avec le nombre d'AGV actuel")
                        if askyesno("Ajout AGV","Impossible avec le nombre d'AGV actuel \n \nVoulez vous ajouter un AGV a la ligne pour respecter le temps de production demandé ?" ) :
                            self.nbAGV=3
                            tpsstandard=((nbAV+1)*self.tpsProdAV+nbAR*self.tpsProdAR)/self.nbAGV
                            (h,m,s)=self.sec2hms(tpsstandard)
                            if askyesno("Lancement production","Voulez vraiment lancer la production de "+str(nbp)+" portes en {}h {}min {}sec ?".format(str(h),str(m),str(s))):
                                heures.attributes("-topmost",False)
                                programmation.attributes("-topmost",False)
                                heures.destroy()
                                programmation.destroy()
                                self.charger()
                                self.ido=0
                                self.pep=[]
                                self.ovales=[]
                                self.tp=[]
                                if productionAVAR=="Type apres type":
                                    tps1p=self.tpsProdAR/self.nbAGV
                                    for i in range(nbAR):
                                        self.ajouterPorte(tps1p,'AR')
                                    tps1p=self.tpsProdAV/self.nbAGV
                                    for i in range(nbAV):
                                        self.ajouterPorte(tps1p,'AV')
                                if productionAVAR=="En quiconce":
                                    if nbAV==nbAR:
                                        tps1p=tpsstandard/(nbp+1)
                                        for i in range(nbp):
                                            self.ajouterPorte(tps1p,'AV')
                                            self.ajouterPorte(tps1p,'AR')
                                    else:
                                        c=min(nbAV,nbAR)
                                        while c>0:
                                            c-=1
                                            tps1p=self.tpsProdAV/self.nbAGV
                                            self.ajouterPorte(tps1p,'AV')
                                            self.ajouterPorte(tps1p,'AR')
                                        if min(nbAV,nbAR)==nbAV:
                                            for i in range(nbp-nbAV):
                                                tps1p=self.tpsProdAR/self.nbAGV
                                                self.ajouterPorte(tps1p,'AR')
                                        else:
                                            for i in range(nbp-nbAR):
                                                tps1p=self.tpsProdAV/self.nbAGV
                                                self.ajouterPorte(tps1p,'AV')
                            else:heures.attributes("-topmost",True)
                        else:heures.attributes("-topmost",True)
                else:                                                                   # Si le temps demandé est proche du temps par default
                    h,m,s=self.sec2hms(tpsstandard)
                    if askyesno("Lancement production","Voulez vraiment lancer la production de "+str(nbp)+" portes en {}h {}min {}sec ?".format(str(h),str(m),str(s))):
                        heures.attributes("-topmost",False)
                        programmation.attributes("-topmost",False)
                        heures.destroy()
                        programmation.destroy()
                        self.charger()
                        self.ido=0
                        self.pep=[]
                        self.ovales=[]
                        self.tp=[]
                        if productionAVAR=="Type apres type":
                            tps1p=self.tpsProdAR/self.nbAGV
                            for i in range(nbAR): 
                                self.ajouterPorte(tps1p,'AR')
                            tps1p=self.tpsProdAV/self.nbAGV
                            for i in range(nbAV):
                                self.ajouterPorte(tps1p,'AV')
                        if productionAVAR=="En quiconce":
                            if nbAV==nbAR:
                                for i in range(nbp):
                                    tps1p=self.tpsProdAV/self.nbAGV
                                    self.ajouterPorte(tps1p,'AV')
                                    self.ajouterPorte(tps1p,'AR')
                            else:
                                c=min(nbAV,nbAR)
                                while c>0:
                                    c-=1
                                    tps1p=self.tpsProdAV/self.nbAGV
                                    self.ajouterPorte(tps1p,'AV')
                                    self.ajouterPorte(tps1p,'AR')
                                if min(nbAV,nbAR)==nbAV:
                                    for i in range(nbp-nbAV):
                                        tps1p=self.tpsProdAR/self.nbAGV
                                        self.ajouterPorte(tps1p,'AR')
                                else:
                                    for i in range(nbp-nbAR):
                                        tps1p=self.tpsProdAV/self.nbAGV
                                        self.ajouterPorte(tps1p,'AV')
                    else:heures.attributes("-topmost",True)
            button_frame=Frame(heures)
            button_frame.pack(side=BOTTOM)
            Button(button_frame,text="Selectionner",command=act2).grid(row=0,column=0)
            Button(button_frame,text="Retour",command=heures.destroy).grid(row=0,column=1)
        button_frame=Frame(programmation)
        button_frame.pack(side=BOTTOM)
        Button(button_frame,text="Selectionner",command=act).grid(row=0,column=0)
        Button(button_frame,text="Annuler",command=programmation.destroy).grid(row=0,column=1)

#Fonctions d'opérations diverses
    def hms2sec(self,hh,mm,ss):                    # Temps en heures,minutes,secondes converti en temps en secondes seulement
        return 3600*hh+60*mm+ss

    def sec2hms(self,ss):                           # Temps en secondes converti en heure, minutes, secondes
        (hh,ss)=divmod(ss,3600)
        (mm,ss)=divmod(ss,60)
        return (round(hh),round(mm),round(ss))
    
     
print("INITIALISATION IHM\n")

#LISTE DES VAR SELF:
# self.w,self.h             int; int Taille de la fenetre
# self.FenetreValou    Canvas
# self.FenetreGus                Canvas
# self.sas                  int position en hauteur du selecteur de fenetre
# self.edition              Boolean
# self.ligne                ligne de la classe Ligne 
# self.I,self.II,self.III,self.IV    coordonées [int,int] des points de changement de dir du tracé
# self.Tag                  liste [create_oval] des tags pour les Postes
# self.first                booleen pour les boucles, à remettre à True après la dernière utilisation
# self.ovales
# self.ido
# self.TagStart
# self.pep                  Tableaux avec toutes les portes en production
# self.portesFini           Nombre de portes terminé
# self.tp                   Liste des temps de production
# self.text
# self.btnPoste             liste de [Button] des postes
# self.vit_droit=1.2        multiplicateur de vitesse en ligne droite
# self.vit_virage=0.9       multiplicateur de vitesse en virage
# self.portesprodglob
# self.p
# self.nbAGV
# self.tpsProdAV
# self.tpsProdAR
# self.premiercoup

#ETAT D'AVANCEMENT
# init: ok              val
# cbDeTags: ok          val
# create_circle: ok     val
# ajouterPorte: ok      gus
# charger: ok           val
# info: ok              val
# ajouter: ok           val
# deplacement: ok       gus
# modifier: ok          val
# clear: ok             val
# suppr: ok             val
# posiDispo: ok         val
# affichage: ok         gus
# detectionTags: ok     gus

#COMMENTAIRES TECH
# pb radioboutton dans modifier: #La lecture de la valeur des radiobouttons se fait mal si les 2 fenetres ne sont pas init comme des classes différentes (l'interpréteur ne va chercher var que dans la 1ere instance de tk...)
# meme pb avec OptionMenu (les listes déroulantes)
# Tous les Getter créés dans les différentes classes ne servent pas à grand chose à part alourdir le code, en cas d'opti: tout suppr

#RECAP RÉU
# réu du 17/1:
# faire un espace/fenetre de supervision il pourrait y avoir les modifs en direct des portes, l'etat de la ligne et des postes

# réu du 2/2:
# Léa prévoit ajout de fonctionnalitées comme onglet de modif des vitesses, onglet de selection de scénarios

# réu du 12/2:
# préparation recette pour la prochaine réu: voir paragraphe dessous
# rapport: méthodo (agile, gestion projet, évolution du bordel), 5 chapitres: les sprints
# voir à créer des classes distinctes telles que une regroupe les infos, une crée les dessins, une qui regroupe les fonctions

# préparation réu de projet vendredi 18 pour la pré-recette:
# pré-recette: réuclient mais sans objectifs pour le prochain sprint, pré-recette pour vérifier ce qu'on s'apprette à rendre = attentes client
# diapo de fin de projet fonctionnel
# avoir un poster pret
# fiche de synthèse: fiche de présentation du projet: objectifs, méthodologie et résultats (à mettre dans le rapport, mais peu etre prise à part)

# Fin projet le Mardi 22 février 2022