# 安装和配置指南

## 🚀 快速开始

### 1. 启用 Windows 开发者模式

这是运行 Flutter Windows 应用程序的**必要步骤**：

1. 按 `Win + I` 打开 Windows 设置
2. 导航到 "隐私和安全" -> "开发者选项"
3. 开启 "开发者模式"
4. 重启计算机

或者在命令行中运行：

```cmd
start ms-settings:developers
```

### 2. 验证 Flutter 环境

```bash
flutter doctor
```

确保以下项目显示为 ✓：

- Flutter (Channel stable)
- Windows toolchain
- Visual Studio Build Tools

### 3. 运行应用程序

#### 方法一：使用批处理文件（推荐）

双击 `build_and_run.bat` 文件

#### 方法二：手动执行

```bash
# 安装依赖
flutter pub get

# 运行调试版本
flutter run -d windows

# 或构建发布版本
flutter build windows --release
```

## 🎵 应用程序功能

### 主要特性

- ✅ 音乐播放器（支持 MP3、WAV、M4A、AAC、OGG）
- ✅ 中文语音识别控制
- ✅ 音量调节滑块
- ✅ 文件夹音乐扫描
- ✅ 播放进度控制

### 语音指令

| 指令                 | 功能         |
| -------------------- | ------------ |
| "播放" 或 "开始"     | 开始播放音乐 |
| "暂停" 或 "停止"     | 暂停播放     |
| "下一首" 或 "下一个" | 下一首歌曲   |
| "上一首" 或 "上一个" | 上一首歌曲   |
| "音量大一点"         | 增加音量     |
| "音量小一点"         | 减少音量     |

## 🔧 故障排除

### 构建问题

**错误**: "Building with plugins requires symlink support"
**解决**: 启用 Windows 开发者模式并重启计算机

**错误**: Visual Studio Build Tools 未找到
**解决**: 安装 Visual Studio Community 或 Build Tools

### 运行时问题

**问题**: 语音识别不工作
**解决**:

1. 检查麦克风权限
2. 确保网络连接正常
3. 在 Windows 隐私设置中允许应用访问麦克风

**问题**: 音频播放失败
**解决**:

1. 确保音频文件格式受支持
2. 检查文件路径中没有特殊字符
3. 确保音频文件未被占用

## 📁 项目结构

```
AI_Manager/UI/frontend/
├── lib/
│   └── main.dart              # 主应用程序
├── windows/                   # Windows平台配置
├── pubspec.yaml              # 依赖配置
├── build_and_run.bat         # 自动构建脚本
└── README.md                 # 详细说明
```

## 🏗️ 开发环境要求

- Flutter SDK (>=3.1.0)
- Windows 10/11
- Visual Studio Build Tools 2019+
- 开发者模式已启用

## 📞 技术支持

如果遇到问题，请：

1. 检查 Flutter 环境: `flutter doctor`
2. 清理并重新构建: `flutter clean && flutter pub get`
3. 确保开发者模式已启用
4. 检查防火墙和杀毒软件设置
