import tkinter as tk
from tkinter import filedialog
import os
from os.path import dirname, basename, splitext, join
import sys

root = tk.Tk()
root.withdraw()

xor=open("OctopusXorKey.bin", mode="rb")
xorKey=xor.read()
filePath=filedialog.askopenfilename()
file=open(filePath,mode="rb")

outFile=join(dirname(filePath), splitext(basename(filePath))[0])+".bin"

# default seek offset is 13922 (0x3662)
file.seek(13922)
inFile=file.read()
size=len(inFile)

def convertToBin(byteObject, key, outFile):
    output=open(outFile, "wb")
    keyPot=0
    for x in range(size):
        output.write((byteObject[x] ^ key[keyPot]).to_bytes(1, 'big'))
        keyPot+=1
        if keyPot==1280:
            keyPot=0

print("Bin file is %s bytes" % size)
print("Now deciphering, please wait...")
convertToBin(inFile, xorKey, outFile)
input("Done. Press enter to exit")
sys.exit()
