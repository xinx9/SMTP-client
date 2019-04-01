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
current_directory = os.getcwd()
final_directory = os.path.join(current_directory, r'db')
print("created: %s" % final_directory)
if not os.path.exists(final_directory):
   os.makedirs(final_directory)
a = "a"
newdir = os.path.join(current_directory + "/db/" + a)
print("created: %s" %newdir)
os.makedirs(newdir)

filename = newdir + "/test.txt"
f = open(filename, "a+")
f.write("\nwhat it do bruh\n")
