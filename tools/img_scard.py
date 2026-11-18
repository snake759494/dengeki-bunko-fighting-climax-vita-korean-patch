# 캐릭터 선택 소형 카드(s_chara) 이름 한글화
import os,sys,glob,numpy as np
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from imgutil import commit,APP,ROOT
from img_csel import NAME,comp
from PIL import Image,ImageDraw,ImageFont
import cv2
HEAVY=ROOT+'/NanumSquareNeo-eHv.ttf'
N=dict(NAME); N.update({'aen':'아이하라 엔쥬','akj':'아카츠키 코죠','alc':'알리시아','bog':'부기팝','crt':'셀티','dok':'도쿠로쨩','ero':'토와 에리오','har':'하루유키','hol':'호로','ino':'이노센트 참','izy':'오리하라 이자야','kgk':'카가 코코','kin':'키노','kro':'쿠로네코','lea':'리파','mas':'시이나 마시로','mou':'마오 사다오','pai':'파이','sbt':'시바 타츠야','tks':'타카스 류지','tom':'카미조 토우마','wil':'빌헬미나','acr':'액셀러레이터','yak':'아키라','slv':'셀베리아'})
def main():
    out=[]
    for p in sorted(glob.glob(APP+'/grpdat/CSel/s_chara/*.gxt.gz')):
        b=os.path.basename(p); k=b.split('_')[1][:3]; rel='grpdat/CSel/s_chara/'+b
        d=gxt.load(p); t=gxt.textures(d)[0]; o=gxt.decode(d,t); a=o.copy(); H,W=a.shape[:2]
        sc=W/1024 if W>=1024 else W/512
        y0r,y1r=int(118*H/256),int(180*H/256)
        sub=a[y0r:y1r,int(W*0.32) if W>=1024 else int(W*0.62):]; xoff=W-sub.shape[1]
        m=(sub[...,3]>120)&(sub[...,:3].max(-1)<185); ys,xs=np.nonzero(m)
        if not len(ys): print('skip',b); continue
        y0,y1,x0,x1=ys.min()+y0r,ys.max()+y0r,xs.min()+xoff,xs.max()+xoff
        if y1-y0>40: print('odd',b,y0,y1); continue
        a[y0-4:y1+4,x0-5:x1+4]=0
        hh=y1-y0+1; f=ImageFont.truetype(HEAVY,int(hh*1.15))
        ti=Image.new('L',(900,120),0); ImageDraw.Draw(ti).text((4,4),N[k],font=f,fill=255); tm=np.array(ti); yy,xx=np.nonzero(tm); tm=tm[yy.min():yy.max()+1,xx.min():xx.max()+1]
        maxw=x1-int(W*0.33 if W>=1024 else W*0.6)
        if tm.shape[1]>maxw: tm=cv2.resize(tm,(maxw,tm.shape[0]),interpolation=cv2.INTER_AREA)
        M=np.zeros((H,W),np.uint8); ty=y1-tm.shape[0]+1; M[ty:y1+1,x1-tm.shape[1]+1:x1+1]=tm
        comp(a,M,(40,40,40),(255,255,255),2)
        commit(rel,d,t,o,a); out.append(a[max(0,y0-10):y1+10,x1-260:x1+6].copy())
    sh=Image.new('RGBA',(270*4,60*((len(out)+3)//4)),(0,90,0,255))
    for i,c in enumerate(out): sh.alpha_composite(Image.fromarray(c).crop((0,0,266,min(60,c.shape[0]))),((i%4)*270,(i//4)*60))
    sh.save(ROOT+'/work/c.png')
if __name__=='__main__': main()
