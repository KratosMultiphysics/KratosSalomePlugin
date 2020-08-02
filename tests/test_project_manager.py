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
from os import makedirs
import json
from shutil import rmtree
import unittest
from unittest.mock import patch

# plugin imports
from kratos_salome_plugin import IsExecutedInSalome
from kratos_salome_plugin.gui.project_manager import ProjectManager

# tests imports
from testing_utilities import QtTestCase, DeleteDirectoryIfExisting, skipUnlessPythonVersionIsAtLeast, CreateHDFStudyFile, SalomeTestCaseWithBox


@skipUnlessPythonVersionIsAtLeast((3,6), 'pathlib.Path does not work with some fcts before 3.6 (e.g. "with open" or "os.makedirs")')
class TestProjectManager(QtTestCase):

    # I don't think I need the QtTestCase for the Save - tests
    # => only when creating a dialog I guess (i.e. for unsaved changes when opening / resetting)
    # tests could be done with mocking the dialog (i.e. with and without Qt available, same as for salome)

    def test_SaveProject_empty_input(self):
        with self.assertRaisesRegex(NameError, 'Path cannot be empty!'):
            ProjectManager().SaveProject(Path())

    def test_SaveProject_string(self):
        with self.assertRaisesRegex(TypeError, 'Path must be a "pathlib.Path" object!'):
            ProjectManager().SaveProject("save_study_name")

    def test_OpenProject_empty_input(self):
        with self.assertRaisesRegex(NameError, 'Path cannot be empty!'):
            ProjectManager().OpenProject(Path())

    def test_OpenProject_string(self):
        with self.assertRaisesRegex(TypeError, 'Path must be a "pathlib.Path" object!'):
            ProjectManager().OpenProject("open_study_name")

    def test_OpenProject_non_existing_folder(self):
        with self.assertRaisesRegex(NotADirectoryError, 'Attempting to open project "some_completely_random_non_existin_path" failed, it does not exist!'):
            ProjectManager().OpenProject(Path("some_completely_random_non_existin_path"))

    def test_OpenProject_non_existing_study_file(self):
        project_dir = Path(self._testMethodName).with_suffix(".ksp")

        self.addCleanup(lambda: DeleteDirectoryIfExisting(project_dir))

        DeleteDirectoryIfExisting(project_dir)
        makedirs(project_dir)

        with self.assertRaisesRegex(FileNotFoundError, 'Salome study does not exist in project "test_OpenProject_non_existing_study_file.ksp"'):
            ProjectManager().OpenProject(project_dir)

    def test_OpenProject_non_existing_plugin_data(self):
        project_dir = Path(self._testMethodName).with_suffix(".ksp")

        self.addCleanup(lambda: DeleteDirectoryIfExisting(project_dir))

        DeleteDirectoryIfExisting(project_dir)
        makedirs(project_dir)

        salome_study_path = project_dir / "salome_study.hdf"
        salome_study_path.touch()

        with self.assertRaisesRegex(FileNotFoundError, 'Plugin data file does not exist in project "test_OpenProject_non_existing_plugin_data.ksp"'):
            ProjectManager().OpenProject(project_dir)

    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    def test_SaveProject_mocked_salome(self, mock_save_study, mock_version):
        _ExecuteTestSaveProject(self)

        self.assertTrue(mock_version.called)
        self.assertEqual(mock_version.call_count, 1)

        self.assertTrue(mock_save_study.called)
        self.assertEqual(mock_save_study.call_count, 1)

    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    def test_SaveProject_existing_folder(self, mock_save_study, mock_version):
        """this test makes sure that no unrelated files are changed/overwritten"""
        project_name = Path("project_with_kratos")
        project_dir = project_name.with_suffix(".ksp")

        DeleteDirectoryIfExisting(project_dir)
        makedirs(project_dir)

        main_kratos_py_path = project_dir / "MainKratos.py"
        proj_params_json_path = project_dir / "ProjectParameters.json"

        plugin_data_path = project_dir / "plugin_data.json"
        salome_study_path = project_dir / "salome_study.hdf"

        main_kratos_py_path.touch()
        proj_params_json_path.touch()

        _ExecuteTestSaveProject(self, project_name)

        self.assertTrue(mock_version.called)
        self.assertEqual(mock_version.call_count, 1)

        self.assertTrue(mock_save_study.called)
        self.assertEqual(mock_save_study.call_count, 1)

        # make sure the previously existing file wasn't deleted aka the folder wasn't removed and recreated
        self.assertTrue(main_kratos_py_path.is_file())
        self.assertTrue(proj_params_json_path.is_file())
        self.assertTrue(plugin_data_path.is_file())
        self.assertTrue(salome_study_path.is_file())

    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    @patch('salome.myStudy.Open', return_value=True)
    @patch('kratos_salome_plugin.salome_study_utilities.GetNumberOfObjectsInStudy', return_value=0)
    def test_SaveAndReOpenProject_mocked_salome(self, mock_num_objs_study, mock_open_study, mock_save_study, mock_version):
        _ExecuteTestSaveAndOpenProject(self)


class TestProjectManagerWithSalome(SalomeTestCaseWithBox):
    def test_SaveProject(self):
        _ExecuteTestSaveProject(self)

    def test_SaveAndReOpenProject(self):
        _ExecuteTestSaveAndOpenProject(self)


def _ExecuteTestSaveProject(test_case, project_name=None):
    if not project_name:
        project_name = Path(test_case._testMethodName)

    project_dir = project_name.with_suffix(".ksp")

    test_case.addCleanup(lambda: DeleteDirectoryIfExisting(project_dir))

    manager = ProjectManager()

    test_case.assertTrue(manager.SaveProject(project_name))

    plugin_data_path = project_dir / "plugin_data.json"

    # check the files were created
    test_case.assertTrue(project_dir.is_dir())
    test_case.assertTrue(plugin_data_path.is_file())
    test_case.assertTrue(project_dir.joinpath("salome_study.hdf").is_file())

    # check content of "plugin_data.json"
    with open(plugin_data_path, 'r') as plugin_data_file:
        plugin_data = json.load(plugin_data_file)

    test_case.assertIn("general", plugin_data)
    test_case.assertIn("groups", plugin_data)
    test_case.assertNotIn("application", plugin_data) # no app was loaded hence this shouldn't exist

    general = plugin_data["general"]
    test_case.assertIn("version_plugin", general)
    test_case.assertIn("version_salome", general)
    test_case.assertIn("creation_time", general)
    test_case.assertIn("operating_system", general)

    return project_name

def _ExecuteTestSaveAndOpenProject(test_case, project_name=None):
    # imported here due to patching issues
    from kratos_salome_plugin.salome_study_utilities import GetNumberOfObjectsInStudy, ResetStudy

    manager = ProjectManager()

    # first save the project
    project_name = _ExecuteTestSaveProject(test_case)
    project_dir = project_name.with_suffix(".ksp")

    initial_num_objs = GetNumberOfObjectsInStudy()

    ResetStudy()

    # then open it again and check if is is the same
    test_case.assertTrue(manager.OpenProject(project_dir))

    test_case.assertEqual(initial_num_objs, GetNumberOfObjectsInStudy())
    # TODO implement checks (GroupsManager and App should be checked)


if __name__ == '__main__':
    unittest.main()
