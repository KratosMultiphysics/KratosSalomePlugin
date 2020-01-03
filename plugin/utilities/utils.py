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

import os

def GetPluginPath():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

def GetPythonFilesInDirectory(dir_name):
    return [os.path.relpath(os.path.join(os.path.relpath(dp, dir_name), f)) for dp, _, filenames in os.walk(dir_name) for f in filenames if (f.endswith(".py") and f != "__init__.py")]
