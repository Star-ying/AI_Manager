import 'dart:async';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:path_provider/path_provider.dart';

// 仅在非Web平台导入permission_handler
import 'package:permission_handler/permission_handler.dart' as ph;

class RecorderService {
  FlutterSoundRecorder? _recorder;
  StreamSubscription? _recorderSubscription;
  bool _isRecording = false;
  bool _isInitialized = false;
  StreamSubscription? _recordingSubscription;
  String? _lastError;
  String? _recordingPath;
  
  // 录音状态流
  final StreamController<bool> _recordingStateController = StreamController<bool>.broadcast();
  Stream<bool> get recordingState => _recordingStateController.stream;
  
  // 音量级别流
  final StreamController<double> _volumeLevelController = StreamController<double>.broadcast();
  Stream<double> get volumeLevel => _volumeLevelController.stream;
  
  // 录音数据流
  final StreamController<Uint8List> _audioDataController = StreamController<Uint8List>.broadcast();
  Stream<Uint8List> get audioData => _audioDataController.stream;

  bool get isRecording => _isRecording;
  bool get isInitialized => _isInitialized;
  String? get lastError => _lastError;
  String? get recordingPath => _recordingPath;

  Future<bool> initialize() async {
    try {
      // 请求麦克风权限
      if (!kIsWeb) {
        final permissionStatus = await ph.Permission.microphone.request();
        if (permissionStatus != ph.PermissionStatus.granted) {
          _lastError = '麦克风权限被拒绝';
          return false;
        }
      }

      // 初始化录音器
      _recorder = FlutterSoundRecorder();
      
      // 打开录音器
      await _recorder!.openRecorder();
      
      // 设置录音参数
      await _recorder!.setSubscriptionDuration(const Duration(milliseconds: 100));
      
      // 获取临时目录路径
      final tempDir = await getTemporaryDirectory();
      _recordingPath = '${tempDir.path}/recording_${DateTime.now().millisecondsSinceEpoch}.wav';

      _isInitialized = true;
      return true;
    } catch (e) {
      _lastError = '初始化录音服务失败: $e';
      return false;
    }
  }

  Future<bool> startRecording() async {
    if (!_isInitialized) {
      final initialized = await initialize();
      if (!initialized) {
        return false;
      }
    }

    try {
      // 开始录音
      await _recorder!.startRecorder(
        toFile: _recordingPath,
        codec: Codec.pcm16WAV,
        sampleRate: 16000,
        numChannels: 1,
      );
      
      _isRecording = true;
      _recordingStateController.add(_isRecording);
      
      // 监听录音数据
      _recorderSubscription = _recorder!.onProgress?.listen((event) {
        _volumeLevelController.add(event.decibels ?? 0.0);
            });
      
      return true;
    } catch (e) {
      _lastError = '开始录音失败: $e';
      return false;
    }
  }

  Future<bool> stopRecording() async {
    if (!_isInitialized || !_isRecording) {
      return false;
    }

    try {
      // 停止录音
      await _recorder!.stopRecorder();
      
      _isRecording = false;
      _recordingStateController.add(_isRecording);
      
      // 取消数据监听
      _recorderSubscription?.cancel();
      
      return true;
    } catch (e) {
      _lastError = '停止录音失败: $e';
      return false;
    }
  }

  Future<bool> pauseRecording() async {
    if (!_isInitialized || !_isRecording) {
      return false;
    }

    try {
      // 暂停录音
      await _recorder!.pauseRecorder();
      return true;
    } catch (e) {
      _lastError = '暂停录音失败: $e';
      return false;
    }
  }

  Future<bool> resumeRecording() async {
    if (!_isInitialized || _isRecording) {
      return false;
    }

    try {
      // 恢复录音
      await _recorder!.resumeRecorder();
      return true;
    } catch (e) {
      _lastError = '恢复录音失败: $e';
      return false;
    }
  }

  Future<String?> saveRecording(String filePath) async {
    if (!_isInitialized) {
      _lastError = '录音服务未初始化';
      return null;
    }

    try {
      // 如果正在录音，先停止录音
      if (_isRecording) {
        await stopRecording();
      }
      
      // 将录音文件复制到指定路径
      final File sourceFile = File(_recordingPath!);
      final File destFile = File(filePath);
      
      if (await sourceFile.exists()) {
        await sourceFile.copy(filePath);
        return filePath;
      } else {
        _lastError = '录音文件不存在';
        return null;
      }
    } catch (e) {
      _lastError = '保存录音失败: $e';
      return null;
    }
  }

  void dispose() {
    _recorderSubscription?.cancel();
    _recordingSubscription?.cancel();
    _recordingStateController.close();
    _volumeLevelController.close();
    _audioDataController.close();
    _recorder?.closeRecorder();
    _isInitialized = false;
    _isRecording = false;
  }

  void clearError() {
    _lastError = null;
  }
}