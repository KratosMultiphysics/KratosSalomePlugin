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
import os

# plugin imports
from kratos_salome_plugin.model_part import ModelPart
from kratos_salome_plugin.read_mdpa import ReadMdpa

# tests imports
from testing_utilities import GetTestsDir, ModelPartForTests

class TestReadMdpa(unittest.TestCase):
    def test_read_comments(self):
        mp_read = ModelPart()
        ReadMdpa(mp_read, GetPathToRefMdpa("mdpa_header"))

        mp_ref = ModelPart() # reference is empty

        self.assertEqual(mp_read, mp_ref)

    def test_read_nodes(self):
        mp_read = ModelPart()
        ReadMdpa(mp_read, GetPathToRefMdpa("nodes"))

        mp_ref = ModelPart()
        ModelPartForTests.CreateNodes(mp_ref)

        self.assertEqual(mp_read, mp_ref)

    def test_read_elements(self):
        mp_read = ModelPart()
        ReadMdpa(mp_read, GetPathToRefMdpa("elements"))

        mp_ref = ModelPart()
        ModelPartForTests.CreateNodesAndLineElements(mp_ref)

        self.assertEqual(mp_read, mp_ref)

    def test_read_conditions(self):
        mp_read = ModelPart()
        ReadMdpa(mp_read, GetPathToRefMdpa("conditions"))

        mp_ref = ModelPart()
        ModelPartForTests.CreateNodesAndTriangleConditions(mp_ref)

        self.assertEqual(mp_read, mp_ref)


def GetPathToRefMdpa(mdpa_file_name_without_ext):
    return os.path.join(GetTestsDir(), "mdpa_ref_files", "ref_{}.mdpa".format(mdpa_file_name_without_ext))


if __name__ == '__main__':
    unittest.main()
