import tkinter as tk
from tkinter import filedialog
import os
from os import listdir
from os.path import basename, splitext, join
import string

root = tk.Tk()
root.withdraw()

filePath=filedialog.askdirectory()
if not filePath:
    print("File dialog cancelled")
    exit()

bname=basename(filePath)

wavFiles=[f for f in listdir(filePath) if splitext(f)[1]==".wav"]


for f in wavFiles:
    file=open(join(filePath, f), "r+b")
    size=os.path.getsize(join(filePath, f))
    newBytes=bytearray(b'')
    job=True
    for x in range(size):
        if job:
            file.seek(x)
            checkByte=file.read(1)
            if checkByte==b"d":
                file.seek(x)
                checkByte=file.read(4)
                if checkByte==b"data":
                    waveLen=int.from_bytes(file.read(4), "little")
                    waveData=file.read(waveLen)
                    waveAddr=x+8
                    file.seek(0)
                    for y in range(waveLen//2):
                        bytea=waveData[y*2]
                        byteb=waveData[(y*2)+1]
                        newBytes.append(byteb)
                        newBytes.append(bytea)
                    file.seek(waveAddr)
                    file.write(newBytes)
                    file.close()
                    job=False
