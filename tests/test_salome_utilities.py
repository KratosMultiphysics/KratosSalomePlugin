#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher
#

# python imports
import unittest, sys, os

# plugin imports
sys.path.append(os.pardir) # required to be able to do "from plugin import xxx"
from plugin.utilities import utils

# tests imports
import testing_utilities

if utils.IsExecutedInSalome():
    # imports that have dependenices on salome, hence can only be imported if executed in salome
    import salome_study
    import plugin.utilities.salome_utilities as salome_utils


class TestSalomeTestCaseStudyCleaning(testing_utilities.SalomeTestCase):
    # test to make sure that the cleaning of studies between tests works correctly

    # the order of execution is not deterministic, hence we need a flag
    already_executed = False
    num_objs_in_study = None
xxxx
    def setUp(self):
        super(TestSalomeTestCaseStudyCleaning, self).setUp()

        # create geometry
        O = self.geompy.MakeVertex(0, 0, 0)
        OX = self.geompy.MakeVectorDXDYDZ(1, 0, 0)
        OY = self.geompy.MakeVectorDXDYDZ(0, 1, 0)
        OZ = self.geompy.MakeVectorDXDYDZ(0, 0, 1)
        Box_1 = self.geompy.MakeBoxDXDYDZ(200, 200, 200)
        self.geompy.addToStudy( O, 'O' )
        self.geompy.addToStudy( OX, 'OX' )
        self.geompy.addToStudy( OY, 'OY' )
        self.geompy.addToStudy( OZ, 'OZ' )
        self.geompy.addToStudy( Box_1, 'Box_1' )

        # create mesh
        from salome.smesh import smeshBuilder
        Mesh_1 = self.smesh.Mesh(Box_1)
        Regular_1D = Mesh_1.Segment()
        Max_Size_1 = Regular_1D.MaxSize(34.641)
        MEFISTO_2D = Mesh_1.Triangle(algo=smeshBuilder.MEFISTO)
        NETGEN_3D = Mesh_1.Tetrahedron()
        isDone = Mesh_1.Compute()

        ## Set names of Mesh objects
        self.smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
        self.smesh.SetName(NETGEN_3D.GetAlgorithm(), 'NETGEN 3D')
        self.smesh.SetName(MEFISTO_2D.GetAlgorithm(), 'MEFISTO_2D')
        self.smesh.SetName(Max_Size_1, 'Max Size_1')
        self.smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')

    def test_1(self):
        self.__CheckStudy()

    def test_2(self):
        self.__CheckStudy()

    def __CheckStudy(self):
        if TestSalomeTestCaseStudyCleaning.already_executed:
            # make sure the number of components is the same!
            current_num_objs_in_study = GetNumberOfObjectsInStudy(self.study)
            # if this check fails it means that the study was not cleaned, leftover objects exist!
            self.assertEqual(current_num_objs_in_study, TestSalomeTestCaseStudyCleaning.num_objs_in_study)
        else:
            TestSalomeTestCaseStudyCleaning.already_executed = True
            # if executed for the first time then count the components
            TestSalomeTestCaseStudyCleaning.num_objs_in_study = GetNumberOfObjectsInStudy(self.study)


def GetNumberOfObjectsInStudy(the_study):
    # adapted from python script "salome_study" in KERNEL py-scripts
    def GetNumberOfObjectsInComponent(SO):
        num_objs_in_comp = 0
        it = the_study.NewChildIterator(SO)
        while it.More():
            CSO = it.Value()
            num_objs_in_comp += 1 + GetNumberOfObjectsInComponent(CSO)
            it.Next()
        return num_objs_in_comp

    fct_args = []
    if salome_utils.GetVersionMajor() < 9:
        fct_args.append(the_study)
    # salome_study.DumpStudy(*fct_args) # for debugging

    itcomp = the_study.NewComponentIterator()
    num_objs_in_study = 0
    while itcomp.More(): # loop components (e.g. GEOM, SMESH)
        SC = itcomp.Value()
        num_objs_in_study += 1 + GetNumberOfObjectsInComponent(SC)
        itcomp.Next()
    return num_objs_in_study


class TestSalomeUtilities(testing_utilities.SalomeTestCase):

    def setUp(self):
        super(TestSalomeUtilities, self).setUp()
        # create some entities needed in the testing

    # def test_IsMesh(self):
    #     self.assertTrue(self.main_mesh)
    #     self.assertFalse(self.sub_mesh_1)
    #     self.assertFalse(self.mesh_group_1)

    #     self.assertFalse(self.main_geom)
    #     self.assertFalse(self.sub_geom_1)
    #     self.assertFalse(self.geom_group_1)

    # def test_IsSubMesh(self):
    #     self.assertFalse(self.main_mesh)
    #     self.assertTrue(self.sub_mesh_1)
    #     self.assertFalse(self.mesh_group_1)

    #     self.assertFalse(self.main_geom)
    #     self.assertFalse(self.sub_geom_1)
    #     self.assertFalse(self.geom_group_1)

    # def test_IsMeshGroup(self):
    #     self.assertFalse(self.main_mesh)
    #     self.assertFalse(self.sub_mesh_1)
    #     self.assertTrue(self.mesh_group_1)

    #     self.assertFalse(self.main_geom)
    #     self.assertFalse(self.sub_geom_1)
    #     self.assertFalse(self.geom_group_1)

    def test_ExportMeshToDat(self):
        pass

    def test_GetMeshIdentifierFromSelection(self):
        pass


if __name__ == '__main__':
    unittest.main()
