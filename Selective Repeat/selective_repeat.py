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

def frame_arrival_error():
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
        self.timeout = timeout()

    """
    Starts the whole simulation of the selective repeat protocol
    Description: Basically loops the protocol sending pacakages constantly until the connection is finished
    Inputs: None
    """
    #Starts the whole simulation of the selective repeat protocol
    def start(self):
        sequence_num = 1
        while True:
            #Send the frame
            self.frame = Frame("Normal Frame", sequence_num, None, packets[self.current_packet].info)
            self.buffer.append(self.frame)
            self.send_frame(self.frame)
            #Start the timer
            timers[sequence_num] = Timer(3, self.timeout)
            timers[sequence_num].start()
            #Increment the sequence number
            sequence_num += 1
            #Increment the current packet
            self.current_packet += 1
            #Check if the current packet is out of the range of the packets
            if self.current_packet == len(packets):
                self.current_packet = 0
            #Wait for the confirmation
            self.wait_for_confirmation()
            #Check if the sequence number is out of the range of the window size
            if sequence_num == self.window_size + 1:
                sequence_num = 1

    """
    Sends the frame to the reciever
    Description: Sends the frame to the reciever and waits for the confirmation
    Inputs: frame
    """
    def send_frame(self, frame):
        print("\nEnviando el siguiente paquete: " + str(frame.packet_info))
        self.client_socket.send(pickle.dumps(frame))
        print("Paquete enviado")

    """
    Waits for the confirmation of the frame
    Description: Waits for the confirmation of the frame and checks if the frame is corrupted or not
    Inputs: None
    """
    def wait_for_confirmation(self):
        print("Esperando la confirmacion del paquete...")
        self.frame_s = pickle.loads(self.client_socket.recv(1024))
        print("Confirmacion recibida")
        #Check if the frame is corrupted
        if self.frame_s.frame_type == "Corrupted Frame":
            self.frame_s = checksum(self.frame_s)
        #Check if the frame is a confirmation
        if self.frame_s.frame_type == "Confirmation":
            #Stop the timer
            timers[self.frame_s.seq_number].cancel()
            print("El paquete se ha enviado correctamente")
            #Check if the frame is the last one
            if self.frame_s.seq_number == self.window_size:
                self.base = 1
                self.next_seq_num = 1
            else:
                self.base = self.frame_s.seq_number + 1
                self.next_seq_num = self.frame_s.seq_number + 1

#Start the server
sock.listen(1)
print("Waiting for connection...")
client_socket, address = sock.accept()
print("Connection established")
sender = Sender(client_socket, address)
sender.start()

