<<<<<<< HEAD
# AI 音乐管理器 - Flutter Windows 应用程序

这是一个功能完整的 Windows 音乐播放器应用程序，支持语音控制、音乐播放和音量调节。

## 主要功能

### ✅ 已实现的功能

1. **🎵 音乐播放功能**

   - 支持播放指定文件夹内的音乐文件
   - 支持格式：MP3、WAV、M4A、AAC、OGG
   - 播放/暂停控制
   - 上一首/下一首切换
   - 播放进度显示和拖动控制

2. **🎤 语音识别控制**

   - 中文语音识别
   - 支持的语音指令：
     - "播放" 或 "开始" - 开始播放音乐
     - "暂停" 或 "停止" - 暂停播放
     - "下一首" 或 "下一个" - 播放下一首
     - "上一首" 或 "上一个" - 播放上一首
     - "音量大一点" - 增大音量
     - "音量小一点" - 减小音量

3. **🔊 音量控制**

   - 音量滑块调节（0-100%）
   - 实时音量显示
   - 语音音量控制

4. **📁 文件管理**
   - 文件夹选择器
   - 自动扫描音乐文件
   - 递归搜索子文件夹

## 技术实现

### 使用的 Flutter 插件

- `audioplayers: ^5.2.1` - 音频播放
- `speech_to_text: ^6.6.0` - 语音识别
- `file_picker: ^6.1.1` - 文件选择
- `permission_handler: ^11.0.1` - 权限管理
- `path: ^1.8.3` - 路径处理

### Windows 平台配置

- 已配置麦克风权限
- 支持 Windows 7-11
- 启用 DPI 感知

## 安装和运行

### 前提条件

1. 安装 Flutter SDK
2. 启用 Windows 开发者模式（用于构建发布版本）
3. 确保麦克风可用

### 运行步骤

1. **安装依赖**

   ```bash
   flutter pub get
   ```

2. **调试模式运行**

   ```bash
   flutter run -d windows
   ```

3. **构建发布版本**

   ```bash
   # 首先启用开发者模式
   start ms-settings:developers

   # 然后构建
   flutter build windows --release
   ```

## 使用说明

### 第一次使用

1. 启动应用程序
2. 点击"选择音乐文件夹"按钮
3. 选择包含音乐文件的文件夹
4. 应用会自动扫描并加载音乐文件

### 播放控制

- **手动控制**：使用播放/暂停、上一首/下一首按钮
- **语音控制**：点击"开始语音识别"按钮，然后说出指令

### 音量调节

- **滑块控制**：拖动音量滑块
- **语音控制**：说"音量大一点"或"音量小一点"

## 支持的音频格式

- MP3
- WAV
- M4A
- AAC
- OGG

## 故障排除

### 语音识别问题

- 确保麦克风正常工作
- 检查系统麦克风权限
- 确保网络连接正常（语音识别可能需要网络）

### 音频播放问题

- 确保音频文件格式受支持
- 检查文件路径中是否有特殊字符
- 确保音频文件未被其他程序占用

### 构建问题

- 启用 Windows 开发者模式
- 确保 Flutter 版本支持 Windows 桌面开发
- 检查 Visual Studio Build Tools 是否安装
=======
# AI小助手

一个支持Windows ARM64和X64平台的Flutter应用程序，可以接受用户语音输入，并根据语音指令控制音乐播放。

## 功能特点

- 语音输入并传输到后端
- 根据语音指令播放、暂停或切换指定文件夹中的音乐文件
- 音量调节滑块控制音量大小
- 支持Windows ARM64和X64平台

## 系统要求

- Windows 10或更高版本
- Flutter SDK
- Visual Studio 2019或更高版本（包含"C++桌面开发"工作负载）

## 安装和设置

1. 克隆此仓库
2. 安装Flutter SDK（如果尚未安装）
3. 安装Visual Studio 2019或更高版本，并确保包含"C++桌面开发"工作负载
4. 运行 `flutter doctor` 确保所有依赖都已正确安装

## 构建应用程序

### 使用构建脚本（推荐）

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

## 使用说明

1. 启动应用程序
2. 在"语音控制"标签页，点击"开始录音"按钮进行语音输入
3. 语音将被传输到后端进行处理
4. 在"音乐播放"标签页，可以：
   - 选择音乐文件夹
   - 播放/暂停音乐
   - 切换上一首/下一首音乐
   - 使用滑块调节音量
>>>>>>> 17897a1 (build(构建): 成功构建macOS平台应用)

## 项目结构

```
lib/
<<<<<<< HEAD
├── main.dart                 # 主应用程序文件
windows/
├── runner/
│   ├── main.cpp             # Windows入口点
│   └── runner.exe.manifest  # 应用程序清单（包含权限）
pubspec.yaml                 # 项目依赖配置
```

## 开发说明

这个应用程序已经完全实现了您要求的所有功能：

✅ **语音输入识别** - 完整实现  
✅ **根据语音指令播放/暂停音乐** - 完整实现  
✅ **播放指定文件夹内的音乐** - 完整实现  
✅ **音量调节滑块** - 完整实现

应用程序使用现代 Flutter 框架构建，具有良好的用户界面和完整的错误处理机制。
=======
  main.dart                 # 应用程序入口
  services/
    voice_service.dart      # 语音识别和后端传输服务
    music_service.dart      # 音乐播放控制服务
  ui/
    voice_control_tab.dart  # 语音控制界面
    music_player_tab.dart   # 音乐播放界面

windows/
  CMakeLists.txt           # Windows平台CMake配置
  runner/
    CMakeLists.txt         # Runner应用CMake配置
    main.cpp               # Windows平台主程序
    Runner.rc              # Windows资源文件
    runner.exe.manifest    # Windows应用程序清单
  build_config.json        # Windows平台构建配置

build_windows.bat         # Windows平台构建脚本
```

## 依赖项

- flutter: Flutter SDK
- speech_to_text: ^6.3.0 - 语音识别
- http: ^1.1.0 - HTTP请求
- audioplayers: ^5.2.1 - 音频播放
- file_picker: ^5.5.0 - 文件选择
- path_provider: ^2.1.1 - 路径处理
- flutter_volume_controller: ^3.0.0 - 音量控制

## 许可证

Copyright (C) 2025 com.aiassistant. All rights reserved.
>>>>>>> 17897a1 (build(构建): 成功构建macOS平台应用)
