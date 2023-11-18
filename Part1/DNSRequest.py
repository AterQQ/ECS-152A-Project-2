import socket
import random
import struct
import time

ROOTIP = "199.9.14.201"
DNSPORT = 53
WEBSITE = "tmz.com"

def PacketConstruion(domain):
    id = random.randint(1, 65536)
    flags = 0
    numQuestions = 1
    numAnswerRR = 0
    numAuthorityRR = 0
    numAdditionalRR = 0

    header = struct.pack("!HHHHHH", id, flags, numQuestions, numAnswerRR, numAuthorityRR, numAdditionalRR)

    question = b''

    for part in domain.split("."):
        question += (len(part).to_bytes(1, 'big')) + part.encode()
    question += struct.pack("!B", 0) + struct.pack("!HH", 1, 1)

    # print(header, "Question is", question)
    request = header + question
    # print("Total string is", request)
    return request

def recieveDNSResponse(socket):
    recieve, addr = socket.recvfrom(1024)
    id, flags, questions, answerRR, authorityRR, additionalRR = struct.unpack("!HHHHHH", recieve[0:12])
    
    recieveCounter = 12
    query = ("1")
    
    # query is a tuple, so need to index
    while(query[0] != 0):
        query = struct.unpack("!B", recieve[recieveCounter : recieveCounter + 1])
        recieveCounter += 1

    # increment bytes for type and class
    ntype, nclass = struct.unpack("!HH", recieve[recieveCounter : recieveCounter + 4])
    # print("Type and class are ", ntype, nclass)
    recieveCounter += 4

    totalRR = answerRR + authorityRR + additionalRR
    
    # parseNameOfNameServers is tuple, which is needed to unpack
    parseNameOfNameServers = ("1")
    for answer in range(totalRR):
        parseNameOfNameServers = struct.unpack("!B", recieve[recieveCounter : recieveCounter + 1])
        # print((parseNameOfNameServers[0]))
        
        # Check if first two bits in string are 11 using int (11000000 == 192)
        if (parseNameOfNameServers[0] >= 192):
            recieveCounter += 2
        # Name of domain will be null terminated if full url is used
        else:
            while(parseNameOfNameServers[0] != 0):
                parseNameOfNameServers = struct.unpack("!B", recieve[recieveCounter : recieveCounter + 1])
                # print("Name servers:", parseNameOfNameservers)
                recieveCounter += 1
        
        dnsType, dnsClass = struct.unpack("!HH", recieve[recieveCounter : recieveCounter + 4])
        # print("DNS type and class:", dnsType, dnsClass)
        recieveCounter += 4
        
        # time to live (TTL) is the next field, 4 bytes long but don't need
        recieveCounter += 4
        
        dnsDataLength = struct.unpack("!H", recieve[recieveCounter : recieveCounter + 2])
        # print("Data len", dnsDataLength[0])
        recieveCounter += 2
        
        # A Type and IN Class
        if (dnsType == 1 and dnsClass == 1):
            ip = struct.unpack("!BBBB", recieve[recieveCounter : recieveCounter + 4])
            ipToString = ''
            for i in range(len(ip)):
                ipToString += str(ip[i])
                if i != len(ip) - 1:
                    ipToString += "."
            # print(ipToString)
            return ipToString
        else:
            recieveCounter += dnsDataLength[0]
        # print("Iterator at ", answer + 1)

def send_http_request_tcp_by_ip(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcpSocket:
        tcpSocket.connect((ip, port))
        tcpSocket.settimeout(3)

        request = f"GET / HTTP/1.1\r\nHost: {ip}\r\n\r\n"
        
        tcpSocket.sendall(request.encode())

        response = ""
        try:
            while True:
                data = tcpSocket.recv(1024).decode()
                if not data:
                    tcpSocket.close()
                    break
                response += data
        except socket.timeout:
            pass

        return response
    
def main():
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = PacketConstruion(WEBSITE)
    udpSocket.sendto(message, (ROOTIP, DNSPORT))

    tldIP = recieveDNSResponse(udpSocket)
    udpSocket.sendto(message, (tldIP, DNSPORT))

    authoratativeIP = recieveDNSResponse(udpSocket)
    udpSocket.sendto(message, (authoratativeIP, DNSPORT))

    ip = recieveDNSResponse(udpSocket)
    print(WEBSITE, "IP is", ip)

    response = send_http_request_tcp_by_ip(ip, 80)
    
    print(response)

    # Uncomment to export to file
    # with open("Response.txt", "w") as response_file:
    #     response_file.write(response)
    
if __name__ == "__main__":
    main()
    




