#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# set up testing environment (before anything else)
import initialize_testing_environment

# python imports
import sys
import unittest
from unittest.mock import patch, MagicMock

@unittest.skipIf(initialize_testing_environment.IS_EXECUTED_IN_SALOME, "This test can only be executed outside Salome")
class TestSalomePlugins(unittest.TestCase):
    def test_CreatePluginController(self):

        sys.modules['salome_pluginsmanager'] = MagicMock()

        with patch('kratos_salome_plugin.gui.plugin_controller.PluginController') as mock_plugin_controller:
            with patch('salome_plugins.salome_utils.GetVersions', return_value=[10,0,0]) as mock_getversions:
                from salome_plugins import InitializePlugin

if __name__ == '__main__':
    unittest.main()
