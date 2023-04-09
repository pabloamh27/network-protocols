from src.UtopianProtocol.sender import senderUtopian
from src.UtopianProtocol.receiver import receiverUtopian
from src.SelectiveRepetitiveProtocol.sender import senderSelectiveRepetitive
from src.SelectiveRepetitiveProtocol.receiver import receiverSelectiveRepetitive
import threading, time

def test():
    #Selective Repetitive Protocol
    '''
    t1 = threading.Thread(target=receiverSelectiveRepetitive, args=())
    t2 = threading.Thread(target=senderSelectiveRepetitive, args=())
    
    t1.start()
    time.sleep(1)
    t2.start()
    
    t1.join()
    t2.join()
    '''
    #Utopian Protocol
    
    t1 = threading.Thread(target=receiverUtopian, args=())
    t2 = threading.Thread(target=senderUtopian, args=())
    
    t1.start()
    time.sleep(2)
    t2.start()
    
    t1.join()
    t2.join()
    
test()