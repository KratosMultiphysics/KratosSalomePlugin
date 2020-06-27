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
import unittest
from unittest.mock import patch

# plugin imports
from kratos_salome_plugin.gui.project_path_handler import ProjectPathHandler

# using a module local patch due to import of QFileDialog in project_path_handler
# see https://realpython.com/python-mock-library/#where-to-patch
_QFileDialog_patch = 'kratos_salome_plugin.gui.project_path_handler.QFileDialog.'

class TestProjectPathHandler(unittest.TestCase):
    """At the moment of this writing QtTest didn't provide functionalities to test
    - getExistingDirectory
    - getSaveFileName
    hence those are patched using mocks
    see
    """
    def test_GetOpenPath(self):
        path_handler = ProjectPathHandler()

        patch_path_dir = os.path.join("some", "direc", "to")
        patch_path = os.path.join(patch_path_dir, "project.ksp")

        with patch(_QFileDialog_patch+'getExistingDirectory', return_value=patch_path) as patch_fct:
            path = path_handler.GetOpenPath()
            self.assertTrue(patch_fct.called)
            self.assertEqual(patch_fct.call_count, 1)

        self.assertEqual(path, patch_path)
        self.assertEqual(path_handler.last_path, patch_path_dir)

        # the second call should use the previous dir as starting point
        patch_path_2 = os.path.join("another", "proj", "dir", "project.ksp")
        with patch(_QFileDialog_patch+'getExistingDirectory', return_value=patch_path_2) as patch_fct:
            path_handler.GetOpenPath()
            self.assertTrue(patch_fct.called)
            self.assertEqual(patch_fct.call_count, 1)
            self.assertEqual(patch_fct.call_args_list[0][0][2], patch_path_dir)

    def test_GetOpenPath_invalid_input(self):
        # this test might become obligatory if it is possible to figure out a way
        # to only use folders with ".ksp" extension (like is possible for files)
        with patch(_QFileDialog_patch+'getExistingDirectory', return_value="random_folder"):
            with self.assertRaisesRegex(Exception, 'Invalid project folder selected, must end with ".ksp"!'):
                path = ProjectPathHandler().GetOpenPath()

    def test_GetSavePath(self):
        path_handler = ProjectPathHandler()

        patch_path_dir = os.path.join("some", "direc", "to")
        patch_path = os.path.join(patch_path_dir, "my_project")

        with patch(_QFileDialog_patch+'getSaveFileName', return_value=(patch_path,0)) as patch_fct:
            path = path_handler.GetSavePath()
            self.assertTrue(patch_fct.called)
            self.assertEqual(patch_fct.call_count, 1)

        self.assertEqual(path, patch_path+".ksp")
        self.assertEqual(path_handler.last_path, patch_path_dir)

        # the second call should use the previous dir as starting point
        patch_path_2 = os.path.join("another", "proj", "dir", "dummy_proj")
        with patch(_QFileDialog_patch+'getSaveFileName', return_value=(patch_path_2,0)) as patch_fct:
            path_handler.GetSavePath()
            self.assertTrue(patch_fct.called)
            self.assertEqual(patch_fct.call_count, 1)
            self.assertEqual(patch_fct.call_args_list[0][0][2], patch_path_dir)


if __name__ == '__main__':
    unittest.main()
