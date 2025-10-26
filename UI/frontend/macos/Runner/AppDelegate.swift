import Cocoa
import FlutterMacOS
import AVFoundation

@main
class AppDelegate: FlutterAppDelegate {
  override func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
    return true
  }

  override func applicationSupportsSecureRestorableState(_ app: NSApplication) -> Bool {
    return true
  }
  
  override func applicationDidFinishLaunching(_ notification: Notification) {
    // 请求麦克风权限
    requestMicrophonePermission()

    let mainBundle = Bundle.main
    if let infoDictionary = mainBundle.infoDictionary {
      if let microphoneUsageDescription = infoDictionary["NSMicrophoneUsageDescription"] as? String {
        print("麦克风权限描述: \(microphoneUsageDescription)")
      }
    }
  }

  // 申请 macOS 麦克风权限（修正版）
  private func requestMicrophonePermission() {
    // 检查麦克风设备是否可用
    // 检查麦克风设备是否可用（仅判断是否存在，不保留变量）
    guard AVCaptureDevice.default(.builtInMicrophone, for: .audio, position: .unspecified) != nil else {
        print("未检测到麦克风设备")
        return
    }
    
    // 修正：通过 AVCaptureDevice 类调用 authorizationStatus(for:)
    switch AVCaptureDevice.authorizationStatus(for: .audio) {
    case .notDetermined:
        // 首次请求权限
        AVCaptureDevice.requestAccess(for: .audio) { [weak self] granted in
            DispatchQueue.main.async {
                self?.handlePermissionResult(granted: granted)
            }
        }
    case .authorized:
        // 已授权
        handlePermissionResult(granted: true)
    case .denied, .restricted:
        // 被拒绝或受限制
        handlePermissionResult(granted: false)
    @unknown default:
        handlePermissionResult(granted: false)
    }
  }

  // 处理权限结果
  private func handlePermissionResult(granted: Bool) {
    if granted {
        print("麦克风权限已授予")
    } else {
        print("麦克风权限被拒绝或未授权")
        let alert = NSAlert()
        alert.messageText = "麦克风权限被拒绝"
        alert.informativeText = "请前往系统设置 -> 隐私与安全性 -> 麦克风，开启本应用的权限"
        alert.addButton(withTitle: "确定")
        alert.runModal()
    }
  }
}