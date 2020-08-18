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
from kratos_salome_plugin import salome_gui_utilities


class TestSalomeMeshUtilities(unittest.TestCase):
    """patching the gui related functions as they are only available when running in GUI mode
    maybe will be refactored in the future but this means properly integrating the testing in GUI
    """

    def test_ClearSelection(self):
        with patch('salome.sg') as patch_sg:
            salome_gui_utilities.ClearSelection()

        self.assertEqual(patch_sg.ClearIObjects.call_count, 1)

    def test_GetAllSelected(self):
        selection_ret = ["1:2:3", "5:6:7", "3:2:3"]

        with patch('salome.sg'):
            with patch('salome.sg.getAllSelected', return_value=selection_ret) as patch_fct:
                selection = salome_gui_utilities.GetAllSelected()

        self.assertEqual(patch_fct.call_count, 1)
        self.assertListEqual(selection, selection_ret)

    def test_HideAll(self):
        with patch('salome.sg') as patch_sg:
            selection = salome_gui_utilities.HideAll()

        self.assertEqual(patch_sg.EraseAll.call_count, 1)
        self.assertEqual(patch_sg.UpdateView.call_count, 1)

    def test_SelectObjects(self):
        selection = ["1:2:3", "5:6:7", "3:2:3"]

        with patch('salome.sg') as patch_sg:
            with patch('kratos_salome_plugin.salome_gui_utilities.ClearSelection') as patch_ClearSelection:
                salome_gui_utilities.SelectObjects(selection)

        self.assertEqual(patch_ClearSelection.call_count, 1)

        self.assertEqual(patch_sg.AddIObject.call_count, 3)
        for exp, call_arg in zip(selection, patch_sg.AddIObject.call_args_list):
            self.assertEqual(exp, call_arg[0][0])

    def test_DisplayObjectsOnly(self):
        selection = ["1:2:3", "5:6:7", "3:2:3"]

        with patch('salome.sg') as patch_sg:
            with patch('kratos_salome_plugin.salome_gui_utilities.HideAll') as patch_HideAll:
                with patch('kratos_salome_plugin.salome_gui_utilities.SelectObjects') as patch_SelectObjects:
                    salome_gui_utilities.DisplayObjectsOnly(selection)

        self.assertEqual(patch_HideAll.call_count, 1)
        self.assertEqual(patch_SelectObjects.call_count, 1)
        self.assertListEqual(patch_SelectObjects.call_args_list[0][0][0], selection)

        self.assertEqual(patch_sg.FitSelection.call_count, 1)


if __name__ == '__main__':
    unittest.main()
