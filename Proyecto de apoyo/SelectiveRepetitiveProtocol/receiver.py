import socket, pickle

BUFFER_SIZE = 8192
BUFFER_FRAME_SIZE = 0

BUFFER_FRAME = []
EXPECTED_SEQUENCE_NUMBER = 0

receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = socket.gethostname()
portA = 4001
portB = 4002
receiverSocket.bind(('', portB))

class Frame:

    def __init__(self, frame_type: str, seq_number: int, ack: int, packet_info: str):
        self.frame_type = frame_type
        self.seq_number = seq_number
        self.ack = ack
        self.packet_info = packet_info

#it simulates the receiver function in selective repetitive protocol
def receiverSelectiveRepetitive(windowSize=7):
    global EXPECTED_SEQUENCE_NUMBER
    global BUFFER_FRAME_SIZE
    BUFFER_FRAME_SIZE = (windowSize + 1) / 2
    
    while True:
        frameObtained = Frame(0, "", "", "")

        try:
            frameObtained, _ =  receiverSocket.recvfrom(BUFFER_SIZE)
            frameObtained = pickle.loads(frameObtained)
            
            sequenceNumber = frameObtained.sequenceNumber
            print("\nProcesando: ", sequenceNumber)
            
            if EXPECTED_SEQUENCE_NUMBER == sequenceNumber and not frameObtained.kind == Kind.CKSUM_ERR:
                print("Info: ", frameObtained.packetInfo)
                receiverSocket.sendto(pickle.dumps(sequenceNumber), (host, portA))
                
                EXPECTED_SEQUENCE_NUMBER += 1
                
                if len(BUFFER_FRAME) > 0:
                    print("Frames en el Buffer: ", [item.sequenceNumber for item in BUFFER_FRAME])
                    EXPECTED_SEQUENCE_NUMBER += len(BUFFER_FRAME)
                    BUFFER_FRAME.clear() 
                    print("Frame esperado: ", EXPECTED_SEQUENCE_NUMBER)
                    
            elif sequenceNumber >= EXPECTED_SEQUENCE_NUMBER - BUFFER_FRAME_SIZE/2 and sequenceNumber <= EXPECTED_SEQUENCE_NUMBER + BUFFER_FRAME_SIZE/2 and len(BUFFER_FRAME) < BUFFER_FRAME_SIZE:
                if not frameObtained.kind == Kind.CKSUM_ERR:
                    print("Info: ", frameObtained.packetInfo)
                    BUFFER_FRAME.append(frameObtained)
                    print("Frame esperado: ", EXPECTED_SEQUENCE_NUMBER)
                    receiverSocket.sendto(pickle.dumps(sequenceNumber), (host, portA))
            
            print("____________________________")
        except Exception as e:
            print(e)