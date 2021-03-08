#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

"""
This file contains the initialization of the logger
that is used in the plugin.
I.e. it configures the "logging" module of python
"""

# python imports
import os
import sys
import traceback
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger("KRATOS SALOME PLUGIN")

# qt imports
try:
    from PyQt5 import QtWidgets
    qt_available = True
except:
    qt_available = False

# plugin imports
from . import IsExecutedInSalome
from .utilities import GetAbsPathInPlugin
if qt_available:
    from kratos_salome_plugin.gui.utilities import CreateInformativeMessageBox


class _AnsiColorStreamHandler(logging.StreamHandler):
    """This handler colorizes the log-level (e.g. INFO or DEBUG)
    It supports ansi color codes
    adapted from https://gist.github.com/mooware/a1ed40987b6cc9ab9c65
    """
    DEFAULT = '\x1b[0m'
    RED     = '\x1b[1;31m'
    RED_UDL = '\x1b[1;4m\x1b[1;31m'
    GREEN   = '\x1b[1;32m'
    YELLOW  = '\x1b[1;33m'
    BLUE    = '\x1b[1;34m'
    CYAN    = '\x1b[1;36m'

    CRITICAL = RED_UDL
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


class _MessageBoxLogHandler(logging.Handler):
    """This handler shows critical problems in a messagebox
    It is supposed to be used when running in salome to make the user aware
    """
    def __init__(self):
        """Only logs with level CRITICAL are emitted"""
        super().__init__(logging.CRITICAL)

    def emit(self, record):
        """Open a messagebox showing the critical message"""
        informative_text = 'Please report this problem under "https://github.com/KratosMultiphysics/KratosSalomePlugin"'
        CreateInformativeMessageBox(
            "Critical event occurred!",
            'Critical',
            informative_text,
            record.getMessage())


def _HandleUnhandledException(exc_type, exc_value, exc_traceback):
    """Handler for unhandled exceptions that will write to the logs
    taken from: https://www.scrygroup.com/tutorial/2018-02-06/python-excepthook-logging/
    TODO: check if this also works properly in GUI
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # call the default excepthook saved at __excepthook__
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # log exception
    logger.exception("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    # if a GUI exists then also show exception in a MessageBox
    # see http://timlehr.com/python-exception-hooks-with-qt-message-box/
    if qt_available:
        if QtWidgets.QApplication.instance() is not None: # check if a GUI exists
            text = 'An unhandled excepition occured!'
            informative_text = 'Please report this problem under "https://github.com/KratosMultiphysics/KratosSalomePlugin"'

            detailed_text  = 'Details of the error:\n'
            detailed_text += 'Type: {}\n\n'.format(exc_type.__name__)
            detailed_text += 'Message: {}\n\n'.format(exc_value)
            detailed_text += 'Traceback:\n'
            for line in traceback.format_tb(exc_traceback):
                detailed_text += '  ' + line
            detailed_text = detailed_text.rstrip("\n")

            CreateInformativeMessageBox(text, 'Critical', informative_text, detailed_text)


def InitializeLogging(logging_level=logging.DEBUG):
    """Initialize and configure the logging of the plugin"""
     # CONFIG logging level
    # TODO switch the default in the future
    # TODO this should come from the config file
    # logger_level = 2 # default value: 0
    # logger_levels = { 0 : logging.WARNING,
    #                 1 : logging.INFO,
    #                 2 : logging.DEBUG }

    # configuring the root logger, same configuration will be automatically used for other loggers
    root_logger = logging.getLogger()

    # this is particularily helpful for testing to reduce the output
    disable_logging = bool(int(os.getenv("KRATOS_SALOME_PLUGIN_DISABLE_LOGGING", False)))

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
        elif IsExecutedInSalome():
            # Salome terminal supports colors both in Win and Linux
            ch = _AnsiColorStreamHandler()
        else:
            if os.name=="nt":
                # handler that supports color in Win is not yet implemented
                # see https://gist.github.com/mooware/a1ed40987b6cc9ab9c65
                # see https://plumberjack.blogspot.com/2010/12/colorizing-logging-output-in-terminals.html
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

        if IsExecutedInSalome():
            # if running in Salome, then show critical messages in a messagebox
            root_logger.addHandler(_MessageBoxLogHandler())

        sys.excepthook = _HandleUnhandledException

        logging.getLogger("PyQt5").setLevel(logging.WARNING) # CONFIG
