import tkinter as tk
from tkinter import filedialog
import os
from os.path import dirname, basename, splitext, join
import sys

root = tk.Tk()
root.withdraw()

# xor=open("scry_37D70C1.key", mode="rb")
# xorKey=xor.read()
filePath=filedialog.askopenfilename()
file=open(filePath,mode="rb")

inFile=file.read()
size=len(inFile)

outFile=join(dirname(filePath), splitext(basename(filePath))[0])+".sre"

def convertToBin(byteObject, key, outFile):
    output=open(outFile, "wb")
    keyPot=0
    for x in range(size):
        outputBuffer=byteObject[x]^key[keyPot]
        output.write(outputBuffer.to_bytes(1, "big"))
        
        keyPot+=1
        if keyPot==19:
            keyPot=0

def locateKeyOffset(byteObject):
    size=len(byteObject)
    for x in range(size):
        if byteObject[x:x+6] == byteObject[x+912:x+918]:
            return x+2
    return "Fail"

def crack(byteObject, offset):
    keyvals={}
    for x in range(19):
        keyvals[(offset+(x*48))%19]=(byteObject[offset+(x*48)]^83)
    key=bytearray()
    for x in range(19):
        key.append(keyvals.get(x))
    return key

print("Bin file is %s bytes" % size)
print("Locating deciphering offset...")
decOffset=locateKeyOffset(inFile)
print("Key repetition offset is "+str(decOffset))
print("Now cracking file...")
crackedKey=crack(inFile,decOffset)
print("Key is "+str(crackedKey))
print("Now deciphering, please wait...")
convertToBin(inFile, crackedKey, outFile)
input("Done. Press enter to exit")
sys.exit()
