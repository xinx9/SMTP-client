##############################################
##############################################
##                                          ##
##  Name: Brandon Burke                     ##
##                                          ##
##  Project Name: server.py                 ##
##                                          ##
##  Class: 447-001                          ##
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

MAX = 1024 # 1KB
##########################
##  Bad Input Response  ##
##########################
if(len(sys.argv) != 3):
    print("\n> python3 server.py <IP ADDRESS> <TCP PORT> <UDP PORT>")
    sys.exit(1)

######################
##  File Managment  ##
######################
CwdPath = os.getcwd()
path = os.path.join(CwdPath, r'db')
try:
    if(not os.path.exists(path)):
        os.mkdirs(path)
    os.chdir(path)
except Exception as e:
    print("Error: %" %e)
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
    return 0

###############################
##  HTTP Email read Service  ##
###############################
def HTTP(uport):
    return 0

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

######################################
##  Create user on first time login ##
##  call Generate Random Password   ##
##  write user to .user_pass file   ##
######################################
def CreateUser(user):
    print("Creating new user\n")
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
    