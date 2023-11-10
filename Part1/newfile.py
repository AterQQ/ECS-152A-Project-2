import socket
import random

class DNSPayload:
    # def __init__(self) -> None:
        # self.destIP
        # self.destPort
        # self.message
    
    # def tmzPacketConstuction(self):
    #     bits = ['0', '1']
    #     id = ''
    #     for i in range(16):
    #         id += random.choice(bits)
    #     flags = 
    def tmzPacketConstruion(self):
        id = random.randint(1, 65536)
        flags = 0b0000000100000000

        idUpper, idLower = divmod(id, 256)
        flagsUpper, flagsLower = divmod(flags, 256)
        fillerByte = 0
        numQuestions = 1
        numAnswerRR = 0
        numAuthorityRR = 0
        numAdditionalRR = 0

        encodedQuery = bytearray([
                        idUpper,
                        idLower,
                        flagsUpper,
                        flagsLower,
                        fillerByte, 
                        numQuestions,
                        fillerByte,
                        numAnswerRR,
                        fillerByte,
                        numAuthorityRR,
                        fillerByte,
                        numAdditionalRR
                        ])
        
        print(encodedQuery)



        
        
    
    

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

objects = DNSPayload()
objects.tmzPacketConstruion()