from src.frame import Frame
import socket, pickle, keyboard

BUFFER_SIZE = 8192

#it simulates the receiver function side in utipian protocol
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