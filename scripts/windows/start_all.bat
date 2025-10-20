@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: =====================================================
:: AI Manager - 一键启动（Python 可执行 + Java 后端）
:: 目录结构期望：
::   dist\ai-manager-core.exe
::   ai-manager-backend\runtime\jre\bin\java.exe（可选）
::   ai-manager-backend\target\ai-manager-backend-*.jar
:: =====================================================

set "ROOT=%~dp0..\.."
set "CORE_EXE=%ROOT%\dist\ai-manager-core.exe"

if exist "%CORE_EXE%" (
  echo 启动Python核心...
  start "AI Manager Core" "%CORE_EXE%"
) else (
  echo ⚠️ 未找到 %CORE_EXE%
  echo 若尚未打包Python核心，请在开发机执行 PyInstaller 打包。
)

:: 启动后端
call "%~dp0start_backend.bat"

exit /b %errorlevel%
