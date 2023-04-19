#--------------------------RECEIVER
import socket
import pickle
import time
import random

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 3000
sock.connect((host, port))
print("\nConectado a: " + str(host) + ":" + str(port))

class Frame:
    def __init__(self, frame_type: str, packet_info: str, seq_number: int, confirmation_number: int):
        self.frame_type = frame_type
        self.packet_info = packet_info
        self.seq_number = seq_number
        self.confirmation_number = confirmation_number

def receiver():
    frame_r, frame_s = Frame("Normal Frame", None, 0, 1), Frame("Confirmation", None, 1, 1)
    event_type = "FRAME_ARRIVAL"

    while True:
        print("Esperando la llegada de un frame")
        frame_r = wait_for_event()
        print("Informacion obtenida: ", frame_r.packet_info)
        frame_s.packet_info = "Frame de confirmacion"
        print("Enviando confirmacion")

        to_physical_layer(frame_s)

def wait_for_event():
    frame_arrival = None

    while True:
        frame_arrival = sock.recv(4096)
        if frame_arrival:
            print("Un frame llego")
            break
    return pickle.loads(frame_arrival)

def to_physical_layer(frame):
    sock.send(pickle.dumps(frame))
#--------------------------EJECUCION

if __name__ == '__main__':
    receiver()
    sock.close()