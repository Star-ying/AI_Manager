# =====================================================
# AI Manager Backend - 依赖管理工具 (PowerShell版本)
# 功能：检查、更新、验证项目依赖
# =====================================================

param(
    [string]$Action = "all",
    [switch]$Help
)

# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 颜色定义
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
}

# 项目根目录
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "=====================================================" -ForegroundColor $Colors.Blue
Write-Host "AI Manager Backend - 依赖管理工具 (PowerShell)" -ForegroundColor $Colors.Blue
Write-Host "=====================================================" -ForegroundColor $Colors.Blue

function Show-Help {
    Write-Host "使用方法: .\dependency-check.ps1 [选项]" -ForegroundColor $Colors.Blue
    Write-Host ""
    Write-Host "选项:" -ForegroundColor $Colors.Blue
    Write-Host "  -Action <action>  执行的操作 (check|tree|analyze|update|security|validate|clean|report|all)"
    Write-Host "  -Help             显示帮助信息"
    Write-Host ""
    Write-Host "示例:" -ForegroundColor $Colors.Blue
    Write-Host "  .\dependency-check.ps1 -Action check     # 检查环境"
    Write-Host "  .\dependency-check.ps1 -Action analyze   # 分析依赖"
    Write-Host "  .\dependency-check.ps1 -Action all       # 执行所有检查"
}

function Test-Maven {
    Write-Host "[1/6] 检查Maven安装..." -ForegroundColor $Colors.Yellow
    
    try {
        $mavenVersion = & mvn --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Maven未安装"
        }
        Write-Host "✅ Maven已安装: $($mavenVersion[0])" -ForegroundColor $Colors.Green
        return $true
    }
    catch {
        Write-Host "❌ Maven未安装，请先安装Maven" -ForegroundColor $Colors.Red
        Write-Host "安装指南：" -ForegroundColor $Colors.Yellow
        Write-Host "  Windows: 下载并安装 https://maven.apache.org/download.cgi"
        Write-Host "  或使用 Chocolatey: choco install maven"
        Write-Host "  或使用 Scoop: scoop install maven"
        return $false
    }
}

function Test-Java {
    Write-Host "[2/6] 检查Java安装..." -ForegroundColor $Colors.Yellow
    
    try {
        $javaVersion = & java -version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Java未安装"
        }
        
        # 提取Java版本号
        $versionLine = $javaVersion | Where-Object { $_ -match 'version' } | Select-Object -First 1
        if ($versionLine -match '"(\d+)') {
            $majorVersion = [int]$matches[1]
            if ($majorVersion -lt 17) {
                throw "Java版本过低: $majorVersion，需要Java 17+"
            }
        }
        
        Write-Host "✅ Java版本: $($javaVersion[0])" -ForegroundColor $Colors.Green
        return $true
    }
    catch {
        Write-Host "❌ Java未安装或版本过低，请先安装Java 17+" -ForegroundColor $Colors.Red
        Write-Host "安装指南：" -ForegroundColor $Colors.Yellow
        Write-Host "  Windows: 下载并安装 https://adoptium.net/"
        Write-Host "  或使用 Chocolatey: choco install openjdk17"
        Write-Host "  或使用 Scoop: scoop install openjdk17"
        return $false
    }
}

function Show-DependencyTree {
    Write-Host "[3/6] 显示依赖树..." -ForegroundColor $Colors.Yellow
    Write-Host "📊 显示依赖树..." -ForegroundColor $Colors.Cyan
    
    try {
        & mvn dependency:tree -Dverbose=false
        if ($LASTEXITCODE -ne 0) {
            throw "依赖树显示失败"
        }
    }
    catch {
        Write-Host "❌ 依赖树显示失败: $_" -ForegroundColor $Colors.Red
    }
}

function Analyze-Dependencies {
    Write-Host "[4/6] 分析依赖..." -ForegroundColor $Colors.Yellow
    Write-Host "🔍 分析依赖..." -ForegroundColor $Colors.Cyan
    
    try {
        Write-Host "检查未使用的依赖:" -ForegroundColor $Colors.Yellow
        & mvn dependency:analyze
        
        Write-Host "检查过时的依赖:" -ForegroundColor $Colors.Yellow
        & mvn versions:display-dependency-updates
        
        Write-Host "检查插件更新:" -ForegroundColor $Colors.Yellow
        & mvn versions:display-plugin-updates
    }
    catch {
        Write-Host "❌ 依赖分析失败: $_" -ForegroundColor $Colors.Red
    }
}

function Test-Security {
    Write-Host "[5/6] 检查安全漏洞..." -ForegroundColor $Colors.Yellow
    Write-Host "🔒 检查安全漏洞..." -ForegroundColor $Colors.Cyan
    
    try {
        # 检查是否有OWASP Dependency Check
        $dependencyCheck = Get-Command dependency-check.bat -ErrorAction SilentlyContinue
        if ($dependencyCheck) {
            Write-Host "运行OWASP依赖检查:" -ForegroundColor $Colors.Yellow
            & dependency-check.bat --project "AI Manager Backend" --scan $ProjectRoot
        }
        else {
            Write-Host "⚠️ OWASP Dependency Check未安装，跳过安全检查" -ForegroundColor $Colors.Yellow
            Write-Host "安装命令:" -ForegroundColor $Colors.Yellow
            Write-Host "  wget https://github.com/jeremylong/DependencyCheck/releases/latest/download/dependency-check-8.4.0-release.zip"
            Write-Host "  unzip dependency-check-8.4.0-release.zip"
        }
    }
    catch {
        Write-Host "❌ 安全检查失败: $_" -ForegroundColor $Colors.Red
    }
}

function Test-ValidateDependencies {
    Write-Host "[6/6] 验证依赖..." -ForegroundColor $Colors.Yellow
    Write-Host "✅ 验证依赖..." -ForegroundColor $Colors.Cyan
    
    try {
        Write-Host "编译项目:" -ForegroundColor $Colors.Yellow
        & mvn clean compile
        
        Write-Host "运行测试:" -ForegroundColor $Colors.Yellow
        & mvn test
        
        Write-Host "打包项目:" -ForegroundColor $Colors.Yellow
        & mvn package -DskipTests
        
        Write-Host "✅ 依赖验证完成" -ForegroundColor $Colors.Green
    }
    catch {
        Write-Host "❌ 依赖验证失败: $_" -ForegroundColor $Colors.Red
    }
}

function Update-Dependencies {
    Write-Host "🔄 更新依赖版本..." -ForegroundColor $Colors.Cyan
    
    try {
        Write-Host "更新依赖到最新版本:" -ForegroundColor $Colors.Yellow
        & mvn versions:use-latest-versions
        
        Write-Host "更新插件到最新版本:" -ForegroundColor $Colors.Yellow
        & mvn versions:use-latest-releases
        
        Write-Host "✅ 依赖更新完成" -ForegroundColor $Colors.Green
    }
    catch {
        Write-Host "❌ 依赖更新失败: $_" -ForegroundColor $Colors.Red
    }
}

function Clear-Dependencies {
    Write-Host "🧹 清理依赖..." -ForegroundColor $Colors.Cyan
    
    try {
        Write-Host "清理Maven缓存:" -ForegroundColor $Colors.Yellow
        & mvn dependency:purge-local-repository
        
        Write-Host "清理项目:" -ForegroundColor $Colors.Yellow
        & mvn clean
        
        Write-Host "✅ 依赖清理完成" -ForegroundColor $Colors.Green
    }
    catch {
        Write-Host "❌ 依赖清理失败: $_" -ForegroundColor $Colors.Red
    }
}

function New-Report {
    Write-Host "📋 生成依赖报告..." -ForegroundColor $Colors.Cyan
    
    try {
        & mvn dependency:analyze-report
        & mvn site
        
        Write-Host "✅ 报告生成完成，查看target/site/index.html" -ForegroundColor $Colors.Green
    }
    catch {
        Write-Host "❌ 报告生成失败: $_" -ForegroundColor $Colors.Red
    }
}

function Start-AllChecks {
    Write-Host "🚀 执行所有依赖检查..." -ForegroundColor $Colors.Cyan
    
    if (-not (Test-Maven)) { return }
    if (-not (Test-Java)) { return }
    
    Show-DependencyTree
    Analyze-Dependencies
    Test-Security
    Test-ValidateDependencies
    
    Write-Host "🎉 所有检查完成！" -ForegroundColor $Colors.Green
}

# 主逻辑
if ($Help) {
    Show-Help
    exit 0
}

switch ($Action.ToLower()) {
    "check" {
        Test-Maven
        Test-Java
    }
    "tree" {
        if (Test-Maven) {
            Show-DependencyTree
        }
    }
    "analyze" {
        if (Test-Maven) {
            Analyze-Dependencies
        }
    }
    "update" {
        if (Test-Maven) {
            Update-Dependencies
        }
    }
    "security" {
        if (Test-Maven) {
            Test-Security
        }
    }
    "validate" {
        if (Test-Maven) {
            Test-ValidateDependencies
        }
    }
    "clean" {
        if (Test-Maven) {
            Clear-Dependencies
        }
    }
    "report" {
        if (Test-Maven) {
            New-Report
        }
    }
    "all" {
        Start-AllChecks
    }
    default {
        Write-Host "❌ 未知操作: $Action" -ForegroundColor $Colors.Red
        Show-Help
        exit 1
    }
}

Write-Host ""
Write-Host "下一步操作:" -ForegroundColor $Colors.Yellow
Write-Host "  1. 运行应用: java -jar target\ai-manager-backend-1.0.0.jar"
Write-Host "  2. 查看报告: target\site\index.html"
Write-Host "  3. 查看日志: logs\ai-manager-backend.log"
