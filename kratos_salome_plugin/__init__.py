#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

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
        from .salome_dependent.salome_utilities import GetVersionString as GetVersionString_Salome
        logger.info('Running in Salome; Salome version: {}'.format(GetVersionString_Salome()))
    else:
        logger.info('Not running in Salome')
    logger.debug('Operating system: {}'.format(sys.platform))


__InitializeLogging()
