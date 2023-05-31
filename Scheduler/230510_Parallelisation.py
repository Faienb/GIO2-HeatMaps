#Import des librairies
from numpy import array
import math
import os #Creation de dossiers
import threading
import zmq #Communication reseau via PUB SUB / PUSH PULL
import time
import pickle #Conversion bytes2utf-8
#Librairie de coloration syntaxique dans la console
from colorama import Fore,Style

#Initialisation de l'objet verrou
global lock
lock = threading.RLock()

#initialisation de la liste des jobs de premiere generation
global JobsFirstGen
global TaskCompleted


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

#Creation de la classe des RPIs
#Initialisation de la classe RPI
class RPI():
    def __init__(self, RPIline) :
        self.cont = True
        self.hostName = RPIline["hostname"]
        self.ip = RPIline["ip"]
        self.port_rec = RPIline["port_rec"]
        self.port_send = RPIline["port_send"]
        self.status = RPIline["status"]
        self.byteName = RPIline["byteName"]
    def createPullContext(self):
        self.contextRPI = zmq.Context()
        self.receiverRPI = self.contextRPI.socket(zmq.PULL) # Création du socket en mode Pull
        self.receiverRPI.bind("tcp://*:{:d}".format(self.port_send)) # Choix du port
    def listenForPullRequests(self):
        with lock :
            print(Fore.RED + Style.BRIGHT + "Waiting for processed data of task 1 from RPI {:s}".format(self.hostName) + Fore.RESET)
        #lorsque toutes les taches sont terminees on vient update en dehors le cont pour interrompre la boucle
        while self.cont :
            with lock :
                print(Fore.RED + Style.BRIGHT + "Waiting for computed Raster of RPI {:s}".format(self.hostName) + Fore.RESET)
            #A definir ce qu'il y a dans le multipart
            msg = self.receiverRPI.recv_pyobj()
            msgReceived = msg
            #Recuperation de la tuile Raster
            Rasterdata = msgReceived["data"]
            taskId = msgReceived["task"]
            X = msgReceived["X"]
            Y = msgReceived["Y"]
            #Il va falloir y mettre un lock pour l'update des deux dicos cas ou deux taches finissent en meme temps
            with lock :
                print(Fore.RED + Style.BRIGHT + "Task id={:s} X={:d}, Y={:d} receive from RPI {:s}".format(taskId,X,Y,self.hostName) + Fore.RESET)
                JobsFirstGen["data"] = Rasterdata
                #update du statut de la tuile
                #Peut etre y ajouter un controle ici avant
                #Si tuile pas correct remettre le status en False
                JobsFirstGen["status"] = True
                JobsFirstGen["completion"] = True
                RPIs[self.hostName]["status"] = True
            
            
#Iteration sur les clients pour creer un objet PULL dans la donnee de chaque ligne
for key,data in RPIs.items():
    data.update({"PullObject":RPI(data)})

#Declaration des parametres de base du calcul
#Niveau maximal de zoom
Zmax = 17
#Chemin relatif du dossier des tuiles en fonction de l'emplacement du script python
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

#Calcul sur le Valais central 
LatMinDeg = 45.90386
LonMinDeg =  7.11991
LatMaxDeg = 46.000
LonMaxDeg = 7.21

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
            JobsFirstGen.update({JobId:{"Z":1,"X":i,"Y":j,"task":str(JobId),"status":False,"completion":False,"data":False}})
            JobId += 1
    return TuileXY_Zmax,JobsFirstGen

#Liste des jobs de la premiere generation de travaux
TuileXY_Zmax, JobsFirstGen = generateXYforZ(LatMinDeg, LonMinDeg, LatMaxDeg, LonMaxDeg, Zmax)

#Fonction d'envoi des données de bounding box aux RPI's
#Status in JobsFirsGen :
    #if False : a faire
    #if True : en cours ou termine
def threadSendRPIs():
    with lock :
        print(Fore.GREEN + Style.BRIGHT + "Starting Task 1" + Fore.RESET)
        print(Fore.GREEN + Style.BRIGHT + "Sending data for computation of the minimum level tiles" + Fore.RESET)
    #Creation du contexte zmq pour le publisher
    SendContext = zmq.Context()
    #Creation du socket
    socket = SendContext.socket(zmq.PUB) # Création du socket en mode Publisher
    socket.bind("tcp://*:5556") # On accepte toutes les connexions sur le port 5556
    print(Fore.GREEN + Style.BRIGHT + "Initializing socket" + Fore.RESET)
    time.sleep(2.0)
    CheckSendingForBreak = True
    TaskCompleted = False
    counterTasks = 0
    while not TaskCompleted :
        CheckSendingForBreak = True
        for key in RPIs.keys():
            if CheckSendingForBreak :
                if RPIs[key]["status"] :
                    with lock :
                        print(Fore.GREEN + Style.BRIGHT + "{:s} is free".format(RPIs[key]["hostname"]) + Fore.RESET)
                    for key2 in JobsFirstGen.keys():
                        if not JobsFirstGen[key2]["status"] :
                            with lock :
                                print(Fore.GREEN + Style.BRIGHT + "Sending task : id={:s} X={:d}, Y={:d}".format(JobsFirstGen[key2]["task"],JobsFirstGen[key2]["X"],JobsFirstGen[key2]["Y"]) + Fore.RESET)
                            #Envoi de la tache
                            topic = RPIs[key]["byteName"]
                            socket.send_multipart([topic,pickle.dumps(JobsFirstGen[key2])])
                            with lock :
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
                                with lock :
                                    print(Fore.GREEN + Style.BRIGHT + "All tasks of generation 1 are sent or done !" + Fore.RESET)
                                TaskCompleted = True

            #Ce break la s'opere si une tache a ete envoyee
            #Pour que la boucle de controle des RPI reparte a zero a chaque envoi de tache
            else :
                break
                        
        time.sleep(0.2)
    with lock :
        print(Fore.GREEN + Style.BRIGHT + "All tasks of generation 1 are sent or done !" + Fore.RESET)
        print(Fore.GREEN + Style.BRIGHT + "Waiting for thread 2 to retrieve all tasks" + Fore.RESET)
        print(Fore.GREEN + Style.BRIGHT + "Closing publish context" + Fore.RESET)
        

#Fonction de controle de la recuperation des heatmap Raster
def threadControlTask1():
    statusTask1 = False
    with lock :
        print(Fore.MAGENTA + Style.BRIGHT + "Starting to control Task 1 reception" + Fore.RESET)
    while not statusTask1 :
        findNotFinishedTask = True
        for key,data in JobsFirstGen.items():
            if not data['completion'] :
                findNotFinishedTask = False
                break
        
        if not findNotFinishedTask :
            with lock :
                print(Fore.MAGENTA + Style.BRIGHT + "Process still pending" + Fore.RESET)
        else :
            with lock :
                print(Fore.MAGENTA + Style.BRIGHT + "All tasks are finished, closing process 1" + Fore.RESET)
            statusTask1 = True
            #Interruption de toutes les requetes Pull sur les RPIs
            for key,data in RPIs.items():
                data["PullObject"].cont = False
        with lock :
            print(Fore.MAGENTA + Style.BRIGHT + "Going to sleep for 5 seconds" + Fore.RESET)
        time.sleep(1.0)
    with lock :
        print(Fore.MAGENTA + Style.BRIGHT + "Control of task 1 finished, all tasks completed" + Fore.RESET)

#Fonction de generation des taches pour le tuilage
def generateTasksForTiling():
    pass

#Fonction d'envoi des 4 heatmap pour le tuilage

#Fonction de réception des tuiles

#Fonction de gestion des niveaux de zoom pour l'envoi et la réception des heatmap (tuilage)

#Fonction de stockage des ZXY tuilées
def createZoomLevelFolders(ParentFolder, Z):
    if not os.path.exists(ParentFolder+str(Z)):
        os.mkdir(ParentFolder+str(Z))
        with lock :
            print(Fore.CYAN + Style.BRIGHT + "Zoom folder {:d} created".format(Z) + Fore.RESET)
    else :
        with lock :
            print(Fore.CYAN + Style.BRIGHT + "Zoom folder {:d} already exists".format(Z) + Fore.RESET)


#Fonction générale du Scheduler tuilage

#Processus complet
#Start des thread sending et receiving
thread1 = threading.Thread(target=threadSendRPIs)
thread1.start()
thread2 = threading.Thread(target=threadControlTask1)
thread2.start()

RPIsThreads = []

for key,data in RPIs.items():
    data["PullObject"].createPullContext()
    RPIsThreads.append(threading.Thread(target=data["PullObject"].listenForPullRequests))
 
#Creation des threads Pull RPIs
for i in RPIsThreads :
    i.start()    

#Creation des dossiers des tuiles
for i in range(8,Zmax+1):
    createZoomLevelFolders(ParentFolder, i)
