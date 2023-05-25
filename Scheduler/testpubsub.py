import zmq
import time
import pickle

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
    dt = time.time()-t0
    if dt >= 20.0 :
        cont = False
    