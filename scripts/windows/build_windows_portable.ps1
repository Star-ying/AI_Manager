# =====================================================
# AI Manager - Windows 一键打包（离线版）
# 功能：
# 1) 构建Java后端Jar（使用mvnw）
# 2) 下载并解压JRE 17（x64）到 ai-manager-backend\runtime\jre
# 3) 使用PyInstaller打包Python核心为单文件exe
# 4) 生成分发目录 dist\AI_Manager_Windows_Offline\ 并拷贝必要文件
# 5) 放入一键启动脚本
# =====================================================

param(
  [string]$JreZipUrl = "https://github.com/adoptium/temurin17-binaries/releases/latest/download/OpenJDK17U-jre_x64_windows_hotspot_17.0.13_11.zip",
  [string]$PythonExeName = "ai-manager-core.exe"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Ensure-Dir($path) { if (!(Test-Path $path)) { New-Item -ItemType Directory -Force -Path $path | Out-Null } }

# 根路径
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "ai-manager-backend"
$BackendTarget = Join-Path $Backend "target"
$BackendRuntime = Join-Path $Backend "runtime"
$JreDir = Join-Path $BackendRuntime "jre"
$DistDir = Join-Path $Root "dist"
$BundleDir = Join-Path $DistDir "AI_Manager_Windows_Offline"

Write-Host "==== 步骤 1/5: 构建Java后端Jar ====" -ForegroundColor Cyan
Push-Location $Backend
if (Test-Path "mvnw.cmd") {
  & .\mvnw.cmd -DskipTests package
} else {
  throw "未找到 mvnw.cmd"
}
Pop-Location

$jar = Get-ChildItem -Path $BackendTarget -Filter "ai-manager-backend-*.jar" | Sort-Object LastWriteTime | Select-Object -Last 1
if (-not $jar) { throw "未找到构建产物Jar" }

Write-Host "==== 步骤 2/5: 下载并解压JRE (x64) ====" -ForegroundColor Cyan
Ensure-Dir $BackendRuntime
Ensure-Dir $JreDir
$tempZip = Join-Path $BackendRuntime "jre.zip"
try {
  Invoke-WebRequest -Uri $JreZipUrl -OutFile $tempZip -UseBasicParsing
  Expand-Archive -Path $tempZip -DestinationPath $JreDir -Force
} finally {
  if (Test-Path $tempZip) { Remove-Item $tempZip -Force }
}

Write-Host "==== 步骤 3/5: 打包Python核心 (PyInstaller) ====" -ForegroundColor Cyan
Push-Location $Root
# 安装依赖（开发机一次性）
python -m pip install --upgrade pip
pip install pyinstaller speechrecognition pyttsx3 pyaudio requests pygame psutil schedule dashscope

# 处理资源路径（按项目已有结构）
$SpecOutDir = Join-Path $DistDir "build"
Ensure-Dir $SpecOutDir

# 生成可执行
pyinstaller Progress\app\main.py --name $PythonExeName.Replace('.exe','') --noconsole --onefile `
  --add-data "config.json;." `
  --add-data "Progress\resoures;Progress\resoures" `
  --add-data "my_resources;my_resources"

Pop-Location

$CoreExe = Get-ChildItem -Path (Join-Path $Root "dist") -Filter "$PythonExeName" -Recurse | Select-Object -First 1
if (-not $CoreExe) { $CoreExe = Get-ChildItem -Path (Join-Path $Root "dist") -Filter "*.exe" | Where-Object { $_.Name -like "ai-manager-core*.exe" } | Select-Object -First 1 }
if (-not $CoreExe) { throw "未找到PyInstaller生成的核心可执行文件" }

Write-Host "==== 步骤 4/5: 组装分发目录 ====" -ForegroundColor Cyan
if (Test-Path $BundleDir) { Remove-Item $BundleDir -Recurse -Force }
Ensure-Dir $BundleDir

# 拷贝核心exe
Copy-Item $CoreExe.FullName -Destination (Join-Path $BundleDir $PythonExeName) -Force

# 拷贝后端目录（Jar + JRE + 启动脚本）
$BundleBackend = Join-Path $BundleDir "ai-manager-backend"
Ensure-Dir $BundleBackend
Ensure-Dir (Join-Path $BundleBackend "target")
Ensure-Dir (Join-Path $BundleBackend "runtime")

Copy-Item $jar.FullName -Destination (Join-Path $BundleBackend "target") -Force
Copy-Item $JreDir -Destination (Join-Path $BundleBackend "runtime") -Recurse -Force

# 拷贝脚本
Copy-Item (Join-Path $Root "scripts\windows\start_backend.bat") -Destination (Join-Path $BundleDir "start_backend.bat") -Force
Copy-Item (Join-Path $Root "scripts\windows\start_all.bat") -Destination (Join-Path $BundleDir "start_all.bat") -Force

# 拷贝资源与配置
if (Test-Path (Join-Path $Root "my_resources")) { Copy-Item (Join-Path $Root "my_resources") -Destination (Join-Path $BundleDir "my_resources") -Recurse -Force }
Copy-Item (Join-Path $Root "config.json") -Destination (Join-Path $BundleDir "config.json") -Force

Write-Host "==== 步骤 5/5: 生成用户说明 ====" -ForegroundColor Cyan
$Readme = @"
AI Manager - Windows 免安装版
================================

使用方法：
1) 双击 start_all.bat 一键启动（先启动Python核心，再启动Java后端）
2) 如仅需后端，双击 start_backend.bat
3) 若报“缺少JRE”，请检查 ai-manager-backend\runtime\jre 是否存在
4) 若Python核心未启动，检查 dist 是否包含 ai-manager-core.exe

注意：
- 首次启动可能需要防火墙放行
- 如需更换通义千问API Key，请编辑同目录下 config.json

目录结构（示例）：
- start_all.bat
- start_backend.bat
- config.json
- my_resources\
- ai-manager-backend\
  - target\ai-manager-backend-*.jar
  - runtime\jre\bin\java.exe
- ai-manager-core.exe
"@
Set-Content -Path (Join-Path $BundleDir "README.txt") -Value $Readme -Encoding UTF8

Write-Host "✅ 打包完成。分发目录： $BundleDir" -ForegroundColor Green
