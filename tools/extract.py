import os,re,shutil
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
R=ROOT+'/emu/fs/ux0/app/PCSG00341'
def targets():
    out=[]
    for dp,dn,fn in os.walk(R):
        for f in fn:
            p=os.path.relpath(os.path.join(dp,f),R).replace(chr(92),'/')
            if not f.endswith(('.txt','.csv','.ini')): continue
            ok=(p.startswith('System/str_jp/') and 'bannedword' not in p) or \
               (p.startswith('BattleRes/talk/script/') and '__Test' not in p) or \
               p.startswith('BattleRes/win_mes/script/') or p.startswith('grpdat/command/') or \
               p.startswith('grpdat/Special/Illustration/') or p.startswith('grpdat/Network/') or p in ('bg/BgList.txt','System/BtlCharaTbl.txt','System/BtlCharaTbl_R.txt')
            if not ok: continue
            t=open(os.path.join(R,p),'rb').read().decode('cp932')
            if re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',re.sub(r'//.*','',t)): out.append(p)
    return sorted(out)
if __name__=='__main__':
    for p in targets():
        d=ROOT+'/work/ja/'+p; os.makedirs(os.path.dirname(d),exist_ok=True)
        t=open(os.path.join(R,p),'rb').read().decode('cp932')
        open(d,'w',encoding='utf-8',newline='').write(t)
    print(len(targets()))
