# AI小助手

一个支持Windows ARM64和X64平台的Flutter应用程序，可以接受用户语音输入，并根据语音指令控制音乐播放和与AI助手交互。

## 功能特点

- 语音输入并传输到后端
- 根据语音指令播放、暂停或切换指定文件夹中的音乐文件
- 音量调节滑块控制音量大小
- AI助手交互功能
- 支持Windows ARM64和X64平台
- 支持测试和生产环境切换

## 系统要求

- Windows 10或更高版本
- Flutter SDK
- Visual Studio 2019或更高版本（包含"C++桌面开发"工作负载）

## 安装和设置

1. 克隆此仓库
2. 安装Flutter SDK（如果尚未安装）
3. 安装Visual Studio 2019或更高版本，并确保包含"C++桌面开发"工作负载
4. 运行 `flutter doctor` 确保所有依赖都已正确安装

## 环境配置

应用支持两种环境模式：

### 测试环境
- 包含测试UI界面
- 使用本地API端点 (http://localhost:8080/api)
- 显示详细的调试信息和测试按钮

### 生产环境
- 不包含测试UI界面
- 使用生产API端点 (https://api.yourapp.com)
- 简化的用户界面

## 构建应用程序

### 使用构建脚本（推荐）

#### macOS/Linux
```bash
./build.sh
```
然后选择构建类型：
1. 测试环境
2. 生产环境

#### Windows
1. 在Windows上打开命令提示符或PowerShell
2. 导航到项目根目录
3. 运行构建脚本：
   ```
   build_windows.bat
   ```
4. 构建完成后，可执行文件将位于以下位置：
   - X64版本：`build\windows\x64\runner\Release\ai_assistant.exe`
   - ARM64版本：`build\windows\arm64\runner\Release\ai_assistant.exe`

### 手动构建

#### 测试环境
```bash
# 修改配置文件
sed -i '' 's/static const bool isTestMode = false;/static const bool isTestMode = true;/' lib/config/app_config.dart

# 构建应用
flutter build apk --debug  # Android
flutter build windows --debug  # Windows
```

#### 生产环境
```bash
# 修改配置文件
sed -i '' 's/static const bool isTestMode = true;/static const bool isTestMode = false;/' lib/config/app_config.dart

# 构建应用
flutter build apk --release  # Android
flutter build windows --release  # Windows
```

#### 为X64平台构建

```
flutter build windows --release --target-platform windows-x64
```

#### 为ARM64平台构建

```
flutter build windows --release --target-platform windows-arm64
```

## 运行应用程序

### 开发模式

```
flutter run -d windows
```

### 发布模式

从构建目录中运行可执行文件：
- X64版本：`build\windows\x64\runner\Release\ai_assistant.exe`
- ARM64版本：`build\windows\arm64\runner\Release\ai_assistant.exe`

## 语音命令

应用支持以下语音命令：

### AI助手控制
- "你好助手" - 启动AI助手
- "今天天气怎么样" - 询问天气
- "设置一个闹钟" - 设置提醒
- "帮我查一下资料" - 搜索信息

### 播放控制
- "播放音乐" 或 "play" - 播放当前音乐
- "暂停音乐" 或 "pause" - 暂停当前音乐
- "下一首" 或 "next" - 播放下一首音乐
- "上一首" 或 "previous" - 播放上一首音乐

### 音量控制
- "增加音量" 或 "音量大一点" - 增加音量
- "减小音量" 或 "音量小一点" - 减少音量
- "音量50%" - 设置音量为50%

### 播放指定歌曲
- "播放[歌曲名]" - 播放指定的歌曲
  例如: "播放夜曲"

## 使用说明

1. 启动应用程序
2. 在"语音控制"标签页，点击"开始录音"按钮进行语音输入
3. 语音将被传输到后端进行处理
4. 在"音乐播放"标签页，可以：
   - 选择音乐文件夹
   - 播放/暂停音乐
   - 切换上一首/下一首音乐
   - 使用滑块调节音量
5. 在测试环境中，可以使用额外的测试功能：
   - API连接测试
   - 状态查询
   - 助手启动测试
   - 命令发送测试

## 项目结构

```
lib/
  main.dart                 # 应用程序入口
  config/
    app_config.dart         # 应用配置文件
  providers/
    voice_service.dart      # 语音识别和后端传输服务
    music_service.dart      # 音乐播放控制服务
    api_provider.dart       # API交互服务
  services/
    voice_service.dart      # 语音识别和后端传输服务
    music_service.dart      # 音乐播放控制服务
    api_service.dart        # API服务实现
  models/
    api_models.dart         # API数据模型

windows/
  CMakeLists.txt           # Windows平台CMake配置
  runner/
    CMakeLists.txt         # Runner应用CMake配置
    main.cpp               # Windows平台主程序
    Runner.rc              # Windows资源文件
    runner.exe.manifest    # Windows应用程序清单
  build_config.json        # Windows平台构建配置

build_windows.bat         # Windows平台构建脚本
build.sh                  # macOS/Linux平台构建脚本
```

## API配置

API配置在 `lib/config/app_config.dart` 文件中：

```dart
class AppConfig {
  // 是否为测试环境
  static const bool isTestMode = true;
  
  // API配置
  static const String apiBaseUrl = isTestMode 
      ? 'http://localhost:8080/api'  // 测试环境API
      : 'https://api.yourapp.com';   // 生产环境API
  
  // 是否显示测试UI元素
  static const bool showTestUI = isTestMode;
}
```

## 测试功能

在测试环境中，应用会显示额外的测试UI区域，包括：

- API连接测试
- 状态查询
- 助手启动测试
- 命令发送测试

这些功能在生产环境中会被隐藏。

## 注意事项

1. 确保在构建前已正确配置环境模式
2. 生产环境构建前请仔细测试所有功能
3. API端点需要根据实际部署情况进行配置
4. 测试功能仅用于开发和调试，不应在生产环境中使用

## 依赖项

- flutter: Flutter SDK
- speech_to_text: ^6.3.0 - 语音识别
- http: ^1.1.0 - HTTP请求
- audioplayers: ^5.2.1 - 音频播放
- file_picker: ^5.5.0 - 文件选择
- path_provider: ^2.1.1 - 路径处理
- flutter_volume_controller: ^3.0.0 - 音量控制
- provider: ^6.0.5 - 状态管理

## 许可证

Copyright (C) 2025 com.aiassistant. All rights reserved.
