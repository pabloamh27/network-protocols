import socket
import time
import random
import pickle

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 8000
s.connect((host,port))
print("Connected to " + str(host) + ":" + str(port) + "\n")

class Frame:

    def __init__(self, frame_type: str, seq_number: int, ack: int, packet_info: str):
        self.frame_type = frame_type
        self.seq_number = seq_number
        self.ack = ack
        self.packet_info = packet_info


def receiver():
    frame_r, frame_s = Frame("Received Frame", None, None, None), Frame("Dummy Confirmation Frame", None, None, None)
    event_type = "FRAME ARRIVAL"

    while True:
        print("Waiting for new arrival\n")
        frame_r = wait_for_event() # Wait for frame arrival and return it (from_physical_layer)

        print("Data received:", frame_r.packet_info)

        frame_s.seq_number = frame_r.seq_number
        frame_s.ack = frame_r.ack
        frame_s.packet_info = "Confirmation frame" #  Dummy confirmation frame
        print("Sending confirmation")

        to_physical_layer(frame_s)

def wait_for_event():
    frame_arrival = None

    while True:
        frame_arrival = s.recv(16384) # We have to decode it

        if frame_arrival:
            print("A frame has arrived!")
            break
    
    return pickle.loads(frame_arrival)

def to_physical_layer(frame):
    s.send(pickle.dumps(frame))
    print("Confirmation sent\n")

if __name__ == '__main__':
    receiver()
    s.close()