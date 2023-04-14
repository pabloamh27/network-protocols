#use this as a template /home/luis/Documentos/redes/network-protocols/Proyecto de apoyo/sliding-window/Servidor.py
#make a sever for the slididng window protocol
# """
#
import socket
import pickle
import time
import random

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
        self.base = 0
        self.next_seq_num = 0
        self.window_size = 3
        self.buffer = []
        self.frame = Frame("Normal Frame", None, None, None)
        self.frame_s = Frame("Confirmation", None, None, None)
        self.event_type = "FRAME_ARRIVAL"

    """
    Simulation of Sender
    """
    def begin(self):
        while True:
            print("\nEnviando un nuevo paquete")

            self.buffer = self.from_network_layer()
            print("Paquete obtenido")

            self.frame.packet_info = self.buffer
            self.frame.seq_number = self.next_seq_num
            self.frame.ack = self.next_seq_num
            self.to_physical_layer(self.frame)
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
        return packet
    
    """
    Send a frame to the physical layer
    """
    def to_physical_layer(self, frame):
        self.client_socket.send(pickle.dumps(frame))
        print("Frame enviado")


    """
    Wait for a confirmation from the receiver
    """
    def wait_confirmation(self):
        while True:
            data = self.client_socket.recv(1024)
            self.frame_s = pickle.loads(data)
            if self.frame_s.frame_type == "Confirmation":
                print("Confirmación recibida")
                self.next_seq_num = self.next_seq_num + 1
                break

    """
    Close the connection
    """
    def close(self):
        self.client_socket.close()
        print("Connection closed")

if __name__ == "__main__":
    sock.listen(5)
    print("Server listening on port 3000")
    while True:
        client_socket, address = sock.accept()
        print("Connection established with {}".format(address))
        sender = Sender(client_socket, address)
        sender.begin()
        sender.close()
