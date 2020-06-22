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
import kratos_salome_plugin.utilities as utils

if utils.IsExecutedInSalome():
    # Check https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html for how to handle study
    # imports that have dependenices on salome, hence can only be imported if executed in salome
    import salome
    import kratos_salome_plugin.salome_dependent.salome_utilities as salome_utils

    # initialize salome, should be done only once
    salome.salome_init()

    # importing important modules, explicitly done after salome_init
    # not sure if the order is important, but this is how it is done in the dumped studies
    import GEOM
    from salome.geom import geomBuilder

    import SMESH
    from salome.smesh import smeshBuilder

from PyQt5.QtGui import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt


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
        salome_utils.ResetStudy()
        self.assertEqual(GetNumberOfObjectsInStudy(), 0, msg="Resetting the study failed!")

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


class SalomeTestCaseCantilever2D(SalomeTestCase):
    # a test case that has a simple 2D cantilever

    def setUp(self):
        super().setUp()

        debug = False

        # creating geometry
        self.O = self.geompy.MakeVertex(0, 0, 0)
        self.OX = self.geompy.MakeVectorDXDYDZ(1, 0, 0)
        self.OY = self.geompy.MakeVectorDXDYDZ(0, 1, 0)
        self.OZ = self.geompy.MakeVectorDXDYDZ(0, 0, 1)
        self.Vertex_1 = self.geompy.MakeVertex(0, 0, 0)
        self.Vertex_2 = self.geompy.MakeVertex(5, 0, 0)
        self.Vertex_3 = self.geompy.MakeVertex(5, 1, 0)
        self.Vertex_4 = self.geompy.MakeVertex(0, 1, 0)
        self.Line_1 = self.geompy.MakeLineTwoPnt(self.Vertex_1, self.Vertex_2)
        self.Line_2 = self.geompy.MakeLineTwoPnt(self.Vertex_2, self.Vertex_3)
        self.Line_3 = self.geompy.MakeLineTwoPnt(self.Vertex_3, self.Vertex_4)
        self.Line_4 = self.geompy.MakeLineTwoPnt(self.Vertex_4, self.Vertex_1)
        self.Face_1 = self.geompy.MakeFaceWires([self.Line_1, self.Line_2, self.Line_3, self.Line_4], 1)
        [self.Neumann,self.Dirichlet] = self.geompy.SubShapes(self.Face_1, [6, 10])

        # publish geometry ( only in debug)
        if debug:
            self.geompy.addToStudy( self.O, 'O' )
            self.geompy.addToStudy( self.OX, 'OX' )
            self.geompy.addToStudy( self.OY, 'OY' )
            self.geompy.addToStudy( self.OZ, 'OZ' )
            self.geompy.addToStudy( self.Vertex_1, 'Vertex_1' )
            self.geompy.addToStudy( self.Vertex_2, 'Vertex_2' )
            self.geompy.addToStudy( self.Vertex_3, 'Vertex_3' )
            self.geompy.addToStudy( self.Vertex_4, 'Vertex_4' )
            self.geompy.addToStudy( self.Line_1, 'Line_1' )
            self.geompy.addToStudy( self.Line_2, 'Line_2' )
            self.geompy.addToStudy( self.Line_3, 'Line_3' )
            self.geompy.addToStudy( self.Line_4, 'Line_4' )
            self.geompy.addToStudy( self.Face_1, 'domain' )
            self.geompy.addToStudyInFather( self.Face_1, self.Neumann, 'Neumann' )
            self.geompy.addToStudyInFather( self.Face_1, self.Dirichlet, 'Dirichlet' )

        # creating mesh
        self.smeshObj_1 = self.smesh.CreateHypothesis('MaxLength')
        self.smeshObj_2 = self.smesh.CreateHypothesis('NumberOfSegments')
        self.domain_mesh = self.smesh.Mesh(self.Face_1)
        self.Regular_1D = self.domain_mesh.Segment()
        self.Local_Length_1 = self.Regular_1D.LocalLength(1,None,1e-07)
        self.Quadrangle_2D = self.domain_mesh.Quadrangle(algo=smeshBuilder.QUADRANGLE)
        self.Local_Length_1.SetLength( 0.2 )
        self.Local_Length_1.SetPrecision( 1e-07 )
        isDone = self.domain_mesh.Compute()
        self.assertTrue(isDone, msg="Mesh could not be computed!")
        self.neumann_mesh = self.domain_mesh.GetSubMesh( self.Neumann, 'neumann' )
        self.dirichlet_mesh = self.domain_mesh.GetSubMesh( self.Dirichlet, 'dirichlet' )

        if debug:
            self.smesh.SetName(self.Regular_1D.GetAlgorithm(), 'Regular_1D')
            self.smesh.SetName(self.Quadrangle_2D.GetAlgorithm(), 'Quadrangle_2D')
            self.smesh.SetName(self.Local_Length_1, 'Local Length_1')
            self.smesh.SetName(self.domain_mesh.GetMesh(), 'domain_mesh')
            self.smesh.SetName(self.dirichlet_mesh, 'dirichlet')
            self.smesh.SetName(self.neumann_mesh, 'neumann')

            salome.myStudy.SaveAs("SalomeTestCaseCantilever2D.hdf", False, False) # args: use_multifile, use_acsii


def CompareMdpaWithReferenceFile(mdpa_file_name, test_case):
    """This function compares two mdpa files"""

    def GetFileLines(ref_mdpa_file, other_mdpa_file):
        """This function reads the reference and the output file
        It returns the lines read from both files and also compares
        if they contain the same numer of lines
        """
        # check if files are valid
        err_msg  = 'The specified reference file name "'
        err_msg += ref_mdpa_file
        err_msg += '" is not valid!'
        test_case.assertTrue(os.path.isfile(ref_mdpa_file), msg=err_msg)

        err_msg  = 'The specified output file name "'
        err_msg += other_mdpa_file
        err_msg += '" is not valid!'
        test_case.assertTrue(os.path.isfile(other_mdpa_file), msg=err_msg)

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
        test_case.assertEqual(num_lines_ref, num_lines_out, msg=err_msg)

        return lines_ref, lines_out

    def CompareNodes(lines_ref, lines_out, line_index):
        line_index += 1 # skip the "Begin" line

        while not lines_ref[line_index].split(" ")[0] == "End":
            line_ref_splitted = lines_ref[line_index].split(" ")
            line_out_splitted = lines_out[line_index].split(" ")
            test_case.assertEqual(len(line_ref_splitted), len(line_out_splitted), msg="Line {}: Node format is not correct!".format(line_index+1))

            # compare node Id
            test_case.assertEqual(int(line_ref_splitted[0]), int(line_out_splitted[0]), msg="Line {}: Node Ids do not match!".format(line_index+1))

            # compare node coordinates
            for i in range(1,4):
                ref_coord = float(line_ref_splitted[i])
                out_coord = float(line_out_splitted[i])
                test_case.assertAlmostEqual(ref_coord, out_coord, msg="Line {}: Node Coordinates do not match!".format(line_index+1))

            line_index += 1

        return line_index+1

    def CompareGeometricalObjects(lines_ref, lines_out, line_index):
        # compare entity types (Elements or Conditions)
        test_case.assertEqual(lines_ref[line_index], lines_out[line_index])

        line_index += 1 # skip the "Begin" line

        while not lines_ref[line_index].split(" ")[0] == "End":
            line_ref_splitted = lines_ref[line_index].split(" ")
            line_out_splitted = lines_out[line_index].split(" ")

            test_case.assertListEqual(line_ref_splitted, line_out_splitted)

            line_index += 1

        return line_index+1

    def CompareSubModelParts(lines_ref, lines_out, line_index):
        while not lines_ref[line_index].split(" ")[0] == "End":
            if lines_ref[line_index].startswith("Begin SubModelPartData"):
                line_index = CompareKeyValueData(lines_ref, lines_out, line_index)

            test_case.assertEqual(lines_ref[line_index], lines_out[line_index])
            line_index += 1

        test_case.assertEqual(lines_ref[line_index+1], lines_out[line_index+1]) # compare "End" line

        return line_index+1

    def CompareEntityValues(line_ref_splitted, line_out_splitted, line_index):
        test_case.assertEqual(len(line_ref_splitted), len(line_out_splitted), msg="Line {}: Data format is not correct!".format(line_index+1))
        # compare data key
        test_case.assertEqual(line_ref_splitted[0], line_out_splitted[0], msg="Line {}: Data Keys do not match!".format(line_index+1))

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
                test_case.assertAlmostEqual(val_ref, val_out, msg="Line {}: Value does not match!".format(line_index+1))
            else:
                test_case.assertEqual(line_ref_splitted[1], line_out_splitted[1], msg="Line {}: Value does not match!".format(line_index+1))

        elif len(line_ref_splitted) == 3: # vector or matrix
            def StripLeadingAndEndingCharacter(the_string):
                # e.g. "[12]" => "12"
                return the_string[1:-1]

            def ReadValues(the_string):
                the_string = the_string.replace("(", "").replace(")", "")
                return [float(s) for s in the_string.split(",")]

            def ReadVector(line_with_vector_splitted):
                size_vector = int(StripLeadingAndEndingCharacter(line_with_vector_splitted[1]))
                test_case.assertGreater(size_vector, 0)
                values_vector = ReadValues(line_with_vector_splitted[2])
                test_case.assertEqual(size_vector, len(values_vector))
                return size_vector, values_vector

            def ReadMatrix(line_with_matrix_splitted):
                    # "serializes" the values which is ok for testing
                    # only thing that cannot be properly tested this way is the num of rows & cols
                    # however probably not worth the effort
                    sizes_as_string = StripLeadingAndEndingCharacter(line_with_matrix_splitted[1])
                    sizes_splitted = sizes_as_string.split(",")
                    test_case.assertEqual(len(sizes_splitted), 2)
                    num_rows = int(sizes_splitted[0])
                    num_cols = int(sizes_splitted[1])
                    test_case.assertGreater(num_rows, 0)
                    test_case.assertGreater(num_cols, 0)

                    values_matrix = ReadValues(line_with_matrix_splitted[2])
                    test_case.assertEqual(len(values_matrix), num_rows*num_cols)
                    return num_rows, num_cols, values_matrix

            if "," in line_ref_splitted[1]: # matrix
                num_rows_ref, num_cols_ref, vals_mat_ref = ReadMatrix(line_ref_splitted)
                num_rows_out, num_cols_out, vals_mat_out = ReadMatrix(line_out_splitted)

                test_case.assertEqual(num_rows_ref, num_rows_out)
                test_case.assertEqual(num_cols_ref, num_cols_out)

                for val_ref, val_out in zip(vals_mat_ref, vals_mat_out):
                    test_case.assertAlmostEqual(val_ref, val_out)

            else: # vector
                size_vec_ref, vals_vec_ref = ReadVector(line_ref_splitted)
                size_vec_out, vals_vec_out = ReadVector(line_out_splitted)

                test_case.assertEqual(size_vec_ref, size_vec_out)

                for val_ref, val_out in zip(vals_vec_ref, vals_vec_out):
                    test_case.assertAlmostEqual(val_ref, val_out)

        else:
            raise Exception("Line {}: Data Value has too many entries!".format(line_index+1))

    def CompareEntitiyData(lines_ref, lines_out, line_index):
        test_case.assertEqual(lines_ref[line_index], lines_out[line_index])
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
        test_case.assertEqual(ref_type, out_type, msg="Line {}: Types do not match!".format(line_index+1))

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
                    test_case.assertEqual(lines_ref[line_index], lines_out[line_index])
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


def CheckModelPartHierarchie(model_part, hierarchie, test_case):
    """Checking if the hierarchie of a ModelPart matches the expected one
    This is intended to check larger models, where it is not feasible
    save large mdpa-files as references
    the hierarchie is a dict with the structure of the ModelPart. E.g.:
    {
        "name_model_part" : {
            "nodes": 15
            "elements": 11
            "conditions": 5
            "properties": 2,
            "sub_model_parts" : {
                "domain" : {
                    "nodes": 15,
                    "elements" : 11,
                    "properties" :1
                    "sub_model_parts" : {
                        "sub_domain" : {
                            "nodes" : 3,
                            "elements" : 2
                        }
                    }
                },
                "boundary" : {
                    "nodes": 6
                    "conditions" : 5,
                    "properties" : 1
                }
                }
            }
        }
    }
    """
    def CheckModelPartHierarchieNumbers(smp, smp_hierarchie):
        exp_num = smp_hierarchie.get("nodes", 0)
        test_case.assertEqual(smp.NumberOfNodes(), exp_num, msg='ModelPart "{}" is expected to have {} nodes but has {}'.format(smp.FullName(), exp_num, smp.NumberOfNodes()))

        exp_num = smp_hierarchie.get("elements", 0)
        test_case.assertEqual(smp.NumberOfElements(), exp_num, msg='ModelPart "{}" is expected to have {} elements but has {}'.format(smp.FullName(), exp_num, smp.NumberOfElements()))

        exp_num = smp_hierarchie.get("conditions", 0)
        test_case.assertEqual(smp.NumberOfConditions(), exp_num, msg='ModelPart "{}" is expected to have {} conditions but has {}'.format(smp.FullName(), exp_num, smp.NumberOfConditions()))

        exp_num = smp_hierarchie.get("properties", 0)
        test_case.assertEqual(smp.NumberOfProperties(), exp_num, msg='ModelPart "{}" is expected to have {} properties but has {}'.format(smp.FullName(), exp_num, smp.NumberOfProperties()))

        if "sub_model_parts" in smp_hierarchie:
            smp_hierarchie = smp_hierarchie["sub_model_parts"]
            for name_smp in smp_hierarchie:
                test_case.assertTrue(smp.HasSubModelPart(name_smp), msg='ModelPart "{}" does not have SubModelPart with name "{}"'.format(smp.FullName(), name_smp))
                CheckModelPartHierarchieNumbers(smp.GetSubModelPart(name_smp), smp_hierarchie[name_smp])

    # check name of MainModelPart
    test_case.assertEqual(len(hierarchie), 1)
    name_main_model_part = hierarchie.__iter__().__next__()
    test_case.assertEqual(model_part.Name, name_main_model_part)

    CheckModelPartHierarchieNumbers(model_part, hierarchie[name_main_model_part])



def GetNumberOfObjectsInStudy():
    """Counts the number of objects in the study, for all components
    adapted from python script "salome_study" in KERNEL py-scripts
    """
    def GetNumberOfObjectsInComponent(SO):
        """Counts the number of objects in a component (e.g. GEOM, SMESH)"""
        num_objs_in_comp = 0
        it = salome.myStudy.NewChildIterator(SO)
        while it.More():
            CSO = it.Value()
            num_objs_in_comp += 1 + GetNumberOfObjectsInComponent(CSO)
            it.Next()
        return num_objs_in_comp

    # salome.myStudy.DumpStudy() # for debugging

    itcomp = salome.myStudy.NewComponentIterator()
    num_objs_in_study = 0
    while itcomp.More(): # loop components (e.g. GEOM, SMESH)
        SC = itcomp.Value()
        num_objs_in_study += 1 + GetNumberOfObjectsInComponent(SC)
        itcomp.Next()
    return num_objs_in_study

class ModelPartForTests(object):
    """auxiliary functions for creating entities in ModelParts for testing purposes
    Names of the entities are compatible with Kratos
    """
    @staticmethod
    def CreateNodes(mp):
        for i in range(8):
            mp.CreateNewNode(i+1, i**1.1, i*2.2, 2.6)

    @staticmethod
    def CreateNodesAndLineElements(mp):
        for i in range(6):
            mp.CreateNewNode(i+1, 0.0, 0.0, 0.0) # coordinates do not matter here

        props_1 = mp.CreateNewProperties(1)
        props_2 = mp.CreateNewProperties(15)

        for i in range(10):
            if i%3 == 0:
                props = props_2
            else:
                props = props_1

            mp.CreateNewElement("Element2D2N", i+1, [i%3+1,i%6+1], props)

    @staticmethod
    def CreateNodesAndTriangleConditions(mp):
        for i in range(6):
            mp.CreateNewNode(i+1, 0.0, 0.0, 0.0) # coordinates do not matter here

        props_1 = mp.CreateNewProperties(1)
        props_2 = mp.CreateNewProperties(15)

        for i in range(17):
            if i%5 == 0:
                props = props_2
            else:
                props = props_1

            mp.CreateNewCondition("SurfaceCondition3D3N", i+1, [i%3+1,i%6+1,i%2+1], props)
