import sys,os,glob,numpy as np,cv2
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from PIL import Image,ImageDraw,ImageFont
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
os.makedirs(ROOT+'/work/img',exist_ok=True)
APP=ROOT+'/emu/fs/ux0/app/PCSG00341'; OUT=ROOT+'/work/out/PCSG00341'
NAMES=dict(asu='아스나',hiw='헤이와지마 시즈오',krn='코사카 키리노',krt='키리토',kur='흑설공주',mis='미사카 미코토',sbm='시바 미유키',
 sha='샤나',slv='셀베리아',stm='사토미 렌타로',tgr='아이사카 타이가',tmk='미나토 토모카',yak='아키라',ykn='히메라기 유키나')
F=ImageFont.truetype(ROOT+'/work/Galmuri11-Bold.ttf',12)
def draw_outlined(img,xy,text,font,fill=(255,255,255,255),ol=(0,0,0,255),r=1,anchor='ls'):
    dr=ImageDraw.Draw(img)
    for dx in range(-r,r+1):
        for dy in range(-r,r+1):
            if dx or dy: dr.text((xy[0]+dx,xy[1]+dy),text,font=font,fill=ol,anchor=anchor)
    dr.text(xy,text,font=font,fill=fill,anchor=anchor)
def patch(rel,x0,y0,x1,y1,text,font=F,preview=None):
    src=APP+'/'+rel; d=gxt.load(src); t=gxt.textures(d)[0]; a=gxt.decode(d,t).copy()
    sub=a[98:117,x0:x1].astype(int)
    m=(sub[...,:3].min(-1)>232)&((sub[...,:3].max(-1)-sub[...,:3].min(-1))<25)
    ys,xs=np.nonzero(m); bx1=min(xs.max()+x0,190); by1=116
    L=x0; R=bx1+4
    band=a[96:120,L:R+1].astype(int)
    tm=((band[...,:3].min(-1)>150)&((band[...,:3].max(-1)-band[...,:3].min(-1))<50)).astype(np.uint8)
    mask=np.zeros(a.shape[:2],np.uint8); mask[96:120,L:R+1]=cv2.dilate(tm,np.ones((3,3),np.uint8))
    rgb=cv2.inpaint(np.ascontiguousarray(a[...,:3]),mask,3,cv2.INPAINT_TELEA)
    a[...,:3]=np.where(mask[...,None]>0,rgb,a[...,:3])
    for x in range(L,R+1):
        al=min(1.0,(x-L)/14.0)*0.8
        for y in range(95,121):
            e=1.0 if 97<=y<=118 else 0.5
            a[y,x,:3]=(a[y,x,:3]*(1-al*e)).astype(np.uint8)
    im=Image.fromarray(a)
    draw_outlined(im,(bx1+1,by1),text,font,anchor='rs')
    b=np.array(im)
    ch=np.nonzero((b!=gxt.decode(d,t)).any(-1))
    blocks=set(zip((ch[1]//4).tolist(),(ch[0]//4).tolist()))
    nd=gxt.encode_blocks(d,t,b,blocks)
    if preview is not None: preview.append(Image.fromarray(gxt.decode(nd,t)).crop((0,60,220,140)))
    os.makedirs(os.path.dirname(OUT+'/'+rel),exist_ok=True); gxt.save(OUT+'/'+rel,nd)
if __name__=='__main__':
    pv=[]
    for p in sorted(glob.glob(APP+'/grpdat/Cockpit/gauge_face/*.gxt.gz')):
        n=os.path.basename(p); k=n[9:12]
        patch(os.path.relpath(p,APP).replace(chr(92),'/'),34 if '2p' in n else 36,92,200,120,NAMES[k],preview=pv)
    sh=Image.new('RGBA',(220*4,80*7),(40,40,90,255))
    for i,im in enumerate(pv): sh.alpha_composite(im,((i%4)*220,(i//4)*80))
    sh.resize((1760,1120),0).save(ROOT+'/work/img/gface_new.png')
