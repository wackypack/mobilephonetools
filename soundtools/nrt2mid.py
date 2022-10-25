import tkinter as tk
from tkinter import filedialog
import os
from os import listdir
from os.path import dirname, basename, splitext, join
from struct import pack

root = tk.Tk()
root.withdraw()

#filePath=filedialog.askopenfilename()
#file=open(filePath,mode='rb')
#BaseName=splitext(basename(filePath))[0]

filePath=filedialog.askdirectory()

nrtFiles=[f for f in listdir(filePath) if splitext(basename(f))[1] in [".nrt", ".rng", None]]

def vlq(num):
    outArray=bytearray()
    power=1
    while 128**power <= num:
        power+=1
    if 128**power > num:
        power-=1
    for n in range(power+1):
        place=num//(128**power)
        if power != 0:
            outArray.append(place+128)
        else:
            outArray.append(place)
        num=num-(place*(128**power))
        power-=1
    return(outArray)

# Variables for midi output!!!!!
# Subtracted key offset. Note that this may cause conversion errors with certain files
# 2300: 41
# 3310: 55
# 5110, 6110, 7110: 54
# 6340i: 25
# 8910i: 29
keyOffset=55
# Tempo
# 2300: 95
# 5110, 6110, 7110: 60
# 6340i: 50
# 8910i: 50
tempo=60

# Instrument, must be between 0-127
instrument=79

midiTempo=int(round(60000/tempo, 3)*1000)


for f in nrtFiles:
    print("Now converting "+f)
    file=open(join(filePath,f),mode='rb')
    Nrt=file.read()
    outFile=join(filePath,f)+".mid"
    midiHead=b"\x4D\x54\x68\x64\x00\x00\x00\x06\x00\x01\x00\x02\x00\x78\x4D\x54\x72\x6B\x00\x00\x00\x1D\x00\xFF\x03\x00\x00\xFF\x51\x03"+midiTempo.to_bytes(3, "big")+b"\x00\xFF\x58\x04\x04\x02\x18\x08\x00\xFF\x59\x02\x00\x00\x01\xFF\x2F\x00"
    midiData=bytes()

    loopDetect=0
    lastNote=0
    read=0
    convert=True
    isResting=True
    while convert:
        loopDetect+=1
        if Nrt[read] == int("0x00", 16):
            read+=1
            # ignores
            loopDetect=0
        if Nrt[read] == int("0x02", 16):
            read+=2
            loopDetect=0
        if Nrt[read] == int("0x09", 16):
            read+=1
            loopDetect=0
        if Nrt[read] == int("0x0A", 16):
            read+=2
            # typically triggers vibration, but will be ignored for now
            loopDetect=0
        if Nrt[read] == int("0x05", 16):
            loopStart=read+2
            loopCount=Nrt[read+1]
            read+=2
            loopDetect=0
        if Nrt[read] == int("0x06", 16):
            loopingSection=Nrt[loopStart:read]



            for x in range(loopCount-1):
                isLooping=True
                lread=0
                while isLooping:
                    if loopingSection[lread] == int("0x0A", 16):
                        increment=2
                    if loopingSection[lread] == int("0x40", 16):
                        midiData=midiData+(lastNote.to_bytes(1,"big"))
                        midiData=midiData+b"\x00"+vlq(loopingSection[lread+1])
                        #print("Rest with duration "+str(loopingSection[lread+1]))
                        increment=2
                            
                    if loopingSection[lread] >= int("0x41", 16) and loopingSection[lread] <= int("0xB5", 16):
                        if not isResting:
                            midiData=midiData+(lastNote.to_bytes(1,"big"))+b"\x00\x00"
                        lastNote=(loopingSection[lread]-keyOffset)
                        midiData=midiData+(lastNote.to_bytes(1,"big"))
                        midiData=midiData+b"\x7F"+vlq(loopingSection[lread+1])
                        #print("Note on "+str(lastNote)+" with duration "+str(Nrt[read+1]))
                        isResting=False
                        increment=2
                    lread+=increment
                    if lread >= len(loopingSection):
                        isLooping=False



            read+=1
        if Nrt[read] == int("0x40", 16):
            midiData=midiData+(lastNote.to_bytes(1,"big"))
            midiData=midiData+b"\x00"+vlq(Nrt[read+1])
            #print("Rest with duration "+str(Nrt[read+1]))
            read+=2
            isResting=True
            loopDetect=0
            
        if Nrt[read] >= int("0x41", 16) and Nrt[read] <= int("0xB5", 16):
            if not isResting:
                midiData=midiData+(lastNote.to_bytes(1,"big"))+b"\x00\x00"
            lastNote=(Nrt[read]-keyOffset)
            midiData=midiData+(lastNote.to_bytes(1,"big"))
            midiData=midiData+b"\x7F"+vlq(Nrt[read+1])
            #print("Note on "+str(lastNote)+" with duration "+str(Nrt[read+1]))
            read+=2
            isResting=False
            loopDetect=0
        if Nrt[read] == int("0x07", 16):
            if not isResting:
                midiData=midiData+(lastNote.to_bytes(1,"big"))+b"\x00\x00"
            convert=False
        if loopDetect >= 4:
            convert=False
            
    outBytes=bytes(midiHead+b"MTrk"+(len(midiData)+8).to_bytes(4, "big")+b"\x00\xC0"+instrument.to_bytes(1,"big")+b"\x00\x90"+midiData+b"\xFF\x2F\x00")
    output=open(outFile,"wb")
    output.write(outBytes)
    output.close()
    
    
