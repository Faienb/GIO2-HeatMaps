import zmq
import time
import pickle
import threading
from numpy import array, zeros
from bruno import fusion_tuile_bruno
import webget as webget
import math

IPscheduler = "10.192.91.197"
RPIs = {"laptop_Elisa":{"ip":"192.168.16.17",
                   "hostname":"laptop-Elisa",
                      "port_rec":5556,
                      "port_send":5560,
                      "status":True,
                      "byteName":b'topica'},
        "laptop_Bruno":{"ip":"192.168.16.18",
                   "hostname":"laptop_Bruno",
                      "port_rec":5556,
                      "port_send":5561,
                      "status":True,
                      "byteName":b'topicb'}}

def num2deg(x_tile, y_tile, zoom):
    """
    return the NW-corner of the tile, Use x_tile+1, y_tile+1 to get the other corners
    """
    n = 2.0 ** zoom
    lon_deg = x_tile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg

# FONCTION DE CREATION DES TUILES 
def tuile_create_elisa(json_recv):
    print("tuile créée")
    element_send = {
        "Z" : json_recv['Z'],
        "X" : json_recv['X'],
        "Y": json_recv['Y'],
        "status" : json_recv['status'],
        "completion" : json_recv['completion'],
        "task" : 0,
        "tuile_array" : [
            ]
    }

    bbox_lat_max, bbox_lon_min = num2deg(element_send['X'],element_send['Y'],17)
    bbox_lat_min, bbox_lon_max = num2deg(element_send['X']+1,element_send['Y']+1,17)

    options = {'utagawavtt':'t',
           'tracegps':'t',
           'openstreetmap':'t',
           'bikingspots':'t',
           'camptocamp':'',
           'openrunner':''}

    raster_array = webget.task_get_array_from_bbox(bbox_lon_min,bbox_lat_min,bbox_lon_max,bbox_lat_max,options)

    element_send["data"] = raster_array

    return element_send

def Subscribe():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    ip = "tcp://{:s}:{:d}".format(IPscheduler,RPIs["laptop_Elisa"]["port_rec"])
    socket.connect(ip)
    # socket.subscribe("ecg-rpi-01")
    socket.subscribe("topica")

    context2 = zmq.Context()
    sender2 = context2.socket(zmq.PUSH) # Création du socket en mode Push
    sender2.connect("tcp://{:s}:{:d}".format(IPscheduler,RPIs["laptop_Elisa"]["port_send"])) # changer ici localhost pour l'IP de votre machine

    t0 = time.time()
    cont = True
    while cont :
        print("Hello")
        [topic,msg] = socket.recv_multipart()
        msg2 = pickle.loads(msg)
        task = msg2["task"]
        if task == 0 :
            msg2 = tuile_create_elisa(msg2)
        else :
            tile = fusion_tuile_bruno(msg2)
            msg2["tuile_array"] = tile

        time.sleep(1.0)
        # Connexion au serveur
        sender2.send_pyobj(msg2)

#Start des thread sending et receiving
thread1 = threading.Thread(target=Subscribe)
thread1.start()