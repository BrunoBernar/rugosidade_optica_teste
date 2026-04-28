@echo off
chcp 65001 >nul
title Build - BCI STLA
color 0A

echo ============================================================
echo  BUILD - BCI STLA v1.0.0
echo ============================================================
echo.

cd /d "%~dp0"

set VENV_PYTHON=.venv\Scripts\python.exe
set VENV_PYINST=.venv\Scripts\pyinstaller.exe

if not exist "%VENV_PYTHON%" (
    echo [ERRO] Ambiente virtual nao encontrado em .venv\
    echo Execute: python -m venv .venv  e  pip install -r requirements.txt
    pause & exit /b 1
)

:: ─── PASSO 1: Gerar icone ─────────────────────────────────────────────────────
echo [1/4] Gerando icone...
"%VENV_PYTHON%" BCI_STLA_icon.py
if errorlevel 1 (
    echo [AVISO] Falha ao gerar icone. Continuando sem icone personalizado.
) else (
    echo [OK] stellantis.ico criado.
)
echo.

:: ─── PASSO 2: Gerar manual PDF ───────────────────────────────────────────────
echo [2/4] Gerando manual PDF...
"%VENV_PYTHON%" BCI_STLA_manual.py
if errorlevel 1 (
    echo [AVISO] Falha ao gerar manual.pdf. O instalador sera gerado sem ele.
) else (
    echo [OK] manual.pdf criado.
)
echo.

:: ─── PASSO 3: Compilar executavel com PyInstaller ────────────────────────────
echo [3/4] Compilando executavel com PyInstaller...
"%VENV_PYINST%" BCI_STLA_build.spec --noconfirm
if errorlevel 1 (
    echo [ERRO] Falha na compilacao. Veja mensagens acima.
    pause & exit /b 1
)
echo [OK] Executavel gerado em dist\BCI_STLA.exe
echo.

:: ─── PASSO 4: Gerar instalador com Inno Setup ────────────────────────────────
echo [4/4] Gerando instalador Inno Setup...

set ISCC=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe"       set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"

if "%ISCC%"=="" (
    echo [AVISO] Inno Setup nao encontrado.
    echo.
    echo  Para gerar o instalador:
    echo  1. Baixe o Inno Setup em: https://jrsoftware.org/isdl.php
    echo  2. Instale e execute novamente este script, OU
    echo  3. Abra BCI_STLA_installer.iss no Inno Setup IDE e compile manualmente.
    echo.
) else (
    mkdir installer_output 2>nul
    "%ISCC%" BCI_STLA_installer.iss
    if errorlevel 1 (
        echo [ERRO] Falha ao gerar o instalador.
    ) else (
        echo [OK] Instalador gerado em installer_output\
    )
)

echo.
echo ============================================================
echo  Processo finalizado!
echo  Executavel : dist\BCI_STLA.exe
if not "%ISCC%"=="" echo  Instalador : installer_output\Setup_BCI_STLA_v1.0.0.exe
echo ============================================================
pause
