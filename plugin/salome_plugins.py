#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

'''
This is the file that is detected by salome in order to load the plugin
Do not rename or move this file!
Check "salome_pluginsmanager.py" for more information
'''

# Initialize logging
import os
import logging
from logging.handlers import RotatingFileHandler

logger_level = 2 # default value: 0

logger_levels = { 0 : logging.WARNING,
                  1 : logging.INFO,
                  2 : logging.DEBUG }

# configuring the root logger, same configuration will be automatically used for other loggers
root_logger = logging.getLogger()
root_logger.setLevel(logger_levels[logger_level])
root_logger.handlers.clear() # has to be cleared, otherwise more and more handlers are added if the plugin is reopened

# logging to console - without timestamp
ch = logging.StreamHandler()
ch_formatter = logging.Formatter("KSP [%(levelname)8s] %(name)s : %(message)s")
ch.setFormatter(ch_formatter)
root_logger.addHandler(ch)

# logging to file - with timestamp
from utilities.utils import GetAbsPathInPlugin
fh = RotatingFileHandler(os.path.join(GetAbsPathInPlugin(), "../plugin.log"), maxBytes=5*1024*1024, backupCount=1) # 5 MB
fh_formatter = logging.Formatter("[%(asctime)s] [%(levelname)8s] %(name)s : %(message)s", "%Y-%m-%d %H:%M:%S")
fh.setFormatter(fh_formatter)
root_logger.addHandler(fh)

logger = logging.getLogger(__name__)
logger.debug('loading module')


def InitializePlugin(context):
    """This is the main function for initializing the plugin
    The functions used must be declared inside this function, otherwise they are not available
    when the plugin is being loaded inside of Salome
    """

    ### settings for development/debugging
    reinitialize_data_handler = True # default value: False
    reload_modules = True # default value: False

    # python imports
    import os
    import sys
    import logging
    logger = logging.getLogger(__name__)

    # plugin imports
    from utilities import utils
    from module_reload_order import MODULE_RELOAD_ORDER
    import version
    from utilities import salome_utilities
    import qtsalome

    ### functions used in the plugin ###
    def ReloadModules():
        """Force reload of the modules
        This way Salome does not have to be reopened
        when something in the modules is changed
        """

        logger.debug("Starting to reload modules")

        for module_name in MODULE_RELOAD_ORDER:
            the_module = __import__(module_name, fromlist=[module_name[-1]])

            if sys.version_info < (3, 0): # python 2
                reload(the_module)
            elif sys.version_info >= (3, 4): # python >= 3.4
                import importlib
                importlib.reload(the_module)
            else: # python > 2 and <= 3.3
                # this variant is not strictly necessary, since salome uses either py2.7 (Salome 8) or py 3.6 (Salome 9)
                import imp
                imp.reload(the_module)

        # check the list
        # Note: performing the checks after reloading, this way Salome does not have to be closed for changing the list
        for module_name in MODULE_RELOAD_ORDER:
            if MODULE_RELOAD_ORDER.count(module_name) > 1:
                raise Exception('Module "{}" exists multiple times in the module reload order list!'.format(module_name))

        for module_name in utils.GetPythonModulesInDirectory(utils.GetPluginPath()):
            if module_name not in MODULE_RELOAD_ORDER and module_name != "salome_plugins":
                raise Exception('The python file "{}" was not added to the list for reloading modules!'.format(module_name))

        logger.debug("Successfully reloaded modules")


    ### initializing the plugin ###
    logger.info("Starting to initialize plugin\n")

    # logging configuration
    logger.info('Salome version: {}'.format(salome_utilities.GetVersion()))
    logger.info('Plugin version: {}'.format(version.VERSION))
    logger.info('Operating system: {}'.format(sys.platform))
    logger.info('Plugin-Config: reinitialize_data_handler: {}'.format(reinitialize_data_handler))
    logger.info('Plugin-Config: reload_modules: {}'.format(reload_modules))

    if reload_modules:
        ReloadModules()

    logger.info("Successfully initialized plugin")

    # check version of py-qt
    expected_qt_version = 5
    if not qtsalome.QT_SALOME_VERSION == expected_qt_version:
        logger.warning('The version of PyQt has changed, from {} to {}!'.format(expected_qt_version, QT_SALOME_VERSION))

    # check if version of salome is among the checked versions
    # TODO this should only appear once, couple it with data-handler intialization
    if not salome_utilities.GetVersion() in version.TESTED_SALOME_VERSIONS:
        msg  = 'This Plugin is not tested with this version of Salome.\n'
        msg += 'The tested versions are:'
        for v in version.TESTED_SALOME_VERSIONS:
            msg += '\n    {}.{}'.format(v[0], v[1])
        qtsalome.QMessageBox.warning(None, 'Untested Salome Version', msg)

    # message saying that it is under development
    info_msg  = 'This Plugin is currently under development and not fully operational yet.\n'
    info_msg += 'Please check "https://github.com/philbucher/KratosSalomePlugin" again at a later time.\n'
    info_msg += 'For further questions / requests please open an issue or contact "philipp.bucher@tum.de" directly.'

    qtsalome.QMessageBox.warning(None, 'Under Development', info_msg)



### Registering the Plugin in Salome ###

fct_args = [
    'Kratos Multiphysics',
    'Starting the plugin for Kratos Multiphysics',
]

import salome_pluginsmanager
import utilities.salome_utilities as salome_utils
from utilities.utils import GetAbsPathInPlugin

if salome_utils.GetVersion() >= (9,3):
    fct_args.append(InitializePlugin)
    from qtsalome import QIcon
    icon_file = GetAbsPathInPlugin("utilities","kratos_logo.png")
    fct_args.append(QIcon(icon_file))
else:
    def ShowMessageUnSupportedVersion(dummy):
        from qtsalome import QMessageBox
        QMessageBox.critical(None, 'Unsupported version', 'This Plugin only works for Salome versions 9.3 and newer.')
    fct_args.append(ShowMessageUnSupportedVersion)

salome_pluginsmanager.AddFunction(*fct_args)
