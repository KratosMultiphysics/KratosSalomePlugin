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

import os
import sys
import logging

logger_level = 2 # default value: 0

logger_levels = { 0 : logging.WARNING,
                  1 : logging.INFO,
                  2 : logging.DEBUG }

logging.getLogger().setLevel(logger_levels[logger_level])


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

    # plugin imports
    from utilities import utils

    ### functions used in the plugin ###
    def ReloadModules():
        """Force reload of the modules
        This way Salome does not have to be reopened
        when something in the modules is changed"""

        logging.debug("Starting to reload modules")

        for module_name in utils.GetOrderModulesForReload():
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

        logging.debug("Successfully reloaded modules")


    ### initializing the plugin ###
    print("in InitializePlugin")
    if reload_modules:
        ReloadModules()


### Registering the Plugin in Salome ###

fct_args = [
    'Kratos Multiphysics',
    'Starting the plugin for Kratos Multiphysics',
    InitializePlugin]

# if salome_utilities.GetVersion() >= (9,3):
#     from plugin_utilities import GetPluginFilePath
#     from qtsalome import QIcon
#     icon_file = GetPluginFilePath("pictures","kratos_logo.png")
#     fct_args.append(QIcon(icon_file))

import salome_pluginsmanager
salome_pluginsmanager.AddFunction(*fct_args)
