@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"
title 전격문고 FIGHTING CLIMAX 한글패치 적용
echo ============================================
echo  전격문고 FIGHTING CLIMAX (PCSG00341) 한글패치
echo ============================================
echo.
set "XD="
for %%f in (xdelta3*.exe xdelta*.exe) do if not defined XD set "XD=%~dp0%%f"
if not defined XD (
  echo [오류] 이 폴더에 xdelta3.exe 가 없습니다.
  goto end
)
if not exist "PCSG00341\eboot.bin" (
  echo [오류] 원본 게임 폴더를 찾을 수 없습니다.
  echo 원본 PCSG00341 폴더를 이 파일과 같은 폴더에 넣어 주세요.
  echo   예: 적용하기.bat 옆에 PCSG00341\eboot.bin 이 있어야 합니다.
  goto end
)
if not exist "list.txt" (
  echo [오류] list.txt 가 없습니다.
  goto end
)
set /a ok=0, bad=0, n=0
echo 적용 중입니다. 몇 분 걸릴 수 있습니다...
for /f "usebackq tokens=1-3 delims=|" %%a in ("list.txt") do (
  set /a n+=1
  set "src=PCSG00341\%%a"
  set "out=한글패치\PCSG00341\%%a"
  set "pat=patch\PCSG00341\%%a.xdelta"
  if not exist "!src!" (
    echo [원본 없음] %%a
    set /a bad+=1
  ) else (
    set "h="
    for /f "skip=1 delims=" %%h in ('certutil -hashfile "!src!" MD5') do if not defined h set "h=%%h"
    set "h=!h: =!"
    if /i not "!h!"=="%%b" (
      echo [원본 불일치] %%a
      set /a bad+=1
    ) else (
      for %%d in ("!out!") do if not exist "%%~dpd" mkdir "%%~dpd"
      "!XD!" -d -f -s "!src!" "!pat!" "!out!"
      set "h="
      for /f "skip=1 delims=" %%h in ('certutil -hashfile "!out!" MD5') do if not defined h set "h=%%h"
      set "h=!h: =!"
      if /i "!h!"=="%%c" (
        set /a ok+=1
      ) else (
        echo [결과 불일치] %%a
        set /a bad+=1
      )
    )
  )
  set /a r=n %% 100
  if !r!==0 echo   !n! 개 처리...
)
echo.
echo 성공 !ok! / 전체 !n!, 문제 !bad!
echo.
if !bad!==0 (
  echo 완료되었습니다. 한글패치\PCSG00341 폴더의 내용을
  echo VitaShell 등으로 ux0:app/PCSG00341/ 에 덮어쓰기 복사하세요.
) else (
  echo 문제가 있는 파일이 있습니다. 원본이 일본판 PCSG00341 v1.00 인지 확인하세요.
)
:end
echo.
pause
