// API响应模型类

// 健康检查响应
class HealthResponse {
  final String status;
  final int? timestamp;
  final String? version;
  
  HealthResponse({
    required this.status,
    this.timestamp,
    this.version,
  });
  
  factory HealthResponse.fromJson(Map<String, dynamic> json) {
    return HealthResponse(
      status: json['status'] ?? '',
      timestamp: json['timestamp'] is int ? json['timestamp'] : int.tryParse(json['timestamp']?.toString() ?? '') ?? 0,
      version: json['version'],
    );
  }
}

// 状态查询响应
class StatusResponse {
  final String status;
  final int? timestamp;
  final bool? isListening;
  final bool? isProcessing;
  final bool? isSpeaking;
  final String? lastCommand;
  final String? lastResponse;
  final String? deviceStatus;
  final String? batteryLevel;
  final String? networkStatus;
  final String? lastError;
  final Map<String, dynamic>? assistantState;
  
  StatusResponse({
    required this.status,
    this.timestamp,
    this.isListening,
    this.isProcessing,
    this.isSpeaking,
    this.lastCommand,
    this.lastResponse,
    this.deviceStatus,
    this.batteryLevel,
    this.networkStatus,
    this.lastError,
    this.assistantState,
  });
  
  factory StatusResponse.fromJson(Map<String, dynamic> json) {
    return StatusResponse(
      status: json['status'] ?? '',
      timestamp: json['timestamp'] is int ? json['timestamp'] : int.tryParse(json['timestamp']?.toString() ?? '') ?? 0,
      isListening: json['is_listening'],
      isProcessing: json['is_processing'],
      isSpeaking: json['is_speaking'],
      lastCommand: json['last_command'],
      lastResponse: json['last_response'],
      deviceStatus: json['device_status'],
      batteryLevel: json['battery_level'],
      networkStatus: json['network_status'],
      lastError: json['last_error'],
      assistantState: json['assistant_state'],
    );
  }
}

// 启动助手响应
class StartResponse {
  final String status;
  final String? message;
  final int? timestamp;
  final Map<String, dynamic>? config;
  
  StartResponse({
    required this.status,
    this.message,
    this.timestamp,
    this.config,
  });
  
  factory StartResponse.fromJson(Map<String, dynamic> json) {
    return StartResponse(
      status: json['status'] ?? '',
      message: json['message'],
      timestamp: json['timestamp'] is int ? json['timestamp'] : int.tryParse(json['timestamp']?.toString() ?? '') ?? 0,
      config: json['config'],
    );
  }
}

// 执行命令响应
class CommandResponse {
  final bool success;
  final String? responseToUser;
  final String? operation;
  final Map<String, dynamic>? details;
  final bool? shouldSpeak;
  final int? timestamp;
  final String? error;
  
  CommandResponse({
    required this.success,
    this.responseToUser,
    this.operation,
    this.details,
    this.shouldSpeak,
    this.timestamp,
    this.error,
  });
  
  factory CommandResponse.fromJson(Map<String, dynamic> json) {
    return CommandResponse(
      success: json['success'] ?? false,
      responseToUser: json['response_to_user'],
      operation: json['operation'],
      details: json['details'],
      shouldSpeak: json['should_speak'],
      timestamp: json['timestamp'] is int ? json['timestamp'] : int.tryParse(json['timestamp']?.toString() ?? '') ?? 0,
      error: json['error'],
    );
  }
}

// TTS播报响应
class TTSResponse {
  final String status;
  final String? text;
  final int? timestamp;
  final String? audioFile;
  final int? duration;
  final String? error;
  
  TTSResponse({
    required this.status,
    this.text,
    this.timestamp,
    this.audioFile,
    this.duration,
    this.error,
  });
  
  factory TTSResponse.fromJson(Map<String, dynamic> json) {
    return TTSResponse(
      status: json['status'] ?? '',
      text: json['text'],
      timestamp: json['timestamp'] is int ? json['timestamp'] : int.tryParse(json['timestamp']?.toString() ?? '') ?? 0,
      audioFile: json['audio_file'],
      duration: json['duration'],
      error: json['error'],
    );
  }
}

// 远程唤醒响应
class WakeupResponse {
  final String status;
  final String? message;
  final int? timestamp;
  final String? device;
  final String? location;
  final String? wakeTime;
  final String? error;
  
  WakeupResponse({
    required this.status,
    this.message,
    this.timestamp,
    this.device,
    this.location,
    this.wakeTime,
    this.error,
  });
  
  factory WakeupResponse.fromJson(Map<String, dynamic> json) {
    return WakeupResponse(
      status: json['status'] ?? '',
      message: json['message'],
      timestamp: json['timestamp'] is int ? json['timestamp'] : int.tryParse(json['timestamp']?.toString() ?? '') ?? 0,
      device: json['device'],
      location: json['location'],
      wakeTime: json['wake_time'],
      error: json['error'],
    );
  }
}