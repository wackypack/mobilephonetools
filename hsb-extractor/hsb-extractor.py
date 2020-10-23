import tkinter as tk
from tkinter import filedialog, messagebox
import os
from os import listdir, getcwd
from os.path import isfile, isdir, join, dirname, basename
import wave
import string
import struct

root = tk.Tk()
root.withdraw()

try:
    lutAlaw=open(join(getcwd(), "alaw16.lut"), mode="rb").read()
    lutAlawIsLoaded=True
except:
    print("A-law LUT is missing. Extractor will run, but will not convert A-law waves.")
    lutAlawIsLoaded=False

filePath=filedialog.askopenfilename()
file=open(filePath, mode="rb")
size=os.path.getsize(filePath)
outPath=dirname(filePath)
bname=basename(filePath)

newBytes=bytearray(b'')

metafile = open(join(outPath, bname+".waveparams.txt"), "w")
metadata = ""

for x in range(size):
    file.seek(x)
    checkByte=file.read(1)
    if checkByte==b"s":
        file.seek(x)
        checkByte=file.read(4)
        if checkByte==b"snd ":
            sampAdd=x
            file.seek(x+6)
            sampIndex=int.from_bytes(file.read(2), "big")
            sampName=str(sampIndex)
            nameLen=-1
            nameRead=""
            while nameRead!=b"\x00":
                nameLen+=1
                file.seek(x+9+nameLen)
                nameRead=file.read(1)
            if nameLen>=1:
                file.seek(x+9)
                sampName=file.read(nameLen).decode("utf-8").replace("*", "-").replace("/", "-")
            headOffset=x+nameLen+9
            file.seek(headOffset+6)
            detectMpeg=file.read(3)
            if detectMpeg==b"mpg":
                file.seek(headOffset+22)
                streamSize=int.from_bytes(file.read(4), "big")
                file.seek(headOffset+130)
                stream=file.read(streamSize)

                streamOut=open(outPath+"/%s.mp3" % sampName,"wb")
                streamOut.write(stream)
                streamOut.close()
            else:
                try:
                    file.seek(headOffset+31)
                    sampChannels=int.from_bytes(file.read(1), "big")
                    file.seek(headOffset+32)
                    sampRate=int.from_bytes(file.read(2), "big")
                    file.seek(headOffset+36)
                    loopStart=int.from_bytes(file.read(4), "big")
                    file.seek(headOffset+40)
                    loopEnd=int.from_bytes(file.read(4), "big")
                    file.seek(headOffset+45)
                    rootKey=int.from_bytes(file.read(1), "big")
                    file.seek(headOffset+46)
                    sampLen=int.from_bytes(file.read(4), "big")
                    file.seek(headOffset+73)
                    bitWidth=int.from_bytes(file.read(1), "big")
                    if bitWidth==16:
                        sampLen=sampLen*2
                        sampWidth=2
                        oddFmt=False
                    elif bitWidth==0:
                        sampWidth=1
                        oddFmt=True
                    else:
                        sampWidth=1
                        oddfmt=False

                    wavefact=0
                    if oddFmt:
                        file.seek(headOffset+64)
                        # 0: don't change
                        # 1: alaw
                        try:
                            fmtCheck=file.read(4).decode("utf-8")
                        except:
                            wavefact=0
                        if fmtCheck=="alaw":
                            wavefact=1
                            sampWidth=2
                    file.seek(headOffset+88)
                    sampWave=file.read(sampLen)
                    # for alaw waves
                    if wavefact==1 and lutAlawIsLoaded:
                        srcWave=sampWave
                        sampWave=bytearray(b'')
                        for s in range(len(srcWave)):
                            sampWave+=lutAlaw[srcWave[s]*2:srcWave[s]*2+2]
                    wavOut = wave.open(outPath+"/%s.wav" % sampName,"w")
                    wavOut.setnchannels(sampChannels)
                    wavOut.setsampwidth(sampWidth)
                    wavOut.setframerate(sampRate)
                    wavOut.writeframesraw(sampWave)
                    wavOut.close()
                    wavFinal=open(outPath+"/%s.wav" % sampName,"r+b")
                    wavFinal.seek(0, 2)

                    sampRootKey=struct.pack('<B', rootKey)
                    sampLoopStart=struct.pack('<L', loopStart)
                    if loopEnd<=1:
                        sampLoopEnd=struct.pack('<L', 0)
                    else:
                        sampLoopEnd=struct.pack('<L', loopEnd-1)
                    
                    wavFinal.write(b"smpl\x3c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x12\x7a\x00\x00"+sampRootKey+b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"+sampLoopStart+sampLoopEnd+b"\x00\x00\x00\x00\x00\x00\x00\x00")
                    wavFinal.seek(4)
                    riffSize=int.from_bytes(wavFinal.read(4), "little")
                    riffSize+=68
                    wavFinal.seek(4)
                    wavFinal.write(struct.pack('<L', riffSize))
                    metadata=metadata+"Sample: %s\nLoop Start: %s\nLoop End: %s\nRoot Key: %s\n\n" % (sampName, str(loopStart), str(loopEnd), str(rootKey))
                except Exception as e:
                    print("Failed to read sample "+sampName+" because "+str(e))

metafile.write(metadata)
metafile.close()
