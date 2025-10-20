# 依赖管理迁移指南

## 📋 迁移概述

本项目已从Python的简单依赖管理升级为Java的企业级依赖管理系统。以下是迁移的详细说明。

## 🔄 已删除的文件

以下文件已被删除，不再需要：

- ❌ `requirements.txt` - Python依赖列表
- ❌ `install_deps.bat` - Python依赖安装脚本

## ✅ 新的依赖管理方式

### Java后端依赖管理

**配置文件**: `ai-manager-backend/pom.xml`

**管理工具**:
- Maven Wrapper (`mvnw` / `mvnw.cmd`)
- 跨平台脚本工具
- 自动化依赖检查和安全扫描

**使用方法**:
```bash
# Windows
mvnw.cmd dependency:tree
scripts\dependency-check.bat

# Linux/macOS
./mvnw dependency:tree
./scripts/dependency-check.sh check
```

### Python核心依赖管理

**安装方式**: 手动安装（推荐使用虚拟环境）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install speechrecognition>=3.10.0
pip install pyttsx3>=2.90
pip install pyaudio
pip install requests>=2.31.0
pip install pygame>=2.5.2
pip install psutil>=5.9.6
pip install schedule>=1.2.0
pip install dashscope
```

## 🚀 迁移步骤

### 1. 清理旧环境
```bash
# 删除旧的虚拟环境（如果存在）
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# 清理pip缓存
pip cache purge
```

### 2. 设置新环境
```bash
# 创建新的虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装Python依赖
pip install speechrecognition pyttsx3 pyaudio requests pygame psutil schedule dashscope
```

### 3. 验证Java后端
```bash
# 进入后端目录
cd ai-manager-backend

# 检查依赖
./scripts/dependency-check.sh check  # Linux/macOS
# 或
scripts\dependency-check.bat  # Windows

# 构建项目
./scripts/build.sh --clean  # Linux/macOS
# 或
scripts\build.bat --clean  # Windows
```

## 📊 对比分析

### 旧方式 (Python)
```bash
# 安装依赖
pip install -r requirements.txt

# 检查依赖
pip list

# 更新依赖
pip install --upgrade package_name
```

**问题**:
- 版本冲突难以解决
- 依赖关系不清晰
- 安全漏洞检查缺失
- 跨平台支持有限

### 新方式 (Java + Python)

#### Java后端
```bash
# 依赖管理
./mvnw dependency:tree
./mvnw versions:display-dependency-updates
./mvnw versions:use-latest-versions

# 安全检查
./scripts/dependency-check.sh security

# 构建和测试
./scripts/build.sh --clean
```

**优势**:
- 智能依赖解析
- 自动版本管理
- 安全漏洞扫描
- 跨平台脚本支持
- 企业级工具链

#### Python核心
```bash
# 虚拟环境管理
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# 依赖安装
pip install package_name
```

**优势**:
- 环境隔离
- 版本控制
- 依赖冲突避免

## 🔧 开发工作流

### 日常开发
```bash
# 1. 启动Java后端
cd ai-manager-backend
./mvnw spring-boot:run

# 2. 启动Python核心
cd ..
source venv/bin/activate  # Linux/macOS
python Progress/app/main.py
```

### 依赖更新
```bash
# Java后端依赖更新
cd ai-manager-backend
./scripts/dependency-check.sh update

# Python核心依赖更新
pip install --upgrade package_name
```

### 安全检查
```bash
# Java后端安全检查
cd ai-manager-backend
./scripts/dependency-check.sh security

# Python核心安全检查
pip audit
```

## 🐛 常见问题

### Q: 为什么删除了requirements.txt？
A: 因为现在使用Java的Maven进行依赖管理，Python部分使用虚拟环境管理，更加灵活和安全。

### Q: 如何添加新的Java依赖？
A: 在`ai-manager-backend/pom.xml`中添加依赖，然后运行`./mvnw clean compile`。

### Q: 如何添加新的Python依赖？
A: 激活虚拟环境后使用`pip install package_name`安装。

### Q: 如何回滚到旧版本？
A: 使用Git回滚到删除文件之前的版本：
```bash
git checkout HEAD~1 -- requirements.txt install_deps.bat
```

## 📚 相关文档

- [Java后端使用指南](ai-manager-backend/README.md)
- [依赖管理策略](ai-manager-backend/docs/development/DEPENDENCY_MANAGEMENT.md)
- [项目结构说明](ai-manager-backend/PROJECT_STRUCTURE.md)

## 💡 最佳实践

1. **使用虚拟环境**: Python依赖始终在虚拟环境中安装
2. **定期更新**: 使用脚本工具定期检查和更新依赖
3. **安全扫描**: 定期运行安全检查
4. **版本锁定**: 生产环境使用固定版本
5. **文档记录**: 记录依赖变更和原因

---

**注意**: 如果遇到任何问题，请查看相关文档或提交Issue。
