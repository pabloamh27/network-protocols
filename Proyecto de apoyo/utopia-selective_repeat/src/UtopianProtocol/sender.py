from src.frame import Frame, Kind
import socket, random, time, pickle, keyboard

'''
    It simulates the utopian protocol
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