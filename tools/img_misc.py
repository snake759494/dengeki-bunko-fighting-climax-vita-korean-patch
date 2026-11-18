# 기타 UI 이미지 한글화(모드 설명, 이름 목록, 연승, 모드 목록)
import os,sys,numpy as np,cv2
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from imgutil import commit,APP,ROOT,OUT,erase_text
from img_csel import comp
from PIL import Image,ImageDraw,ImageFont
HEAVY=ROOT+'/NanumSquareNeo-eHv.ttf'; BOLD=ROOT+'/NanumSquareNeo-dEb.ttf'; REG=ROOT+'/NanumSquareNeo-cBd.ttf'
def mask(text,font,h,maxw=None,shear=0.0):
    f=ImageFont.truetype(font,max(8,int(h*1.5)))
    ti=Image.new('L',(2400,int(h*3)),0); ImageDraw.Draw(ti).text((8,4),text,font=f,fill=255)
    if shear: ti=ti.transform(ti.size,Image.AFFINE,(1,shear,-shear*ti.size[1]*0.6,0,1,0),resample=Image.BICUBIC)
    tm=np.array(ti); yy,xx=np.nonzero(tm); tm=tm[yy.min():yy.max()+1,xx.min():xx.max()+1]
    # 한글 기준 높이를 h로
    tm=cv2.resize(tm,(max(1,int(tm.shape[1]*h/tm.shape[0])),h),interpolation=cv2.INTER_AREA)
    if maxw and tm.shape[1]>maxw: tm=cv2.resize(tm,(maxw,h),interpolation=cv2.INTER_AREA)
    return tm
def put(a,tm,x,y,align='l'):
    M=np.zeros(a.shape[:2],np.uint8); h,w=tm.shape
    if align=='r': x=x-w
    if align=='c': x=x-w//2
    M[y:y+h,x:x+w]=tm; return M
def load(rel):
    d=gxt.load(APP+'/'+rel); t=gxt.textures(d)[0]; o=gxt.decode(d,t); return d,t,o,o.copy()
def rowbox(a,y0,y1,x0=0,x1=None):
    m=a[y0:y1,x0:x1,3]>100; ys,xs=np.nonzero(m); return x0+xs.min(),y0+ys.min(),x0+xs.max(),y0+ys.max()
MODE_DESC=['일반 모드입니다. 캐릭터의','스토리를 따라가며 클리어를 목표로 합니다.','점수를 겨루는 모드입니다.','평소보다 IP를 얻기 쉽습니다.','클리어 타임을 겨루는 모드입니다.','평소보다 IP를 얻기 쉽습니다.','자유롭게 연습할 수 있는 모드입니다.','1크레딧으로 7분 정도 자유롭게 연습할 수 있습니다.','첫 대전 캐릭터를 선택해 주세요.','이후로는 순서대로 대전하게 됩니다.','상대 캐릭터를 선택해 주세요.','트레이닝을 시작하면 변경할 수 없습니다.']
MAIN=['샤나','아스나','키리토','미사카 미코토','코사카 키리노','흑설공주','아이사카 타이가','사토미 렌타로','히메라기 유키나','시바 미유키','미나토 토모카','헤이와지마 시즈오',None,'아키라','셀베리아']
SUP=['빌헬미나','리파','카미조 토우마','쿠로네코','시바 타츠야','타카스 류지','아이하라 엔쥬','아카츠키 코죠','셀티','호로','카가 코코','하루유키','부기팝','이노센트 참','키노','시이나 마시로','토와 에리오','마오 사다오','파이','알리시아','도쿠로쨩','액셀러레이터','오리하라 이자야']
def main():
    prev=[]
    # 모드 설명
    rel='grpdat/BattleResult/modesele_m00.gxt.gz'; d,t,o,a=load(rel)
    for i,s in enumerate(MODE_DESC):
        y0=4+32*i if i<11 else 354
        a[y0-2:y0+28]=0
        comp(a,put(a,mask(s,REG,19,500),6,y0+3),(255,255,255),(0,0,0),2)
    commit(rel,d,t,o,a); prev.append(a[:390])
    # 캐릭터 이름 목록(메인)
    rel='grpdat/Customize/custom_name00.gxt.gz'; d,t,o,a=load(rel)
    for i,s in enumerate(MAIN):
        if not s: continue
        y0=5+32*i if i<12 else 5+32*i-4
        x0,yy0,x1,yy1=rowbox(a,y0-3,y0+25)
        a[yy0-4:yy1+5]=0
        comp(a,put(a,mask(s,BOLD,yy1-yy0-1,370),x0,yy0+1),(255,255,255),(40,0,200),2)
    commit(rel,d,t,o,a); prev.append(a)
    # 서포트 이름 목록
    rel='grpdat/Customize/custom_name01.gxt.gz'; d,t,o,a=load(rel)
    for i,s in enumerate(SUP):
        y0=36+32*i
        a[y0-3:y0+26,108:]=0
        comp(a,put(a,mask(s,BOLD,13,260),116,y0+5),(255,255,255),(40,0,200),2)
    commit(rel,d,t,o,a); prev.append(a[:,:384])
    # 모드 목록(가타카나)
    rel='grpdat/BattleResult/modesele00.gxt.gz'; d,t,o,a=load(rel)
    for i,s in enumerate(['노멀 모드','스코어 어택 모드','타임 어택 모드','트레이닝 모드','서바이벌 모드']):
        y0=158+32*i
        x0,yy0,x1,yy1=rowbox(a,y0,y0+31,380,720)
        a[yy0-2:yy1+3,x0-3:x1+4]=0
        comp(a,put(a,mask(s,HEAVY,yy1-yy0-4,x1-x0,shear=0.2),x0,yy0+2),(255,255,255),(0,0,0),2)
    x0,yy0,x1,yy1=rowbox(a,30,46,420,620); a[yy0-1:yy1+2,x0-2:x1+3]=0
    comp(a,put(a,mask('모드 선택',REG,yy1-yy0,x1-x0),x0,yy0),(255,255,255),(0,0,0),1)
    commit(rel,d,t,o,a); prev.append(a[:320,300:760])
    # 연승
    rel='grpdat/Winner/winner_f00.gxt.gz'; import img_title; img_title.main(); d=gxt.load(OUT+'/'+rel); t=gxt.textures(d)[0]; o=gxt.decode(d,t); a=o.copy()
    for (x0,x1,Y0,Y1),fill,gl in [((737,856,517,570),(255,215,205),(235,30,40)),((742,861,614,667),(255,235,140),(240,120,0))]:
        m=np.zeros(a.shape[:2],np.uint8); m[Y0-5:Y1+6,x0-6:x1+7]=1
        a[...,:3]=np.where(m[...,None]>0,cv2.inpaint(np.ascontiguousarray(a[...,:3]),m,6,cv2.INPAINT_TELEA),a[...,:3])
        tm=mask('연승',HEAVY,Y1-Y0-4,x1-x0,shear=0.18)
        comp(a,put(a,tm,(x0+x1)//2,Y0+2,'c'),fill,gl,0,glow=2.0)
    commit(rel,d,t,o,a); prev.append(a[480:680,540:960])
    # 네트워크 상태 라벨
    rel='grpdat/Network/net_sozai000.gxt.gz'; d,t,o,a=load(rel)
    for (x0,x1,cx),s in [((56,152,101),'대기 중'),((231,376,304),'대전 준비 중'),((463,556,508),'대전 중'),((666,760,711),'관전 중')]:
        for y in range(192,221):
            L=a[y,x0-1,:3].astype(float); R=a[y,x1,:3].astype(float); w=np.linspace(0,1,x1-x0)[:,None]
            a[y,x0:x1,:3]=(L*(1-w)+R*w).astype(np.uint8)
        comp(a,put(a,mask(s,HEAVY,16,150),cx,198,'c'),(255,255,255),(0,0,0),1)
    commit(rel,d,t,o,a); prev.append(a[185:225,:800])
    for i,p in enumerate(prev):
        bg=Image.new('RGBA',(p.shape[1],p.shape[0]),(0,70,0,255)); bg.alpha_composite(Image.fromarray(p)); bg.save(ROOT+'/work/m%d.png'%i)
if __name__=='__main__': main()
