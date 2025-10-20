@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: =====================================================
:: AI Manager Backend - 构建脚本 (Windows版本)
:: 功能：编译、测试、打包项目
:: =====================================================

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

echo =====================================================
echo AI Manager Backend - 构建脚本 (Windows)
echo =====================================================

:: 默认参数
set "CLEAN=false"
set "TEST=true"
set "PACKAGE=true"
set "SKIP_TESTS=false"
set "PROFILE=dev"

:: 解析命令行参数
:parse_args
if "%~1"=="" goto :start_build
if "%~1"=="--clean" (
    set "CLEAN=true"
    shift
    goto :parse_args
)
if "%~1"=="--skip-tests" (
    set "SKIP_TESTS=true"
    set "TEST=false"
    shift
    goto :parse_args
)
if "%~1"=="--no-package" (
    set "PACKAGE=false"
    shift
    goto :parse_args
)
if "%~1"=="--profile" (
    set "PROFILE=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--help" (
    echo 使用方法: %0 [选项]
    echo.
    echo 选项:
    echo   --clean        清理项目
    echo   --skip-tests   跳过测试
    echo   --no-package   不打包
    echo   --profile      指定配置文件 (dev/test/prod)
    echo   --help         显示帮助
    exit /b 0
)
echo ❌ 未知选项: %~1
exit /b 1

:start_build
echo 构建配置:
echo   清理项目: %CLEAN%
echo   运行测试: %TEST%
echo   打包项目: %PACKAGE%
echo   配置文件: %PROFILE%
echo.

:: 检查Maven
echo [1/4] 检查Maven...
mvn --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Maven未安装
    echo 请先安装Maven: https://maven.apache.org/download.cgi
    pause
    exit /b 1
)
echo ✅ Maven检查通过

:: 检查Java
echo [2/4] 检查Java...
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Java未安装
    echo 请先安装Java 17+: https://adoptium.net/
    pause
    exit /b 1
)
echo ✅ Java检查通过

:: 清理项目
if "%CLEAN%"=="true" (
    echo [3/4] 清理项目...
    mvn clean
    echo ✅ 项目清理完成
)

:: 编译项目
echo [4/4] 编译项目...
mvn compile -P%PROFILE%
echo ✅ 项目编译完成

:: 运行测试
if "%TEST%"=="true" (
    echo 🧪 运行测试...
    if "%SKIP_TESTS%"=="true" (
        mvn test -DskipTests -P%PROFILE%
    ) else (
        mvn test -P%PROFILE%
    )
    echo ✅ 测试完成
)

:: 打包项目
if "%PACKAGE%"=="true" (
    echo 📦 打包项目...
    if "%SKIP_TESTS%"=="true" (
        mvn package -DskipTests -P%PROFILE%
    ) else (
        mvn package -P%PROFILE%
    )
    echo ✅ 项目打包完成
    
    :: 显示打包结果
    for %%f in (target\*.jar) do (
        if not "%%~nxf"=="*sources.jar" if not "%%~nxf"=="*javadoc.jar" (
            echo 📁 打包文件: %%f
            for %%s in ("%%f") do echo 📊 文件大小: %%~zs 字节
        )
    )
)

:: 生成报告
echo 📋 生成构建报告...
mvn site -P%PROFILE%
echo ✅ 构建报告生成完成

echo.
echo 🎉 构建完成！
echo.
echo 下一步:
echo   1. 运行应用: java -jar target\ai-manager-backend-1.0.0.jar
echo   2. 查看报告: target\site\index.html
echo   3. 查看日志: logs\ai-manager-backend.log

pause
