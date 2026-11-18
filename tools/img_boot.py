import sys,os,numpy as np
sys.path.insert(0,os.path.dirname(__file__)); import gxt
from PIL import Image,ImageDraw,ImageFont
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
os.makedirs(ROOT+'/work/img',exist_ok=True)
rel='grpdat/BootLogo/PSVITA-BL.gxt.gz'
d=gxt.load(ROOT+'/emu/fs/ux0/app/PCSG00341/'+rel); t=gxt.textures(d)[0]
im=Image.new('RGBA',(960,544),(0,0,0,255)); dr=ImageDraw.Draw(im)
F=ImageFont.truetype(ROOT+'/NanumSquareNeo-cBd.ttf',26)
dr.text((480,155),'< 주의 >',font=F,fill=(255,255,255,255),anchor='mm')
L=['권리자의 허락 없이 게임 소프트웨어를 인터넷을 통해 전송·배포하는',
   '행위, 또한 위법한 인터넷 전송임을 알면서 다운로드하는 행위는',
   '법률로 엄격히 금지되어 있습니다.',
   '여러분의 이해와 협조를 부탁드립니다.']
for i,s in enumerate(L): dr.text((100,203+i*48),s,font=F,fill=(255,255,255,255),anchor='lm')
nd=gxt.encode_blocks(d,t,np.array(im),None)
os.makedirs(os.path.dirname(ROOT+'/work/out/PCSG00341/'+rel),exist_ok=True); gxt.save(ROOT+'/work/out/PCSG00341/'+rel,nd)
Image.fromarray(gxt.decode(nd,t)).save(ROOT+'/work/img/boot_new.png')
# HD(PS TV)판 1280x720
rel='grpdat/BootLogo/HD-BL.gxt.gz'
d=gxt.load(ROOT+'/emu/fs/ux0/app/PCSG00341/'+rel); t=gxt.textures(d)[0]
im=Image.new('RGBA',(1280,720),(0,0,0,255)); dr=ImageDraw.Draw(im)
F=ImageFont.truetype(ROOT+'/NanumSquareNeo-cBd.ttf',30)
dr.text((640,229),'< 주의 >',font=F,fill=(255,255,255,255),anchor='mm')
for i,s in enumerate(L): dr.text((170,281+i*52),s,font=F,fill=(255,255,255,255),anchor='lm')
nd=gxt.encode_blocks(d,t,np.array(im),None)
gxt.save(ROOT+'/work/out/PCSG00341/'+rel,nd)
Image.fromarray(gxt.decode(nd,t)).save(ROOT+'/work/img/boot_hd.png')
