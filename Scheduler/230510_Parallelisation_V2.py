#Import des librairies
import numpy as np
import math
import os #Creation de dossiers
import threading
import zmq #Communication reseau via PUB SUB / PUSH PULL
import time
import pickle #Conversion bytes2utf-8
#Librairie de coloration syntaxique dans la console
from colorama import Fore,Style
from PIL import Image

#Initialisation de l'objet verrou
global lock
lock = threading.RLock()

#initialisation de la liste des jobs de premiere generation
global JobsFirstGen
global JobsSecondGen
global TaskCompleted

#Creation du contexte zmq pour le publisher
SendContext = zmq.Context()
#Creation du socket
socket = SendContext.socket(zmq.PUB) # Création du socket en mode Publisher
socket.bind("tcp://*:5556") # On accepte toutes les connexions sur le port 5556


#Creation du dictionnaire des clients
global RPIs
# RPIs = {"ecg-rpi-01":{"ip":"192.168.16.17",
#                    "hostname":"ecg-rpi-01",
#                       "port_rec":5556,
#                       "port_send":5560,
#                       "status":True,
#                       "byteName":b'topica'},
#         "ecg-rpi-06":{"ip":"192.168.16.18",
#                    "hostname":"ecg-rpi-06",
#                       "port_rec":5556,
#                       "port_send":5561,
#                       "status":True,
#                       "byteName":b'topicb'},
#         "ecg-rpi-03":{"ip":"192.168.16.19",
#                    "hostname":"ecg-rpi-03",
#                       "port_rec":5556,
#                       "port_send":5562,
#                       "status":True,
#                       "byteName":b'topicc'},
#         "ecg-rpi-04":{"ip":"192.168.16.20",
#                    "hostname":"ecg-rpi-04",
#                       "port_rec":5556,
#                       "port_send":5563,
#                       "status":True,
#                       "byteName":b'topicd'}}

RPIs = {"laptop_Elisa1":{"ip":"192.168.16.17",
                   "hostname":"laptop_Elisa1",
                      "port_rec":5556,
                      "port_send":5560,
                      "status":True,
                      "byteName":b'topicaa'},
        "laptop_Elisa2":{"ip":"192.168.16.17",
                           "hostname":"laptop_Elisa2",
                              "port_rec":5556,
                              "port_send":5561,
                              "status":True,
                              "byteName":b'topicab'},
        "laptop_Elisa3":{"ip":"192.168.16.17",
                           "hostname":"laptop_Elisa3",
                              "port_rec":5556,
                              "port_send":5562,
                              "status":True,
                              "byteName":b'topicac'},
        "laptop_Bruno1":{"ip":"192.168.16.18",
                   "hostname":"laptop_Bruno1",
                      "port_rec":5556,
                      "port_send":5570,
                      "status":True,
                      "byteName":b'topicba'},
        "laptop_Bruno2":{"ip":"192.168.16.18",
                   "hostname":"laptop_Bruno2",
                      "port_rec":5556,
                      "port_send":5571,
                      "status":True,
                      "byteName":b'topicbb'},
        "laptop_Bruno3":{"ip":"192.168.16.18",
                   "hostname":"laptop_Bruno3",
                      "port_rec":5556,
                      "port_send":5572,
                      "status":True,
                      "byteName":b'topicbc'}}

def generate_color_rgba_from_nbre(nb, fact, type_color):
    """
    

    Parameters
    ----------
    nb : int
        nombre à transformer en RGBA
    fact : int
        facteur pour rgb maximum et pas de transparence.
    type_color : string
        "r" : red / "g" = green / "b" : bleu / "w": white.

    Returns
    -------
    list
        [r,g,b,a]

    """
    # initialisation RGBA
    r=0
    g=0
    b=0
    a=0
    col_haut=255
    col_bas=0
    if type_color=="r" or type_color=="g" or type_color=="b":
        col_haut=100
        col_bas=255
    
    # Longeur de la couleur d'échelle
    l_col=abs(col_haut-col_bas)
    
    degre=2
    mult_c=l_col/(fact**degre)
    mult_deg=255/(fact**degre)
    mult_log=255/np.log2(fact+1)
    mult_lin=255/fact
    
    
    color=mult_c*nb**degre
    
    # transparence selon log
    # a=mult_log*np.log2(nb+1)
    
    # Transparence selon degré
    a=mult_deg*nb**degre
    
    # Transparence selon linéaire
    # a=mult_lin*nb
    
    if color>l_col:
        color=l_col
    if a>255:
        a=255
    
    if type_color=="r":
        r=col_bas-color
    elif type_color=="g":
        g=col_bas-color
    elif type_color=="b":
        b=col_bas-color
    else:
        r=color
        g=color
        b=color
    
    return [r,g,b,a]

def create_image_from_array(array, color):
    """
    

    Parameters
    ----------
    array : np.array
        array 256x256 contenant le nbre de passage.
    color : string
        "r" : red / "g" = green / "b" : bleu / "w": white

    Returns
    -------
    image_create : img
        image RGBA.
    color_image : array RGBA (256x256x4)
        valeur int des RGBA dans un array.

    """
    color_image = np.zeros(shape=(256,256,4), dtype="uint8")
    
    # calcul du facteur de la couleur maximum
    mean = np.mean(array)
    maxi = 1
    

    for i in range(array.shape[0]) :
        for j in range(array.shape[1]):
            color_rgba=generate_color_rgba_from_nbre(array[i][j],maxi, color)
            
            
            color_image[i][j][0]=color_rgba[0]
            color_image[i][j][1]=color_rgba[1]
            color_image[i][j][2]=color_rgba[2]
            color_image[i][j][3]=color_rgba[3]
            
            
    image_create = Image.fromarray(color_image)
    return image_create, color_image



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
            task = msgReceived["task"]
            X = msgReceived["X"]
            Y = msgReceived["Y"]
            Z = msgReceived["Z"]
            key = msgReceived["key"]
            #Il va falloir y mettre un lock pour l'update des deux dicos cas ou deux taches finissent en meme temps
            with lock :
                print(Fore.RED + Style.BRIGHT + "X={:d}, Y={:d} receive from RPI {:s}".format(X,Y,self.hostName) + Fore.RESET)
                Rasterdata = msgReceived["data"]
                JobsFirstGen[key]["data"] = Rasterdata
                JobsFirstGen[key]["status"] = True
                JobsFirstGen[key]["completion"] = True
                RPIs[self.hostName]["status"] = True
                    
                #Ecriture des images
                img, array = create_image_from_array(Rasterdata, "r")
                if not os.path.exists(ParentFolder+str(Z)+"/"+str(X)):
                    os.mkdir(ParentFolder+str(Z)+"/"+str(X))
                img.save(ParentFolder + str(Z) + "/" + str(X) + "/" + str(Y) + ".PNG" )
            
            
#Iteration sur les clients pour creer un objet PULL dans la donnee de chaque ligne
for key,data in RPIs.items():
    data.update({"PullObject":RPI(data)})

#Declaration des parametres de base du calcul
#Niveau maximal de zoom
global Zmax
Zmax = 18
global Zmin
Zmin = 14
#Chemin relatif du dossier des tuiles en fonction de l'emplacement du script python
global ParentFolder
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


# Calcul sur Chamonix
LatMinDeg = 45.713
LonMinDeg =  4.82
LatMaxDeg = 45.7267
LonMaxDeg = 4.844

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
            JobsFirstGen.update({JobId:{"Z":Zmax,"X":i,"Y":j,"task":0,"status":False,"completion":False,"data":False,"key":JobId}})
            JobId += 1
    return JobsFirstGen         
#Fonction d'envoi des données de bounding box aux RPI's
#Status in JobsFirsGen :
    #if False : a faire
    #if True : en cours ou termine
def threadSendRPIs1():
    with lock :
        print(Fore.GREEN + Style.BRIGHT + "Starting Task 1" + Fore.RESET)
        print(Fore.GREEN + Style.BRIGHT + "Sending data for computation of the minimum level tiles" + Fore.RESET)
    print(Fore.GREEN + Style.BRIGHT + "Initializing socket" + Fore.RESET)
    time.sleep(2.0)
    CheckSendingForBreak = True
    TaskCompleted = False
    while not TaskCompleted :
        CheckSendingForBreak = True
        for key in RPIs.keys():
            if CheckSendingForBreak :
                if RPIs[key]["status"] :
                    with lock :
                        print(Fore.GREEN + Style.BRIGHT + "{:s} is free".format(RPIs[key]["hostname"]) + Fore.RESET)
                    counterTasks = 0
                    for key2 in JobsFirstGen.keys():
                        if not JobsFirstGen[key2]["status"] :
                            with lock :
                                print(Fore.GREEN + Style.BRIGHT + "Sending task : id={:d} X={:d}, Y={:d}".format(key2,JobsFirstGen[key2]["X"],JobsFirstGen[key2]["Y"]) + Fore.RESET)
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
                                break

            #Ce break la s'opere si une tache a ete envoyee
            #Pour que la boucle de controle des RPI reparte a zero a chaque envoi de tache
            else :
                break
                        
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
            statTask1 = True
            #Interruption de toutes les requetes Pull sur les RPIs
            for key,data in RPIs.items():
                data["PullObject"].cont = False
        with lock :
            print(Fore.MAGENTA + Style.BRIGHT + "Going to sleep for 1 seconds" + Fore.RESET)
        time.sleep(1.0)
    with lock :
        print(Fore.MAGENTA + Style.BRIGHT + "Control of task 1 finished, all tasks completed" + Fore.RESET)
    
    


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

#Creation des dossiers des tuiles
for i in range(Zmin,Zmax+1):
    createZoomLevelFolders(ParentFolder, i)

RPIsThreads = []

for key,data in RPIs.items():
    data["PullObject"].createPullContext()
    RPIsThreads.append(threading.Thread(target=data["PullObject"].listenForPullRequests))
    
#Creation des threads Pull RPIs
for i in RPIsThreads :
    i.start()

#Fonction générale du Scheduler tuilage
for i in range(Zmax,Zmin,-1):
    JobsFirstGen = {}
    JobsFirstGen = generateXYforZ(LatMinDeg, LonMinDeg, LatMaxDeg, LonMaxDeg, i)
    print(len(JobsFirstGen))

    #Processus complet
    #Start des thread sending et receiving
    thread1 = threading.Thread(target=threadSendRPIs1)
    thread1.start()
    thread2 = threading.Thread(target=threadControlTask1)
    thread2.start()
    
    cont = False
    while not cont :
        findNotFinishedTask = True
        for key,data in JobsFirstGen.items():
            if not data['completion'] :
                findNotFinishedTask = False
                break
        if findNotFinishedTask :
            cont = True
    thread1.join()
    thread2.join()
            


     
 





        
