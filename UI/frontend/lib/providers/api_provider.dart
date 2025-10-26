import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../models/api_models.dart';

class ApiProvider extends ChangeNotifier {
  HealthResponse? _healthStatus;
  StatusResponse? _currentStatus;
  StartResponse? _startResponse;
  CommandResponse? _lastCommandResponse;
  TTSResponse? _lastTTSResponse;
  WakeupResponse? _lastWakeupResponse;
  
  bool _isLoading = false;
  String? _lastError;
  
  // Getters
  HealthResponse? get healthStatus => _healthStatus;
  StatusResponse? get currentStatus => _currentStatus;
  StartResponse? get startResponse => _startResponse;
  CommandResponse? get lastCommandResponse => _lastCommandResponse;
  TTSResponse? get lastTTSResponse => _lastTTSResponse;
  WakeupResponse? get lastWakeupResponse => _lastWakeupResponse;
  
  bool get isLoading => _isLoading;
  String? get lastError => _lastError;
  
  // 健康检查
  Future<bool> checkHealth() async {
    _setLoading(true);
    _clearError();
    
    try {
      _healthStatus = await ApiService.checkHealth();
      if (_healthStatus == null) {
        _setError('健康检查失败');
        return false;
      }
      notifyListeners();
      return true;
    } catch (e) {
      _setError('健康检查异常: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }
  
  // 获取状态
  Future<bool> getStatus() async {
    _setLoading(true);
    _clearError();
    
    try {
      _currentStatus = await ApiService.getStatus();
      if (_currentStatus == null) {
        _setError('获取状态失败');
        return false;
      }
      notifyListeners();
      return true;
    } catch (e) {
      _setError('获取状态异常: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }
  
  // 启动助手
  Future<bool> startAssistant() async {
    _setLoading(true);
    _clearError();
    
    try {
      _startResponse = await ApiService.startAssistant();
      if (_startResponse == null) {
        _setError('启动助手失败');
        return false;
      }
      notifyListeners();
      return true;
    } catch (e) {
      _setError('启动助手异常: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }
  
  // 发送命令
  Future<bool> sendCommand(
    String text, {
    Map<String, dynamic>? context,
    bool shouldSpeak = true,
    bool returnPlan = false,
  }) async {
    _setLoading(true);
    _clearError();
    
    try {
      _lastCommandResponse = await ApiService.sendCommand(
        text,
        context: context,
        shouldSpeak: shouldSpeak,
        returnPlan: returnPlan,
      );
      
      if (_lastCommandResponse == null) {
        _setError('发送命令失败');
        return false;
      }
      
      notifyListeners();
      return true;
    } catch (e) {
      _setError('发送命令异常: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }
  
  // TTS播报
  Future<bool> speak(String text) async {
    _setLoading(true);
    _clearError();
    
    try {
      _lastTTSResponse = await ApiService.speak(text);
      if (_lastTTSResponse == null) {
        _setError('语音播报失败');
        return false;
      }
      notifyListeners();
      return true;
    } catch (e) {
      _setError('语音播报异常: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }
  
  // 远程唤醒
  Future<bool> wakeup({
    String device = 'phone',
    String location = 'living_room',
  }) async {
    _setLoading(true);
    _clearError();
    
    try {
      _lastWakeupResponse = await ApiService.wakeup(
        device: device,
        location: location,
      );
      
      if (_lastWakeupResponse == null) {
        _setError('远程唤醒失败');
        return false;
      }
      
      notifyListeners();
      return true;
    } catch (e) {
      _setError('远程唤醒异常: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }
  
  // 辅助方法
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
  
  void _setError(String error) {
    _lastError = error;
    notifyListeners();
  }
  
  void _clearError() {
    _lastError = null;
  }
}