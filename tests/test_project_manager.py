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
import os
import json
from shutil import rmtree
import unittest
from unittest.mock import patch

# plugin imports
from kratos_salome_plugin import IsExecutedInSalome
from kratos_salome_plugin.gui.project_manager import ProjectManager

# tests imports
from testing_utilities import QtTestCase, GetTestsDir, DeleteDirectoryIfExisting_OLD

# helper functions
def CreateHDFStudyFile(file_name, *ignored_args):
    # ignoring arguments for multifile and mode (ascii or binary)
    if not file_name.endswith(".hdf"):
        file_name+=".hdf"
    with open(file_name, "w"): pass # "touch" to create empty file
    return True

def CreateFile(file_name):
    with open(file_name, "w"): pass # "touch" to create empty file


class TestProjectManager(QtTestCase):

    # I don't think I need the QtTestCase for the Save - tests
    # => only when creating a dialog I guess (i.e. for unsaved changes when opening / resetting)
    # tests could be done with mocking the dialog (i.e. with and without Qt available, same as for salome)

    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    def test_SaveProject_mocked_salome(self, mock_save_study, mock_version):
        self.__execute_test_SaveProject()

        self.assertTrue(mock_version.called)
        self.assertEqual(mock_version.call_count, 1)

        self.assertTrue(mock_save_study.called)
        self.assertEqual(mock_save_study.call_count, 1)

    @unittest.skipUnless(IsExecutedInSalome(), "Test requires Salome!")
    def test_SaveProject_real_salome(self):
        self.__execute_test_SaveProject()

    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    def test_SaveProject_existing_folder(self, mock_save_study, mock_version):
        """this test makes sure that no unrelated files are changed/overwritten"""
        project_name = "project_with_kratos"
        save_dir = os.path.join(GetTestsDir(), project_name)
        project_dir = save_dir+".ksp"

        DeleteDirectoryIfExisting_OLD(project_dir)
        os.makedirs(project_dir)

        CreateFile(os.path.join(project_dir, "MainKratos.py"))

        self.__execute_test_SaveProject(project_name)

        self.assertTrue(mock_version.called)
        self.assertEqual(mock_version.call_count, 1)

        self.assertTrue(mock_save_study.called)
        self.assertEqual(mock_save_study.call_count, 1)

        # make sure the previously existing file wasn't deleted aka the folder wasn't removed and recreated
        self.assertTrue(os.path.isfile(os.path.join(project_dir, "MainKratos.py")))

    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    @patch('salome.myStudy.Open', return_value=True)
    @patch('kratos_salome_plugin.salome_study_utilities.GetNumberOfObjectsInStudy', return_value=0)
    def test_OpenProject(self, mock_num_objs_study, mock_open_study, mock_save_study, mock_version):
        manager = ProjectManager()

        # first save the project
        project_name = "project_for_opening"
        self.__execute_test_SaveProject(project_name)
        project_dir = os.path.join(GetTestsDir(), project_name+".ksp")

        # then open it again and check if is is the same
        manager.OpenProject(project_dir)
        # TODO implement checks (GroupsManager and App should be checked)

    def test_ResetProject(self):
        manager = ProjectManager()
        manager.ResetProject()

        self.assertIsNone(manager.application)
        # TODO check also the GroupsManager once implemented


    def __execute_test_SaveProject(self, project_name="my_own_project"):
        save_dir = os.path.join(GetTestsDir(), project_name)
        project_dir = save_dir+".ksp"

        self.addCleanup(lambda: DeleteDirectoryIfExisting_OLD(project_dir))

        manager = ProjectManager()

        manager.SaveProject(save_dir)

        # check the files were created
        self.assertTrue(os.path.isdir(project_dir))
        self.assertTrue(os.path.isfile(os.path.join(project_dir, "plugin_data.json")))
        self.assertTrue(os.path.isfile(os.path.join(project_dir, "salome_study.hdf")))

        # check content of "plugin_data.json"
        with open(os.path.join(project_dir, "plugin_data.json"), 'r') as plugin_data_file:
            plugin_data = json.load(plugin_data_file)

        self.assertIn("general", plugin_data)
        self.assertIn("groups", plugin_data)
        self.assertNotIn("application", plugin_data) # no app was loaded hence this shouldn't exist

        general = plugin_data["general"]
        self.assertIn("version_plugin", general)
        self.assertIn("version_salome", general)
        self.assertIn("creation_time", general)
        self.assertIn("operating_system", general)


if __name__ == '__main__':
    unittest.main()
