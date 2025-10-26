import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart';

class VoiceService extends ChangeNotifier {
  final SpeechToText _speechToText = SpeechToText();
  bool _isListening = false;
  bool _speechEnabled = false;
  String _lastWords = '';
  String _lastError = '';
  String _currentLocaleId = '';
  
  // 语音识别完成回调
  Function(String)? onRecognitionComplete;

  // Getters
  bool get isListening => _isListening;
  bool get speechEnabled => _speechEnabled;
  String get lastWords => _lastWords;
  String get lastError => _lastError;
  String get currentLocaleId => _currentLocaleId;

  // 初始化语音服务
  Future<bool> initialize() async {
    try {
      _speechEnabled = await _speechToText.initialize(
        onError: (error) {
          _lastError = error.errorMsg;
          notifyListeners();
        },
        onStatus: (status) {
          if (status == 'listening') {
            _isListening = true;
          } else {
            _isListening = false;
          }
          notifyListeners();
        },
        debugLogging: true,
      );
      
      if (_speechEnabled) {
        // 获取系统语言
        var systemLocale = await _speechToText.systemLocale();
        _currentLocaleId = systemLocale?.localeId ?? 'zh_CN';
        
        // 如果系统语言不是中文，尝试设置为中文
        if (!_currentLocaleId.contains('zh')) {
          var locales = await _speechToText.locales();
          var chineseLocale = locales.firstWhere(
            (locale) => locale.localeId.contains('zh'),
            orElse: () => systemLocale ?? locales.first,
          );
          _currentLocaleId = chineseLocale.localeId;
        }
      }
      
      notifyListeners();
      return _speechEnabled;
    } catch (e) {
      _lastError = '语音服务初始化失败: $e';
      notifyListeners();
      return false;
    }
  }

  // 开始监听
  Future<bool> startListening() async {
    if (!_speechEnabled) {
      _lastError = '语音识别未启用，请先初始化';
      notifyListeners();
      return false;
    }

    try {
      await _speechToText.listen(
        onResult: (result) {
          _lastWords = result.recognizedWords;
          notifyListeners();
          
          // 如果识别完成且有结果，触发回调
          if (result.finalResult && _lastWords.isNotEmpty) {
            onRecognitionComplete?.call(_lastWords);
          }
        },
        listenFor: const Duration(seconds: 30),
        pauseFor: const Duration(seconds: 3),
        partialResults: true,
        localeId: _currentLocaleId,
        onSoundLevelChange: (level) {
          // 可以在这里添加音量级别变化的处理
        },
        cancelOnError: true,
      );
      return true;
    } catch (e) {
      _lastError = '开始监听失败: $e';
      notifyListeners();
      return false;
    }
  }

  // 停止监听
  Future<void> stopListening() async {
    try {
      await _speechToText.stop();
      _isListening = false;
      notifyListeners();
    } catch (e) {
      _lastError = '停止监听失败: $e';
      notifyListeners();
    }
  }

  // 取消监听
  Future<void> cancelListening() async {
    try {
      await _speechToText.cancel();
      _isListening = false;
      notifyListeners();
    } catch (e) {
      _lastError = '取消监听失败: $e';
      notifyListeners();
    }
  }

  // 检查麦克风权限
  Future<bool> checkMicrophonePermission() async {
    try {
      bool available = await _speechToText.initialize();
      return available;
    } catch (e) {
      _lastError = '检查麦克风权限失败: $e';
      notifyListeners();
      return false;
    }
  }

  // 请求麦克风权限
  Future<bool> requestMicrophonePermission() async {
    try {
      bool available = await _speechToText.initialize();
      if (!available) {
        _lastError = '无法获取麦克风权限';
        notifyListeners();
        return false;
      }
      _speechEnabled = available;
      notifyListeners();
      return true;
    } catch (e) {
      _lastError = '请求麦克风权限失败: $e';
      notifyListeners();
      return false;
    }
  }

  // 清除最后的识别结果
  void clearLastWords() {
    _lastWords = '';
    notifyListeners();
  }
}