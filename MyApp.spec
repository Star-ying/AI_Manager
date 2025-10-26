# MyApp.spec - 修复 Vosk 打包问题版本
# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# 使用 hook 工具自动收集 vosk 及其二进制文件
datas, binaries, hiddenimports = collect_all('vosk')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,              # 👈 关键：加入 vosk 的 .dll/.so 文件
    datas=datas + [
        ('database', 'database'),
        ('Progress', 'Progress'),
        ('models','models'),
    ],
    hiddenimports=hiddenimports,    # 👈 自动包含 vosk 所需模块
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)
