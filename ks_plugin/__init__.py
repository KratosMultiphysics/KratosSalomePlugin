#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# In a "private" function to not pollute the global namespace
def __PrivateInitializeLogging():
    # python imports
    import sys
    import logging

    # plugin imports
    from .plugin_logging import InitializeLogging
    from .version import VERSION as PLUGIN_VERSION
    from .utilities.utils import IsExecutedInSalome

    InitializeLogging()

    logger = logging.getLogger("KRATOS SALOME PLUGIN")
    logger.info('Plugin version: {}'.format(PLUGIN_VERSION))
    if IsExecutedInSalome():
        from .utilities.salome_utilities import GetVersion as GetSalomeVersion
        logger.info('Running in Salome; Salome version: {}'.format(GetSalomeVersion()))
    else:
        logger.info('Not running in Salome')
    logger.debug('Operating system: {}'.format(sys.platform))

__PrivateInitializeLogging()
