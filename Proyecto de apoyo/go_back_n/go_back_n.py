import socket
import time
import random
import pickle
from threading import Timer

FRAME_ARRIVAL = 0
CKSUM_ERR = 1
TIMEOUT = 2


MAX_SEQ = 3
MAX_TIME = 10

packets = ["0, 1110", "1, 1011", "0, 0110", "1, 0111"]
timers = [None, None, None, None]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 8000
s.bind((host, port))

class Frame:

    def __init__(self, frame_type: str, seq_number: int, ack: int, packet_info: str):
        self.frame_type = frame_type
        self.seq_number = seq_number
        self.ack = ack
        self.packet_info = packet_info

class Sender:

    def __init__(self, client_socket, address):
        self.client_socket = client_socket
        self.address = address
        self.timer = None
        self.network_layer_ready = True
        
    def start(self):
        next_frame_to_send = None
        ack_expected = None
        frame_expected = None
        frame_r = None

        buffer = []
        used_buffers = None # Cantidad de buffers en uso
        index = None # Para acceder a cada buffer
        event_type = None

        enable_network_layer()
        ack_expected = 0
        next_frame_to_send = 0
        frame_expected = 0
        used_buffers = 0

        while True:
            event_type = self.wait_for_event()

            if event_type == self.network_layer_ready:
                print("Sending frame:", str(next_frame_to_send) + "\n")
                time.sleep(2)
                buffer.insert(next_frame_to_send, self.from_network_layer(next_frame_to_send))
                used_buffers += 1
                self.send_data(next_frame_to_send, frame_expected, buffer)
                next_frame_to_send = self.inc(next_frame_to_send)

            elif event_type == FRAME_ARRIVAL:
                frame_r = self.from_physical_layer()
                print("Frame has arrived")
                if frame_r.seq_number == frame_expected:
                    print("Data received:", frame_r.packet_info)
                    frame_expected = self.inc(frame_expected)

                # To handle piggybacked ack
                while self.between(ack_expected, frame_r.ack, next_frame_to_send):
                    used_buffers -= 1
                    self.stop_timer(ack_expected)
                    ack_expected = self.inc(ack_expected)

            elif event_type == CKSUM_ERR:
                # Ignore bad frames
                continue
            
            # TIMEOUT EVENT
            else:
                next_frame_to_send = ack_expected

                for i in range(1, used_buffers):
                    self.send_data(next_frame_to_send, frame_expected, buffer)
                    next_frame_to_send = self.inc(next_frame_to_send)
            
            if used_buffers < MAX_SEQ:
                print("\nEnabling network layer\n")
                self.enable_network_layer()
            
            else:
                print("\nDisabling network layer\n")
                self.disable_network_layer()

    def wait_for_event(self):
        
        while True:
            
            if self.network_layer_ready:
                return True
            
            elif self.from_physical_layer():
                return FRAME_ARRIVAL
            
            else:
                if timers[ack_expected] != None:
                    if timers[ack_expected] > MAX_TIME:
                        return TIMEOUT
                    
                return None

    def from_network_layer(self, packet):
        data = packets[packet]
        return data

    def from_physical_layer(self):

        frame_arrival = self.client_socket.recv(16384)

        if frame_arrival:

            print("A frame has arrived!")

        return pickle.loads(frame_arrival)

    def send_data(self, frame_number, frame_expected, buffer):
        ack = (frame_expected + MAX_SEQ) % (MAX_SEQ + 1)
        packet_info = buffer[frame_number]
        frame_s = Frame("Data Frame", frame_number, ack, packet_info)
        self.to_physical_layer(frame_s)
        self.start_timer(frame_number)
    
    def to_physical_layer(self, frame):
        self.client_socket.send(pickle.dumps(frame))

    def enable_network_layer(self):
        self.network_layer_ready = True

    def disable_network_layer(self):
        self.network_layer_ready = False
    
    def start_timer(self, frame_number):

        start = time.perf_counter()
        timers[frame_number] = start
    
    def stop_timer(self, frame_number):
        timers[frame_number] = None

    # Increment index circularly
    def inc(self, index):

        if index < MAX_SEQ:
            index += 1
            return index

        return 0

    def between(self, seq_number_a, seq_number_b, seq_number_c):

        if (((seq_number_a <= seq_number_b) and (seq_number_b < seq_number_c))\
          or ((seq_number_c < seq_number_a) and (seq_number_a <= seq_number_b))\
          or ((seq_number_b < seq_number_c) and (seq_number_c < seq_number_a))):
            return True

        else:
            return False

# Start listening for connections
s.listen(1)
print("Server is listening")

while True:
    client_socket, address = s.accept()
    print("Connected by " + str(address))
    sender = Sender(client_socket, address)
    sender.start()