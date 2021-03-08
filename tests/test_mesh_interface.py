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
import unittest

# plugin imports
from kratos_salome_plugin.mesh_interface import MeshInterface
from kratos_salome_plugin import salome_utilities

# tests imports
import testing_utilities

# salome imports
import SMESH


class TestMeshInterfaceObservers(unittest.TestCase):
    def test_observers(self):
        self.skipTest("This test is not yet implemented")


# The expected definitions are here to make the handling of the
# multiline-stings easier (no need to deal with indentation)
mesh_interface_str = '''MeshInterface
  Mesh identifier: 0:1:2:3:7:2
  Mesh is valid: True
  Mesh has the following entities:
    Node: 49
    Triangle: 80
'''
mesh_interface_not_valid_str = '''MeshInterface
  Mesh identifier: 1:55555:114777
  Mesh is valid: False
'''

class TestMeshInterfaceMeshRelatedMethods(testing_utilities.SalomeTestCaseWithBox):

    def setUp(self):
        super().setUp()
        # this also tests the "CheckMeshIsValid" function right here
        existing_mesh_identifier = salome_utilities.GetSalomeID(self.mesh_tetra.GetMesh())
        self.mesh_interface_main_mesh_tetra = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_main_mesh_tetra.CheckMeshIsValid())

        self.mesh_interface_non_exist_mesh = MeshInterface(existing_mesh_identifier)
        self.mesh_interface_non_exist_mesh.mesh_identifier = "1:55555:114777" # has to be overwritten, otherwise throws in constructor
        self.assertFalse(self.mesh_interface_non_exist_mesh.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.mesh_hexa.GetMesh())
        self.mesh_interface_main_mesh_hexa = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_main_mesh_hexa.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_tetra_e_1)
        self.mesh_interface_sub_mesh_tetra_edge = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_sub_mesh_tetra_edge.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_tetra_f_2)
        self.mesh_interface_sub_mesh_tetra_face = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_sub_mesh_tetra_face.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_tetra_g_1)
        self.mesh_interface_sub_mesh_group_tetra_face = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_sub_mesh_group_tetra_face.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_hexa_g_2)
        self.mesh_interface_sub_mesh_group_hexa_edge = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_sub_mesh_group_hexa_edge.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_hexa_g_1)
        self.mesh_interface_sub_mesh_group_hexa_face = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_sub_mesh_group_hexa_face.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_hexa_f_2)
        self.mesh_interface_sub_mesh_hexa_face = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_sub_mesh_hexa_face.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.group_tetra_0D_elements)
        self.mesh_interface_tetra_0D_elements = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_tetra_0D_elements.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.group_hexa_ball_elements)
        self.mesh_interface_hexa_ball_elements = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_hexa_ball_elements.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.group_tetra_f1_nodes)
        self.mesh_interface_tetra_mesh_group_f1_nodes = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_tetra_mesh_group_f1_nodes.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.group_tetra_f1_faces)
        self.mesh_interface_tetra_mesh_group_f1_faces = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_tetra_mesh_group_f1_faces.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.group_hexa_edges)
        self.mesh_interface_hexa_mesh_group_edges = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_hexa_mesh_group_edges.CheckMeshIsValid())


    def test_printing(self):
        self.assertMultiLineEqual(str(self.mesh_interface_sub_mesh_tetra_face), mesh_interface_str)
        self.assertMultiLineEqual(str(self.mesh_interface_non_exist_mesh), mesh_interface_not_valid_str)

    def test_GetNodes_NonExistingMesh(self):
        self.assertEqual({}, self.mesh_interface_non_exist_mesh.GetNodes())

    def test_GetNodes_MainMesh(self):
        nodes = self.mesh_interface_main_mesh_tetra.GetNodes()
        self.assertEqual(366, len(nodes)) # this might fail if different versions of salome give different meshes
        for node_coords in nodes.values():
            self.assertEqual(3, len(node_coords))

    def test_GetNodes_SubMeshOnEdge(self):
        nodes = self.mesh_interface_sub_mesh_tetra_edge.GetNodes()
        self.assertEqual(5, len(nodes)) # this might fail if different versions of salome give different meshes
        # all nodes are on an edge, hence we can test at least for that
        for node_coords in nodes.values():
            self.assertAlmostEqual(200.0, node_coords[0])
            self.assertAlmostEqual(200.0, node_coords[2])

    def test_GetNodes_SubMeshOnFace(self):
        nodes = self.mesh_interface_sub_mesh_tetra_face.GetNodes()
        self.assertEqual(49, len(nodes)) # this might fail if different versions of salome give different meshes
        # all nodes are on a face, hence we can test at least for that
        for node_coords in nodes.values():
            self.assertAlmostEqual(0.0, node_coords[1])

    def test_GetNodes_SubMeshOnTriFaceGroup(self):
        nodes = self.mesh_interface_sub_mesh_group_tetra_face.GetNodes()
        self.assertEqual(98, len(nodes)) # this might fail if different versions of salome give different meshes

    def test_GetNodes_SubMeshOnEdgeGroup(self):
        nodes = self.mesh_interface_sub_mesh_group_hexa_edge.GetNodes()
        self.assertEqual(32, len(nodes)) # this might fail if different versions of salome give different meshes

    def test_GetNodes_SubMeshOnFaceGroup(self):
        nodes = self.mesh_interface_sub_mesh_group_hexa_face.GetNodes()
        self.assertEqual(162, len(nodes)) # this might fail if different versions of salome give different meshes

    def test_GetNodes_Group_tetra_0D(self):
        nodes = self.mesh_interface_tetra_0D_elements.GetNodes()
        self.assertEqual(10, len(nodes)) # this might fail if different versions of salome give different meshes

    def test_GetNodes_Group_hexa_ball(self):
        nodes = self.mesh_interface_hexa_ball_elements.GetNodes()
        self.assertEqual(6, len(nodes)) # this might fail if different versions of salome give different meshes

    def test_GetNodes_GroupOnGeom_tetra_f1_nodes(self):
        nodes = self.mesh_interface_tetra_mesh_group_f1_nodes.GetNodes()
        self.assertEqual(49, len(nodes)) # this might fail if different versions of salome give different meshes
        for node_coords in nodes.values():
            self.assertAlmostEqual(200.0, node_coords[0])

    def test_GetNodes_GroupOnGeom_tetra_f1_faces(self):
        nodes = self.mesh_interface_tetra_mesh_group_f1_faces.GetNodes()
        self.assertEqual(49, len(nodes)) # this might fail if different versions of salome give different meshes

    def test_GetNodes_GroupOnFilter_hexa_edge(self):
        nodes = self.mesh_interface_hexa_mesh_group_edges.GetNodes()
        self.assertEqual(92, len(nodes)) # this might fail if different versions of salome give different meshes


    def test_GetGeomEntities_NonExistingMesh(self):
        self.assertEqual(({}, {}), self.mesh_interface_non_exist_mesh.GetNodesAndGeometricalEntities([]))

    def test_GetGeomEntities_MainMesh_tetra(self):
        entity_types = {
            "Triangle" : 480,
            "Edge"     : 48,
            "Tetra"    : 1355,
            "Node"     : 366,
            "0D"       : 14
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_main_mesh_tetra, entity_types, 366)

    def test_GetGeomEntities_MainMesh_tetra_retrieve_subset(self):
        entity_types = {
            "Triangle" : 480,
            "Edge"     : 48
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_main_mesh_tetra, entity_types, 366)

    def test_GetGeomEntities_MainMesh_tetra_retrieve_not_existing(self):
        entity_types = {
            "Quadrangle" : 0, # no quadrangles in this mesh
            "Triangle"   : 480,
            "Edge"       : 48
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_main_mesh_tetra, entity_types, 366)

    def test_GetGeomEntities_MainMesh_hexa(self):
        entity_types = {
            "Quadrangle" : 384,
            "Triangle"   : 0,
            "Edge"       : 96,
            "Tetra"      : 0,
            "Hexa"       : 512,
            "Node"       : 729,
            "Ball"       : 17
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_main_mesh_hexa, entity_types, 729)

    def test_GetGeomEntities_SubMeshOnGeom_face_tri(self):
        entity_types = {
            "Triangle" : 80,
            "Edge"     : 0,
            "Tetra"    : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_sub_mesh_tetra_face, entity_types, 49)

    def test_GetGeomEntities_SubMeshOnGeom_face_quad(self):
        entity_types = {
            "Quadrangle" : 64,
            "Triangle"   : 0,
            "Edge"       : 0,
            "Hexa"       : 0,
            "Tetra"      : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_sub_mesh_hexa_face, entity_types, 81)

    def test_GetGeomEntities_SubMeshOnGeom_edge(self):
        entity_types = {
            "Triangle" : 0,
            "Edge"     : 4,
            "Tetra"    : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_sub_mesh_tetra_edge, entity_types, 5)

    def test_GetGeomEntities_SubMeshOnGroup_face_tri(self):
        entity_types = {
            "Quadrangle" : 0,
            "Triangle"   : 160,
            "Edge"       : 0,
            "Hexa"       : 0,
            "Tetra"      : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_sub_mesh_group_tetra_face, entity_types, 98)

    def test_GetGeomEntities_SubMeshOnGroup_face_quad(self):
        entity_types = {
            "Quadrangle" : 128,
            "Triangle"   : 0,
            "Edge"       : 0,
            "Hexa"       : 0,
            "Tetra"      : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_sub_mesh_group_hexa_face, entity_types, 162)

    def test_GetGeomEntities_SubMeshOnGroup_edge(self):
        entity_types = {
            "Quadrangle" : 0,
            "Triangle"   : 0,
            "Edge"       : 32,
            "Hexa"       : 0,
            "Tetra"      : 0
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_sub_mesh_group_hexa_edge, entity_types, 32)

    def test_GetGeomEntities_Group_tetra_0D(self):
        entity_types = {
            "0D" : 10
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_tetra_0D_elements, entity_types, 10)

    def test_GetGeomEntities_Group_hexa_ball(self):
        entity_types = {
            "Ball" : 6
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_hexa_ball_elements, entity_types, 6)

    def test_GetGeomEntities_GroupOnGeom_tetra_f1_nodes(self):
        entity_types = {} # group only contains nodes
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_tetra_mesh_group_f1_nodes, entity_types, 49)

    def test_GetGeomEntities_GroupOnGeom_tetra_f1_faces(self):
        entity_types = {
            "Triangle" : 80
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_tetra_mesh_group_f1_faces, entity_types, 49)

    def test_GetGeomEntities_GroupOnFilter_hexa_edge(self):
        entity_types = {
            "Edge" : 96
        }
        self.__Execute_GetGeomEntities_Test(self.mesh_interface_hexa_mesh_group_edges, entity_types, 92)


    def test_GetMeshName(self):
        self.assertEqual(self.name_main_mesh_tetra, self.mesh_interface_main_mesh_tetra.GetMeshName())
        self.assertEqual("", self.mesh_interface_non_exist_mesh.GetMeshName())


    def test_GetEntityTypesInMesh_NonExistingMesh(self):
        self.assertEqual([], self.mesh_interface_non_exist_mesh.GetEntityTypesInMesh())

    def test_GetEntityTypesInMesh_MainMesh_tetra(self):
        exp_entity_types = [
            SMESH.Entity_Triangle,
            SMESH.Entity_Edge,
            SMESH.Entity_Node,
            SMESH.Entity_0D,
            SMESH.Entity_Tetra
        ]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_interface_main_mesh_tetra, exp_entity_types)

    def test_GetEntityTypesInMesh_MainMesh_hexa(self):
        exp_entity_types = [
            SMESH.Entity_Quadrangle,
            SMESH.Entity_Edge,
            SMESH.Entity_Node,
            SMESH.Entity_Ball,
            SMESH.Entity_Hexa
        ]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_interface_main_mesh_hexa, exp_entity_types)

    def test_GetEntityTypesInMesh_SubMeshOnEdge(self):
        exp_entity_types = [
            SMESH.Entity_Edge,
            SMESH.Entity_Node
        ]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_interface_sub_mesh_tetra_edge, exp_entity_types)

    def test_GetEntityTypesInMesh_SubMeshOnFace(self):
        exp_entity_types = [
            SMESH.Entity_Triangle,
            SMESH.Entity_Node
        ]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_interface_sub_mesh_tetra_face, exp_entity_types)

    def test_GetEntityTypesInMesh_SubMeshOnEdgeGroup(self):
        exp_entity_types = [
            SMESH.Entity_Edge,
            SMESH.Entity_Node
        ]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_interface_sub_mesh_group_hexa_edge, exp_entity_types)

    def test_GetEntityTypesInMesh_SubMeshOnFaceGroup(self):
        exp_entity_types = [
            SMESH.Entity_Quadrangle,
            SMESH.Entity_Node
        ]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_interface_sub_mesh_group_hexa_face, exp_entity_types)

    def test_GetEntityTypesInMesh_0DElemsGroup(self):
        exp_entity_types = [SMESH.Entity_0D]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_interface_tetra_0D_elements, exp_entity_types)

    def test_GetEntityTypesInMesh_BallElemsGroup(self):
        exp_entity_types = [SMESH.Entity_Ball]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_interface_hexa_ball_elements, exp_entity_types)

    def test_GetEntityTypesInMesh_MeshGroup_tetra_nodes(self):
        exp_entity_types = [SMESH.Entity_Node]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_interface_tetra_mesh_group_f1_nodes, exp_entity_types)

    def test_GetEntityTypesInMesh_MeshGroup_tetra_faces(self):
        exp_entity_types = [SMESH.Entity_Triangle]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_interface_tetra_mesh_group_f1_faces, exp_entity_types)

    def test_GetEntityTypesInMesh_MeshGroup_hexa_edges(self):
        exp_entity_types = [SMESH.Entity_Edge]
        self.__Execute_GetEntityTypesInMesh_Test(self.mesh_interface_hexa_mesh_group_edges, exp_entity_types)

    def test_DoMeshesBelongToSameMainMesh_same_main_mesh(self):
        mesh_interfaces_to_check = [
            self.mesh_interface_main_mesh_tetra,
            self.mesh_interface_sub_mesh_tetra_face,
            self.mesh_interface_sub_mesh_tetra_edge,
            self.mesh_interface_tetra_0D_elements
        ]

        self.assertTrue(MeshInterface.DoMeshesBelongToSameMainMesh(mesh_interfaces_to_check))

    def test_DoMeshesBelongToSameMainMesh_not_same_main_mesh(self):
        mesh_interfaces_to_check = [
            self.mesh_interface_main_mesh_tetra,
            self.mesh_interface_main_mesh_hexa
        ]

        self.assertFalse(MeshInterface.DoMeshesBelongToSameMainMesh(mesh_interfaces_to_check))

    def test_DoMeshesBelongToSameMainMesh_invalid_mesh(self):
        mesh_interfaces_to_check = [
            self.mesh_interface_main_mesh_tetra,
            self.mesh_interface_non_exist_mesh
        ]

        self.assertFalse(MeshInterface.DoMeshesBelongToSameMainMesh(mesh_interfaces_to_check))


    def __Execute_GetEntityTypesInMesh_Test(self, mesh_interface, exp_entity_types):
        entity_types = mesh_interface.GetEntityTypesInMesh()
        self.assertListEqual(sorted(entity_types), sorted(exp_entity_types))


    def __Execute_GetGeomEntities_Test(self, mesh_interface, exp_entity_types, num_nodes):
        nodes, geom_entities = mesh_interface.GetNodesAndGeometricalEntities(list(exp_entity_types.keys()))

        self.assertEqual(num_nodes, len(nodes)) # this might fail if different versions of salome give different meshes

        self.assertEqual(len(exp_entity_types), len(geom_entities))

        num_nodes_per_entity = {
            "Quadrangle" : 4,
            "Triangle"   : 3,
            "Edge"       : 2,
            "Ball"       : 1,
            "Hexa"       : 8,
            "0D"         : 1,
            "Node"       : 1,
            "Tetra"      : 4
        }

        for entity_type, num_entities in exp_entity_types.items():
            self.assertEqual(num_entities, len(geom_entities[entity_type])) # this might fail if different versions of salome give different meshes
            exp_num_nodes = num_nodes_per_entity[entity_type]
            for node_id_list in geom_entities[entity_type].values():
                self.assertEqual(exp_num_nodes, len(node_id_list))


class TestMeshInterfaceWith2DCantilever(testing_utilities.SalomeTestCaseCantilever2D):
    """Make sure that the nodes on non-overlapping interfaces are different
    This should work fine when directly accessing the database of Salome, but apparantly
    there can be some issues when using "*.dat" files
    see https://www.salome-platform.org/forum/forum_10/566761473
    """

    def setUp(self):
        super().setUp()
        # this also tests the "CheckMeshIsValid" function right here
        existing_mesh_identifier = salome_utilities.GetSalomeID(self.domain_mesh.GetMesh())
        self.mesh_interface_domain_mesh = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_domain_mesh.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.neumann_mesh)
        self.mesh_interface_neumann = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_neumann.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.dirichlet_mesh)
        self.mesh_interface_dirichlet = MeshInterface(existing_mesh_identifier)
        self.assertTrue(self.mesh_interface_dirichlet.CheckMeshIsValid())

    def test_overlapping_node_ids(self):
        nodes_neumann = self.mesh_interface_neumann.GetNodes()
        nodes_dirichlet = self.mesh_interface_dirichlet.GetNodes()

        nodes_ids_neumann = set(nodes_neumann.keys())
        nodes_ids_dirichlet = set(nodes_dirichlet.keys())

        # the ids must not overlap, since the two meshes have no overlap!
        self.assertEqual(len(nodes_ids_neumann.intersection(nodes_ids_dirichlet)), 0)

        # mesh is quads, hence has to have same number of nodes on both sides!
        self.assertEqual(len(nodes_neumann), len(nodes_dirichlet))

        # the submeshes must have less elements than the main mesh
        self.assertLess(len(nodes_neumann), len(self.mesh_interface_domain_mesh.GetNodes()))


if __name__ == '__main__':
    unittest.main()
