# 번역 텍스트 <-> 원문 대비 차분(JSON) 변환
#   make : work/ja + work/ko  -> text/ko/<경로>.json  (바뀐 줄의 바뀐 구간만, 원문 없이 저장)
#   apply: work/ja + text/ko -> work/ko
import os,sys,json,difflib
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
JA,KO,TX=ROOT+'/work/ja',ROOT+'/work/ko',ROOT+'/text/ko'
def rd(p): return open(p,encoding='utf-8',newline='').read().split('\n')
def make():
    n=0
    for dp,dn,fn in os.walk(KO):
        for f in fn:
            r=os.path.relpath(os.path.join(dp,f),KO).replace(chr(92),'/')
            a,b=rd(JA+'/'+r),rd(KO+'/'+r); assert len(a)==len(b),r
            L=[]
            for i,(x,y) in enumerate(zip(a,b)):
                if x==y: continue
                ops=[[i1,i2,y[j1:j2]] for t,i1,i2,j1,j2 in difflib.SequenceMatcher(None,x,y,autojunk=False).get_opcodes() if t!='equal']
                L.append([i,ops])
            o=TX+'/'+r+'.json'; os.makedirs(os.path.dirname(o),exist_ok=True)
            json.dump(L,open(o,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':')); n+=1
    print('files',n)
def apply():
    n=0
    for dp,dn,fn in os.walk(TX):
        for f in fn:
            r=os.path.relpath(os.path.join(dp,f),TX).replace(chr(92),'/')[:-5]
            a=rd(JA+'/'+r)
            for i,ops in json.load(open(os.path.join(dp,f),encoding='utf-8')):
                x=a[i]; out=[]; pos=0
                for i1,i2,s in ops: out.append(x[pos:i1]); out.append(s); pos=i2
                out.append(x[pos:]); a[i]=''.join(out)
            o=KO+'/'+r; os.makedirs(os.path.dirname(o),exist_ok=True)
            open(o,'w',encoding='utf-8',newline='').write('\n'.join(a)); n+=1
    print('files',n)
if __name__=='__main__': {'make':make,'apply':apply}[sys.argv[1]]()
