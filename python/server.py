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

MAX = 2048 # 2KB

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


################################
##  SMTP Email write Service  ##
################################
def SMTP(conn,tport):
    count = 0
    while True:
        command = conn.recv(MAX).decode().upper()
        if((command == "HELO") and count == 0):
            response = "250 OK"
            conn.send(response.encode())
            count += 1
        elif((command == "AUTH") and count == 1):
            ##########################
            ##  Request Username    ##
            ##########################
            response = "334 username:"
            conn.send(response.encode())
            ######################
            ##  Get Username    ##
            ######################
            username = conn.recv(MAX).decode()
            ###########################
            ##  validate Username    ##
            ###########################
            if(validate(username)):
                ##########################
                ##  Request Password    ##
                ##########################
                response = "334 password:"
                conn.send(response.encode())
                ######################
                ##  get Username    ##
                ######################
                password = conn.recv(MAX).decode()
                if(not validate(password)):
                ##########################
                ##  Invalid Password    ##
                ##########################
                    while(not validate(password)):
                        ##############################
                        ##  Request Valid Password  ##
                        ##  and validate Password   ##
                        ##############################
                        response = "535 re-enter password:"
                        conn.send(response.encode())
                        password = conn.recv(MAX).decode()
                response = "235 AUTH OK"
                conn.send(response.encode())
                count += 1
            else:
                ##################
                ##  New User    ##
                ##################
                newpass = CreateUser(username)
                response = "330 " + AuthenticateEncode(newpass)
                conn.send(response.encode())
                count = 0
        elif((command.find("MAIL FROM") == 0 ) and count == 2):
            ##########################
            ##  Who is sending data ##
            ##########################
            EmailSend = command[10:len(command)]
            response = "250 OK"
            conn.send(response.encode())
            count += 1
        elif((command.find("RCPT TO") == 0 ) and count == 3):
            ##########################
            ##  Who is getting data ##
            ##########################
            EmailRecv = command[8:len(command)]
            touser = EmailRecv.split("@")
            try:
                CurrentDir = os.path.join(path + "/" + touser[0])
                if(not os.path.exists(CurrentDir)):
                    os.makedirs(CurrentDir)
            except Exception as e:
                print("Error: %s" %e)
            response = "250 OK"
            conn.send(response.encode())
            count += 1
        elif((command == "DATA") and count == 4):
            response = '354 Send message content; End with <CLRF>.<CLRF>'
            conn.send(response.encode())
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
            date = "Date: {:%A %d %m %Y %H:%M:%S}".format(datetime.datetime.now())
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
            count += 1
        elif(command == "QUIT"):
            count = 0
            response = "221"
            conn.send(response.encode())
            conn.close()
        elif(count > 1):
            count = 2
            response = "501 Invalid Command"
            conn.send(response.encode())
        else:
            count = 0
    return 0

###############################
##  HTTP Email read Service  ##
###############################
def HTTP(uport):
    cready, caddr = udp.recvfrom(MAX)
    if(cready.find("200 Ready")):
        response = "200"
        udp.sendto(response.encode(),caddr)
        user, caddr = udp.recvfrom(MAX)
        user = user.decode()
        password, caddr = udp.recvfrom(MAX)
        password = password.decode()
        userData = user + ":" + password
        if(validate(userData)):
            response = "250 OK"
            udp.sendto(response.encode,caddr)
        elif(not validate(userData)):
            while(not validate(userData)):
                response = "535"
                udp.sendto(response.encode(),caddr)
                user, caddr = udp.recvfrom(MAX)
                user = user.decode()
                password, caddr = udp.recvfrom(MAX)
                password = password.decode()
                userData = user + ":" + password
            response = "250 OK"
            udp.sendto(response.encode,caddr)
    else:
        getrequest, caddr = udp.recvfrom(MAX)
        getrequest = getrequest.decode()
        userpath = getrequest.split()[1]
        maildir = os.path.join(os.getcwd() + userpath)
        try:
            if(not os.path.exists(maildir)):
                response = "404: directory not found"
                udp.sendto(response.encode(), caddr)
            else:
                response = "250 Download"
                files = os.listdir(maildir)
                files = sorted(files, reverse = True)
                curdir = os.getcwd()
                i = 0
                while i < len(files):
                    mail = files[i]
                    filepath = os.path.join(maildir + "/" + mail)
                    mail = mail.split(".")[0]
                    mail = mail + ".txt"
                    f = open(filepath,"r")
                    message = f.read(MAX)
                    response = "250 File"
                    upd.sendto(mail.encode(), caddr)
                    udp.sendto(response.encode(), caddr)
                    while(message):
                        response = "250 Msg"
                        message = getrequest + "\n" + message
                        if(udp.sendto(message.encode(), caddr)):
                            message = f.read(MAX)
                            time.sleep(0.02)
                    f.close()
                    i+=1
                response = "250 Downloaded"
                udp.sendto(response.encode(), caddr)
        except Exception as e:
            print("Error: %s" %e)
        modmessage = "New file Received. Check contents in your directory."
        udp.sendto(modmessage.encode(),caddr)

######################################
##  Create user on first time login ##
##  call Generate Random Password   ##
##  write user to .user_pass file   ##
######################################
def CreateUser(user):
    print("Creating new user\n")
    password = ""
    try:
        userpassfile = open(os.getcwd() + "/db/.user-pass", "a+")
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
##  userData = Euser:Epassword              ##
##  udb64 = User Data Base64                ##
##############################################
def validate(userData):
    flag = False
    with open(".user-pass") as f:
        udb64 = f.readline()
        while udb64:
            if(udb64.find(userData) == 0):
                flag = True
            else:
                flag = False
        udb64 = f.readline()
    return flag
    
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
    Bin = Sin.decode("utf-8")
    Ein = base64.b64encode(Bin)
    return Ein

def AuthenticateDecode(Ein):
    salt = "447"
    Ein = Ein[2:-1]
    Sin = base64.b64decode(Ein)
    Sin = Sin.decode("utf-8")
    Cin = Sin[:len(Sin)-3]
    return Cin

def strinc(x):
    x = int(x) + 1
    return "%03d" %num

while inputs:
    read = select([tcp,udp], [], [])
    for s in read:
        ####################################
        ##  MultiThreaded SMTP over TCP   ##
        ####################################
        if(read[0]):
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
        elif(read[1]):
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

