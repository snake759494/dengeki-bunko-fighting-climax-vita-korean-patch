# 갤러리 캐릭터 이름(큰 글씨) 한글화
import os,sys,glob,numpy as np,cv2
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from imgutil import commit,APP,ROOT
from img_csel import comp
from img_scard import N
from PIL import Image,ImageDraw,ImageFont
HEAVY=ROOT+'/NanumSquareNeo-eHv.ttf'
N2=dict(N); N2.update({'hiw':'헤이와지마 시즈오','yak':'유키 아키라','kur':'흑설공주'})
def main():
    out=[]
    for p in sorted(glob.glob(APP+'/grpdat/Special/Illustration/gallery_chara/gallerycha_*00.gxt.gz')):
        b=os.path.basename(p); k=b[11:14].lower(); rel=os.path.relpath(p,APP).replace(chr(92),'/')
        d=gxt.load(p); t=gxt.textures(d)[0]; o=gxt.decode(d,t); a=o.copy()
        m=a[:95,:,3]>100; ys,xs=np.nonzero(m); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
        a[:95]=0
        f=ImageFont.truetype(HEAVY,64)
        ti=Image.new('L',(1400,140),0); ImageDraw.Draw(ti).text((6,6),N2.get(k,k),font=f,fill=255); tm=np.array(ti); yy,xx=np.nonzero(tm); tm=tm[yy.min():yy.max()+1,xx.min():xx.max()+1]
        th=y1-y0-6; tm=cv2.resize(tm,(int(tm.shape[1]*th/tm.shape[0]),th),interpolation=cv2.INTER_AREA)
        if tm.shape[1]>x1-8: tm=cv2.resize(tm,(x1-8,th),interpolation=cv2.INTER_AREA)
        M=np.zeros(a.shape[:2],np.uint8); M[y0+3:y0+3+th,x1-3-tm.shape[1]:x1-3]=tm
        comp(a,M,(255,255,255),(10,10,10),3)
        commit(rel,d,t,o,a); out.append(a[:100])
    sh=Image.new('RGBA',(512*3,100*((len(out)+2)//3)),(0,90,0,255))
    for i,c in enumerate(out): sh.alpha_composite(Image.fromarray(c),((i%3)*512,(i//3)*100))
    sh.resize((sh.width//2,sh.height//2)).save(ROOT+'/work/c.png')
if __name__=='__main__': main()
