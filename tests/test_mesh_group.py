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
import shutil

# plugin imports
sys.path.append(os.pardir) # required to be able to do "from plugin import xxx"
sys.path.append(os.path.join(os.pardir, "plugin")) # required that the imports from the "plugin" folder work inside the py-modules of the plugin
from plugin.mesh_group import MeshGroup
from utilities.utils import IsExecutedInSalome

# tests imports
import testing_utilities
import time

if IsExecutedInSalome():
    from plugin.utilities import salome_utilities
    import salome


# from development.utilities import PrintObjectInfo

class TestMeshGroupObservers(unittest.TestCase):
    def test_observers(self):
        pass


class TestMeshGroupMeshRelatedMethods(testing_utilities.SalomeTestCaseWithBox):

    def setUp(self):
        super(TestMeshGroupMeshRelatedMethods, self).setUp()
        # this also tests the "MeshExists" function right here
        existing_mesh_identifier = self.GetSalomeID(self.mesh_tetra.GetMesh(), "0:1:2:3")
        self.mesh_group_main_mesh_tetra = MeshGroup(existing_mesh_identifier)
        self.assertTrue(self.mesh_group_main_mesh_tetra.MeshExists())

        self.mesh_group_non_exist_mesh = MeshGroup(existing_mesh_identifier)
        self.mesh_group_non_exist_mesh.mesh_identifier = "1:55555:114777" # has to be overwritten, otherwise throws in constructor
        self.assertFalse(self.mesh_group_non_exist_mesh.MeshExists())


    def test_GetNodes_NonExistingMesh(self):
        self.assertEqual({}, self.mesh_group_non_exist_mesh.GetNodes())

    def test_GetNodes_MainMesh(self):
        nodes = self.mesh_group_main_mesh_tetra.GetNodes()
        self.assertEqual(366, len(nodes)) # this might fail if different versions of salome give different meshes
        for node_coords in nodes.values():
            self.assertEqual(3, len(node_coords))

    def test_GetNodes_SubMeshOnEdge(self):
        existing_mesh_identifier = self.GetSalomeID(self.sub_mesh_tetra_e_1, "0:1:2:3:5:1")
        mesh_group = MeshGroup(existing_mesh_identifier)
        nodes = mesh_group.GetNodes()
        self.assertEqual(5, len(nodes)) # this might fail if different versions of salome give different meshes
        # all nodes are on an edge, hence we can test at least for that
        for node_coords in nodes.values():
            self.assertAlmostEqual(200.0, node_coords[0])
            self.assertAlmostEqual(200.0, node_coords[2])

    def test_GetNodes_SubMeshOnFace(self):
        existing_mesh_identifier = self.GetSalomeID(self.sub_mesh_tetra_f_2, "0:1:2:3:7:2")
        mesh_group = MeshGroup(existing_mesh_identifier)
        nodes = mesh_group.GetNodes()
        self.assertEqual(49, len(nodes)) # this might fail if different versions of salome give different meshes
        # all nodes are on a face, hence we can test at least for that
        for node_coords in nodes.values():
            self.assertAlmostEqual(0.0, node_coords[1])

    def test_GetNodes_SubMeshOnEdgeGroup(self):
        existing_mesh_identifier = self.GetSalomeID(self.sub_mesh_hexa_g_2, "0:1:2:4:10:2")
        mesh_group = MeshGroup(existing_mesh_identifier)
        nodes = mesh_group.GetNodes()
        self.assertEqual(32, len(nodes)) # this might fail if different versions of salome give different meshes

    def test_GetNodes_SubMeshOnFaceGroup(self):
        existing_mesh_identifier = self.GetSalomeID(self.sub_mesh_tetra_g_1, "0:1:2:3:10:1")
        mesh_group = MeshGroup(existing_mesh_identifier)
        nodes = mesh_group.GetNodes()
        self.assertEqual(98, len(nodes)) # this might fail if different versions of salome give different meshes

    def test_GetGeomEntities_NonExistingMesh(self):
        self.assertEqual(({}, {}), self.mesh_group_non_exist_mesh.GetNodesAndGeometricalEntities([]))

    def test_GetGeomEntities_MainMesh(self):
        pass

    def test_GetGeomEntities_SubMeshOnGeom(self):
        pass

    def test_GetGeomEntities_SubMeshOnGroup(self):
        pass

    def test_GetMeshName(self):
        self.assertEqual(self.name_main_mesh_tetra, self.mesh_group_main_mesh_tetra.GetMeshName())
        self.assertEqual("", self.mesh_group_non_exist_mesh.GetMeshName())

    def test_GetEntityTypesInMesh(self):
        entity_types = self.mesh_group_main_mesh_tetra.GetEntityTypesInMesh()

        print(entity_types)

        for e in entity_types:
            print(type(e))





        # mesh_group = MeshGroup(salome.ObjectToID(self.sub_mesh_tetra_f_1))
        # PrintObjectInfo("self.study", self.study)
        # import salome_study
        # print(salome_study.DumpStudy())
        # print(self.mesh_tetra.GetID)


        # start_time = time.time()
        # print(len(mesh_group.GetNodes()))
        # print("TIME TO GET NODES:", time.time() - start_time)


if __name__ == '__main__':
    unittest.main()
