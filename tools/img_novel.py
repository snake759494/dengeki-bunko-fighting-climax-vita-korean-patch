# 스페셜 > 노벨 갤러리 본문(세로쓰기) 한글화
# text/novel/novelBB_PPP.txt (한 줄 = 한 문단)을 세로쓰기로 다시 그린다.
import os,sys,glob,numpy as np,cv2,gzip
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from imgutil import APP,ROOT,OUT
from PIL import Image,ImageDraw,ImageFont
KO=ROOT+'/text/novel'; FONT=ROOT+'/SeoulHangangM.ttf'
NREL='grpdat/Special/Novel/gallery_novel_vita'
ROT=set('「」『』…—―ー~～()（）-〜[]<>《》〈〉:：')
SMALLP=set('.,、。')
NOSTART=set('.,、。」』)）!?…—―')
CELLS=40; TOP=44.0; P0=23.75; C0=38.6; LEFTMIN=95
def dxt1_encode(img,bl):
    """img HxWx3 uint8(4배수 패딩), bl: (n,2) [bx,by] -> (n,8) uint8"""
    bx,by=bl[:,0],bl[:,1]
    yy=by[:,None]*4+np.repeat(np.arange(4),4)[None]; xx=bx[:,None]*4+np.tile(np.arange(4),4)[None]
    px=img[yy,xx].astype(float)                       # n,16,3
    lum=px@np.array([0.299,0.587,0.114]); n=len(bl); ar=np.arange(n)
    hi=px[ar,lum.argmax(1)]; lo=px[ar,lum.argmin(1)]
    def q(c): c=np.clip(c,0,255).astype(int); return ((c[:,0]*31+127)//255<<11)|((c[:,1]*63+127)//255<<5)|((c[:,2]*31+127)//255)
    def dq(v): return np.stack([((v>>11)&31)*255//31,((v>>5)&63)*255//63,(v&31)*255//31],-1).astype(float)
    c0,c1=q(hi),q(lo); sw=c0<c1; c0,c1=np.where(sw,c1,c0),np.where(sw,c0,c1)
    p0,p1=dq(c0),dq(c1); pal=np.stack([p0,p1,(2*p0+p1)/3,(p0+2*p1)/3],1)   # n,4,3
    idx=((px[:,:,None,:]-pal[:,None])**2).sum(-1).argmin(2)              # n,16
    idx=np.where((c0==c1)[:,None],0,idx).astype(np.uint64)
    bits=(idx<<(2*np.arange(16,dtype=np.uint64))[None]).sum(1).astype(np.uint32)
    out=np.zeros((n,8),np.uint8)
    out[:,0:2]=c0.astype('<u2').view(np.uint8).reshape(n,2); out[:,2:4]=c1.astype('<u2').view(np.uint8).reshape(n,2)
    out[:,4:8]=bits.astype('<u4').view(np.uint8).reshape(n,4); return out
def commit_fast(rel,d,t,orig,new):
    w,h=t['w'],t['h']; bw,bh=(w+3)//4,(h+3)//4
    ch=(new!=orig).any(-1); pad=np.zeros((bh*4,bw*4),bool); pad[:h,:w]=ch
    bm=pad.reshape(bh,4,bw,4).any((1,3)); by,bx=np.nonzero(bm); bl=np.stack([bx,by],1)
    img=np.zeros((bh*4,bw*4,3),np.uint8); img[:h,:w]=new[...,:3]
    enc=dxt1_encode(img,bl); idx,_,_=gxt.sworder(bw,bh)
    arr=np.frombuffer(d,np.uint8).copy(); offs=t['off']+idx[by,bx].astype(np.int64)*8
    arr[offs[:,None]+np.arange(8)[None]]=enc
    p=OUT+'/'+rel; os.makedirs(os.path.dirname(p),exist_ok=True)
    with gzip.open(p,'wb',compresslevel=6) as f: f.write(arr.tobytes())
_gc={}
def glyph(ch,size):
    k=(ch,size)
    if k in _gc: return _gc[k]
    f=ImageFont.truetype(FONT,size); S=size*2
    im=Image.new('L',(S,S),0); ImageDraw.Draw(im).text((S//2,S//2),ch,font=f,fill=255,anchor='mm')
    if ch in ROT: im=im.rotate(-90,resample=Image.BICUBIC)
    _gc[k]=np.array(im).astype(np.float32)/255; return _gc[k]
def layout(paras,scale,top=TOP):
    P=P0*scale; cells=int((CELLS*P0-(top-TOP))//P); cols=[]
    for para in paras:
        col=[]; pos=0.0; i=0
        while i<len(para):
            ch=para[i]
            if ch==' ':
                if pos>0: pos+=0.5
                i+=1; continue
            if pos+1>cells+0.01 and not (ch in NOSTART and pos<cells+0.6):
                cols.append(col); col=[]; pos=0.0
                continue
            col.append((ch,pos)); pos+=1; i+=1
        cols.append(col)
    return cols,P
def render(bg,paras,xt):
    x0,top=xt
    for scale in [1.0,0.97,0.94,0.91,0.88,0.85,0.82,0.79,0.76,0.73,0.7,0.66,0.62]:
        cols,P=layout(paras,scale,top); C=C0*scale
        if x0-(len(cols)-1)*C>=LEFTMIN: break
    size=max(10,round(21*scale)); a=bg.astype(np.float32); ink=np.array([28,24,24],np.float32)
    M=np.zeros(a.shape[:2],np.float32)
    for ci,col in enumerate(cols):
        cx=x0-ci*C
        for ch,pos in col:
            g=glyph(ch,size); S=g.shape[0]; cy=top+pos*P+P/2
            if ch in SMALLP: cx2,cy2=cx+size*0.42,cy-size*0.42
            else: cx2,cy2=cx,cy
            X=int(round(cx2-S/2)); Y=int(round(cy2-S/2))
            sub=M[max(0,Y):Y+S,max(0,X):X+S]; gs=g[max(0,-Y):max(0,-Y)+sub.shape[0],max(0,-X):max(0,-X)+sub.shape[1]]
            np.maximum(sub,gs,out=sub)
    a[...,:3]=a[...,:3]*(1-M[...,None])+ink*M[...,None]
    return a.astype(np.uint8),scale
def rightcol(o):
    d=(o[...,:3].astype(int).sum(-1)<250); d[940:,:820]=0
    c=d[30:1000].sum(0); xs=np.nonzero(c>40)[0]; xs=xs[(xs>150)&(xs<1700)]
    runs=[];st=xs[0];pv=xs[0]
    for x in xs[1:]:
        if x>pv+3: runs.append((st,pv)); st=x
        pv=x
    runs.append((st,pv)); runs=[r for r in runs if r[1]-r[0]>12]
    x0,x1=runs[-1]; ys=np.nonzero(d[:,x0:x1+1].sum(1)>2)[0]
    top=float(ys.min()) if len(ys) else TOP
    return (x0+x1)/2,(top if top>70 else TOP)
def mkbg(path):
    # 공통 종이 배경: 모든 책 본문 쪽의 화소별 중앙값(글자가 지워진 종이 바탕)
    st=[]
    for bdir in sorted(glob.glob(APP+'/'+NREL+'/gal_book*')):
        for p in sorted(glob.glob(bdir+'/novel*_*.gxt.gz'))[1:-1]:
            d=gxt.load(p); t=gxt.textures(d)[0]; st.append(gxt.decode(d,t)[...,:3])
    m=np.median(np.stack(st),0).astype(np.uint8); m=cv2.medianBlur(m,3)
    os.makedirs(os.path.dirname(path),exist_ok=True); Image.fromarray(m).save(path)
def main(only=None):
    BG=ROOT+'/work/novel/bg.png'
    if not os.path.exists(BG): mkbg(BG)
    bgall=np.array(Image.open(BG))
    rep=[]
    for bdir in sorted(glob.glob(APP+'/'+NREL+'/gal_book*')):
        b=bdir[-2:]
        if only and b not in only: continue
        pages=sorted(glob.glob(bdir+'/novel%s_*.gxt.gz'%b))[1:]
        if not all(os.path.exists(KO+'/novel%s_%s.txt'%(b,os.path.basename(p)[8:11])) for p in pages):
            print('book',b,'번역 미완료, 건너뜀'); continue
        data=[]
        for p in pages:
            d=gxt.load(p); t=gxt.textures(d)[0]; data.append((p,d,t,gxt.decode(d,t)))
        st=np.stack([x[3][...,:3] for x in data[:-1]]); k=np.abs(st.astype(np.int16)-bgall[None].astype(np.int16)).sum(-1).argmin(0)
        bg=np.take_along_axis(st,k[None,...,None],0)[0]; del st
        bgi=bg.astype(int)
        for p,d,t,o in data:
            pg=os.path.basename(p)[8:11]
            raw=open(KO+'/novel%s_%s.txt'%(b,pg),encoding='utf-8').read()
            if '[미번역]' in raw: print('원문 유지',b,pg); continue
            for k,v in {'〝':'「','〟':'」','・':'·','ー':'—'}.items(): raw=raw.replace(k,v)
            paras=[l.rstrip() for l in raw.strip('\n').split('\n')]
            if p==pages[-1]:   # 마지막 쪽: 표지 그림 + 안내문. 오른쪽 글 영역만 교체
                base=o[...,:3].copy(); base[:,950:]=bgall[:,950:]
            else: base=bg
            new,sc=render(base,paras,rightcol(o))
            # 쪽수 표시 <n/m> 는 원본 그대로
            new[968:,:150]=o[968:,:150,:3]
            na=np.dstack([new,np.full(new.shape[:2],255,np.uint8)])
            commit_fast(os.path.relpath(p,APP).replace(chr(92),'/'),d,t,o,na)
            rep.append((b,pg,sc))
            if sc<0.85: print('작게 축소됨',b,pg,sc)
    print('novel pages',len(rep))
if __name__=='__main__': main(sys.argv[1:] or None)
