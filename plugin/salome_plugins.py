#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher
#

'''
This is the file that is detected by salome in order to load the plugin
Do not rename or move this file!
Check "salome_pluginsmanager.py" for more information
'''

### settings for development/debugging
logger_level = 2 # default value: 0
reinitialize_data_handler = True # default value: False
reload_modules = True # default value: False

import salome_pluginsmanager
# from utilities import utils
# from utilities import salome_utilities

def ReloadModules():
    pass

def InitializeKratosPlugin(context):
    print("in InitializeKratosPlugin")

### Registering the Plugin in Salome ###
fct_args = [
    'Kratos Multiphysics',
    'Starting the plugin for Kratos Multiphysics',
    InitializeKratosPlugin]

# if salome_utilities.GetVersion() >= (9,3):
#     from plugin_utilities import GetPluginFilePath
#     from qtsalome import QIcon
#     icon_file = GetPluginFilePath("pictures","kratos_logo.png")
#     fct_args.append(QIcon(icon_file))

salome_pluginsmanager.AddFunction(*fct_args)
