from pprint import pprint
from src.frame import Frame, Kind
import threading, pickle, socket, time, random

WINDOW_COUNTER = 0

BUFFER_SIZE = 1024

FRAMES_WITHOUT_CONFIRMATION = []
WINDOW_FRAMES = []

RETRY_TIMER = 0

CURRENT_SEQUENCE_NUMBER = 0
CURRENT_ACK_SEQUENCE_NUMBER = -1

LOCK = threading.Lock()

NETWORK_LAYER_READY = True

TYPE_FRAME = [Kind.DATA, 
              Kind.DATA, 
              Kind.DATA, 
              Kind.DATA, 
              Kind.DATA, 
              Kind.DATA, 
              Kind.DATA, 
              Kind.DATA,
              Kind.CKSUM_ERR,
              Kind.CKSUM_ERR]

senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = socket.gethostname()
portA = 4001
portB = 4002

#Gets the next frame of the window to send 
def nextFrame():
    global WINDOW_COUNTER
    
    nextFrameToSend = WINDOW_FRAMES[WINDOW_COUNTER]
    
    WINDOW_COUNTER += 1
        
    return nextFrameToSend    

#Check if there are some confimartions of received frames
def confirmedSent():
    global CURRENT_ACK_SEQUENCE_NUMBER
    senderSocket.bind(('', portA))
    print("inicio")
    while True:
        try:
            ack, _ = senderSocket.recvfrom(BUFFER_SIZE)
            
            LOCK.acquire()
            ackNum = pickle.loads(ack)
            
            print("\nFrame Confirmed: ", ackNum)
            CURRENT_ACK_SEQUENCE_NUMBER = ackNum
            FRAMES_WITHOUT_CONFIRMATION.remove(ackNum)
            
            LOCK.release()
        except Exception as e:
            print("Error: ", e)

#Slide the window sender in order to get new frames to send        
def setWindowSender():
    global CURRENT_SEQUENCE_NUMBER
    
    packet = "Lorem Ipsum Dolor sit amet"
    
    frameToSend = Frame(random.choice(TYPE_FRAME), CURRENT_SEQUENCE_NUMBER, -1, packet)
    
    WINDOW_FRAMES.append(frameToSend)
    CURRENT_SEQUENCE_NUMBER += 1

#When some frame timeout it tries to send it again
def retry_send(frameToSend):
    LOCK.acquire()
    
    if frameToSend.sequenceNumber not in FRAMES_WITHOUT_CONFIRMATION:
        LOCK.release()
        return
    
    frameToSend.kind = random.choice(TYPE_FRAME)
    print("\n**** Timeout: ", frameToSend.sequenceNumber, " ****")
    print("____________________________")
    print("\nSending Again: ", frameToSend.sequenceNumber, "\nType: ", frameToSend.kind)
    
    serializedFrame = pickle.dumps(frameToSend)
    try:
        senderSocket.sendto(serializedFrame, (host, portB))
    except:
        print("The execution has ended")
        LOCK.release()
        return
    
    timer = threading.Timer(RETRY_TIMER, retry_send, args=(frameToSend,))
    timer.start()
    LOCK.release()

#Main function, it manages all functions to establish the selective repetitive protocol
def senderSelectiveRepetitive(windowSize=7):
    global NETWORK_LAYER_READY
    global CURRENT_ACK_SEQUENCE_NUMBER
    global WINDOW_COUNTER
    global RETRY_TIMER
    
    RETRY_TIMER = (windowSize + 1) / 2
    thread = threading.Thread(target=confirmedSent, args=())
    thread.start()
    
    while True:
        if len(WINDOW_FRAMES) < windowSize and NETWORK_LAYER_READY:
            setWindowSender()
        else: 
            NETWORK_LAYER_READY = False
            time.sleep(1.5)
            
            LOCK.acquire()
            
            frameToSend = nextFrame()
            FRAMES_WITHOUT_CONFIRMATION.append(frameToSend.sequenceNumber)
            serializedFrame = pickle.dumps(frameToSend)
            
            print("____________________________")
            print("\nSending: ", frameToSend.sequenceNumber, "\nType: ", frameToSend.kind)
            
            try:
                senderSocket.sendto(serializedFrame, (host, portB))
            except:
                print("The execution has ended")
                return
            
            timer = threading.Timer(RETRY_TIMER, retry_send, args=(frameToSend,))
            timer.start()
            
            LOCK.release()
            
            if WINDOW_COUNTER == windowSize:
                WINDOW_FRAMES.clear()
                WINDOW_COUNTER = 0
                NETWORK_LAYER_READY = True
                
        
        
            
        