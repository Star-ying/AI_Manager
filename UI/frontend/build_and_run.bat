@echo off
echo ======================================
echo AI音乐管理器 - 构建和运行脚本
echo ======================================
echo.

echo 正在检查Flutter环境...
flutter doctor
if %errorlevel% neq 0 (
    echo Flutter环境检查失败，请检查Flutter安装
    pause
    exit /b 1
)
echo.

echo 正在启用Windows桌面支持...
flutter config --enable-windows-desktop
echo.

echo 正在安装依赖...
flutter pub get
if %errorlevel% neq 0 (
    echo 依赖安装失败
    pause
    exit /b 1
)
echo.

echo 正在分析代码...
flutter analyze lib/main.dart
echo.

echo 尝试运行应用程序...
echo 注意：如果遇到符号链接错误，请：
echo 1. 按Win+I打开设置
echo 2. 进入"更新和安全" -> "开发者选项"
echo 3. 启用"开发者模式"
echo 4. 重启计算机后重新运行此脚本
echo.
echo 如果Nuget下载失败，请检查网络连接或稍后重试
echo.

flutter run -d windows --verbose

pause