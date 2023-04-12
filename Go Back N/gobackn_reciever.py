import socket
import time
import random
import pickle
from threading import Timer

#packets = ["0, 1110", "1, 1011", "0, 0110", "1, 0111"]

class Packet:
    def __init__(self, info: str):
        self.info = info

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 3000
sock.connect((host, port))
print("\nConectado a: " + str(host) + ":" + str(port))

class Frame:

    def __init__(self, frame_type: str, seq_number: int, ack: int, packet_info: str):
        self.frame_type = frame_type
        self.seq_number = seq_number
        self.ack = ack
        self.packet_info = packet_info

#Go back N protocol algorithm
def reciever():
    while True:
        print("\nEsperando un nuevo paquete")
        frame = sock.recv(1024)
        frame = pickle.loads(frame)
        print("Paquete recibido")
        print("Paquete: " + str(frame.packet_info.info))
        print("Enviando confirmación")
        frame_s = Frame("Confirmation", frame.seq_number, frame.ack, None)
        sock.send(pickle.dumps(frame_s))
        print("Confirmación enviada")
        time.sleep(2)
if __name__ == '__main__':
    reciever()
    sock.close()

