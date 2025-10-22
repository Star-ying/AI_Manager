@echo off
title Flutter中国镜像环境变量管理工具
color 0A

echo ========================================
echo    Flutter 中国镜像环境变量管理
echo ========================================
echo.

:menu
echo 请选择操作:
echo [1] 设置Flutter中国镜像环境变量
echo [2] 检查当前环境变量状态
echo [3] 删除Flutter镜像环境变量
echo [4] 验证Flutter环境
echo [5] 退出
echo.
set /p choice=请输入选择 (1-5): 

if "%choice%"=="1" goto set_env
if "%choice%"=="2" goto check_env
if "%choice%"=="3" goto remove_env
if "%choice%"=="4" goto verify_flutter
if "%choice%"=="5" goto exit
goto menu

:set_env
echo.
echo 正在设置Flutter中国镜像环境变量...
powershell -Command "[System.Environment]::SetEnvironmentVariable('PUB_HOSTED_URL', 'https://pub.flutter-io.cn', 'User')"
powershell -Command "[System.Environment]::SetEnvironmentVariable('FLUTTER_STORAGE_BASE_URL', 'https://storage.flutter-io.cn', 'User')"
echo ✅ 环境变量设置完成!
echo.
echo 注意: 需要重新启动命令提示符或PowerShell才能使用新的环境变量
echo.
pause
goto menu

:check_env
echo.
echo 检查Flutter镜像环境变量状态:
echo.
echo PUB_HOSTED_URL:
powershell -Command "[System.Environment]::GetEnvironmentVariable('PUB_HOSTED_URL', 'User')"
echo.
echo FLUTTER_STORAGE_BASE_URL:
powershell -Command "[System.Environment]::GetEnvironmentVariable('FLUTTER_STORAGE_BASE_URL', 'User')"
echo.
echo 当前会话环境变量:
echo PUB_HOSTED_URL = %PUB_HOSTED_URL%
echo FLUTTER_STORAGE_BASE_URL = %FLUTTER_STORAGE_BASE_URL%
echo.
pause
goto menu

:remove_env
echo.
echo 正在删除Flutter镜像环境变量...
powershell -Command "[System.Environment]::SetEnvironmentVariable('PUB_HOSTED_URL', $null, 'User')"
powershell -Command "[System.Environment]::SetEnvironmentVariable('FLUTTER_STORAGE_BASE_URL', $null, 'User')"
echo ✅ 环境变量已删除!
echo.
pause
goto menu

:verify_flutter
echo.
echo 验证Flutter环境和网络连接...
echo.
echo 检查Flutter版本:
flutter --version
echo.
echo 检查Flutter Doctor:
flutter doctor
echo.
echo 测试pub镜像连接:
flutter pub deps
echo.
pause
goto menu

:exit
echo.
echo 感谢使用Flutter中国镜像环境变量管理工具!
pause
exit