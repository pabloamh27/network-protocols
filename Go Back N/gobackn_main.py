import socket
import threading
import time
import random
import pickle
from threading import Timer
import tkinter as tk

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
pausa = False

def timeout(self):
    self.frame.ack = 0
    self.frame.packet_info = Packet("Timed Out")
    gui.add_frame(self.frame)
    gui.frame_listbox.insert(tk.END, "Error: timeout")
    print("\n\n\nError: timeout")


def checksum(self, frame):
    frame.frame_type = "Corrupted Frame"
    frame.ack = 0
    gui.frame_listbox.insert(tk.END, "Error: cksum_err")
    gui.frame_listbox.insert(tk.END, "El frame esta corrupto, la transferencia de datos no puede continuar :(")
    print("\n\n\nError: cksum_err")
    print("El frame esta corrupto, la transferencia de datos no puede continuar :(")
    return frame

def frame_arrival_error(self):
    print("FRAME_ARRIVAL")
    gui.frame_listbox.insert(tk.END, "FRAME_ARRIVAL")

class SimulatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Go Back N Protocol Simulator")

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
        self.frame_listbox.insert(tk.END, f"Kind: {frame.frame_type} | Seq: {frame.seq_number} | Ack?: {frame.ack} | Info: {frame.packet_info.info}")

    def pause(self):
        global pausa
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
            if pausa == True:
                continue
            if random.randint(0,10) in range (0,7):
                print("\n\n\nLa capa de red no tiene datos para enviar")
                time.sleep(1)
                continue
            gui.frame_listbox.insert(tk.END ,"Network_layer_ready: Nuevo paquete listo para enviarse")
            print("El numero de secuencia del paquete es: " , sequence_num)
            #Go back N algorithm
            if self.next_seq_num < self.base + self.window_size:
                self.buffer_network = self.from_network_layer()
                if self.buffer_network == 0:
                    continue
                print("Paquete obtenido")
                self.frame = Frame("Normal Frame", sequence_num, 0, self.buffer_network)
                frame_result = self.to_physical_layer(self.frame)
                if frame_result != None and frame_result.frame_type == "Corrupted Frame":
                    time.sleep(2)  
                    exit()
                self.buffer.append(frame_result)
                self.next_seq_num += 1
                self.wait_confirmation()
                #ACK confirmed
                self.base += 1
                self.frame.seq_number = sequence_num
                self.frame.ack = 1
                gui.add_frame(self.frame)
                sequence_num += 1
                if self.base == self.next_seq_num:
                    self.start_timer(self.base)                
            else:
                print("La ventana esta llena, el paquete se descarta")
                gui.frame_listbox.insert(tk.END, "La ventana esta llena, el paquete se descarta")
                self.next_seq_num = 0
                continue





    """
    Get packet from network layer
    Inputs: None
    Outputs: packet
    """
    def from_network_layer(self):
        error_prob = random.randint(0,8)
        if  error_prob == 1:
            time.sleep(6)
            timeout(self)
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
        if  error_prob == 13:
            frame = checksum(self, frame)
            return frame
        self.client_socket.send(pickle.dumps(frame))
        self.start_timer(frame.seq_number)
        return frame

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
                frame_arrival_error(self)
                time.sleep(1)
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
        self.frame.seq_number = seq_number
        self.frame.ack = 0
        gui.frame_listbox.insert(tk.END, "Error: ack_timeout")
        gui.frame_listbox.insert(tk.END, "Intento de reenvio de paquete y esperando respuesta")
        gui.add_frame(self.frame)
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
def startSimulation():
    sock.listen(5)
    print("Esperando conexion")
    while True:
        client_socket, address = sock.accept()
        print("Conexion establecida")
        sender = Sender(client_socket, address)
        sender.begin()
        client_socket.close()
        print("Conexion cerrada")

def button():
    threading.Thread(target=startSimulation).start()

gui.startSimulationButton = tk.Button(gui.root, text="Start Simulation", command=button)
gui.startSimulationButton.pack(side=tk.BOTTOM, pady=10)

gui.start()