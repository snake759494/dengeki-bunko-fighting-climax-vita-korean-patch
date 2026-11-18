import struct,gzip,numpy as np,os,sys
sys.path.insert(0,os.path.dirname(__file__)); import fnt
_R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
_APP=os.path.normcase(os.path.abspath(_R+'/emu/fs/ux0/app/PCSG00341'))
def load(p):
    ap=os.path.normcase(os.path.abspath(p))
    if ap.startswith(_APP):
        import shutil
        rel=os.path.relpath(os.path.abspath(p),os.path.abspath(_R+'/emu/fs/ux0/app/PCSG00341')); bk=os.path.join(_R,'work','orig',rel)
        if not os.path.exists(bk):
            os.makedirs(os.path.dirname(bk),exist_ok=True); shutil.copy2(p,bk)
        p=bk
    d=open(p,'rb').read()
    return gzip.decompress(d) if d[:2]==b'\x1f\x8b' else d
def textures(d):
    n=struct.unpack_from('<I',d,8)[0]; out=[]
    for i in range(n):
        off,size,pal,fl,typ,fmt,w,h=struct.unpack_from('<IIiIIIHH',d,0x20+i*0x20); out.append(dict(i=i,off=off,size=size,typ=typ,fmt=fmt,w=w,h=h,hdr=0x20+i*0x20))
    return out
def pot(x):
    p=1
    while p<x: p*=2
    return p
def sworder(w,h):
    # returns array idx-> (x,y) for swizzled w x h (units)
    W,H=pot(w),pot(h); m=min(W,H)
    xs=np.arange(W); ys=np.arange(H); X,Y=np.meshgrid(xs,ys)
    def spread(v):
        r=np.zeros_like(v)
        for i in range(12): r|=((v>>i)&1)<<(2*i)
        return r
    if W>=H: idx=(X//m)*m*m+ (spread(Y%m)|(spread(X%m)<<1))
    else: idx=(Y//m)*m*m+ (spread(Y%m)|(spread(X%m)<<1))
    return idx,W,H
def decode(d,t):
    w,h,fmt,typ=t['w'],t['h'],t['fmt']&0xff000000,t['typ']
    raw=d[t['off']:t['off']+t['size']]
    linear=typ in (0x60000000,0x0c000000)
    if fmt==0x0c000000:
        if linear: a=np.frombuffer(raw,np.uint8)[:w*h*4].reshape(h,w,4)
        else:
            idx,W,H=sworder(w,h); px=np.frombuffer(raw,np.uint8).reshape(-1,4)
            a=px[idx][:h,:w]
        return a[...,[2,1,0,3]] if (t['fmt']&0xffff)==0x1000 else a
    bw,bh=(w+3)//4,(h+3)//4
    bs=8 if fmt==0x85000000 else 16
    if linear: idx=np.arange(bw*bh).reshape(bh,bw); W,H=bw,bh
    else: idx,W,H=sworder(bw,bh)
    img=np.zeros((bh*4,bw*4,4),np.uint8)
    for by in range(bh):
        for bx in range(bw):
            o=int(idx[by,bx])*bs; blk=raw[o:o+bs]
            if len(blk)<bs: continue
            cb=blk[-8:]; c0,c1,bits=struct.unpack_from('<HHI',cb)
            p0,p1=fnt.c565(c0),fnt.c565(c1)
            if bs==8 and c0<=c1: pal=[p0,p1,(p0+p1)//2,np.zeros(3,int)]; al=[255,255,255,0]
            else: pal=[p0,p1,(2*p0+p1)//3,(p0+2*p1)//3]; al=[255]*4
            ii=[(bits>>(2*j))&3 for j in range(16)]
            px=np.array([pal[k] for k in ii]).reshape(4,4,3)
            if bs==16:
                if fmt==0x87000000: a=np.array(fnt.dxt5_alpha_decode(blk[:8])).reshape(4,4)
                else: a=np.array([((int.from_bytes(blk[:8],'little')>>(4*j))&15)*17 for j in range(16)]).reshape(4,4)
            else: a=np.array([al[k] for k in ii]).reshape(4,4)
            img[by*4:by*4+4,bx*4:bx*4+4,:3]=px; img[by*4:by*4+4,bx*4:bx*4+4,3]=a
    return img[:h,:w]
if __name__=='__main__':
    from PIL import Image
    src,dst=sys.argv[1],sys.argv[2]
    d=load(src)
    for t in textures(d):
        im=decode(d,t); Image.fromarray(im).save(dst+('_%d'%t['i'] if t['i'] else '')+'.png')

def _c565(c): 
    c=np.clip(c,0,255).astype(int); return ((c[0]*31+127)//255<<11)|((c[1]*63+127)//255<<5)|((c[2]*31+127)//255)
def enc_color(px,alpha_mode=False):
    # px (16,3) float; returns 8 bytes (4-color mode)
    lum=px@np.array([0.299,0.587,0.114])
    hi,lo=px[lum.argmax()],px[lum.argmin()]
    c0,c1=_c565(hi),_c565(lo)
    if c0<c1: c0,c1,hi,lo=c1,c0,lo,hi
    if c0==c1:
        return struct.pack('<HHI',c0,c1,0)
    from fnt import c565
    p0,p1=c565(c0).astype(float),c565(c1).astype(float)
    pal=np.array([p0,p1,(2*p0+p1)/3,(p0+2*p1)/3])
    idx=((px[:,None,:]-pal[None])**2).sum(-1).argmin(1)
    bits=0
    for j,k in enumerate(idx): bits|=int(k)<<(2*j)
    return struct.pack('<HHI',c0,c1,bits)
def encode_blocks(d,t,img,blocks):
    """img: HxWx4 uint8 full texture, blocks: set of (bx,by) to re-encode in place. returns new bytes"""
    import fnt as F
    d=bytearray(d); w,h,fmt,typ=t['w'],t['h'],t['fmt']&0xff000000,t['typ']
    linear=typ in (0x60000000,0x0c000000)
    if fmt==0x0c000000:
        if linear:
            arr=np.frombuffer(bytes(d[t['off']:t['off']+w*h*4]),np.uint8).reshape(h,w,4).copy()
            src=img[...,[2,1,0,3]] if (t['fmt']&0xffff)==0x1000 else img
            arr[:]=src; d[t['off']:t['off']+w*h*4]=arr.tobytes(); return bytes(d)
        idx,W,H=sworder(w,h)
        src=img[...,[2,1,0,3]] if (t['fmt']&0xffff)==0x1000 else img
        for (bx,by) in blocks:
            for y in range(by*4,min(by*4+4,h)):
                for x in range(bx*4,min(bx*4+4,w)):
                    o=t['off']+int(idx[y,x])*4; d[o:o+4]=bytes(src[y,x])
        return bytes(d)
    bw,bh=(w+3)//4,(h+3)//4; bs=8 if fmt==0x85000000 else 16
    if linear: idx=np.arange(bw*bh).reshape(bh,bw)
    else: idx,W,H=sworder(bw,bh)
    pad=np.zeros((bh*4,bw*4,4),np.uint8); pad[:h,:w]=img
    for (bx,by) in blocks:
        blk=pad[by*4:by*4+4,bx*4:bx*4+4].reshape(16,4)
        col=enc_color(blk[:,:3].astype(float))
        if bs==16:
            if fmt==0x87000000: al=F.encode_alpha_block([int(v) for v in blk[:,3]])
            else:
                v=0
                for j,a in enumerate(blk[:,3]): v|=(int(a)//17)<<(4*j)
                al=v.to_bytes(8,'little')
            out=al+col
        else: out=col
        o=t['off']+int(idx[by,bx])*bs; d[o:o+bs]=out
    return bytes(d)
def save(p,d):
    import gzip
    if p.endswith('.gz'):
        with gzip.open(p,'wb',compresslevel=6) as f: f.write(d)
    else: open(p,'wb').write(d)

def _decode_fast(d,t):
    w,h,fmt,typ=t['w'],t['h'],t['fmt']&0xff000000,t['typ']
    if fmt not in (0x85000000,0x87000000,0x86000000): return None
    raw=d[t['off']:t['off']+t['size']]
    linear=typ in (0x60000000,0x0c000000)
    bw,bh=(w+3)//4,(h+3)//4; bs=8 if fmt==0x85000000 else 16
    if linear: idx=np.arange(bw*bh).reshape(bh,bw)
    else: idx,W,H=sworder(bw,bh); idx=idx[:bh,:bw]
    buf=np.frombuffer(raw,np.uint8)
    nb=len(buf)//bs; B=buf[:nb*bs].reshape(nb,bs)
    B=B[np.minimum(idx.reshape(-1),nb-1)]
    cb=B[:,-8:]
    c0=cb[:,0].astype(np.uint32)|(cb[:,1].astype(np.uint32)<<8); c1=cb[:,2].astype(np.uint32)|(cb[:,3].astype(np.uint32)<<8)
    bits=cb[:,4].astype(np.uint32)|(cb[:,5].astype(np.uint32)<<8)|(cb[:,6].astype(np.uint32)<<16)|(cb[:,7].astype(np.uint32)<<24)
    def rgb(c): return np.stack([((c>>11)&31)*255//31,((c>>5)&63)*255//63,(c&31)*255//31],-1).astype(np.int32)
    p0,p1=rgb(c0),rgb(c1)
    four=(c0>c1)|(bs==16)
    p2=np.where(four[:,None],(2*p0+p1)//3,(p0+p1)//2); p3=np.where(four[:,None],(p0+2*p1)//3,0)
    pal=np.stack([p0,p1,p2,p3],1)  # n,4,3
    ii=(bits[:,None]>>(2*np.arange(16,dtype=np.uint32)))&3
    px=np.take_along_axis(pal,ii[...,None].astype(np.int64).repeat(3,-1),1)  # n,16,3
    if bs==8:
        al=np.where((~four[:,None])&(ii==3),0,255)
    elif fmt==0x87000000:
        a0=B[:,0].astype(np.int32); a1=B[:,1].astype(np.int32)
        ab=np.zeros(len(B),np.uint64)
        for j in range(6): ab|=B[:,2+j].astype(np.uint64)<<np.uint64(8*j)
        ai=((ab[:,None]>>(np.uint64(3)*np.arange(16,dtype=np.uint64)))&np.uint64(7)).astype(np.int64)
        k=np.arange(1,7)
        m8=np.concatenate([a0[:,None],a1[:,None],((7-k)[None]*a0[:,None]+k[None]*a1[:,None])//7],1)
        k4=np.arange(1,5)
        m6=np.concatenate([a0[:,None],a1[:,None],((5-k4)[None]*a0[:,None]+k4[None]*a1[:,None])//5,np.zeros((len(B),1),int),np.full((len(B),1),255)],1)
        apal=np.where((a0>a1)[:,None],m8,m6)
        al=np.take_along_axis(apal,ai,1)
    else:
        ab=np.zeros(len(B),np.uint64)
        for j in range(8): ab|=B[:,j].astype(np.uint64)<<np.uint64(8*j)
        al=(((ab[:,None]>>(np.uint64(4)*np.arange(16,dtype=np.uint64)))&np.uint64(15))*np.uint64(17)).astype(np.int64)
    out=np.concatenate([px,al[...,None]],-1).astype(np.uint8).reshape(bh,bw,4,4,4).transpose(0,2,1,3,4).reshape(bh*4,bw*4,4)
    return out[:h,:w]
_decode_slow=decode
def decode(d,t):
    r=_decode_fast(d,t)
    return r if r is not None else _decode_slow(d,t)
