@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: =====================================================
:: AI Manager Backend - 依赖管理工具 (Windows版本)
:: 功能：检查、更新、验证项目依赖
:: =====================================================

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

echo =====================================================
echo AI Manager Backend - 依赖管理工具 (Windows)
echo =====================================================

:: 检查Maven是否安装
:check_maven
echo [1/6] 检查Maven安装...
mvn --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Maven未安装，请先安装Maven
    echo 安装指南：
    echo   Windows: 下载并安装 https://maven.apache.org/download.cgi
    echo   或使用 Chocolatey: choco install maven
    echo   或使用 Scoop: scoop install maven
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('mvn --version ^| findstr "Apache Maven"') do set MAVEN_VERSION=%%i
echo ✅ Maven已安装: %MAVEN_VERSION%

:: 检查Java版本
:check_java
echo [2/6] 检查Java安装...
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Java未安装，请先安装Java 17+
    echo 安装指南：
    echo   Windows: 下载并安装 https://adoptium.net/
    echo   或使用 Chocolatey: choco install openjdk17
    echo   或使用 Scoop: scoop install openjdk17
    pause
    exit /b 1
)

for /f "tokens=3" %%i in ('java -version 2^>^&1 ^| findstr "version"') do set JAVA_VERSION=%%i
set JAVA_VERSION=%JAVA_VERSION:"=%
echo ✅ Java版本: %JAVA_VERSION%

:: 显示依赖树
:show_dependency_tree
echo [3/6] 显示依赖树...
echo 📊 显示依赖树...
mvn dependency:tree -Dverbose=false

:: 分析依赖
:analyze_dependencies
echo [4/6] 分析依赖...
echo 🔍 分析依赖...

echo 检查未使用的依赖:
mvn dependency:analyze

echo 检查过时的依赖:
mvn versions:display-dependency-updates

echo 检查插件更新:
mvn versions:display-plugin-updates

:: 检查安全漏洞
:check_security
echo [5/6] 检查安全漏洞...
echo 🔒 检查安全漏洞...

:: 检查是否有OWASP Dependency Check
where dependency-check.bat >nul 2>&1
if %errorlevel% equ 0 (
    echo 运行OWASP依赖检查:
    dependency-check.bat --project "AI Manager Backend" --scan "%PROJECT_ROOT%"
) else (
    echo ⚠️ OWASP Dependency Check未安装，跳过安全检查
    echo 安装命令:
    echo   wget https://github.com/jeremylong/DependencyCheck/releases/latest/download/dependency-check-8.4.0-release.zip
    echo   unzip dependency-check-8.4.0-release.zip
)

:: 验证依赖
:validate_dependencies
echo [6/6] 验证依赖...
echo ✅ 验证依赖...

echo 编译项目:
mvn clean compile

echo 运行测试:
mvn test

echo 打包项目:
mvn package -DskipTests

echo ✅ 依赖验证完成

echo.
echo 🎉 所有检查完成！
echo.
echo 下一步操作:
echo   1. 运行应用: java -jar target\ai-manager-backend-1.0.0.jar
echo   2. 查看报告: target\site\index.html
echo   3. 查看日志: logs\ai-manager-backend.log

pause
