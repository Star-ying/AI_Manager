@echo off
echo Building AI小助手 for Windows...

REM 检查Flutter是否已安装
where flutter >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Flutter is not installed or not in PATH.
    pause
    exit /b 1
)

REM 创建构建目录
if not exist build mkdir build
cd build

REM 清理之前的构建
echo Cleaning previous builds...
flutter clean

REM 获取Windows依赖
echo Getting Windows dependencies...
flutter pub get

REM 为X64架构构建
echo Building for Windows x64...
flutter build windows --release --target-platform windows-x64
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to build for Windows x64.
    pause
    exit /b 1
)

REM 为ARM64架构构建
echo Building for Windows ARM64...
flutter build windows --release --target-platform windows-arm64
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to build for Windows ARM64.
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo X64 build: build\windows\x64\runner\Release\
echo ARM64 build: build\windows\arm64\runner\Release\
echo.
pause