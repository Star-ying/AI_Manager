import 'dart:async';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:speech_to_text/speech_to_text.dart';

import 'services/voice_service.dart';
import 'services/music_service.dart';
import 'providers/api_provider.dart';
import 'config/app_config.dart';

void main() => runApp(const AIAssistantApp());

class AIAssistantApp extends StatelessWidget {
  const AIAssistantApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => VoiceService()),
        ChangeNotifierProvider(create: (_) => MusicService()),
        ChangeNotifierProvider(create: (_) => ApiProvider()),
      ],
      child: MaterialApp(
        title: 'AI小助手',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.deepPurple,
            brightness: Brightness.dark,
          ),
          useMaterial3: true,
          appBarTheme: const AppBarTheme(
            centerTitle: true,
            elevation: 0,
            backgroundColor: Colors.transparent,
          ),
        ),
        home: const MainScreen(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> with TickerProviderStateMixin {
  late TabController _tabController;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);

    // 初始化动画控制器
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );

    _scaleAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.elasticOut),
    );

    // 启动动画
    _animationController.forward();

    // 初始化服务
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeServices();
    });
  }

  Future<void> _initializeServices() async {
    // 初始化语音服务
    final voiceService = Provider.of<VoiceService>(context, listen: false);
    await voiceService.initialize();

    // 初始化音乐服务
    final musicService = Provider.of<MusicService>(context, listen: false);
    await musicService.initialize();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      // appBar: AppBar(
      //   title: AnimatedBuilder(
      //     animation: _fadeAnimation,
      //     builder: (context, child) {
      //       return FadeTransition(
      //         opacity: _fadeAnimation,
      //         child: ScaleTransition(
      //           scale: _scaleAnimation,
      //           child: const Text(
      //             'AI小助手',
      //             style: TextStyle(
      //               fontWeight: FontWeight.bold,
      //               fontSize: 24,
      //             ),
      //           ),
      //         ),
      //       );
      //     },
      //   ),
      //   backgroundColor: Colors.transparent,
      //   elevation: 0,
      // ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Theme.of(context).colorScheme.primary.withOpacity(0.8),
              Theme.of(context).colorScheme.secondary.withOpacity(0.8),
              Theme.of(context).colorScheme.tertiary.withOpacity(0.8),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              const SizedBox(height: 20),
              TabBar(
                controller: _tabController,
                indicator: BoxDecoration(
                  borderRadius: BorderRadius.circular(25),
                  color: Colors.white.withOpacity(0.3),
                ),
                indicatorSize: TabBarIndicatorSize.tab,
                dividerColor: Colors.transparent,
                labelColor: Colors.white,
                unselectedLabelColor: Colors.white.withOpacity(0.6),
                labelStyle: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
                tabs: const [
                  Tab(
                    icon: Icon(Icons.mic),
                    text: '语音控制',
                  ),
                  Tab(
                    icon: Icon(Icons.music_note),
                    text: '音乐播放',
                  ),
                ],
              ),
              Expanded(
                // 修复：将 body 改为 child（Expanded 组件没有 body 属性，使用 child 承载子组件）
                child: TabBarView(
                  controller: _tabController,
                  children: const [
                    VoiceControlTab(),
                    MusicPlayerTab(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class VoiceControlTab extends StatefulWidget {
  const VoiceControlTab({super.key});

  @override
  State<VoiceControlTab> createState() => _VoiceControlTabState();
}

class _VoiceControlTabState extends State<VoiceControlTab>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;
  late BuildContext _context;

  @override
  void initState() {
    super.initState();
    _context = context; // 保存context引用
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.2).animate(
      CurvedAnimation(
        parent: _pulseController,
        curve: Curves.easeInOut,
      ),
    );

    // 设置语音识别完成回调
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final voiceService = Provider.of<VoiceService>(context, listen: false);
      voiceService.onRecognitionComplete = (command) {
        _processVoiceCommand(context, command);
      };
    });
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer2<VoiceService, ApiProvider>(
      builder: (context, voiceService, apiProvider, child) {
        // 根据监听状态控制动画
        if (voiceService.isListening) {
          _pulseController.repeat(reverse: true);
        } else {
          _pulseController.stop();
          _pulseController.reset();
        }

        return SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(height: 40),
              // API状态卡片
              // Container(
              //   width: double.infinity,
              //   padding: const EdgeInsets.all(20),
              //   decoration: BoxDecoration(
              //     color: Colors.white.withOpacity(0.15),
              //     borderRadius: BorderRadius.circular(20),
              //     boxShadow: [
              //       BoxShadow(
              //         color: Colors.black.withOpacity(0.1),
              //         blurRadius: 10,
              //         offset: const Offset(0, 5),
              //       ),
              //     ],
              //   ),
              //   child: Column(
              //     children: [
              //       Text(
              //         'API服务状态: ${apiProvider.healthStatus?.status == "success" ? "已连接" : "未连接"}',
              //         style: TextStyle(
              //           fontSize: 18,
              //           fontWeight: FontWeight.bold,
              //           color: apiProvider.healthStatus?.status == "success"
              //               ? Colors.green
              //               : Colors.red,
              //         ),
              //       ),
              //       const SizedBox(height: 10),
              //       if (apiProvider.lastError != null)
              //         Text(
              //           apiProvider.lastError!,
              //           style: const TextStyle(
              //             fontSize: 14,
              //             color: Colors.red,
              //           ),
              //           textAlign: TextAlign.center,
              //         ),
              //       const SizedBox(height: 10),
              //       Row(
              //         mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              //         children: [
              //           ElevatedButton(
              //             onPressed: () => apiProvider.checkHealth(),
              //             style: ElevatedButton.styleFrom(
              //               backgroundColor: Colors.white.withOpacity(0.2),
              //               foregroundColor: Colors.white,
              //             ),
              //             child: const Text('检查API连接'),
              //           ),
              //           ElevatedButton(
              //             onPressed: () => apiProvider.getStatus(),
              //             style: ElevatedButton.styleFrom(
              //               backgroundColor: Colors.white.withOpacity(0.2),
              //               foregroundColor: Colors.white,
              //             ),
              //             child: const Text('获取状态'),
              //           ),
              //           ElevatedButton(
              //             onPressed: () => apiProvider.startAssistant(),
              //             style: ElevatedButton.styleFrom(
              //               backgroundColor: Colors.white.withOpacity(0.2),
              //               foregroundColor: Colors.white,
              //             ),
              //             child: const Text('启动助手'),
              //           ),
              //         ],
              //       ),
              //     ],
              //   ),
              // ),
              const SizedBox(height: 20),
              // 语音状态卡片
              Consumer<VoiceService>(
                builder: (context, voiceService, child) {
                  return Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 10,
                          offset: const Offset(0, 5),
                        ),
                      ],
                    ),
                    child: Column(
                      children: [
                        const Text(
                          '语音状态',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 15),
                        Text(
                          voiceService.isListening ? '正在监听...' : '未监听',
                          style: TextStyle(
                            fontSize: 16,
                            color: voiceService.isListening
                                ? Colors.green
                                : Colors.grey,
                          ),
                        ),
                        const SizedBox(height: 10),
                        if (voiceService.lastWords.isNotEmpty)
                          Text(
                            '识别结果: ${voiceService.lastWords}',
                            style: const TextStyle(
                              fontSize: 14,
                              color: Colors.white,
                            ),
                          ),
                      ],
                    ),
                  );
                },
              ),

              const SizedBox(height: 30),

              // 麦克风按钮
              Consumer<VoiceService>(
                builder: (context, voiceService, child) {
                  return GestureDetector(
                    onTap: () {
                      if (voiceService.isListening) {
                        voiceService.stopListening();
                      } else {
                        voiceService.startListening();
                      }
                    },
                    child: Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: voiceService.isListening
                            ? Colors.red.withOpacity(0.8)
                            : Colors.blue.withOpacity(0.8),
                        boxShadow: [
                          BoxShadow(
                            color: voiceService.isListening
                                ? Colors.red.withOpacity(0.4)
                                : Colors.blue.withOpacity(0.4),
                            blurRadius: 20,
                            spreadRadius: 5,
                          ),
                        ],
                      ),
                      child: Icon(
                        voiceService.isListening ? Icons.mic : Icons.mic_none,
                        size: 60,
                        color: Colors.white,
                      ),
                    ),
                  );
                },
              ),

              const SizedBox(height: 30),

              // 识别tresult区域
              Consumer<VoiceService>(
                builder: (context, voiceService, child) {
                  return Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 10,
                          offset: const Offset(0, 5),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          '识别结果',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 10),
                        if (voiceService.lastWords.isNotEmpty)
                          Text(
                            voiceService.lastWords,
                            style: const TextStyle(
                              fontSize: 14,
                              color: Colors.white,
                            ),
                          )
                        else
                          const Text(
                            '等待语音输入...',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey,
                            ),
                          ),
                        const SizedBox(height: 15),
                        if (voiceService.lastWords.isNotEmpty)
                          ElevatedButton(
                            onPressed: () => _processVoiceCommand(
                                context, voiceService.lastWords),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.blue,
                              foregroundColor: Colors.white,
                            ),
                            child: const Text('执行命令'),
                          ),
                      ],
                    ),
                  );
                },
              ),

              const SizedBox(height: 30),

              // 语音命令帮助
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    const Text(
                      '语音命令帮助',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 10),
                    ElevatedButton(
                      onPressed: _showVoiceCommandHelp,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue,
                        foregroundColor: Colors.white,
                      ),
                      child: const Text('查看命令列表'),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 30),

              // 初始化语音识别
              Consumer<VoiceService>(
                builder: (context, voiceService, child) {
                  return Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 10,
                          offset: const Offset(0, 5),
                        ),
                      ],
                    ),
                    child: Column(
                      children: [
                        const Text(
                          '语音识别初始化',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 10),
                        ElevatedButton(
                          onPressed: () => voiceService.initialize(),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green,
                            foregroundColor: Colors.white,
                          ),
                          child: const Text('初始化语音识别'),
                        ),
                      ],
                    ),
                  );
                },
              ),

              const SizedBox(height: 30),

              // 错误信息
              Consumer<VoiceService>(
                builder: (context, voiceService, child) {
                  if (voiceService.lastError.isEmpty) {
                    return const SizedBox.shrink();
                  }

                  return Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(15),
                    decoration: BoxDecoration(
                      color: Colors.red.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      voiceService.lastError,
                      style: const TextStyle(
                        fontSize: 14,
                        color: Colors.white,
                      ),
                    ),
                  );
                },
              ),
            ],
          ),
        );
      },
    );
  }

  // 处理语音命令
  void _processVoiceCommand(BuildContext context, String command) async {
    try {
      final apiProvider = Provider.of<ApiProvider>(context, listen: false);
      final musicService = Provider.of<MusicService>(context, listen: false);

      // 首先尝试通过API服务处理命令
      final success = await apiProvider.sendCommand(command);

      if (!success) {
        // 如果API服务失败，回退到本地音乐服务
        if (command.toLowerCase().contains('播放') ||
            command.toLowerCase().contains('play')) {
          musicService.togglePlayPause();
        } else if (command.toLowerCase().contains('暂停') ||
            command.toLowerCase().contains('pause')) {
          musicService.togglePlayPause();
        } else if (command.toLowerCase().contains('下一首') ||
            command.toLowerCase().contains('next')) {
          musicService.playNext();
        } else if (command.toLowerCase().contains('上一首') ||
            command.toLowerCase().contains('previous')) {
          musicService.playPrevious();
        } else if (command.toLowerCase().contains('音量')) {
          // 尝试从命令中提取音量值
          final volumeRegex = RegExp(r'(\d+)%');
          final match = volumeRegex.firstMatch(command);
          if (match != null) {
            final volume = int.parse(match.group(1)!) / 100.0;
            musicService.setVolume(volume);
          }
        }
      }
    } catch (e) {
      print('处理语音命令时出错: $e');
    }
  }

  void _showVoiceCommandHelp() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('语音命令帮助'),
          content: SingleChildScrollView(
            child: ListBody(
              children: const [
                Text('AI助手控制:', style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                Text('• "你好助手" - 启动AI助手'),
                Text('• "今天天气怎么样" - 询问天气'),
                Text('• "设置一个闹钟" - 设置提醒'),
                Text('• "帮我查一下资料" - 搜索信息'),
                SizedBox(height: 16),
                Text('播放控制:', style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                Text('• "播放音乐" 或 "play" - 播放当前音乐'),
                Text('• "暂停音乐" 或 "pause" - 暂停当前音乐'),
                Text('• "下一首" 或 "next" - 播放下一首音乐'),
                Text('• "上一首" 或 "previous" - 播放上一首音乐'),
                SizedBox(height: 16),
                Text('音量控制:', style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                Text('• "增加音量" 或 "音量大一点" - 增加音量'),
                Text('• "减小音量" 或 "音量小一点" - 减少音量'),
                Text('• "音量50%" - 设置音量为50%'),
                SizedBox(height: 16),
                Text('播放指定歌曲:', style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                Text('• "播放[歌曲名]" - 播放指定的歌曲'),
                Text('例如: "播放夜曲"'),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: const Text('关闭'),
            ),
          ],
        );
      },
    );
  }
}

class MusicPlayerTab extends StatelessWidget {
  const MusicPlayerTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<MusicService>(
      builder: (context, musicService, child) {
        return SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              const SizedBox(height: 20),

              // 当前播放信息
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    const Text(
                      '正在播放',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      musicService.currentTrackName.isEmpty
                          ? '未选择音乐'
                          : musicService.currentTrackName,
                      style: const TextStyle(
                        fontSize: 16,
                        color: Colors.white,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 10),
                    // 进度条
                    Column(
                      children: [
                        SliderTheme(
                          data: SliderTheme.of(context).copyWith(
                            thumbShape: const RoundSliderThumbShape(
                                enabledThumbRadius: 8),
                            trackHeight: 4,
                            activeTrackColor: Colors.white,
                            inactiveTrackColor: Colors.white.withOpacity(0.3),
                            thumbColor: Colors.white,
                          ),
                          child: Slider(
                            value:
                                musicService.position.inMilliseconds.toDouble(),
                            max:
                                musicService.duration.inMilliseconds.toDouble(),
                            onChanged: (value) {
                              musicService.seekTo(
                                  Duration(milliseconds: value.round()));
                            },
                          ),
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              _formatDuration(musicService.position),
                              style: const TextStyle(
                                fontSize: 12,
                                color: Colors.white,
                              ),
                            ),
                            Text(
                              _formatDuration(musicService.duration),
                              style: const TextStyle(
                                fontSize: 12,
                                color: Colors.white,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 30),

              // 播放控制按钮
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // 上一首
                  IconButton(
                    onPressed: musicService.musicFiles.isEmpty
                        ? null
                        : () => musicService.playPrevious(),
                    icon: const Icon(Icons.skip_previous),
                    iconSize: 40,
                    color: Colors.white,
                  ),

                  // 播放/暂停
                  Container(
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.white.withOpacity(0.2),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 10,
                          offset: const Offset(0, 5),
                        ),
                      ],
                    ),
                    child: IconButton(
                      onPressed: musicService.musicFiles.isEmpty
                          ? null
                          : () => musicService.togglePlayPause(),
                      icon: Icon(
                        musicService.isPlaying ? Icons.pause : Icons.play_arrow,
                      ),
                      iconSize: 50,
                      color: Colors.white,
                    ),
                  ),

                  // 下一首
                  IconButton(
                    onPressed: musicService.musicFiles.isEmpty
                        ? null
                        : () => musicService.playNext(),
                    icon: const Icon(Icons.skip_next),
                    iconSize: 40,
                    color: Colors.white,
                  ),
                ],
              ),

              const SizedBox(height: 30),

              // 音量控制
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    const Text(
                      '音量控制',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        const Icon(Icons.volume_down, color: Colors.white),
                        Expanded(
                          child: SliderTheme(
                            data: SliderTheme.of(context).copyWith(
                              thumbShape: const RoundSliderThumbShape(
                                  enabledThumbRadius: 8),
                              trackHeight: 4,
                              activeTrackColor: Colors.white,
                              inactiveTrackColor: Colors.white.withOpacity(0.3),
                              thumbColor: Colors.white,
                            ),
                            child: Slider(
                              value: musicService.volume,
                              onChanged: (value) {
                                musicService.setVolume(value);
                              },
                            ),
                          ),
                        ),
                        const Icon(Icons.volume_up, color: Colors.white),
                        const SizedBox(width: 10),
                        SizedBox(
                          width: 40,
                          child: Text(
                            '${(musicService.volume * 100).round()}%',
                            style: const TextStyle(
                              fontSize: 12,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 30),

              // 音乐列表
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          '音乐列表',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        TextButton.icon(
                          onPressed: () => musicService.selectMusicFolder(),
                          icon: const Icon(Icons.folder_open,
                              color: Colors.white),
                          label: const Text('选择文件夹',
                              style: TextStyle(color: Colors.white)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    if (musicService.musicFiles.isEmpty)
                      const Text(
                        '暂无音乐文件，请选择音乐文件夹',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.white,
                        ),
                      )
                    else
                      SizedBox(
                        height: 200,
                        child: ListView.builder(
                          itemCount: musicService.musicFiles.length,
                          itemBuilder: (context, index) {
                            final file = musicService.musicFiles[index];
                            final fileName = file.path.split('/').last;
                            final isCurrentTrack =
                                index == musicService.currentTrackIndex;

                            return ListTile(
                              title: Text(
                                fileName,
                                style: TextStyle(
                                  color: isCurrentTrack
                                      ? Colors.yellow
                                      : Colors.white,
                                  fontWeight: isCurrentTrack
                                      ? FontWeight.bold
                                      : FontWeight.normal,
                                ),
                              ),
                              trailing: isCurrentTrack && musicService.isPlaying
                                  ? const Icon(Icons.play_arrow,
                                      color: Colors.white)
                                  : null,
                              onTap: () => musicService.playTrack(index),
                            );
                          },
                        ),
                      ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // 错误信息
              if (musicService.lastError.isNotEmpty)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(15),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    musicService.lastError,
                    style: const TextStyle(
                      fontSize: 14,
                      color: Colors.white,
                    ),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    String twoDigitMinutes = twoDigits(duration.inMinutes.remainder(60));
    String twoDigitSeconds = twoDigits(duration.inSeconds.remainder(60));
    return "$twoDigitMinutes:$twoDigitSeconds";
  }
}
