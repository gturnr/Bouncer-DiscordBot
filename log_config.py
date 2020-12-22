import logging, sys

formatter = logging.Formatter('%(asctime)s [%(levelname)s] | %(message)s')

def setup_logger(name, file_based=True, log_file='log.txt', level=logging.INFO, console_level=logging.WARNING):

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if file_based:
        handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)

        logger.addHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)

    return logger
