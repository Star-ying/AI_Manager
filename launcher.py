# launcher.py
import subprocess
import time
import requests
import os
import sys


def get_resource_path(relative_path):
    """获取资源真实路径，兼容 PyInstaller 打包"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# ✅ 改为指向 backend 目录下的 Python 模块
BACKEND_DIR = get_resource_path("backend")
FLUTTER_APP = get_resource_path("flutter_app\\ai_assistant.exe")

PYTHON_EXECUTABLE = "python"  # 或者用绝对路径 "python.exe"


def wait_for_api(url, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200 and resp.json().get("status") == "ok":
                print("✅ API 已就绪")
                return True
        except Exception as e:
            print(f"❌ API 尚未就绪: {e}")
        time.sleep(1)
    return False


def main():
    print("🎮 启动 AI 助手整合包...")
    print(f"📌 当前工作目录: {os.getcwd()}")

    # 检查 backend 是否存在
    if not os.path.exists(BACKEND_DIR):
        print(f"❌ 找不到 backend 目录: {BACKEND_DIR}")
        input("按回车键退出...")
        return

    if not os.path.exists(FLUTTER_APP):
        print(f"❌ 找不到 Flutter 应用: {FLUTTER_APP}")
        input("按回车键退出...")
        return

    # ✅ 使用 python -m backend.main 启动后端
    print("🔧 启动 Python AI 助手服务...")
    try:
        process = subprocess.Popen(
            [PYTHON_EXECUTABLE, "-m", "backend.main"],
            cwd=os.path.dirname(BACKEND_DIR),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            env={**os.environ, "PYTHONPATH": os.path.dirname(BACKEND_DIR)}  # 确保能 import
        )
    except FileNotFoundError:
        print("❌ 找不到 Python 解释器，请安装 Python 或使用虚拟环境打包")
        input("按回车键退出...")
        return
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        input("按回车键退出...")
        return

    print("⏳ 等待 API 就绪...")
    if not wait_for_api("http://127.0.0.1:5000/api/health"):
        print("❌ API 启动失败或超时")
        process.terminate()
        input("按回车键退出...")
        return

    print(f"📱 启动 Flutter 前端: {FLUTTER_APP}")
    try:
        subprocess.Popen([FLUTTER_APP], cwd=os.path.dirname(FLUTTER_APP))
    except Exception as e:
        print(f"❌ 启动 Flutter 失败: {e}")
        input("按回车键退出...")
        return

    print("🎉 系统已启动，正在运行中...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        process.terminate()


if __name__ == "__main__":
    main()
