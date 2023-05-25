# -*- coding: utf-8 -*-
"""
Created on Wed May 17 13:35:53 2023

@author: Bruno
"""
import zmq
import time
import numpy as np
import PIL
ip="127.0.0.1"
hostname="ecg-rpi-02"
port_rec="5556"
port_send="5555"

context = zmq.Context()
socket = context.socket(zmq.REQ) # Création du socket en mode Publisher
socket.connect ("tcp://10.192.91.138:5555") # On accepte toutes les connexions sur le port 5555

def random_array(size, scale):
        tuile_array = np.ones(shape=(size,size))
        for i in range(size):
            for j in range(size):
                tuile_array[i][j]=np.abs(np.round(np.random.normal(loc=0.0, scale=scale, size=None)))
        return tuile_array

# while True:
for request in range(10):
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
    socket.send_pyobj(dict_send)
    
    message = socket.recv_pyobj()
    print(f"Received reply {request} [ {message} ]")
    
    time.sleep(1)

