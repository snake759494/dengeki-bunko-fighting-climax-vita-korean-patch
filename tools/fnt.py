import struct,gzip,os
import numpy as np
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))+'/emu/fs/ux0/app/PCSG00341'
FD=R+'/grpdat/Font'
def readfnt(p=FD+'/Font00.fnt'):
    d=open(p,'rb').read()
    hdr=d[:0x3c]; n=struct.unpack_from('<I',d,0x34)[0]
    ents=[list(struct.unpack_from('<I9h',d,0x3c+i*22)) for i in range(n)]
    return hdr,ents,d[0x3c+n*22:]
def writefnt(hdr,ents,tail,p):
    hdr=bytearray(hdr); struct.pack_into('<I',hdr,0x34,len(ents))
    open(p,'wb').write(bytes(hdr)+b''.join(struct.pack('<I9h',*e) for e in ents)+tail)
def morton(y,x):
    r=0
    for i in range(16):
        r|=((x>>i)&1)<<(2*i)|((y>>i)&1)<<(2*i+1)
    return r
def blockorder(bw,bh):
    # vita swizzle: morton over square min dim
    m=min(bw,bh); order=[]
    idx={}
    for by in range(bh):
        for bx in range(bw):
            if bw>=bh: t=(bx//m)*m*m+morton(bx%m,by)
            else: t=(by//m)*m*m+morton(bx,by%m)
            idx[t]=(bx,by)
    return [idx[i] for i in range(bw*bh)]
def dxt5_alpha_decode(b):
    a0,a1=b[0],b[1]; bits=int.from_bytes(b[2:8],'little')
    if a0>a1: pal=[a0,a1]+[((6-i)*a0+(i+1)*a1)//7 for i in range(6)]
    else: pal=[a0,a1]+[((4-i)*a0+(i+1)*a1)//5 for i in range(4)]+[0,255]
    return [pal[(bits>>(3*i))&7] for i in range(16)]
def readgxt(p):
    d=gzip.open(p).read() if p.endswith('.gz') else open(p,'rb').read()
    return d
def gxtinfo(d):
    off,size,pal,fl,typ,fmt,w,h=struct.unpack_from('<IIiIIIHH',d,0x20)
    return off,size,typ,fmt,w,h
def decode_alpha(d):
    off,size,typ,fmt,w,h=gxtinfo(d); bw,bh=w//4,h//4
    img=np.zeros((h,w),np.uint8); order=blockorder(bw,bh)
    for i,(bx,by) in enumerate(order):
        blk=d[off+i*16:off+i*16+16]
        a=dxt5_alpha_decode(blk)
        img[by*4:by*4+4,bx*4:bx*4+4]=np.array(a,np.uint8).reshape(4,4)
    return img
def encode_alpha_block(px):
    # px 16 alpha values; use a0=max,a1=min 8-level mode
    mx,mn=max(px),min(px)
    if mx==mn: return bytes([mx,mn])+b'\0'*6
    a0,a1=mx,mn; pal=[a0,a1]+[((6-i)*a0+(i+1)*a1)//7 for i in range(6)]
    bits=0
    for i,v in enumerate(px):
        k=min(range(8),key=lambda j:abs(pal[j]-v)); bits|=k<<(3*i)
    return bytes([a0,a1])+bits.to_bytes(6,'little')
def c565(c): return np.array([((c>>11)&31)*255//31,((c>>5)&63)*255//63,(c&31)*255//31])
def decode_rgba(d):
    off,size,typ,fmt,w,h=gxtinfo(d); bw,bh=w//4,h//4
    img=np.zeros((h,w,4),np.uint8); order=blockorder(bw,bh)
    for i,(bx,by) in enumerate(order):
        blk=d[off+i*16:off+i*16+16]
        a=dxt5_alpha_decode(blk)
        c0,c1,bits=struct.unpack_from('<HHI',blk,8)
        p0,p1=c565(c0),c565(c1); pal=[p0,p1,(2*p0+p1)//3,(p0+2*p1)//3]
        px=np.array([pal[(bits>>(2*j))&3] for j in range(16)]).reshape(4,4,3)
        img[by*4:by*4+4,bx*4:bx*4+4,:3]=px; img[by*4:by*4+4,bx*4:bx*4+4,3]=np.array(a).reshape(4,4)
    return img
