import logging
import os
from datetime import datetime

# 创建logs目录（如果不存在）
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# 配置日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# 创建日志记录器
def get_logger(name=__name__, level=logging.INFO):
    """
    获取配置好的日志记录器
    
    :param name: 日志记录器名称
    :param level: 日志级别
    :return: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    
    # 避免重复添加处理器
    if not logger.handlers:
        # 创建文件处理器
        log_file = os.path.join(logs_dir, f"{name}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # 创建格式化器并添加到处理器
        formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器到日志记录器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# 创建默认日志记录器
default_logger = get_logger("print_tool_advanced")
