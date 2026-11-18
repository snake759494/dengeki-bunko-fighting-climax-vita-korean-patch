import numpy as np,cv2,os,sys
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from PIL import Image,ImageDraw,ImageFont
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
os.makedirs(ROOT+'/work/img',exist_ok=True)
APP=ROOT+'/emu/fs/ux0/app/PCSG00341'; OUT=ROOT+'/work/out/PCSG00341'
def text_img(text,font,fill=(255,255,255,255),ol=(0,0,0,255),r=1,shear=0.0,spacing=0):
    bb=font.getbbox(text); W=bb[2]-bb[0]+2*r+8+int(abs(shear)*(bb[3]))+ (len(text)*spacing); H=bb[3]+2*r+6
    im=Image.new('RGBA',(W,H),(0,0,0,0)); dr=ImageDraw.Draw(im)
    def put(x,y,c):
        cx=x
        for ch in text:
            dr.text((cx,y),ch,font=font,fill=c); cx+=font.getlength(ch)+spacing
    if r:
        for dx in range(-r,r+1):
            for dy in range(-r,r+1):
                if dx*dx+dy*dy<=r*r+1 and (dx or dy): put(r+4-bb[0]+dx,r+3+dy,ol)
    put(r+4-bb[0],r+3,fill)
    if shear:
        im=im.transform((W,H),Image.AFFINE,(1,shear,-shear*H,0,1,0),resample=Image.BICUBIC)
    a=np.array(im); ys,xs=np.nonzero(a[...,3]); return Image.fromarray(a[ys.min():ys.max()+1,xs.min():xs.max()+1])
def fit_font(path,text,maxw,size,minsize=8,**kw):
    while size>minsize:
        f=ImageFont.truetype(path,size)
        if text_img(text,f,**kw).width<=maxw: return f
        size-=1
    return ImageFont.truetype(path,minsize)
def erase_text(a,x0,y0,x1,y1,thr=190,sat=50,dil=3,rad=4):
    sub=a[y0:y1,x0:x1].astype(int)
    m=((sub[...,:3].min(-1)>thr)&((sub[...,:3].max(-1)-sub[...,:3].min(-1))<sat)).astype(np.uint8)
    mask=np.zeros(a.shape[:2],np.uint8); mask[y0:y1,x0:x1]=cv2.dilate(m,np.ones((dil,dil),np.uint8))
    rgb=cv2.inpaint(np.ascontiguousarray(a[...,:3]),mask,rad,cv2.INPAINT_TELEA)
    a[...,:3]=np.where(mask[...,None]>0,rgb,a[...,:3])
    ys,xs=np.nonzero(m)
    return (xs.min()+x0,ys.min()+y0,xs.max()+x0,ys.max()+y0) if len(xs) else None
def commit(rel,d,t,orig,new):
    ch=np.nonzero((new!=orig).any(-1)); blocks=set(zip((ch[1]//4).tolist(),(ch[0]//4).tolist()))
    nd=gxt.encode_blocks(d,t,new,blocks)
    os.makedirs(os.path.dirname(OUT+'/'+rel),exist_ok=True); gxt.save(OUT+'/'+rel,nd); return nd
