#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher
#

# The file must NOT have dependencies on other files in the plugin!

# python imports
import os

def GetPluginPath():
    """This function returns the absolute path to the plugin
    """
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

def GetPythonFilesInDirectory(dir_name):
    """This function returns a list of all python files in a directory
    """
    return [os.path.relpath(os.path.join(os.path.relpath(dp, dir_name), f)) for dp, _, filenames in os.walk(dir_name) for f in filenames if (f.endswith(".py") and f != "__init__.py")]

def GetPythonModulesInDirectory(dir_name):
    """This function returns a list of all python modules in a directory
    """
    py_files = GetPythonFilesInDirectory(dir_name)
    # replacing "/" or "\" with "." and removing ".py" extension, e.g.:
    # folder/py_file.py => folder.py_file
    return [f[:-3].replace(os.sep, ".") for f in py_files]

def GetOrderModulesForReload():
    """This function returns a list containing the order in which the python modules should be reloaded
    The order has to be specified because of dependencies
    """
    module_reload_order = [
        "version",
        "utilities.utils",
        "model_part",
        "connectivities_io",
        "application",
        "serializer",
        "applications.generic.application",
        "applications.structural_mechanics.application"
    ]

    # check the list
    for module_name in module_reload_order:
        if module_reload_order.count(module_name) > 1:
            raise Exception('Module "{}" exists multiple times in the module reload order list!'.format(module_name))

    for module_name in GetPythonModulesInDirectory(GetPluginPath()):
        if module_name not in module_reload_order and module_name != "salome_plugins":
            raise Exception('The python file "{}" was not added to the list for reloading modules!'.format(module_name))

    return module_reload_order