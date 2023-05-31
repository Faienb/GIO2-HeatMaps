import zmq
context = zmq.Context()
sender = context.socket(zmq.PUSH) # Création du socket en mode Push
# Connexion au serveur
sender.connect("tcp://10.191.6.34:5560") # changer ici localhost pour l'IP de votre machine
sender.send_string("Hello, my name is RPi 1")
