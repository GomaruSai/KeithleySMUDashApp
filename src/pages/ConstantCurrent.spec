# -*- mode: python ; coding: utf-8 -*-

import os
import os.path

block_cipher = None


#filen = pkgutil.get_data('/../dat/CC', 'test.txt')
#filename = filen.decode('UTF-8', 'ignore')

file = open(os.path.dirname(os.path.abspath("__file__"))  + '/../dat/CC/test.txt', "r")
filename = file.read()
file.close()

CC_a = Analysis(
    ['ConstantCurrent.py'],
    pathex=['/pages/ConstantCurrent'],
    binaries=[],
    datas=[(os.path.dirname(os.path.abspath("__file__"))  +  '/../dat/CC/test.txt', 'dat/CC'), (os.path.dirname(os.path.abspath("__file__"))  +  '/../dat/CC/' + filename, 'dat/CC')],
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


CC_pyz = PYZ(CC_a.pure, CC_a.zipped_data, cipher=block_cipher)

CC_exe = EXE(
    CC_pyz,
    CC_a.scripts,
    [],
    exclude_binaries=True,
    name='ConstantCurrent',
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
CC_coll = COLLECT(
    CC_exe,
    CC_a.binaries,
    CC_a.zipfiles,
    CC_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ConstantCurrent',
)
