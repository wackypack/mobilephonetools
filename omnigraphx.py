 ############################################# 
#                                             #
#                                             #
#       Graphic Extractor for Python 3        #
#                                             #
#                                             #
 ############################################# 

import tkinter as tk
from tkinter import filedialog
import os
from os.path import dirname, basename, splitext

root = tk.Tk()
root.withdraw()

filePath=filedialog.askopenfilename()
file=open(filePath,mode='rb')
size=os.path.getsize(filePath)
outDir=dirname(filePath)
BaseName=splitext(basename(filePath))[0]

Bin=file.read()

outFile=input("Please give a name prefix for output files: ")
numFiles=0

sr=iter(range(size))

# File identifiers vv

gifHeader = b"GIF89a"
gifEof=b"\x00\x3B"

# File identifiers ^^


# Functions vv

def writeFile(address, size, ext):
    global numFiles
    outBytes=Bin[address:address+size]
    output=open(outDir+"/%s_%s.%s" % (outFile, str(numFiles), ext), mode="xb")
    output.write(outBytes)
    output.close()
    print("Exported %s_%s.%s at address %s, size %s" % (outFile, str(numFiles), ext, hex(address), str(size)))
    numFiles+=1

# Functions ^^


print("Now searching "+basename(filePath))

for x in sr:
    # Pick up GIF files.
    if Bin[x:x+1] == b"G":
        chunkSize=0
        if Bin[x:x+6] == gifHeader:
            readByte=Bin[x+chunkSize:x+chunkSize+11]
            while readByte != gifEof:
                chunkSize+=1
                readByte=Bin[x+chunkSize:x+chunkSize+2]
                if chunkSize >= size-x:
                    readByte=gifEof
            if readByte == gifEof:
                writeFile(x, chunkSize+2, "gif")

print("Found %s total hits." % str(numFiles))
input("Press Enter to exit")
