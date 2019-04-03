import socket
import sys

TCP_IP = "127.0.0.1"
FILE_PORT = 5005
DATA_PORT = 5006
buf = 1024
#file_name = sys.argv[1]


try:
#    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while(True):
        file_name = input()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((TCP_IP, DATA_PORT))
        except Exception as e:
            print(e)
        finally:
            print("\n")
        sock.send(file_name.encode())
        print( "Sending %s ..." % file_name)

        f = open(file_name, "r")
        data = f.read()
        f.close()
        sock.send(data.encode())
 
        sock.close()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((TCP_IP, DATA_PORT))
        except Exception as e:
            print(e)
finally:
    print("bye")
