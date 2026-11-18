# 스페셜 > 뮤직 곡 목록 한글화
import os,sys,numpy as np
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from imgutil import commit,APP,ROOT
from img_csel import comp
from img_misc import mask,put,BOLD
from PIL import Image,ImageDraw,ImageFont
SONGS=['콘솔판 테마송 「belief」','아케이드판 테마송 「FIGHTING CLIMAX」','전장의 발키리아 스테이지','버추어 파이터 5 스테이지','NiGHTS 스테이지',
'판타지 스타 온라인 2 스테이지','소닉 더 헤지혹 스테이지','세븐스 드래곤 2020 스테이지','Shinobi 스테이지','전뇌전기 버추얼 온 스테이지',
'보더 브레이크 스테이지','전장의 발키리아 스테이지(밤)','콘솔판 결전 스테이지','아케이드판 결전 스테이지','스토리: 일반 장면',
'스토리: 일상 장면','스토리: 긴장 장면','스토리: 비애 장면','스토리: 개그 장면','스토리: 행복 장면',
'콘솔판 타이틀','아케이드판 타이틀','메인 메뉴','네트워크 메뉴','스페셜 메뉴',
'캐릭터 선택','대전 개시 연출','대전 승리 연출','컨티뉴 연출','게임 오버 연출']
def main():
    rel='grpdat/Special/Music/gallery_musicmenu00.gxt.gz'
    d=gxt.load(APP+'/'+rel); t=gxt.textures(d)[0]; o=gxt.decode(d,t); a=o.copy()
    a[:]=0
    for i,s in enumerate(SONGS):
        y=6+32*i
        ti=Image.new('L',(512,32),0); ImageDraw.Draw(ti).text((4,2),s,font=ImageFont.truetype(BOLD,19),fill=255)
        M=np.zeros(a.shape[:2],np.uint8); M[y:y+32,:]=np.array(ti)
        comp(a,M,(255,255,255),(0,0,0),2)
    commit(rel,d,t,o,a)
    bg=Image.new('RGBA',(512,1024),(0,60,0,255)); bg.alpha_composite(Image.fromarray(a)); bg.save(ROOT+'/work/c.png')
if __name__=='__main__': main()
