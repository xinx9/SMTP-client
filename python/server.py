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

######################
##  File Managment  ##
######################
path = os.path.join(os.getcwd(), r'db')
try:
    if(not os.path.exists(path)):
        os.mkdirs(path)
except Exception as e:
    print("Error: %s" %e)
    sys.exit(1)


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
                print("Error: %s\n" %e)
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
                print("Error: %s\n" %e)
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
            response = "250 OK"
            conn.send(response.encode())
        elif((command.find("AUTH") == 0 ) and count == 1):
            count += 1
            ##########################
            ##  Request Username    ##
            ##########################
            response = AuthenticateEncode("334 username:")
            conn.send(response.encode())
            ######################
            ##  Get Username    ##
            ######################
            username = conn.recv(MAX).decode()
            conn.send(response.encode())
            ###########################
            ##  validate Username    ##
            ###########################
            if(validate(username)):
                ##########################
                ##  Request Password    ##
                ##########################
                response = AuthenticateEncode("334 password:")
                conn.send(response.encode())
                ######################
                ##  get Username    ##
                ######################
                password = conn.recv(MAX).decode()
                if(not validate(password)):
                ##########################
                ##  Invalid Password    ##
                ##########################
                    while(validate(password)):
                        ##############################
                        ##  Request Valid Password  ##
                        ##  and validate Password   ##
                        ##############################
                        response = AuthenticateEncode("535 re-enter password:")
                        conn.send(response.encode())
                        password = conn.recv(MAX).decode()
                response = "235 AUTH OK"
                conn.send(response.encode())
            else:
                ##################
                ##  New User    ##
                ##################
                newpass = CreateUser(username)
                response = "330 " + AuthenticateEncode(newpass)
                conn.send(response.encode())
                count = 2501
        elif(count == 2501):
            time.sleep(5)
            count = 0
        elif((command.find("MAIL FROM") == 0 ) and count == 2):
            count += 1
            ##########################
            ##  Who is sending data ##
            ##########################
            EmailSend = command[10:len(command)]
            response = "250 OK"
            conn.send(response.encode())
        elif((command.find("RCPT TO") == 0 ) and count == 3):
            count += 1
            ##########################
            ##  Who is getting data ##
            ##########################
            EmailRecv = command[8:len(command)]
            rcpt = EmailRecv.split("@")
            try:
                CurrentDir = os.path.join(path + "/" + rcpt[0])
                if(not os.path.exists(CurrentDir)):
                    os.makedirs(CurrentDir)
            except Exception as e:
                print("Error: %s" %e)
            response = "250 OK"
            conn.send(response.encode())
        elif((command.find("DATA") == 0 ) and count == 4):
            count += 1
            modfiles = 0
            dirListing = os.listdir(CurrentDir)
            if(len(dirListing) != 0):
                for f in dirListing:
                    mtime = os.path.getmtime(CurrentDir)
                    if mtime > modfiles:
                        filename = f
                    fns = filename.split(".")
                    EmailFile = strinc(fns[0]) + "." + fns[1]
            else:
                EmailFile = "001.email"            
            date = "Date: {: %A %d %m %Y %H:%M:%S}".format(datetime.datetime.now())
            body = "Subject: "
            data = conn.recv(MAX).decode()
            body = data
            filepath = os.path.join(CurrentDir, EmailFile)
            try:
                f = open(filepath, "a+")
                f.write(date + 
                "\nFrom: " + EmailSend + 
                "\nTo: " + EmailRecv + 
                "\nSubject: " + body) 
                f.close()
            except Exception as e:
                print("Error: %s\n" %e)
            response = "250 OK"
            conn.send(response.encode())
        elif(command.find("QUIT") == 0):
            respone = "421 GOOD BYE"
            conn.send(respone.encode())
            conn.close()
        elif(command.find("HELP") == 0):
            response = "HELP FILE"
            conn.send(respone.encode())
        elif(count > 1):
            count = 2
            response = "501"
            conn.send(respone.encode())
        else:
            count = 0
    return 0

###############################
##  HTTP Email read Service  ##
###############################
def HTTP(uport):
    message, caddr = udp.redvfrom(MAX)
    modmessage = message.decode().upper()
    if(modmessage.find("GET") == 0):
        user = modmessage.split("/")[2]
        count = modmessage.split("COUNT:")
        count = int(count[1])
        maildir = os.path.join(os.getcwd + "/db/" + user)
        try:
            if(not os.path.exists(maildir)):
                response = "404: directory not found"
                udp.sendto(response.encode(), caddr)
            else:
                files = os.listdir(maildir)
                files = sorted(files)
                files = reversed(files)
                files = list(files)
                curdir = os.getcwd()
                i = 0
                while i < count and count < len(files):
                    message = ""
                    mail = files[i]
                    filepath = os.path.join(maildir,mail)
                    f = open(filepath,"r")
                    mesage = f.read()
                    f.close()
                    mail = mail.split(".")[0]
                    mail = mail + ".txt"
                    storepath = os.path.join(curdir,mail)
                    m = open(storepath, "a+")
                    m.write(message)
                    m.close()
                    i+=1
        except Exception as e:
            print("Error: %s" %e)
    else:
        print("invalid GET request")
        modmessage = "Check current directory for text files"
        udp.sendto(modmessage.encode(),caddr)
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
        userpassfile = open(path + "/.user-pass", "a+")
        password = PasswordGenerator()
        Euser = AuthenticateEncode(user)
        Epassword = AuthenticateEncode(password)
        userData = Euser + ":" + Epassword
        userpassfile.write(userData)
        userpassfile.write("\n")
    except Exception as e:
        print("Error: %s" %e)
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
""" def validate(user, password):
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
     """
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

def strinc(x):
    x = int(x) + 1
    return "%03d" %num