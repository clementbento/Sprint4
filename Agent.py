from threading import Thread
import time

class Agent(Thread):
    '''
    classdocs
    '''

    def __init__(self):  #Constructeur
        '''
        Constructor
        '''
        self.active = True
        Thread.__init__(self)   # Lance automatiquement la fonction run
        
    def terminate(self):        # Fonction qui mets fin au Thread
        self.active = False
        
    def run(self):              # Tant que le Thread est actif alors la fonction tourne.
        while(self.active):
            time.sleep(0.5)
        print("Fin")