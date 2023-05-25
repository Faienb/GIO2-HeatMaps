import zmq
import time
import pickle
import threading

def Subscribe():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    
    socket.connect("tcp://10.128.25.98:5556")
    # socket.subscribe("ecg-rpi-01")
    socket.subscribe("topica")
    t0 = time.time()
    cont = True
    while cont :
        print("Hello")
        [topic,msg] = socket.recv_multipart()
        msg2 = pickle.loads(msg)
        print(msg2["X"])
        print(msg2["Y"])
        print(topic)

#Start des thread sending et receiving
thread1 = threading.Thread(target=Subscribe)
thread1.start()  