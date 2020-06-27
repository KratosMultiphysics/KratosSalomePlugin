#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

def __CheckVersions():
    """Make sure a compatible version of Python and Salome is used"""
    # python imports
    import sys

    # plugin imports
    from .utilities import IsExecutedInSalome

    if sys.version_info[0] < 3:
        raise ImportError("This plugin only works with Python 3!")

    # activate this in the future
    # if sys.version_info[1] < 6:
    #     raise ImportError("This plugin needs at least Python 3.6!")

    if IsExecutedInSalome():
        from . import salome_utilities
        # if running in TUI, then also check the Salome version
        # => the GUI has a separate check for this, see "salome_plugins.py"
        if salome_utilities.GetVersions() < [9,3,0] and not salome_utilities.HasDesktop():
            raise ImportError("This Plugin only works for Salome version 9.3 and newer!")


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
        from . import salome_utilities
        logger.info('Running in Salome; version: {}; mode: {}'.format(salome_utilities.GetVersionString(), salome_utilities.ExecutionMode()))
    else:
        logger.info('Not running in Salome')
    logger.debug('Python version: {}'.format(".".join(map(str, sys.version_info[:3]))))
    if sys.version_info[1] < 6:
        logger.warning('It is recommended to use at least Python version 3.6, support for older versions will be dropped in the future!')
    logger.debug('Operating system: {}'.format(sys.platform))


__CheckVersions()
__InitializeLogging()
