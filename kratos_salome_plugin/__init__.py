#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

def __CheckPythonVersion():
    """Make sure a compatible version of python is used"""
    # python imports
    import sys

    if sys.version_info[0] < 3:
        raise ImportError("This plugin only works with Python 3!")

    # activate this in the future
    # if sys.version_info[1] < 6:
    #     raise ImportError("This plugin needs at least Python 3.6!")


def __InitializeLogging():
    """Initialize the logging of the plugin
    It is a "private" function to not pollute the global namespace
    """
    # python imports
    import sys
    import logging

    # plugin imports
    from .plugin_logging import InitializeLogging
    from .version import GetVersionString as GetVersionString_Plugin
    from .utilities import IsExecutedInSalome

    InitializeLogging()

    logger = logging.getLogger("KRATOS SALOME PLUGIN")
    logger.info('Plugin version: {}'.format(GetVersionString_Plugin()))
    if IsExecutedInSalome():
        from .salome_dependent import salome_utilities
        logger.info('Running in Salome; version: {}; mode: {}'.format(salome_utilities.GetVersionString(), salome_utilities.ExecutionMode()))
    else:
        logger.info('Not running in Salome')
    logger.debug('Python version: {}'.format(".".join(map(str, sys.version_info[:3]))))
    if sys.version_info[1] < 6:
        logger.warning('It is recommended to use at least Python version 3.6, support for older versions will be dropped in the future!')
    logger.debug('Operating system: {}'.format(sys.platform))


__CheckPythonVersion()
__InitializeLogging()
