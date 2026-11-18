# 릴리즈 xdelta 묶음 적용 도구
#   python tools/apply_release.py --xdelta xdelta3.exe --source-dir <원본 PCSG00341 폴더> --patch-dir <압축 푼 xdelta 폴더> --output-dir <결과 폴더>
# release_manifest.json 의 원본 MD5를 확인한 뒤 xdelta를 적용하고, 결과 MD5를 검사합니다.
# 같은 이름의 출력 파일이 이미 있으면 덮어쓰지 않습니다.
import argparse,hashlib,json,os,subprocess,sys
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
def md5(p):
    h=hashlib.md5()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
ap=argparse.ArgumentParser()
ap.add_argument('--xdelta',default='xdelta3'); ap.add_argument('--source-dir',required=True)
ap.add_argument('--patch-dir',required=True); ap.add_argument('--output-dir',required=True)
ap.add_argument('--manifest',default=ROOT+'/release_manifest.json')
a=ap.parse_args(); m=json.load(open(a.manifest,encoding='utf-8')); bad=0
for e in m['files']:
    src=os.path.join(a.source_dir,e['target']); pat=os.path.join(a.patch_dir,e['patch']); out=os.path.join(a.output_dir,e['target'])
    if os.path.exists(out): print('건너뜀(이미 있음)',e['target']); continue
    if not os.path.exists(src) or md5(src)!=e['source_md5']: print('원본 불일치',e['target']); bad+=1; continue
    os.makedirs(os.path.dirname(out),exist_ok=True)
    subprocess.run([a.xdelta,'-d','-s',src,pat,out],check=True)
    if md5(out)!=e['output_md5']: print('결과 불일치',e['target']); bad+=1
print('완료' if not bad else '문제 %d건'%bad, len(m['files'])); sys.exit(1 if bad else 0)
