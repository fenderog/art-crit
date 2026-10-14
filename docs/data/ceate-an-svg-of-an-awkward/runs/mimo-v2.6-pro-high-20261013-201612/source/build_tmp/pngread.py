import zlib,struct
def read_png(p):
    d=open(p,'rb').read(); pos=8; idat=b''; w=h=None; ct=None
    while pos<len(d):
        ln=struct.unpack('>I',d[pos:pos+4])[0]; typ=d[pos+4:pos+8]; data=d[pos+8:pos+8+ln]; pos+=12+ln
        if typ==b'IHDR': w,h,bd,ct=struct.unpack('>IIBB',data[:10])
        elif typ==b'IDAT': idat+=data
    raw=zlib.decompress(idat); nch={0:1,2:3,3:1,4:2,6:4}[ct]; stride=w*nch
    out=bytearray(); prev=bytearray(stride); i=0
    for y in range(h):
        f=raw[i]; i+=1; line=bytearray(raw[i:i+stride]); i+=stride
        if f==1:
            for x in range(nch,stride): line[x]=(line[x]+line[x-nch])&255
        elif f==2:
            for x in range(stride): line[x]=(line[x]+prev[x])&255
        elif f==3:
            for x in range(stride):
                a=line[x-nch] if x>=nch else 0
                line[x]=(line[x]+((a+prev[x])>>1))&255
        elif f==4:
            for x in range(stride):
                a=line[x-nch] if x>=nch else 0
                b=prev[x]; c=prev[x-nch] if x>=nch else 0
                p=a+b-c; pa=abs(p-a); pb=abs(p-b); pc=abs(p-c)
                pr=a if (pa<=pb and pa<=pc) else (b if pb<=pc else c)
                line[x]=(line[x]+pr)&255
        out+=line; prev=line
    return w,h,nch,bytes(out)
