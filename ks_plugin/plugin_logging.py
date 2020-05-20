#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# python imports
import logging
import os
from logging.handlers import RotatingFileHandler

# plugin imports
from .utilities.utils import GetAbsPathInPlugin

class _AnsiColorStreamHandler(logging.StreamHandler):
    # adapted from https://gist.github.com/mooware/a1ed40987b6cc9ab9c65
    DEFAULT = '\x1b[0m'
    RED     = '\x1b[31m'
    GREEN   = '\x1b[32m'
    YELLOW  = '\x1b[33m'
    CYAN    = '\x1b[36m'

    CRITICAL = RED
    ERROR    = RED
    WARNING  = YELLOW
    INFO     = GREEN
    DEBUG    = CYAN

    @classmethod
    def __GetColor(cls, level):
        if   level == logging.CRITICAL: return cls.CRITICAL
        elif level == logging.ERROR:    return cls.ERROR
        elif level == logging.WARNING:  return cls.WARNING
        elif level == logging.INFO:     return cls.INFO
        elif level == logging.DEBUG:    return cls.DEBUG
        else:                           return cls.DEFAULT

    @classmethod
    def __ColorLevel(cls, record):
        return cls.__GetColor(record.levelno) + record.levelname + cls.DEFAULT

    def format(self, record):
        text = super().format(record)
        return text.replace(record.levelname, self.__ColorLevel(record))


def InitializeLogging(logging_level=logging.DEBUG):
    # TODO switch the default in the future
    # TODO this should come from the config file
    # logger_level = 2 # default value: 0
    # logger_levels = { 0 : logging.WARNING,
    #                 1 : logging.INFO,
    #                 2 : logging.DEBUG }

    # configuring the root logger, same configuration will be automatically used for other loggers
    root_logger = logging.getLogger()

    disable_logging = os.getenv("KRATOS_SALOME_PLUGIN_DISABLE_LOGGING", False)

    if disable_logging:
        # this is intended for disabling the logger during testing, because some tests would generate output
        root_logger.disabled = True
        root_logger.setLevel(100) # setting a level higher than "critical" (which is level 50)
    else:
        root_logger.setLevel(logging_level)
        root_logger.handlers.clear() # has to be cleared, otherwise more and more handlers are added if the plugin is reopened

        # logging to console - without timestamp
        if "NO_COLOR" in os.environ: # maybe also check if isatty!
            # see https://no-color.org/
            ch = logging.StreamHandler()
        else:
            if os.name=="nt":
                # handler that supports color in Win is not yet implemented
                # see https://gist.github.com/mooware/a1ed40987b6cc9ab9c65
                ch = logging.StreamHandler()
            else:
                ch = _AnsiColorStreamHandler()

        ch_formatter = logging.Formatter("KSP [%(levelname)-8s] %(name)s : %(message)s")
        ch.setFormatter(ch_formatter)
        root_logger.addHandler(ch)

        # logging to file - with timestamp
        log_file_path = os.getenv("KRATOS_SALOME_PLUGIN_LOG_FILE_PATH", GetAbsPathInPlugin(os.pardir)) # unless otherwise specified log in root-dir
        fh = RotatingFileHandler(os.path.join(log_file_path, "kratos_salome_plugin.log"), maxBytes=5*1024*1024, backupCount=1) # 5 MB
        fh_formatter = logging.Formatter("[%(asctime)s] [%(levelname)-8s] %(name)s : %(message)s", "%Y-%m-%d %H:%M:%S")
        fh.setFormatter(fh_formatter)
        root_logger.addHandler(fh)
