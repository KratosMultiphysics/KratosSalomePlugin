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
    """This is the main function for initializing the plugin
    The functions used must be declared inside this function, otherwise they are not available
    when the plugin is being loaded inside of Salome
    """

    ### settings for development/debugging
    reinitialize_data_handler = True # default value: False
    reload_modules = True # default value: False

    # python imports
    import logging
    logger = logging.getLogger(__name__)

    # plugin imports
    import kratos_salome_plugin.utilities as utils
    from kratos_salome_plugin.module_reload_order import MODULE_RELOAD_ORDER
    import kratos_salome_plugin.version as plugin_version
    from kratos_salome_plugin.salome_dependent import salome_utilities

    # salome imports
    import qtsalome

    ### functions used in the plugin ###
    def ReloadModules():
        """Force reload of the modules
        This way Salome does not have to be reopened
        when something in the modules is changed
        Very helpful (and only needed) for developing
        """

        import importlib
        logger.debug("Starting to reload modules")

        def ReloadListOfModules(list_modules):
            for module_name in list_modules:
                module_name = 'kratos_salome_plugin.' + module_name # forcing that only things from the "kratos_salome_plugin" folder can be imported
                the_module = __import__(module_name, fromlist=[module_name[-1]])
                importlib.reload(the_module)

        # first reload the real modules then the "__init__.py" files (some "__init__.py"s depend on other files but not vise-versa!)
        ReloadListOfModules(MODULE_RELOAD_ORDER)
        # the order overall should not matter since the "__init__.py"s don't (really should not) depend on each other
        ReloadListOfModules(utils.GetInitModulesInDirectory(utils.GetPluginPath()))

        # check the list
        # Note: performing the checks after reloading, this way Salome does not have to be closed for changing the list (bcs we are also reloading MODULE_RELOAD_ORDER)
        for module_name in MODULE_RELOAD_ORDER:
            if MODULE_RELOAD_ORDER.count(module_name) > 1:
                raise Exception('Module "{}" exists multiple times in the module reload order list!'.format(module_name))

        for module_name in utils.GetPythonModulesInDirectory(utils.GetPluginPath()):
            if module_name not in MODULE_RELOAD_ORDER and module_name != "salome_plugins":
                raise Exception('The python file "{}" was not added to the list for reloading modules!'.format(module_name))

        logger.debug("Successfully reloaded modules")


    ### initializing the plugin ###
    logger.info("")
    logger.info("Starting to initialize plugin")

    # logging configuration
    logger.info('Plugin-Config: reinitialize_data_handler: {}'.format(reinitialize_data_handler))
    logger.info('Plugin-Config: reload_modules: {}'.format(reload_modules))

    if reload_modules:
        ReloadModules()

    logger.info("Successfully initialized plugin")

    # check version of py-qt
    expected_qt_version = 5
    if not qtsalome.QT_SALOME_VERSION == expected_qt_version:
        logger.warning('The version of PyQt has changed, from {} to {}!'.format(expected_qt_version, qtsalome.QT_SALOME_VERSION))

    # check if version of salome is among the checked versions
    # TODO this should only appear once, couple it with data-handler intialization
    if not salome_utilities.GetVersions() in plugin_version.TESTED_SALOME_VERSIONS:
        msg  = 'This Plugin is not tested with this version of Salome.\n'
        msg += 'The tested versions are:'
        for v in plugin_version.TESTED_SALOME_VERSIONS:
            msg += '\n    {}.{}.{}'.format(v[0],v[1],v[2])
        qtsalome.QMessageBox.warning(None, 'Untested Salome Version', msg)

    # message saying that it is under development
    info_msg  = 'This Plugin is currently under development and not fully operational yet.\n\n'
    info_msg += 'Please check "https://github.com/philbucher/KratosSalomePlugin/issues/32" for infos about the current status of development.\n\n'
    info_msg += 'For further questions / requests please open an issue or contact "philipp.bucher@tum.de" directly.'

    qtsalome.QMessageBox.warning(None, 'Under Development', info_msg)


### Registering the Plugin in Salome ###

fct_args = [
    'Kratos Multiphysics',
    'Starting the plugin for Kratos Multiphysics',
]

import salome_pluginsmanager
import kratos_salome_plugin.salome_dependent.salome_utilities as salome_utils
from kratos_salome_plugin.utilities import GetAbsPathInPlugin

if salome_utils.GetVersions() >= [9,3,0]:
    fct_args.append(InitializePlugin)
    from qtsalome import QIcon
    icon_file = GetAbsPathInPlugin("misc","kratos_logo.png")
    fct_args.append(QIcon(icon_file))
else:
    def ShowMessageUnSupportedVersion(dummy):
        from qtsalome import QMessageBox
        QMessageBox.critical(None, 'Unsupported version', 'This Plugin only works for Salome version 9.3 and newer!')
    fct_args.append(ShowMessageUnSupportedVersion)

salome_pluginsmanager.AddFunction(*fct_args)
