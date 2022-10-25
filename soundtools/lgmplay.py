import sys
from sys import argv
import pyaudio
import numpy as np
from os.path import getsize
from time import sleep

if len(argv) != 6:
    print("Invalid number of arguments\n")
    print("Command structure:")
    print("python lgmplay.py [infile] [offs fmt] [offs] [basenote] [len mult. fac]\n")
    print("infile: Name or path of file to load\noffs fmt: Format of byte offset to start at (h for hex or d for decimal)")
    print("offs: Byte offset of infile to start playing at\nbasenote: Number to subtract from note value (higher value makes output lower in pitch)")
    print("len. mult fac: Value by which to multiply the note length. Note lengths are interpreted as 1/100sec\n")
    print("Sample Usage:")
    print("python lgmplay.py SD20V95.bin h 427F6 37 3")
    sys.exit()

if len(argv) == 6:
    if argv[2] not in ("h","d"):
        print("Unexpected argument \"%s\". Expecting \"h\" or \"d\"" % argv[2])
        sys.exit()
    else:
        infile=open(argv[1],"rb")
        flen=getsize(argv[1])
        if argv[2] == "h":
            offs=int(argv[3], 16)
        elif argv[2] == "d":
            offs=int(argv[3])
        basenote=int(argv[4])
        lenmult=float(argv[5])

p = pyaudio.PyAudio()

def playNote(note,d,stm):
    notes=[262,
           277,
           294,
           311,
           330,
           349,
           370,
           396,
           415,
           440,
           466,
           494]
    octaves=[0.0625,
             0.125,
             0.25,
             0.5,
             1,
             2,
             4,
             8,
             16]
    # middle octave should be 5, so that the range is 0-8 (preferable 1-8 but we'll see)
    # the note values should correspond to MIDI notes!!!
    duration=d/100
    volume=0.5
    octave = (note // 12)-1
    snote = (note % 12)
    
    if note < 12 or note > 108:
        sleep(duration)
    else:
        freq=notes[snote]*(octaves[octave])
        samples = (np.sin(2*np.pi*np.arange(44100*duration)*freq/44100)).astype(np.float32)
        stm.write(volume*samples)

stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=44100,
                        output=True)

# playNote(84,25,stream)
# midi note; duration in 1/100sec; output stream

infile.seek(offs)
while infile.tell() < flen:
    cnote=int.from_bytes(infile.read(2),"little")
    clen=int.from_bytes(infile.read(2),"little")
    nlen=clen*lenmult
    if cnote < basenote:
        print("%s: rest for %s msec" % (str(infile.tell()), str(nlen*10)))
        sleep(nlen/100)
    else:
        print("%s:   %s for %s msec" % (str(infile.tell()), str(cnote-basenote), str(nlen*10)))
        playNote(cnote-basenote,nlen,stream)
