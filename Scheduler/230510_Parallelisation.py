#Import des librairies
from numpy import array
import math
import os
import threading
import zmq
import time
import pickle

#Lien pour le cote subscriber du publish du premier thread
#https://stackoverflow.com/questions/33159395/how-to-add-topic-filters-when-calling-recv-pyobj-in-zeromq

#==========
#Temporaire
#==========

#Creation du dictionnaire des clients
global RPIs
RPIs = {"ecg-rpi-01":{"ip":"192.168.16.17",
                   "hostname":"ecg-rpi-01",
                      "port_rec":5556,
                      "port_send":5560,
                      "status":True,
                      "byteName":b'topica'},
        "ecg-rpi-02":{"ip":"192.168.16.18",
                   "hostname":"ecg-rpi-02",
                      "port_rec":5556,
                      "port_send":5561,
                      "status":True,
                      "byteName":b'topicb'},
        "ecg-rpi-03":{"ip":"192.168.16.19",
                   "hostname":"ecg-rpi-03",
                      "port_rec":5556,
                      "port_send":5562,
                      "status":True,
                      "byteName":b'topicc'},
        "ecg-rpi-04":{"ip":"192.168.16.20",
                   "hostname":"ecg-rpi-04",
                      "port_rec":5556,
                      "port_send":5563,
                      "status":True,
                      "byteName":b'topicd'}}

#Niveau maximal de zoom
Zmax = 18
#Declaration des parametres de base du calcul
ParentFolder = "../Tuiles/"
#Calcul sur toute la suisse
LatMinDeg = 45.80000
LonMinDeg =  5.80000
LatMaxDeg = 47.85000
LonMaxDeg = 10.60000

#Calcul sur le Valais central 
LatMinDeg = 45.90386
LonMinDeg =  7.11991
LatMaxDeg = 46.39470
LonMaxDeg = 7.49827

#Fonction pour calculer dpeuis une latitude et une longitude le numero X et Y de la tuile
#C'est un standard OGC
#Il depend du niveau de zoom car plus on zoom plus on a de tuiles sur l'entier de la suisse
def deg2num(lat_deg, lon_deg, zoom):
    """
    return the tile containing the point (lat_deg, lon_deg)
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x_tile = int((lon_deg + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return x_tile, y_tile

def num2deg(x_tile, y_tile, zoom):
    """
    return the NW-corner of the tile, Use x_tile+1, y_tile+1 to get the other corners
    """
    n = 2.0 ** zoom
    lon_deg = x_tile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg

#Fonction de calcul de toutes les coordonnées de la bounding box de la Suisse et creation de la liste de job
#X sens longitude
#Y sens latitude
def generateXYforZ(LatMinDeg, LonMinDeg, LatMaxDeg, LonMaxDeg, Zmax) :
    TuileXY_Zmax = []
    JobsFirstGen = {}
    Xmin,Ymax = deg2num(LatMinDeg, LonMinDeg, Zmax)
    Xmax,Ymin = deg2num(LatMaxDeg, LonMaxDeg, Zmax)
    JobId = 1
    for i in range(Xmin,Xmax+1):
        for j in range(Ymin,Ymax+1):
            TuileXY_Zmax.append([i,j])
            #Le status nous indique si False que la tache n'est pas faite
            JobsFirstGen.update({JobId:{"Z":1,"X":i,"Y":j,"task":str(JobId),"status":False,"data":False}})
            JobId += 1
    return TuileXY_Zmax,JobsFirstGen
    
    
#Liste des jobs de la premiere generation de travaux
global JobsFirstGen
TuileXY_Zmax, JobsFirstGen = generateXYforZ(LatMinDeg, LonMinDeg, LatMaxDeg, LonMaxDeg, Zmax)

#Fonction d'envoi des données de bounding box aux RPI's
#Status in JobsFirsGen :
    #if False : a faire
    #if True : en cours ou termine
def threadSendRPIs():
    print("Starting Task 1")
    print("Sending data for computation of the minimum level tiles")
    #Creation du contexte zmq pour le publisher
    SendContext = zmq.Context()
    #Creation du socket
    socket = SendContext.socket(zmq.PUB) # Création du socket en mode Publisher
    socket.bind("tcp://*:5556") # On accepte toutes les connexions sur le port 5556

    CheckSendingForBreak = True
    TaskCompleted = False
    counterTasks = 0
    while not TaskCompleted :
        CheckSendingForBreak = True
        for key in RPIs.keys():
            if CheckSendingForBreak :
                if RPIs[key]["status"] :
                    print("{:s} is free".format(RPIs[key]["hostname"]))
                    for key2 in JobsFirstGen.keys():
                        if not JobsFirstGen[key2]["status"] :
                            print("Sending task : id={:s} X={:d}, Y={:d}".format(JobsFirstGen[key2]["task"],JobsFirstGen[key2]["X"],JobsFirstGen[key2]["Y"]))
                            #Envoi de la tache
                            '''
                            Regler le probleme du topic proprement
                            Integrer des controles de la bonne recepetion de la task
                            '''
                            topic = RPIs[key]["byteName"]
                            topic = b'topica'
                            socket.send_multipart([topic,pickle.dumps(JobsFirstGen[key2])])
                            #Changement de statut du RPI
                            RPIs[key]["status"] = False
                            #Changement de statut de la tache envoyee
                            JobsFirstGen[key2]["status"] = True
                            CheckSendingForBreak = False
                            break
                        #Compteur a chaque iteration de recherche de tache
                        #Pous savoir si toutes les taches ont ete faites
                        else :
                            counterTasks += 1
                            if counterTasks == len(JobsFirstGen):
                                print("All tasks of generation 1 are sent or done !")
                                TaskCompleted = True

            #Ce break la s'opere si une tache a ete envoyee
            #Pour que la boucle de controle des RPI reparte a zero a chaque envoi de tache
            else :
                break
                        
        time.sleep(2.0)
    print("All tasks of generation 1 are sent or done !")
    print("Waiting for thread 2 to retrieve all tasks")
    
threadSendRPIs()
        
# def threadGetBackFromRPIs():
    

#Fonction de récupération des Heatmap Raster

#Fonction d'envoi des 4 heatmap pour le tuilage

#Fonction de réception des tuiles

#Fonction de gestion des niveaux de zoom pour l'envoi et la réception des heatmap (tuilage)

#Fonction de stockage des ZXY tuilées
def createZoomLevelFolders(ParentFolder, Z):
    if not os.path.exists(ParentFolder+str(Z)):
        os.mkdir(ParentFolder+str(Z))
        print("Zoom folder {:d} created".format(Z))
    else : 
        print("Zoom folder {:d} already exists".format(Z))
            
for i in range(8,Zmax+1):
    createZoomLevelFolders(ParentFolder, i)

#Fonction générale du Scheduler Bounding Box

#Fonction générale du Scheduler tuilage

#Processus complet


#Schema
#Creation de la liste de job
#envoi bbox lat lon min lat lon max
#Reception array 256x256
#Envoi 4 array + bbox
#Reception 1 array +bbox
#Sequencage par niveau de zoom
