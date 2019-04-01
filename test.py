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
current_directory = os.path.join(os.getcwd(), r'db')
try:
    print("created: %s" % current_directory)
    if not os.path.exists(current_directory):
        os.makedirs(current_directory)
except Exception as e:
    print("Error: %s", e) 

rcpt = "RCPT TO:rabbit@junk.com"
email = rcpt[8:len(rcpt)]
username = email.split("@")

newdir = os.path.join(current_directory + "/" + username[0])

if(not os.path.exists(newdir)):
    os.makedirs(newdir)

f = open(newdir + "/test.txt", "a+")
f.write("\nwhat doesn't kill you will make you a killer\n")






f.close()



