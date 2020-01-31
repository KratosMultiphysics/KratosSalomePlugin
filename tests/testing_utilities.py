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
import unittest, sys, os

# plugin imports
sys.path.append(os.pardir) # required to be able to do "from plugin import xxx"
from plugin.utilities import utils

if utils.IsExecutedInSalome():
    # imports that have dependenices on salome, hence can only be imported if executed in salome
    import salome
    import plugin.utilities.salome_utilities as salome_utils

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


@unittest.skipUnless(utils.IsExecutedInSalome(), "This test can only be executed in Salome")
class SalomeTestCase(unittest.TestCase):

    def setUp(self):
        # initializing salome also creates a study.
        # closing and creating a new study (salome < 9) or clearing the study (salome >= 9)
        # in order to have a clean study for each test.
        # This is much faster than re-launching salome for each test
        # Note: The behavior is quite different between different versions of salome,
        # since from version 9 salome is single study, before multiple studies were possible!
        # This also requires different arguments for some functions

        if salome_utils.GetVersionMajor() < 9:
            self.__CloseOpenStudies()

            salome.createNewStudy()

            open_studies = salome.myStudyManager.GetOpenStudies()
            num_open_studies = len(open_studies)
            if num_open_studies != 1:
                raise Exception("Wrong number of open studies: {}".format(num_open_studies))

            self.study = salome.myStudyManager.GetStudyByName(open_studies[0])

            self.geompy = geomBuilder.New(self.study)
            self.smesh = smeshBuilder.New(self.study)

        else:
            self.study = salome.myStudy
            self.study.Clear()
            salome.salome_study_init()

            self.geompy = geomBuilder.New()
            self.smesh = smeshBuilder.New()

    @classmethod
    def tearDownClass(cls):
        # make sure to clean leftovers, otherwise can cause errors at exit
        if salome_utils.GetVersionMajor() < 9:
            cls.__CloseOpenStudies()

    @classmethod
    def __CloseOpenStudies(cls):
        if salome_utils.GetVersionMajor() >= 9:
            raise Exception("This method can only be used with versions < 9!")

        for study_id in salome.myStudyManager.GetOpenStudies():
            salome.myStudyManager.Close(salome.myStudyManager.GetStudyByName(study_id))

        num_open_studies = len(salome.myStudyManager.GetOpenStudies())
        if num_open_studies != 0:
            raise Exception("{} open studies still exist!".format(num_open_studies))

    def GetSalomeID(self, salome_object, expected_id):
        # this function returns the ID of a given salome object, which is only useful for tests so far
        # unfortunately "salome.ObjectToID" seems not to work with salome versions < 9
        # due to this reason the expected ID has to be provided
        # in newer versions it is checked if it is the same as the actual ID of the object
        if salome_utils.GetVersionMajor() >= 9:
            self.assertEqual(expected_id, salome.ObjectToID(salome_object))

        return expected_id


class SalomeTestCaseWithBox(SalomeTestCase):
    # a test case that has a simple box with a tetra and hexa mesh as setup

    def setUp(self):
        super(SalomeTestCaseWithBox, self).setUp()

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
