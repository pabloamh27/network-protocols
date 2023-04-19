import socket
import time
import random
import pickle
from threading import Timer

#packets = ["0, 1110", "1, 1011", "0, 0110", "1, 0111"]

class Packet:
    def __init__(self, info: str):
        self.info = info

#Setup the connection for the message transmission
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 3100
sock.connect((host, port))
print("\nConectado a: " + str(host) + ":" + str(port))

#Definition of Frame class
class Frame:
    def __init__(self, frame_type: str, seq_number: int, ack: int, packet_info: str):
        self.frame_type = frame_type
        self.seq_number = seq_number
        self.ack = ack
        self.packet_info = packet_info

def frame_arrival():
    print("FRAME_ARRIVAL")

#Definition of the main function for the reciever in go back n protocol
def reciever():
    counter = 0
    package_name = ""
    while True:
        print("\nEsperando un nuevo paquete")
        frame = sock.recv(1024)
        frame = pickle.loads(frame)
        if str(package_name) != str(frame.packet_info.info):
            counter += 1
        frame_arrival()
        print("Paquete: " + str(frame.packet_info.info))
        print("El paquete contiene el siguiente numero de secuencia: ", counter)
        print("Enviando confirmación")
        frame_s = Frame("Confirmation", frame.seq_number, frame.ack, None)
        sock.send(pickle.dumps(frame_s))
        print("Confirmación enviada")
        package_name = frame.packet_info.info
        time.sleep(2)

if __name__ == '__main__':
    reciever()
    sock.close()

