import 'dart:async';
import 'dart:io';
import 'package:audioplayers/audioplayers.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter_volume_controller/flutter_volume_controller.dart';

class MusicService {
  AudioPlayer? _audioPlayer;
  AudioPlayer? _bgmPlayer; // 背景音乐播放器
  List<String> _musicFiles = [];
  int _currentMusicIndex = 0;
  bool _isPlaying = false;
  double _volume = 0.5;
  String _musicFolderPath = '';

  MusicService() {
    _audioPlayer = AudioPlayer();
    _bgmPlayer = AudioPlayer();
    
    // 监听播放完成事件
    _audioPlayer?.onPlayerComplete.listen((_) {
      _playNextMusic();
    });
    
    // 初始化音量
    _initVolume();
  }

  bool get isPlaying => _isPlaying;
  double get volume => _volume;
  String get currentMusic => _musicFiles.isNotEmpty ? _musicFiles[_currentMusicIndex] : '';
  int get currentMusicIndex => _currentMusicIndex;
  int get musicCount => _musicFiles.length;

  Future<void> _initVolume() async {
    _volume = await FlutterVolumeController.getVolume() ?? 0.5;
    await _audioPlayer?.setVolume(_volume);
    await _bgmPlayer?.setVolume(_volume);
  }

  Future<void> setMusicFolder(String path) async {
    _musicFolderPath = path;
    await _loadMusicFiles();
  }

  Future<void> _loadMusicFiles() async {
    if (_musicFolderPath.isEmpty) return;
    
    try {
      final directory = Directory(_musicFolderPath);
      if (await directory.exists()) {
        List<String> musicFiles = [];
        final files = await directory.list().where((entity) => entity is File).cast<File>().toList();
        
        for (var file in files) {
          final path = file.path.toLowerCase();
          if (path.endsWith('.mp3') || 
              path.endsWith('.wav') || 
              path.endsWith('.ogg') || 
              path.endsWith('.aac') || 
              path.endsWith('.flac')) {
            musicFiles.add(file.path);
          }
        }
        
        _musicFiles = musicFiles;
        _currentMusicIndex = 0;
      }
    } catch (e) {
      print('加载音乐文件时出错: $e');
    }
  }

  Future<void> play() async {
    if (_musicFiles.isEmpty) {
      print('没有可播放的音乐文件');
      return;
    }
    
    try {
      await _audioPlayer?.play(UrlSource(_musicFiles[_currentMusicIndex]));
      _isPlaying = true;
    } catch (e) {
      print('播放音乐时出错: $e');
    }
  }

  Future<void> pause() async {
    try {
      await _audioPlayer?.pause();
      _isPlaying = false;
    } catch (e) {
      print('暂停音乐时出错: $e');
    }
  }

  Future<void> resume() async {
    try {
      await _audioPlayer?.resume();
      _isPlaying = true;
    } catch (e) {
      print('恢复播放音乐时出错: $e');
    }
  }

  Future<void> stop() async {
    try {
      await _audioPlayer?.stop();
      _isPlaying = false;
    } catch (e) {
      print('停止播放音乐时出错: $e');
    }
  }

  Future<void> playNext() async {
    if (_musicFiles.isEmpty) return;
    
    _currentMusicIndex = (_currentMusicIndex + 1) % _musicFiles.length;
    if (_isPlaying) {
      await play();
    }
  }

  Future<void> playPrevious() async {
    if (_musicFiles.isEmpty) return;
    
    _currentMusicIndex = (_currentMusicIndex - 1 + _musicFiles.length) % _musicFiles.length;
    if (_isPlaying) {
      await play();
    }
  }

  void _playNextMusic() {
    if (_musicFiles.isEmpty) return;
    
    _currentMusicIndex = (_currentMusicIndex + 1) % _musicFiles.length;
    play();
  }

  Future<void> playMusicByIndex(int index) async {
    if (index < 0 || index >= _musicFiles.length) return;
    
    _currentMusicIndex = index;
    if (_isPlaying) {
      await play();
    }
  }

  Future<void> setVolume(double volume) async {
    _volume = volume.clamp(0.0, 1.0);
    try {
      await FlutterVolumeController.setVolume(_volume);
      await _audioPlayer?.setVolume(_volume);
      await _bgmPlayer?.setVolume(_volume);
    } catch (e) {
      print('设置音量时出错: $e');
    }
  }

  Future<void> pickMusicFolder() async {
    try {
      String? directoryPath = await FilePicker.platform.getDirectoryPath();
      if (directoryPath != null) {
        _musicFolderPath = directoryPath;
        await _loadMusicFiles();
      }
    } catch (e) {
      print('选择音乐文件夹时出错: $e');
    }
  }

  String getMusicFileName(int index) {
    if (index < 0 || index >= _musicFiles.length) return '';
    return _musicFiles[index].split(Platform.pathSeparator).last;
  }

  Future<void> playBgm(String filePath) async {
    try {
      await _bgmPlayer?.play(UrlSource(filePath));
    } catch (e) {
      print('播放背景音乐时出错: $e');
    }
  }

  Future<void> stopBgm() async {
    try {
      await _bgmPlayer?.stop();
    } catch (e) {
      print('停止背景音乐时出错: $e');
    }
  }

  void dispose() {
    _audioPlayer?.dispose();
    _bgmPlayer?.dispose();
  }
}