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

# plugin imports
from ks_plugin.utilities.utils import IsExecutedInSalome

# tests imports
import testing_utilities

if IsExecutedInSalome():
    import create_kratos_input_tui


class TestSalomeMesh(testing_utilities.SalomeTestCaseWithBox):
    def test_xxx(self):
        pass

class TestCreateModelPart(testing_utilities.SalomeTestCaseWithBox):
    def test_xxx(self):
        pass

class TestCreateMdpaFile(testing_utilities.SalomeTestCaseWithBox):
    def test_xxx(self):
        pass


if __name__ == '__main__':
    unittest.main()