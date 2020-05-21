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
import os

def IsExecutedInSalome():
    """Function to check if the script is being executed inside Salome
    """
    return "SALOMEPATH" in os.environ

def GetPluginPath():
    """This function returns the absolute path to the plugin
    """
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

def GetAbsPathInPlugin(*paths):
    """This function prepends the path to the plugin to a path given in the input
    """
    return os.path.join(GetPluginPath(), *paths)

def GetPythonFilesInDirectory(dir_name):
    """This function returns a list of all python files in a directory
    """
    return [os.path.relpath(os.path.join(os.path.relpath(dp, dir_name), f)) for dp, _, filenames in os.walk(dir_name) for f in filenames if (f.endswith(".py") and f != "__init__.py")]

def GetPythonModulesInDirectory(dir_name):
    """This function returns a list of all python modules in a directory
    """
    # replacing "/" or "\" with "." and removing ".py" extension, e.g.:
    # folder/py_file.py => folder.py_file
    return [f[:-3].replace(os.sep, ".") for f in GetPythonFilesInDirectory(dir_name)]
