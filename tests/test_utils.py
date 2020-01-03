import unittest
import sys, os, shutil

import testing_utilities

sys.path.append(os.pardir)
from plugin.utilities import utils

class TestUtils(unittest.TestCase):

    def test_GetPluginPath(self):
        # make sure the path points to the "plugins" folder, aka ends with "plugin"
        self.assertEqual(os.path.split(utils.GetPluginPath())[1], "plugin")


class TestUtilsPyFiles(unittest.TestCase):

    def test_GetPythonFilesInDirectory(self):
        py_file_list = [f for f in self.raw_file_list if (f.endswith(".py") and os.path.split(f)[1] != "__init__.py")]

        files_found = utils.GetPythonFilesInDirectory(self.folder_name)

        self.assertEqual(sorted(py_file_list), sorted(files_found)) # sort here, bcs order does not matter in the function

    def test_GetPythonModulesInDirectory(self):
        py_file_list = [f for f in self.raw_file_list if (f.endswith(".py") and os.path.split(f)[1] != "__init__.py")]

        py_module_list = [f[:-3].replace(os.sep, ".") for f in py_file_list]

        modules_found = utils.GetPythonModulesInDirectory(self.folder_name)

        self.assertEqual(sorted(py_module_list), sorted(modules_found)) # sort here, bcs order does not matter in the function

    def test_CheckOrderModulesReloadPlugin(self):
        # make sure all modules are specified in the module reload list
        order_module_reload = utils.GetOrderModulesForReload()
        self.assertFalse("salome_plugins" in order_module_reload) # "salome_plugins" is the main file of the plugin and must not be reloaded!

        self.assertEqual(len(order_module_reload), len(set(order_module_reload))) # check for duplicated entries

        all_modules = utils.GetPythonModulesInDirectory(utils.GetPluginPath())
        self.assertTrue("salome_plugins" in all_modules) # "salome_plugins" is the main file of the plugin and has to exist!

        all_modules.remove("salome_plugins")

        self.assertEqual(sorted(all_modules), sorted(order_module_reload)) # sort here, bcs order does not matter for only checking the contents


    def setUp(self):
        def CreateFile(file_path):
            path, _ = os.path.split(file_path)
            if not os.path.isdir(path):
                os.makedirs(path)
            open(file_path, 'w').close()

        self.folder_name = os.path.join(testing_utilities.GetTestsDir(), "the_dir_to_test")

        if os.path.isdir(self.folder_name):
            # clean leftovers, just in case
            shutil.rmtree(self.folder_name)

        # create hierarchy of files
        self.raw_file_list = [
            "top_sth",
            "top_py_file.py",
            "top_py_file.pyc",
            "subdir{}top_py_file.pyc".format(os.sep),
            "subdir{}__init__.py".format(os.sep),
            "subdir{}mult_exist_file.py".format(os.sep), # this file exists also in a different dir
            "subdir{}another_py_file.py".format(os.sep),
            "subdir{}sd_pyaass_file.txt".format(os.sep),
            "different_subdir{}mult_exist_file.py".format(os.sep), # create a file with the same name in a different directory
            "subdir{0}subsdir{0}sd_pyaass_file.txt".format(os.sep),
            "subdir{0}subsdir{0}the_py_file.py".format(os.sep),
            "subdir{0}subsdir{0}some_list_file".format(os.sep),
            "subdir{0}subsdir{0}some_f.pyc".format(os.sep),
            "subdir{0}subsdir{0}mult_exist_file.py".format(os.sep) # create a file with the same name in a different directory
        ]

        self.file_list = ['{}{}{}'.format(self.folder_name, os.sep, f) for f in self.raw_file_list] # prepending folder name

        for f in self.file_list:
            CreateFile(f)

    def tearDown(self):
        shutil.rmtree(self.folder_name)


if __name__ == '__main__':
    unittest.main()
