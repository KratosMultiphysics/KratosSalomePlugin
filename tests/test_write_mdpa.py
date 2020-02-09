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
        pass
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
        pass

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

    def __CompareMdpaWithReferenceFile(self, created_file_name):
        ref_file_name = os.path.join(GetTestsDir(), "write_mdpa_ref_files", "ref_"+created_file_name)
        try:
            CompareMdpaFiles(ref_file_name, created_file_name)
            successful = True
            err_msg=""
        except Exception as e:
            successful = False
            err_msg = e
        os.remove(created_file_name)
        self.assertTrue(successful, msg=err_msg)


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

        # removing trailing newline AND whitespaces than can mess with the comparison
        lines_ref = [line.rstrip() for line in lines_ref]
        lines_other = [line.rstrip() for line in lines_other]

        num_lines_ref = len(lines_ref)
        num_lines_other = len(lines_other)

        if num_lines_ref != num_lines_other:
            err_msg  = "Files have different number of lines!"
            err_msg += "\nNum Lines Reference File: " + str(num_lines_ref)
            err_msg += "\nNum Lines Other File: " + str(num_lines_other)
            raise Exception(err_msg)

        return lines_ref, lines_other

    lines_ref, lines_other = GetFileLines(ref_mdpa_file, other_mdpa_file)

    return True


if __name__ == '__main__':
    unittest.main()
