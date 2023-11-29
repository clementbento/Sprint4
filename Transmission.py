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

import socket
import json

Stockage = []

def StockageDonnees(a, b, c):
    Stockage.append(a)
    Stockage.append(b)
    Stockage.append(c)
    print("-----",a,b,c)



def EnvoiDonneeDirect(t,id,type,action,poste):
    # Créez un socket client TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connectez-vous à un serveur distant
    server_address = ('localhost', 8080)
    client_socket.connect(server_address)
    message = []
    message.append(t)
    message.append(id)
    message.append(type)
    message.append(action)
    message.append(poste)
    #Serialisation du message en json
    messageJson = json.dumps(message)

    # Envoyez des données au serveur
    client_socket.send(messageJson.encode())

    # Fermez les sockets client et serveur
    client_socket.close()



    


    
