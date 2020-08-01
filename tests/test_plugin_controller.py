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
from pathlib import Path
from os import listdir
import unittest
from unittest.mock import patch

# plugin imports
from kratos_salome_plugin.gui.plugin_controller import PluginController

# tests imports
from testing_utilities import QtTestCase, CreateHDFStudyFile, DeleteDirectoryIfExisting, SalomeTestCaseWithBox

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
            controller._main_window.actionNew.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_file_open(self):
        with patch.object(PluginController, '_Open') as patch_fct:
            controller = PluginController()
            controller._main_window.actionOpen.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_file_open_button(self):
        with patch.object(PluginController, '_Open') as patch_fct:
            controller = PluginController()
            QTest.mouseClick(controller._main_window.pushButton_Open, Qt.LeftButton)
            self.assertEqual(patch_fct.call_count, 1)

    def test_file_save(self):
        with patch.object(PluginController, '_Save') as patch_fct:
            controller = PluginController()
            controller._main_window.actionSave.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_file_save_as(self):
        with patch.object(PluginController, '_SaveAs') as patch_fct:
            controller = PluginController()
            controller._main_window.actionSave_As.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_file_settings(self):
        with patch.object(PluginController, '_Settings') as patch_fct:
            controller = PluginController()
            controller._main_window.actionSettings.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_file_close(self):
        with patch.object(PluginController, '_Close') as patch_fct:
            controller = PluginController()
            controller._main_window.actionClose.trigger()
            self.assertEqual(patch_fct.call_count, 1)


    def test_kratos_groups(self):
        with patch.object(PluginController, '_Groups') as patch_fct:
            controller = PluginController()
            controller._main_window.actionGroups.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_kratos_load_application(self):
        with patch.object(PluginController, '_LoadApplication') as patch_fct:
            controller = PluginController()
            controller._main_window.actionLoad_Application.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_kratos_load_application_button(self):
        with patch.object(PluginController, '_LoadApplication') as patch_fct:
            controller = PluginController()
            QTest.mouseClick(controller._main_window.pushButton_Load_Application, Qt.LeftButton)
            self.assertEqual(patch_fct.call_count, 1)

    def test_kratos_import_mdpa(self):
        with patch.object(PluginController, '_ImportMdpa') as patch_fct:
            controller = PluginController()
            controller._main_window.actionImport_MDPA.trigger()
            self.assertEqual(patch_fct.call_count, 1)


    def test_help_about(self):
        with patch('kratos_salome_plugin.gui.plugin_controller.ShowAbout') as patch_fct:
            controller = PluginController()
            controller._main_window.actionAbout.trigger()
            self.assertEqual(patch_fct.call_count, 1)

    def test_help_website(self):
        with patch('kratos_salome_plugin.gui.plugin_controller.webbrowser') as patch_fct:
            controller = PluginController()
            controller._main_window.actionWebsite.trigger()
            self.assertEqual(patch_fct.open.call_count, 1)


class TestPluginControllerWindowCloseReopen(QtTestCase):
    """This test makes sure if the MainWindow is closed, it is not destroyed"""

    def test_main_window_reopen(self):
        controller = PluginController()

        orig_obj = controller._main_window

        controller._main_window.close()

        controller.ShowMainWindow()

        self.assertIs(orig_obj, controller._main_window)


# using a module local patch due to import of QFileDialog in project_path_handler
# see https://realpython.com/python-mock-library/#where-to-patch
_QFileDialog_patch = 'kratos_salome_plugin.gui.project_path_handler.QFileDialog.'

class TestPluginControllerProject(unittest.TestCase):

    def test_New(self):
        controller = PluginController()

        controller._previous_save_path = Path("some/path")

        initial_project_manager = controller._project_manager
        initial_project_path_handler = controller._project_path_handler

        controller._New()

        # make sure things were cleaned properly
        self.assertIsNone(controller._previous_save_path)
        self.assertIsNot(initial_project_manager, controller._project_manager)
        self.assertIsNot(initial_project_path_handler, controller._project_path_handler)


    def test_Close(self):
        controller = PluginController()
        controller.ShowMainWindow()

        self.assertFalse(controller._main_window.isMinimized())
        self.assertTrue(controller._main_window.isVisible())
        self.assertFalse(controller._main_window.isHidden())
        self.assertEqual(controller._main_window.windowState(), Qt.WindowNoState)

        controller._Close()

        self.assertFalse(controller._main_window.isMinimized())
        self.assertFalse(controller._main_window.isVisible())
        self.assertTrue(controller._main_window.isHidden())
        self.assertEqual(controller._main_window.windowState(), Qt.WindowNoState)


    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    def test_SaveAs(self, mock_save_study, mock_version):
        project_dir = Path("controller_save_project_as.ksp")

        self.addCleanup(lambda: DeleteDirectoryIfExisting(project_dir))
        DeleteDirectoryIfExisting(project_dir) # remove potential leftovers

        controller = PluginController()

        self.assertIsNone(controller._previous_save_path)

        with patch.object(controller._main_window, 'StatusBarInfo') as patch_fct_status_bar:
            with patch.object(controller._project_path_handler, 'GetSavePath', return_value=project_dir) as patch_fct:
                with self.assertLogs('kratos_salome_plugin.gui.plugin_controller', level='INFO') as cm:
                    controller._SaveAs()
                    self.assertEqual(len(cm.output), 2)
                    self.assertEqual(cm.output[0], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saving project as ...')
                    self.assertEqual(cm.output[1], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saved project under "{}"'.format(project_dir))

                self.assertEqual(patch_fct_status_bar.call_count, 1)
                self.assertEqual(patch_fct.call_count, 1)
                self.assertTrue(project_dir.is_dir())
                num_files_after_first_save = len(listdir(project_dir))
                self.assertGreater(num_files_after_first_save, 0)

                self.assertEqual(controller._previous_save_path, project_dir)

                # calling it a second time should ask again for the save-path
                controller._SaveAs()
                self.assertEqual(patch_fct_status_bar.call_count, 2)
                self.assertEqual(patch_fct.call_count, 2)
                self.assertTrue(project_dir.is_dir())
                self.assertEqual(num_files_after_first_save, len(listdir(project_dir))) # make sure not more files are created

                self.assertEqual(controller._previous_save_path, project_dir)

    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    def test_SaveAs_aborted(self, mock_save_study, mock_version):
        project_dir = Path("controller_save_project_as_aborted.ksp")

        controller = PluginController()

        self.assertIsNone(controller._previous_save_path)

        with patch.object(controller._project_manager, 'SaveProject') as patch_fct_save_project:
            with patch.object(controller._main_window, 'StatusBarWarning') as patch_fct_status_bar:
                with patch(_QFileDialog_patch+'getSaveFileName', return_value=("",0)) as patch_fct:
                    with self.assertLogs('kratos_salome_plugin.gui.plugin_controller', level='INFO') as cm:
                        controller._SaveAs()
                        self.assertEqual(len(cm.output), 2)
                        self.assertEqual(cm.output[0], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saving project as ...')
                        self.assertEqual(cm.output[1], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saving was aborted')

                    self.assertEqual(patch_fct_save_project.call_count, 0)
                    self.assertEqual(patch_fct_status_bar.call_count, 1)
                    self.assertEqual(patch_fct.call_count, 1)
                    self.assertFalse(project_dir.is_dir())
                    self.assertIsNone(controller._previous_save_path)

    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    def test_SaveAs_failed(self, mock_save_study, mock_version):
        project_dir = Path("controller_save_project_as_failed.ksp")

        controller = PluginController()

        self.assertIsNone(controller._previous_save_path)

        with patch.object(controller._project_path_handler, 'GetSavePath', return_value=project_dir) as patch_fct_get_save_path:
            with patch.object(controller._project_manager, 'SaveProject', return_value=False) as patch_fct_save_proj:
                with self.assertLogs('kratos_salome_plugin.gui.plugin_controller', level='INFO') as cm:
                    controller._SaveAs()
                    self.assertEqual(len(cm.output), 2)
                    self.assertEqual(cm.output[0], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saving project as ...')
                    self.assertEqual(cm.output[1], 'CRITICAL:kratos_salome_plugin.gui.plugin_controller:Failed to save project under "{}"!'.format(project_dir))

                self.assertEqual(patch_fct_get_save_path.call_count, 1)
                self.assertEqual(patch_fct_save_proj.call_count, 1)
                self.assertFalse(project_dir.is_dir())
                self.assertIsNone(controller._previous_save_path)

    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    def test_Save_first_save(self, mock_save_study, mock_version):
        project_dir = Path("controller_save_project_first.ksp")

        self.addCleanup(lambda: DeleteDirectoryIfExisting(project_dir))
        DeleteDirectoryIfExisting(project_dir) # remove potential leftovers

        controller = PluginController()

        self.assertIsNone(controller._previous_save_path)

        with patch.object(controller._main_window, 'StatusBarInfo') as patch_fct_status_bar:
            with patch.object(controller._project_path_handler, 'GetSavePath', return_value=project_dir) as patch_fct:
                with self.assertLogs('kratos_salome_plugin.gui.plugin_controller', level='INFO') as cm:
                    controller._Save()
                    self.assertEqual(len(cm.output), 2)
                    self.assertEqual(cm.output[0], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saving project as ...')
                    self.assertEqual(cm.output[1], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saved project under "{}"'.format(project_dir))

                self.assertEqual(patch_fct_status_bar.call_count, 1)
                self.assertEqual(patch_fct.call_count, 1)
                self.assertTrue(project_dir.is_dir())
                num_files_after_first_save = len(listdir(project_dir))
                self.assertGreater(num_files_after_first_save, 0)

                self.assertEqual(controller._previous_save_path, project_dir)

                with self.assertLogs('kratos_salome_plugin.gui.plugin_controller', level='INFO') as cm:
                    controller._Save()
                    self.assertEqual(len(cm.output), 2)
                    self.assertEqual(cm.output[0], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saving project with previous save path ...')
                    self.assertEqual(cm.output[1], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saved project under "{}"'.format(project_dir))

                # calling Save a second time should not ask again for the save-path
                self.assertEqual(patch_fct_status_bar.call_count, 2)
                self.assertEqual(patch_fct.call_count, 1)
                self.assertTrue(project_dir.is_dir())
                self.assertEqual(num_files_after_first_save, len(listdir(project_dir))) # make sure not more files are created

                self.assertEqual(controller._previous_save_path, project_dir)

    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    def test_Save_second_save(self, mock_save_study, mock_version):
        project_dir = Path("controller_save_project_second.ksp")

        self.addCleanup(lambda: DeleteDirectoryIfExisting(project_dir))
        DeleteDirectoryIfExisting(project_dir) # remove potential leftovers

        controller = PluginController()

        controller._previous_save_path = project_dir

        with patch.object(controller._main_window, 'StatusBarInfo') as patch_fct_status_bar:
            with patch.object(controller._project_path_handler, 'GetSavePath', return_value=project_dir) as patch_fct:
                with self.assertLogs('kratos_salome_plugin.gui.plugin_controller', level='INFO') as cm:
                    controller._Save()
                    self.assertEqual(len(cm.output), 2)
                    self.assertEqual(cm.output[0], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saving project with previous save path ...')
                    self.assertEqual(cm.output[1], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saved project under "{}"'.format(project_dir))

                self.assertEqual(patch_fct_status_bar.call_count, 1)
                self.assertEqual(patch_fct.call_count, 0) # should not be called as previous save path is used
                self.assertTrue(project_dir.is_dir())

                self.assertEqual(controller._previous_save_path, project_dir)

    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    def test_Save_aborted(self, mock_save_study, mock_version):
        project_dir = Path("controller_save_project_aborted.ksp")

        controller = PluginController()

        self.assertIsNone(controller._previous_save_path)

        with patch.object(controller._project_manager, 'SaveProject') as patch_fct_save_project:
            with patch.object(controller._main_window, 'StatusBarWarning') as patch_fct_status_bar:
                with patch(_QFileDialog_patch+'getSaveFileName', return_value=("",0)) as patch_fct:
                    with self.assertLogs('kratos_salome_plugin.gui.plugin_controller', level='INFO') as cm:
                        controller._Save()
                        self.assertEqual(len(cm.output), 2)
                        self.assertEqual(cm.output[0], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saving project as ...')
                        self.assertEqual(cm.output[1], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saving was aborted')

                    self.assertEqual(patch_fct_save_project.call_count, 0)
                    self.assertEqual(patch_fct_status_bar.call_count, 1)
                    self.assertEqual(patch_fct.call_count, 1)
                    self.assertFalse(project_dir.is_dir())
                    self.assertIsNone(controller._previous_save_path)

    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    def test_Save_failed(self, mock_save_study, mock_version):
        project_dir = Path("controller_save_project_failed.ksp")

        controller = PluginController()

        controller._previous_save_path = project_dir

        with patch.object(controller._project_path_handler, 'GetSavePath', return_value=project_dir) as patch_fct_get_save_path:
            with patch.object(controller._project_manager, 'SaveProject', return_value=False) as patch_fct_save_proj:
                with self.assertLogs('kratos_salome_plugin.gui.plugin_controller', level='INFO') as cm:
                    controller._Save()
                    self.assertEqual(len(cm.output), 2)
                    self.assertEqual(cm.output[0], 'INFO:kratos_salome_plugin.gui.plugin_controller:Saving project with previous save path ...')
                    self.assertEqual(cm.output[1], 'CRITICAL:kratos_salome_plugin.gui.plugin_controller:Failed to save project under "{}"!'.format(project_dir))

                self.assertEqual(patch_fct_get_save_path.call_count, 0)
                self.assertEqual(patch_fct_save_proj.call_count, 1)
                self.assertFalse(project_dir.is_dir())
                self.assertEqual(controller._previous_save_path, project_dir)


    def test_Open(self):
        controller = PluginController()

        project_dir = Path("controller_open_project.ksp")

        with patch.object(controller._project_path_handler, 'GetOpenPath', return_value=project_dir) as patch_fct_get_open_path:
            with patch.object(controller._project_manager, 'OpenProject', return_value=True) as patch_fct_open_proj:
                with self.assertLogs('kratos_salome_plugin.gui.plugin_controller', level='INFO') as cm:
                    controller._Open()
                    self.assertEqual(len(cm.output), 1)
                    self.assertEqual(cm.output[0], 'INFO:kratos_salome_plugin.gui.plugin_controller:Successfully opened project from "{}"'.format(project_dir))

                self.assertEqual(patch_fct_get_open_path.call_count, 1)
                self.assertEqual(patch_fct_open_proj.call_count, 1)

    def test_Open_invalid_folder(self):
        controller = PluginController()

        with patch(_QFileDialog_patch+'getExistingDirectory', return_value=str("random_folder")) as patch_fct:
            with patch.object(controller._project_manager, 'OpenProject', return_value=True) as patch_fct_open_proj:
                with self.assertLogs('kratos_salome_plugin.gui.plugin_controller', level='INFO') as cm:
                    controller._Open()
                    self.assertEqual(len(cm.output), 1)
                    self.assertEqual(cm.output[0], 'WARNING:kratos_salome_plugin.gui.plugin_controller:User input error while opening project: Invalid project folder selected, must end with ".ksp"!')

                self.assertEqual(patch_fct.call_count, 1)
                self.assertEqual(patch_fct_open_proj.call_count, 0)

    def test_Open_aborted(self):
        controller = PluginController()

        with patch.object(controller._project_path_handler, 'GetOpenPath', return_value=Path(".")) as patch_fct_get_open_path:
            with patch.object(controller._project_manager, 'OpenProject', return_value=True) as patch_fct_open_proj:
                with self.assertLogs('kratos_salome_plugin.gui.plugin_controller', level='INFO') as cm:
                    controller._Open()
                    self.assertEqual(len(cm.output), 1)
                    self.assertEqual(cm.output[0], 'INFO:kratos_salome_plugin.gui.plugin_controller:Opening was aborted')

                self.assertEqual(patch_fct_get_open_path.call_count, 1)
                self.assertEqual(patch_fct_open_proj.call_count, 0)

    def test_Open_failed(self):
        controller = PluginController()

        project_dir = Path("controller_open_project_failed.ksp")

        with patch.object(controller._project_path_handler, 'GetOpenPath', return_value=project_dir) as patch_fct_get_open_path:
            with patch.object(controller._project_manager, 'OpenProject', return_value=False) as patch_fct_open_proj:
                with self.assertLogs('kratos_salome_plugin.gui.plugin_controller', level='INFO') as cm:
                    controller._Open()
                    self.assertEqual(len(cm.output), 1)
                    self.assertEqual(cm.output[0], 'CRITICAL:kratos_salome_plugin.gui.plugin_controller:Failed to open project from "{}"!'.format(project_dir))

                self.assertEqual(patch_fct_get_open_path.call_count, 1)
                self.assertEqual(patch_fct_open_proj.call_count, 1)


class PluginControllerIntegationTests(SalomeTestCaseWithBox):
    """these tests make sure the complete workflow is working"""
    def test_Save(self):
        project_dir = Path("controller_save_project_salome.ksp")
        self.__execute_test_save(project_dir)

    def test_SaveAndReOpen(self):
        # imported here due to patching issues
        from kratos_salome_plugin.salome_study_utilities import GetNumberOfObjectsInStudy, ResetStudy

        project_dir = Path("controller_save_open_project_salome.ksp")

        initial_num_objs = GetNumberOfObjectsInStudy()

        self.__execute_test_save(project_dir)

        ResetStudy()

        controller = PluginController()

        with patch.object(controller._project_path_handler, 'GetOpenPath', return_value=project_dir) as patch_fct:
            controller._Open()

            self.assertEqual(GetNumberOfObjectsInStudy(), initial_num_objs)

    def __execute_test_save(self, project_dir):
        self.addCleanup(lambda: DeleteDirectoryIfExisting(project_dir))
        DeleteDirectoryIfExisting(project_dir) # remove potential leftovers

        controller = PluginController()

        with patch.object(controller._project_path_handler, 'GetSavePath', return_value=project_dir) as patch_fct:
            controller._Save()
            self.assertTrue(project_dir.is_dir())
            self.assertGreater(len(listdir(project_dir)), 0) # make sure sth was created



if __name__ == '__main__':
    unittest.main()
