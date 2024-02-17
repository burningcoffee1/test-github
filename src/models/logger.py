"""
Logger 类和日志装饰器。
类介绍：
    Logger 类用于创建日志目录并构建日志文件路径。
    日志装饰器用于记录函数的开始和结束，以及记录函数的异常信息。

使用方法：
    1. 创建 Logger 实例。
    2. 使用 log_info、log_warning、log_error 方法记录日志。
    3. 使用 log_decorator 装饰器记录函数的开始和结束，以及记录函数的异常信息。

示例：
    # 创建 Logger 实例
    logger = Logger()
    logger.log_info("测试日志记录")
    print(logger.get_log_file_path())

    # 日志装饰器
    @log_decorator
    def test_function():
        print("测试函数")
        raise Exception("测试异常")
    test_function()
"""


import os
import logging
import functools

from datetime import datetime

class Logger:
    """
    设置日志功能。

    这个类用于创建日志目录并构建日志文件路径。
    """
    def __init__(self, log_directory="log"):
        self.log_directory = log_directory
        self.log_file = None
        self.setup_logging()

    def setup_logging(self):
        try:
            # 创建日志目录
            if not os.path.exists(self.log_directory):
                os.makedirs(self.log_directory)

            # 获取当前日期
            current_date = datetime.now().strftime("%Y-%m-%d")

            # 构建日志文件路径
            self.log_file = os.path.join(self.log_directory, f"{current_date}.log")

            # 配置日志记录
            logging.basicConfig(
                filename=self.log_file,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )

        except FileNotFoundError as exception:
            print(f"日志目录不存在: {str(exception)}")
        except OSError as exception:
            print(f"无法创建日志目录: {str(exception)}")
        except Exception as exception:
            print(f"日志配置失败: {str(exception)}")

    def log(self, message, level=logging.INFO):
        """
        通用日志记录方法

        Args:
            message (string): 记录的日志内容。
            level (logging.Level): 日志级别，默认为 INFO。
        """
        logging.log(level, message)

    def log_warning(self, message):
        """
        记录警告日志方法

        Args:
            message (string): 记录的日志内容。
        """
        self.log(message, level=logging.WARNING)

    def log_error(self, message):
        """
        记录错误日志方法

        Args:
            message (string): 记录的日志内容。
        """
        self.log(message, level=logging.ERROR)

    def log_info(self, message):
        """
        记录信息日志方法

        Args:
            message (string): 记录的日志内容。
        """
        self.log(message, level=logging.INFO)

    def get_log_file_path(self):
        """
        返回当前日志文件的路径。

        Returns:
            string: 日志文件的路径。
        """
        return self.log_file

# 创建 Logger 实例
logger_instance = Logger()

# 日志装饰器
def log_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 检查装饰的是否是实例方法
        if args and hasattr(args[0], func.__name__):
            class_name = args[0].__class__.__name__
            method_name = func.__name__
            full_name = f"{class_name}.{method_name}"
        else:
            full_name = func.__name__

        logger_instance.log_info(f"Starting '{full_name}'...")
        try:
            result = func(*args, **kwargs)
            logger_instance.log_info(f"Finished '{full_name}' successfully.")
            return result
        except Exception as e:
            logger_instance.log_error(f"Error occurred in '{full_name}': {e}")
            raise
    return wrapper
    
if __name__ == "__main__":
    # 创建全局的 Logger 实例
    logger = Logger()
    logger.log_info("测试日志记录")
    print(logger.get_log_file_path())
    