#!/bin/bash

# 构建脚本 - 用于区分测试和生产环境

echo "请选择构建类型:"
echo "1. 测试环境 (包含测试UI)"
echo "2. 生产环境 (不包含测试UI)"
read -p "请输入选项 (1 或 2): " choice

case $choice in
  1)
    echo "正在构建测试环境版本..."
    # 修改配置文件中的isTestMode为true
    sed -i '' 's/static const bool isTestMode = false;/static const bool isTestMode = true;/' lib/config/app_config.dart
    flutter build apk --debug
    echo "测试环境构建完成"
    ;;
  2)
    echo "正在构建生产环境版本..."
    # 修改配置文件中的isTestMode为false
    sed -i '' 's/static const bool isTestMode = true;/static const bool isTestMode = false;/' lib/config/app_config.dart
    flutter build apk --release
    echo "生产环境构建完成"
    ;;
  *)
    echo "无效选项"
    exit 1
    ;;
esac