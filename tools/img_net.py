import sys,os,numpy as np
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from imgutil import *
ORDER=['샤나','아스나','키리토','미사카 미코토','코사카 키리노','흑설공주','아이사카 타이가','사토미 렌타로','히메라기 유키나','시바 미유키','미나토 토모카','헤이와지마 시즈오',None,'아키라','셀베리아']
# large plates
rel='grpdat/Network/net_meincha000.gxt.gz'; d=gxt.load(APP+'/'+rel); t=gxt.textures(d)[0]; o=gxt.decode(d,t); a=o.copy()
im=None
for i,n in enumerate(ORDER):
    if not n: continue
    y0=i*64; bb=erase_text(a,200,y0+12,400,y0+58,thr=200,sat=60,dil=5,rad=5)
    cx=(bb[0]+bb[2])//2; cy=(bb[1]+bb[3])//2
    f=fit_font(ROOT+'/NanumSquareNeo-eHv.ttf',n,200,30,r=2,shear=0.2,ol=(20,40,120,255))
    ti=text_img(n,f,r=2,shear=0.2,ol=(20,40,120,255))
    img=Image.fromarray(a); img.alpha_composite(ti,(cx-ti.width//2,cy-ti.height//2)); a=np.array(img)
nd=commit(rel,d,t,o,a); Image.fromarray(gxt.decode(nd,t)).save(ROOT+'/work/img/meincha_new.png')
# small icons
rel='grpdat/Network/net_chaicon000.gxt.gz'; d=gxt.load(APP+'/'+rel); t=gxt.textures(d)[0]; o=gxt.decode(d,t); a=o.copy()
G=ROOT+'/work/Galmuri9.ttf'
col=o[:,72:142].astype(int); wm=(o[:,72:142,3]>200)&(col[...,:3].min(-1)>200)&((col[...,:3].max(-1)-col[...,:3].min(-1))<40)
rows=wm.any(1); runs=[]; y=0
while y<len(rows):
    if rows[y]:
        s0=y
        while y<len(rows) and rows[y]: y+=1
        if y-s0>=5: runs.append((s0,y))
    y+=1
print(runs)
names=[n for n in ORDER if n]
runs=[(10+32*i,23+32*i) for i,n in enumerate(ORDER) if n]
for (r0,r1),n in zip(runs,names):
    bb=erase_text(a,72,r0-1,142,r1+1,thr=200,sat=40,dil=3,rad=3)
    f=fit_font(G,n,82,10,minsize=9,r=1)
    ti=text_img(n,f,r=1)
    img=Image.fromarray(a); img.alpha_composite(ti,(bb[2]+1-ti.width,(bb[1]+bb[3]+1)//2-ti.height//2)); a=np.array(img)
nd=commit(rel,d,t,o,a); Image.fromarray(gxt.decode(nd,t)).resize((288,1024),0).save(ROOT+'/work/img/chaicon_new.png')
