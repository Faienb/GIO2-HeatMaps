# -*- coding: utf-8 -*-
"""
Created on Wed May 17 13:35:53 2023

@author: Bruno
"""
import zmq
import time
import numpy as np
import PIL
import pickle

ip="127.0.0.1"
hostname="ecg-rpi-02"
port_rec="5556"
port_send="5555"

# Requete de recepetion du serveru PULL
context = zmq.Context()
receiver = context.socket(zmq.PULL) # Création du socket en mode Publisher
receiver.bind("tcp://*:"+port_rec) # On accepte toutes les connexions sur le port 5556
# while True:
#     json_receiv=receiver.recv_pyobj()
#     print(json_receiv)
#     pass


# Requete d'envoi du serveur PUB
context = zmq.Context()
socket = context.socket(zmq.PUB) # Création du socket en mode Publisher
socket.bind("tcp://*:"+port_send) # On accepte toutes les connexions sur le port 5556
    
def random_array(size, scale):
        tuile_array = np.ones(shape=(size,size))
        for i in range(size):
            for j in range(size):
                tuile_array[i][j]=np.abs(np.round(np.random.normal(loc=0.0, scale=scale, size=None)))
        return tuile_array
request=0
while True:
# for request in range(10):
      # syntaxe : topic_name message
    dict_send =  {
        "z" : 1,
        "x" : 151616,
        "y": 15161,
        "task" : 1,
        "tuile_array1" : random_array(256,5),
        "tuile_array2" : random_array(256,5),
        "tuile_array3" : random_array(256,5),
        "tuile_array4" : random_array(256,5)
    }
    
    print(f"Sending request {request} …")
    socket.send_multipart([b"ecg-rpi-02", pickle.dumps(dict_send)])
    
    request+=1
    time.sleep(1)

