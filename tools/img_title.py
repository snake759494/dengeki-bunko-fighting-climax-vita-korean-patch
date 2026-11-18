import os,sys,numpy as np
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from imgutil import text_img,fit_font,commit,APP,ROOT
from PIL import Image
EHV=ROOT+'/NanumSquareNeo-eHv.ttf'
def box(a,x0,y0,x1,y1,text,h,maxw,col=(255,255,255,255),ol=(0,0,0,255),r=0,shear=0.0,fillbg=True,cx=None):
    if fillbg: a[y0:y1,x0:x1]=[0,0,0,255]
    else: a[y0:y1,x0:x1]=0
    f=fit_font(EHV,text,maxw,h,ol=ol,r=r,shear=shear)
    t=np.array(text_img(text,f,fill=col,ol=ol,r=r,shear=shear))
    th,tw=t.shape[:2]; X=(x0+2) if cx=='L' else (x0+x1)//2-tw//2; Y=(y0+y1)//2-th//2
    im=Image.fromarray(a); im.alpha_composite(Image.fromarray(t),(X,Y)); a[:]=np.array(im)
def logo(rel,s,ox,oy):
    # s: 원본 타이틀 로고(1024x512) 대비 배율, ox/oy: 로고 원점 위치
    p=APP+'/'+rel; d=gxt.load(p); t=gxt.textures(d)[0]; o=gxt.decode(d,t); a=o.copy()
    S=lambda v:int(round(v*s)); X=lambda v:int(round(ox+v*s)); Y=lambda v:int(round(oy+v*s))
    box(a,X(255),Y(36),X(427),Y(76),'전격문고',max(8,S(40)),S(168))
    box(a,X(266),Y(306),X(554),Y(330),'파이팅 클라이맥스',max(7,S(21)),S(284),shear=0.18)
    return d,t,o,a
def main():
    rel='grpdat/Title/taitle_logo00.gxt.gz'
    d,t,o,a=logo(rel,1.0,0,0)
    # 저작권 표기의 가타카나 부분
    a[434:460,356:580]=0
    box(a,356,434,580,460,'아스키 미디어웍스',17,200,col=(255,255,255,255),ol=(0,0,0,255),r=2,shear=0.2,fillbg=False,cx='L')
    commit(rel,d,t,o,a)
    Image.fromarray(a).save(ROOT+'/work/c_title.png')
    for i,(rel,sc,ox,oy) in enumerate([('grpdat/System/demo_logo00.gxt.gz',0.44,31.4,33),('grpdat/Winner/winner_f00.gxt.gz',0.68,-41.2,486),('grpdat/exstorysel/dm_allc.gxt.gz',0.68,-55.2,103)]):
        d,t,o,a=logo(rel,sc,ox,oy); commit(rel,d,t,o,a); Image.fromarray(a).save(ROOT+'/work/c_logo%d.png'%i)
if __name__=='__main__': main()
