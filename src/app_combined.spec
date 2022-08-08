# -*- mode: python ; coding: utf-8 -*-

import os
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
    pathex=['/pages/'],
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
    name='KeithleyDashApp'
)

home_a = Analysis(
    ['pages/home.py'],
    pathex=['/pages/home'],
    binaries=[],
    datas=[],
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

#filename = pkgutil.get_data('dat/CC', 'test.txt').decode('UTF-8', 'ignore')

CC_a = Analysis(
    ['pages/ConstantCurrent.py'],
    pathex=['/pages/ConstantCurrent'],
    binaries=[],
    datas=[],
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

IV_a = Analysis(
    ['pages/IV.py'],
    pathex=['/pages/IV'],
    binaries=[],
    datas=[],
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

PM_a = Analysis(
    ['pages/PulsedMode.py'],
    pathex=['/pages/PulsedMode'],
    binaries=[],
    datas=[],
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

MERGE( (home_a, 'home', 'home'), (CC_a, 'ConstantCurrent', 'ConstantCurrent'), (IV_a, 'IV', 'IV'), (PM_a, 'PulsedMode', 'PulsedMode') )

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

home_pyz = PYZ(home_a.pure, home_a.zipped_data, cipher=block_cipher)

CC_pyz = PYZ(CC_a.pure, CC_a.zipped_data, cipher=block_cipher)

IV_pyz = PYZ(IV_a.pure, IV_a.zipped_data, cipher=block_cipher)

PM_pyz = PYZ(PM_a.pure, PM_a.zipped_data, cipher=block_cipher)


exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
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
home_exe = EXE(
    home_pyz,
    home_a.scripts,
    [],
    exclude_binaries=True,
    name='home',
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
IV_exe = EXE(
    IV_pyz,
    IV_a.scripts,
    [],
    exclude_binaries=True,
    name='IV',
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
PM_exe = EXE(
    PM_pyz,
    PM_a.scripts,
    [],
    exclude_binaries=True,
    name='PulsedMode',
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
home_coll = COLLECT(
    home_exe,
    home_a.binaries,
    home_a.zipfiles,
    home_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='home',
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
IV_coll = COLLECT(
    IV_exe,
    IV_a.binaries,
    IV_a.zipfiles,
    IV_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='IV',
)
PM_coll = COLLECT(
    PM_exe,
    PM_a.binaries,
    PM_a.zipfiles,
    PM_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PulsedMode',
)