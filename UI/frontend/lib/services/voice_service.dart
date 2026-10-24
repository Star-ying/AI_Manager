import 'dart:async';

import 'package:flutter/foundation.dart';

import 'api_service.dart';

// 【留痕 2026-10-24】收音权统一归后端（Vosk 常驻监听 PC 麦克风），本服务改为纯遥控器：
// 原基于 speech_to_text 的本地识别已停用，避免与后端 Vosk 抢麦、双 ASR 管线打架。
// import 'package:speech_to_text/speech_to_text.dart';

class VoiceService extends ChangeNotifier {
  // 原本地识别引擎已停用：
  // final SpeechToText _speechToText = SpeechToText();
  bool _isListening = false;
  bool _speechEnabled = false; // 语义变更：现在表示"后端 API 可达"
  String _lastWords = '';
  String _lastError = '';
  String _currentLocaleId = 'zh_CN';

  Timer? _statusPollTimer;
  String _polledTranscript = '';
  
  // 语音识别完成回调
  Function(String)? onRecognitionComplete;

  // Getters
  bool get isListening => _isListening;
  bool get speechEnabled => _speechEnabled;
  String get lastWords => _lastWords;
  String get lastError => _lastError;
  String get currentLocaleId => _currentLocaleId;

  // 初始化语音服务（原：初始化本地 speech_to_text；现：探测后端 API 健康并同步收音开关）
  Future<bool> initialize() async {
    // 【留痕】原本地初始化逻辑（含 locale 选择）已停用，改为后端健康探测：
    // _speechEnabled = await _speechToText.initialize(...);
    // var systemLocale = await _speechToText.systemLocale(); ... 选择中文 locale ...
    try {
      final health = await ApiService.checkHealth();
      _speechEnabled = health != null;
      if (!_speechEnabled) {
        _lastError = '后端服务不可达，请确认 AI 助手（main.py）已启动';
      } else {
        _lastError = '';
        await _refreshStatusOnce();
      }
      notifyListeners();
      return _speechEnabled;
    } catch (e) {
      _lastError = '语音服务初始化失败: $e';
      notifyListeners();
      return false;
    }
  }

  // 开始监听（原：本地 _speechToText.listen；现：遥控后端 Vosk 开收音 + 轮询识别结果）
  Future<bool> startListening() async {
    // 【留痕】原本地 listen（onResult/finalResult 回调直推）已停用：
    // await _speechToText.listen(onResult: (result) { ... onRecognitionComplete?.call(...) }, ...);
    try {
      final ok = await ApiService.controlListen('start');
      if (ok == null) {
        _lastError = '开始监听失败：后端未响应';
        _isListening = false;
        notifyListeners();
        return false;
      }
      _isListening = true;
      _lastError = '';
      _startPolling();
      notifyListeners();
      return true;
    } catch (e) {
      _lastError = '开始监听失败: $e';
      notifyListeners();
      return false;
    }
  }

  // 停止监听（原：本地 _speechToText.stop；现：关闭后端收音并停轮询）
  Future<void> stopListening() async {
    try {
      await ApiService.controlListen('stop');
      _stopPolling();
      _isListening = false;
      notifyListeners();
    } catch (e) {
      _lastError = '停止监听失败: $e';
      notifyListeners();
    }
    // 原本地实现已停用：await _speechToText.stop();
  }

  // 取消监听（与 stop 同义，保留原接口兼容调用方）
  Future<void> cancelListening() async {
    await stopListening();
    // 原本地实现已停用：await _speechToText.cancel();
  }

  void _startPolling() {
    _stopPolling();
    _statusPollTimer = Timer.periodic(const Duration(milliseconds: 800), (_) async {
      final status = await ApiService.getStatus();
      if (status == null) {
        _speechEnabled = false;
        _lastError = '后端状态轮询失败，服务可能已退出';
        notifyListeners();
        return;
      }
      _speechEnabled = true;
      _isListening = status.isListening ?? _isListening;
      final transcript = status.lastTranscript ?? '';
      if (transcript.isNotEmpty && transcript != _polledTranscript) {
        _polledTranscript = transcript;
        _lastWords = transcript;
        onRecognitionComplete?.call(_lastWords);
      }
      notifyListeners();
    });
  }

  void _stopPolling() {
    _statusPollTimer?.cancel();
    _statusPollTimer = null;
  }

  Future<void> _refreshStatusOnce() async {
    final status = await ApiService.getStatus();
    if (status != null) {
      _isListening = status.isListening ?? _isListening;
      _polledTranscript = status.lastTranscript ?? '';
      if (_isListening) _startPolling();
    }
  }

  // 检查麦克风权限（原：本地权限探测；现：后端可达即视为可用，麦克风归后端管理）
  Future<bool> checkMicrophonePermission() async {
    // 原本地实现已停用：bool available = await _speechToText.initialize(); return available;
    final health = await ApiService.checkHealth();
    return health != null;
  }

  // 请求麦克风权限（同上，保留接口兼容）
  Future<bool> requestMicrophonePermission() async {
    final available = await checkMicrophonePermission();
    if (!available) {
      _lastError = '无法连接后端服务，也就无法使用其麦克风';
      notifyListeners();
      return false;
    }
    _speechEnabled = available;
    notifyListeners();
    return true;
  }

  // 清除最后的识别结果
  void clearLastWords() {
    _lastWords = '';
    _polledTranscript = '';
    notifyListeners();
  }

  @override
  void dispose() {
    _stopPolling();
    super.dispose();
  }
}