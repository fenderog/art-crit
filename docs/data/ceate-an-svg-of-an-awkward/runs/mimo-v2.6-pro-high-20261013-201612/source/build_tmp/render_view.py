import sys, subprocess, os
sys.path.insert(0,'build_tmp')
from pngread import read_png
svg_file, out = sys.argv[1], sys.argv[2]
tmp = 'build_tmp/_r.svg'
s = open(svg_file).read()
if 'height="1150"' in s:
    s = s.replace('width="1600" height="1150"', 'width="1600" height="1600"', 1)
open(tmp,'w').write(s)
subprocess.run(['qlmanage','-t','-s','1600','-o','build_tmp',tmp], capture_output=True)
src = 'build_tmp/_r.svg.png'
w,h,nch,px = read_png(src)
W,H = 400,288
ox,oy = 0,225
outb = bytearray()
for y in range(H):
    sy = oy + y*1150//H
    outb.append(0)
    for x in range(W):
        sx = ox + x*1600//W
        o = (sy*w+sx)*nch
        outb += bytes(px[o:o+3])
import zlib, struct
def chunk(t,d):
    return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0)) + chunk(b'IDAT',zlib.compress(bytes(outb),6)) + chunk(b'IEND',b'')
open(out,'wb').write(png)
print('rendered', out)
