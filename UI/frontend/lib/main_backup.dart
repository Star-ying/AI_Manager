import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:file_picker/file_picker.dart';
import 'dart:io';
import 'dart:async';
import 'package:path/path.dart' as path;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI音乐管理器',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        cardTheme: CardTheme(
          elevation: 4,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
        cardTheme: CardTheme(
          elevation: 4,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
      themeMode: ThemeMode.system,
      home: const MusicPlayerPage(title: 'AI音乐管理器'),
    );
  }
}

class MusicPlayerPage extends StatefulWidget {
  const MusicPlayerPage({super.key, required this.title});

  final String title;

  @override
  State<MusicPlayerPage> createState() => _MusicPlayerPageState();
}

class _MusicPlayerPageState extends State<MusicPlayerPage>
    with TickerProviderStateMixin {
  // Audio player instance
  final AudioPlayer _audioPlayer = AudioPlayer();

  // Speech recognition instance
  late stt.SpeechToText _speech;
  bool _isListening = false;
  String _recognizedText = '';

  // Music state
  List<File> _musicFiles = [];
  int _currentTrackIndex = 0;
  bool _isPlaying = false;
  double _volume = 0.5;
  Duration _currentPosition = Duration.zero;
  Duration _totalDuration = Duration.zero;
  String? _selectedFolder;

  // Animation controllers
  late AnimationController _playButtonController;
  late AnimationController _voiceButtonController;
  late Animation<double> _playButtonAnimation;
  late Animation<double> _voiceButtonAnimation;

  // Timer for updating position
  Timer? _positionTimer;

  @override
  void initState() {
    super.initState();
    _initializeSpeech();
    _setupAudioPlayer();
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    _positionTimer?.cancel();
    super.dispose();
  }

  void _initializeSpeech() async {
    _speech = stt.SpeechToText();
    await _speech.initialize(
      onError: (error) => print('语音识别错误: $error'),
      onStatus: (status) => print('语音识别状态: $status'),
    );
  }

  void _setupAudioPlayer() {
    _audioPlayer.onDurationChanged.listen((duration) {
      setState(() {
        _totalDuration = duration;
      });
    });

    _audioPlayer.onPositionChanged.listen((position) {
      setState(() {
        _currentPosition = position;
      });
    });

    _audioPlayer.onPlayerStateChanged.listen((state) {
      setState(() {
        _isPlaying = state == PlayerState.playing;
      });
    });

    _audioPlayer.onPlayerComplete.listen((event) {
      _playNext();
    });
  }

  Future<void> _selectMusicFolder() async {
    String? selectedDirectory = await FilePicker.platform.getDirectoryPath();

    if (selectedDirectory != null) {
      setState(() {
        _selectedFolder = selectedDirectory;
      });
      await _loadMusicFiles(selectedDirectory);
    }
  }

  Future<void> _loadMusicFiles(String folderPath) async {
    final directory = Directory(folderPath);
    final List<File> musicFiles = [];

    if (await directory.exists()) {
      await for (var entity in directory.list(recursive: true)) {
        if (entity is File) {
          String ext = path.extension(entity.path).toLowerCase();
          if (['.mp3', '.wav', '.m4a', '.aac', '.ogg'].contains(ext)) {
            musicFiles.add(entity);
          }
        }
      }
    }

    setState(() {
      _musicFiles = musicFiles;
      _currentTrackIndex = 0;
    });

    if (musicFiles.isNotEmpty) {
      _showSnackBar('找到 ${musicFiles.length} 首音乐文件');
    } else {
      _showSnackBar('未找到音乐文件');
    }
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Future<void> _playMusic() async {
    if (_musicFiles.isEmpty) {
      _showSnackBar('请先选择音乐文件夹');
      return;
    }

    if (_currentTrackIndex < _musicFiles.length) {
      await _audioPlayer
          .play(DeviceFileSource(_musicFiles[_currentTrackIndex].path));
      await _audioPlayer.setVolume(_volume);
    }
  }

  Future<void> _pauseMusic() async {
    await _audioPlayer.pause();
  }

  Future<void> _stopMusic() async {
    await _audioPlayer.stop();
  }

  void _playNext() {
    if (_musicFiles.isNotEmpty) {
      setState(() {
        _currentTrackIndex = (_currentTrackIndex + 1) % _musicFiles.length;
      });
      _playMusic();
    }
  }

  void _playPrevious() {
    if (_musicFiles.isNotEmpty) {
      setState(() {
        _currentTrackIndex = _currentTrackIndex > 0
            ? _currentTrackIndex - 1
            : _musicFiles.length - 1;
      });
      _playMusic();
    }
  }

  void _setVolume(double volume) {
    setState(() {
      _volume = volume;
    });
    _audioPlayer.setVolume(volume);
  }

  void _startListening() async {
    if (!_isListening && await _speech.initialize()) {
      setState(() {
        _isListening = true;
        _recognizedText = '';
      });

      _speech.listen(
        onResult: (result) {
          setState(() {
            _recognizedText = result.recognizedWords;
          });

          if (result.finalResult) {
            _processVoiceCommand(_recognizedText);
            _stopListening();
          }
        },
        listenFor: const Duration(seconds: 10),
        pauseFor: const Duration(seconds: 3),
        partialResults: true,
        localeId: 'zh_CN',
      );
    }
  }

  void _stopListening() {
    if (_isListening) {
      _speech.stop();
      setState(() {
        _isListening = false;
      });
    }
  }

  void _processVoiceCommand(String command) {
    String lowerCommand = command.toLowerCase();

    if (lowerCommand.contains('播放') || lowerCommand.contains('开始')) {
      _playMusic();
      _showSnackBar('开始播放音乐');
    } else if (lowerCommand.contains('暂停') || lowerCommand.contains('停止')) {
      _pauseMusic();
      _showSnackBar('暂停播放');
    } else if (lowerCommand.contains('下一首') || lowerCommand.contains('下一个')) {
      _playNext();
      _showSnackBar('播放下一首');
    } else if (lowerCommand.contains('上一首') || lowerCommand.contains('上一个')) {
      _playPrevious();
      _showSnackBar('播放上一首');
    } else if (lowerCommand.contains('音量') && lowerCommand.contains('大')) {
      _setVolume((_volume + 0.2).clamp(0.0, 1.0));
      _showSnackBar('音量增大');
    } else if (lowerCommand.contains('音量') && lowerCommand.contains('小')) {
      _setVolume((_volume - 0.2).clamp(0.0, 1.0));
      _showSnackBar('音量减小');
    } else {
      _showSnackBar('未识别的语音命令: $command');
    }
  }

  String _getCurrentTrackName() {
    if (_musicFiles.isEmpty || _currentTrackIndex >= _musicFiles.length) {
      return '无音乐';
    }
    return path.basenameWithoutExtension(_musicFiles[_currentTrackIndex].path);
  }

  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    String twoDigitMinutes = twoDigits(duration.inMinutes.remainder(60));
    String twoDigitSeconds = twoDigits(duration.inSeconds.remainder(60));
    return "${twoDigits(duration.inHours)}:$twoDigitMinutes:$twoDigitSeconds";
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // 文件夹选择
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Text(
                      '音乐文件夹',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _selectedFolder ?? '未选择文件夹',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 8),
                    ElevatedButton(
                      onPressed: _selectMusicFolder,
                      child: const Text('选择音乐文件夹'),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 20),

            // 当前播放信息
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Text(
                      '正在播放',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _getCurrentTrackName(),
                      style: Theme.of(context).textTheme.headlineSmall,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),

                    // 进度条
                    Column(
                      children: [
                        Slider(
                          value: _currentPosition.inSeconds.toDouble(),
                          max: _totalDuration.inSeconds.toDouble(),
                          onChanged: (value) {
                            _audioPlayer.seek(Duration(seconds: value.toInt()));
                          },
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(_formatDuration(_currentPosition)),
                            Text(_formatDuration(_totalDuration)),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 20),

            // 播放控制按钮
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                IconButton(
                  onPressed: _playPrevious,
                  icon: const Icon(Icons.skip_previous),
                  iconSize: 48,
                ),
                IconButton(
                  onPressed: _isPlaying ? _pauseMusic : _playMusic,
                  icon: Icon(_isPlaying ? Icons.pause : Icons.play_arrow),
                  iconSize: 64,
                ),
                IconButton(
                  onPressed: _playNext,
                  icon: const Icon(Icons.skip_next),
                  iconSize: 48,
                ),
              ],
            ),

            const SizedBox(height: 20),

            // 音量控制
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Text(
                      '音量控制',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    Row(
                      children: [
                        const Icon(Icons.volume_down),
                        Expanded(
                          child: Slider(
                            value: _volume,
                            onChanged: _setVolume,
                            divisions: 20,
                            label: '${(_volume * 100).round()}%',
                          ),
                        ),
                        const Icon(Icons.volume_up),
                      ],
                    ),
                    Text('音量: ${(_volume * 100).round()}%'),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 20),

            // 语音控制
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Text(
                      '语音控制',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _recognizedText.isEmpty ? '点击按钮开始语音识别' : _recognizedText,
                      style: Theme.of(context).textTheme.bodyMedium,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    ElevatedButton.icon(
                      onPressed:
                          _isListening ? _stopListening : _startListening,
                      icon: Icon(_isListening ? Icons.mic_off : Icons.mic),
                      label: Text(_isListening ? '停止录音' : '开始语音识别'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _isListening ? Colors.red : null,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      '支持的语音指令：\n"播放"、"暂停"、"下一首"、"上一首"、"音量大一点"、"音量小一点"',
                      style: TextStyle(fontSize: 12),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
