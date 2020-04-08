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

# plugin imports
from ks_plugin.model_part import ModelPart
from ks_plugin import write_mdpa

# tests imports
from testing_utilities import GetTestsDir, CompareMdpaWithReferenceFile

class TestWriteMdpa(unittest.TestCase):
    def test_WriteHeaderMdpa(self):
        mp = CreateFullModelPart()
        additional_header_info = "my_custom mdpa file"
        file_name = "mdpa_header.mdpa"
        write_creation_time = True
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteHeaderMdpa(mp, additional_header_info, write_creation_time, mdpa_file)

        CompareMdpaWithReferenceFile(file_name, self)

    def test_WriteNodesMdpa(self):
        mp = ModelPart()
        for i in range(8):
            mp.CreateNewNode(i+1, i**1.1, i*2.2, 2.6)

        file_name = "nodes.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteNodesMdpa(mp.Nodes, mdpa_file)

        CompareMdpaWithReferenceFile(file_name, self)

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

        file_name = "elements.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteEntitiesMdpa(mp.Elements, "Element", mdpa_file)

        CompareMdpaWithReferenceFile(file_name, self)

    def test_WriteEntitiesMdpa_conditions(self):
        mp = ModelPart()
        for i in range(6):
            mp.CreateNewNode(i+1, 0.0, 0.0, 0.0) # coordinates do not matter here

        props_1 = mp.CreateNewProperties(1)
        props_2 = mp.CreateNewProperties(15)

        for i in range(17):
            if i%5 == 0:
                props = props_2
            else:
                props = props_1

            mp.CreateNewCondition("MainCondition", i+1, [i%3+1,i%6+1,i%2+1], props)

        file_name = "conditions.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteEntitiesMdpa(mp.Conditions, "Condition", mdpa_file)

        CompareMdpaWithReferenceFile(file_name, self)

    def test_WriteEntitiesMdpa_multiple_elements(self):
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

            mp.CreateNewElement("CustomElement", i+1, [i%3+1, i%6+1], props)

        for i in range(10, 15):
            mp.CreateNewElement("ShellElement", i+1, [i%3+1, i%6+1, i%4+1, i%5+1], props_1)

        for i in range(15, 23):
            mp.CreateNewElement("TriangleSolidElement", i+1, [i%6+1, i%4+1, i%5+1], props_2)

        file_name = "multiple_elements.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteEntitiesMdpa(mp.Elements, "Element", mdpa_file)

        CompareMdpaWithReferenceFile(file_name, self)

    def test_WriteSubModelPartsMdpa(self):
        mp = ModelPart()
        smp_1 = mp.CreateSubModelPart("smp_one")
        smp_1.SetValue("wweerrtt", 12345)
        smp_1.SetValue("LITF", 852.74)

        for i in range(4):
            smp_1.CreateNewNode(i+1, i*2.2, 0.0, 0.0)

        props = mp.CreateNewProperties(15)
        for i in range(6):
            smp_1.CreateNewElement("CustomElement", i+1, [i%3+1, i%4+1], props)
        for i in range(3):
            smp_1.CreateNewCondition("TheMainCondition", i+1, [i%3+1], props)

        file_name = "sub_model_part.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteSubModelPartsMdpa(smp_1, mdpa_file)

        CompareMdpaWithReferenceFile(file_name, self)

    def test_WriteSubModelPartMdpa_SubSubModelPart(self):
        mp = CreateFullModelPart()
        smp_1 = mp.GetSubModelPart("smp_one") # sub

        file_name = "sub_sub_model_part.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteSubModelPartsMdpa(smp_1, mdpa_file)

        CompareMdpaWithReferenceFile(file_name, self)

    def test_WriteEntityDataMdpa_nodes(self):
        mp = ModelPart()
        for i in range(8):
            node = mp.CreateNewNode(i+1, i**1.1, i*2.2, 2.6)
            node.SetValue("simple", 15.336+i)

        file_name = "entity_data_nodes.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteEntityDataMdpa(mp.Nodes, "Nod", mdpa_file)

        CompareMdpaWithReferenceFile(file_name, self)

    def test_WriteEntityDataMdpa_nodes_multiple_data(self):
        mp = ModelPart()
        for i in range(8):
            node = mp.CreateNewNode(i+1, 0.0, 0.0, 0.0) # coordinates do not matter here
            node.SetValue("Card", 15.336*i)
            if i%2==1:
                node.SetValue("kMui", [2, 3.3, -78.1, i+2]) # vector
            if i%4==3:
                node.SetValue("SomeMatrix", [[2, i+2, 3.3], [i+2, 5.3, 7.456]]) # matrix
                node.SetValue("TheString", "SmallDisp"+str(i))
            if i==6 or i==7:
                node.SetValue("CustomDisp", 5*i)
                node.SetValue("REACTION_X", -2*i)

        file_name = "multiple_entity_data_nodes.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteEntityDataMdpa(mp.Nodes, "Nod", mdpa_file)

        CompareMdpaWithReferenceFile(file_name, self)

    def test_WriteEntityDataMdpa_elements(self):
        mp = ModelPart()
        mp.CreateNewNode(1, 0.0, 0.0, 0.0) # coordinates do not matter here

        props = mp.CreateNewProperties(1)

        for i in range(10):
            elem = mp.CreateNewElement("CustomElement", i+1, [1], props)
            elem.SetValue("Mulz", 1.66**i)
            elem.SetValue("AAbbCC", 1.336*10**i)
            if i%2==0:
                elem.SetValue("YOUNG", 2397-10.369*i)

        file_name = "entity_data_elements.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteEntityDataMdpa(mp.Elements, "Element", mdpa_file)

        CompareMdpaWithReferenceFile(file_name, self)

    def test_WriteEntityDataMdpa_conditions(self):
        mp = ModelPart()
        mp.CreateNewNode(1, 0.0, 0.0, 0.0) # coordinates do not matter here

        props = mp.CreateNewProperties(1)

        for i in range(14):
            cond = mp.CreateNewCondition("OneCondition", i+1, [1], props)
            cond.SetValue("Mwwz", 1+i*3)
            cond.SetValue("AAbqbCC", 1.336E6*i)
            if i%3==0:
                cond.SetValue("SomeMatrix", [[2, i+2, 3.3], [i+2, 5.3, 7.456]]) # matrix
            if i%4==0:
                cond.SetValue("YOUNG", 2397+5*i)

        file_name = "entity_data_conditions.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteEntityDataMdpa(mp.Conditions, "Condition", mdpa_file)

        CompareMdpaWithReferenceFile(file_name, self)

    def test_WritePropertiesMdpa(self):
        mp = ModelPart()
        mp.CreateNewProperties(0) # left empty

        props_36 = mp.CreateNewProperties(36)
        props_36.SetValue("Card", 15.336)
        props_36.SetValue("kMui", [2, 3.3])
        props_36.SetValue("SomeMatrix", [[2, 3.3], [5.3, 7.456]])
        props_36.SetValue("TheString", "SmallDisp")

        props_2 = mp.CreateNewProperties(2)
        props_2.SetValue("Mulz", 1)
        props_2.SetValue("AAbbCC", 1.336E6)
        props_2.SetValue("YOUNG", 2397)

        file_name = "properties.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WritePropertiesMdpa(mp.Properties, mdpa_file)

        CompareMdpaWithReferenceFile(file_name, self)

    def test_WriteModelPartDataMdpa(self):
        mp = ModelPart()

        mp.SetValue("Card", 15.336)
        mp.SetValue("kMui", [2, 3.3])
        mp.SetValue("SomeMatrix", [[2, 3.3, 5.147], [5.3, 7.456, -13.002]])
        mp.SetValue("TheString", "SmallDisp")
        mp.SetValue("Mulz", 1)
        mp.SetValue("AAbbCC", 1.336E6)
        mp.SetValue("YOUNG", 2397)

        file_name = "model_part_data.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteModelPartDataMdpa(mp, mdpa_file)

        CompareMdpaWithReferenceFile(file_name, self)

    def test_WriteModelPartDataMdpa_SubModelPart(self):
        mp = ModelPart()
        smp = mp.CreateSubModelPart("sub_1")

        smp.SetValue("Card", 15.336)
        smp.SetValue("kMui", [2, 3.3, 15.78, -33.74, 36.01, 72.1])
        smp.SetValue("SomeMatrix", [[2, 3.3, 10.4, 11.2, 0.33], [5.3, 456, 88.123, 101.3, 7.456], [1.129,2.129,3.129,4.129,5.129]])
        smp.SetValue("TheString", "SmallDisp")
        smp.SetValue("Mulz", 1)
        smp.SetValue("AAbbCC", 1.336E6)
        smp.SetValue("YOUNG", 2397)

        file_name = "sub_model_part_data.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteModelPartDataMdpa(smp, mdpa_file, level=1)

        CompareMdpaWithReferenceFile(file_name, self)

    def test_WriteMdpa(self):
        mp = CreateFullModelPart()
        additional_header_info = "The very cool model"
        file_name = "full_model_part.mdpa"
        write_mdpa.WriteMdpa(mp, file_name, additional_header_info)

        CompareMdpaWithReferenceFile(file_name, self)


def CreateFullModelPart():
    # just creating a full ModelPart for testing
    mp = ModelPart()
    mp.SetValue("Card", 15.336)
    mp.SetValue("kMui", [2, 3.3, 15.78, -33.74, 36.01, 72.1])
    mp.SetValue("SomeMatrix", [[2, 3.3, 10.4, 11.2, 0.33], [5.3, 456, 88.123, 101.3, 7.456], [1.129,2.129,3.129,4.129,5.129]])
    mp.SetValue("TheString", "SmallDisp")
    mp.SetValue("Mulz", 1)
    mp.SetValue("AAbbCC", 1.336E6)
    mp.SetValue("YOUNG", 2397)

    smp_1 = mp.CreateSubModelPart("smp_one") # sub
    smp_2 = smp_1.CreateSubModelPart("smp_two") # subsub
    smp_22 = smp_1.CreateSubModelPart("smp_two_two") # subsub
    smp_3 = smp_2.CreateSubModelPart("smp_two_three") # subsubsub

    smp_1.SetValue("wweerrtt", 12345)
    smp_1.SetValue("LITF", 852.74)

    smp_22.SetValue("My_Val", -92.74)
    smp_22.SetValue("TAB", 13)

    for i in range(4):
        node = smp_1.CreateNewNode(i+1, i*2.2, 0.0, 0.0)
        node.SetValue("kMui", [2, 3.3, -78.1, i+2]) # vector
        if i%2==0:
            node.SetValue("Hjkwq", 15-i)
    for i in range(4, 11):
        smp_2.CreateNewNode(i+1, 0.0, 0.0, -i*8.3)
    for i in range(11, 14):
        smp_22.CreateNewNode(i+1, 0.0, i*i+2.3, 0.0)
    for i in range(14, 20):
        smp_3.CreateNewNode(i+1, 1.897+i, -i*i+2.3, 0.0)

    for i in range(25, 35):
        node = mp.CreateNewNode(i+1, 1.897+i, i*i+2.3, 18+i*1.33)
        node.SetValue("Hjkwq", 1+5*i)

    props_1 = smp_1.CreateNewProperties(1)
    props_1.SetValue("Card", 15.336)
    props_1.SetValue("kMui", [2, 3.3])
    props_1.SetValue("SomeMatrix", [[2, 3.3], [5.3, 7.456]])
    props_1.SetValue("TheString", "SmallDisp")

    props_2 = mp.CreateNewProperties(2)
    props_2.SetValue("sdlwzy", [2, 3.3, 15.78, -33.74, 36.01, 72.1])

    props = mp.CreateNewProperties(15)
    props.SetValue("Mulz", 1)
    props.SetValue("AAbbCC", 1.336E6)
    props.SetValue("YOUNG", 2397)

    for i in range(6):
        elem = smp_1.CreateNewElement("CustomElement", i+1, [1], props_1)
        elem.SetValue("AUX_INDEX", 1.45*i)
    for i in range(3):
        cond = smp_1.CreateNewCondition("TheMainCondition", i+1, [1], props)
        cond.SetValue("main", [1-i, i*9, 3.7093-10*i, 3.45, 5.1])
    for i in range(6):
        elem = smp_2.CreateNewElement("FluidElement", i+7, [1], props_2)
        if i%2==0:
            elem.SetValue("AUX_INDEX", 1.45*i)
        else:
            elem.SetValue("MIN", -13.9*i)

    for i in range(3):
        cond = smp_22.CreateNewCondition("WallCondition", i+4, [1], props)
        cond.SetValue("DIST", i+1)
    for i in range(6): # again adding the same type to make sure this also works
        smp_1.CreateNewElement("CustomElement", i+18, [1], props_1)

    return mp


if __name__ == '__main__':
    unittest.main()
