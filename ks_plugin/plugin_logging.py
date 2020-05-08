#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# This file must NOT have dependencies on other files in the plugin!

# python imports
import logging
import os
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
logger.debug('loading module')


def InitializeLogging(log_file_path, logging_level=logging.DEBUG):
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
        ch = logging.StreamHandler()
        ch_formatter = logging.Formatter("KSP [%(levelname)8s] %(name)s : %(message)s")
        ch.setFormatter(ch_formatter)
        root_logger.addHandler(ch)

        # logging to file - with timestamp
        fh = RotatingFileHandler(os.path.join(log_file_path, "kratos_salome_plugin.log"), maxBytes=5*1024*1024, backupCount=1) # 5 MB
        fh_formatter = logging.Formatter("[%(asctime)s] [%(levelname)8s] %(name)s : %(message)s", "%Y-%m-%d %H:%M:%S")
        fh.setFormatter(fh_formatter)
        root_logger.addHandler(fh)
