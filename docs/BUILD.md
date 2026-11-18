# 재빌드 방법

필요한 것:
- Python 3.11 이상, Pillow, NumPy, OpenCV(`opencv-python`)
- 원본 게임 폴더
- 복호화한 실행 파일(ELF)
- [글꼴](FONT_CREDITS.md)

1. 복호화된 게임 폴더 `PCSG00341`을 `emu/fs/ux0/app/PCSG00341/`에 둡니다. Vita3K에 설치했다면 그 폴더를 그대로 연결해도 됩니다.
2. 원본 `eboot.bin`을 복호화한 ELF를 `work/orig/eboot.elf`에 둡니다. 실기에서는 FAGDec 등으로 만들 수 있습니다.
3. 글꼴을 둡니다.
   - 나눔스퀘어네오, 서울한강체: 저장소 최상위 폴더
   - 갈무리11 Bold, 갈무리9: `work/`
4. 원문을 뽑고 번역을 입힌 뒤 빌드합니다. 결과는 `work/out/PCSG00341/`에 생깁니다.
   ```powershell
   cd tools
   python extract.py
   python textdiff.py apply
   python build.py
   ```
   - `extract.py`: 번역 대상 텍스트 295개를 `work/ja/`에 UTF-8로 뽑습니다.
   - `textdiff.py apply`: `work/ja/`에 `text/ko/`를 입혀 `work/ko/`를 만듭니다.
   - `build.py`: 텍스트·글꼴·실행 파일·그림 글자를 만듭니다. 노벨 갤러리 389쪽 때문에 10분 이상 걸릴 수 있습니다.
5. Vita3K 게임 폴더에 바로 넣어 시험하려면 `python build.py install`, 원본으로 되돌리려면 `python build.py restore`를 실행합니다. 원본은 처음 빌드할 때 `work/orig/`에 백업됩니다.

## 번역을 고칠 때

`work/ko/`의 텍스트를 고친 뒤 `python textdiff.py make`를 실행하면 `text/ko/`가 갱신됩니다. 노벨 번역은 `text/novel/`을 직접 고칩니다.

## 주의

노벨 갤러리 공통 종이 배경(`work/novel/bg.png`)은 처음 빌드할 때 자동으로 만듭니다. 릴리즈를 만들 때 쓴 배경은 얼룩을 손으로 정리한 것이라, 저장소만으로 빌드하면 노벨 쪽 결과 해시가 릴리즈와 다를 수 있습니다. 완성본은 릴리즈의 xdelta를 쓰세요.
