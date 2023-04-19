import threading, time, socket, pickle, keyboard, random
from enum import Enum
import tkinter as tk

BUFFER_SIZE = 8192
pausa = False

#This class is to define the kind of data
class Kind(Enum):
    DATA = 1
    ACK = 2
    CKSUM_ERR = 3

#This defines the Frame class 
class Frame:
    kind = Kind
    sequenceNumber = 0
    confirmationNumber = 0
    packetInfo = ""

    def __init__(self, kind, sequenceNumber, confirmationNumber, packetInfo):
        self.kind = kind
        self.sequenceNumber = sequenceNumber
        self.confirmationNumber = confirmationNumber
        self.packetInfo = packetInfo

class SimulatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Utopian Protocol Simulator")

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
        self.frame_listbox.insert(tk.END, f"Kind: {frame.kind} | Seq: {frame.sequenceNumber} | Conf: {frame.confirmationNumber} | Info: {frame.packetInfo}")

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

'''
Function that simulates the receiver behavior
Description: It receives the data from the sender and prints it
Inputs: None
Outputs: None
'''
def receiverUtopian():
    COUNTER = 0
    
    receiverSocket = socket.socket()
    host = socket.gethostname()
    port = 8181
    receiverSocket.bind((host, port))
    
    receiverSocket.listen(1)
    connection,address = receiverSocket.accept()
    
    gui.add_frame(Frame(0, "", "", f"Got connection {address}"))
    
    frameObtained = Frame(0, "", "", "")
    
    while not keyboard.is_pressed("q"):
        frameObtained = connection.recv(BUFFER_SIZE)
        frameObtained = pickle.loads(frameObtained)

        COUNTER += 1
       
    connection.close()

'''
Function that simulates the sender behavior
Description: It sends the data to the receiver
Inputs: None
Outputs: None
'''
def senderUtopian():
    senderSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 8181
    
    senderSocket.connect((host, port))
    #Definition of the classes 
    class Packet:
        def __init__(self, info: str):
            self.info = info

    sequenceNumber = 1
    packet = [Packet("Paquete 1"), Packet("Paquete 2"), Packet("Paquete 3"), Packet("Paquete 4")]
    i = 0
    while True:
        try:
            if i == 4:
                i = 0
            if pausa == True:
                continue
            frameToSend = Frame(Kind.DATA, sequenceNumber, 0, packet[i].info)
            ETA = random.randint(2, 5)
            time.sleep(ETA)
            serializedFrame = pickle.dumps(frameToSend)
            senderSocket.send(serializedFrame)
            gui.add_frame(frameToSend)
            i+=1
            sequenceNumber+=1
        except socket.error:
            break
    
    senderSocket.close()

def startSimulation():
    receiver_thread = threading.Thread(target=receiverUtopian)
    sender_thread = threading.Thread(target=senderUtopian)
    receiver_thread.start()
    sender_thread.start()

gui.startSimulationButton = tk.Button(gui.root, text="Start Simulation", command=startSimulation)
gui.startSimulationButton.pack(side=tk.BOTTOM, pady=10)

gui.start()