# UKArc(.pac) 묶음 읽기·재구성, 서포트 캐릭터 말풍선(Support_SetMessage) 교체
# 헤더: "UKArc\0\0\0", u16 2, u16 0x1234, u32 항목 수
# 항목(0x4C): 이름 64바이트, u32 크기, u32 이름 해시(그대로 유지), u32 위치(실제 위치 = 값 + 0x10)
import gzip,json,os,re,struct
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
def read(d):
    n=struct.unpack_from('<I',d,12)[0]; E=[]
    for i in range(n):
        o=16+i*0x4c; a,b,c=struct.unpack_from('<3I',d,o+64)
        E.append([d[o:o+64],b,d[c+0x10:c+0x10+a]])
    return d[:16],E
def write(hdr,E):
    out=bytearray(hdr); pos=16+len(E)*0x4c; body=bytearray()
    for nm,b,blob in E:
        out+=nm+struct.pack('<3I',len(blob),b,pos-0x10); body+=blob; pos+=len(blob)
    return bytes(out+body)
def TR():
    p=ROOT+'/text/support.json'
    if not os.path.exists(p): p=ROOT+'/repo/text/support.json'
    return json.load(open(p,encoding='utf-8'))
PAT=re.compile(rb'(Support_SetMessage\(\s*")([^"]*)("\s*,\s*\d+\s*,\s*(\d+)\s*\))')
def patch(src,dst,tr,enc):
    raw=open(src,'rb').read(); d=gzip.decompress(raw)
    hdr,E=read(d); n=0
    for e in E:
        if not e[0].split(b'\0')[0].endswith(b'_mv.txt'): continue
        def rep(m):
            nonlocal n
            k=m.group(4).decode()
            if k not in tr: return m.group(0)
            n+=1; return m.group(1)+enc(tr[k])+m.group(3)
        e[2]=PAT.sub(rep,e[2])
    os.makedirs(os.path.dirname(dst),exist_ok=True)
    with gzip.open(dst,'wb',compresslevel=6) as f: f.write(write(hdr,E))
    return n
