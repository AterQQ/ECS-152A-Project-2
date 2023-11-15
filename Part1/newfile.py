import socket
import random
import struct

ROOTIP = "199.9.14.201"
DNSPORT = 53

def tmzPacketConstruion(domain):
    id = random.randint(1, 65536)
    flags = 0
    numQuestions = 1
    numAnswerRR = 0
    numAuthorityRR = 0
    numAdditionalRR = 0

    header = struct.pack("!HHHHHH", id, flags, numQuestions, numAnswerRR, numAuthorityRR, numAdditionalRR)

    question = b''

    for part in domain.split("."):
        question += (len(part).to_bytes(1, 'big')) + part.encode("utf-8")
    question += struct.pack("!B", 0) + struct.pack("!HH", 1, 1)

    # print(header, "Question is", question)
    request = header + question
    print("Total string is", request)
    return request



        
        
    
    

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = tmzPacketConstruion("tmz.com")
sock.sendto(message, (ROOTIP, DNSPORT))

recieve, addr = sock.recvfrom(1024)
print(recieve)
# objects = DNSPayload()
# objects.tmzPacketConstruion()