-- Active: 1760938925090@@127.0.0.1@3306
CREATE DATABASE IF NOT EXISTS ai_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ai_manager

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '用户姓名',
    email VARCHAR(100) UNIQUE COMMENT '邮箱（可选）',
    timezone VARCHAR(30) DEFAULT 'Asia/Shanghai' COMMENT '时区',
    language VARCHAR(10) DEFAULT 'zh-CN' COMMENT '语言偏好',
    avatar_url TEXT COMMENT '头像链接',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE sessions (
    session_id VARCHAR(64) PRIMARY KEY COMMENT '会话ID，UUID生成',
    user_id INT NOT NULL COMMENT '所属用户',
    title VARCHAR(100) DEFAULT '新对话' COMMENT '会话标题（AI 自动生成）',
    status ENUM('active', 'ended') DEFAULT 'active' COMMENT '状态',
    context JSON COMMENT '对话上下文，如意图、步骤、临时变量',
    model VARCHAR(50) DEFAULT 'gpt-4o-mini' COMMENT '使用的模型',
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NULL,
    metadata JSON COMMENT '附加信息：设备、IP、来源等',

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_status (user_id, status),
    INDEX idx_start_time (start_time)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE messages (
    message_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(64) NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    tokens INT COMMENT 'token 数量（用于成本统计）',
    model VARCHAR(50) COMMENT '本次响应所用模型',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON COMMENT '延迟、情绪标签、语音语调等',

    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_time (session_id, timestamp),
    INDEX idx_role (role)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tasks (
    task_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL COMMENT '任务标题',
    description TEXT COMMENT '详细描述',
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    due_date DATETIME NULL COMMENT '截止时间',
    category VARCHAR(50) COMMENT '分类：工作、生活、健康等',
    source VARCHAR(50) COMMENT '来源：语音指令、文本输入、日历同步等',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME NULL,
    metadata JSON COMMENT '额外字段：重复周期、提醒时间等',

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_status (user_id, status),
    INDEX idx_due_date (due_date),
    INDEX idx_category (category)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE files (
    file_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_id VARCHAR(64) NULL COMMENT '关联会话（可选）',
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(100) COMMENT 'MIME type: image/png, text/pdf 等',
    file_size BIGINT COMMENT '字节大小',
    storage_path TEXT NOT NULL COMMENT '本地路径或S3 URL',
    thumbnail_url TEXT COMMENT '缩略图（图片/视频）',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON COMMENT 'OCR结果、语音转文字内容等',

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE SET NULL,
    INDEX idx_user_filetype (user_id, file_type),
    INDEX idx_uploaded_at (uploaded_at)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入唯一用户
INSERT INTO users (name, email, timezone) 
VALUES ('Alice', 'alice@example.com', 'Asia/Shanghai');