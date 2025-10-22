import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:io';
import 'package:path/path.dart' as path;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI音乐管理器 - 测试版',
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
      ),
      themeMode: ThemeMode.system,
      home: const MusicPlayerPage(title: 'AI音乐管理器 - 测试版'),
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
  
  // Music state
  List<File> _musicFiles = [];
  int _currentTrackIndex = 0;
  bool _isPlaying = false;
  double _volume = 0.5;
  String? _selectedFolder;
  String _recognizedText = '';
  bool _isListening = false;

  // Animation controllers
  late AnimationController _playButtonController;
  late AnimationController _voiceButtonController;
  late Animation<double> _playButtonAnimation;
  late Animation<double> _voiceButtonAnimation;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
  }

  void _initializeAnimations() {
    _playButtonController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    _voiceButtonController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _playButtonAnimation = Tween<double>(
      begin: 1.0,
      end: 1.1,
    ).animate(CurvedAnimation(
      parent: _playButtonController,
      curve: Curves.elasticOut,
    ));

    _voiceButtonAnimation = Tween<double>(
      begin: 1.0,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _voiceButtonController,
      curve: Curves.elasticInOut,
    ));
  }

  @override
  void dispose() {
    _playButtonController.dispose();
    _voiceButtonController.dispose();
    super.dispose();
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
      _showSnackBar('找到 ${musicFiles.length} 首音乐文件', Colors.green);
    } else {
      _showSnackBar('未找到音乐文件', Colors.orange);
    }
  }

  void _showSnackBar(String message, [Color? backgroundColor]) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: backgroundColor,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  void _playMusic() {
    setState(() {
      _isPlaying = true;
    });
    _playButtonController.forward();
    _showSnackBar('🎵 模拟播放音乐', Colors.blue);
  }

  void _pauseMusic() {
    setState(() {
      _isPlaying = false;
    });
    _playButtonController.reverse();
    _showSnackBar('⏸️ 模拟暂停播放', Colors.orange);
  }

  void _playNext() {
    if (_musicFiles.isNotEmpty) {
      setState(() {
        _currentTrackIndex = (_currentTrackIndex + 1) % _musicFiles.length;
      });
      _showSnackBar('⏭️ 播放下一首', Colors.green);
    }
  }

  void _playPrevious() {
    if (_musicFiles.isNotEmpty) {
      setState(() {
        _currentTrackIndex = _currentTrackIndex > 0
            ? _currentTrackIndex - 1
            : _musicFiles.length - 1;
      });
      _showSnackBar('⏮️ 播放上一首', Colors.green);
    }
  }

  void _setVolume(double volume) {
    setState(() {
      _volume = volume;
    });
    _showSnackBar('🔊 音量设置为 ${(volume * 100).round()}%', Colors.purple);
  }

  void _startListening() {
    setState(() {
      _isListening = true;
      _recognizedText = '模拟语音识别中...';
    });
    _voiceButtonController.repeat(reverse: true);
    
    // 模拟语音识别过程
    Future.delayed(const Duration(seconds: 3), () {
      if (_isListening) {
        setState(() {
          _recognizedText = '播放音乐';
        });
        _processVoiceCommand('播放音乐');
        _stopListening();
      }
    });
  }

  void _stopListening() {
    setState(() {
      _isListening = false;
    });
    _voiceButtonController.stop();
    _voiceButtonController.reset();
  }

  void _processVoiceCommand(String command) {
    String lowerCommand = command.toLowerCase();

    if (lowerCommand.contains('播放') || lowerCommand.contains('开始')) {
      _playMusic();
    } else if (lowerCommand.contains('暂停') || lowerCommand.contains('停止')) {
      _pauseMusic();
    } else if (lowerCommand.contains('下一首') || lowerCommand.contains('下一个')) {
      _playNext();
    } else if (lowerCommand.contains('上一首') || lowerCommand.contains('上一个')) {
      _playPrevious();
    } else if (lowerCommand.contains('音量') && lowerCommand.contains('大')) {
      _setVolume((_volume + 0.2).clamp(0.0, 1.0));
    } else if (lowerCommand.contains('音量') && lowerCommand.contains('小')) {
      _setVolume((_volume - 0.2).clamp(0.0, 1.0));
    } else {
      _showSnackBar('❓ 未识别的语音命令: $command', Colors.grey);
    }
  }

  String _getCurrentTrackName() {
    if (_musicFiles.isEmpty || _currentTrackIndex >= _musicFiles.length) {
      return '暂无音乐';
    }
    return path.basenameWithoutExtension(_musicFiles[_currentTrackIndex].path);
  }

  Widget _buildFolderSection() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            Row(
              children: [
                Icon(
                  Icons.folder,
                  color: Theme.of(context).colorScheme.primary,
                  size: 24,
                ),
                const SizedBox(width: 12),
                Text(
                  '音乐文件夹',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Theme.of(context)
                    .colorScheme
                    .surfaceVariant
                    .withOpacity(0.3),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
                ),
              ),
              child: Text(
                _selectedFolder ?? '尚未选择文件夹',
                style: Theme.of(context).textTheme.bodyMedium,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _selectMusicFolder,
                icon: const Icon(Icons.folder_open),
                label: const Text('选择音乐文件夹'),
              ),
            ),
            if (_musicFiles.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                '已找到 ${_musicFiles.length} 首音乐',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.primary,
                    ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildPlayerSection() {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            // 专辑封面占位符
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Theme.of(context).colorScheme.primary.withOpacity(0.8),
                    Theme.of(context).colorScheme.secondary.withOpacity(0.6),
                  ],
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color:
                        Theme.of(context).colorScheme.primary.withOpacity(0.3),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Icon(
                _isPlaying ? Icons.music_note : Icons.music_off,
                size: 60,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 20),

            // 歌曲标题
            Text(
              _getCurrentTrackName(),
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 8),

            // 播放状态
            Text(
              _isPlaying ? '正在播放 (模拟)' : '已暂停',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: 24),

            // 模拟进度条
            Column(
              children: [
                SliderTheme(
                  data: SliderTheme.of(context).copyWith(
                    trackHeight: 4,
                    thumbShape:
                        const RoundSliderThumbShape(enabledThumbRadius: 8),
                    overlayShape:
                        const RoundSliderOverlayShape(overlayRadius: 16),
                  ),
                  child: Slider(
                    value: 0.3,
                    max: 1.0,
                    onChanged: (value) {
                      // 模拟进度条
                    },
                  ),
                ),
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('01:23'),
                      Text('04:56'),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildControlButtons() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            IconButton(
              onPressed: _musicFiles.isEmpty ? null : _playPrevious,
              icon: const Icon(Icons.skip_previous),
              iconSize: 40,
              style: IconButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.surfaceVariant,
                foregroundColor: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
            ScaleTransition(
              scale: _playButtonAnimation,
              child: Container(
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Theme.of(context).colorScheme.primary,
                      Theme.of(context).colorScheme.primary.withOpacity(0.8),
                    ],
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Theme.of(context)
                          .colorScheme
                          .primary
                          .withOpacity(0.4),
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: IconButton(
                  onPressed: _isPlaying ? _pauseMusic : _playMusic,
                  icon: Icon(_isPlaying ? Icons.pause : Icons.play_arrow),
                  iconSize: 48,
                  color: Colors.white,
                ),
              ),
            ),
            IconButton(
              onPressed: _musicFiles.isEmpty ? null : _playNext,
              icon: const Icon(Icons.skip_next),
              iconSize: 40,
              style: IconButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.surfaceVariant,
                foregroundColor: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVolumeSection() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            Row(
              children: [
                Icon(
                  Icons.volume_up,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 12),
                Text(
                  '音量控制',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                ),
                const Spacer(),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${(_volume * 100).round()}%',
                    style: Theme.of(context).textTheme.labelMedium?.copyWith(
                          color:
                              Theme.of(context).colorScheme.onPrimaryContainer,
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Icon(
                  Icons.volume_mute,
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
                Expanded(
                  child: SliderTheme(
                    data: SliderTheme.of(context).copyWith(
                      trackHeight: 6,
                      thumbShape:
                          const RoundSliderThumbShape(enabledThumbRadius: 10),
                      overlayShape:
                          const RoundSliderOverlayShape(overlayRadius: 18),
                    ),
                    child: Slider(
                      value: _volume,
                      onChanged: _setVolume,
                      divisions: 20,
                    ),
                  ),
                ),
                Icon(
                  Icons.volume_up,
                  color: Theme.of(context).colorScheme.primary,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVoiceSection() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            Row(
              children: [
                Icon(
                  Icons.mic,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 12),
                Text(
                  '语音控制 (模拟)',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // 语音识别状态显示
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: _isListening
                    ? Theme.of(context)
                        .colorScheme
                        .primaryContainer
                        .withOpacity(0.3)
                    : Theme.of(context)
                        .colorScheme
                        .surfaceVariant
                        .withOpacity(0.3),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: _isListening
                      ? Theme.of(context).colorScheme.primary.withOpacity(0.5)
                      : Theme.of(context).colorScheme.outline.withOpacity(0.3),
                  width: 2,
                ),
              ),
              child: Column(
                children: [
                  Text(
                    _isListening ? '🎤 正在听取语音...' : '💬 点击开始语音识别 (模拟)',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w500,
                        ),
                    textAlign: TextAlign.center,
                  ),
                  if (_recognizedText.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      '"$_recognizedText"',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            fontStyle: FontStyle.italic,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 16),

            // 语音控制按钮
            ScaleTransition(
              scale: _voiceButtonAnimation,
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _isListening ? _stopListening : _startListening,
                  icon: Icon(_isListening ? Icons.mic_off : Icons.mic),
                  label: Text(_isListening ? '停止录音' : '开始语音识别 (模拟)'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _isListening
                        ? Theme.of(context).colorScheme.error
                        : Theme.of(context).colorScheme.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 支持的指令
            ExpansionTile(
              title: Text(
                '支持的语音指令',
                style: Theme.of(context).textTheme.labelLarge,
              ),
              children: [
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _buildVoiceCommandChip('播放'),
                    _buildVoiceCommandChip('暂停'),
                    _buildVoiceCommandChip('下一首'),
                    _buildVoiceCommandChip('上一首'),
                    _buildVoiceCommandChip('音量大一点'),
                    _buildVoiceCommandChip('音量小一点'),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVoiceCommandChip(String command) {
    return Chip(
      label: Text(command),
      backgroundColor: Theme.of(context).colorScheme.secondaryContainer,
      labelStyle: TextStyle(
        color: Theme.of(context).colorScheme.onSecondaryContainer,
        fontSize: 12,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.transparent,
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Theme.of(context).colorScheme.primary,
                Theme.of(context).colorScheme.primary.withOpacity(0.8),
              ],
            ),
          ),
        ),
        title: Text(
          widget.title,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.info, color: Colors.white),
            onPressed: () {
              _showSnackBar('这是测试版本，音频播放和语音识别功能为模拟实现', Colors.blue);
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              _buildFolderSection(),
              const SizedBox(height: 16),
              _buildPlayerSection(),
              const SizedBox(height: 16),
              _buildControlButtons(),
              const SizedBox(height: 16),
              _buildVolumeSection(),
              const SizedBox(height: 16),
              _buildVoiceSection(),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }
}