import 'package:flutter/material.dart';
import 'package:ai_assistant/services/voice_service.dart';
import 'package:ai_assistant/services/music_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI小助手',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const AIAssistantHomePage(),
    );
  }
}

class AIAssistantHomePage extends StatefulWidget {
  const AIAssistantHomePage({super.key});

  @override
  State<AIAssistantHomePage> createState() => _AIAssistantHomePageState();
}

class _AIAssistantHomePageState extends State<AIAssistantHomePage> {
  late VoiceService _voiceService;
  late MusicService _musicService;
  bool _isInitialized = false;
  String _statusMessage = '正在初始化...';

  @override
  void initState() {
    super.initState();
    _initializeServices();
  }

  Future<void> _initializeServices() async {
    try {
      _voiceService = VoiceService();
      _musicService = MusicService();
      
      await _voiceService.initialize();
      
      setState(() {
        _isInitialized = true;
        _statusMessage = '初始化完成';
      });
    } catch (e) {
      setState(() {
        _statusMessage = '初始化失败: $e';
      });
    }
  }

  @override
  void dispose() {
    _musicService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('AI小助手'),
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(),
              const SizedBox(height: 20),
              Text(_statusMessage),
            ],
          ),
        ),
      );
    }

    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('AI小助手'),
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          bottom: const TabBar(
            tabs: [
              Tab(icon: Icon(Icons.mic), text: '语音控制'),
              Tab(icon: Icon(Icons.music_note), text: '音乐播放'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            VoiceControlTab(voiceService: _voiceService),
            MusicPlayerTab(musicService: _musicService),
          ],
        ),
      ),
    );
  }
}

class VoiceControlTab extends StatefulWidget {
  final VoiceService voiceService;

  const VoiceControlTab({super.key, required this.voiceService});

  @override
  State<VoiceControlTab> createState() => _VoiceControlTabState();
}

class _VoiceControlTabState extends State<VoiceControlTab> {
  bool _isListening = false;
  String _recognizedText = '';

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text(
            '语音控制',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[200],
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              _recognizedText.isEmpty ? '等待语音输入...' : _recognizedText,
              style: const TextStyle(fontSize: 18),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 30),
          FloatingActionButton(
            onPressed: _toggleListening,
            backgroundColor: _isListening ? Colors.red : Colors.green,
            child: Icon(_isListening ? Icons.mic_off : Icons.mic),
          ),
          const SizedBox(height: 20),
          Text(
            _isListening ? '正在听取语音...' : '点击按钮开始语音输入',
            style: TextStyle(fontSize: 16, color: Colors.grey[600]),
          ),
          const SizedBox(height: 30),
          const Text(
            '语音指令示例:',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          const Text('• "播放音乐" - 播放当前音乐'),
          const Text('• "暂停音乐" - 暂停当前音乐'),
          const Text('• "下一首" - 播放下一首音乐'),
          const Text('• "上一首" - 播放上一首音乐'),
          const Text('• "音量增加" - 增加音量'),
          const Text('• "音量减少" - 减少音量'),
        ],
      ),
    );
  }

  void _toggleListening() {
    if (_isListening) {
      widget.voiceService.stopListening();
      setState(() {
        _isListening = false;
      });
    } else {
      widget.voiceService.startListening().then((_) {
        setState(() {
          _isListening = true;
          _recognizedText = '';
        });
      });

      // 监听语音识别结果
      widget.voiceService.startListening();
      _listenForResults();
    }
  }

  void _listenForResults() {
    if (mounted) {
      setState(() {
        _recognizedText = widget.voiceService.text;
      });

      if (widget.voiceService.isListening) {
        Future.delayed(const Duration(milliseconds: 100), _listenForResults);
      }
    }
  }
}

class MusicPlayerTab extends StatefulWidget {
  final MusicService musicService;

  const MusicPlayerTab({super.key, required this.musicService});

  @override
  State<MusicPlayerTab> createState() => _MusicPlayerTabState();
}

class _MusicPlayerTabState extends State<MusicPlayerTab> {
  double _volume = 0.5;
  bool _isPlaying = false;
  List<String> _musicFiles = [];
  int _currentMusicIndex = 0;

  @override
  void initState() {
    super.initState();
    _updateMusicStatus();
  }

  void _updateMusicStatus() {
    if (mounted) {
      setState(() {
        _volume = widget.musicService.volume;
        _isPlaying = widget.musicService.isPlaying;
        _musicFiles = List.generate(widget.musicService.musicCount, (index) => 
          widget.musicService.getMusicFileName(index));
        _currentMusicIndex = widget.musicService.currentMusicIndex;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          const Text(
            '音乐播放器',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),
          ElevatedButton.icon(
            onPressed: () async {
              await widget.musicService.pickMusicFolder();
              _updateMusicStatus();
            },
            icon: const Icon(Icons.folder_open),
            label: const Text('选择音乐文件夹'),
          ),
          const SizedBox(height: 20),
          if (_musicFiles.isNotEmpty) ...[
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(10),
              ),
              child: Column(
                children: [
                  Text(
                    '当前播放: ${_musicFiles[_currentMusicIndex]}',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    '${_currentMusicIndex + 1} / ${_musicFiles.length}',
                    style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(
                  onPressed: () async {
                    await widget.musicService.playPrevious();
                    _updateMusicStatus();
                  },
                  icon: const Icon(Icons.skip_previous),
                  iconSize: 40,
                ),
                IconButton(
                  onPressed: () async {
                    if (_isPlaying) {
                      await widget.musicService.pause();
                    } else {
                      await widget.musicService.play();
                    }
                    _updateMusicStatus();
                  },
                  icon: Icon(_isPlaying ? Icons.pause : Icons.play_arrow),
                  iconSize: 50,
                ),
                IconButton(
                  onPressed: () async {
                    await widget.musicService.playNext();
                    _updateMusicStatus();
                  },
                  icon: const Icon(Icons.skip_next),
                  iconSize: 40,
                ),
              ],
            ),
            const SizedBox(height: 30),
            Row(
              children: [
                const Icon(Icons.volume_down),
                Expanded(
                  child: Slider(
                    value: _volume,
                    onChanged: (value) async {
                      await widget.musicService.setVolume(value);
                      _updateMusicStatus();
                    },
                    min: 0.0,
                    max: 1.0,
                    divisions: 10,
                    label: '${(_volume * 100).round()}%',
                  ),
                ),
                const Icon(Icons.volume_up),
              ],
            ),
            Text(
              '音量: ${(_volume * 100).round()}%',
              style: TextStyle(fontSize: 16, color: Colors.grey[600]),
            ),
            const SizedBox(height: 20),
            const Text(
              '音乐列表:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: ListView.builder(
                itemCount: _musicFiles.length,
                itemBuilder: (context, index) {
                  return ListTile(
                    title: Text(_musicFiles[index]),
                    onTap: () async {
                      await widget.musicService.playMusicByIndex(index);
                      _updateMusicStatus();
                    },
                    selected: index == _currentMusicIndex,
                    selectedTileColor: Colors.deepPurple[100],
                  );
                },
              ),
            ),
          ] else ...[
            const SizedBox(height: 50),
            const Text(
              '请选择包含音乐文件的文件夹',
              style: TextStyle(fontSize: 16, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
          ],
        ],
      ),
    );
  }
}
