ai-manager-backend/
├── pom.xml                           # Maven配置文件
├── README.md                         # 项目说明文档
├── .gitignore                        # Git忽略文件
├── .mvn/                             # Maven Wrapper
│   └── wrapper/
│       ├── maven-wrapper.jar
│       └── maven-wrapper.properties
├── mvnw                              # Maven Wrapper脚本
├── mvnw.cmd                          # Maven Wrapper脚本(Windows)
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── aimanager/
│   │   │           ├── AiManagerBackendApplication.java
│   │   │           ├── config/                      # 配置类
│   │   │           │   ├── DatabaseConfig.java
│   │   │           │   ├── SecurityConfig.java
│   │   │           │   ├── WebSocketConfig.java
│   │   │           │   └── LoggingConfig.java
│   │   │           ├── controller/                 # REST控制器
│   │   │           │   ├── VoiceController.java
│   │   │           │   ├── SystemController.java
│   │   │           │   ├── ConfigController.java
│   │   │           │   └── HealthController.java
│   │   │           ├── service/                    # 业务服务层
│   │   │           │   ├── VoiceService.java
│   │   │           │   ├── SystemService.java
│   │   │           │   ├── ConfigService.java
│   │   │           │   ├── LoggingService.java
│   │   │           │   └── PythonApiService.java
│   │   │           ├── repository/                 # 数据访问层
│   │   │           │   ├── VoiceHistoryRepository.java
│   │   │           │   ├── UserSettingsRepository.java
│   │   │           │   └── SystemLogRepository.java
│   │   │           ├── entity/                     # 实体类
│   │   │           │   ├── VoiceHistory.java
│   │   │           │   ├── UserSettings.java
│   │   │           │   └── SystemLog.java
│   │   │           ├── dto/                        # 数据传输对象
│   │   │           │   ├── VoiceCommandDto.java
│   │   │           │   ├── SystemStatusDto.java
│   │   │           │   └── ConfigDto.java
│   │   │           ├── exception/                  # 异常处理
│   │   │           │   ├── GlobalExceptionHandler.java
│   │   │           │   ├── VoiceException.java
│   │   │           │   └── SystemException.java
│   │   │           ├── util/                       # 工具类
│   │   │           │   ├── JsonUtils.java
│   │   │           │   ├── FileUtils.java
│   │   │           │   └── ValidationUtils.java
│   │   │           └── websocket/                  # WebSocket处理
│   │   │               ├── WebSocketHandler.java
│   │   │               └── VoiceStatusHandler.java
│   │   └── resources/
│   │       ├── application.yml                     # 主配置文件
│   │       ├── application-dev.yml                 # 开发环境配置
│   │       ├── application-test.yml                # 测试环境配置
│   │       ├── application-prod.yml                # 生产环境配置
│   │       ├── logback-spring.xml                  # 日志配置
│   │       ├── db/
│   │       │   ├── migration/                     # 数据库迁移脚本
│   │       │   │   ├── V1__Create_initial_tables.sql
│   │       │   │   └── V2__Add_indexes.sql
│   │       │   └── data/                          # 初始数据
│   │       │       └── default_settings.sql
│   │       └── static/                             # 静态资源
│   │           ├── css/
│   │           ├── js/
│   │           └── images/
│   └── test/
│       ├── java/
│       │   └── com/
│       │       └── aimanager/
│       │           ├── AiManagerBackendApplicationTests.java
│       │           ├── controller/                 # 控制器测试
│       │           ├── service/                    # 服务层测试
│       │           ├── repository/                 # 数据层测试
│       │           └── integration/                # 集成测试
│       └── resources/
│           ├── application-test.yml               # 测试配置
│           └── test-data/                          # 测试数据
│               ├── test-voice-commands.json
│               └── test-config.json
├── docs/                                           # 项目文档
│   ├── api/                                        # API文档
│   ├── deployment/                                 # 部署文档
│   └── development/                                # 开发文档
├── scripts/                                        # 脚本文件
│   ├── build.sh                                    # 构建脚本
│   ├── deploy.sh                                   # 部署脚本
│   └── dependency-check.sh                         # 依赖检查脚本
└── docker/                                         # Docker配置
    ├── Dockerfile
    ├── docker-compose.yml
    └── docker-compose.dev.yml
