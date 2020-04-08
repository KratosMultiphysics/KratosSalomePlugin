#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# this file contains helpers used in the tests

# python imports
import unittest, os

# plugin imports
from ks_plugin.utilities import utils

if utils.IsExecutedInSalome():
    # Check https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html for how to handle study
    # imports that have dependenices on salome, hence can only be imported if executed in salome
    import salome
    import ks_plugin.utilities.salome_utilities as salome_utils

    # initialize salome, should be done only once
    salome.salome_init()

    # importing important modules, explicitly done after salome_init
    # not sure if the order is important, but this is how it is done in the dumped studies
    import GEOM
    from salome.geom import geomBuilder

    import SMESH
    from salome.smesh import smeshBuilder


def GetTestsDir():
    return os.path.dirname(os.path.realpath(__file__))

def CheckIfKratosAvailable():
    if "KRATOS_AVAILABLE" in os.environ:
        # this is intended to be used in the CI
        # there "try-except" might lead to an undiscovered failure
        return (os.environ["KRATOS_AVAILABLE"] == "1")
    else:
        try:
            import KratosMultiphysics
            return True
        except:
            return False


def CheckIfApplicationsAvailable(*application_names):
    raise Exception("This function is untested!")
    if not CheckIfKratosAvailable():
        return False
    from KratosMultiphysics.kratos_utilities import CheckIfApplicationsAvailable
    return CheckIfApplicationsAvailable(application_names)

@unittest.skipUnless(utils.IsExecutedInSalome(), "This test can only be executed in Salome")
class SalomeTestCase(unittest.TestCase):

    def setUp(self):
        # initializing salome also creates a study.
        # clearing the study in order to have a clean study for each test.
        # This is much faster than re-launching salome for each test
        self.study = salome.myStudy
        self.study.Clear()
        self.study.Init()

        self.geompy = geomBuilder.New()
        self.smesh = smeshBuilder.New()


class SalomeTestCaseWithBox(SalomeTestCase):
    # a test case that has a simple box with a tetra and hexa mesh as setup

    def setUp(self):
        super().setUp()

        # creating geometry
        O = self.geompy.MakeVertex(0, 0, 0)
        OX = self.geompy.MakeVectorDXDYDZ(1, 0, 0)
        OY = self.geompy.MakeVectorDXDYDZ(0, 1, 0)
        OZ = self.geompy.MakeVectorDXDYDZ(0, 0, 1)
        self.box = self.geompy.MakeBoxDXDYDZ(200, 200, 200)
        [self.face_1, self.face_2] = self.geompy.SubShapes(self.box, [13, 23])
        [self.edge_1, self.edge_2] = self.geompy.SubShapes(self.box, [18, 26])
        self.group_faces = self.geompy.CreateGroup(self.box, self.geompy.ShapeType["FACE"])
        self.geompy.UnionIDs(self.group_faces, [33, 31])
        self.group_edges = self.geompy.CreateGroup(self.box, self.geompy.ShapeType["EDGE"])
        self.geompy.UnionIDs(self.group_edges, [25, 12, 29, 22])

        self.name_main_box = 'main_box'
        self.geompy.addToStudy(self.box, self.name_main_box)

        # creating mesh
        self.mesh_tetra = self.smesh.Mesh(self.box)
        Regular_1D = self.mesh_tetra.Segment()
        Max_Size_1 = Regular_1D.MaxSize(60)
        MEFISTO_2D = self.mesh_tetra.Triangle(algo=smeshBuilder.MEFISTO)
        NETGEN_3D = self.mesh_tetra.Tetrahedron()
        isDone = self.mesh_tetra.Compute()
        self.assertTrue(isDone, msg="Tetra mesh could not be computed!")
        self.name_main_mesh_tetra = 'main_mesh_tetra'
        self.smesh.SetName(self.mesh_tetra.GetMesh(), self.name_main_mesh_tetra)

        self.mesh_hexa = self.smesh.Mesh(self.box)
        Regular_1D_1 = self.mesh_hexa.Segment()
        Number_of_Segments_1 = Regular_1D_1.NumberOfSegments(8)
        Quadrangle_2D = self.mesh_hexa.Quadrangle(algo=smeshBuilder.QUADRANGLE)
        Hexa_3D = self.mesh_hexa.Hexahedron(algo=smeshBuilder.Hexa)
        isDone = self.mesh_hexa.Compute()
        self.assertTrue(isDone, msg="Hexa mesh could not be computed!")
        self.name_main_mesh_hexa = 'main_mesh_hexa'
        self.smesh.SetName(self.mesh_hexa.GetMesh(), self.name_main_mesh_hexa)

        # adding 0D Elements
        for i in range(10):
            self.mesh_tetra.Add0DElement( i+1 )
        self.group_tetra_0D_elements = self.mesh_tetra.CreateEmptyGroup(SMESH.ELEM0D, "subset_0D_elements") # type "SMESH._objref_SMESH_Group"
        self.group_tetra_0D_elements.AddFrom(self.mesh_tetra.GetMesh())

        for i in range(4):
            self.mesh_tetra.Add0DElement( i+15 ) # those are only in the main-mesh

        # adding Ball Elements
        for i in range(6):
            self.mesh_hexa.AddBall(i+1, i*6+1)
        self.group_hexa_ball_elements = self.mesh_hexa.CreateEmptyGroup(SMESH.BALL, "subset_ball_elements") # type "SMESH._objref_SMESH_Group"
        self.group_hexa_ball_elements.AddFrom(self.mesh_hexa.GetMesh())

        for i in range(11):
            self.mesh_hexa.AddBall(i+15, i+2) # those are only in the main-mesh

        # creating more mesh groups
        self.group_tetra_f1_nodes = self.mesh_tetra.GroupOnGeom(self.face_1,'face_1_nodes',SMESH.NODE) # type "SMESH._objref_SMESH_GroupOnGeom"
        self.group_tetra_f1_faces = self.mesh_tetra.GroupOnGeom(self.face_1,'face_1_faces',SMESH.FACE) # type "SMESH._objref_SMESH_GroupOnGeom"

        criteria = [self.smesh.GetCriterion(SMESH.EDGE, SMESH.FT_Length, SMESH.FT_LessThan, 150)]
        filter_1 = self.smesh.GetFilterFromCriteria(criteria)
        filter_1.SetMesh(self.mesh_hexa.GetMesh())
        self.group_hexa_edges = self.mesh_hexa.GroupOnFilter( SMESH.EDGE, 'group_edges', filter_1) # type "SMESH._objref_SMESH_GroupOnFilter"

        # using random names since they are not used so far
        self.sub_mesh_tetra_f_1 = self.mesh_tetra.GetSubMesh( self.face_1, 'Sub-mesh_1' )
        self.sub_mesh_tetra_f_2 = self.mesh_tetra.GetSubMesh( self.face_2, 'Sub-mesh_2' )
        self.sub_mesh_tetra_e_1 = self.mesh_tetra.GetSubMesh( self.edge_1, 'Sub-mesh_3' )
        self.sub_mesh_tetra_e_2 = self.mesh_tetra.GetSubMesh( self.edge_2, 'Sub-mesh_4' )
        self.sub_mesh_tetra_g_1 = self.mesh_tetra.GetSubMesh( self.group_faces, 'Sub-mesh_5' )
        self.sub_mesh_tetra_g_2 = self.mesh_tetra.GetSubMesh( self.group_edges, 'Sub-mesh_6' )

        self.sub_mesh_hexa_f_1 = self.mesh_hexa.GetSubMesh( self.face_1, 'Sub-mesh_7' )
        self.sub_mesh_hexa_f_2 = self.mesh_hexa.GetSubMesh( self.face_2, 'Sub-mesh_8' )
        self.sub_mesh_hexa_e_1 = self.mesh_hexa.GetSubMesh( self.edge_1, 'Sub-mesh_9' )
        self.sub_mesh_hexa_e_2 = self.mesh_hexa.GetSubMesh( self.edge_2, 'Sub-mesh_10' )
        self.sub_mesh_hexa_g_1 = self.mesh_hexa.GetSubMesh( self.group_faces, 'Sub-mesh_11' )
        self.name_mesh_group = "name_mesh_group"
        self.sub_mesh_hexa_g_2 = self.mesh_hexa.GetSubMesh( self.group_edges, self.name_mesh_group )


def CompareMdpaWithReferenceFile(mdpa_file_name, UnitTestObject):
    """This function compares two mdpa files
    """
    def GetFileLines(ref_mdpa_file, other_mdpa_file):
        """This function reads the reference and the output file
        It returns the lines read from both files and also compares
        if they contain the same numer of lines
        """
        # check if files are valid
        err_msg  = 'The specified reference file name "'
        err_msg += ref_mdpa_file
        err_msg += '" is not valid!'
        UnitTestObject.assertTrue(os.path.isfile(ref_mdpa_file), msg=err_msg)

        err_msg  = 'The specified output file name "'
        err_msg += other_mdpa_file
        err_msg += '" is not valid!'
        UnitTestObject.assertTrue(os.path.isfile(other_mdpa_file), msg=err_msg)

        # "readlines" adds a newline at the end of the line,
        # which will be removed with rstrip afterwards
        with open(ref_mdpa_file,'r') as ref_file:
            lines_ref = ref_file.readlines()
        with open(other_mdpa_file,'r') as out_file:
            lines_out = out_file.readlines()

        # removing trailing newline AND whitespaces (beginning & end) than can mess with the comparison
        # furthermore convert tabs to spaces
        lines_ref = [line.rstrip().lstrip().replace("\t", " ") for line in lines_ref]
        lines_out = [line.rstrip().lstrip().replace("\t", " ") for line in lines_out]

        num_lines_ref = len(lines_ref)
        num_lines_out = len(lines_out)

        err_msg  = "Files have different number of lines!"
        err_msg += "\nNum Lines Reference File: " + str(num_lines_ref)
        err_msg += "\nNum Lines Other File: " + str(num_lines_out)
        UnitTestObject.assertEqual(num_lines_ref, num_lines_out, msg=err_msg)

        return lines_ref, lines_out

    def CompareNodes(lines_ref, lines_out, line_index):
        line_index += 1 # skip the "Begin" line

        while not lines_ref[line_index].split(" ")[0] == "End":
            line_ref_splitted = lines_ref[line_index].split(" ")
            line_out_splitted = lines_out[line_index].split(" ")
            UnitTestObject.assertEqual(len(line_ref_splitted), len(line_out_splitted), msg="Line {}: Node format is not correct!".format(line_index+1))

            # compare node Id
            UnitTestObject.assertEqual(int(line_ref_splitted[0]), int(line_out_splitted[0]), msg="Line {}: Node Ids do not match!".format(line_index+1))

            # compare node coordinates
            for i in range(1,4):
                ref_coord = float(line_ref_splitted[i])
                out_coord = float(line_out_splitted[i])
                UnitTestObject.assertAlmostEqual(ref_coord, out_coord, msg="Line {}: Node Coordinates do not match!".format(line_index+1))

            line_index += 1

        return line_index+1

    def CompareGeometricalObjects(lines_ref, lines_out, line_index):
        # compare entity types (Elements or Conditions)
        UnitTestObject.assertEqual(lines_ref[line_index], lines_out[line_index])

        line_index += 1 # skip the "Begin" line

        while not lines_ref[line_index].split(" ")[0] == "End":
            line_ref_splitted = lines_ref[line_index].split(" ")
            line_out_splitted = lines_out[line_index].split(" ")

            UnitTestObject.assertListEqual(line_ref_splitted, line_out_splitted)

            line_index += 1

        return line_index+1

    def CompareSubModelParts(lines_ref, lines_out, line_index):
        while not lines_ref[line_index].split(" ")[0] == "End":
            if lines_ref[line_index].startswith("Begin SubModelPartData"):
                line_index = CompareKeyValueData(lines_ref, lines_out, line_index)

            UnitTestObject.assertEqual(lines_ref[line_index], lines_out[line_index])
            line_index += 1

        UnitTestObject.assertEqual(lines_ref[line_index+1], lines_out[line_index+1]) # compare "End" line

        return line_index+1

    def CompareEntityValues(line_ref_splitted, line_out_splitted, line_index):
        UnitTestObject.assertEqual(len(line_ref_splitted), len(line_out_splitted), msg="Line {}: Data format is not correct!".format(line_index+1))
        # compare data key
        UnitTestObject.assertEqual(line_ref_splitted[0], line_out_splitted[0], msg="Line {}: Data Keys do not match!".format(line_index+1))

        # compare data value
        if len(line_ref_splitted) == 2: # normal key-value pair
            try: # check if the value can be converted to float
                val_ref = float(line_ref_splitted[1])
                val_is_float = True
            except ValueError:
                val_is_float = False

            if val_is_float:
                val_ref = float(line_ref_splitted[1])
                val_out = float(line_out_splitted[1])
                UnitTestObject.assertAlmostEqual(val_ref, val_out, msg="Line {}: Value does not match!".format(line_index+1))
            else:
                UnitTestObject.assertEqual(line_ref_splitted[1], line_out_splitted[1], msg="Line {}: Value does not match!".format(line_index+1))

        elif len(line_ref_splitted) == 3: # vector or matrix
            def StripLeadingAndEndingCharacter(the_string):
                # e.g. "[12]" => "12"
                return the_string[1:-1]

            def ReadValues(the_string):
                the_string = the_string.replace("(", "").replace(")", "")
                return [float(s) for s in the_string.split(",")]

            def ReadVector(line_with_vector_splitted):
                size_vector = int(StripLeadingAndEndingCharacter(line_with_vector_splitted[1]))
                UnitTestObject.assertGreater(size_vector, 0)
                values_vector = ReadValues(line_with_vector_splitted[2])
                UnitTestObject.assertEqual(size_vector, len(values_vector))
                return size_vector, values_vector

            def ReadMatrix(line_with_matrix_splitted):
                    # "serializes" the values which is ok for testing
                    # only thing that cannot be properly tested this way is the num of rows & cols
                    # however probably not worth the effort
                    sizes_as_string = StripLeadingAndEndingCharacter(line_with_matrix_splitted[1])
                    sizes_splitted = sizes_as_string.split(",")
                    UnitTestObject.assertEqual(len(sizes_splitted), 2)
                    num_rows = int(sizes_splitted[0])
                    num_cols = int(sizes_splitted[1])
                    UnitTestObject.assertGreater(num_rows, 0)
                    UnitTestObject.assertGreater(num_cols, 0)

                    values_matrix = ReadValues(line_with_matrix_splitted[2])
                    UnitTestObject.assertEqual(len(values_matrix), num_rows*num_cols)
                    return num_rows, num_cols, values_matrix

            if "," in line_ref_splitted[1]: # matrix
                num_rows_ref, num_cols_ref, vals_mat_ref = ReadMatrix(line_ref_splitted)
                num_rows_out, num_cols_out, vals_mat_out = ReadMatrix(line_out_splitted)

                UnitTestObject.assertEqual(num_rows_ref, num_rows_out)
                UnitTestObject.assertEqual(num_cols_ref, num_cols_out)

                for val_ref, val_out in zip(vals_mat_ref, vals_mat_out):
                    UnitTestObject.assertAlmostEqual(val_ref, val_out)

            else: # vector
                size_vec_ref, vals_vec_ref = ReadVector(line_ref_splitted)
                size_vec_out, vals_vec_out = ReadVector(line_out_splitted)

                UnitTestObject.assertEqual(size_vec_ref, size_vec_out)

                for val_ref, val_out in zip(vals_vec_ref, vals_vec_out):
                    UnitTestObject.assertAlmostEqual(val_ref, val_out)

        else:
            raise Exception("Line {}: Data Value has too many entries!".format(line_index+1))

    def CompareEntitiyData(lines_ref, lines_out, line_index):
        UnitTestObject.assertEqual(lines_ref[line_index], lines_out[line_index])
        is_nodal_data = ("Nodal" in lines_ref[line_index])

        line_index += 1 # skip the "Begin" line

        while not lines_ref[line_index].split(" ")[0] == "End":
            line_ref_splitted = lines_ref[line_index].split(" ")
            line_out_splitted = lines_out[line_index].split(" ")
            if is_nodal_data:
                # removing the "fixity"
                line_ref_splitted.pop(1)
                line_out_splitted.pop(1)

            CompareEntityValues(line_ref_splitted, line_out_splitted, line_index)

            line_index += 1

        return line_index+1

    def CompareKeyValueData(lines_ref, lines_out, line_index):
        # compare entity types (Elements or Conditions)
        ref_type = lines_ref[line_index].split(" ")[1]
        out_type = lines_out[line_index].split(" ")[1]
        UnitTestObject.assertEqual(ref_type, out_type, msg="Line {}: Types do not match!".format(line_index+1))

        line_index += 1 # skip the "Begin" line

        while not lines_ref[line_index].split(" ")[0] == "End":
            line_ref_splitted = lines_ref[line_index].split(" ")
            line_out_splitted = lines_out[line_index].split(" ")

            CompareEntityValues(line_ref_splitted, line_out_splitted, line_index)

            line_index += 1

        return line_index+1

    def CompareMdpaFiles(ref_mdpa_file, other_mdpa_file):
        lines_ref, lines_out = GetFileLines(ref_mdpa_file, other_mdpa_file)

        line_index = 0
        while line_index < len(lines_ref):
            ref_line_splitted = lines_ref[line_index].split(" ")

            if lines_ref[line_index].startswith("//"):
                if line_index > 0: # skip first line as this contains the date and time
                    UnitTestObject.assertEqual(lines_ref[line_index], lines_out[line_index])
                line_index += 1

            elif ref_line_splitted[0] == "Begin":
                comparison_type = ref_line_splitted[1]

                if comparison_type == "Nodes":
                    line_index = CompareNodes(lines_ref, lines_out, line_index)

                elif comparison_type == "Elements" or comparison_type == "Conditions":
                    line_index = CompareGeometricalObjects(lines_ref, lines_out, line_index)

                elif comparison_type in ["SubModelPart", "SubModelPartNodes", "SubModelPartElements", "SubModelPartConditions"]:
                    line_index = CompareSubModelParts(lines_ref, lines_out, line_index)

                elif comparison_type in ["NodalData", "ElementalData", "ConditionalData"]:
                    line_index = CompareEntitiyData(lines_ref, lines_out, line_index)

                elif comparison_type in ["Properties", "ModelPartData", "SubModelPartData"]:
                    line_index = CompareKeyValueData(lines_ref, lines_out, line_index)

                else:
                    raise Exception('Comparison for "{}" not implemented!'.format(comparison_type))

            else:
                line_index += 1


    if not mdpa_file_name.endswith(".mdpa"):
        mdpa_file_name += ".mdpa"

    # the naming has to follow a certain style!
    ref_file_name = os.path.join(GetTestsDir(), "mdpa_ref_files", "ref_"+mdpa_file_name)
    CompareMdpaFiles(ref_file_name, mdpa_file_name)
    os.remove(mdpa_file_name) # remove file (only done if test is successful!)
