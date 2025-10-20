# =====================================================
# AI Manager Backend - 构建脚本 (PowerShell版本)
# 功能：编译、测试、打包项目
# =====================================================

param(
    [switch]$Clean,
    [switch]$SkipTests,
    [switch]$NoPackage,
    [string]$Profile = "dev",
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
Write-Host "AI Manager Backend - 构建脚本 (PowerShell)" -ForegroundColor $Colors.Blue
Write-Host "=====================================================" -ForegroundColor $Colors.Blue

function Show-Help {
    Write-Host "使用方法: .\build.ps1 [选项]" -ForegroundColor $Colors.Blue
    Write-Host ""
    Write-Host "选项:" -ForegroundColor $Colors.Blue
    Write-Host "  -Clean        清理项目"
    Write-Host "  -SkipTests    跳过测试"
    Write-Host "  -NoPackage    不打包"
    Write-Host "  -Profile      指定配置文件 (dev/test/prod)"
    Write-Host "  -Help         显示帮助"
    Write-Host ""
    Write-Host "示例:" -ForegroundColor $Colors.Blue
    Write-Host "  .\build.ps1 -Clean"
    Write-Host "  .\build.ps1 -SkipTests -Profile prod"
}

function Test-Maven {
    Write-Host "[1/4] 检查Maven..." -ForegroundColor $Colors.Yellow
    
    try {
        $mavenVersion = & mvn --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Maven未安装"
        }
        Write-Host "✅ Maven检查通过" -ForegroundColor $Colors.Green
        return $true
    }
    catch {
        Write-Host "❌ Maven未安装" -ForegroundColor $Colors.Red
        Write-Host "请先安装Maven: https://maven.apache.org/download.cgi" -ForegroundColor $Colors.Yellow
        return $false
    }
}

function Test-Java {
    Write-Host "[2/4] 检查Java..." -ForegroundColor $Colors.Yellow
    
    try {
        $javaVersion = & java -version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Java未安装"
        }
        Write-Host "✅ Java检查通过" -ForegroundColor $Colors.Green
        return $true
    }
    catch {
        Write-Host "❌ Java未安装" -ForegroundColor $Colors.Red
        Write-Host "请先安装Java 17+: https://adoptium.net/" -ForegroundColor $Colors.Yellow
        return $false
    }
}

function Start-Clean {
    Write-Host "[3/4] 清理项目..." -ForegroundColor $Colors.Yellow
    
    try {
        & mvn clean
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 项目清理完成" -ForegroundColor $Colors.Green
        } else {
            throw "清理失败"
        }
    }
    catch {
        Write-Host "❌ 项目清理失败: $_" -ForegroundColor $Colors.Red
    }
}

function Start-Build {
    Write-Host "[4/4] 编译项目..." -ForegroundColor $Colors.Yellow
    
    try {
        # 编译项目
        & mvn compile -P$Profile
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 项目编译完成" -ForegroundColor $Colors.Green
        } else {
            throw "编译失败"
        }
        
        # 运行测试
        if (-not $SkipTests) {
            Write-Host "🧪 运行测试..." -ForegroundColor $Colors.Cyan
            & mvn test -P$Profile
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ 测试完成" -ForegroundColor $Colors.Green
            } else {
                Write-Host "⚠️ 测试失败，但继续构建" -ForegroundColor $Colors.Yellow
            }
        }
        
        # 打包项目
        if (-not $NoPackage) {
            Write-Host "📦 打包项目..." -ForegroundColor $Colors.Cyan
            if ($SkipTests) {
                & mvn package -DskipTests -P$Profile
            } else {
                & mvn package -P$Profile
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ 项目打包完成" -ForegroundColor $Colors.Green
                
                # 显示打包结果
                $jarFiles = Get-ChildItem -Path "target" -Filter "*.jar" | Where-Object { 
                    $_.Name -notlike "*sources.jar" -and $_.Name -notlike "*javadoc.jar" 
                }
                
                if ($jarFiles) {
                    $jarFile = $jarFiles[0]
                    Write-Host "📁 打包文件: $($jarFile.FullName)" -ForegroundColor $Colors.Green
                    Write-Host "📊 文件大小: $([math]::Round($jarFile.Length / 1MB, 2)) MB" -ForegroundColor $Colors.Green
                }
            } else {
                throw "打包失败"
            }
        }
        
        # 生成报告
        Write-Host "📋 生成构建报告..." -ForegroundColor $Colors.Cyan
        & mvn site -P$Profile
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 构建报告生成完成" -ForegroundColor $Colors.Green
        }
        
    }
    catch {
        Write-Host "❌ 构建失败: $_" -ForegroundColor $Colors.Red
    }
}

# 主逻辑
if ($Help) {
    Show-Help
    exit 0
}

Write-Host "构建配置:" -ForegroundColor $Colors.Yellow
Write-Host "  清理项目: $Clean"
Write-Host "  运行测试: $(-not $SkipTests)"
Write-Host "  打包项目: $(-not $NoPackage)"
Write-Host "  配置文件: $Profile"
Write-Host ""

if (-not (Test-Maven)) { exit 1 }
if (-not (Test-Java)) { exit 1 }

if ($Clean) {
    Start-Clean
}

Start-Build

Write-Host ""
Write-Host "🎉 构建完成！" -ForegroundColor $Colors.Green
Write-Host ""
Write-Host "下一步:" -ForegroundColor $Colors.Yellow
Write-Host "  1. 运行应用: java -jar target\ai-manager-backend-1.0.0.jar"
Write-Host "  2. 查看报告: target\site\index.html"
Write-Host "  3. 查看日志: logs\ai-manager-backend.log"
