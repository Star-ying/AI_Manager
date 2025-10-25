import Cocoa
import FlutterMacOS

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
    let mainBundle = Bundle.main
    if let infoDictionary = mainBundle.infoDictionary {
      if let microphoneUsageDescription = infoDictionary["NSMicrophoneUsageDescription"] as? String {
        print("麦克风权限描述: \(microphoneUsageDescription)")
      }
    }
  }
}
