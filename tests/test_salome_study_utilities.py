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
import os
import unittest
from unittest.mock import patch

# plugin imports
from kratos_salome_plugin import salome_study_utilities

# tests imports
from testing_utilities import SalomeTestCase, SalomeTestCaseWithBox, GetTestsPath, DeleteDirectoryIfExisting, DeleteFileIfExisting, DeleteDirectoryIfExisting_OLD

# salome imports
import salome


class TestSalomeTestCaseStudyCleaning(SalomeTestCase):
    """test to make sure that the cleaning of studies between tests works correctly"""

    # the order of execution is not deterministic, hence we need a flag
    already_executed = False
    num_objs_in_study = None

    def setUp(self):
        super().setUp()

        # create geometry
        O = self.geompy.MakeVertex(0, 0, 0)
        OX = self.geompy.MakeVectorDXDYDZ(1, 0, 0)
        OY = self.geompy.MakeVectorDXDYDZ(0, 1, 0)
        OZ = self.geompy.MakeVectorDXDYDZ(0, 0, 1)
        Box_1 = self.geompy.MakeBoxDXDYDZ(200, 200, 200)
        self.geompy.addToStudy( O, 'O' )
        self.geompy.addToStudy( OX, 'OX' )
        self.geompy.addToStudy( OY, 'OY' )
        self.geompy.addToStudy( OZ, 'OZ' )
        self.geompy.addToStudy( Box_1, 'Box_1' )

        # create mesh
        from salome.smesh import smeshBuilder
        Mesh_1 = self.smesh.Mesh(Box_1)
        Regular_1D = Mesh_1.Segment()
        Max_Size_1 = Regular_1D.MaxSize(34.641)
        MEFISTO_2D = Mesh_1.Triangle(algo=smeshBuilder.MEFISTO)
        NETGEN_3D = Mesh_1.Tetrahedron()
        isDone = Mesh_1.Compute()

        ## Set names of Mesh objects
        self.smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
        self.smesh.SetName(NETGEN_3D.GetAlgorithm(), 'NETGEN 3D')
        self.smesh.SetName(MEFISTO_2D.GetAlgorithm(), 'MEFISTO_2D')
        self.smesh.SetName(Max_Size_1, 'Max Size_1')
        self.smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')

    def test_1(self):
        self.__CheckStudy()

    def test_2(self):
        self.__CheckStudy()

    def __CheckStudy(self):
        if TestSalomeTestCaseStudyCleaning.already_executed:
            # make sure the number of components is the same!
            current_num_objs_in_study = salome_study_utilities.GetNumberOfObjectsInStudy()
            # if this check fails it means that the study was not cleaned, leftover objects exist!
            self.assertEqual(current_num_objs_in_study, TestSalomeTestCaseStudyCleaning.num_objs_in_study)
        else:
            TestSalomeTestCaseStudyCleaning.already_executed = True
            # if executed for the first time then count the components
            TestSalomeTestCaseStudyCleaning.num_objs_in_study = salome_study_utilities.GetNumberOfObjectsInStudy()


class TestSalomeStudyUtilities(SalomeTestCaseWithBox):

    def test_GetNumberOfObjectsInComponent(self):
        num_components = 0
        num_objs_in_comp = []

        itcomp = salome.myStudy.NewComponentIterator()
        while itcomp.More(): # loop components (e.g. GEOM, SMESH)
            num_components += 1
            component = itcomp.Value()
            num_objs_in_comp.append(salome_study_utilities.GetNumberOfObjectsInComponent(component))
            itcomp.Next()

        self.assertEqual(num_components, 2)
        self.assertListEqual(num_objs_in_comp, [13,67])

    def test_GetNumberOfObjectsInStudy(self):
        self.assertEqual(salome_study_utilities.GetNumberOfObjectsInStudy(), 80)
        salome_study_utilities.ResetStudy()
        self.assertEqual(salome_study_utilities.GetNumberOfObjectsInStudy(), 0)

    def test_SaveStudy(self):
        file_path = Path("my_study_saved.hdf")

        self.addCleanup(lambda: DeleteFileIfExisting(file_path))
        DeleteFileIfExisting(file_path) # remove potential leftovers

        with self.assertLogs('kratos_salome_plugin.salome_study_utilities', level='DEBUG') as cm:
            save_successful = salome_study_utilities.SaveStudy(file_path)
            self.assertEqual(len(cm.output), 1)
            self.assertEqual(cm.output[0], 'INFO:kratos_salome_plugin.salome_study_utilities:Study was saved with path: "{}"'.format(file_path))

        self.assertTrue(save_successful)
        self.assertTrue(file_path.is_file())

    def test_SaveStudy_empty_input(self):
        with self.assertRaisesRegex(NameError, '"file_path" cannot be empty!'):
            salome_study_utilities.SaveStudy(Path())

    def test_SaveStudy_string(self):
        with self.assertRaisesRegex(TypeError, '"file_path" must be a "pathlib.Path" object!'):
            salome_study_utilities.SaveStudy("save_study_name")

    def test_SaveStudy_without_suffix(self):
        file_path = Path("my_study_saved_without_suffix")
        file_path_with_suffix = file_path.with_suffix(".hdf")

        self.addCleanup(lambda: DeleteFileIfExisting(file_path_with_suffix))
        DeleteFileIfExisting(file_path_with_suffix) # remove potential leftovers

        save_successful = salome_study_utilities.SaveStudy(file_path)

        self.assertTrue(save_successful)
        self.assertTrue(file_path_with_suffix.is_file())

    def test_SaveStudy_fake_failure(self):
        file_path = Path("my_study_saved_faked_failure.hdf")

        with patch('salome.myStudy.SaveAs', return_value=False):
            with self.assertLogs('kratos_salome_plugin.salome_study_utilities', level='DEBUG') as cm:
                salome_study_utilities.SaveStudy(file_path)
                self.assertEqual(len(cm.output), 1)
                self.assertEqual(cm.output[0], 'CRITICAL:kratos_salome_plugin.salome_study_utilities:Study could not be saved with path: "{}"'.format(file_path))

    def test_SaveStudy_overwrite_info(self):
        file_path = Path("my_study_saved_overwrite.hdf")
        self.addCleanup(lambda: DeleteFileIfExisting(file_path))
        DeleteFileIfExisting(file_path) # remove potential leftovers
        file_path.touch() # this creates the file that is overwritten

        with self.assertLogs('kratos_salome_plugin.salome_study_utilities', level='DEBUG') as cm:
            save_successful = salome_study_utilities.SaveStudy(file_path)
            self.assertEqual(len(cm.output), 2)
            self.assertEqual(cm.output[0], 'INFO:kratos_salome_plugin.salome_study_utilities:File "{}" exists already and will be overwritten'.format(file_path))
            self.assertEqual(cm.output[1], 'INFO:kratos_salome_plugin.salome_study_utilities:Study was saved with path: "{}"'.format(file_path))

        self.assertTrue(save_successful)
        self.assertTrue(file_path.is_file())


    def test_SaveStudy_in_folder(self):
        self.__execute_test_save_study_in_folder()

    def test_SaveStudy_in_sub_folder(self):
        parent_save_folder_path = GetTestsPath() / "test_SaveStudy_sub_folder"
        save_folder_path = parent_save_folder_path / "some_subfolder" / "actual_save_folder"

        self.addCleanup(lambda: DeleteDirectoryIfExisting(parent_save_folder_path))

        # cleaning potential leftovers
        DeleteDirectoryIfExisting(parent_save_folder_path)

        # Note: ".hdf" extension is added automatically and folder to be saved in is created
        file_name_full_path = save_folder_path / "my_study_test_save"
        save_successful = salome_study_utilities.SaveStudy(file_name_full_path)
        self.assertTrue(save_successful)

        self.assertTrue(save_folder_path.is_dir()) # make sure folder was created
        self.assertFalse(file_name_full_path.is_file())
        self.assertTrue(file_name_full_path.with_suffix(".hdf").is_file())
        self.assertEqual(len(os.listdir(save_folder_path)), 1) # make sure only one file was created

    def test_SaveStudy_in_existing_folder(self):
        save_folder_path = GetTestsPath() / "test_SaveStudy_existing_folder"

        self.addCleanup(lambda: DeleteDirectoryIfExisting(save_folder_path))

        # cleaning potential leftovers
        DeleteDirectoryIfExisting(save_folder_path)

        os.makedirs(save_folder_path)

        # Note: ".hdf" extension is added automatically and folder to be saved in is created
        file_name_full_path = save_folder_path / "my_study_test_save"
        save_successful = salome_study_utilities.SaveStudy(file_name_full_path)
        self.assertTrue(save_successful)

        self.assertTrue(save_folder_path.is_dir()) # make sure folder was created
        self.assertFalse(file_name_full_path.is_file())
        self.assertTrue(file_name_full_path.with_suffix(".hdf").is_file())
        self.assertEqual(len(os.listdir(save_folder_path)), 1) # make sure only one file was created

    def test_SaveStudy_in_existing_sub_folder(self):
        parent_save_folder_path = GetTestsPath() / "test_SaveStudy_existing_sub_folder"
        save_folder_path = parent_save_folder_path / "some_subfolder" / "actual_save_folder"

        self.addCleanup(lambda: DeleteDirectoryIfExisting(parent_save_folder_path))

        # cleaning potential leftovers
        DeleteDirectoryIfExisting(parent_save_folder_path)

        os.makedirs(save_folder_path)

        # Note: ".hdf" extension is added automatically and folder to be saved in is created
        file_name_full_path = save_folder_path / "my_study_test_save"
        save_successful = salome_study_utilities.SaveStudy(file_name_full_path)
        self.assertTrue(save_successful)

        self.assertTrue(save_folder_path.is_dir()) # make sure folder was created
        self.assertFalse(file_name_full_path.is_file())
        self.assertTrue(file_name_full_path.with_suffix(".hdf").is_file())
        self.assertEqual(len(os.listdir(save_folder_path)), 1) # make sure only one file was created

    def test_SaveStudy_in_partially_existing_sub_folder(self):
        parent_save_folder_path = GetTestsPath() / "test_SaveStudy_partially_existing_sub_folder"
        partial_folder_path = parent_save_folder_path / "some_subfolder"
        save_folder_path = partial_folder_path / "actual_save_folder"

        self.addCleanup(lambda: DeleteDirectoryIfExisting(parent_save_folder_path))

        # cleaning potential leftovers
        DeleteDirectoryIfExisting(parent_save_folder_path)

        os.makedirs(partial_folder_path)

        # Note: ".hdf" extension is added automatically and folder to be saved in is created
        file_name_full_path = save_folder_path / "my_study_test_save"
        save_successful = salome_study_utilities.SaveStudy(file_name_full_path)
        self.assertTrue(save_successful)

        self.assertTrue(save_folder_path.is_dir()) # make sure folder was created
        self.assertFalse(file_name_full_path.is_file())
        self.assertTrue(file_name_full_path.with_suffix(".hdf").is_file())
        self.assertEqual(len(os.listdir(save_folder_path)), 1) # make sure only one file was created

    def test_SaveStudy_exception(self):
        def SaveAs_raising(*args):
            raise Exception("random error")

        file_path = Path("my_empty_invaid_study_file.hdf")

        with patch('salome.myStudy.SaveAs', side_effect=SaveAs_raising):
            with self.assertLogs('kratos_salome_plugin.salome_study_utilities', level='ERROR') as cm:
                salome_study_utilities.SaveStudy(file_path)
                self.assertEqual(len(cm.output), 2)
                self.assertIn('ERROR:kratos_salome_plugin.salome_study_utilities:Exception when saving study:', cm.output[0])
                self.assertEqual(cm.output[1], 'CRITICAL:kratos_salome_plugin.salome_study_utilities:Study could not be saved with path: "{}"'.format(file_path))

    def test_OpenStudy_empty_input(self):
        with self.assertRaisesRegex(NameError, '"file_path" cannot be empty!'):
            salome_study_utilities.OpenStudy(Path())

    def test_OpenStudy_string(self):
        with self.assertRaisesRegex(TypeError, '"file_path" must be a "pathlib.Path" object!'):
            salome_study_utilities.OpenStudy("open_study_name")

    def test_OpenStudy_non_existing(self):
        with self.assertRaisesRegex(FileNotFoundError, 'File "some_completely_random_non_existin_path" does not exist!'):
            salome_study_utilities.OpenStudy(Path("some_completely_random_non_existin_path"))

    @patch('salome.myStudy.Open', return_value=True)
    @patch('kratos_salome_plugin.salome_study_utilities.IsStudyModified', return_value=False)
    @patch('kratos_salome_plugin.salome_study_utilities.GetNumberOfObjectsInStudy', return_value=0)
    def test_OpenStudy_warning_logs_wrong_suffix(self, mock_num_objs_study, mock_is_modified, mock_open_study):
        file_path = Path("without_suffix")
        self.addCleanup(lambda: DeleteFileIfExisting(file_path))
        file_path.touch()

        with self.assertLogs('kratos_salome_plugin.salome_study_utilities', level='WARNING') as cm:
            salome_study_utilities.OpenStudy(file_path)
            self.assertEqual(len(cm.output), 1)
            self.assertEqual(cm.output[0], 'WARNING:kratos_salome_plugin.salome_study_utilities:Opening study from file without ".hdf" extension: "{}"'.format(file_path))

    @patch('salome.myStudy.Open', return_value=True)
    @patch('kratos_salome_plugin.salome_study_utilities.IsStudyModified', return_value=True)
    @patch('kratos_salome_plugin.salome_study_utilities.GetNumberOfObjectsInStudy', return_value=3)
    def test_OpenStudy_warning_logs_modified_study(self, mock_num_objs_study, mock_is_modified, mock_open_study):
        file_path = Path("my_study_file.hdf")
        self.addCleanup(lambda: DeleteFileIfExisting(file_path))
        file_path.touch()

        with self.assertLogs('kratos_salome_plugin.salome_study_utilities', level='WARNING') as cm:
            salome_study_utilities.OpenStudy(file_path)
            self.assertEqual(len(cm.output), 1)
            self.assertEqual(cm.output[0], 'WARNING:kratos_salome_plugin.salome_study_utilities:Opening study when current study has unsaved changes')

    @patch('salome.myStudy.Open', return_value=True)
    @patch('kratos_salome_plugin.salome_study_utilities.IsStudyModified', return_value=True)
    @patch('kratos_salome_plugin.salome_study_utilities.GetNumberOfObjectsInStudy', return_value=0)
    def test_OpenStudy_warning_logs_modified_but_empty_study(self, mock_num_objs_study, mock_is_modified, mock_open_study):
        # if the study is modified but empty it should not give the warning
        file_path = Path("my_empty_study_file.hdf")
        self.addCleanup(lambda: DeleteFileIfExisting(file_path))
        file_path.touch()

        with self.assertLogs('kratos_salome_plugin.salome_study_utilities', level='INFO') as cm:
            salome_study_utilities.OpenStudy(file_path)
            self.assertEqual(len(cm.output), 1)
            self.assertEqual(cm.output[0], 'INFO:kratos_salome_plugin.salome_study_utilities:Study was openend from path: "{}"'.format(file_path))


    def test_OpenStudy_fake_failure(self):
        file_path = Path("my_study_open_faked_failure.hdf")
        self.addCleanup(lambda: DeleteFileIfExisting(file_path))
        file_path.touch()

        with patch('salome.myStudy.Open', return_value=False):
            with self.assertLogs('kratos_salome_plugin.salome_study_utilities', level='CRITICAL') as cm:
                salome_study_utilities.OpenStudy(file_path)
                self.assertEqual(len(cm.output), 1)
                self.assertEqual(cm.output[0], 'CRITICAL:kratos_salome_plugin.salome_study_utilities:Study could not be opened from path: "{}"'.format(file_path))

    def test_OpenStudy(self):
        num_objs_in_study = salome_study_utilities.GetNumberOfObjectsInStudy()

        # this creates the study file
        study_file_name = self.__execute_test_save_study_in_folder()

        salome_study_utilities.ResetStudy()

        self.assertTrue(salome_study_utilities.OpenStudy(study_file_name))

        self.assertEqual(num_objs_in_study, salome_study_utilities.GetNumberOfObjectsInStudy(), msg="Number of objects in study has changed!")

    def test_OpenStudy_exception(self):
        file_path = Path("my_empty_invaid_study_file.hdf")
        self.addCleanup(lambda: DeleteFileIfExisting(file_path))
        file_path.touch() # this is of course no vaild study_file

        with self.assertLogs('kratos_salome_plugin.salome_study_utilities', level='ERROR') as cm:
            salome_study_utilities.OpenStudy(file_path)
            self.assertEqual(len(cm.output), 2)
            self.assertIn('ERROR:kratos_salome_plugin.salome_study_utilities:Exception when opening study:', cm.output[0])
            self.assertEqual(cm.output[1], 'CRITICAL:kratos_salome_plugin.salome_study_utilities:Study could not be opened from path: "{}"'.format(file_path))

    def test_ResetStudy(self):
        self.assertGreater(salome_study_utilities.GetNumberOfObjectsInStudy(), 0)
        salome_study_utilities.ResetStudy()
        self.assertEqual(salome_study_utilities.GetNumberOfObjectsInStudy(), 0)

    def test_IsStudyModified(self):
        # the test-study was never saved hence it should be modified
        prop = self.study.GetProperties()
        self.assertTrue(prop.IsModified())
        self.assertTrue(salome_study_utilities.IsStudyModified())

        # now save the study
        file_path = Path("my_study_saved_is_modified.hdf")

        self.addCleanup(lambda: DeleteFileIfExisting(file_path))

        save_successful = salome_study_utilities.SaveStudy(file_path)

        self.assertTrue(save_successful)
        self.assertFalse(prop.IsModified()) # after saving this should return false
        self.assertFalse(salome_study_utilities.IsStudyModified()) # after saving this should return false


    def __execute_test_save_study_in_folder(self):
        save_folder_path = GetTestsPath() / "test_SaveStudy_folder"

        self.addCleanup(lambda: DeleteDirectoryIfExisting(save_folder_path))

        # cleaning potential leftovers
        DeleteDirectoryIfExisting(save_folder_path)

        # Note: ".hdf" extension is added automatically and folder to be saved in is created
        file_name_full_path = save_folder_path / "my_study_test_save"
        save_successful = salome_study_utilities.SaveStudy(file_name_full_path)
        self.assertTrue(save_successful)

        self.assertTrue(save_folder_path.is_dir()) # make sure folder was created
        self.assertFalse(file_name_full_path.is_file())
        self.assertTrue(file_name_full_path.with_suffix(".hdf").is_file())
        self.assertEqual(len(os.listdir(save_folder_path)), 1) # make sure only one file was created

        return file_name_full_path.with_suffix(".hdf")


if __name__ == '__main__':
    unittest.main()
