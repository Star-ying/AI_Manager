@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: =====================================================
:: AI Manager - 启动Java后端（内置JRE优先）
:: 目录结构期望：
::   ai-manager-backend\target\ai-manager-backend-*.jar
::   ai-manager-backend\runtime\jre\bin\java.exe
:: =====================================================

set "BASE=%~dp0..\..\ai-manager-backend"
set "JRE_DIR=%BASE%\runtime\jre"
set "JAR_DIR=%BASE%\target"

:: 优先定位最新的后端JAR
set "BACKEND_JAR="
for /f "delims=" %%f in ('dir /b /od "%JAR_DIR%\ai-manager-backend-*.jar" 2^>nul') do set "BACKEND_JAR=%%f"
if "%BACKEND_JAR%"=="" (
    echo 未找到后端Jar，尝试构建...
    pushd "%BASE%"
    if exist mvnw.cmd (
        call mvnw.cmd -DskipTests package
    ) else (
        echo 缺少 mvnw.cmd 无法自动构建，请先在 %BASE% 运行 mvnw.cmd package
        pause
        exit /b 1
    )
    popd
    for /f "delims=" %%f in ('dir /b /od "%JAR_DIR%\ai-manager-backend-*.jar" 2^>nul') do set "BACKEND_JAR=%%f"
)

if "%BACKEND_JAR%"=="" (
    echo ❌ 未找到后端Jar，启动失败。
    pause
    exit /b 1
)

set "JAVA_EXE=%JRE_DIR%\bin\java.exe"
if exist "%JAVA_EXE%" (
    echo 使用内置JRE启动...
    "%JAVA_EXE%" -jar "%JAR_DIR%\%BACKEND_JAR%" --spring.profiles.active=dev
    exit /b %errorlevel%
) else (
    echo 未找到内置JRE，尝试使用系统Java...
    where java >nul 2>nul
    if errorlevel 1 (
        echo ❌ 未检测到Java运行时环境。请将JRE解压到：
        echo   %JRE_DIR%
        echo 或在系统中安装/配置Java 17+
        pause
        exit /b 1
    )
    java -version
    java -jar "%JAR_DIR%\%BACKEND_JAR%" --spring.profiles.active=dev
    exit /b %errorlevel%
)
