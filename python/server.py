##############################################
##############################################
##                                          ##
##  Name: Brandon Burke                     ##
##                                          ##
##  Project Name: server.py                 ##
##                                          ##
##  Definition: this is a SMTP server       ##
##  which both takes a clients request      ##
##  to send an email to an authenticated    ##
##  user, or read their email.              ##
##                                          ##
##  Features:                               ##
##      TCP Multithreaded (write)           ##
##      UDP (read)                          ##
##      Authenticate Users                  ##
##      Base64 + salt Password Generator    ##
##      Write emails to file                ##
##      Send email data over udp            ##
##      Graceful exit                       ##
##                                          ##
##############################################
##############################################
from socket import *
from select import *
import sys
import os
import datetime
import _thread
import base64
import random
import string
import time

MAX = 1024 # 1KB
##########################
##  Bad Input Response  ##
##########################
if(len(sys.argv) != 3):
    print("\nUsage: python3 server.py <IP ADDRESS> <TCP PORT> <UDP PORT>")
    sys.exit(1)

####################################
##  TCP socket, bind, and listen  ##
####################################
tcp = socket(AF_INET, SOCK_STREAM)
print("\nTCP Binding\n")
TCP_ServerAddress = (sys.argv[1], int(sys.argv[2]))
tcp.bind(TCP_ServerAddress)
print("TCP Bound\n")
tcp.listen(5)

##############################
##  UDP socket, and bind    ##
##############################
udp = socket(AF_INET, SOCK_DGRAM)
print("\nUDP Binding\n")
UDP_ServerAddress = (sys.argv[1], int(sys.argv[3]))
udp.bind(UDP_ServerAddress)
print("UDP Bound\n")

######################
##  File Managment  ##
######################
CwdPath = os.getcwd()
path = os.path.join(CwdPath, r'db')
try:
    if(not os.path.exists(path)):
        os.mkdirs(path)
except Exception as e:
    print("Error: %" %e)
    sys.exit(1)

inputs = [tcp,udp]
outputs = []
while inputs:
    read = select(inputs, outputs, inputs)
    for s in read:
        ####################################
        ##  MultiThreaded SMTP over TCP   ##
        ####################################
        if(s == tcp):
            try:
                print("TCP Connecting\n")
                connection, client_address = s.accept()
                _thread.start_new_thread(SMTP, (connection,sys.argv[2]))
            except Exception as e:
                print("Error: %\n" %e)
                tcp.close()
                print("TCP Socket Closed\n")
                sys.exit(1)
        ######################
        ##  HTTP over UDP   ##
        ######################
        elif(s == udp):
            try:
                HTTP(sys.argv[3])
            except Exception as e:
                print("Error: %\n" %e)
                udp.close()
                print("UDP Socket Closed\n")
                sys.exit(1)
        else:
            print("Error: %s is not TCP or UDP\n" % s)
            tcp.close()
            udp.close()
            sys.exit(1)


################################
##  SMTP Email write Service  ##
################################
def SMTP(conn,tport):
    count = 0
    while True:
        command = conn.recv(MAX).decode().upper()
        if((command.find("HELO") == 0 ) and count == 0):
            count += 1
            responce = "250 OK"
            conn.send(responce.encode())
        elif((command.find("AUTH") == 0 ) and count == 1):
            count += 1
            ##########################
            ##  Request Username    ##
            ##########################
            response = AuthenticateEncode("334 username:")
            conn.send(responce.encode())
            ######################
            ##  Get Username    ##
            ######################
            username = conn.recv(MAX).decode()
            conn.send(responce.encode())
            ###########################
            ##  validate Username    ##
            ###########################
            if(validate(username)):
                ##########################
                ##  Request Password    ##
                ##########################
                response = AuthenticateEncode("334 password:")
                conn.send(responce.encode())
                ######################
                ##  get Username    ##
                ######################
                password = conn.recv(MAX).decode()
                if(not validate(password)):
                ##########################
                ##  Invalid Password    ##
                ##########################
                    while(validate(password)):
                        ##########################
                        ##  Request Password    ##
                        ##  and get Password    ##
                        ##########################
                        responce = AuthenticateEncode("535 re-enter password:")
                        conn.send(responce.encode())
                        password = conn.recv(MAX).decode()
            else:
                ##################
                ##  New User    ##
                ##################
                newpass = CreateUser(username)
                responce = "330 " + AuthenticateEncode(newpass)
                conn.send(response.encode())
                command = "NEW USER"
        elif((command.find("MAIL FROM") == 0 ) and count == 2):
            count += 1
        elif((command.find("RCPT TO") == 0 ) and count == 3):
            count += 1
        elif((command.find("DATA") == 0 ) and count == 4):
            count += 1
        elif(command.find("QUIT") == 0):
            conn.close()
        elif(command.find("NEW USER") == 0):
            time.sleep(5)
            count = 0
        else:
            count = 0
    return 0

###############################
##  HTTP Email read Service  ##
###############################
def HTTP(uport):
    return 0

######################################
##  Create user on first time login ##
##  call Generate Random Password   ##
##  write user to .user_pass file   ##
######################################
def CreateUser(user):
    print("Creating new user\n")
    password = ""
    try:
        userpassfile = open(".user-pass", "a+")
        password = PasswordGenerator()
        Euser = AuthenticateEncode(user)
        Epassword = AuthenticateEncode(password)
        userData = Euser + ":" + Epassword
        userpassfile.write(userData)
        userpassfile.write("\n")
    except Exception as e:
        print("Error: %" %e)
    return password

##############################
##  password generator      ##
##  create a 5 character    ## 
##  alphanumeric password   ##
##############################
def PasswordGenerator():
    password = ""
    for x in range(5):
        password += ''.join(random.choice(string.ascii_letters + string.digits))
    return password

##############################################
##  Validate user                           ##
##  compares userData to encodedUserData    ##
##  sets flag to True if successful compare ##
##  Euser = base64 encoded username         ##
##  Epassword = base64 encoded password     ##
##  userData = Euser:Epassword              ##
##############################################
def validate(user, password):
    flag = False
    Euser = AuthenticateEncode(user)
    Epassword = AuthenticateEncode(password)
    userData = Euser + ":" + Epassword
    with open(".user-pass", "r+") as f:
        for b64d in f:
            encodedUserData = b64d.readline()
            if(userData == encodedUserData):
                flag = True
            else:
                flag = False
    f.close()
    return flag
    
def validate(userData):
    flag = False
    with open(".user-pass", "r+") as f:
        for b64d in f:
            encodedUserData = b64d.readline()
            if(encodedUserData.find(userData) == 0):
                flag = True
            else:
                flag = False
    f.close()
    return flag
    
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
