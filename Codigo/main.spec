# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=["C:\\Users\\Usuario\\Documents\\Programa-Procesamiento-datos-pluviometricos-Grafana\\Codigo"],
    binaries=[],
    datas=[("./MONTEVIDEO.png", "."),("./Logo_Grupo_Tau.png", "."),("./Logo_imm.jpg", "."),("./Logo_Dica.png", "."), ("./Coordenadas_Equipos.csv", "Coordenadas_Equipos.csv"),  ("./Funciones_basicas.py", "."), ("./Funciones_mensual.py", "."), ("./Funciones_tormenta.py", "."), ("./interfaz.py", "."), ("./isoyetas.py", ".")],
    hiddenimports=[],
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
    name='main',
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
)
