##############################################
##############################################
##                                          ##
##  Name: Brandon Burke                     ##
##                                          ##
##  Project Name: client.py                 ##
##                                          ##
##  Description: this program uses smtp     ##
##  over TCP to send an email to another    ##
##  authenticated user on the server        ##
##  this program also uses HTTP over UDP    ##
##  to read the users email                 ##
##                                          ##
##  Features:                               ##
##      login                               ##
##      write to server (TCP)               ##
##      read from server (UDP)              ##
##                                          ##
##############################################
##############################################
from socket import *
from threading import *
from select import select
import sys
import os
import datetime
import time
import _thread
import base64
MAX = 1024
if(len(sys.argv) != 3):
    print("\n> python3 server.py <HOST NAME> <PORT NUMBER>")
    sys.exit(1)

##############################################
##  Encode/Decode text input with base64    ##
##  Cin = clear text input                  ## 
##  Sin = salted input                      ##   
##  Ein = encoded input                     ##  
##  Bin = binary input                      ##   
##############################################
def AuthenticateEncode(Cin):
    salt = "447"
    Sin = Cin + salt
    Bin = Sin.encode("utf-8")
    Ein = base64.b64encode(Bin)
    return Ein

def AuthenticateDecode(Ein):
    salt = "447"
    Ein = Ein[2:-1]
    Sin = base64.b64decode(Ein)
    Sin = Sin.decode("utf-8")
    Cin = Sin[:len(Sin)-3]
    return Cin

######################################
##  Initialize Server Connection    ##
######################################
print("Would you like to send or recieve?")
sendOrRecieve = input(">").upper()
if(sendOrRecieve.find("SEND") == 0):
    TCP_ServerAddr = (sys.argv[1], int(sys.argv[2]))
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(TCP_ServerAddr)
    ##################
    #TCP interaction
    ##################
    while True:
        #--------------------------------------------#
        cmsg = input(">")
        if(len(cmsg) == 0):
            while(len(cmsg) < 1):
                print("Please enter a command\n")
                cmsg = input(">")
        
        clientSocket.send(cmsg.encode())
        smsg = clientSocket.recv(MAX).decode()
        
        if(smsg.find("221") == 0):
            print(smsg)
            clientSocket.close()
            sys.exit()
        elif(smsg.find("334 username:") == 0):
            user = input(smsg)
            Euser = AuthenticateEncode(user)
            clientSocket.send(str(Euser).encode())
            smsg = clientSocket.recv(MAX).decode()
            if(smsg.find("334") == 0 or smsg.find("535") == 0):
                while(smsg != "235"):
                    password = input(smsg)
                    Epassword = AuthenticateEncode(password)
                    clientSocket.send(str(Epassword).encode())                    
                    smsg = clientSocket.recv(MAX).decode()
            elif(smsg.find("330") == 0):
                x = AuthenticateDecode(smsg.split()[1])
                print("your password is: " + x)
                #time.sleep(5)
            else:
                print(smsg)
        elif(smsg.find("354 Send message content; End with <CLRF>.<CLRF>") == 0):
            print(smsg)
            datamsg = []
            i = 0
            while True:
                data = input()
                if data == '.':
                    datamessage = "\n".join(datamsg)
                    clientSocket.send(datamessage.encode())
                    break
                else:
                    datamsg.append(data)
            print(clientSocket.recv(MAX).decode())
        else:
            print(smsg)
        #--------------------------------------------#    
    clientSocket.close()
    sys.exit()
#########################################
elif(sendOrRecieve.find("RECIEVE") == 0):
    UDP_ServerAddr = (sys.argv[1], int(sys.argv[2]))
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    init = "200"
    clientSocket.sendto(init.encode(), UDP_ServerAddr)
    auth , saddr = clientSocket.recvfrom(MAX)
    if(auth.decode() == "200"):
        username = input("username: ")
        password = input("password: ")
        Eusername = AuthenticateEncode(username)
        clientSocket.sendto(str(Eusername).encode(), UDP_ServerAddr)
        Epassword = AuthenticateEncode(password)
        clientSocket.sendto(str(Epassword).encode(), UDP_ServerAddr)
        valid, saddr = clientSocket.recvfrom(MAX)
        if(valid.decode() == "250 OK"):
            print(valid.decode() + " Login Successful")
        elif(valid.decode() == "535"):
            while(valid.decode() != "250 OK"):
                print("Invalid Credentials please Re-enter:\n")
                username = input("username: ")
                password = input("password: ")
                Eusername = AuthenticateEncode(username)
                clientSocket.sendto(str(Eusername).encode(), UDP_ServerAddr)
                Epassword = AuthenticateEncode(password)
                clientSocket.sendto(str(Epassword).encode(), UDP_ServerAddr)
                valid , saddr = clientSocket.recvfrom(MAX)
            print(valid.decode() + " Login Successful")
    data , saddr = clientSocket.recvfrom(MAX)
    data = data.decode()
    if(data == "250 Download"):
        message = "GET /db/" + username.upper() + "/ HTTP/1.1\nHost: " + sys.argv[1]
        clientSocket.sendto(message.encode(),UDP_ServerAddr)
        while(not data == "250 Downloaded"):
            data , saddr = clientSocket.recvfrom(MAX)
            data = data.decode()
            if(data == "250 File"):
                filename , saddr = clientSocket.recvfrom(MAX)
                filename.decode()
                f = open(filename, "a+")
            elif(data == "250 Msg"):
                servermessage , saddr = clientSocket.recvfrom(MAX)
                servermessage = servermessage.decode()
                f.write(servermessage)
        end, saddr = clientSocket.recvfrom(MAX)
        print(end.decode())
        sys.exit()
    elif(data == "404: directory not found"):
        print(data)
        sys.exit()
else:
    print("invalid selection")
    sys.exit()