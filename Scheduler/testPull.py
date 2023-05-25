import zmq
context = zmq.Context()
receiver = context.socket(zmq.PULL) # Création du socket en mode Pull
receiver.bind("tcp://*:5560") # On accepte toutes les connexions sur le port 5558
def loop():
    while True:
        print("Hello")
        string = receiver.recv_string()
        print(string)
        return string

print(loop()) 