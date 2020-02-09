#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# python imports
import unittest, sys, os

# plugin imports
sys.path.append(os.pardir) # required to be able to do "from plugin import xxx"
from plugin.utilities import utils
from plugin.model_part import ModelPart
from plugin import write_mdpa

# tests imports
import testing_utilities

class TestWriteMdpa(unittest.TestCase):
    def test_WriteHeaderMdpa(self):
        pass
        # with open(file_name, 'w') as mdpa_file:
        #     _WriteHeaderMdpa(model_part, additional_header, mdpa_file)

    def test_WriteNodesMdpa(self):
        mp = ModelPart()
        for i in range(10):
            mp.CreateNewNode(i+1, i**1.1, i*2.2, 2.6)

        with open("file_name", 'w') as mdpa_file:
            write_mdpa._WriteNodesMdpa(mp.Nodes, mdpa_file)

    def test_WriteEntitiesMdpa_elements(self):
        mp = ModelPart()
        for i in range(6):
            mp.CreateNewNode(i+1, 0.0, 0.0, 0.0) # coordinates do not matter here

        props_1 = mp.CreateNewProperties(1)
        props_2 = mp.CreateNewProperties(15)

        for i in range(10):
            if i%3 == 0:
                props = props_2
            else:
                props = props_1

            mp.CreateNewElement("CustomElement", i+1, [i%3+1,i%6+1], props)

        with open("file_name", 'w') as mdpa_file:
            write_mdpa._WriteEntitiesMdpa(mp.Elements, "Element", mdpa_file)

    def test_WriteEntitiesMdpa_conditions(self):
        pass

    def test_WriteEntitiesMdpa_multiple_elements(self):
        pass

    def test_WriteSubModelPartMdpa(self):
        pass

    def test_WriteSubModelPartMdpa_SubSubModelPart(self):
        pass

    def test_WriteEntityDataMdpa_nodes(self):
        pass

    def test_WriteEntityDataMdpa_nodes_multiple_data(self):
        pass

    def test_WriteEntityDataMdpa_elements(self):
        pass

    def test_WriteEntityDataMdpa_conditions(self):
        pass

    def test_WritePropertiesMdpa(self):
        pass

    def test_WriteModelPartDataMdpa(self):
        pass

    def test_WriteModelPartDataMdpa_SubModelPart(self):
        pass

    def test_WriteMdpa(self):
        pass


if __name__ == '__main__':
    unittest.main()
