import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/api_models.dart';

class ApiService {
  static const String _baseUrl = 'http://127.0.0.1:5001/api';
  static const String _apiKey = 'your-secret-token'; // 可选的API密钥
  
  // 获取通用请求头
  static Map<String, String> _getHeaders({bool includeApiKey = false}) {
    final headers = {'Content-Type': 'application/json'};
    
    // 如果需要，添加API密钥
    if (includeApiKey && _apiKey.isNotEmpty) {
      headers['X-API-Key'] = _apiKey;
    }
    
    return headers;
  }
  
  // 健康检查
  static Future<HealthResponse?> checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/health'),
        headers: _getHeaders(),
      );
      
      if (response.statusCode == 200) {
        return HealthResponse.fromJson(jsonDecode(response.body));
      }
      return null;
    } catch (e) {
      print('健康检查失败: $e');
      return null;
    }
  }
  
  // 获取当前状态
  static Future<StatusResponse?> getStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/status'),
        headers: _getHeaders(includeApiKey: true),
      );
      
      if (response.statusCode == 200) {
        return StatusResponse.fromJson(jsonDecode(response.body));
      }
      return null;
    } catch (e) {
      print('获取状态失败: $e');
      return null;
    }
  }
  
  // 启动助手
  static Future<StartResponse?> startAssistant() async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/start'),
        headers: _getHeaders(includeApiKey: true),
        body: jsonEncode({}),
      );
      
      if (response.statusCode == 200) {
        return StartResponse.fromJson(jsonDecode(response.body));
      }
      return null;
    } catch (e) {
      print('启动助手失败: $e');
      return null;
    }
  }
  
  // 发送命令
  static Future<CommandResponse?> sendCommand(
    String text, {
    Map<String, dynamic>? context,
    bool shouldSpeak = true,
    bool returnPlan = false,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/command'),
        headers: _getHeaders(includeApiKey: true),
        body: jsonEncode({
          'text': text,
          if (context != null) 'context': context,
          'options': {
            'should_speak': shouldSpeak,
            'return_plan': returnPlan,
          },
        }),
      );
      
      if (response.statusCode == 200) {
        return CommandResponse.fromJson(jsonDecode(response.body));
      }
      return null;
    } catch (e) {
      print('发送命令失败: $e');
      return null;
    }
  }
  
  // 播报语音
  static Future<TTSResponse?> speak(String text) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/tts/speak'),
        headers: _getHeaders(includeApiKey: true),
        body: jsonEncode({'text': text}),
      );
      
      if (response.statusCode == 200) {
        return TTSResponse.fromJson(jsonDecode(response.body));
      }
      return null;
    } catch (e) {
      print('播报语音失败: $e');
      return null;
    }
  }
  
  // 远程唤醒
  static Future<WakeupResponse?> wakeup({
    String device = 'phone',
    String location = 'living_room',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/wakeup'),
        headers: _getHeaders(includeApiKey: true),
        body: jsonEncode({
          'device': device,
          'location': location,
        }),
      );
      
      if (response.statusCode == 200) {
        return WakeupResponse.fromJson(jsonDecode(response.body));
      }
      return null;
    } catch (e) {
      print('远程唤醒失败: $e');
      return null;
    }
  }
}