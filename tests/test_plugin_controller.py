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
import unittest
from unittest.mock import patch

# plugin imports
from kratos_salome_plugin.gui.plugin_controller import PluginController

# tests imports
from testing_utilities import QtTestCase

# qt imports
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


class TestPluginControllerGUIConnection(QtTestCase):
    """This test checks if the correct functions of the backend are called
    Due to the connection of the functions to the gui the methods have to be mocked
    before the object is created
    """

    def test_file_new(self):
        with patch.object(PluginController, '_New') as patch_fct:
            controller = PluginController()
            controller.main_window.actionNew.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_file_open(self):
        with patch.object(PluginController, '_Open') as patch_fct:
            controller = PluginController()
            controller.main_window.actionOpen.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_file_open_button(self):
        with patch.object(PluginController, '_Open') as patch_fct:
            controller = PluginController()
            QTest.mouseClick(controller.main_window.pushButton_Open, Qt.LeftButton)
            self.assertEqual(patch_fct.call_count, 1)

    def test_file_save(self):
        with patch.object(PluginController, '_Save') as patch_fct:
            controller = PluginController()
            controller.main_window.actionSave.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_file_save_as(self):
        with patch.object(PluginController, '_SaveAs') as patch_fct:
            controller = PluginController()
            controller.main_window.actionSave_As.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_file_settings(self):
        with patch.object(PluginController, '_Settings') as patch_fct:
            controller = PluginController()
            controller.main_window.actionSettings.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_file_close(self):
        with patch.object(PluginController, '_Close') as patch_fct:
            controller = PluginController()
            controller.main_window.actionClose.trigger()
            self.assertEqual(patch_fct.call_count, 1)


    def test_kratos_groups(self):
        with patch.object(PluginController, '_Groups') as patch_fct:
            controller = PluginController()
            controller.main_window.actionGroups.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_kratos_load_application(self):
        with patch.object(PluginController, '_LoadApplication') as patch_fct:
            controller = PluginController()
            controller.main_window.actionLoad_Application.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_kratos_load_application_button(self):
        with patch.object(PluginController, '_LoadApplication') as patch_fct:
            controller = PluginController()
            QTest.mouseClick(controller.main_window.pushButton_Load_Application, Qt.LeftButton)
            self.assertEqual(patch_fct.call_count, 1)

    def test_kratos_import_mdpa(self):
        with patch.object(PluginController, '_ImportMdpa') as patch_fct:
            controller = PluginController()
            controller.main_window.actionImport_MDPA.trigger()
            self.assertEqual(patch_fct.call_count, 1)


    def test_help_about(self):
        with patch('kratos_salome_plugin.gui.plugin_controller.ShowAbout') as patch_fct:
            controller = PluginController()
            controller.main_window.actionAbout.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_help_website(self):
        with patch('kratos_salome_plugin.gui.plugin_controller.webbrowser') as patch_fct:
            controller = PluginController()
            controller.main_window.actionWebsite.trigger()
            self.assertEqual(patch_fct.open.call_count, 1)


class TestPluginControllerWindowCloseReopen(QtTestCase):
    """This test makes sure if the MainWindow is closed, it is not destroyed"""

    def test_main_window_reopen(self):
        controller = PluginController()

        orig_obj = controller.main_window

        controller.main_window.close()

        controller.ShowMainWindow()

        self.assertIs(orig_obj, controller.main_window)


if __name__ == '__main__':
    unittest.main()
