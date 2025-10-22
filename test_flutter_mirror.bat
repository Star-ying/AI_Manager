@echo off
title Flutter中国镜像测试工具
color 0A

echo ========================================
echo     Flutter 中国镜像连接测试
echo ========================================
echo.

REM 设置当前会话的环境变量
set PUB_HOSTED_URL=https://pub.flutter-io.cn
set FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn

echo 当前使用的镜像地址:
echo PUB_HOSTED_URL = %PUB_HOSTED_URL%
echo FLUTTER_STORAGE_BASE_URL = %FLUTTER_STORAGE_BASE_URL%
echo.

echo 测试项目:
echo [1/4] 检查Flutter版本...
flutter --version
echo.

echo [2/4] 检查Flutter Doctor状态...
flutter doctor --android-licenses >nul 2>&1
flutter doctor
echo.

echo [3/4] 进入UI目录...
cd /d "%~dp0UI"
if %errorlevel% neq 0 (
    echo ❌ 错误: 无法找到UI目录
    pause
    exit /b 1
)

echo [4/4] 测试依赖包下载速度...
echo 正在清理缓存...
flutter clean >nul 2>&1

echo 开始下载依赖包（这可能需要几分钟）...
set start_time=%time%
flutter pub get
set end_time=%time%

if %errorlevel% equ 0 (
    echo.
    echo ✅ 依赖包下载成功！
    echo 开始时间: %start_time%
    echo 结束时间: %end_time%
    echo.
    echo 🎉 Flutter中国镜像工作正常！
    echo 您现在可以正常使用Flutter开发了。
) else (
    echo.
    echo ❌ 依赖包下载失败！
    echo.
    echo 可能的原因:
    echo 1. 网络连接问题
    echo 2. 环境变量未正确设置
    echo 3. Flutter版本不兼容
    echo.
    echo 建议解决方案:
    echo 1. 运行 setup_flutter_mirror.bat 重新设置环境变量
    echo 2. 重启命令提示符
    echo 3. 检查网络连接
)

echo.
echo ========================================
echo              测试完成
echo ========================================
pause