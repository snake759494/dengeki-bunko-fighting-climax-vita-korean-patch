import os,sys,re,gzip,json,shutil,struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,os.path.dirname(__file__)); import fnt
sys.stdout.reconfigure(encoding='utf-8')
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
APP=ROOT+'/emu/fs/ux0/app/PCSG00341'; ORIG=ROOT+'/work/orig'; OUT=ROOT+'/work/out/PCSG00341'
KO=os.environ.get('KO',ROOT+'/work/ko')
TTF=ROOT+'/NanumSquareNeo-cBd.ttf'; SIZE=20
def orig(p):
    o=ORIG+'/'+p
    if not os.path.exists(o):
        os.makedirs(os.path.dirname(o),exist_ok=True); shutil.copy2(APP+'/'+p,o)
    return o
def kofiles():
    for dp,dn,fn in os.walk(KO):
        for f in fn: yield os.path.relpath(os.path.join(dp,f),KO).replace(chr(92),'/')
def okslot(c):
    lo=c&0xff
    return 0x989f<=c<=0xeaa4 and not(lo==0x40 or 0x5b<=lo<=0x60 or 0x7b<=lo<=0x7f)
def main():
    files=list(kofiles()); texts={p:open(KO+'/'+p,encoding='utf-8',newline='').read() for p in files}
    from eboot import TR
    hang=sorted(set(ch for t in list(texts.values())+[x[2] for x in TR()] for ch in t if '\uac00'<=ch<='\ud7a3'))
    hdr,ents,tail=fnt.readfnt(orig('grpdat/Font/Font00.fnt'))
    slots=sorted([i for i,e in enumerate(ents) if okslot(e[0]) and e[6]>=21 and e[7]>=21],key=lambda i:ents[i][0])
    assert len(hang)<=len(slots),(len(hang),len(slots))
    m={ch:slots[k] for k,ch in enumerate(hang)}
    cmap={ch:ents[i][0] for ch,i in m.items()}
    json.dump({ch:hex(c) for ch,c in cmap.items()},open(ROOT+'/work/map.json','w',encoding='utf-8'),ensure_ascii=False)
    # text
    for p,t in texts.items():
        b=bytearray()
        for ch in t:
            if ch in cmap: b+=cmap[ch].to_bytes(2,'big')
            else: b+=ch.encode('cp932')
        orig(p); os.makedirs(os.path.dirname(OUT+'/'+p),exist_ok=True); open(OUT+'/'+p,'wb').write(b)
    # font
    F=ImageFont.truetype(TTF,SIZE)
    bypage={}
    for ch,i in m.items(): bypage.setdefault(ents[i][1],[]).append((ch,i))
    for pg,lst in bypage.items():
        gp='grpdat/Font/Font_%04d.gxt.gz'%pg
        d=bytearray(gzip.open(orig(gp)).read())
        off,size,typ,fmt,W,H=fnt.gxtinfo(d)
        A=fnt.decode_alpha(bytes(d)); touched=set()
        for ch,i in lst:
            e=ents[i]; _,_,_,_,_,sw,sh,u,v=e[1:]
            im=Image.new('L',(24,24),0); ImageDraw.Draw(im).text((1,0),ch,font=F,fill=255)
            a=np.array(im); ys,xs=np.nonzero(a)
            x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
            g=a[y0:y1,x0:x1]; gh,gw=g.shape
            assert gw<=sw and gh<=sh,(ch,gw,gh,sw,sh)
            A[v:v+sh,u:u+sw]=0; A[v:v+gh,u:u+gw]=g
            top=y0+1
            ents[i]=[e[0],pg,11,int(x0)-11,-int(top),22,gw,gh,u,v]
            for by in range(v//4,(v+sh+3)//4):
                for bx in range(u//4,(u+sw+3)//4): touched.add((bx,by))
        order=fnt.blockorder(W//4,H//4)
        for k,(bx,by) in enumerate(order):
            if (bx,by) in touched:
                px=[int(x) for x in A[by*4:by*4+4,bx*4:bx*4+4].reshape(-1)]
                d[off+k*16:off+k*16+16]=fnt.encode_alpha_block(px)+b'\xff\xff\xff\xff\0\0\0\0'
        os.makedirs(os.path.dirname(OUT+'/'+gp),exist_ok=True)
        with gzip.open(OUT+'/'+gp,'wb',compresslevel=6) as f: f.write(d)
    fnt.writefnt(hdr,ents,tail,OUT+'/grpdat/Font/Font00.fnt')
    import eboot; eboot.build(cmap,OUT+'/eboot.bin')
    import subprocess
    for sc in ['img_boot.py','img_gface.py','img_winner.py','img_net.py','img_title.py','img_csel.py','img_scard.py','img_gallery.py','img_misc.py','img_gsup.py','img_galsel.py','img_music.py','img_novel.py']:
        subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),sc)],check=True,stdout=subprocess.DEVNULL)
    print('files',len(files),'hangul',len(hang),'pages',sorted(bypage))
def install():
    for dp,dn,fn in os.walk(OUT):
        for f in fn:
            s=os.path.join(dp,f); shutil.copy2(s,APP+'/'+os.path.relpath(s,OUT))
def restore():
    for dp,dn,fn in os.walk(ORIG):
        for f in fn:
            s=os.path.join(dp,f); shutil.copy2(s,APP+'/'+os.path.relpath(s,ORIG))
if __name__=='__main__':
    c=sys.argv[1] if len(sys.argv)>1 else 'build'
    if c=='build': main()
    elif c=='install': main(); install()
    elif c=='restore': restore()
