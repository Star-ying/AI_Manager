import 'dart:io';
import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

class MacOSPermissionService {
  static const String _errorMessage = '请在系统设置中为应用授予麦克风权限';

  // 请求并检查麦克风权限
  Future<bool> requestMicrophonePermission(BuildContext context) async {
    try {
      // 在macOS上，我们无法直接通过代码请求麦克风权限
      // 只能检查权限状态，并引导用户到系统设置
      if (await checkMicrophonePermission()) {
        return true;
      }
      
      // 显示权限请求对话框
      bool? userConfirmed = await showDialog<bool>(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: const Text('需要麦克风权限'),
            content: const Text(
              '此应用需要访问您的麦克风才能进行语音识别。\n\n'
              '请在系统设置中为应用授予麦克风权限：\n\n'
              '1. 打开系统偏好设置\n'
              '2. 点击"安全性与隐私"\n'
              '3. 选择"隐私"标签\n'
              '4. 在左侧列表中找到"麦克风"\n'
              '5. 在右侧列表中找到此应用并开启权限',
            ),
            actions: <Widget>[
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop(false);
                },
                child: const Text('取消'),
              ),
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop(true);
                },
                child: const Text('打开系统设置'),
              ),
            ],
          );
        },
      );

      if (userConfirmed == true) {
        // 使用GlobalKey来获取有效的BuildContext
        final navigatorKey = GlobalKey<NavigatorState>();
        if (navigatorKey.currentContext != null) {
          await openSystemSettings(navigatorKey.currentContext!);
        } else {
          // 如果无法获取有效的context，直接打开系统设置
          await Process.run('open', ['/System/Library/PreferencePanes/Security.prefPane']);
        }
      }
      
      return false;
    } catch (e) {
      print('请求麦克风权限时出错: $e');
      return false;
    }
  }

  // 检查麦克风权限状态
  Future<bool> checkMicrophonePermission() async {
    try {
      // 在macOS上，我们尝试通过speech_to_text插件来检查麦克风权限
      // 这不是一个完美的解决方案，但是一个实用的方法
      // 如果speech_to_text能够初始化，那么我们假设有麦克风权限
      try {
        final stt.SpeechToText speech = stt.SpeechToText();
        bool isAvailable = false;
        
        // 尝试初始化，但不抛出异常
        try {
          isAvailable = await speech.initialize(
            onStatus: (status) {
              print('语音识别状态: $status');
            },
            onError: (error) {
              print('语音识别错误: ${error.errorMsg}');
            },
          );
        } catch (e) {
          print('语音识别初始化失败: $e');
          return false;
        }
        
        // 如果初始化成功，说明有麦克风权限
        if (isAvailable) {
          print('语音识别服务可用，麦克风权限已授予');
          return true;
        }
        
        // 如果初始化失败，可能是权限问题
        print('语音识别服务不可用，可能没有麦克风权限');
        return false;
      } catch (e) {
        print('检查麦克风权限时出错: $e');
        // 如果检查出错，我们假设没有权限，让语音识别尝试初始化
        // 如果没有权限，语音识别会失败并提示用户
        return false;
      }
    } catch (e) {
      print('检查麦克风权限时出错: $e');
      // 如果检查出错，我们假设没有权限，让语音识别尝试初始化
      // 如果没有权限，语音识别会失败并提示用户
      return false;
    }
  }

  // 打开系统设置
  Future<void> openSystemSettings(BuildContext context) async {
    try {
      // 在macOS上，我们可以使用Process.run来打开系统设置
      await Process.run('open', ['/System/Library/PreferencePanes/Security.prefPane']);
      
      // 显示提示对话框
      showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: const Text('已打开系统设置'),
            content: const Text(
              '请在系统设置中为应用授予麦克风权限：\n\n'
              '1. 点击"隐私"标签\n'
              '2. 在左侧列表中找到"麦克风"\n'
              '3. 在右侧列表中找到此应用并开启权限\n\n'
              '授予权限后，请返回应用并重试。',
            ),
            actions: <Widget>[
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                },
                child: const Text('确定'),
              ),
            ],
          );
        },
      );
    } catch (e) {
      print('打开系统设置时出错: $e');
      // 如果出错，显示提示对话框
      showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: const Text('需要麦克风权限'),
            content: const Text(
              '请在系统设置中为应用授予麦克风权限：\n\n'
              '1. 打开系统偏好设置\n'
              '2. 点击"安全性与隐私"\n'
              '3. 选择"隐私"标签\n'
              '4. 在左侧列表中找到"麦克风"\n'
              '5. 在右侧列表中找到此应用并开启权限',
            ),
            actions: <Widget>[
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                },
                child: const Text('确定'),
              ),
            ],
          );
        },
      );
    }
  }
}