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

# plugin imports
from kratos_salome_plugin import IsExecutedInSalome

# tests imports
from testing_utilities import QtTestCase

# tests are currently only run when Qt is available due to problems with mocking the QMessageBox

@unittest.skipIf(IsExecutedInSalome(), 'This test cannot be executed in Salome to not mess with "salome_pluginsmanager"')
class TestSalomePlugins(QtTestCase):
    def setUp(self):
        self.addCleanup(lambda: DeleteModuleIfExisting('salome_pluginsmanager'))
        self.addCleanup(lambda: DeleteModuleIfExisting('qtsalome'))
        self.addCleanup(lambda: DeleteModuleIfExisting('salome_plugins')) # this import is checked hence not importing it here

        sys.modules['salome_pluginsmanager'] = MagicMock()
        sys.modules['qtsalome'] = MagicMock()

    @patch('PyQt5.QtWidgets.QMessageBox')
    @patch('kratos_salome_plugin.salome_utilities.GetVersions', return_value= [9,4,0])
    @patch('kratos_salome_plugin.gui.active_window')
    @patch('kratos_salome_plugin.gui.plugin_controller.PluginController')
    def test_CreatePluginController(self,
        mock_plugin_controller,
        mock_active_window,
        mock_fct_get_versions,
        mock_message_box):
        """Test for checking if the initialization of the PluginController works correctly
        This must only be done once per salome session and not every time the plugin is reopened,
        otherwise data is lost
        """
        self.assertEqual(mock_plugin_controller.call_count, 0)
        self.assertEqual(mock_fct_get_versions.call_count, 0)
        self.assertEqual(mock_message_box.warning.call_count, 0)

        # this does sth when importing, hence doing it inside the test
        from salome_plugins import InitializePlugin

        self.assertEqual(mock_plugin_controller.call_count, 0)
        self.assertEqual(mock_fct_get_versions.call_count, 1) # called during importing
        self.assertEqual(mock_message_box.warning.call_count, 0)

        salome_context = None # this should not be used hence passing None
        InitializePlugin(salome_context)

        self.assertEqual(mock_plugin_controller.call_count, 1)
        self.assertEqual(mock_fct_get_versions.call_count, 2)
        self.assertEqual(mock_message_box.warning.call_count, 0) # not used if version is ok (which it is in this test)

        # calling it a second time is like pressing the plugin button a second time in salome
        # this should NOT re-create the PluginController, otherwise data is lost
        # also the version check should only be done once
        InitializePlugin(None)

        self.assertEqual(mock_plugin_controller.call_count, 1, msg="PluginController was not initialized correctly!")
        self.assertEqual(mock_fct_get_versions.call_count, 2)
        self.assertEqual(mock_message_box.warning.call_count, 0) # not used if version is ok (which it is in this test)

    @patch('PyQt5.QtWidgets.QMessageBox')
    @patch('kratos_salome_plugin.salome_utilities.GetVersions', return_value= [9,3,111])
    @patch('kratos_salome_plugin.gui.active_window')
    @patch('kratos_salome_plugin.gui.plugin_controller.PluginController')
    def test_IssueUntestedSalomeVersionMsgBox(self,
        mock_plugin_controller,
        mock_active_window,
        mock_fct_get_versions,
        mock_message_box):
        """Test for checking if the issuing of the MessageBox for untested Salome versions works"""
        self.assertEqual(mock_fct_get_versions.call_count, 0)
        self.assertEqual(mock_message_box.warning.call_count, 0)

        # this does sth when importing, hence doing it inside the test
        from salome_plugins import InitializePlugin

        self.assertEqual(mock_fct_get_versions.call_count, 1) # called during importing
        self.assertEqual(mock_message_box.warning.call_count, 0)

        salome_context = None # this should not be used hence passing None
        InitializePlugin(salome_context)

        self.assertEqual(mock_fct_get_versions.call_count, 2)
        self.assertEqual(mock_message_box.warning.call_count, 1)

        # calling it a second time is like pressing the plugin button a second time in salome
        # this should NOT open another version-warning messagebox
        # also the version check should only be done once
        InitializePlugin(None)

        self.assertEqual(mock_fct_get_versions.call_count, 2)
        self.assertEqual(mock_message_box.warning.call_count, 1)

    @patch('PyQt5.QtWidgets.QMessageBox')
    @patch('kratos_salome_plugin.salome_utilities.GetVersions', return_value= [9,3,111])
    @patch('kratos_salome_plugin.gui.active_window')
    @patch('kratos_salome_plugin.gui.plugin_controller.PluginController')
    def test_ShowActiveWindow(self,
        mock_plugin_controller,
        mock_active_window,
        mock_fct_get_versions,
        mock_message_box):
        """Test for checking if the active window is shown"""
        # this does sth when importing, hence doing it inside the test
        from salome_plugins import InitializePlugin

        self.assertEqual(mock_active_window.ACTIVE_WINDOW.ShowOnTop.call_count, 0)

        salome_context = None # this should not be used hence passing None
        InitializePlugin(salome_context)

        self.assertEqual(mock_active_window.ACTIVE_WINDOW.ShowOnTop.call_count, 1)

        # calling it a second time is like pressing the plugin button a second time in salome
        # this should again show the active win on top
        InitializePlugin(None)

        self.assertEqual(mock_active_window.ACTIVE_WINDOW.ShowOnTop.call_count, 2)


def DeleteModuleIfExisting(module_name):
    if module_name in sys.modules:
        del sys.modules[module_name]


if __name__ == '__main__':
    unittest.main()
