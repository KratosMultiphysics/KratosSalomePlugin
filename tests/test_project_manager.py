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
from shutil import rmtree
import unittest
from unittest.mock import patch

# plugin imports
from kratos_salome_plugin.gui.project_manager import ProjectManager
from kratos_salome_plugin.utilities import IsExecutedInSalome

# tests imports
from testing_utilities import QtTestCase, GetTestsDir

# helper functions
def CreateHDFStudyFile(file_name, *ignored_args):
    # ignoring arguments for multifile and mode (ascii or binary)
    if not file_name.endswith(".hdf"):
        file_name+=".hdf"
    with open(file_name, "w"): pass # "touch" to create empty file

    return True

def DeleteDirectoryIfExisting(directory_name):
    if os.path.isdir(directory_name):
        rmtree(directory_name)



class TestProjectManager(QtTestCase):

    @patch('salome_version.getVersions', return_value=[1,2,3])
    @patch('salome.myStudy.SaveAs', side_effect=CreateHDFStudyFile)
    def test_SaveProject_mocked_salome(self, mock_version, mock_save_study):
        self.__execute_test_SaveProject()

        self.assertTrue(mock_version.called)
        self.assertEqual(mock_version.call_count, 1)

        self.assertTrue(mock_save_study.called)
        self.assertEqual(mock_save_study.call_count, 1)

    @unittest.skipUnless(IsExecutedInSalome(), "Test requires Salome!")
    def test_SaveProject_real_salome(self):
        self.__execute_test_SaveProject()

    # test also with pre-existing directory that has some stuff in it
    # => the pre-existing stuff should not be changed! (e.g. can be Kratos stuffs)
    # the plugin stuffs should be changed though, e.g. "plugin_data.json"


    def test_OpenProject(self):
        manager = ProjectManager()

    def test_ResetProject(self):
        manager = ProjectManager()
        manager.ResetProject()


    def __execute_test_SaveProject(self):
        save_dir = os.path.join(GetTestsDir(), "my_own_project")
        project_dir = save_dir+".ksp"

        self.addCleanup(lambda: DeleteDirectoryIfExisting(project_dir))

        manager = ProjectManager()

        manager.SaveProject(save_dir)

        # check the files were created
        self.assertTrue(os.path.isdir(project_dir))
        self.assertTrue(os.path.isfile(os.path.join(project_dir, "plugin_data.json")))
        self.assertTrue(os.path.isfile(os.path.join(project_dir, "salome_study.hdf")))

        # check content of "plugin_data.json"
        # ... TODO implement


if __name__ == '__main__':
    unittest.main()
