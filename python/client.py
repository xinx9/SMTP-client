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
import _thread

MAX = 1024
if(len(sys.argv) != 3):
    print("\n> python3 server.py <HOST NAME> <PORT NUMBER>")
    sys.exit(1)


TCP_ServerAddr, UDP_ServerAddr = (sys.argv[1], int(sys.argv[2]))

######################################
##  Initialize Server Connection    ##
######################################
print('Would you like to send or recieve?')
sendOrRecieve = input().upper()
if(sendOrRecieve.find('SEND') == 0):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(TCP_ServerAddr)
    ##################
    #TCP interaction
    ##################
    while 1:
        cmsg = input()
        clientSocket.send(cmsg.encode())
        smsg = clientSocket.re
        userData = ""cv(MAX).decode()
        if(smsg.find("221 Bye") == 0):
            print(smsg)
            sys.exit()
        elif(smsg.find("334 username") == 0):
            print(smsg)
            user = input()
            Euser = AuthenticateEncode(user)
            clientSocket.send(Euser.decode())
        elif(smsg.find("334 password") == 0 or smsg.find("535 reEnter password") == 0):
            print(smsg)
            password = input()
            Epassword = AuthenticateEncode(password)
            clientSocket.send(Epassword)
        elif(smsg.find("354 Send message content; End with <CLRF>.<CLRF>") == 0):
            print(smsg)
            datamsg = []
            i = 0
            while True:
                data = input()
                if data == '.':
                    datamessage = '\n'.join(datamsg)
                    clientSocket.send(datamessage.encode())
                    break
                else:
                    datamsg.append(data)
        else:
            print(smsg)
    clientSocket.close()

elif(sendOrRecieve.find('RECIEVE') == 0):
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    init = "200 Ready"
    clientSocket.sendto(init.encode(), UDP_ServerAddr)
    data = clientSocket.recvfrom(MAX)
    if(data.find("334"))
        lines = []
        while True:
            line = input()
            if line:
                lines.append(line)
            else:
                break
        message = '\n'.join(lines)
        print(message)
        clientSocket.sendto(message.encode(),UDP_ServerAddr)
        modifiedMessage = clientSocket.recvfrom(MAX)
        print(modifiedMessage.decode())
        sys.exit()
else:
    print('invalid selection')

######################################################
##  Authenticate clear text input with base64       ##
##  Cin = clear text input                          ##
##  Sin = salted input                              ##
##  Ein = encoded input                             ##
######################################################
def AuthenticateEncode(Cin):
    salt = "447"
    Sin = Cin + salt
    Ein = base64.b64encode(Sin)
    return Ein

######################################################
##  Authenticate encoded input with base64          ##
##  Cin = clear text input                          ##
##  Sin = salted input                              ##
##  Ein = encoded input                             ##
######################################################
def AuthenticateDecode(Ein):
    salt = "447"
    Sin = base64.b64decode(Ein)
    Cin = string.replace(salt, "")
    return Cin
