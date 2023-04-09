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

    def __init__(self, frame_type: str, packet_info: str):
        self.frame_type = frame_type
        self.packet_info = packet_info

"""
Starts the simulation for the receiver for stop and wait protocol
Args:
    None

Returns:
    None
"""
def receiver():
    frame_r, frame_s = Frame("Normal Frame", None), Frame("Dummy Confirmation Frame", None)
    event_type = "FRAME ARRIVAL"

    while True:
        print("Waiting for new arrival\n")
        frame_r = wait_for_event() # Wait for frame arrival and return it (from_physical_layer)

        print("Data received:", frame_r.packet_info)

        frame_s.packet_info = "Confirmation frame" #  Dummy confirmation frame
        print("Sending confirmation\n")

        to_physical_layer(frame_s)

"""
Waits till frame arrival confirmation
Args:
    None

Returns:
    frame_arrival: The decoded frame that has arrived
"""
def wait_for_event():
    frame_arrival = None

    while True:
        frame_arrival = s.recv(4096) # We have to decode it

        if frame_arrival:
            print("A frame has arrived!")
            break
    
    return pickle.loads(frame_arrival)

"""
Pass the frame to the physical layer for transmission
Args:
    frame: The frame to fetch

Returns:
    None
"""
def to_physical_layer(frame):
    s.send(pickle.dumps(frame))

if __name__ == '__main__':
    receiver()
    s.close()