import 'dart:async';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:http/http.dart' as http;

class VoiceService {
  late stt.SpeechToText _speech;
  bool _isListening = false;
  String _text = '';
  final String _backendUrl = 'http://localhost:8080/voice'; // 本地开发服务器URL

  VoiceService() {
    _speech = stt.SpeechToText();
  }

  bool get isListening => _isListening;
  String get text => _text;

  Future<void> initialize() async {
    bool available = await _speech.initialize(
      onStatus: (val) => print('onStatus: $val'),
      onError: (val) => print('onError: $val'),
    );
    if (!available) {
      print('语音识别不可用');
    }
  }

  Future<void> startListening() async {
    if (!_isListening) {
      _isListening = true;
      await _speech.listen(
        onResult: (result) {
          _text = result.recognizedWords;
          if (result.finalResult) {
            _sendToBackend(_text);
          }
        },
        localeId: 'zh_CN', // 中文识别
      );
    }
  }

  Future<void> stopListening() async {
    if (_isListening) {
      await _speech.stop();
      _isListening = false;
    }
  }

  Future<void> _sendToBackend(String text) async {
    try {
      final response = await http.post(
        Uri.parse(_backendUrl),
        headers: {
          'Content-Type': 'application/json; charset=UTF-8',
        },
        body: '{"text": "$text"}',
      );
      
      if (response.statusCode == 200) {
        print('语音数据已成功发送到后端');
      } else {
        print('发送语音数据到后端失败: ${response.statusCode}');
      }
    } catch (e) {
      print('发送语音数据到后端时出错: $e');
    }
  }

  void cancelListening() {
    if (_isListening) {
      _speech.cancel();
      _isListening = false;
    }
  }
}