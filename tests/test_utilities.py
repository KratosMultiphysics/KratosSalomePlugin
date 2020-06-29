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
import unittest, os
import shutil

# plugin imports
import kratos_salome_plugin.utilities as utils
from kratos_salome_plugin.reload_modules import MODULE_RELOAD_ORDER

# tests imports
import testing_utilities

class TestUtilities(unittest.TestCase):

    def test_GetPluginPath(self):
        # make sure the path points to the "plugins" folder, aka ends with "plugin"
        self.assertEqual(os.path.split(utils.GetPluginPath())[1], "kratos_salome_plugin")

    def test_GetAbsPathInPlugin(self):
        file_name = "app.py"
        folder_name = "subdir"
        a_path = ["ddir", "subdir2", "file.txt"]

        self.assertEqual(os.path.split(utils.GetAbsPathInPlugin(file_name))[1], file_name)
        self.assertEqual(os.path.split(utils.GetAbsPathInPlugin(folder_name))[1], folder_name)

        self.assertEqual(utils.GetAbsPathInPlugin(*a_path).split(os.sep)[-len(a_path):], a_path)


class TestUtilsPyFiles(unittest.TestCase):
    maxDiff = None # to display the entire comparison of "assertListEqual"

    def test_ConvertPythonFileToPythonModule(self):
        py_file_name_1 = "my_custom_class.py"
        py_file_name_2 = os.path.join("folder" , py_file_name_1)
        py_file_name_3 = os.path.join("my_module", py_file_name_2)

        self.assertEqual("my_custom_class", utils.ConvertPythonFileToPythonModule(py_file_name_1))
        self.assertEqual("folder.my_custom_class", utils.ConvertPythonFileToPythonModule(py_file_name_2))
        self.assertEqual("my_module.folder.my_custom_class", utils.ConvertPythonFileToPythonModule(py_file_name_3))

        not_a_py_file_name = "some_file.txt"
        with self.assertRaisesRegex(Exception, 'The input \("some_file.txt"\) is not a python-file, i.e. does not end with '):
            utils.ConvertPythonFileToPythonModule(not_a_py_file_name)

    def test_ConvertPythonFilesToPythonModules(self):
        py_file_name_1 = "my_custom_class.py"
        py_file_name_2 = os.path.join("folder" , py_file_name_1)
        py_file_name_3 = os.path.join("my_module", py_file_name_2)

        py_file_list = [py_file_name_1, py_file_name_2, py_file_name_3]

        exp_py_module_list = ["my_custom_class", "folder.my_custom_class", "my_module.folder.my_custom_class"]

        self.assertListEqual(exp_py_module_list, utils.ConvertPythonFilesToPythonModules(py_file_list))

    def test_GetFilesInDirectory(self):
        files_found = utils.GetFilesInDirectory(self.folder_name)
        self.assertListEqual(sorted(self.raw_file_list), sorted(files_found)) # sort here, the "raw_file_list" was not set up ordered

    def test_GetPythonFilesInDirectory(self):
        py_file_list = [f for f in self.raw_file_list if (f.endswith(".py") and os.path.split(f)[1] != "__init__.py")]

        files_found = utils.GetPythonFilesInDirectory(self.folder_name)

        self.assertListEqual(sorted(py_file_list), sorted(files_found)) # sort here, bcs order does not matter in the function

    def test_GetPythonModulesInDirectory(self):
        py_file_list = [f for f in self.raw_file_list if (f.endswith(".py") and os.path.split(f)[1] != "__init__.py")]

        py_module_list = [f[:-3].replace(os.sep, ".") for f in py_file_list]

        modules_found = utils.GetPythonModulesInDirectory(self.folder_name)

        self.assertListEqual(sorted(py_module_list), sorted(modules_found)) # sort here, bcs order does not matter in the function

    def test_GetInitFilesInDirectory(self):
        py_file_list = [f for f in self.raw_file_list if os.path.split(f)[1] == "__init__.py"]

        files_found = utils.GetInitFilesInDirectory(self.folder_name)

        self.assertListEqual(sorted(py_file_list), sorted(files_found)) # sort here, bcs order does not matter in the function

    def test_GetInitModulesInDirectory(self):
        py_file_list = [f for f in self.raw_file_list if os.path.split(f)[1] == "__init__.py"]

        py_module_list = [f[:-3].replace(os.sep, ".") for f in py_file_list]

        modules_found = utils.GetInitModulesInDirectory(self.folder_name)

        self.assertListEqual(sorted(py_module_list), sorted(modules_found)) # sort here, bcs order does not matter in the function

    def test_CheckOrderModulesReloadPlugin(self):
        # make sure all modules are specified in the module reload list
        order_module_reload = MODULE_RELOAD_ORDER
        self.assertFalse("salome_plugins" in order_module_reload) # "salome_plugins" is the main file of the plugin and must not be reloaded!

        self.assertEqual(len(order_module_reload), len(set(order_module_reload))) # check for duplicated entries

        all_modules = utils.GetPythonModulesInDirectory(utils.GetPluginPath())

        self.assertListEqual(sorted(all_modules), sorted(order_module_reload)) # sort here, bcs order does not matter for only checking the contents


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
