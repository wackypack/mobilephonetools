import tkinter as tk
from tkinter import filedialog
import os
import binascii
from os.path import dirname, basename, splitext, join

filePath=filedialog.askopenfilename()
file=open(filePath,mode='rb')
size=os.path.getsize(filePath)

sbn=file.read()

outFile=join(dirname(filePath), splitext(basename(filePath))[0])+".bin"

sbnSize=iter(range(size))

def getFlashSize(byteObject):
    readFile=True
    x=0
    address=0
    while readFile:
        if byteObject[x:x+2] == b"S0":
            x+=4
            print("this is an sbn file")
        if byteObject[x:x+2] == b"S1":
            readAddress=int.from_bytes(byteObject[x+3:x+5], "big")
            readSize=int.from_bytes(byteObject[x+2:x+3], "big")
            if readAddress+readSize > address:
                address=readAddress+readSize
            x+=int.from_bytes(byteObject[x+2:x+3], "big")+3
        if byteObject[x:x+2] == b"S2":
            readAddress=int.from_bytes(byteObject[x+3:x+6], "big")
            readSize=int.from_bytes(byteObject[x+2:x+3], "big")
            if readAddress+readSize > address:
                address=readAddress+readSize
            x+=int.from_bytes(byteObject[x+2:x+3], "big")+3
        if byteObject[x:x+2] == b"S8":
            readFile=False
    return(address)

def convertToBin(byteObject, arraySize, outFile):
    
    readFile=True
    x=0
    output=open(outFile, "wb")
    output.write(b"\xFF"*arraySize)
    while readFile:
        if byteObject[x:x+2] == b"S0":
            x+=4
            print("now processing bin file")
            print(outFile)
        if byteObject[x:x+2] == b"S1":
            readAddress=int.from_bytes(byteObject[x+3:x+5], "big")
            readSize=int.from_bytes(byteObject[x+2:x+3], "big")
            output.seek(readAddress)
            output.write(byteObject[x+5:x+readSize+2])
            x+=int.from_bytes(byteObject[x+2:x+3], "big")+3
        if byteObject[x:x+2] == b"S2":
            readAddress=int.from_bytes(byteObject[x+3:x+6], "big")
            readSize=int.from_bytes(byteObject[x+2:x+3], "big")
            output.seek(readAddress)
            output.write(byteObject[x+6:x+readSize+2])
            x+=int.from_bytes(byteObject[x+2:x+3], "big")+3
        if byteObject[x:x+2] == b"S8":
            readFile=False
    output.close()
            

binSize=getFlashSize(sbn)
print("the size of the bin file is "+str(binSize))
binFile=convertToBin(sbn, binSize, outFile)
print("done")
        
