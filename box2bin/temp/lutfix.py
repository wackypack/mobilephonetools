sw=open("sweep.bin","rb")
swdata=sw.read()
sw.close()
lut=open("pfw.lut","rb")
lutdata=lut.read()
lut.close()
size=len(lutdata)
out=open("out.lut","wb")
out.write(b"\x00"*4096)

col=0
for x in range(size):
    if col>=16:
        col=0
    currByte=lutdata[x]
    seb=b""
    row=0
    while seb!=currByte:
        seb=swdata[col+(16*row)]
        row+=1
    
    out.seek(col+(16*row))
    out.write(swdata[x].to_bytes(1,"big"))
    col+=1
