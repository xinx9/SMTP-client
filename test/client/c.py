import socket
import select
import os, sys
UDP_IP = "127.0.0.1"
IN_PORT = 5005
timeout = 3


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, IN_PORT))

while True:
    datae, addr = sock.recvfrom(1024)
    data = datae.decode()
    if data:
        print( "File name:", data)
        file_name = data.strip()

    f = open(file_name, 'w+')

    while True:
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            datae, addr = sock.recvfrom(1024)
            data = datae.decode()
            f.write(data)
        else:
            print( "%s Finish!" % file_name)
            f.close()
            break
