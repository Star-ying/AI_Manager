# Flutter 中国镜像配置指南

## 🚀 快速设置

已为您创建了 Flutter 中国镜像的永久环境变量设置。这将大大提高在中国网络环境下使用 Flutter 的速度。

## 📁 相关文件说明

### 1. `setup_flutter_mirror.bat` - 永久设置工具

- **功能**: 一次性永久设置 Flutter 中国镜像环境变量
- **使用方法**: 双击运行，按提示操作
- **设置内容**:
  - `PUB_HOSTED_URL=https://pub.flutter-io.cn`
  - `FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn`

### 2. `flutter_mirror_manager.bat` - 管理工具

- **功能**: 管理 Flutter 镜像环境变量
- **包含选项**:
  - 设置环境变量
  - 检查当前状态
  - 删除环境变量
  - 验证 Flutter 环境

### 3. `test_flutter_mirror.bat` - 测试工具

- **功能**: 测试 Flutter 中国镜像是否正常工作
- **测试内容**: Flutter 版本、Doctor 状态、依赖包下载速度

### 4. 更新的启动脚本

- `start_music_app.bat` - 已更新，自动设置镜像
- `UI/dev_run.bat` - 已更新，自动设置镜像

## 🔧 使用步骤

### 第一次设置（推荐）

1. **双击运行** `setup_flutter_mirror.bat`
2. 按提示确认设置
3. **重启** 所有命令行窗口
4. 运行 `test_flutter_mirror.bat` 验证

### 验证设置

```bash
# 在新的命令行窗口中运行
echo %PUB_HOSTED_URL%
echo %FLUTTER_STORAGE_BASE_URL%
```

### 测试应用

双击运行 `start_music_app.bat` 启动音乐应用

## 🌟 优势

### 设置前（使用官方源）

- 下载速度慢
- 经常连接超时
- 可能无法访问

### 设置后（使用中国镜像）

- ⚡ 下载速度快
- 🔄 连接稳定
- 📦 依赖安装顺畅

## 🛠️ 环境变量详解

### PUB_HOSTED_URL

- **作用**: 设置 Dart 包管理器 pub 的镜像地址
- **默认**: https://pub.dartlang.org
- **中国镜像**: https://pub.flutter-io.cn

### FLUTTER_STORAGE_BASE_URL

- **作用**: 设置 Flutter SDK 和工具的下载地址
- **默认**: https://storage.googleapis.com
- **中国镜像**: https://storage.flutter-io.cn

## 🔍 故障排除

### 如果环境变量不生效

1. 确保已重启命令行窗口
2. 运行 `flutter_mirror_manager.bat` 检查状态
3. 手动验证: `flutter pub deps`

### 如果下载仍然很慢

1. 检查网络连接
2. 尝试清理缓存: `flutter clean`
3. 重新获取依赖: `flutter pub get`

### 恢复默认设置

运行 `flutter_mirror_manager.bat`，选择"删除 Flutter 镜像环境变量"

## 📞 技术支持

如有问题，请：

1. 运行 `test_flutter_mirror.bat` 获取诊断信息
2. 检查 Flutter Doctor: `flutter doctor`
3. 查看详细错误信息

---

**注意**: 这些设置只影响 Flutter 相关的下载，不会影响其他网络活动。
