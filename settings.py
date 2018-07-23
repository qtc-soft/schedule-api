import logging
from aiohttp.log import access_logger
import configparser
import os

logger = logging.getLogger('mgate.service')
config = configparser.ConfigParser()


# !!! ENABLED DEV_MODE in PyCharm: start-project-settings -> edit configuration -> Environment variables -> add "dev_mode: True"
# set dev_mod
def get_dev_mode():
    return bool(os.environ.get('dev_mode'))


# init logging
def init_logging(prefix_log='', enable_console_handler=True):
    # path of the current file
    # path = os.path.dirname(os.path.abspath(__file__))
    # logs relative directory
    logs_abs_path = 'logs'
    # logs filename
    service_file_name = '%sservice.log' % prefix_log
    access_file_name = '%saccess.log' % prefix_log
    error_file_name = '%serror.log' % prefix_log

    # create logs directory
    if not os.path.exists(logs_abs_path):
        os.mkdir(logs_abs_path)

    # setup log formatter
    log_formatter = logging.Formatter(u'%(levelname)s: %(asctime)s: %(filename)s[LINE:%(lineno)d] %(message)s')

    # service log
    service_file_handler = logging.FileHandler(os.path.join(logs_abs_path, service_file_name))
    service_file_handler.setFormatter(log_formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(service_file_handler)

    # access log
    access_file_handler = logging.FileHandler(os.path.join(logs_abs_path, access_file_name))
    access_file_handler.setFormatter(log_formatter)
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(access_file_handler)

    # error log
    error_file_handler = logging.FileHandler(os.path.join(logs_abs_path, error_file_name))
    error_file_handler.setFormatter(log_formatter)
    error_file_handler.setLevel(logging.ERROR)

    # Logging service messages into console
    root_logger = logging.getLogger()
    root_logger.addHandler(error_file_handler)

    if enable_console_handler:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        console_handler.setLevel(logging.NOTSET)
        root_logger.addHandler(console_handler)


def init_settings():
    # TODO init settings-path (name folder)
    default_config_filename = 'default.cfg'
    config_filename = "config.cfg"
    successfully_loaded_cfg_files = config.read([default_config_filename, config_filename])
    logger.info("Successfully loaded config files {}".format(successfully_loaded_cfg_files))
