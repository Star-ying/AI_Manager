# AI Manager Backend - Java后端服务

## 📋 项目概述

这是AI Manager项目的Java后端服务，提供REST API、数据库管理、日志系统等企业级功能。

## 🚀 快速开始（Windows）

### 使用Maven Wrapper（已内置）
```cmd
:: 依赖树
mvnw.cmd dependency:tree

:: 构建
mvnw.cmd clean package

:: 运行
mvnw.cmd spring-boot:run
```

### 使用脚本工具（可选）
```cmd
:: 依赖检查（批处理）
scripts\dependency-check.bat

:: 构建（批处理）
scripts\build.bat --clean

:: 依赖检查（PowerShell）
PowerShell -ExecutionPolicy Bypass -File scripts\dependency-check.ps1 -Action check

:: 构建（PowerShell）
PowerShell -ExecutionPolicy Bypass -File scripts\build.ps1 -Clean
```

## 📋 环境要求（Windows）
- Java 17+（如使用mvnw.cmd，可不预装Maven）
- 可选：Chocolatey 或 Scoop 进行安装管理

## 🔧 安装指南（Windows）
```cmd
:: 安装Java（二选一）
choco install openjdk17
:: 或
scoop install openjdk17
```

## 🛠️ 开发环境设置
```cmd
:: 克隆并进入后端目录
git clone <repository-url>
cd ai-manager-backend

:: 检查环境
scripts\dependency-check.bat

:: 构建
scripts\build.bat --clean

:: 运行
mvnw.cmd spring-boot:run
```

## 📁 项目结构（简要）
```
ai-manager-backend/
├── mvnw.cmd                # Maven Wrapper (Windows)
├── pom.xml                 # Maven配置
├── scripts/                # Windows脚本
│   ├── build.bat           # 构建脚本（批处理）
│   ├── build.ps1           # 构建脚本（PowerShell）
│   ├── dependency-check.bat
│   └── dependency-check.ps1
├── src/                    # 源代码
└── target/                 # 构建输出
```

## 🔍 常用命令
```cmd
:: 依赖树
mvnw.cmd dependency:tree

:: 检查过时依赖
mvnw.cmd versions:display-dependency-updates

:: 更新依赖
mvnw.cmd versions:use-latest-versions

:: 清理/编译/测试/打包
mvnw.cmd clean
mvnw.cmd compile
mvnw.cmd test
mvnw.cmd package
```

## 🐛 故障排除（Windows）
```cmd
:: 查看Java版本
java -version

:: PowerShell执行策略（如脚本受限）
PowerShell -ExecutionPolicy Bypass -File scripts\build.ps1 -Clean

:: 控制台编码
chcp 65001
```

## 📚 更多资源
- Spring Boot: https://spring.io/projects/spring-boot
- Maven: https://maven.apache.org/guides/
- Java: https://docs.oracle.com/en/java/

## 📄 许可证
本项目采用MIT许可证，详见LICENSE文件。
