# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

# ========== Step 1: 收集 vosk 所有依赖 ==========
datas, binaries, hiddenimports = collect_all('vosk')

# ========== Step 2: 添加项目资源文件 ==========
extra_datas = [
    ('database', 'database'),
    ('Progress', 'Progress'),
    ('models', 'models'),           # Vosk 模型
    # ('.env', '.'),                  # 环境变量
]

# 合并到 datas
datas += extra_datas

# ========== Step 3: 排除不需要的包（可选，减小体积）==========
excludes = []

# ========== Step 4: Analysis ==========
a = Analysis(
    ['main.py'],                # 主入口脚本
    pathex=[],                      # 可添加额外 PYTHONPATH
    binaries=binaries,
    datas=datas,                    # 包括所有资源
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# ========== Step 5: 创建 PYZ ==========
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# ========== Step 6: EXE 输出配置 ==========
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI_Assistant_Launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                       # 建议安装 UPX 加速压缩
    upx_exclude=[],                 # 如 msvcr*.dll 等可排除
    console=True,                   # 开发阶段保留控制台日志
    #console=False,                # 发布时隐藏黑窗
)
