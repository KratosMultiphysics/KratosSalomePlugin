import unittest
import sys, os, shutil

import testing_utilities

sys.path.insert(0, "../")
from plugin.utilities import utils

class TestUtils(unittest.TestCase):

    def test_GetPluginPath(self):
        self.assertEqual(os.path.split(utils.GetPluginPath())[1], "plugin")

    def test_GetPythonFilesInDirectory(self):
        def CreateFile(file_path):
            path, _ = os.path.split(file_path)
            if not os.path.isdir(path):
                os.makedirs(path)
            open(file_path, 'w').close()

        folder_name = os.path.join(testing_utilities.GetTestsDir(), "the_dir_to_test")

        if os.path.isdir(folder_name):
            # clean leftovers
            shutil.rmtree(folder_name)

        # create hierarchy of files
        file_list = [
            "top_sth",
            "top_py_file.py",
            "top_py_file.pyc",
            "subdir{}top_py_file.pyc".format(os.sep),
            "subdir{}__init__.py".format(os.sep),
            "subdir{}sd_py_file.py".format(os.sep),
            "subdir{}another_py_file.py".format(os.sep),
            "subdir{}sd_pyaass_file.txt".format(os.sep),
            "subdir{0}subsdir{0}sd_pyaass_file.txt".format(os.sep),
            "subdir{0}subsdir{0}the_py_file.py".format(os.sep),
            "subdir{0}subsdir{0}some_list_file".format(os.sep),
            "subdir{0}subsdir{0}some_f.pyc".format(os.sep)
        ]

        py_file_list = [f for f in file_list if (f.endswith(".py") and os.path.split(f)[1] != "__init__.py")]

        file_list = ['{}{}{}'.format(folder_name, os.sep, f) for f in file_list] # prepending folder name

        for f in file_list:
            CreateFile(f)

        files_found = utils.GetPythonFilesInDirectory(folder_name)

        shutil.rmtree(folder_name)

        self.assertEqual(sorted(py_file_list), sorted(files_found))


if __name__ == '__main__':
    unittest.main()
