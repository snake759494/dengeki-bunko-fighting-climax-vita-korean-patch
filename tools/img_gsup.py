# 전투 HUD 서포트 캐릭터 이름(gauge_support) 한글화 - 작은 글씨라 갈무리체 사용
import os,sys,glob,numpy as np
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from imgutil import commit,APP,ROOT
from img_scard import N
from img_gface import draw_outlined
from PIL import Image,ImageFont
F=ImageFont.truetype(ROOT+'/work/Galmuri11-Bold.ttf',12)
def main():
    pv=[]
    for p in sorted(glob.glob(APP+'/grpdat/Cockpit/gauge_support/*.gxt.gz')):
        b=os.path.basename(p); k=b[9:12]; rel=os.path.relpath(p,APP).replace(chr(92),'/')
        d=gxt.load(p); t=gxt.textures(d)[0]; o=gxt.decode(d,t); a=o.copy()
        m=a[128:190,:,3]>40; ys,xs=np.nonzero(m)
        if not len(ys): print('skip',b); continue
        y0,y1,x0,x1=ys.min()+128,ys.max()+128,xs.min(),xs.max()
        a[y0-1:y1+2,max(0,x0-2):x1+3]=0
        im=Image.fromarray(a); draw_outlined(im,((x0+x1)//2,y1),N[k],F,anchor='ms')
        a=np.array(im); commit(rel,d,t,o,a); pv.append(a[y0-6:y1+6,:])
    sh=Image.new('RGBA',(256*4,30*((len(pv)+3)//4)),(0,90,0,255))
    for i,c in enumerate(pv): sh.alpha_composite(Image.fromarray(c[:30]),((i%4)*256,(i//4)*30))
    sh.save(ROOT+'/work/c.png')
if __name__=='__main__': main()
