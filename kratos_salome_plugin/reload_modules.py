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
This file contains functionalities for reloading the modules of the plugin
This is used for debugging, this way Salome can stay opened and the source code
can be changed
"""

# python imports
import importlib
import logging
logger = logging.getLogger(__name__)

# plugin imports
from kratos_salome_plugin import utilities


"""A list containing the order in which the python modules should be reloaded when the plugin is (re-)opened
The order has to be specified because of dependencies
"""
MODULE_RELOAD_ORDER = [
    "exceptions",
    "version",
    "utilities",
    "salome_utilities",
    "salome_gui_utilities",
    "salome_mesh_utilities",
    "salome_study_utilities",
    "reload_modules",
    "mesh_interface",
    "model_part",
    "geometries_io",
    "write_mdpa",
    "plugin_logging",
    "base_application",
    "gui.utilities",
    "gui.about",
    "gui.active_window",
    "gui.project_path_handler",
    "gui.project_manager",
    "gui.base_window",
    "gui.plugin_main_window",
    "gui.group",
    "gui.groups_model",
    "gui.groups_window",
    "gui.plugin_controller",
    "applications.Generic.application",
    "applications.StructuralMechanics.application"
]

def ReloadModules():
    """Force reload of the modules
    This way Salome does not have to be reopened
    when something in the modules is changed
    Very helpful (and only needed) for developing
    """

    logger.debug("Starting to reload modules")

    def ReloadListOfModules(list_modules):
        for module_name in list_modules:
            module_name = 'kratos_salome_plugin.' + module_name # forcing that only things from the "kratos_salome_plugin" folder can be imported
            the_module = __import__(module_name, fromlist=[module_name[-1]])
            importlib.reload(the_module)

    # first reload the real modules then the "__init__.py" files (some "__init__.py"s depend on other files but not vise-versa!)
    ReloadListOfModules(MODULE_RELOAD_ORDER)
    # the order overall should not matter since the "__init__.py"s don't (really should not) depend on each other
    ReloadListOfModules(utilities.GetInitModulesInDirectory(utilities.GetPluginPath()))

    # check the list
    # Note: performing the checks after reloading, this way Salome does not have to be closed for changing the list (bcs we are also reloading MODULE_RELOAD_ORDER)
    for module_name in MODULE_RELOAD_ORDER:
        if MODULE_RELOAD_ORDER.count(module_name) > 1:
            raise Exception('Module "{}" exists multiple times in the module reload order list!'.format(module_name))

    for module_name in utilities.GetPythonModulesInDirectory(utilities.GetPluginPath()):
        if module_name not in MODULE_RELOAD_ORDER and module_name != "salome_plugins":
            raise Exception('The python file "{}" was not added to the list for reloading modules!'.format(module_name))

    logger.debug("Successfully reloaded modules")
