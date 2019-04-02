import os, sys

# Open a file
path = os.getcwd()
dirs = os.listdir( path )

# This would print all the files and directories
print(dirs)

db = os.path.join(path + "/db/" + "rabbit")

dbdir = os.listdir(db)
print(dbdir)
db = os.path.join(db+ "/" + dbdir[0])
print(db)
with open(db) as fp: 
    line = fp.readline()
    while line:
        print(line)
        line = fp.readline()

