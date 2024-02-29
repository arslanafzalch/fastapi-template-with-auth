import logging

from app.config import settings


class Logger(object):
    """
    class to call in methods and
    capture Debug logs into multiple files.
    """

    def __init__(self):
        self.formatter = logging.Formatter(
            "[%(asctime)s] - %(name)s -  %(levelname)s - %(message)s"
        )
        self.log_path = settings.LOG_PATH

    def extendable_logger(self, log_name, level=logging.DEBUG):
        handler = logging.FileHandler(self.log_path)
        handler.setFormatter(self.formatter)
        specified_logger = logging.getLogger(log_name)
        specified_logger.addHandler(handler)

        return specified_logger


logger = Logger()
