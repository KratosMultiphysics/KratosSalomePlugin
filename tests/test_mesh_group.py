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
sys.path.append(os.path.join(os.pardir, "plugin")) # required that the imports from the "plugin" folder work inside the py-modules of the plugin
from plugin.mesh_group import MeshGroup
from utilities.utils import IsExecutedInSalome

# tests imports
import testing_utilities
import time

if IsExecutedInSalome():
    from plugin.utilities import salome_utilities
    import salome
    import SMESH


# from development.utilities import PrintObjectInfo

class TestMeshGroupObservers(unittest.TestCase):
    def test_observers(self):
        pass


class TestMeshGroupMeshRelatedMethods(testing_utilities.SalomeTestCaseWithBox):

    def setUp(self):
        super(TestMeshGroupMeshRelatedMethods, self).setUp()
        # this also tests the "MeshExists" function right here
        existing_mesh_identifier = salome_utilities.GetSalomeID(self.mesh_tetra.GetMesh())
        self.mesh_group_main_mesh_tetra = MeshGroup(existing_mesh_identifier)
        self.assertTrue(self.mesh_group_main_mesh_tetra.MeshExists())

        self.mesh_group_non_exist_mesh = MeshGroup(existing_mesh_identifier)
        self.mesh_group_non_exist_mesh.mesh_identifier = "1:55555:114777" # has to be overwritten, otherwise throws in constructor
        self.assertFalse(self.mesh_group_non_exist_mesh.MeshExists())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.mesh_hexa.GetMesh())
        self.mesh_group_main_mesh_hexa = MeshGroup(existing_mesh_identifier)
        self.assertTrue(self.mesh_group_main_mesh_hexa.MeshExists())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_tetra_e_1)
        self.mesh_group_sub_mesh_tetra_edge = MeshGroup(existing_mesh_identifier)
        self.assertTrue(self.mesh_group_sub_mesh_tetra_edge.MeshExists())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_tetra_f_2)
        self.mesh_group_sub_mesh_tetra_face = MeshGroup(existing_mesh_identifier)
        self.assertTrue(self.mesh_group_sub_mesh_tetra_face.MeshExists())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_tetra_g_1)
        self.mesh_group_sub_mesh_group_tetra_face = MeshGroup(existing_mesh_identifier)
        self.assertTrue(self.mesh_group_sub_mesh_group_tetra_face.MeshExists())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_hexa_g_2)
        self.mesh_group_sub_mesh_group_hexa_edge = MeshGroup(existing_mesh_identifier)
        self.assertTrue(self.mesh_group_sub_mesh_group_hexa_edge.MeshExists())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_hexa_g_1)
        self.mesh_group_sub_mesh_group_hexa_face = MeshGroup(existing_mesh_identifier)
        self.assertTrue(self.mesh_group_sub_mesh_group_hexa_face.MeshExists())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_hexa_f_2)
        self.mesh_group_sub_mesh_hexa_face = MeshGroup(existing_mesh_identifier)
        self.assertTrue(self.mesh_group_sub_mesh_hexa_face.MeshExists())


    def test_constructor_exceptions(self):
        with self.assertRaisesRegex(Exception, 'does not exist!'):
            MeshGroup("1:55555:114777")

        with self.assertRaisesRegex(Exception, 'is not a mesh'):
            MeshGroup("0:1:1:1") # using the box


    def test_GetNodes_NonExistingMesh(self):
        self.assertEqual({}, self.mesh_group_non_exist_mesh.GetNodes())

    def test_GetNodes_MainMesh(self):
        nodes = self.mesh_group_main_mesh_tetra.GetNodes()
        self.assertEqual(366, len(nodes)) # this might fail if different versions of salome give different meshes
        for node_coords in nodes.values():
            self.assertEqual(3, len(node_coords))

    def test_GetNodes_SubMeshOnEdge(self):
        nodes = self.mesh_group_sub_mesh_tetra_edge.GetNodes()
        self.assertEqual(5, len(nodes)) # this might fail if different versions of salome give different meshes
        # all nodes are on an edge, hence we can test at least for that
        for node_coords in nodes.values():
            self.assertAlmostEqual(200.0, node_coords[0])
            self.assertAlmostEqual(200.0, node_coords[2])

    def test_GetNodes_SubMeshOnFace(self):
        nodes = self.mesh_group_sub_mesh_tetra_face.GetNodes()
        self.assertEqual(49, len(nodes)) # this might fail if different versions of salome give different meshes
        # all nodes are on a face, hence we can test at least for that
        for node_coords in nodes.values():
            self.assertAlmostEqual(0.0, node_coords[1])

    def test_GetNodes_SubMeshOnTriFaceGroup(self):
        nodes = self.mesh_group_sub_mesh_group_tetra_face.GetNodes()
        self.assertEqual(98, len(nodes)) # this might fail if different versions of salome give different meshes

    def test_GetNodes_SubMeshOnEdgeGroup(self):
        nodes = self.mesh_group_sub_mesh_group_hexa_edge.GetNodes()
        self.assertEqual(32, len(nodes)) # this might fail if different versions of salome give different meshes

    def test_GetNodes_SubMeshOnFaceGroup(self):
        nodes = self.mesh_group_sub_mesh_group_hexa_face.GetNodes()
        self.assertEqual(162, len(nodes)) # this might fail if different versions of salome give different meshes


    def test_GetGeomEntities_NonExistingMesh(self):
        self.assertEqual(({}, {}), self.mesh_group_non_exist_mesh.GetNodesAndGeometricalEntities([]))

    def test_GetGeomEntities_MainMesh_tetra(self):
        entity_types = {
            SMESH.Entity_Triangle : 480,
            SMESH.Entity_Edge     : 48,
            SMESH.Entity_Tetra    : 1355,
            SMESH.Entity_Node     : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_group_main_mesh_tetra, entity_types, 366)

    def test_GetGeomEntities_MainMesh_tetra_retrieve_subset(self):
        entity_types = {
            SMESH.Entity_Triangle : 480,
            SMESH.Entity_Edge     : 48
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_group_main_mesh_tetra, entity_types, 366)

    def test_GetGeomEntities_MainMesh_tetra_retrieve_not_existing(self):
        entity_types = {
            SMESH.Entity_Quadrangle : 0, # no quadrangles in this mesh
            SMESH.Entity_Triangle   : 480,
            SMESH.Entity_Edge       : 48
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_group_main_mesh_tetra, entity_types, 366)

    def test_GetGeomEntities_MainMesh_hexa(self):
        entity_types = {
            SMESH.Entity_Quadrangle : 384,
            SMESH.Entity_Triangle   : 0,
            SMESH.Entity_Edge       : 96,
            SMESH.Entity_Tetra      : 0,
            SMESH.Entity_Hexa       : 512,
            SMESH.Entity_Node       : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_group_main_mesh_hexa, entity_types, 729)

    def test_GetGeomEntities_SubMeshOnGeom_face_tri(self):
        entity_types = {
            SMESH.Entity_Triangle : 80,
            SMESH.Entity_Edge     : 0,
            SMESH.Entity_Tetra    : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_group_sub_mesh_tetra_face, entity_types, 49)

    def test_GetGeomEntities_SubMeshOnGeom_face_quad(self):
        entity_types = {
            SMESH.Entity_Quadrangle : 64,
            SMESH.Entity_Triangle   : 0,
            SMESH.Entity_Edge       : 0,
            SMESH.Entity_Hexa       : 0,
            SMESH.Entity_Tetra      : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_group_sub_mesh_hexa_face, entity_types, 81)

    def test_GetGeomEntities_SubMeshOnGeom_edge(self):
        entity_types = {
            SMESH.Entity_Triangle : 0,
            SMESH.Entity_Edge     : 4,
            SMESH.Entity_Tetra    : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_group_sub_mesh_tetra_edge, entity_types, 5)

    def test_GetGeomEntities_SubMeshOnGroup_face_tri(self):
        entity_types = {
            SMESH.Entity_Quadrangle : 0,
            SMESH.Entity_Triangle   : 160,
            SMESH.Entity_Edge       : 0,
            SMESH.Entity_Hexa       : 0,
            SMESH.Entity_Tetra      : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_group_sub_mesh_group_tetra_face, entity_types, 98)

    def test_GetGeomEntities_SubMeshOnGroup_face_quad(self):
        entity_types = {
            SMESH.Entity_Quadrangle : 128,
            SMESH.Entity_Triangle   : 0,
            SMESH.Entity_Edge       : 0,
            SMESH.Entity_Hexa       : 0,
            SMESH.Entity_Tetra      : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_group_sub_mesh_group_hexa_face, entity_types, 162)

    def test_GetGeomEntities_SubMeshOnGroup_edge(self):
        entity_types = {
            SMESH.Entity_Quadrangle : 0,
            SMESH.Entity_Triangle   : 0,
            SMESH.Entity_Edge       : 32,
            SMESH.Entity_Hexa       : 0,
            SMESH.Entity_Tetra      : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_group_sub_mesh_group_hexa_edge, entity_types, 32)


    def test_GetMeshName(self):
        self.assertEqual(self.name_main_mesh_tetra, self.mesh_group_main_mesh_tetra.GetMeshName())
        self.assertEqual("", self.mesh_group_non_exist_mesh.GetMeshName())


    def test_GetEntityTypesInMesh_NonExistingMesh(self):
        self.assertEqual([], self.mesh_group_non_exist_mesh.GetEntityTypesInMesh())

    def test_GetEntityTypesInMesh_MainMesh(self):
        exp_entity_types = [
            SMESH.Entity_Triangle,
            SMESH.Entity_Edge,
            SMESH.Entity_Node,
            SMESH.Entity_Tetra
        ]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_group_main_mesh_tetra, exp_entity_types)

    def test_GetEntityTypesInMesh_SubMeshOnEdge(self):
        exp_entity_types = [
            SMESH.Entity_Edge,
            SMESH.Entity_Node
        ]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_group_sub_mesh_tetra_edge, exp_entity_types)

    def test_GetEntityTypesInMesh_SubMeshOnFace(self):
        exp_entity_types = [
            SMESH.Entity_Triangle,
            SMESH.Entity_Node
        ]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_group_sub_mesh_tetra_face, exp_entity_types)

    def test_GetEntityTypesInMesh_SubMeshOnEdgeGroup(self):
        exp_entity_types = [
            SMESH.Entity_Edge,
            SMESH.Entity_Node
        ]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_group_sub_mesh_group_hexa_edge, exp_entity_types)

    def test_GetEntityTypesInMesh_SubMeshOnFaceGroup(self):
        exp_entity_types = [
            SMESH.Entity_Quadrangle,
            SMESH.Entity_Node
        ]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_group_sub_mesh_group_hexa_face, exp_entity_types)

    def __Execute_GetEntityTypesInMesh_Test(self, mesh_group, exp_entity_types):
        entity_types = mesh_group.GetEntityTypesInMesh()
        self.assertListEqual(sorted(entity_types), sorted(exp_entity_types))


    def __Execute_GetGeomEntities_Test(self, mesh_group, exp_entity_types, num_nodes):
        nodes, geom_entities = mesh_group.GetNodesAndGeometricalEntities(list(exp_entity_types.keys()))

        self.assertEqual(num_nodes, len(nodes)) # this might fail if different versions of salome give different meshes

        if SMESH.Entity_Node in exp_entity_types:
            exp_entity_types.pop(SMESH.Entity_Node) # nodes are retrieved separately

        self.assertEqual(len(exp_entity_types), len(geom_entities))

        for entity_type, num_entities in exp_entity_types.items():
            self.assertEqual(num_entities, len(geom_entities[entity_type])) # this might fail if different versions of salome give different meshes



if __name__ == '__main__':
    unittest.main()