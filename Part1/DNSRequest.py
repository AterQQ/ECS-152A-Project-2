import socket
import random
import struct
import time
import copy

# Sources:
# https://www.rfc-editor.org/rfc/rfc1035 (for figuring out DNS bytes)
# Harron's ECS 152 Github Page: https://github.com/Haroon96/ecs152a-fall-2023

ROOTIP = "199.9.14.201"
DNSPORT = 53
HTTPPORT = 80
WEBSITE = "tmz.com"

def PacketConstruion(domain):
    # Header construction
    id = random.randint(1, 65536)
    flags = 0
    numQuestions = 1
    numAnswerRR = 0
    numAuthorityRR = 0
    numAdditionalRR = 0

    header = struct.pack("!HHHHHH", id, flags, numQuestions, numAnswerRR, numAuthorityRR, numAdditionalRR)

    # Query Construction
    question = b''

    for part in domain.split("."):
        question += (len(part).to_bytes(1, 'big')) + part.encode()
    question += struct.pack("!B", 0) + struct.pack("!HH", 1, 1)
    
    request = header + question
    
    return request

def recieveDNSResponse(recieve):
    ipList = []
    dnsTypeList = []
    
    # ignore the header, header is 12 bytes
    recieveCounter = 12
    query = ("1")
    
    # query is a tuple, so need to index
    while(query[0] != 0):
        query = struct.unpack("!B", recieve[recieveCounter : recieveCounter + 1])
        recieveCounter += 1

    # increment bytes for type and class
    recieveCounter += 4
    
    # parseNameOfNameServers is tuple
    parseNameOfNameServers = ("1")
    while recieveCounter < len(recieve):
        parseNameOfNameServers = struct.unpack("!B", recieve[recieveCounter : recieveCounter + 1])
        
        # Check if first two bits in string are 11 using int (11000000 == 192)
        if (parseNameOfNameServers[0] >= 192):
            recieveCounter += 2
        # Name of domain will be null terminated if full url is used
        else:
            while(parseNameOfNameServers[0] != 0):
                parseNameOfNameServers = struct.unpack("!B", recieve[recieveCounter : recieveCounter + 1])
                recieveCounter += 1
        
        dnsType, dnsClass = struct.unpack("!HH", recieve[recieveCounter : recieveCounter + 4])
        dnsTypeList.append(dnsType)
        recieveCounter += 4
        
        # time to live (TTL) is the next field, 4 bytes long but don't need
        recieveCounter += 4
        
        dnsDataLength = struct.unpack("!H", recieve[recieveCounter : recieveCounter + 2])
        recieveCounter += 2
        
        # A Type and IN Class
        if (dnsType == 1 and dnsClass == 1):
            # each section for IP is 1 byte, so use B
            ip = struct.unpack("!BBBB", recieve[recieveCounter : recieveCounter + 4])
            ipToString = ''
            for i in range(len(ip)):
                ipToString += str(ip[i])
                if i != len(ip) - 1:
                    ipToString += "."
            recieveCounter += 4
            ipList.append(ipToString)
            
        else:
            recieveCounter += dnsDataLength[0]
            
    return copy.deepcopy(ipList), copy.deepcopy(dnsTypeList)

def typesToString(typeList, name):
    listLength = len(typeList)
    string = f"There were {listLength} records in the {name}: \n"
    
    # translating list to DNS types talked about in the textbook + AAAA
    for element in range(listLength):
        typeName = "TYPE "
        if typeList[element] == 1:
            typeName += "A"
        elif typeList[element] == 2:
            typeName += "NS"
        elif typeList[element] == 5:
            typeName = "CNAME"
        elif typeList[element] == 15:
            typeName += "MX"
        elif typeList[element] == 28:
            typeName += "AAAA"
        else:
            typeName = ""
        string += typeName
        string += '\n'
        
    return string

def storeContents(fileName, content):
    # create a new file and store data
    with open(fileName, "w") as response_file:
        response_file.write(content)

def sendHTTPRequest(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcpSocket:
        tcpSocket.connect((ip, port))
        request = "GET / HTTP/1.1\r\n"
        request += "\r\n"
        
        startTime = time.time()
        tcpSocket.sendall(request.encode())

        response = ""
        while True:
            data = tcpSocket.recv(1024)
            if not data:
                endTime = time.time()
                tcpSocket.close()
                break
            response += data.decode()

        elapsedTime = (endTime - startTime) * 1000
        return response, elapsedTime

def sendAndRecieve(ip, dnsServer):
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = PacketConstruion(WEBSITE)
    
    startTime = time.time()
    
    udpSocket.sendto(message, (ip, DNSPORT))
    response, addr = udpSocket.recvfrom(1024)
    
    endTime = time.time()
    
    elapsedTime = (endTime - startTime) * 1000
    
    # IP is list of IP's, type is the list of DNS types from DNS Server
    IP, Type = recieveDNSResponse(response)
    storeContents(f"{dnsServer}ResponseTypes.txt", typesToString(Type, f"{dnsServer} DNS"))
    
    return IP, elapsedTime
    
    
def main():
    # returned IP's are lists
    tldIP, rootTime = sendAndRecieve(ROOTIP, "Root")
    authoritativeIP, tldTime = sendAndRecieve(tldIP[0], "TLD")
    websiteIP, authoritativeTime = sendAndRecieve(authoritativeIP[0], "Authoritative")

    response, httpTime = sendHTTPRequest(websiteIP[0], HTTPPORT)
    storeContents("httpRequest.html", response)
    
    timeString = f"Root RTT is {str(rootTime)} ms\n"
    timeString += f"TLD RTT is {str(tldTime)} ms\n"
    timeString += f"Authoratative RTT is {str(authoritativeTime)} ms\n"
    timeString += f"HTTP RTT is {str(httpTime)} ms\n"
    storeContents("RTT.txt", timeString)
    
if __name__ == "__main__":
    main()
    print("Done")
    




