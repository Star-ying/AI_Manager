@echo off
title Flutter中国镜像永久设置工具
color 0A

echo ========================================
echo   Flutter 中国镜像永久环境变量设置
echo ========================================
echo.

echo 本工具将为您的系统永久设置Flutter中国镜像环境变量
echo.
echo 设置的环境变量:
echo • PUB_HOSTED_URL = https://pub.flutter-io.cn
echo • FLUTTER_STORAGE_BASE_URL = https://storage.flutter-io.cn
echo.
echo 这些设置将:
echo ✅ 加速Flutter包下载
echo ✅ 解决国内网络访问问题
echo ✅ 永久保存到用户环境变量中
echo.

set /p confirm=确认设置？(Y/N): 
if /i "%confirm%" neq "Y" (
    echo 操作已取消
    pause
    exit
)

echo.
echo 正在设置环境变量...

REM 使用PowerShell设置用户级环境变量
powershell -Command "try { [System.Environment]::SetEnvironmentVariable('PUB_HOSTED_URL', 'https://pub.flutter-io.cn', 'User'); Write-Host '✅ PUB_HOSTED_URL 设置成功' } catch { Write-Host '❌ PUB_HOSTED_URL 设置失败: ' $_.Exception.Message }"

powershell -Command "try { [System.Environment]::SetEnvironmentVariable('FLUTTER_STORAGE_BASE_URL', 'https://storage.flutter-io.cn', 'User'); Write-Host '✅ FLUTTER_STORAGE_BASE_URL 设置成功' } catch { Write-Host '❌ FLUTTER_STORAGE_BASE_URL 设置失败: ' $_.Exception.Message }"

echo.
echo ========================================
echo            设置完成验证
echo ========================================
echo.

echo 验证环境变量设置:
echo.
echo PUB_HOSTED_URL:
powershell -Command "[System.Environment]::GetEnvironmentVariable('PUB_HOSTED_URL', 'User')"
echo.
echo FLUTTER_STORAGE_BASE_URL:
powershell -Command "[System.Environment]::GetEnvironmentVariable('FLUTTER_STORAGE_BASE_URL', 'User')"

echo.
echo ========================================
echo               重要提示
echo ========================================
echo.
echo ✅ 环境变量已成功设置到用户配置文件中
echo.
echo 📋 接下来的步骤:
echo 1. 关闭所有命令提示符和PowerShell窗口
echo 2. 重新打开命令提示符或PowerShell
echo 3. 运行 'flutter pub get' 测试是否生效
echo 4. 或者直接运行 start_music_app.bat 启动应用
echo.
echo 💡 如果想要验证设置是否生效，可以运行:
echo    flutter_mirror_manager.bat
echo.

pause