import socket
import pickle
import time
import random
import tkinter as tk
import threading

pausa = False

#packets = ["0, 1110", "1, 1011", "0, 0110", "1, 0111"]
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 3000
sock.bind((host, port))

class Packet:
    def __init__(self, info: str):
        self.info = info

packets = [Packet("Paquete1"), Packet("Paquete2"), Packet("Paquete 3"), Packet("Paquete 4")]


class SimulatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stop and Wait Protocol Simulator")

        self.frame_listbox = tk.Listbox(self.root)
        self.frame_listbox.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10
        )

        scrollbar = tk.Scrollbar(self.root, orient="vertical")
        scrollbar.config(command=self.frame_listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self.frame_listbox.config(yscrollcommand=scrollbar.set)

        self.pause_button = tk.Button(self.root, text="Pause/Resume", command=self.pause)
        self.pause_button.pack(side=tk.BOTTOM, pady=10)

    def add_frame(self, frame):
        self.frame_listbox.insert(tk.END, f"Kind: {frame.frame_type} | Seq: {frame.seq_number} | Conf: {frame.confirmation_number} | Info: {frame.packet_info}")

    def pause(self):
        global pausa
        print ("Pausa fue llamado")
        if pausa == False:
            self.frame_listbox.insert(tk.END, "El sistema está pausado!")
            pausa = True
        else:
            self.frame_listbox.insert(tk.END, "El sistema se reanudó!")
            pausa = False

    def start(self):
        self.root.mainloop()

gui = SimulatorGUI()

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
        count = 1

        while True:
            if pausa == True:
                continue
            print("\nEnviando un nuevo paquete")

            buffer = self.from_network_layer()
            print("Paquete obtenido")

            frame.packet_info = buffer
            self.to_physical_layer(frame)

            print("Enviando el frame al receiver")
            print("Esperando confirmación")

            self.wait_confirmation()
            frame.seq_number = count
            gui.add_frame(frame)
            count += 1
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
def execute():
    sock.listen(1)
    print("Esperando el receiver")

    while True:
        client_socket, address = sock.accept()
        print("Receiver conectado: " + str(address))
        sender = Sender(client_socket, address)
        sender.begin()

def button():
    threading.Thread(target=execute).start()

gui.startSimulationButton = tk.Button(gui.root, text="Start Simulation", command=button)
gui.startSimulationButton.pack(side=tk.BOTTOM, pady=10)

gui.start()