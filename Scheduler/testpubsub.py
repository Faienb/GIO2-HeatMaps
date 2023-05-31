import zmq
import time
import pickle
import threading
from numpy import array, zeros

IPscheduler = "10.191.6.34"

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

def Subscribe():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    ip = "tcp://{:s}:{:d}".format(IPscheduler,RPIs["ecg-rpi-01"]["port_rec"])
    socket.connect(ip)
    # socket.subscribe("ecg-rpi-01")
    socket.subscribe("topica")
    
    context2 = zmq.Context()
    sender2 = context2.socket(zmq.PUSH) # Création du socket en mode Push
    sender2.connect("tcp://10.191.6.34:{:d}".format(RPIs["ecg-rpi-01"]["port_send"])) # changer ici localhost pour l'IP de votre machine

    t0 = time.time()
    cont = True
    while cont :
        [topic,msg] = socket.recv_multipart()
        msg2 = pickle.loads(msg)
        msg2["data"] = zeros(shape=(255,255))
        print(msg2)
        time.sleep(5.0)
        # Connexion au serveur
        sender2.send_pyobj(msg2)

#Start des thread sending et receiving
thread1 = threading.Thread(target=Subscribe)
thread1.start()