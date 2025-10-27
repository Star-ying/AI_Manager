class AppConfig {
  // 是否为测试环境
  static const bool isTestMode = true;

  // API配置
  static const String apiBaseUrl = 'http://localhost:8080/api';

  // 是否显示测试UI元素
  static const bool showTestUI = false;

  // 日志级别
  static const LogLevel logLevel = isTestMode ? LogLevel.debug : LogLevel.info;
}

enum LogLevel {
  debug,
  info,
  warning,
  error,
}
