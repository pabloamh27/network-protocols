from enum import Enum

class Kind(Enum):
    DATA = 1
    ACK = 2
    CKSUM_ERR = 3

'''
    It models the structure of Frame
'''
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