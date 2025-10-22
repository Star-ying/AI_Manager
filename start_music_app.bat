@echo off
title AI Music Manager - Setup and Run
color 0A

echo ========================================
echo    AI Music Manager - Flutter App
echo ========================================
echo.

REM 设置Flutter中国镜像环境变量
echo [1/6] 设置Flutter中国镜像...
set PUB_HOSTED_URL=https://pub.flutter-io.cn
set FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn
echo ✅ Flutter中国镜像已设置

REM 检查Flutter是否已安装
echo.
echo [2/6] 检查Flutter环境...
flutter --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Flutter SDK!
    echo.
    echo 请按照以下步骤安装Flutter:
    echo 1. 访问 https://flutter.dev/docs/get-started/install/windows
    echo 2. 下载Flutter SDK
    echo 3. 解压到C:\flutter（或其他目录）
    echo 4. 将C:\flutter\bin添加到系统环境变量PATH中
    echo 5. 重新打开命令提示符
    echo.
    pause
    exit /b 1
)
echo ✅ Flutter环境检查通过

REM 启用Windows桌面支持
echo.
echo [3/6] 启用Windows桌面支持...
flutter config --enable-windows-desktop >nul 2>&1
echo ✅ Windows桌面支持已启用

REM 进入UI目录
echo.
echo [4/6] 准备项目环境...
cd /d "%~dp0UI"
if %errorlevel% neq 0 (
    echo ❌ 错误: 无法找到UI目录
    pause
    exit /b 1
)
echo ✅ 项目目录准备完成

REM 获取依赖
echo.
echo [5/6] 安装Flutter依赖包...
flutter pub get
if %errorlevel% neq 0 (
    echo ❌ 错误: 依赖包安装失败
    pause
    exit /b 1
)
echo ✅ 依赖包安装完成

REM 检查Windows设备
echo.
echo [6/6] 检查Windows设备支持...
flutter devices | findstr "Windows" >nul
if %errorlevel% neq 0 (
    echo ⚠️  警告: 未检测到Windows设备支持
    echo 正在尝试强制启用...
    flutter config --enable-windows-desktop
)

echo.
echo ========================================
echo         准备启动应用程序...
echo ========================================
echo.
echo 🎵 AI Music Manager 即将启动
echo.
echo 使用说明:
echo • 点击"选择音乐文件夹"选择包含音乐的文件夹
echo • 支持格式: MP3, WAV, M4A, FLAC
echo • 点击播放列表中的歌曲开始播放
echo • 使用音量滑块调节音量
echo • 点击麦克风图标进行语音控制
echo.
echo 语音命令示例:
echo • "播放 [歌曲名]"
echo • "暂停" / "继续"
echo • "下一首" / "上一首"
echo • "音量大一点" / "音量小一点"
echo.

timeout /t 3 >nul

REM 启动应用
echo 🚀 正在启动应用...
echo.
flutter run -d windows --release

if %errorlevel% neq 0 (
    echo.
    echo ❌ 应用启动失败!
    echo.
    echo 可能的解决方案:
    echo 1. 确保已安装Visual Studio 2019或更高版本
    echo 2. 确保已安装"C++ CMake tools for Visual Studio"
    echo 3. 运行 'flutter doctor' 检查环境
    echo 4. 尝试运行 'flutter clean' 然后重新运行此脚本
    echo.
) else (
    echo.
    echo ✅ 应用已成功启动!
)

echo.
pause