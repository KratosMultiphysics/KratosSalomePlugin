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
from testing_utilities import GetTestsDir

class TestWriteMdpa(unittest.TestCase):
    def test_WriteHeaderMdpa(self):
        raise NotImplementedError
        # with open(file_name, 'w') as mdpa_file:
        #     _WriteHeaderMdpa(model_part, additional_header, mdpa_file)

    def test_WriteNodesMdpa(self):
        mp = ModelPart()
        for i in range(8):
            mp.CreateNewNode(i+1, i**1.1, i*2.2, 2.6)

        file_name = "nodes.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteNodesMdpa(mp.Nodes, mdpa_file)

        self.__CompareMdpaWithReferenceFile(file_name)

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

        self.__CompareMdpaWithReferenceFile(file_name)

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

        self.__CompareMdpaWithReferenceFile(file_name)

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

        self.__CompareMdpaWithReferenceFile(file_name)

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

        self.__CompareMdpaWithReferenceFile(file_name)

    def test_WriteSubModelPartMdpa_SubSubModelPart(self):
        mp = ModelPart()
        smp_1 = mp.CreateSubModelPart("smp_one")
        smp_2 = smp_1.CreateSubModelPart("smp_two")
        smp_22 = smp_1.CreateSubModelPart("smp_two_two")
        smp_3 = smp_2.CreateSubModelPart("smp_two_three")

        smp_1.SetValue("wweerrtt", 12345)
        smp_1.SetValue("LITF", 852.74)

        smp_22.SetValue("My_Val", -92.74)
        smp_22.SetValue("TAB", 13)

        for i in range(4):
            smp_1.CreateNewNode(i+1, i*2.2, 0.0, 0.0)
        for i in range(4, 11):
            smp_2.CreateNewNode(i+1, 0.0, 0.0, i*8.3)
        for i in range(11, 14):
            smp_22.CreateNewNode(i+1, 0.0, i*i+2.3, 0.0)
        for i in range(14, 20):
            smp_3.CreateNewNode(i+1, 1.897+i, i*i+2.3, 0.0)

        props = mp.CreateNewProperties(15)
        for i in range(6):
            smp_1.CreateNewElement("CustomElement", i+1, [1], props)
        for i in range(3):
            smp_1.CreateNewCondition("TheMainCondition", i+1, [1], props)
        for i in range(6):
            smp_2.CreateNewElement("FluidElement", i+7, [1], props)
        for i in range(3):
            smp_22.CreateNewCondition("WallCondition", i+4, [1], props)

        file_name = "sub_sub_model_part.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteSubModelPartsMdpa(smp_1, mdpa_file)

        self.__CompareMdpaWithReferenceFile(file_name)

    def test_WriteEntityDataMdpa_nodes(self):
        mp = ModelPart()
        for i in range(8):
            node = mp.CreateNewNode(i+1, i**1.1, i*2.2, 2.6)
            node.SetValue("simple", 15.336)

        file_name = "entity_data_nodes.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteEntityDataMdpa(mp.Nodes, "Node", mdpa_file)

        self.__CompareMdpaWithReferenceFile(file_name)

    def test_WriteEntityDataMdpa_nodes_multiple_data(self):
        mp = ModelPart()
        for i in range(8):
            node = mp.CreateNewNode(i+1, 0.0, 0.0, 0.0) # coordinates do not matter here
            node.SetValue("Card", 15.336)
            if i%2==0:
                node.SetValue("kMui", [2, 3.3, -78.1]) # vector
            if i%3==0:
                node.SetValue("SomeMatrix", [[2, 3.3], [5.3, 7.456]]) # matrix
                node.SetValue("TheString", "SmallDisp")

        file_name = "multiple_entity_data_nodes.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteEntityDataMdpa(mp.Nodes, "Node", mdpa_file)

        self.__CompareMdpaWithReferenceFile(file_name)

    def test_WriteEntityDataMdpa_elements(self):
        mp = ModelPart()
        mp.CreateNewNode(1, 0.0, 0.0, 0.0) # coordinates do not matter here

        props = mp.CreateNewProperties(1)

        for i in range(10):
            elem = mp.CreateNewElement("CustomElement", i+1, [1], props)
            elem.SetValue("Mulz", 1)
            elem.SetValue("AAbbCC", 1.336E6)
            if i%2==0:
                elem.SetValue("YOUNG", 2397)

        file_name = "entity_data_elements.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteEntityDataMdpa(mp.Elements, "Element", mdpa_file)

        self.__CompareMdpaWithReferenceFile(file_name)

    def test_WriteEntityDataMdpa_conditions(self):
        mp = ModelPart()
        mp.CreateNewNode(1, 0.0, 0.0, 0.0) # coordinates do not matter here

        props = mp.CreateNewProperties(1)

        for i in range(14):
            cond = mp.CreateNewCondition("OneCondition", i+1, [1], props)
            cond.SetValue("Mulz", 1)
            cond.SetValue("AAbbCC", 1.336E6)
            if i%4==0:
                cond.SetValue("YOUNG", 2397)

        file_name = "entity_data_conditions.mdpa"
        with open(file_name, 'w') as mdpa_file:
            write_mdpa._WriteEntityDataMdpa(mp.Conditions, "Condition", mdpa_file)

        self.__CompareMdpaWithReferenceFile(file_name)

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

        self.__CompareMdpaWithReferenceFile(file_name)

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

        self.__CompareMdpaWithReferenceFile(file_name)

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

        self.__CompareMdpaWithReferenceFile(file_name)

    def test_WriteMdpa(self):
        raise NotImplementedError

    def __CompareMdpaWithReferenceFile(self, created_file_name):
        ref_file_name = os.path.join(GetTestsDir(), "write_mdpa_ref_files", "ref_"+created_file_name)
        try:
            CompareMdpaFiles(ref_file_name, created_file_name)
            successful = True
            err_msg=""
            os.remove(created_file_name)
        except Exception as e:
            successful = False
            err_msg = e
        self.assertTrue(successful, msg="\n"+str(err_msg))


def CompareMdpaFiles(ref_mdpa_file, other_mdpa_file):
    def GetFileLines(ref_mdpa_file, other_mdpa_file):
        """This function reads the reference and the output file
        It returns the lines read from both files and also compares
        if they contain the same numer of lines
        """
        # check if files are valid
        if not os.path.isfile(ref_mdpa_file):
            err_msg  = 'The specified reference file name "'
            err_msg += ref_mdpa_file
            err_msg += '" is not valid!'
            raise Exception(err_msg)
        if not os.path.isfile(other_mdpa_file):
            err_msg  = 'The specified output file name "'
            err_msg += other_mdpa_file
            err_msg += '" is not valid!'
            raise Exception(err_msg)

        # "readlines" adds a newline at the end of the line,
        # which will be removed with rstrip afterwards
        with open(ref_mdpa_file,'r') as ref_file:
            lines_ref = ref_file.readlines()
        with open(other_mdpa_file,'r') as out_file:
            lines_other = out_file.readlines()

        # removing trailing newline AND whitespaces (beginning & end) than can mess with the comparison
        # furthermore convert tabs to spaces
        lines_ref = [line.rstrip().lstrip().replace("\t", " ") for line in lines_ref]
        lines_other = [line.rstrip().lstrip().replace("\t", " ") for line in lines_other]

        num_lines_ref = len(lines_ref)
        num_lines_other = len(lines_other)

        if num_lines_ref != num_lines_other:
            err_msg  = "Files have different number of lines!"
            err_msg += "\nNum Lines Reference File: " + str(num_lines_ref)
            err_msg += "\nNum Lines Other File: " + str(num_lines_other)
            raise Exception(err_msg)

        return lines_ref, lines_other

    def CompareNodes(lines_ref, lines_other, line_index):
        line_index += 1 # skip the "Begin" line

        while not lines_ref[line_index].split(" ")[0] == "End":
            line_ref_splitted = lines_ref[line_index].split(" ")
            line_other_splitted = lines_other[line_index].split(" ")
            if len(line_ref_splitted) != len(line_other_splitted):
                raise Exception("Line {}: Node format is not correct!".format(line_index+1))

            # compare node Id
            if int(line_ref_splitted[0]) != int(line_other_splitted[0]):
                raise Exception("Line {}: Node Ids do not match!".format(line_index+1))

            # compare node coordinates
            for i in range(1,4):
                ref_coord = float(line_ref_splitted[i])
                other_coord = float(line_other_splitted[i])
                if abs(ref_coord-other_coord) > 1E-12:
                    raise Exception("Line {}: Node Coordinates do not match!".format(line_index+1))

            line_index += 1

        return line_index+1

    def CompareGeometricalObjects(lines_ref, lines_other, line_index):
        # compare entity types (Elements or Conditions)
        ref_type = lines_ref[line_index].split(" ")[2]
        other_type = lines_other[line_index].split(" ")[2]
        if ref_type != other_type:
            raise Exception("Line {}: Types do not match!".format(line_index+1))

        line_index += 1 # skip the "Begin" line

        while not lines_ref[line_index].split(" ")[0] == "End":
            line_ref_splitted = lines_ref[line_index].split(" ")
            line_other_splitted = lines_other[line_index].split(" ")
            if len(line_ref_splitted) != len(line_other_splitted):
                raise Exception("Line {}: Entity format is not correct!".format(line_index+1))

            # compare entity Id
            if int(line_ref_splitted[0]) != int(line_other_splitted[0]):
                raise Exception("Line {}: Entity Ids do not match!".format(line_index+1))

            # compare entity Id
            if int(line_ref_splitted[1]) != int(line_other_splitted[1]):
                raise Exception("Line {}: Properties Ids do not match!".format(line_index+1))

            # compare node coordinates
            for i in range(2,len(line_ref_splitted)):
                ref_conn = int(line_ref_splitted[i])
                other_conn = int(line_other_splitted[i])
                if abs(ref_conn-other_conn) > 1E-12:
                    raise Exception("Line {}: Connectivities do not match!".format(line_index+1))

            line_index += 1

        return line_index+1

    def CompareSubModelParts(lines_ref, lines_other, line_index):
        raise NotImplementedError
        line_index += 1 # skip the "Begin" line

        while not lines_ref[line_index].split(" ")[0] == "End":
            # print(lines_ref[line_index])
            # print("No")
            line_index += 1
        return line_index+1

    def CompareEntitiyData(lines_ref, lines_other, line_index):
        raise NotImplementedError
        line_index += 1 # skip the "Begin" line

        while not lines_ref[line_index].split(" ")[0] == "End":
            # print(lines_ref[line_index])
            # print("No")
            line_index += 1
        return line_index+1

    def CompareKeyValueData(lines_ref, lines_other, line_index):
        # compare entity types (Elements or Conditions)
        ref_type = lines_ref[line_index].split(" ")[1]
        other_type = lines_other[line_index].split(" ")[1]
        if ref_type != other_type:
            raise Exception("Line {}: Types do not match!".format(line_index+1))

        line_index += 1 # skip the "Begin" line

        while not lines_ref[line_index].split(" ")[0] == "End":
            line_ref_splitted = lines_ref[line_index].split(" ")
            line_other_splitted = lines_other[line_index].split(" ")
            if len(line_ref_splitted) != len(line_other_splitted):
                raise Exception("Line {}: Data format is not correct!".format(line_index+1))

            # compare data key
            if line_ref_splitted[0] != line_other_splitted[0]:
                raise Exception("Line {}: Data Keys do not match!".format(line_index+1))

            # compare data value
            if len(line_ref_splitted) == 2: # normal key-value pair
                try: # check if the value can be converted to float
                    val_ref = float(line_ref_splitted[1])
                    val_is_float = True
                except ValueError:
                    val_is_float = False

                if val_is_float:
                    val_ref = float(line_ref_splitted[1])
                    val_other = float(line_other_splitted[1])
                    if abs(val_ref-val_other) > 1E-12:
                        raise Exception("Line {}: Values (float) do not match!".format(line_index+1))
                else:
                    if len(line_ref_splitted[1]) != len(line_other_splitted[1]):
                        raise Exception("Line {}: Values do not match!".format(line_index+1))

            elif len(line_ref_splitted) == 3: # vector or Matrix
                print(line_ref_splitted, len(line_ref_splitted))
                if "," in line_ref_splitted[1]: # matrix
                    print("Matrix")
                else: # vector
                    print("vector")
            else:
                raise Exception("Line {}: Data Value has too many entries!".format(line_index+1))

            line_index += 1

        return line_index+1

    lines_ref, lines_other = GetFileLines(ref_mdpa_file, other_mdpa_file)

    line_index = 0
    while line_index < len(lines_ref):
        ref_line_splitted = lines_ref[line_index].split(" ")

        if ref_line_splitted[0] == "Begin":
            comparison_type = ref_line_splitted[1]

            if comparison_type == "Nodes":
                line_index = CompareNodes(lines_ref, lines_other, line_index)

            elif comparison_type == "Elements" or comparison_type == "Conditions":
                line_index = CompareGeometricalObjects(lines_ref, lines_other, line_index)

            elif comparison_type == "SubModelPart":
                line_index = CompareSubModelParts(lines_ref, lines_other, line_index)

            elif comparison_type in ["NodalData", "ElementalData", "ConditionalData"]:
                line_index = CompareEntitiyData(lines_ref, lines_other, line_index)

            elif comparison_type in ["Properties", "ModelPartData", "SubModelPartData"]:
                line_index = CompareKeyValueData(lines_ref, lines_other, line_index)

            else:
                raise Exception('Comparison for "{}" not implemented!'.format(comparison_type))

        else:
            line_index += 1


if __name__ == '__main__':
    unittest.main()
