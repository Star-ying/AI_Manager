# AI Manager Backend - Java后端服务

## 📋 项目概述

这是AI Manager项目的Java后端服务，提供REST API、数据库管理、日志系统等企业级功能。

## 🚀 快速开始

### 使用Maven Wrapper (推荐)

Maven Wrapper已经包含在项目中，无需预先安装Maven：

#### Windows
```cmd
# 依赖检查
mvnw.cmd dependency:tree

# 构建项目
mvnw.cmd clean package

# 运行应用
mvnw.cmd spring-boot:run
```

#### Linux/macOS
```bash
# 依赖检查
./mvnw dependency:tree

# 构建项目
./mvnw clean package

# 运行应用
./mvnw spring-boot:run
```

### 使用脚本工具

#### Windows用户

**批处理脚本 (.bat)**
```cmd
# 检查环境和依赖
scripts\dependency-check.bat

# 构建项目
scripts\build.bat --clean
```

**PowerShell脚本 (.ps1)**
```powershell
# 检查环境和依赖
.\scripts\dependency-check.ps1 -Action check

# 构建项目
.\scripts\build.ps1 -Clean
```

#### Linux/macOS用户

**Bash脚本 (.sh)**
```bash
# 检查环境和依赖
./scripts/dependency-check.sh check

# 构建项目
./scripts/build.sh --clean
```

## 📋 环境要求

### 必需软件
- **Java 17+** (推荐使用OpenJDK 17)
- **Maven 3.6+** (可选，项目包含Maven Wrapper)

### 可选软件
- **Git** (用于版本控制)
- **IDE** (IntelliJ IDEA, Eclipse, VS Code等)

## 🔧 安装指南

### Windows

#### 安装Java
```cmd
# 使用Chocolatey
choco install openjdk17

# 使用Scoop
scoop install openjdk17

# 或手动下载安装
# https://adoptium.net/
```

#### 安装Maven (可选)
```cmd
# 使用Chocolatey
choco install maven

# 使用Scoop
scoop install maven
```

### Linux (Ubuntu/Debian)

```bash
# 安装Java 17
sudo apt update
sudo apt install openjdk-17-jdk

# 安装Maven (可选)
sudo apt install maven

# 验证安装
java -version
mvn --version
```

### macOS

```bash
# 使用Homebrew安装Java
brew install openjdk@17

# 使用Homebrew安装Maven (可选)
brew install maven

# 验证安装
java -version
mvn --version
```

## 🛠️ 开发环境设置

### 1. 克隆项目
```bash
git clone <repository-url>
cd ai-manager-backend
```

### 2. 检查环境
```bash
# Windows
scripts\dependency-check.bat

# Linux/macOS
./scripts/dependency-check.sh check
```

### 3. 构建项目
```bash
# Windows
scripts\build.bat --clean

# Linux/macOS
./scripts/build.sh --clean
```

### 4. 运行应用
```bash
# 使用Maven Wrapper
mvnw spring-boot:run

# 或直接运行JAR
java -jar target/ai-manager-backend-1.0.0.jar
```

## 📁 项目结构

```
ai-manager-backend/
├── mvnw                    # Maven Wrapper (Unix)
├── mvnw.cmd               # Maven Wrapper (Windows)
├── pom.xml                # Maven配置
├── scripts/               # 跨平台脚本
│   ├── build.sh          # Linux/macOS构建脚本
│   ├── build.bat         # Windows构建脚本
│   ├── build.ps1         # PowerShell构建脚本
│   ├── dependency-check.sh # Linux/macOS依赖检查
│   ├── dependency-check.bat # Windows依赖检查
│   └── dependency-check.ps1 # PowerShell依赖检查
├── src/                   # 源代码
└── target/               # 构建输出
```

## 🔍 常用命令

### 依赖管理
```bash
# 查看依赖树
mvnw dependency:tree

# 检查过时依赖
mvnw versions:display-dependency-updates

# 更新依赖
mvnw versions:use-latest-versions
```

### 构建和测试
```bash
# 清理项目
mvnw clean

# 编译项目
mvnw compile

# 运行测试
mvnw test

# 打包项目
mvnw package

# 跳过测试打包
mvnw package -DskipTests
```

### 运行应用
```bash
# 开发模式运行
mvnw spring-boot:run

# 指定配置文件
mvnw spring-boot:run -Dspring-boot.run.profiles=dev

# 生产模式运行
java -jar target/ai-manager-backend-1.0.0.jar --spring.profiles.active=prod
```

## 🐛 故障排除

### 常见问题

#### 1. Java版本问题
```bash
# 检查Java版本
java -version

# 如果版本过低，请安装Java 17+
# Windows: https://adoptium.net/
# Linux: sudo apt install openjdk-17-jdk
# macOS: brew install openjdk@17
```

#### 2. Maven Wrapper权限问题 (Linux/macOS)
```bash
# 添加执行权限
chmod +x mvnw
chmod +x scripts/*.sh
```

#### 3. PowerShell执行策略问题 (Windows)
```powershell
# 设置执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 或临时允许执行
PowerShell -ExecutionPolicy Bypass -File scripts\build.ps1
```

#### 4. 编码问题 (Windows)
```cmd
# 设置控制台编码
chcp 65001
```

### 日志查看
```bash
# 查看应用日志
tail -f logs/ai-manager-backend.log

# 查看构建日志
mvnw clean package -X
```

## 🔧 IDE配置

### IntelliJ IDEA
1. 打开项目根目录
2. 选择"Import Maven Project"
3. 等待依赖下载完成
4. 配置运行配置：
   - Main class: `com.aimanager.AiManagerBackendApplication`
   - VM options: `-Dspring.profiles.active=dev`

### Eclipse
1. 导入现有Maven项目
2. 右键项目 → Maven → Reload Projects
3. 运行配置：
   - Main class: `com.aimanager.AiManagerBackendApplication`
   - Program arguments: `--spring.profiles.active=dev`

### VS Code
1. 安装Java扩展包
2. 打开项目根目录
3. 按F5运行或使用命令面板运行

## 📚 更多资源

- [Spring Boot官方文档](https://spring.io/projects/spring-boot)
- [Maven官方文档](https://maven.apache.org/guides/)
- [Java官方文档](https://docs.oracle.com/en/java/)

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。
