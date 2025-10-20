# AI Manager - 语音控制AI助手

一个基于大模型的语音控制应用，可以通过语音对话控制电脑执行各种任务。

## 🏗️ 项目架构

本项目采用**混合架构**设计：
- **Java后端**: 提供REST API、数据库管理、日志系统
- **Python核心**: 语音识别、AI助手、系统控制、语音合成

## 🚀 快速开始

### 环境要求
- **Java 17+** (后端服务)
- **Python 3.8+** (核心引擎)
- **Maven 3.6+** (可选，项目包含Maven Wrapper)

### 安装和运行

#### 1. 启动Java后端服务
```bash
# 进入后端目录
cd ai-manager-backend

# 使用Maven Wrapper构建和运行
./mvnw clean package
./mvnw spring-boot:run

# 或使用脚本工具
./scripts/build.sh --clean
```

#### 2. 启动Python核心引擎
```bash
# 安装Python依赖
pip install speechrecognition pyttsx3 pyaudio requests pygame psutil schedule dashscope

# 运行核心引擎
python Progress/app/main.py
```

## 📁 项目结构

```
AI_Manager/
├── ai-manager-backend/          # Java后端服务
│   ├── pom.xml                  # Maven依赖管理
│   ├── mvnw                     # Maven Wrapper
│   ├── scripts/                 # 跨平台脚本工具
│   └── src/                     # Java源代码
├── Progress/                    # Python核心引擎
│   └── app/                     # Python应用代码
├── database/                    # 数据库配置
├── my_resources/               # 资源文件
└── config.json                 # 配置文件
```

## 🔧 依赖管理

### Java后端依赖
使用Maven管理，详见：[Java后端依赖管理](ai-manager-backend/README.md#依赖管理)

### Python核心依赖
手动安装所需包，详见：[迁移指南](MIGRATION_GUIDE.md#python核心依赖管理)

## 🎯 功能特性

- 🎤 **语音识别与理解**: 支持中文语音识别
- 🤖 **AI助手**: 基于通义千问的智能对话
- 🔊 **语音合成反馈**: 文本转语音输出
- 💻 **系统控制**: 播放音乐、文件操作、应用启动
- 📝 **文本生成与处理**: 文章写作、总结、翻译
- 🔄 **多步骤任务编排**: 复杂任务分解执行
- 🧠 **上下文记忆**: 对话历史记录
- 📊 **数据管理**: 用户设置、历史记录存储
- 🔒 **安全监控**: 依赖安全检查、日志管理

## 🛠️ 开发指南

### Java后端开发
- 使用Spring Boot框架
- REST API设计
- 数据库集成(H2/SQLite)
- 日志系统(Logback)
- 跨平台脚本工具

### Python核心开发
- 语音识别(SpeechRecognition)
- AI模型集成(通义千问)
- 系统控制(psutil, subprocess)
- 语音合成(pyttsx3)

## 📚 文档

- [Java后端使用指南](ai-manager-backend/README.md) - Java后端详细使用说明
- [依赖管理迁移指南](MIGRATION_GUIDE.md) - 从Python到Java依赖管理的迁移说明
- [依赖管理策略](ai-manager-backend/docs/development/DEPENDENCY_MANAGEMENT.md) - 企业级依赖管理策略
- [项目结构说明](ai-manager-backend/PROJECT_STRUCTURE.md) - Java后端项目结构

## 🤝 贡献

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License