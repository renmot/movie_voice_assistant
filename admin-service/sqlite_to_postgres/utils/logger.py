import logging

logger = logging.getLogger("load_data_logger")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s.%(msecs)03d %(name)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S.%m",
)

ch.setFormatter(formatter)
logger.addHandler(ch)
