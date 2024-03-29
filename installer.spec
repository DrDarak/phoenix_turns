# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('phoenix_32x32.png', '.'), ('phoenix.ico', '.'), ('colour_scheme.json', '.'),('LICENSE', '.'), ('phoenix.js', '.'), ('tick.png', '.'), ('main.css', '.'), ('tree.css', '.'), ('tree.js', '.'), ('turns.css', '.'), ('./images/black/*', 'images/black'), ('./images/blue/*', 'images/blue'), ('./images/gold/*', 'images/gold'), ('./images/green/*', 'images/green'), ('./images/pink/*', 'images/pink'), ('./images/purple/*', 'images/purple'),  ('./images/salmon/*', 'images/salmon')],
    hiddenimports=[],
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
    name='phoenix_turns',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='phoenix.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
