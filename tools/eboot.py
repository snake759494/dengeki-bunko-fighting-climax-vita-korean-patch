import struct,os,sys,json
sys.path.insert(0,os.path.dirname(__file__))
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
def TR(): return json.load(open(ROOT+'/text/eboot.json',encoding='utf-8'))
def enc(s,cmap):
    b=bytearray()
    for ch in s: b+=cmap[ch].to_bytes(2,'big') if ch in cmap else ch.encode('cp932')
    return bytes(b)
def build(cmap,out,sdk=None):
    elf=bytearray(open(ROOT+'/work/orig/eboot.elf','rb').read())
    # NUL로 둘러싸인 문자열마다 SHA-1을 계산해 번역표(원문 해시 -> 한국어)와 대조
    import hashlib
    T={h:(n,v) for h,n,v in TR()}; hit=set(); i=1
    while i<len(elf):
        j=elf.find(b'\0',i)
        if j<0: break
        if j>i and elf[i-1]==0:
            h=hashlib.sha1(bytes(elf[i:j])).hexdigest()
            if h in T:
                n,v=T[h]; vb=enc(v,cmap); assert len(vb)<=n,v
                elf[i:j]=vb+b'\0'*(n-len(vb)); hit.add(h)
        i=j+1
    for h in set(T)-hit: print('not found',T[h][1])
    # wrap as fself using original SELF header
    orig=open(ROOT+'/work/orig/eboot.bin','rb').read() if os.path.exists(ROOT+'/work/orig/eboot.bin') else open(ROOT+'/emu/fs/ux0/app/PCSG00341/eboot.bin','rb').read()
    if not os.path.exists(ROOT+'/work/orig/eboot.bin'): open(ROOT+'/work/orig/eboot.bin','wb').write(orig)
    hdr=bytearray(orig[:0x1000])
    phoff=struct.unpack_from('<I',elf,0x1c)[0]; phnum=struct.unpack_from('<H',elf,0x2c)[0]
    body=bytearray(); pos=0x1000
    for i in range(phnum):
        p=struct.unpack_from('<8I',elf,phoff+i*32); off,fsz=p[1],p[4]
        seg=elf[off:off+fsz]
        struct.pack_into('<QQQQ',hdr,0x180+i*32,pos,fsz,1,2)
        body+=seg; pos+=fsz
        pad=(-pos)%16; body+=b'\0'*pad; pos+=pad
    if sdk is not None: struct.pack_into('<H',hdr,8,sdk)
    struct.pack_into('<Q',hdr,0x20,pos)
    open(out,'wb').write(bytes(hdr)+bytes(body))
