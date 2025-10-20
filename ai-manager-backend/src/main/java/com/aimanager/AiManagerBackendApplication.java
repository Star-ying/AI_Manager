package com.aimanager;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * AI Manager Backend 主应用程序
 * 
 * 功能：
 * - 语音控制AI助手后端服务
 * - 提供REST API接口
 * - 数据库管理和日志记录
 * - 与Python核心引擎通信
 * 
 * @author AI Manager Team
 * @version 1.0.0
 */
@SpringBootApplication
@EnableAsync
@EnableScheduling
public class AiManagerBackendApplication {

    public static void main(String[] args) {
        SpringApplication.run(AiManagerBackendApplication.class, args);
    }
}
