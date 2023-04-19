import socket
import pickle
import time
import random

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 3000
sock.connect((host, port))
print("\nConectado a: " + str(host) + ":" + str(port))

class Packet:
    def __init__(self, info: str):
        self.info = info

class Frame:
    def __init__(self, frame_type: str, packet_info: str, seq_number: int, confirmation_number: int):
        self.frame_type = frame_type
        self.packet_info = packet_info
        self.seq_number = seq_number
        self.confirmation_number = confirmation_number

def frame_arrival():
    print("FRAME_ARRIVAL")


class Receiver:
    def __init__(self, client_socket, address):
        self.client_socket = client_socket
        self.address = address
        self.current_packet = 0
        self.base = 0
        self.next_seq_num = 0
        self.window_size = 3
        self.buffer = []
        self.frame = Frame("Normal Frame", None, None, None)
        self.frame_s = Frame("Confirmation", None, None, None)
        self.event_type = "FRAME_ARRIVAL"

    """
    Simulation of Receiver
    """
    def begin(self):
        while True:
            print("\nEsperando un nuevo paquete")
            self.from_physical_layer()
            print("Paquete recibido")
            self.to_network_layer(self.frame)
            print("Enviando confirmación")
            self.send_confirmation()
            time.sleep(2)

    """
    Simulation of from_physical_layer
    """
    def from_physical_layer(self):
        self.frame = pickle.loads(self.client_socket.recv(1024))
        print("Frame recibido: " + str(self.frame.frame_type) + " " + str(self.frame.packet_info) + " " + str(self.frame.seq_number) + " " + str(self.frame.confirmation_number))


    """
    Simulation of to_network_layer
    """
    def to_network_layer(self, frame):
        print("Paquete enviado al network layer: " + str(frame.packet_info.info))

    """
    Simulation of send_confirmation
    """
    def send_confirmation(self):
        self.frame_s.frame_type = "Confirmation"
        self.frame_s.packet_info = None
        self.frame_s.seq_number = None
        self.frame_s.confirmation_number = self.frame.seq_number
        self.to_physical_layer(self.frame_s)

    """
    Simulation of to_physical_layer
    """
    def to_physical_layer(self, frame):
        self.client_socket.send(pickle.dumps(frame))
        print("Frame enviado: " + str(frame.frame_type) + " " + str(frame.packet_info) + " " + str(frame.seq_number) + " " + str(frame.confirmation_number))

receiver = Receiver(sock, host)
receiver.begin()

