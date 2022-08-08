# -*- mode: python ; coding: utf-8 -*-

import os.path

block_cipher = None

file = open(os.path.dirname(os.path.abspath("__file__"))  + '/dat/CC/test.txt', "r")
filename_CC = file.read()
file.close()

file = open(os.path.dirname(os.path.abspath("__file__"))  + '/dat/IV/test.txt', "r")
filename_IV = file.read()
file.close()

file = open(os.path.dirname(os.path.abspath("__file__"))  + '/dat/PM/test.txt', "r")
filename_PM = file.read()
file.close()

a = Analysis(
    ['app.py'],
    pathex=[],#'/pages/'],
    binaries=[],
    datas=[
            (os.path.dirname(os.path.abspath("__file__"))  +  '/dat/CC/test.txt', 'dat/CC'), 
            (os.path.dirname(os.path.abspath("__file__"))  +  '/dat/CC/' + filename_CC, 'dat/CC'),
            (os.path.dirname(os.path.abspath("__file__"))  +  '/dat/IV/test.txt', 'dat/IV'),
            (os.path.dirname(os.path.abspath("__file__"))  +  '/dat/IV/' + filename_IV, 'dat/IV'),
            (os.path.dirname(os.path.abspath("__file__"))  +  '/dat/PM/test.txt', 'dat/PM'),
            (os.path.dirname(os.path.abspath("__file__"))  +  '/dat/PM/' + filename_PM, 'dat/PM')
        ],
    hiddenimports=['pyvisa_py'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KeithleyDashApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
