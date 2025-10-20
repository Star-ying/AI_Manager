# AI Manager - 语音控制AI助手

一个基于大模型的语音控制应用，可以通过语音对话控制电脑执行各种任务。

## 🏗️ 项目架构

本项目采用**混合架构**设计：
- **Java后端**: 提供REST API、数据库管理、日志系统
- **Python核心**: 语音识别、AI助手、系统控制、语音合成

## 🚀 快速开始（Windows）

### 环境要求
- Java 17+（后端服务，已内置 Maven Wrapper：mvnw.cmd）
- 可选：Python 3.8+（仅用于开发机打包Python核心为exe，最终用户无需Python）

### 安装和运行

#### 1. 启动Java后端服务（Windows）
```cmd
cd ai-manager-backend
mvnw.cmd clean package
mvnw.cmd spring-boot:run
```

或使用脚本：
```cmd
scripts\build.bat --clean
```

#### 2. 一键运行（最终用户）
打包完成后，用户在Windows上双击 `start_all.bat` 即可运行（零配置）。

## 📁 项目结构（摘要）
```
AI_Manager/
├── ai-manager-backend/          # Java后端服务
│   ├── pom.xml                  # Maven依赖管理
│   ├── mvnw.cmd                 # Windows Maven Wrapper
│   ├── scripts/                 # Windows脚本工具
│   └── src/                     # Java源代码
├── Progress/                    # Python核心（开发机上用于打包）
├── scripts/windows/             # Windows 一键启动与打包脚本
├── my_resources/                # 资源文件
└── config.json                  # 配置文件
```

## 🔧 依赖管理

- Java后端依赖使用Maven管理，详见：[Java后端使用指南](ai-manager-backend/README.md)
- 迁移与说明：[依赖管理迁移指南](MIGRATION_GUIDE.md)

## 🎯 功能特性

- 🎤 语音识别与理解（中文）
- 🤖 AI助手（通义千问）
- 🔊 语音合成反馈
- 💻 系统控制（音乐、文件、应用）
- 📝 文本生成/总结/翻译
- 🔄 多步骤任务编排
- 🧠 上下文记忆
- 📊 数据管理
- 🔒 依赖与日志管理

## 📚 文档
- [Java后端使用指南](ai-manager-backend/README.md)
- [依赖管理迁移指南](MIGRATION_GUIDE.md)
- [依赖管理策略](ai-manager-backend/docs/development/DEPENDENCY_MANAGEMENT.md)
- [项目结构说明](ai-manager-backend/PROJECT_STRUCTURE.md)

## 🤝 贡献
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证
MIT License