f=open("sweep.bin", "xb")
obuff=bytearray(b'')
for x in range(256):
    for y in range(16):
        obuff+=x.to_bytes(1,"big")

f.write(obuff)
f.close()
