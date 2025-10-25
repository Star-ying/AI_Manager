# 🌐 AI 助手 API 接口文档
服务地址: http://127.0.0.1:5000/api

协议: HTTP/HTTPS
编码: UTF-8
内容类型: application/json
跨域支持: ✅ 已启用 CORS

# 🔑 认证方式（可选）暂时不加密钥
目前为本地服务，默认信任内网调用。
如需安全增强，请添加：

http

    X-API-Key: your-secret-token

或使用 HTTPS + IP 白名单。

# 📚 接口列表
路径	    方法	 功能
/health	    GET	    健康检查
/status	    GET	    获取当前运行状态
/start	    POST	启动或唤醒助手
/command	POST	发送自然语言指令
/tts/speak	POST	主动播放语音
/wakeup	    POST	远程唤醒信号

1. GET /api/health - 健康检查

💡 描述
检查后端服务是否正常运行。

请求示例

http
    GET /api/health

成功响应

    {
        "status": "ok",
        "service": "ai_assistant",
        "timestamp": 1719876543
    }

字段	     类型	     说明
status	    string  	固定为 "ok" 表示存活
service	    string	    服务名称
timestamp	number	    当前时间戳

✅ 用途：Flutter App 启动时探测服务是否存在。

2. GET /api/status - 查询当前状态
💡 描述
获取语音识别器和 TTS 的实时状态。

请求示例

http

    GET /api/status

成功响应

    {
        "is_listening": true,
        "is_tts_playing": false,
        "current_timeout": 8,
        "last_command_result": {
            "success": true,
            "message": "正在播放音乐",
            "operation": "play_music"
        },
        "timestamp": 1719876543
    }

字段	             类型	     说明
is_listening	    boolean	    是否正在监听麦克风
is_tts_playing  	boolean	    是否正在播报语音
current_timeout	    float	    下一次监听超时时间（秒）
last_command_result	object	    上一条命令执行结果
timestamp	        number	     时间戳

📌 用途：

控制前端 UI 显示“AI 正在说话”

防止冲突收音

3. POST /api/start - 启动助手
💡 描述
用于前端点击“启动”按钮时触发。如果服务已运行则返回状态。

⚠️ 注意：不能真正“启动一个进程”，但可以确认服务就绪。

请求示例

http
    POST /api/start
    Content-Type: application/json

json
    {}

成功响应

    {
        "status": "running",
        "message": "AI 助手已就绪",
        "features": ["voice", "tts", "file", "app_control"],
        "timestamp": 1719876543
    }

字段	    类型	     说明
status	    string	    "running"
message	    string  	提示信息
features	array	    支持的功能列表
timestamp	number  	当前时间戳

4. POST /api/command - 执行用户指令（核心接口）
💡 描述
发送一条自然语言命令，走完整 AI 决策 → 执行 → 播报流程。

请求参数

    {
        "text": "打开记事本",
        "context": {
            "user_id": "U123",
            "device": "phone",
            "location": "bedroom"
        },
        "options": {
            "should_speak": true,
            "return_plan": false
        }
    }

参数	                类型	    必填       说明
text	                string  	✅	    用户输入的自然语言文本
context	                object  	❌	    上下文信息（可用于日志追踪）
options.should_speak	boolean 	❌	    是否让 TTS 播报结果（默认 true）
options.return_plan	    boolean	    ❌	    是否返回详细的执行计划（调试用）

成功响应

    {
        "success": true,
        "response_to_user": "已为您打开记事本",
        "operation": "open_app",
        "details": {
            "app_name": "notepad"
        },
        "should_speak": true,
        "plan": { ... },  // 仅当 return_plan=true 时存在
        "timestamp": 1719876543
    }

字段	            类型	     说明
success	            boolean	    执行是否成功
response_to_user	string	    要对用户说的话
operation	        string	    主要操作类型（如 open_app）
details	            object	    操作详情
should_speak	    boolean	    是否应播报语音
plan	            object	    完整任务计划（仅当开启时返回）
timestamp	        number	    时间戳

错误响应（400 Bad Request）

    {
        "success": false,
        "response_to_user": "未收到有效指令"
    }

5. POST /api/tts/speak - 主动播报语音
💡 描述
不经过 AI 决策，直接让助手说出一句话。

请求示例

http

    POST /api/tts/speak
    Content-Type: application/json

json

    {
        "text": "您的会议将在五分钟后开始"
    }

成功响应

    {
        "status": "speaking",
        "text": "您的会议将在五分钟后开始",
        "timestamp": 1719876543
    }

字段    	类型	     说明
status  	string  	"speaking"
text	    string  	正在播报的内容
timestamp	number  	时间戳

📌 用途：通知、提醒、异常报警等场景。

6. POST /api/wakeup - 远程唤醒
💡 描述
当手机检测到“小智小智”唤醒词后，发送此请求通知电脑准备接收指令。

请求示例

http

    POST /api/wakeup
    Content-Type: application/json

设备位置

    {
        "device": "phone",
        "location": "living_room"
    }

成功响应

    {
        "status": "ready",
        "message": "已进入倾听模式",
        "timestamp": 1719876543
    }

后端行为
设置 recognizer.is_listening = True

可播放提示音“滴”一声表示唤醒成功

📌 注意：建议配合 /api/command 使用，唤醒后再发命令。

🧪 测试建议（使用 curl）

# 检查健康
curl http://127.0.0.1:5000/api/health

# 唤醒
curl -X POST http://127.0.0.1:5000/api/wakeup

# 发送命令
curl -X POST http://127.0.0.1:5000/api/command \
     -H "Content-Type: application/json" \
     -d '{"text": "打开浏览器"}'

# 播报语音
curl -X POST http://127.0.0.1:5000/api/tts/speak \
     -H "Content-Type: application/json" \
     -d '{"text": "你好，我是你的语音助手"}'
     
✅ 最佳实践建议
项目	建议
🔐 安全性	生产环境加 Token 或 HTTPS
📦 打包部署	使用 PyInstaller 打包成 .exe 并设置开机自启
🔄 状态同步	前端轮询 /api/status 判断是否可交互
📈 日志记录	记录所有 /api/command 调用用于调试
🧭 唤醒策略	手机端做离线唤醒词检测，再发 /api/wakeup
