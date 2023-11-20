import socket
import struct
import random
import time

def build_dns_query(domain):
    transaction_id = random.randint(0, 65535)  # 16-bit transaction ID
    flags = 0x0000  # Standard query with recursion desired

    query = struct.pack('!HHHHHH', transaction_id, flags, 1, 0, 0, 0)  # Header section

    # Question section: specify the domain to query
    domain_parts = domain.split('.')
    query += b''.join(struct.pack('B', len(part)) + part.encode() for part in domain_parts)
    query += b'\x00'  # End of domain name
    query += struct.pack('!H', 1)  # QTYPE: A record (IPv4 address)
    query += struct.pack('!H', 1)  # QCLASS: IN class

    return query

def send_dns_query(query, dns_server):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        start_time = time.time()
        s.sendto(query, (dns_server, 53))  # Send DNS query to DNS server
        response, _ = s.recvfrom(1024)  # Receive DNS response
        stop_time = time.time()
        elapsed_time = stop_time - start_time
        return response, elapsed_time

def parse_dns_response(response):
    _, flags, _, answer_count, auth_count, additional_count = struct.unpack('!HHHHHH', response[:12])
    
    if flags & 0x8000:  # Check if it's a response
        offset = 12
        
        query = ("1")
    
        # Added code from our implementation
        while(query[0] != 0):
            query = struct.unpack("!B", response[offset : offset + 1])
            offset += 1
        query_type, query_class = struct.unpack("!HH", response[offset:offset+4])
        offset += 4
        # End added code
        
        parsed_records = []
        
        while offset < len(response):
            name, qtype, qclass, ttl, data_len = struct.unpack('!HHHLH', response[offset:offset + 12])
            offset += 12
            
            if qtype == 1:  # A record type
                ip_address = socket.inet_ntoa(response[offset:offset + 4])
                parsed_records.append(("A", ip_address))
            elif qtype == 28:  # AAAA record type (IPv6)
                ip_address = socket.inet_ntop(socket.AF_INET6, response[offset:offset + 16])
                parsed_records.append(("AAAA", ip_address))
            # You can add more record types here
            
            offset += data_len
        
        return parsed_records

    return None

def http_get_request(host, port, path="/"):
    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
    elapsed_time = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        end_time = 0
        start_time = time.time()
        s.sendall(request.encode())

        response = b""
        while True:
            data = s.recv(1024)
            if not data:
                end_time = time.time()
                break
            response += data
        elapsed_time = end_time - start_time
    return response.decode("utf-8"), elapsed_time

# Moved printing records to a function
def parse_records(parsed_records, dnsName, time):
    if parsed_records:
        print(f"{dnsName} records:\n")
        for record_type, record_data in parsed_records:
            print(f"DNS Type: {record_type}")
            print(f"IP Address: {record_data}")
            print("----")
        print(f"{dnsName} time was {time * 1000} ms\n\n\n")
        return parsed_records[0][1]
    else:
        print("No relevant records found in the DNS response for the given domain.")

if __name__ == "__main__":
    domain_to_query = "tmz.com"
    dns_server_ip = "199.9.14.201"
    host = "tmz.com"
    port = 80  # Standard HTTP port

    dns_query = build_dns_query(domain_to_query)
    dns_response_root, root_time = send_dns_query(dns_query, dns_server_ip)
    
    # Added code
    parsed_records_root = parse_dns_response(dns_response_root)
    
    tld_ip = parse_records(parsed_records_root, "ROOT DNS", root_time)
    dns_response_tld, tld_time = send_dns_query(dns_query, tld_ip)
    parsed_records_tld = parse_dns_response(dns_response_tld)
    
    authoratative_ip = parse_records(parsed_records_tld, "TLD DNS", tld_time)
    dns_response_auth, auth_time = send_dns_query(dns_query, authoratative_ip)
    parsed_records_auth = parse_dns_response(dns_response_auth)
    
    website_ip = parse_records(parsed_records_auth, "AUTHORATATIVE DNS", auth_time)
    # End added code
    
    http_response, http_time = http_get_request(website_ip, port)
    
    print("HTTP Response Time:", http_time, "\n\n\n")
    print("HTTP Response:\n")
    print(http_response)
    
    

