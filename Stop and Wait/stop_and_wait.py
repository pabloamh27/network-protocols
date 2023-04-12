import socket
import pickle
import time
import random

#packets = ["0, 1110", "1, 1011", "0, 0110", "1, 0111"]
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 3000
sock.bind((host, port))

class Packet:
    def __init__(self, info: str):
        self.info = info

packets = [Packet("Paquete1"), Packet("Paquete2"), Packet("Paquete 3"), Packet("Paquete 4")]

class Frame:
    def __init__(self, frame_type: str, packet_info: str, seq_number: int, confirmation_number: int):
        self.frame_type = frame_type
        self.packet_info = packet_info
        self.seq_number = seq_number
        self.confirmation_number = confirmation_number

class Sender:
    def __init__(self, client_socket, address):
        self.client_socket = client_socket
        self.address = address
        self.current_packet = 0

    """
    Simulation of Sender
    """
    def begin(self):
        frame = Frame("Normal Frame", None, 0, 1)
        buffer = None
        event_type = "FRAME ARRIVAL"

        while True:
            print("\nEnviando un nuevo paquete")

            buffer = self.from_network_layer()
            print("Paquete obtenido")

            frame.packet_info = buffer
            self.to_physical_layer(frame)

            print("Enviando el frame al receiver")
            print("Esperando confirmación")

            self.wait_confirmation()
            time.sleep(2)

    """
    Fetch a packet from network layer
    """
    def from_network_layer(self):
        if self.current_packet == len(packets):
            self.current_packet = 0
        packet = packets[self.current_packet]
        self.current_packet += 1
        return packet.info

    """
    Pass a frame to physical layer
    """
    def to_physical_layer(self, frame):
        self.client_socket.send(pickle.dumps(frame))

    """
    Waits untill the frame confirms it's arrival
    """
    def wait_confirmation(self):
        while True:
            frame_arrival = self.client_socket.recv(4096)
            print(frame_arrival)
            if frame_arrival:
                print("\nEl frame fue recibido")
                break

#--------------------------EJECUCION
    
sock.listen(1)
print("Esperando el receiver")

while True:
    client_socket, address = sock.accept()
    print("Receiver conectado: " + str(address))
    sender = Sender(client_socket, address)
    sender.begin()