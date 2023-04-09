import socket
import time
import random
import pickle

packets = ["0, 1110", "1, 1011", "0, 0110", "1, 0111"]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 8000
s.bind((host, port))

class Frame:

    def __init__(self, frame_type: str, packet_info: str):
        self.frame_type = frame_type
        self.packet_info = packet_info

class Sender:

    def __init__(self, client_socket, address):
        self.client_socket = client_socket
        self.address = address
        self.current_packet = 0

    """
    Starts the simulation for the sender for stop and wait protocol
    Args:
        None

    Returns:
        None
    """
    def start(self):
        frame = Frame("Normal Frame", None)
        buffer = None
        event_type = "FRAME ARRIVAL"

        while True:
            print("\nSending new packet")

            buffer = self.from_network_layer() # Get something to send
            print("Packet gotten")

            frame.packet_info = buffer # Copy it into the frame for transmission
            self.to_physical_layer(frame)
            
            print("Sending information to receiver")
            print("Waiting for confirmation before continuing...")

            self.wait_for_event() # Wait till confirmation
            time.sleep(2)

    """
    Fetch a packet from the network layer for transmission on the channel
    Args:
        None

    Returns:
        A packet
    """
    def from_network_layer(self):
        if self.current_packet == len(packets):
            self.current_packet = 0
        
        packet = packets[self.current_packet]
        self.current_packet += 1
        
        return packet

    """
    Pass the frame to the physical layer for transmission
    Args:
        frame: The frame to transmit

    Returns:
        None
    """
    def to_physical_layer(self, frame):
        self.client_socket.send(pickle.dumps(frame))

    """
    Waits till frame arrival confirmation
    Args:
        None

    Returns:
        None
    """
    def wait_for_event(self):

        while True:
            frame_arrival = self.client_socket.recv(1024)

            if frame_arrival:
                print("\nAcknowledgement frame received!\n")
                break

# Start listening for connections
s.listen(1)
print("Server is listening")

while True:
    client_socket, address = s.accept()
    print("Connected by " + str(address))
    sender = Sender(client_socket, address)
    sender.start()
