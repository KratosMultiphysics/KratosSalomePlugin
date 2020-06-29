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
This is the file that is detected by salome in order to load the plugin
Do not rename or move this file!
Check "salome_pluginsmanager.py" for more information
"""

def InitializePlugin(context):
    """Main function for initializing / opening the plugin
    This is called each time the user opens the KratosMultiphysics plugin in Salome
    """

    ### for development/debugging
    reinitialize_every_time = True # default value: False

    # python imports
    import logging
    logger = logging.getLogger(__name__)

    # plugin imports
    from kratos_salome_plugin.gui.plugin_controller import PluginController
    import kratos_salome_plugin.version as plugin_version
    from kratos_salome_plugin import salome_utilities
    from kratos_salome_plugin.reload_modules import ReloadModules

    # salome imports
    import qtsalome

    # qt imports
    from PyQt5.QtWidgets import QMessageBox

    ### initializing the plugin ###
    logger.info("")
    logger.info("Starting to initialize plugin")

    # logging configuration
    logger.info('Reinitialize Plugin every time: %s', reinitialize_every_time)

    if reinitialize_every_time:
        ReloadModules()

    global VERSION_CHECKS_PERFORMED
    if 'VERSION_CHECKS_PERFORMED' not in globals():
        # doing the version check only once per session and not every time the plugin is reopened
        VERSION_CHECKS_PERFORMED = 1
        # check version of py-qt
        expected_qt_version = 52
        if not qtsalome.QT_SALOME_VERSION == expected_qt_version:
            logger.warning('The version of PyQt has changed, from %d to %d!', expected_qt_version, qtsalome.QT_SALOME_VERSION)

        # check if version of salome is among the checked versions
        # TODO this should only appear once, couple it with data-handler intialization
        if not salome_utilities.GetVersions() in plugin_version.TESTED_SALOME_VERSIONS:
            msg  = 'This Plugin is not tested with this version of Salome.\n'
            msg += 'The tested versions are:'
            for v in plugin_version.TESTED_SALOME_VERSIONS:
                msg += '\n    {}.{}.{}'.format(v[0],v[1],v[2])
            QMessageBox.warning(None, 'Untested Salome Version', msg)

    # message saying that it is under development
    info_msg  = 'This Plugin is currently under development and not fully operational yet.\n\n'
    info_msg += 'Please check "https://github.com/philbucher/KratosSalomePlugin/issues/32" for infos about the current status of development.\n\n'
    info_msg += 'For further questions / requests please open an issue or contact "philipp.bucher@tum.de" directly.'

    QMessageBox.warning(None, 'Under Development', info_msg)

    global PLUGIN_CONTROLLER
    if 'PLUGIN_CONTROLLER' not in globals() or reinitialize_every_time:
        # initialize only once the PluginController
        PLUGIN_CONTROLLER = PluginController()

    PLUGIN_CONTROLLER.ShowMainWindow()

    logger.info("Successfully initialized plugin")

### Registering the Plugin in Salome ###

fct_args = [
    'Kratos Multiphysics',
    'Starting the plugin for Kratos Multiphysics',
]

import salome_pluginsmanager
import kratos_salome_plugin.salome_utilities as salome_utils
from kratos_salome_plugin.utilities import GetAbsPathInPlugin

if salome_utils.GetVersions() >= [9,3,0]:
    fct_args.append(InitializePlugin)
    from PyQt5.QtGui import QIcon
    icon_file = GetAbsPathInPlugin("misc","kratos_logo.png")
    fct_args.append(QIcon(icon_file))
else:
    def ShowMessageUnSupportedVersion(dummy):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(None, 'Unsupported version', 'This Plugin only works for Salome version 9.3 and newer!')
    fct_args.append(ShowMessageUnSupportedVersion)

salome_pluginsmanager.AddFunction(*fct_args)
