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

## 项目结构

```
lib/
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
