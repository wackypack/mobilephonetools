import tkinter as tk
from tkinter import filedialog
import os
from os.path import dirname, basename, splitext, getsize, isdir, join

root = tk.Tk()
root.withdraw()

filePath=filedialog.askopenfilename()
file=open(filePath, mode="rb")
size=getsize(filePath)
outDir=dirname(filePath)

Mod=file.read()

if Mod[0:4] == b"EFS2":
    print("Input file is an EFS2 archive")
else:
    print("Input file is not a valid EFS2 archive")

# Function definitions

def removeNull(b):
    return (b.rstrip(b"\x00")).decode("utf-8")

# end function definitions

modNameLen=int.from_bytes(Mod[48:52], "little")
modName=removeNull(Mod[52:52+modNameLen])
print(modName)

cur = 0
extract = True

while extract:
    if Mod[cur:cur+4] == b"OBTY":
        tylen=int.from_bytes(Mod[cur+4:cur+8],"little")
        obty=int.from_bytes(Mod[cur+8:cur+8+tylen],"little")
        cur+=(tylen+8)
        if obty==0 and Mod[cur:cur+4] == b"OBPT":
            ptlen=int.from_bytes(Mod[cur+4:cur+8],"little")
            obpt=removeNull(Mod[cur+8:cur+8+ptlen])
            obptp=dirname(obpt)
            if not isdir(outDir+obptp):
                os.makedirs(outDir+obptp)
            cur+=(ptlen+8)
            if Mod[cur:cur+4] == b"OBDT":
                dtlen=int.from_bytes(Mod[cur+4:cur+8],"little")
                obdt=Mod[cur+8:cur+8+dtlen]
                with open(outDir+obpt, "wb") as outFile:
                    outFile.write(obdt)
                    outFile.close()
            cur+=(dtlen+8)
                
        elif obty==1 and Mod[cur:cur+4] == b"OBPT":
            ptlen=int.from_bytes(Mod[cur+4:cur+8],"little")
            obpt=removeNull(Mod[cur+8:cur+8+ptlen])
            print(obpt)
            if not isdir(outDir+obpt):
                os.makedirs(outDir+obpt)
            cur+=(ptlen+8)
        else:
            print("Unrecognized object (%s) at address %s, aborting" % (str(obty), str(cur)))
    else:
        cur+=1
    if cur > size:
        extract = False
        print("Done")
