import sys,os,glob,numpy as np
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from img_gface import NAMES,draw_outlined,APP,OUT,ROOT
from PIL import Image,ImageFont
F=ImageFont.truetype(ROOT+'/NanumSquareNeo-eHv.ttf',27)
pv=[]
for p in sorted(glob.glob(APP+'/grpdat/Winner/win_cha_*.gxt.gz')):
    k=os.path.basename(p)[8:11]; rel=os.path.relpath(p,APP).replace(chr(92),'/')
    d=gxt.load(p); t=gxt.textures(d)[0]; o=gxt.decode(d,t); a=o.copy(); h,w=a.shape[:2]
    rows=(a[:,:320,3]>0).any(1); y=h-1
    while y>0 and not rows[y]: y-=1
    yb=y
    while y>0 and rows[y]: y-=1
    yt=y+1
    xs=np.nonzero((a[yt:yb+1,:320,3]>0).any(0))[0]; xr=xs.max()
    print(k,yt,yb,xr)
    assert yb-yt<60
    a[yt:yb+1,:xr+1]=0
    im=Image.fromarray(a); draw_outlined(im,(xs.min()+3,yb-3),NAMES[k],F,r=3,anchor='ls')
    b=np.array(im); ch=np.nonzero((b!=o).any(-1)); blocks=set(zip((ch[1]//4).tolist(),(ch[0]//4).tolist()))
    nd=gxt.encode_blocks(d,t,b,blocks)
    os.makedirs(os.path.dirname(OUT+'/'+rel),exist_ok=True); gxt.save(OUT+'/'+rel,nd)
    pv.append(Image.fromarray(gxt.decode(nd,t)[h-70:,:400]))
sh=Image.new('RGBA',(400*2,70*7),(40,40,90,255))
for i,im in enumerate(pv): sh.alpha_composite(im,((i%2)*400,(i//2)*70))
sh.save(ROOT+'/work/img/winner_new.png')
