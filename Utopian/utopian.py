import threading, time, socket, pickle, keyboard, random
from enum import Enum

BUFFER_SIZE = 8192

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

'''
Function that simulates the reciever behavior
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
    
    print("Got connection ", address)
    
    frameObtained = Frame(0, "", "", "")
    
    while not keyboard.is_pressed("q"):
        frameObtained = connection.recv(BUFFER_SIZE)
        frameObtained = pickle.loads(frameObtained)
        print(frameObtained.packetInfo.format(COUNTER))
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
    
    packet = "Paquete: {}\nInformación: Lorem Ipsum Dolor sit amet"
    frameToSend = Frame(Kind.DATA, 0, 0, packet)
    
    while True:
        try:
            ETA = random.randint(2, 5)
            time.sleep(ETA)
            serializedFrame = pickle.dumps(frameToSend)
            senderSocket.send(serializedFrame)
        
        except socket.error:
            break
    
    senderSocket.close()

'''
Function that starts the threads
Description: It starts the threads
Inputs: None
Outputs: None
'''
def startUtopian():    
    reciever = threading.Thread(target=receiverUtopian, args=())
    sender = threading.Thread(target=senderUtopian, args=())
    
    reciever.start()
    time.sleep(2)
    sender.start()
    
    reciever.join()
    sender.join()
    
startUtopian()