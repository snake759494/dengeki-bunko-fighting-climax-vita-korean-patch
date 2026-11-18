# 캐릭터 선택 화면: 세로 프로필(_2), 세로 대사(_1), 이름(_1) 한글화
import os,sys,numpy as np,cv2
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from imgutil import text_img,fit_font,commit,APP,ROOT
from PIL import Image,ImageDraw,ImageFont
SERIF=ROOT+'/SeoulHangangEB.ttf'; HEAVY=ROOT+'/NanumSquareNeo-eHv.ttf'
ROT=set('「」『』（）()《》〈〉…―ー～~-─[]')
NAME={'asu':'아스나','hiw':'헤이와지마 시즈오','krn':'코사카 키리노','krt':'키리토','kur':'흑설공주','mis':'미사카 미코토','sbm':'시바 미유키','sha':'샤나','slv':'셀베리아','stm':'사토미 렌타로','tgr':'아이사카 타이가','tmk':'미나토 토모카','yak':'유키 아키라','ykn':'히메라기 유키나'}
PROF={
'asu':['《아인크라드》 안에서도 최강이라 이름난','길드 『혈맹기사단(KoB)』의 부단장.','레이피어 《램번트 라이트》를 구사하는','검술의 속도가 굉장해 《섬광》이라는 이명을','가졌다. 키리토의 연인.'],
'hiw':['늘 바텐더 복장을 한 빚 수금원.','비뚤어진 일이나 불합리한 일을 싫어하고,','화가 나면 이케부쿠로 최강이라 이름높다.','이케부쿠로에서 자판기나 표지판이','날아다니면 대개 그의 짓이다.'],
'krn':['스포츠 만능, 성적 우수, 용모 단정.','모든 게 완벽한 중학교 2학년 소녀.','단, 여동생 게임을 좋아한다는','초특수한 취미를 가졌다.','오빠 쿄스케와는 냉전 상태.'],
'krt':['《소드 아트 온라인》에서도 최강이라','이름 높은 《검은 검사》.','엑스트라 스킬 《이도류》를 구사해','《SAO》를 게임 클리어로 이끌었다.','아스나의 연인. 스구하라는 여동생이 있다.'],
'kur':['우메사토 중학교 학생회 부회장.','그 미모로 《흑설공주(스노 블랙)》','라고 불린다. 검은 레기온','《네가 네뷸러스》의 레기온 마스터.','듀얼 아바타는 《블랙 로터스》.'],
'mis':['토키와다이 중학교에 다니는 학생.','『초전자포(레일건)』라는 이명을 가진','고도의 전격 능력자(일렉트로마스터).','학원도시에서도 7명밖에 없는','초능력자(레벨5) 중 한 명.'],
'sbm':['시바 남매의 여동생. 1학년 A반 소속.','마법과 고교에 수석 입학한 엘리트.','『꽃잎(블룸)』이라 불리는','1과 학생으로, 특기 분야는 『냉각 마법』.','유일한 사랑스러운 결점은 『중증 브라콘』.'],
'sha':['"천양의 겁화" 알라스토르의','플레임헤이즈 『염발작안의 토벌자』.','사람의 존재를 먹는 "홍세의 무리" 토벌의','사명을 지녔다. 대태도 『니에토노샤나』를 다룬다.','멜론빵을 무척 좋아한다.'],
'slv':['막시밀리안에게 절대 충성을 맹세한 젊은 여성 지휘관으로,','「드라이 슈테른」 중 한 명. 고대 발키리아인의','피를 이었으며, 전장에서 발키리아의 방패와 창을','구사해 싸우는 그녀는 1개 중대에 필적한다고 한다.'],
'stm':['텐도 민간경비회사에 소속된 프로모터.','파트너인 이니시에이터 엔쥬와 함께','기생생물 가스트레아와 사투를 벌인다.','곤충 등 생물 마니아로, 주변 사람들에게는','「불행한 얼굴」이라 불린다.'],
'tgr':['가련한 용모와 정반대인 격한 성격 탓에','「손바닥 타이거」라 불리는 소녀.','빈틈없어 보이지만 실은 울보에 덜렁이.'],
'tmk':['어떤 사정으로 케이신 학원에 전학 온','농구부 에이스이자 유일한 경험자.','어머니는 일본무용, 아버지는 다도 선생님이라','늘 예의 바르고 성실한 성격이지만,','농구를 하게 되면……!?'],
'yak':['팔극권을 구사하며 오로지 강함을 좇는 열혈 무도가.','수행의 성과를 시험하고 좋은 적수와 싸우기 위해','제5회 세계격투 토너먼트에 출장. 우승을 노리며','격투를 벌인다. 머리띠가 트레이드마크.'],
'ykn':['제4진조를 감시하기 위해 사자왕기관에서','파견된 견습 검무녀.','고죠의 후배로 사이카이 학원 중등부에 재적.','흡혈귀의 진조조차 멸한다는 파마의 창','"설하랑"의 사용자.'],
}
TITLE={'asu':'소드 아트 온라인','krt':'소드 아트 온라인','hiw':'듀라라라!!','krn':'내 여동생이 이렇게 귀여울 리가 없어','kur':'액셀 월드','mis':'어떤 마술의 금서목록','sbm':'마법과 고교의 열등생','sha':'작안의 샤나','slv':'전장의 발키리아','stm':'블랙 불릿','tgr':'토라도라!','tmk':'로큐부!','ykn':'스트라이크 더 블러드'}
SUBF=ROOT+'/NanumSquareNeo-dEb.ttf'
def subtitle(a,k):
    if k not in TITLE: return
    m=a[600:,:840,3]>40; rr=m.sum(1); last=np.nonzero(rr)[0].max()
    gap=max(i for i in range(last) if rr[i]==0); lm=m[gap+1:last+1]; xs=np.nonzero(lm.any(0))[0]
    cx=(xs.min()+xs.max())//2; y=600+last+4
    def mk(t,sz):
        f=ImageFont.truetype(SUBF,sz); ti=Image.new('L',(900,60),0); ImageDraw.Draw(ti).text((4,4),t,font=f,fill=255)
        tm=np.array(ti); yy,xx=np.nonzero(tm); return tm[yy.min():yy.max()+1,xx.min():xx.max()+1]
    lw=xs.max()-xs.min(); tm=mk(TITLE[k],24)
    if tm.shape[1]>320:
        w=TITLE[k].split(' '); h=len(w)//2; l1,l2=mk(' '.join(w[:h]),22),mk(' '.join(w[h:]),22)
        W=max(l1.shape[1],l2.shape[1]); tm=np.zeros((l1.shape[0]+l2.shape[0]+5,W),np.uint8)
        tm[:l1.shape[0],(W-l1.shape[1])//2:(W-l1.shape[1])//2+l1.shape[1]]=l1
        tm[-l2.shape[0]:,(W-l2.shape[1])//2:(W-l2.shape[1])//2+l2.shape[1]]=l2
    y=min(y,846-tm.shape[0]); x=max(6,min(cx-tm.shape[1]//2,834-tm.shape[1]))
    M=np.zeros(a.shape[:2],np.uint8); M[y:y+tm.shape[0],x:x+tm.shape[1]]=tm
    comp(a,M,(255,255,255),(0,0,0),2)
QUOTE={
'asu':['「……나도. 나도, 절대로 너를 지킬게. 앞으로 영원히 지킬 테니까. 그러니까……」','「그래도, 나는 돌아가고 싶어. 왜냐면, 저쪽에서 못다 한 일이 잔뜩 있으니까」','「있지, 만약 네가 누군가와 결혼한 뒤에, 상대의 숨겨진 일면을 알게 되면, 넌 어떻게 생각해?」','「스토리지 공유화라니, 엄청 실용적인 시스템이지만, 동시에 무척 로맨틱하다고 나는 생각해」'],
'hiw':['「자기 인생을 생각하는 건 자유고 부정은 안 해. 하지만 말이야, 그 답을 남한테 구해서 어쩌자는 거야」','「나는――, 내 존재를 인정해도 되는 거지? 나를 좋아해도 되는 거지?」','「그리고 그렇게 부르지 말랬지. 나한텐 헤이와지마 시즈오라는 이름이 있다고~」','「게다가…나를 사랑해 주는 녀석 앞에서…쓰러질 수는 없잖아?」'],
'krn':['「이, 인생 상담이, 있어…….」','「……내가 너의 여동생이라서, 다행이야. ……너는?」','「하아? 뭘 진지한 얼굴로 떠드는 거야. 이제 와서 설교라니 진짜 짜증 나거든」','「그런 건 물건이 어떻든 상관없이, 자길 위해 뭔가 해 줬다는 게 중요한 거 아냐?」'],
'krt':['「내 목숨은 너의 것이야, 아스나. 그러니까 너를 위해 쓸게. 마지막 순간까지 함께 있자」','「말해 두는데 난 솔로야. 하루 두 번 오렌지가 될 만큼 겁낼 일은 아니라고」','「…너는…무슨 일이 있어도 돌려보내 줄게…저 세계로…」','「의심하고 후회하느니, 믿고 후회하자고! 가자!」'],
'kur':['「더 앞으로, 가속하고 싶지 않나? 소년」','「지금 이 순간이라면, 나의 마지막 말이라면, 믿어 주겠지」','「프로그램이 읽어 내는 건 이상이 아니라 열등감이니까」','「강함이란, 결코 결과로서의 승리만을 의미하는 게 아니야」'],
'mis':['「싸울 생각이 있으면 주먹을 쥐어, 싸울 생각이 없으면 막아서지 마!」','「그러니까, 부탁이니까! 부탁이니까, 네 힘으로 그 녀석의 꿈을 지켜 줘!」','「이를 악물어」','「――그래도 나는, 분명 네가 살아 주길 바라는 거라고 생각해」'],
'sbm':['「저는 오라버니를 업신여기지 않아요」','「설령 저 말고 모든 인류가 오라버니를 중상하고, 비방하고, 업신여긴다 해도, 저는 오라버니께 변함없는 경애를 바치겠어요」','「저는 오라버니만큼, 자비롭지 않아요」','「정말……오라버니는 심술쟁이」'],
'sha':['「무리인 건 무리인 거야!!」','「너 따위한테는 절대 안 져!」','「개인의 주관이 들어간 건, 정확한 분석과 논리적인 사고에 도움이 안 된다니까」','「그래. 너는 그냥 물건이야」'],
'slv':['「내 힘…을 똑똑히 깨닫게 해 주마!」','「기꺼이, 이 몸은 전하를 위해 존재합니다」','「전하의 대망에 보탬이 되고 싶은 겁니다!」','「이번에는……한 사람의 인간으로서! 지금껏 살아온 나 자신의 존재를 걸고!」'],
'stm':['「나도 이름을 대마, 카게타네. 전 육상자위대 동부방면대 제787기계화특수부대 『신인류창조계획』 사토미 렌타로」','「모두가 너처럼 생각할 수 있다면……정말 그렇게 생각해」','「선생님……난 그날부터 한 번도 선생님을 원망한 적 없어」','「어째서 넌 늘 무책임하게 그런 말을 하는 거야. 나는――」'],
'tgr':['「류지인 줄 알았어. 이럴 때 도우러 오는 건 분명 류지니까」','「류지는, 내 거어어어엇! 아무도 손대지 마아아아아앗!」','「닥쳐 그리고 썩어」','「얼마나 기다리는 자세인 거야. 충견 하치코냐?」'],
'tmk':['「내가 진다니―― 사소한 일이야! 지금은, 모두가 함께인걸……!」','「모두를 만나고, 스바루 씨를 만나서, 난 이렇게 지금도 농구를 좋아할 수 있어!」','「안 했어요! 도촬은 안 했어요!」','「싫어! 제한 시간은 안 정했는걸……안 져요! 그러니까 안 졌어요!」'],
'yak':['「이때를 기다렸다!」','「때가 왔다, 간다!」','「재대결하고 싶으면 와라!」','「십 년은 이르다고!」'],
'ykn':['「아뇨, 선배. 저희의 승리예요」','「물론이죠. 감시역이니까요」','「사자의 신자인 고신의 검무녀가 청하옵나니――」','「파마의 서광, 설하의 신랑, 강철의 신위로써 나에게 악신백귀를 토벌케 하소서!」'],
}
def glyph(ch,f):
    im=Image.new('L',(f.size*2,f.size*2),0); ImageDraw.Draw(im).text((f.size//2,f.size//2),ch,font=f,fill=255)
    if ch in ROT: im=im.rotate(-90,center=(f.size,f.size))
    return np.array(im)
def vcol(text,f,cw):
    """세로 한 줄의 글리프 마스크(폭 cw) 반환"""
    cells=[]
    for ch in text:
        if ch==' ': cells.append(np.zeros((f.size//2,cw),np.uint8)); continue
        g=glyph(ch,f); ys,xs=np.nonzero(g)
        if not len(ys): continue
        g=g[ys.min():ys.max()+1,xs.min():xs.max()+1]; h,w=g.shape
        if w>cw: g=cv2.resize(g,(cw,max(1,h*cw//w)),interpolation=cv2.INTER_AREA); h,w=g.shape
        c=np.zeros((max(h,f.size*3//10) if ch in '.,、。' else max(h,int(f.size*0.92)),cw),np.uint8)
        if ch in '.,、。': c[:h,cw-w:]=g
        else: oy=(c.shape[0]-h)//2; ox=(cw-w)//2; c[oy:oy+h,ox:ox+w]=g
        cells.append(c); cells.append(np.zeros((max(1,f.size//10),cw),np.uint8))
    return np.vstack(cells) if cells else np.zeros((1,cw),np.uint8)
def vblock(lines,font,size,xs,top,maxh,cw):
    masks=[]
    for ln in lines:
        s=size
        while True:
            m=vcol(ln,ImageFont.truetype(font,s),cw)
            if m.shape[0]<=maxh or s<=9: break
            s-=1
        masks.append(m)
    return masks
def wrapcols(text,font,size,maxh,cw,maxcols):
    while True:
        f=ImageFont.truetype(font,size); cols=[]; cur=''
        for w in text.split(' '):
            t=(cur+' '+w) if cur else w
            if vcol(t,f,cw).shape[0]<=maxh: cur=t; continue
            if cur: cols.append(cur); cur=''
            while vcol(w,f,cw).shape[0]>maxh:
                n=len(w)
                while vcol(w[:n],f,cw).shape[0]>maxh: n-=1
                cols.append(w[:n]); w=w[n:]
            cur=w
        if cur: cols.append(cur)
        if len(cols)<=maxcols or size<=12: return [vcol(c,f,cw) for c in cols]
        size-=1
def paste_mask(H,W,masks,xs,top):
    M=np.zeros((H,W),np.uint8)
    for m,x in zip(masks,xs):
        h=min(m.shape[0],H-top); M[top:top+h,x:x+m.shape[1]]=np.maximum(M[top:top+h,x:x+m.shape[1]],m[:h])
    return M
def comp(a,M,fill,ol,olr,glow=0):
    Mf=M.astype(np.float32)/255
    if glow:
        G=cv2.GaussianBlur(cv2.dilate(M,np.ones((3,3),np.uint8)),(0,0),glow).astype(np.float32)/255; G=np.clip(G*2.2,0,1)
    else:
        G=cv2.dilate(M,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*olr+1,2*olr+1))).astype(np.float32)/255
    A=np.maximum(G,Mf)
    rgb=np.array(ol,np.float32)*(1-Mf[...,None])+np.array(fill,np.float32)*Mf[...,None]
    sel=A>0
    da=a[...,3].astype(np.float32)/255; oa=A+da*(1-A)
    out=(rgb*A[...,None]+a[...,:3].astype(np.float32)*(da*(1-A))[...,None])/np.maximum(oa,1e-6)[...,None]
    a[sel,:3]=np.clip(out[sel],0,255).astype(np.uint8); a[sel,3]=(oa[sel]*255).astype(np.uint8)
def colx(n,right=1016,cw=18,pitch=32):
    return [right-cw+1-i*pitch for i in range(n)]
def main():
    for k in NAME:
        # 프로필(_2)
        rel='grpdat/CSel/chara/chara_%s_2.gxt.gz'%k; d=gxt.load(APP+'/'+rel); t=gxt.textures(d)[0]; o=gxt.decode(d,t); a=o.copy()
        a[:345,856:]=0
        masks=wrapcols(' '.join(PROF[k]),SERIF,19,330,18,5)
        comp(a,paste_mask(a.shape[0],a.shape[1],masks,colx(len(masks)),4),(255,255,255),(0,0,0),2)
        subtitle(a,k)
        commit(rel,d,t,o,a); prev=[a[:350,840:].copy()]
        # 대사·이름(_1)
        rel='grpdat/CSel/chara/chara_%s_1.gxt.gz'%k; d=gxt.load(APP+'/'+rel); t=gxt.textures(d)[0]; o=gxt.decode(d,t); a=o.copy()
        a[:722,893:]=0
        Q=QUOTE[k]; masks=vblock(Q,SERIF,20,None,6,708,18)
        comp(a,paste_mask(a.shape[0],a.shape[1],masks,colx(4,1017),6),(248,120,248),(235,10,140),0,glow=2.2)
        # 이름: 720~800 구간의 글자 bbox
        sub=a[722:768,60:600]; m=(sub[...,3]>60)&(sub[...,:3].max(-1)<90); ys,xs=np.nonzero(m)
        y0,y1,x0,x1=ys.min()+722,ys.max()+722,xs.min()+60,xs.max()+60
        wm=None
        a[max(722,y0-12):y1+7,x0-8:x1+9]=0
        f=ImageFont.truetype(HEAVY,y1-y0+3)
        ti=Image.new('L',(800,80),0); ImageDraw.Draw(ti).text((4,4),NAME[k],font=f,fill=255); tm=np.array(ti); yy,xx=np.nonzero(tm); tm=tm[yy.min():yy.max()+1,xx.min():xx.max()+1]
        hh=int((y1-y0+1)*1.1); tm=cv2.resize(tm,(max(1,tm.shape[1]*hh//tm.shape[0]),hh),interpolation=cv2.INTER_AREA)
        sh=int(hh*0.2); tm=cv2.warpAffine(tm,np.float32([[1,-0.2,sh],[0,1,0]]),(tm.shape[1]+sh,hh))
        mw=min(420,max(260,int((x1-x0)*1.5)))
        if tm.shape[1]>mw: tm=cv2.resize(tm,(mw,hh),interpolation=cv2.INTER_AREA)
        M=np.zeros(a.shape[:2],np.uint8); M[y1-tm.shape[0]+1:y1+1,x0:x0+tm.shape[1]]=tm
        comp(a,M,(10,10,10),(255,255,255),2)
        commit(rel,d,t,o,a); prev.append(a[:,840:].copy()); prev.append(a[700:820,:560].copy())
        if k in ('sha','slv','sbm'):
            for i,p in enumerate(prev):
                bg=Image.new('RGBA',(p.shape[1],p.shape[0]),(40,30,60,255)); bg.alpha_composite(Image.fromarray(p)); bg.save(ROOT+'/work/cs_%s%d.png'%(k,i))
if __name__=='__main__': main()
