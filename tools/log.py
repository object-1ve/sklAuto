import logging

# 配置日志格式和级别
def init_loging_config():
    # 设置日志文件，记录 INFO 及以上级别的日志
    file_handler = logging.FileHandler('logs/app.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s (%(filename)s:%(lineno)d) - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # 设置控制台输出，记录 DEBUG 及以上级别的日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s (%(filename)s:%(lineno)d) - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    # 获取日志器
    _logger = logging.getLogger("sklZJNU")
    _logger.setLevel(logging.DEBUG)  # 设置日志器级别为 DEBUG，确保所有日志级别都可以被处理

    # 添加文件和控制台处理器
    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)

    return _logger

logger = init_loging_config()

# 记录不同级别的日志信息
# logger.debug('这是一个调试信息')     # 调试信息
# logger.info('程序开始运行')           # 一般信息
# logger.warning('这是一个警告')        # 警告信息
# logger.error('出现了一个错误')        # 错误信息
# logger.critical('程序崩溃')           # 严重错误
