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
This file contains utility functions
NOTE: This file must NOT have dependencies on other files in the plugin!
"""

# python imports
import os


def GetPluginPath():
    """This function returns the absolute path to the plugin"""
    return os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

def GetAbsPathInPlugin(*paths):
    """This function prepends the path to the plugin to a path given in the input"""
    return os.path.join(GetPluginPath(), *paths)

def ConvertPythonFileToPythonModule(file_name):
    """Converting a python file name to a python module name
    replacing "/" or "\" with "." and removing ".py" extension, e.g.:
    folder/py_file.py => folder.py_file
    """
    if not file_name.endswith(".py"):
        raise Exception('The input ("{}") is not a python-file, i.e. does not end with ".py"'.format(file_name))
    return file_name[:-3].replace(os.sep, ".")

def ConvertPythonFilesToPythonModules(file_names):
    """Converting a list of python file names to python module names"""
    return [ConvertPythonFileToPythonModule(file_name) for file_name in file_names]

def GetFilesInDirectory(dir_name):
    """This function returns a list of all files in a directory (top-down which is default for os.walk)
    It orderes the files top-down to get consistent results accross plattforms"""
    return [os.path.relpath(os.path.join(os.path.relpath(dp, dir_name), f)) for dp, _, filenames in os.walk(dir_name) for f in filenames]

def GetPythonFilesInDirectory(dir_name):
    """This function returns a list of all python files in a directory"""
    return [f for f in GetFilesInDirectory(dir_name) if (f.endswith(".py") and f.split(os.sep)[-1] != "__init__.py")]

def GetPythonModulesInDirectory(dir_name):
    """This function returns a list of all python modules in a directory"""
    return ConvertPythonFilesToPythonModules(GetPythonFilesInDirectory(dir_name))

def GetInitFilesInDirectory(dir_name):
    """This function returns a list of all "__init__.py" files in a directory"""
    return [f for f in GetFilesInDirectory(dir_name) if f.split(os.sep)[-1] == "__init__.py"]

def GetInitModulesInDirectory(dir_name):
    """This function returns a list of all "__init__.py" modules in a directory"""
    return ConvertPythonFilesToPythonModules(GetInitFilesInDirectory(dir_name))
