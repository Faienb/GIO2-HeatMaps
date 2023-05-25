import zmq
import time
import pickle

context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.connect("tcp://10.191.6.34:5556")
# socket.subscribe("ecg-rpi-01")
socket.subscribe("topica")
while True :
    print("Hello")
    [topic,msg] = socket.recv_multipart()
    print("Hello2")
    msg2 = pickle.loads(msg)
    print(msg2["X"])
    print(topic)