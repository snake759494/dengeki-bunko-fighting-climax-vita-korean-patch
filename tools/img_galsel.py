# 스페셜 > 캐릭터 갤러리 선택 타일 이름판 한글화
import os,sys,numpy as np
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from imgutil import commit,APP,ROOT
from img_csel import comp
from img_misc import mask,put,BOLD
from PIL import Image
NAMES=['샤나','아스나','미사카 미코토','코사카 키리노','헤이와지마 시즈오','흑설공주','미나토 토모카','키리토','시바 미유키','아이사카 타이가',
 '히메라기 유키나','사토미 렌타로','아키라','셀베리아',None,'빌헬미나','리파','카미조 토우마','쿠로네코','셀티',
 '하루유키','이노센트 참','호로','카가 코코','부기팝','키노','시이나 마시로','토와 에리오','마오 사다오','시바 타츠야',
 '타카스 류지','아카츠키 코죠','아이하라 엔쥬','도쿠로쨩','액셀러레이터','오리하라 이자야','파이','알리시아']
def main():
    pv=[]
    for n in (0,1):
        rel='grpdat/Special/Illustration/Gallery_chasele0%d.gxt.gz'%n
        d=gxt.load(APP+'/'+rel); t=gxt.textures(d)[0]; o=gxt.decode(d,t); a=o.copy()
        for i,s in enumerate(NAMES):
            if not s: continue
            r,c=divmod(i,5); X0,Y0=c*240,r*240
            sub=a[Y0+188:Y0+219,X0+62:X0+180]
            m=(sub[...,:3].min(-1)>200)&(sub[...,3]>200); ys,xs=np.nonzero(m)
            y0,y1,x0,x1=Y0+188+ys.min(),Y0+188+ys.max(),X0+62+xs.min(),X0+62+xs.max()
            L,R=X0+58,X0+184
            for y in range(y0-7,y1+8):
                lc=a[y,L,:3].astype(float); rc=a[y,R,:3].astype(float)
                if lc.max()>110: lc=rc if rc.max()<=110 else np.array([8,8,50.])
                if rc.max()>110: rc=lc
                w=np.linspace(0,1,R-L)[:,None]
                a[y,L:R,:3]=(lc*(1-w)+rc*w).astype(np.uint8)
                seg=a[y,L:R,:3]; br=seg.max(-1)>70; seg[br]=(seg[br]*0.15+np.array([6,6,40])*0.85).astype(np.uint8)
            h=15; cx=X0+121
            comp(a,put(a,mask(s,BOLD,h,118),cx,(y0+y1)//2-7,'c'),(255,255,255),(30,90,255),0,glow=2.0)
        commit(rel,d,t,o,a); pv.append(a)
    for n,a in enumerate(pv):
        sh=Image.new('RGB',(5*170,8*45))
        bg=Image.new('RGBA',(1200,1920),(0,60,0,255)); bg.alpha_composite(Image.fromarray(a))
        for r in range(8):
            for c in range(5): sh.paste(bg.crop((c*240+35,r*240+175,c*240+205,r*240+220)),(c*170,r*45))
        sh.save(ROOT+'/work/g%d.png'%n)
if __name__=='__main__': main()
