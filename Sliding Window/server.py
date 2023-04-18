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
            frame_result = self.to_physical_layer(self.frame)
            if frame_result != None and frame_result.frame_type == "Corrupted Frame":
                exit()
            print("Enviando el frame al receiver")
            print("Esperando confirmación")
            self.wait_confirmation()
            time.sleep(2)

    """
    Fetch a packet from network layer
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
    Send a frame to the physical layer
    """
    def to_physical_layer(self, frame):
        error_prob = random.randint(0,12)
        if  error_prob == 1:
            frame = checksum(frame)
            return frame
        self.client_socket.send(pickle.dumps(frame))
        print("Frame enviado")


    """
    Wait for a confirmation from the receiver
    """
    def wait_confirmation(self):
        if random.randint(0,8) == 1:
            time.sleep(6)
        while True:
            data = self.client_socket.recv(1024)
            print(data)
            if data:
                frame_arrival_error()
                time.sleep(1)
                break
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

if __name__ == "__main__":
    sock.listen(5)
    print("Server listening on port 3000")
    while True:
        client_socket, address = sock.accept()
        print("Connection established with {}".format(address))
        sender = Sender(client_socket, address)
        sender.begin()
        sender.close()
