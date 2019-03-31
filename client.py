##############################################
##############################################
##                                          ##
##  Name: Brandon Burke                     ##
##                                          ##
##  Project Name: client.py                 ##
##                                          ##
##  Class: 447-001                          ##
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
TCP_ClientAddress = (sys.argv[1], int(sys.argv[2]))
#UPORT = sys.argv[3]
if(len(sys.argv) != 3):
    print("\n> python3 server.py <IP ADDRESS> <TCP PORT> <UDP PORT>")
    sys.exit(1)

tcp = socket(AF_INET, SOCK_STREAM)
tcp.connect(TCP_ClientAddress)
while True:
    msg = input()
    tcp.send(msg.encode())
tcp.close()