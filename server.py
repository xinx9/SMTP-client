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
from threading import *
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
dbpath = os.path.join(os.getcwd(), r'db')
upf = (os.path.join(os.getcwd() + "/db/.user-pass"))
logs = (os.path.join(os.getcwd() + "/db/.server_log"))
try:
    if(not os.path.exists(dbpath)):
        os.makedirs(dbpath)
    if(not os.path.exists(upf)):
        f = open(upf, "a+")
        f.close()
    if(not os.path.exists(logs)):
        f = open(logs, "a+")
        f.close()
except Exception as e:
    print("Error: %s" %e)
    sys.exit(1)

##########################
##  Bad Input Response  ##
##########################
if(len(sys.argv) != 4):
    print("\nUsage: python3 server.py <IP ADDRESS> <TCP PORT> <UDP PORT>")
    sys.exit(1)

####################################
##  TCP socket, bind, and listen  ##
####################################
tcp = socket(AF_INET, SOCK_STREAM)
TCP_ServerAddress = (sys.argv[1], int(sys.argv[2]))
tcp.bind(TCP_ServerAddress)
tcp.listen(5)
##############################
##  UDP socket, and bind    ##
##############################
udp = socket(AF_INET, SOCK_DGRAM)
UDP_ServerAddress = (sys.argv[1], int(sys.argv[3]))
udp.bind(UDP_ServerAddress)


##############################
##  password generator      ##
##  create a 5 character    ## 
##  alphanumeric password   ##
##############################
def PasswordGenerator():
    password = ""
    for x in range(5):
        password += ''.join(random.choice(string.ascii_letters + string.digits))
    pw = AuthenticateEncode(password)
    pw = str(pw)
    return pw

######################################
##  Create user on first time login ##
##  call Generate Random Password   ##
##  write user to .user_pass file   ##
######################################
def CreateUser(user):
    try:
        filepath = os.getcwd() + "/db/.user-pass"
        userpassfile = open(filepath, "a+")
        password = PasswordGenerator()
        userData = user + " : " + password
        userpassfile.write(userData + "\n")
        userpassfile.close()
    except Exception as e:
        print("Error: %s" %e)
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
    if(os.path.exists((os.path.join(os.getcwd() + "/db/.user-pass")))):
        f = open((os.path.join(os.getcwd() + "/db/.user-pass")), "r+")
        udb64 = f.readline()
        while udb64:
            if(udb64.find(userData) == 0):
                flag = True
            else:
                flag = False
            udb64 = f.readline()
        f.close()
    return flag

def validateUser(username):
    flag = False
    if(os.path.exists((os.path.join(os.getcwd() + "/db/.user-pass")))):
        f = open((os.path.join(os.getcwd() + "/db/.user-pass")), "r+")
        user = f.readline()
        user = user.split(":")[0]
        while user:
            if(user.find(username) == 0):
                flag = True
            else:
                flag = False
            user = f.readline()
        f.close()
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
    Bin = Sin.encode("utf-8")
    Ein = base64.b64encode(Bin)
    Ein = str(Ein)
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
    return "%03d" %x

def logging(conn, protocol, command, response, description):
    log = (str(datetime.datetime.now()) + " | " +
            str(conn) + " | " + 
            command + " | " + 
            response + " | " + 
            description + "\n")
    print(log)
    return log
################################
##  SMTP Email write Service  ##
################################
def SMTP(conn,tport):
    count = 0
    serverlog = open(logs, "a+")
    while True:
        try:
            command = conn.recv(MAX).decode().upper()
        except Exception as e:
            print("\n")
        if((command == "HELO") and count == 0):
            response = "250 OK"
            conn.send(response.encode())
            serverlog.write(logging(conn, "SMTP", command,response, "HELO recieved"))
            count += 1
        elif((command == "AUTH") and count == 1):
            ##########################
            ##  Request Username    ##
            ##########################
            response = "334 username: "
            conn.send(response.encode())
            ######################
            ##  Get Username    ##
            ######################
            username = conn.recv(MAX).decode()
            ###########################
            ##  validate Username    ##
            ###########################
            flg = validateUser(username)
            if(flg):
                serverlog.write(logging(conn, "SMTP", command,response, "Username recieved: " + username))
                ##########################
                ##  Request Password    ##
                ##########################
                response = "334 password: "
                conn.send(response.encode())
                ######################
                ##  get Username    ##
                ######################
                password = conn.recv(MAX).decode()
                x = (username + " : " + password)
                dootyflag = validate(x)
                ##########################
                ##  Invalid Password    ##
                ##########################
                while(not dootyflag):
                    serverlog.write(logging(conn, "SMTP", command,response, "Password Invalid: " + password))
                    ##############################
                    ##  Request Valid Password  ##
                    ##  and validate Password   ##
                    ##############################
                    response = "535 re-enter password:"
                    conn.send(response.encode())
                    password = conn.recv(MAX).decode()
                    pwck = username + " : " + password
                    dootyflag = validate(pwck)
                serverlog.write(logging(conn, "SMTP", command,response, "Password recieved: " + password))
                response = "235"
                conn.send(response.encode())
                count += 1
            else:
                ##################
                ##  New User    ##
                ##################
                newpass = CreateUser(username)
                response = "330 " + newpass
                conn.send(response.encode())
                serverlog.write(logging(conn, "SMTP", command,response, "New User Created: " + username + " : " + newpass))
                count = 0
        elif((command.find("MAIL FROM") == 0 ) and count == 2):
            ##########################
            ##  Who is sending data ##
            ##########################
            EmailSend = command[10:len(command)]
            response = "250 OK"
            conn.send(response.encode())
            serverlog.write(logging(conn, "SMTP", command,response, "MAIL FROM recieved: " + EmailSend))
            count += 1
        elif((command.find("RCPT TO") == 0 ) and count == 3):
            ##########################
            ##  Who is getting data ##
            ##########################
            EmailRecv = command[8:len(command)]
            touser = EmailRecv.split("@")[0]
            try:
                CurrentDir = os.path.join(os.getcwd() + "/db/" + touser.upper())
                if(not os.path.exists(CurrentDir)):
                    os.makedirs(CurrentDir)
                    serverlog.write(logging(conn,"Server Command","200", CurrentDir + " CREATED"))
            except Exception as e:
                print("Error: %s" %e)
            response = "250 OK"
            conn.send(response.encode())
            serverlog.write(logging(conn, "SMTP", command,response, "RCPT TO recieved: " + EmailRecv))
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
                "\nSubject: " + body + "\n") 
                f.close()
            except Exception as e:
                print("Error: %s\n" %e)
            response = "250 OK"
            conn.send(response.encode())
            serverlog.write(logging(conn, "SMTP", command,response, "Email Written"))
            count = 2
        elif(command == "QUIT"):
            try:
                count = 0
                response = "221"
                conn.send(response.encode())
                serverlog.write(logging(conn, "SMTP", command,response, "User Disconected"))
            except Exception as e:
                print("\n")
        elif(command == "LOGOUT" and count >= 2):
            try:
                response = "220"
                conn.send(response.encode())
                serverlog.write(logging(conn, "SMTP", command,response, "User Logged Out"))
                count = 0
            except Exception as e:
                print("\n")
        elif(command == "HELO" and count == 1):
            try:
                response = "503 ALREADY HELO"
                conn.send(response.encode())
            except Exception as e:
                print("\n")
        elif(command == "LOGOUT" and count < 2):
            try:
                response = "504 NOT LOGGED IN"
                conn.send(response.encode())
            except Exception as e:
                print("\n")
        elif(command == "HELP"):
            try:
                response = "\nHELP\nQUIT\nLOGOUT\n1)HELO\n2)AUTH\n3)MAIL FROM:EMAIL@*.*\n4)RCPT TO:EMAIL@*.*\n5)DATA<CLRF>body<CLRF>.<CLRF>\n"
                conn.send(response.encode())
            except Exception as e:
                print("\n")
        elif(count == 1):
            try:
                count = 1
                response = "501 Invalid Command"
            except Exception as e:
                count = 1
        elif(count > 1):
            try:
                count = 2
                response = "502 Invalid Command"
                conn.send(response.encode())
            except Exception as e:
                count = 2
        elif(len(command) < 1):
            try:
                response = "500 Unknown Command"
                conn.send(response.encode())
                count = 0
            except Exception as e:
                count = 0
        else:
            try:
                response = "500 Unknown Command"
                conn.send(response.encode())
                count = 0
            except Exception as e:
                count = 0
    serverlog.close()

###############################
##  HTTP Email read Service  ##
###############################
def HTTP(uport):
    serverlog = open(logs, "a+")
    cready, caddr = udp.recvfrom(MAX)
    cready = cready.decode()
    if(cready == "200"):
        response = "200"
        udp.sendto(response.encode(),caddr)
        user, caddr = udp.recvfrom(MAX)
        user = user.decode()
        password, caddr = udp.recvfrom(MAX)
        password = password.decode()
        userData = user + " : " + password
        while(not validate(userData)):
            serverlog.write(logging(caddr,"HTTP",cready,response, "Login Failed: " + userData))
            response = "535"
            udp.sendto(response.encode(),caddr)
            user, caddr = udp.recvfrom(MAX)
            user = user.decode()
            password, caddr = udp.recvfrom(MAX)
            password = password.decode()
            userData = user + " : " + password
        response = "250 OK"
        udp.sendto(response.encode(),caddr)
        serverlog.write(logging(caddr,"HTTP",cready,response, "Login Recieved: " + userData))
        response = "250 Download"
        udp.sendto(response.encode(),caddr)
        serverlog.write(logging(caddr,"HTTP",cready,response, "User Downloading files"))
        getrequest, caddr = udp.recvfrom(MAX)
        getrequest = getrequest.decode()
        userpath = getrequest.split()[1]
        username = userpath.split("/")[2].upper()
        maildir = os.path.join(os.getcwd() + "/db/" + username)
        try:
            if(not os.path.exists(maildir)):
                response = "404: directory not found"
                udp.sendto(response.encode(), caddr)
                serverlog.write(logging(caddr,"HTTP",cready,response, "404: Directory not found"))
            else:
                files = os.listdir(maildir)
                files = sorted(files, reverse = True)
                i = 0
                while i < len(files):
                    mail = files[i]
                    filepath = os.path.join(maildir + "/" + mail)
                    mail = mail.split(".")[0]
                    mail = mail + ".txt"
                    f = open(filepath,"r")
                    message = f.read()
                    response = "250 File"
                    udp.sendto(response.encode(), caddr)
                    udp.sendto(mail.encode(), caddr)
                    response = "250 Msg"
                    udp.sendto(response.encode(), caddr)
                    message = getrequest + "\nContent-Type: text/plain\n\n" + message + "\n"
                    udp.sendto(message.encode(), caddr)
                    serverlog.write(logging(caddr,"HTTP",cready,response, "User Downloading: " + mail))
                    f.close()
                    i+=1
                response = "250 Downloaded"
                udp.sendto(response.encode(), caddr)
                serverlog.write(logging(caddr,"HTTP",cready,response, "User Finished Downloading Files"))
                modmessage = "New files Downloaded. Check contents in your current directory."
                udp.sendto(modmessage.encode(),caddr)
        except Exception as e:
            print("Error: %s" %e)
        
    serverlog.close()

input = [tcp,udp]
while True:
    serverlog = open(logs, "a+")
    inputready,outputready,exceptready = select(input,[],[])
    for s in inputready:
        if s == tcp:
            connection, client_address = s.accept()
            serverlog.write(logging(connection,"TCP","","200","TCP Connection"))
            _thread.start_new_thread(SMTP, (connection,sys.argv[2]))
            serverlog.close()
        elif s == udp:
            serverlog.write(logging(connection,"UDP","","200","UDP Connection"))
            threadUDP = Thread(target = HTTP(sys.argv[3]))
            threadUDP.start()
            serverlog.close()
        else:
            print ("unknown socket:", s)
