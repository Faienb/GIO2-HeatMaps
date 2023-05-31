# -*- coding: utf-8 -*-
"""
Created on Wed May 17 13:19:49 2023

@author: Bruno
"""
import zmq
import numpy as np
import skimage
import pickle
import socket
myip=socket.gethostbyname(socket.gethostname())
myhostname=socket.gethostname()
ipserveur="127.0.0.1"
port_rec="5555"
port_send="5556"
# Création des sockets de réception (SUBSCRIBE)
# =======================================================================================

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://"+ipserveur+":"+port_rec)
socket.subscribe(myhostname)

# ENVOI DES INFORMATIONS DE LA MACHINE (PUSH)
# =======================================================================================
# context = zmq.Context()
# sender = context.socket(zmq.PUSH) # Création du socket en mode Push
# # # Connexion au serveur
# sender.connect("tcp://"+ipserveur+":"+port_send) # changer ici localhost pour l'IP de votre machine

# # # Envoyer l'adresse IP du rapsberry ou hostname
# sender.send_pyobj(({"IP": "salut", "Hostname": "hostname"}))





# Création d'un fonction qui envoie l'adresse IP et le HOSTNAME au serveur
# ========================================================================





# FONCTION DE CREATION DES TUILES 
def tuile_create_elisa():
    print("tuile créée")
    element_send = {
        "z" : 1,
        "x" : 151616,
        "y": 15161,
        "task" : 0,
        "host" : myhostname,
        "ip" : myip,
        "tuile_array" : [
            [0,1,2,3],
            [1,2,3,4],
            [1,2,3,4],
            [1,2,3,4]
            ]
    }
    return element_send


# FONCTION DE CREATION DES TUILES 
def fusion_tuile_bruno(json_recv):
    element_send = {
        "z" : json_recv['z'],
        "x" : json_recv['x'],
        "y": json_recv['y'],
        "task" : json_recv['task'],
        "host" : myhostname,
        "ip" : myip,
        "tuile_array" : [
            ]
    }
    
    ar1=np.concatenate((json_recv['tuile_array1'], json_recv['tuile_array2']), axis=1)
    ar2=np.concatenate((json_recv['tuile_array3'], json_recv['tuile_array4']), axis=1)
    array_fus=np.concatenate((ar1, ar2), axis=0)
    
    # Création d'une somme de array
    array_reduced = skimage.measure.block_reduce(array_fus, (2,2), np.sum)
    # Enregistrement du array dans le dictionnaire de livraison
    element_send["tuile_array"]=array_reduced
    
    return element_send




while True:
    # Réception des éléments de fabien
    [topic, msg]=socket.recv_multipart()

    json_recv = pickle.loads(msg)
    if json_recv["task"]==0:
        element_send=tuile_create_elisa(json_recv)
        # socket.send_json(element_send) #transmission de donnée json
    elif json_recv["task"]==1:
        element_send=fusion_tuile_bruno(json_recv)
        print(element_send)
        # socket.send_pyobj(element_send) #transmission de donnée json
    
    
