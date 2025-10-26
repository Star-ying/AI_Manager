# utils/logger_config.py
import logging
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

def setup_logger(
    name="ai_assistant",
    log_dir="logs",
    level=logging.INFO,
    max_bytes=10 * 1024 * 1024,
    backup_count=7
):
    """
    设置并返回一个功能完整的日志器（Logger）
    
    Args:
        name: Logger 名称
        log_dir: 日志存储目录
        level: 默认记录级别
        max_bytes: 单个日志文件最大字节数
        backup_count: 保留的历史文件数量
    
    Returns:
        logging.Logger 实例
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    log_file = log_path / "app.log"
    debug_log_file = log_path / "debug.log"
    error_log_file = log_path / "error.log"

    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if logger.hasHandlers():
        logger.handlers.clear()

    # 1. 控制台输出 (INFO+)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # 2. 按天切分的日志（INFO+）-> app.log + app.log.YYYY-MM-DD
    timed_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=backup_count,
        encoding='utf-8'
    )
    timed_handler.setLevel(logging.INFO)
    timed_handler.setFormatter(detailed_formatter)
    logger.addHandler(timed_handler)

    # 3. Debug 日志（DEBUG+），滚动保存
    debug_handler = RotatingFileHandler(
        debug_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(detailed_formatter)
    logger.addHandler(debug_handler)

    # 4. 错误日志（ERROR+）
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)

    return logger
