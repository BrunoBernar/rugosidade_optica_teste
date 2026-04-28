# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['BCI_STLA_main.py'],
    pathex=[],
    binaries=[],
    datas=[('stellantis.ico', '.')],
    hiddenimports=[
        'PIL._tkinter_finder',
        'reportlab.graphics.barcode.common',
        'reportlab.graphics.barcode.code39',
        'scipy.ndimage._ni_support',
        'pystray._win32',
        'pystray',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BCI_STLA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='stellantis.ico',
)
