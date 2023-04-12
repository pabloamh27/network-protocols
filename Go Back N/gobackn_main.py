import socket
import time
import random
import pickle
from threading import Timer

#packets = ["0, 1110", "1, 1011", "0, 0110", "1, 0111"]
timers = [None, None, None, None]

class Packet:
    def __init__(self, info: str):
        self.info = info

packets = [Packet("Paquete1"), Packet("Paquete2"), Packet("Paquete 3"), Packet("Paquete 4")]


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 3000
sock.bind((host, port))

class Frame:

    def __init__(self, frame_type: str, seq_number: int, ack: int, packet_info: str):
        self.frame_type = frame_type
        self.seq_number = seq_number
        self.ack = ack
        self.packet_info = packet_info

#Go back N protocol algorithm
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
    Send frame to physical layer
    """
    def to_physical_layer(self, frame):
        self.client_socket.send(pickle.dumps(frame))
        self.start_timer(frame.seq_number)

    """
    Wait for confirmation from receiver
    """
    def wait_confirmation(self):
        frame_arrival = None

        while True:
            frame_arrival = self.client_socket.recv(4096)
            if frame_arrival:
                print("Un frame llego")
                break
        self.frame_s = pickle.loads(frame_arrival)
        self.stop_timer(self.frame_s.ack)
        self.base = self.frame_s.ack + 1

    def start_timer(self, seq_number):
        if timers[seq_number] is None:
            timers[seq_number] = Timer(5, self.timeout, [seq_number])
            timers[seq_number].start()

    def stop_timer(self, seq_number):
        if timers[seq_number] is not None:
            timers[seq_number].cancel()
            timers[seq_number] = None

    def timeout(self, seq_number):
        print

    def resend_frame(self, seq_number):
        self.frame.seq_number = seq_number
        self.frame.ack = seq_number
        self.to_physical_layer(self.frame)


sock.listen(5)
print("Esperando conexion")
while True:
    client_socket, address = sock.accept()
    print("Conexion establecida")
    sender = Sender(client_socket, address)
    sender.begin()
    client_socket.close()
    print("Conexion cerrada")

# Path: Go Back N\gobackn_receiver.py

