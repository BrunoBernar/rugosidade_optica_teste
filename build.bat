@echo off
chcp 65001 >nul
title Build - Estimador de Rugosidade Stellantis
color 0A

echo ============================================================
echo  BUILD - Estimador de Rugosidade Stellantis
echo ============================================================
echo.

:: Diretório do script
cd /d "%~dp0"

:: Verificar venv
set VENV_PYTHON=.venv\Scripts\python.exe
set VENV_PYINST=.venv\Scripts\pyinstaller.exe

if not exist "%VENV_PYTHON%" (
    echo [ERRO] Ambiente virtual nao encontrado em .venv\
    echo Execute: python -m venv .venv
    pause & exit /b 1
)

:: ─── PASSO 1: Baixar e gerar icone ──────────────────────────────────────────
echo [1/3] Gerando icone Stellantis...
"%VENV_PYTHON%" create_stellantis_icon.py
if errorlevel 1 (
    echo [AVISO] Falha ao baixar o icone. Verifique a internet.
    echo         O executavel sera gerado sem icone personalizado.
    set SPEC_ICON=
) else (
    echo [OK] stellantis.ico criado.
)
echo.

:: ─── PASSO 2: Gerar executavel com PyInstaller ──────────────────────────────
echo [2/3] Compilando executavel com PyInstaller...
"%VENV_PYINST%" Rugosidade_Stellantis.spec --noconfirm
if errorlevel 1 (
    echo [ERRO] Falha na compilacao. Veja mensagens acima.
    pause & exit /b 1
)
echo [OK] Executavel gerado em dist\Rugosidade_Stellantis.exe
echo.

:: ─── PASSO 3: Gerar instalador com Inno Setup ───────────────────────────────
echo [3/3] Gerando instalador Inno Setup...

:: Procurar ISCC em locais padrao
set ISCC=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if exist "C:\Program Files\Inno Setup 6\ISCC.exe"       set ISCC=C:\Program Files\Inno Setup 6\ISCC.exe

if "%ISCC%"=="" (
    echo [AVISO] Inno Setup nao encontrado.
    echo.
    echo  Para gerar o instalador:
    echo  1. Baixe o Inno Setup em: https://jrsoftware.org/isdl.php
    echo  2. Instale e execute novamente este script,  OU
    echo  3. Abra setup_rugosidade.iss no Inno Setup IDE e compile manualmente.
    echo.
) else (
    mkdir installer_output 2>nul
    "%ISCC%" setup_rugosidade.iss
    if errorlevel 1 (
        echo [ERRO] Falha ao gerar o instalador.
    ) else (
        echo [OK] Instalador gerado em installer_output\
    )
)

echo.
echo ============================================================
echo  Processo finalizado!
echo  Executavel: dist\Rugosidade_Stellantis.exe
if not "%ISCC%"=="" echo  Instalador: installer_output\Setup_Rugosidade_Stellantis_v1.0.0.exe
echo ============================================================
pause
