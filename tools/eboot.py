import struct,os,sys,json
sys.path.insert(0,os.path.dirname(__file__))
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
def TR(): return json.load(open(ROOT+'/text/eboot.json',encoding='utf-8'))
def enc(s,cmap):
    b=bytearray()
    for ch in s: b+=cmap[ch].to_bytes(2,'big') if ch in cmap else ch.encode('cp932')
    return bytes(b)
def build(cmap,out):
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
    # 원본 SELF 헤더로 FSELF를 만든다(FAGDec 방식).
    # 실기는 sdk_type 0xC0 이어야 평문 FSELF로 읽는다. NPDRM 정보와 앱 버전, 최소 펌웨어도 지운다.
    orig=open(ROOT+'/work/orig/eboot.bin','rb').read() if os.path.exists(ROOT+'/work/orig/eboot.bin') else open(ROOT+'/emu/fs/ux0/app/PCSG00341/eboot.bin','rb').read()
    if not os.path.exists(ROOT+'/work/orig/eboot.bin'): open(ROOT+'/work/orig/eboot.bin','wb').write(orig)
    open(out,'wb').write(wrap(elf,orig))
def wrap(elf,orig):
    hdr=bytearray(orig[:0x1000]); HL=struct.unpack_from('<Q',hdr,0x10)[0]
    struct.pack_into('<H',hdr,8,0xC0)                       # sdk_type: fself
    ai=struct.unpack_from('<Q',hdr,0x38)[0]; struct.pack_into('<Q',hdr,ai+0x10,0)   # appinfo.version
    # 원본 SELF 안의 ELF 헤더·프로그램 헤더를 그대로 쓰고, 세그먼트는 원본 오프셋에 놓는다(FAGDec 방식)
    o=struct.unpack_from('<Q',hdr,0x68)[0]
    while True:
        t,sz,nx=struct.unpack_from('<IIQ',hdr,o)
        if t==4: struct.pack_into('<I',hdr,o+0x4C,0)        # min_required_fw
        if t==5: hdr[o+0x10:o+sz]=bytes(sz-0x10)           # NPDRM 정보 제거
        if not nx: break
        o+=sz
    eo=struct.unpack_from('<Q',hdr,0x40)[0]; po=struct.unpack_from('<Q',hdr,0x48)[0]; so=struct.unpack_from('<Q',hdr,0x58)[0]
    ophoff=struct.unpack_from('<I',hdr,eo+0x1c)[0]; phnum=struct.unpack_from('<H',hdr,eo+0x2c)[0]
    phoff=struct.unpack_from('<I',elf,0x1c)[0]
    P=[struct.unpack_from('<8I',hdr,po+i*32) for i in range(phnum)]
    body=bytearray(max(p[1]+p[4] for p in P))
    body[0:0x34]=hdr[eo:eo+0x34]; body[ophoff:ophoff+phnum*32]=hdr[po:po+phnum*32]
    for i,p in enumerate(P):
        q=struct.unpack_from('<8I',elf,phoff+i*32); assert q[4]==p[4] and q[2]==p[2]
        body[p[1]:p[1]+p[4]]=elf[q[1]:q[1]+q[4]]
        struct.pack_into('<QQQQ',hdr,so+i*32,HL+p[1],p[4],1,2)
    struct.pack_into('<Q',hdr,0x18,len(body)); struct.pack_into('<Q',hdr,0x20,HL+len(body))
    return bytes(hdr)+bytes(body)
