import socket
import time
import random
import pickle
from threading import Timer

#packets = ["0, 1110", "1, 1011", "0, 0110", "1, 0111"]
timers = [None, None, None, None, None, None, None, None, None, None, None, None]

#Definition of the classes 
class Packet:
    def __init__(self, info: str):
        self.info = info

packets = [Packet("Paquete 1"), Packet("Paquete 2"), Packet("Paquete 3"), Packet("Paquete 4")]

#Setup the connection for the message transmission
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 3000
sock.bind((host, port))

def timeout():
    print("\n\n\nError: timeout")


def checksum(frame):
    frame.frame_type = "Corrupted Frame"
    print("\n\n\nError: cksum_err")
    print("El frame esta corrupto, la transferencia de datos no puede continuar :(")
    return frame

def frame_arrival():
    print("FRAME_ARRIVAL")

class Frame:
    def __init__(self, frame_type: str, seq_number: int, ack: int, packet_info: str):
        self.frame_type = frame_type
        self.seq_number = seq_number
        self.ack = ack
        self.packet_info = packet_info

#Definition of the Sender class
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
    Starts the whole simulation of the protocol
    Description: Basically loops the protocol sending pacakages constantly until the connection is finished
    Inputs: None
    Outputs: None
    """
    def begin(self):
        sequence_num = 1
        while True:
            if random.randint(0,10) in range (0,7):
                print("\n\n\nLa capa de red no tiene datos para enviar")
                time.sleep(1)
                continue
            print("\n\n\n\nNetwork_layer_ready: Nuevo paquete listo para enviarse")
            print("El numero de secuencia del paquete es: " , sequence_num)
            #self.next_seq_num += 1
            self.buffer = self.from_network_layer()
            if self.buffer == 0:
                continue
            print("Paquete obtenido")
            self.frame.packet_info = self.buffer
            self.frame.seq_number = self.next_seq_num
            self.frame.ack = self.next_seq_num
            frame_result = self.to_physical_layer(self.frame)
            if frame_result != None and frame_result.frame_type == "Corrupted Frame":
                exit()
            print("Enviando el frame al receiver")
            print("Esperando confirmación")
            self.wait_confirmation()
            sequence_num += 1
            time.sleep(2)

    """
    Get packet from network layer
    Inputs: None
    Outputs: packet
    """
    def from_network_layer(self):
        error_prob = random.randint(0,8)
        if  error_prob == 1:
            time.sleep(6)
            timeout()
            return 0
        if self.current_packet == len(packets):
            self.current_packet = 0
        packet = packets[self.current_packet]
        self.current_packet += 1
        return packet


    """
    Send frame to physical layer
    Inputs: frame
    Outputs: None
    """
    def to_physical_layer(self, frame):
        error_prob = random.randint(0,12)
        if  error_prob == 1:
            frame = checksum(frame)
            return frame
        self.client_socket.send(pickle.dumps(frame))
        self.start_timer(frame.seq_number)

    """
    Wait for confirmation from receiver
    Inputs: None
    Outputs: None
    """
    def wait_confirmation(self):
        frame_arrival = None
        if random.randint(0,8) == 1:
            time.sleep(6)
            #ack_timeout()
            #return 0
        while True:
            frame_arrival = self.client_socket.recv(4096)
            print(frame_arrival)
            if frame_arrival:
                frame_arrival()
                break
        self.frame_s = pickle.loads(frame_arrival)
        self.stop_timer(self.frame_s.ack)
        self.base = self.frame_s.ack + 1

    """
    Start timer
    Inputs: seq_number
    Outputs: None
    """
    def start_timer(self, seq_number):
        if timers[seq_number] is None:
            timers[seq_number] = Timer(5, self.ackn_timeout, [seq_number])
            timers[seq_number].start()

    """
    Stop timer
    Inputs: seq_number
    Outputs: None
    """
    def stop_timer(self, seq_number):
        if timers[seq_number] is not None:
            timers[seq_number].cancel()
            timers[seq_number] = None

    """
    Timeout
    Inputs: seq_number
    Outputs: None
    """
    def ackn_timeout(self, seq_number):
        print("\n\n\nError: ack_timeout")
        print("Intento de reenvio de paquete y esperando respuesta")
        self.resend_frame(seq_number)

    """
    Resend frame
    Inputs: seq_number
    Outputs: None
    """
    def resend_frame(self, seq_number):
        self.frame.seq_number = seq_number
        self.frame.ack = seq_number
        self.to_physical_layer(self.frame)


# This starts the code for the go back n sender
#NOTE: YOU HAVE TO RUN BOTH gobackn_main.py and gobackn_receiver.py AT THE SAME TIME TO MAKE IT WORK!
sock.listen(5)
print("Esperando conexion")
while True:
    client_socket, address = sock.accept()
    print("Conexion establecida")
    sender = Sender(client_socket, address)
    sender.begin()
    client_socket.close()
    print("Conexion cerrada")

