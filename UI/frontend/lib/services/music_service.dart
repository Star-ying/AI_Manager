import 'dart:io';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:file_picker/file_picker.dart';
import 'package:path_provider/path_provider.dart';

class MusicService extends ChangeNotifier {
  final AudioPlayer _audioPlayer = AudioPlayer();
  final List<File> _musicFiles = [];
  int _currentTrackIndex = 0;
  bool _isPlaying = false;
  bool _isLoading = false;
  Duration _duration = Duration.zero;
  Duration _position = Duration.zero;
  double _volume = 0.7;
  String _currentTrackName = '';
  String _lastError = '';

  // Getters
  List<File> get musicFiles => _musicFiles;
  int get currentTrackIndex => _currentTrackIndex;
  bool get isPlaying => _isPlaying;
  bool get isLoading => _isLoading;
  Duration get duration => _duration;
  Duration get position => _position;
  double get volume => _volume;
  String get currentTrackName => _currentTrackName;
  String get lastError => _lastError;

  // 初始化音乐服务
  Future<void> initialize() async {
    try {
      // 监听播放状态
      _audioPlayer.onPlayerStateChanged.listen((state) {
        _isPlaying = state == PlayerState.playing;
        notifyListeners();
      });

      // 监听播放进度
      _audioPlayer.onPositionChanged.listen((position) {
        _position = position;
        notifyListeners();
      });

      // 监听音频时长
      _audioPlayer.onDurationChanged.listen((duration) {
        _duration = duration;
        notifyListeners();
      });

      // 监听播放完成事件
      _audioPlayer.onPlayerComplete.listen((_) {
        _isPlaying = false;
        _position = Duration.zero;
        notifyListeners();
        // 自动播放下一首
        _playNext();
      });

      // 设置初始音量
      await _audioPlayer.setVolume(_volume);

      // 加载音乐文件
      await loadMusicFiles();
    } catch (e) {
      _lastError = '音乐服务初始化失败: $e';
      notifyListeners();
    }
  }

  // 加载音乐文件
  Future<void> loadMusicFiles() async {
    try {
      _isLoading = true;
      notifyListeners();

      // 获取应用文档目录
      final directory = await getApplicationDocumentsDirectory();
      final musicDir = Directory('${directory.path}/music');

      // 如果目录不存在，创建它
      if (!await musicDir.exists()) {
        await musicDir.create(recursive: true);
        _lastError = '音乐文件夹已创建，请添加音乐文件到 ${musicDir.path}';
        _isLoading = false;
        notifyListeners();
        return;
      }

      // 获取目录中的所有音频文件
      final files = await musicDir.list().toList();
      _musicFiles.clear();

      for (final file in files) {
        if (file is File) {
          final fileName = file.path.toLowerCase();
          if (fileName.endsWith('.mp3') || 
              fileName.endsWith('.wav') || 
              fileName.endsWith('.m4a') || 
              fileName.endsWith('.aac') || 
              fileName.endsWith('.flac')) {
            _musicFiles.add(file);
          }
        }
      }

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _lastError = '加载音乐文件失败: $e';
      _isLoading = false;
      notifyListeners();
    }
  }

  // 选择音乐文件夹
  Future<void> selectMusicFolder() async {
    try {
      _isLoading = true;
      notifyListeners();

      String? selectedDirectory = await FilePicker.platform.getDirectoryPath(
        dialogTitle: '选择音乐文件夹',
      );

      if (selectedDirectory != null) {
        final directory = Directory(selectedDirectory);
        final files = await directory.list().toList();
        _musicFiles.clear();

        for (final file in files) {
          if (file is File) {
            final fileName = file.path.toLowerCase();
            if (fileName.endsWith('.mp3') || 
                fileName.endsWith('.wav') || 
                fileName.endsWith('.m4a') || 
                fileName.endsWith('.aac') || 
                fileName.endsWith('.flac')) {
              _musicFiles.add(file);
            }
          }
        }

        // 复制文件到应用目录
        final appDir = await getApplicationDocumentsDirectory();
        final musicDir = Directory('${appDir.path}/music');
        
        if (!await musicDir.exists()) {
          await musicDir.create(recursive: true);
        }

        for (final file in _musicFiles) {
          final fileName = file.path.split('/').last;
          final newPath = '${musicDir.path}/$fileName';
          await file.copy(newPath);
        }

        _lastError = '音乐文件已复制到应用目录';
      }

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _lastError = '选择音乐文件夹失败: $e';
      _isLoading = false;
      notifyListeners();
    }
  }

  // 播放指定索引的音乐
  Future<void> playTrack(int index) async {
    if (index < 0 || index >= _musicFiles.length) {
      _lastError = '无效的音乐索引';
      notifyListeners();
      return;
    }

    try {
      _currentTrackIndex = index;
      _currentTrackName = _musicFiles[index].path.split('/').last;
      notifyListeners();

      await _audioPlayer.play(DeviceFileSource(_musicFiles[index].path));
    } catch (e) {
      _lastError = '播放音乐失败: $e';
      notifyListeners();
    }
  }

  // 播放/暂停
  Future<void> togglePlayPause() async {
    try {
      if (_isPlaying) {
        await _audioPlayer.pause();
      } else {
        if (_musicFiles.isEmpty) {
          _lastError = '没有可播放的音乐文件';
          notifyListeners();
          return;
        }
        
        if (_position.inMilliseconds == 0) {
          await playTrack(_currentTrackIndex);
        } else {
          await _audioPlayer.resume();
        }
      }
    } catch (e) {
      _lastError = '播放/暂停失败: $e';
      notifyListeners();
    }
  }

  // 播放下一首
  Future<void> playNext() async {
    if (_musicFiles.isEmpty) {
      _lastError = '没有可播放的音乐文件';
      notifyListeners();
      return;
    }

    int nextIndex = (_currentTrackIndex + 1) % _musicFiles.length;
    await playTrack(nextIndex);
  }

  // 播放上一首
  Future<void> playPrevious() async {
    if (_musicFiles.isEmpty) {
      _lastError = '没有可播放的音乐文件';
      notifyListeners();
      return;
    }

    int prevIndex = (_currentTrackIndex - 1 + _musicFiles.length) % _musicFiles.length;
    await playTrack(prevIndex);
  }

  // 内部方法：播放下一首
  Future<void> _playNext() async {
    if (_musicFiles.isNotEmpty) {
      int nextIndex = (_currentTrackIndex + 1) % _musicFiles.length;
      await playTrack(nextIndex);
    }
  }

  // 设置音量
  Future<void> setVolume(double volume) async {
    if (volume < 0) volume = 0;
    if (volume > 1) volume = 1;
    
    _volume = volume;
    notifyListeners();

    try {
      await _audioPlayer.setVolume(volume);
    } catch (e) {
      _lastError = '设置音量失败: $e';
      notifyListeners();
    }
  }

  // 调整音量
  Future<void> adjustVolume(double delta) async {
    double newVolume = _volume + delta;
    await setVolume(newVolume);
  }

  // 跳转到指定位置
  Future<void> seekTo(Duration position) async {
    try {
      await _audioPlayer.seek(position);
    } catch (e) {
      _lastError = '跳转失败: $e';
      notifyListeners();
    }
  }

  // 停止播放
  Future<void> stop() async {
    try {
      await _audioPlayer.stop();
      _isPlaying = false;
      _position = Duration.zero;
      notifyListeners();
    } catch (e) {
      _lastError = '停止播放失败: $e';
      notifyListeners();
    }
  }

  // 处理语音指令
  Future<String> processVoiceCommand(String command) async {
    try {
      final lowerCommand = command.toLowerCase();
      
      // 播放音乐
      if (lowerCommand.contains('播放') || lowerCommand.contains('play')) {
        if (_musicFiles.isEmpty) {
          return '没有可播放的音乐文件';
        }
        
        // 查找指定歌曲
        for (int i = 0; i < _musicFiles.length; i++) {
          final fileName = _musicFiles[i].path.toLowerCase();
          if (lowerCommand.contains(fileName.split('.').first)) {
            await playTrack(i);
            return '正在播放: ${_musicFiles[i].path.split('/').last}';
          }
        }
        
        // 如果没有指定歌曲，播放当前歌曲
        await togglePlayPause();
        return _isPlaying ? '正在播放音乐' : '音乐已暂停';
      }
      
      // 暂停音乐
      if (lowerCommand.contains('暂停') || lowerCommand.contains('pause')) {
        if (_isPlaying) {
          await togglePlayPause();
          return '音乐已暂停';
        } else {
          return '音乐已经是暂停状态';
        }
      }
      
      // 下一首
      if (lowerCommand.contains('下一首') || lowerCommand.contains('next')) {
        await playNext();
        return '正在播放下一首: $_currentTrackName';
      }
      
      // 上一首
      if (lowerCommand.contains('上一首') || lowerCommand.contains('previous')) {
        await playPrevious();
        return '正在播放上一首: $_currentTrackName';
      }
      
      // 增加音量
      if (lowerCommand.contains('音量') && (lowerCommand.contains('增加') || lowerCommand.contains('大') || lowerCommand.contains('高'))) {
        await adjustVolume(0.1);
        return '音量已增加到: ${(_volume * 100).round()}%';
      }
      
      // 减小音量
      if (lowerCommand.contains('音量') && (lowerCommand.contains('减少') || lowerCommand.contains('小') || lowerCommand.contains('低'))) {
        await adjustVolume(-0.1);
        return '音量已减小到: ${(_volume * 100).round()}%';
      }
      
      // 设置音量
      if (lowerCommand.contains('音量')) {
        final regex = RegExp(r'(\d+)');
        final match = regex.firstMatch(command);
        if (match != null) {
          final volumeValue = int.tryParse(match.group(1) ?? '') ?? 50;
          await setVolume(volumeValue / 100.0);
          return '音量已设置为: $volumeValue%';
        }
      }
      
      return '无法识别的音乐指令: $command';
    } catch (e) {
      _lastError = '处理语音指令失败: $e';
      notifyListeners();
      return '处理语音指令失败: $e';
    }
  }

  // 释放资源
  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }
}