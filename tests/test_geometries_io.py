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
from unittest.mock import MagicMock
from abc import ABCMeta, abstractmethod

# plugin imports
import kratos_salome_plugin.model_part as py_model_part
from kratos_salome_plugin import geometries_io
from kratos_salome_plugin.mesh_interface import MeshInterface
from kratos_salome_plugin import salome_utilities

# tests imports
from testing_utilities import SalomeTestCaseWithBox, CheckIfKratosAvailable

# Kratos imports
kratos_available = CheckIfKratosAvailable()
if kratos_available:
    import KratosMultiphysics as KM


class TestGeometriesIOWithMockMeshInterfaces(object):
    """This TestCase contains basic tests for the GeometriesIO where the MeshInterface is substituted by a Mock object
    """
    class BaseTests(unittest.TestCase, metaclass=ABCMeta):
        @abstractmethod
        def _CreateModelPart(self, name): pass

        def test_not_same_main_mesh(self):
            model_part = self._CreateModelPart()
            # apparently if not configuring this, it returns True
            attrs = { 'DoMeshesBelongToSameMainMesh.return_value': False }
            mesh_interface_mock = MagicMock(spec=MeshInterface)
            mesh_interface_mock.configure_mock(**attrs)

            meshes = [geometries_io.Mesh(mesh_interface_mock, {})]
            with self.assertRaisesRegex(Exception, 'The meshes to be added to ModelPart "for_test" don\'t belong to the same main mesh!\nThis is necessary to ensure a consistent numbering.'):
                geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

        def test_add_nodes_from_one_mesh_to_main_model_part(self):
            self.__ExecuteTestAddNodesFromOneMeshToModelPart("")

        def test_add_nodes_from_one_mesh_to_sub_model_part(self):
            self.__ExecuteTestAddNodesFromOneMeshToModelPart("sub_mp")

        def test_add_nodes_from_one_mesh_to_sub_sub_model_part(self):
            self.__ExecuteTestAddNodesFromOneMeshToModelPart("subda3_mp.the_sub_sub_model_part")

        def __ExecuteTestAddNodesFromOneMeshToModelPart(self, model_part_name):
            model_part = self._CreateModelPart()
            the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}

            attrs = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, {}) }
            mesh_interface_mock = MagicMock(spec=MeshInterface)
            mesh_interface_mock.configure_mock(**attrs)

            meshes = [geometries_io.Mesh(mesh_interface_mock, {}, model_part_name)]
            geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

            def CheckModelPart(model_part_to_check):
                self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in the_nodes)

                    orig_node_coords = the_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

            self.__RecursiveCheckModelParts(model_part, model_part_name, CheckModelPart)


        def test_add_nodes_from_multiple_meshes_to_main_model_part(self):
            self.__ExecuteTestAddNodesFromMultipleMeshesToModelPart("")

        def test_add_nodes_from_multiple_meshes_to_sub_model_part(self):
            self.__ExecuteTestAddNodesFromMultipleMeshesToModelPart("my_sub")

        def test_add_nodes_from_multiple_meshes_to_sub_sub_model_part(self):
            self.__ExecuteTestAddNodesFromMultipleMeshesToModelPart("sub_mp_mul.sub_sub_mult_meshes")

        def __ExecuteTestAddNodesFromMultipleMeshesToModelPart(self, model_part_name):
            model_part = self._CreateModelPart()

            nodes_mesh_1 = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            attrs_mesh_1 = { 'GetNodesAndGeometricalEntities.return_value': (nodes_mesh_1, {}) }
            mesh_interface_mock_mesh_1 = MagicMock(spec=MeshInterface)
            mesh_interface_mock_mesh_1.configure_mock(**attrs_mesh_1)

            nodes_mesh_2 = {i+25 : [i+3.5,i-13.22,i*2] for i in range(5)}
            attrs_mesh_2 = { 'GetNodesAndGeometricalEntities.return_value': (nodes_mesh_2, {}) }
            mesh_interface_mock_mesh_2 = MagicMock(spec=MeshInterface)
            mesh_interface_mock_mesh_2.configure_mock(**attrs_mesh_2)

            nodes_mesh_3 = {i+1 : [i+1,i*2,i+3.5] for i in range(3)} # those nodes have the same coord, hence no new nodes will be created!
            attrs_mesh_3 = { 'GetNodesAndGeometricalEntities.return_value': (nodes_mesh_3, {}) }
            mesh_interface_mock_mesh_3 = MagicMock(spec=MeshInterface)
            mesh_interface_mock_mesh_3.configure_mock(**attrs_mesh_3)

            meshes = [
                geometries_io.Mesh(mesh_interface_mock_mesh_1, {}, model_part_name),
                geometries_io.Mesh(mesh_interface_mock_mesh_2, {}, model_part_name),
                geometries_io.Mesh(mesh_interface_mock_mesh_3, {}, model_part_name)
            ]
            geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

            def CheckModelPart(model_part_to_check):
                self.assertEqual(len(nodes_mesh_1) + len(nodes_mesh_2), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    if node.Id > 16:
                        ref_nodes = nodes_mesh_2
                    else:
                        ref_nodes = nodes_mesh_1

                    self.assertTrue(node.Id in ref_nodes)

                    orig_node_coords = ref_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

            self.__RecursiveCheckModelParts(model_part, model_part_name, CheckModelPart)


        def test_add_elements_from_one_mesh_to_main_model_part(self):
            self.__ExecuteTestAddElementsFromOneMeshToModelPart("")

        def test_add_elements_from_one_mesh_to_sub_model_part(self):
            self.__ExecuteTestAddElementsFromOneMeshToModelPart("sub_mp_el")

        def test_add_elements_from_one_mesh_to_sub_sub_model_part(self):
            self.__ExecuteTestAddElementsFromOneMeshToModelPart("subda3_mp.the_sub_sub_element_model_part")

        def __ExecuteTestAddElementsFromOneMeshToModelPart(self, model_part_name):
            model_part = self._CreateModelPart()

            geometry_name = "Line"
            element_name = "Element2D2N"
            props_id = 12

            mesh_description = { "elements" : {geometry_name : {element_name : props_id} } }

            the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            the_geom_entities = {geometry_name : {i+1 : [i+1, i+2] for i in range(14)}}

            attrs = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, the_geom_entities) }
            mesh_interface_mock = MagicMock(spec=MeshInterface)
            mesh_interface_mock.configure_mock(**attrs)

            meshes = [geometries_io.Mesh(mesh_interface_mock, mesh_description, model_part_name)]
            geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

            def CheckModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id))
                self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in the_nodes)

                    orig_node_coords = the_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                self.assertEqual(len(the_geom_entities[geometry_name]), model_part_to_check.NumberOfElements())
                for elem in model_part_to_check.Elements:
                    # checking the connectivities
                    self.assertTrue(elem.Id in the_geom_entities[geometry_name])
                    nodes_id_list = sorted([node.Id for node in elem.GetNodes()])
                    self.assertListEqual(sorted(the_geom_entities[geometry_name][elem.Id]), nodes_id_list)

            self.__RecursiveCheckModelParts(model_part, model_part_name, CheckModelPart)


        def test_add_elements_from_multiple_meshes_to_main_model_part(self):
            self.__ExecuteTestAddElementsFromMultipleMeshesToModelPart("")

        def test_add_elements_from_multiple_meshes_to_sub_model_part(self):
            self.__ExecuteTestAddElementsFromMultipleMeshesToModelPart("sub_mpss_el")

        def test_add_elements_from_multiple_meshes_to_sub_sub_model_part(self):
            self.__ExecuteTestAddElementsFromMultipleMeshesToModelPart("subdafq23_mp.the_sub_sub_elemaent_model_part")

        def __ExecuteTestAddElementsFromMultipleMeshesToModelPart(self, model_part_name):
            model_part = self._CreateModelPart()

            geometry_name = "Line"
            element_name = "Element2D2N"
            props_id = 12

            mesh_description = { "elements" : {geometry_name : {element_name : props_id} } }

            nodes_mesh_1 = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            geometries_mesh_1 = {geometry_name : {i+1 : [i+1, i+2] for i in range(14)}}
            attrs_mesh_1 = { 'GetNodesAndGeometricalEntities.return_value': (nodes_mesh_1, geometries_mesh_1) }
            mesh_interface_mock_mesh_1 = MagicMock(spec=MeshInterface)
            mesh_interface_mock_mesh_1.configure_mock(**attrs_mesh_1)

            nodes_mesh_2 = {i+1 : [i*2,i+88.5, i-1] for i in range(33,39)}
            geometries_mesh_2 = {geometry_name : {i+1 : [i+1, i+2] for i in range(33,38)}}
            attrs_mesh_2 = { 'GetNodesAndGeometricalEntities.return_value': (nodes_mesh_2, geometries_mesh_2) }
            mesh_interface_mock_mesh_2 = MagicMock(spec=MeshInterface)
            mesh_interface_mock_mesh_2.configure_mock(**attrs_mesh_2)

            # this mesh is a subset of mesh 1, hence NO new entities should be created from this mesh!
            nodes_mesh_3 = {i+1 : [i+1,i*2,i+3.5] for i in range(5)}
            geometries_mesh_3 = {geometry_name : {i+1 : [i+1, i+2] for i in range(3)}}
            attrs_mesh_3 = { 'GetNodesAndGeometricalEntities.return_value': (nodes_mesh_3, geometries_mesh_3) }
            mesh_interface_mock_mesh_3 = MagicMock(spec=MeshInterface)
            mesh_interface_mock_mesh_3.configure_mock(**attrs_mesh_3)

            meshes = [
                geometries_io.Mesh(mesh_interface_mock_mesh_1, mesh_description, model_part_name),
                geometries_io.Mesh(mesh_interface_mock_mesh_2, mesh_description, model_part_name),
                geometries_io.Mesh(mesh_interface_mock_mesh_3, mesh_description, model_part_name)
            ]
            geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

            def CheckModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id))
                self.assertEqual(len(nodes_mesh_1)+len(nodes_mesh_2), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    if node.Id > 16:
                        ref_nodes = nodes_mesh_2
                    else:
                        ref_nodes = nodes_mesh_1

                    self.assertTrue(node.Id in ref_nodes)

                    orig_node_coords = ref_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                self.assertEqual(len(geometries_mesh_1[geometry_name])+len(geometries_mesh_2[geometry_name]), model_part_to_check.NumberOfElements())
                for elem in model_part_to_check.Elements:
                    # checking the connectivities
                    # Id offset is required because Elements are renumbered!
                    if elem.Id > 14:
                        ref_geometries = geometries_mesh_2[geometry_name]
                        id_offset = 19
                    else:
                        ref_geometries = geometries_mesh_1[geometry_name]
                        id_offset = 0

                    self.assertTrue(elem.Id+id_offset in ref_geometries)
                    nodes_id_list = sorted([node.Id for node in elem.GetNodes()])
                    self.assertListEqual(sorted(ref_geometries[elem.Id+id_offset]), nodes_id_list)

                    self.assertEqual(elem.Properties.Id, props_id)

            self.__RecursiveCheckModelParts(model_part, model_part_name, CheckModelPart)

        def test_add_different_elements_to_one_modelpart(self):
            # note that usually different elements/conditions are added to different SubModelParts
            # and hence also to the MainModelPart
            # in this test however we intentionally check the creation of multiple elements form
            # the same mesh
            model_part = self._CreateModelPart()

            geometry_name_1D = "Line"
            element_name_1D = "Element2D2N"
            props_id_1D = 12
            geometry_name_2D = "Triangle"
            element_name_2D = "Element2D3N"
            props_id_2D = 77
            geometry_name_3D = "Tetra"
            element_name_3D = "Element3D4N"
            props_id_3D = 6

            mesh_description = { "elements" : {
                geometry_name_1D : {element_name_1D : props_id_1D},
                geometry_name_2D : {element_name_2D : props_id_2D},
                geometry_name_3D : {element_name_3D : props_id_3D}
            }}

            the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            the_geom_entities = {
                geometry_name_1D : {i+1 : [i+1, i+2] for i in range(12)},
                geometry_name_2D : {i+1 : [(i+1)%15+1, (i+3)%15+1, (i+4)%15+1] for i in range(25)},
                geometry_name_3D : {i+1 : [(i+2)%15+1, (i+6)%15+1, (i+4)%15+1, (i+8)%15+1] for i in range(31)}
            }

            attrs = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, the_geom_entities) }
            mesh_interface_mock = MagicMock(spec=MeshInterface)
            mesh_interface_mock.configure_mock(**attrs)

            meshes = [geometries_io.Mesh(mesh_interface_mock, mesh_description, model_part.Name)]
            geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

            def CheckModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id_1D))
                self.assertTrue(model_part_to_check.HasProperties(props_id_2D))
                self.assertTrue(model_part_to_check.HasProperties(props_id_3D))

                self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in the_nodes)

                    orig_node_coords = the_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                self.assertEqual(sum([len(v) for v in the_geom_entities.values()]), model_part_to_check.NumberOfElements())
                num_elements_1D = 0
                num_elements_2D = 0
                num_elements_3D = 0
                for elem in model_part_to_check.Elements:
                    # Note: due to "mesh_description" and "the_geom_entities" being unordered
                    # and because everything is in one ModelPart we cannot check the connectivities
                    # it is probably possible with some smart sorting to get the Id-offsets
                    if len(elem.GetNodes()) == 2:
                        num_elements_1D += 1
                        ref_props_id = props_id_1D
                    elif len(elem.GetNodes()) == 3:
                        num_elements_2D += 1
                        ref_props_id = props_id_2D
                    elif len(elem.GetNodes()) == 4:
                        num_elements_3D += 1
                        ref_props_id = props_id_3D
                    else:
                        raise Exception("Unknown number of nodes!")
                    self.assertEqual(elem.Properties.Id, ref_props_id)
                self.assertEqual(num_elements_1D, len(the_geom_entities[geometry_name_1D]))
                self.assertEqual(num_elements_2D, len(the_geom_entities[geometry_name_2D]))
                self.assertEqual(num_elements_3D, len(the_geom_entities[geometry_name_3D]))

            CheckModelPart(model_part)

        def test_add_different_elements_to_different_modelparts(self):
            model_part = self._CreateModelPart()

            geometry_name_1D = "Line"
            element_name_1D = "Element2D2N"
            props_id_1D = 12
            smp_name_1D = "smp_1D_lines"

            geometry_name_2D = "Triangle"
            element_name_2D = "Element2D3N"
            props_id_2D = 77
            smp_name_2D = "surfaces"

            geometry_name_3D = "Tetra"
            element_name_3D = "Element3D4N"
            props_id_3D = 6
            smp_name_3D = "part_domain"

            mesh_description_1D = { "elements" : {
                geometry_name_1D : {element_name_1D : props_id_1D}
            }}

            mesh_description_2D = { "elements" : {
                geometry_name_2D : {element_name_2D : props_id_2D}
            }}

            mesh_description_3D = { "elements" : {
                geometry_name_3D : {element_name_3D : props_id_3D}
            }}

            the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            the_geom_entities_1D = {
                geometry_name_1D : {i+1 : [i+1, i+2] for i in range(12)}
            }
            the_geom_entities_2D = {
                geometry_name_2D : {i+1 : [(i+1)%15+1, (i+3)%15+1, (i+4)%15+1] for i in range(25)}
            }
            the_geom_entities_3D = {
                geometry_name_3D : {i+1 : [(i+2)%15+1, (i+6)%15+1, (i+4)%15+1, (i+8)%15+1] for i in range(31)}
            }

            attrs_1D = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, the_geom_entities_1D) }
            attrs_2D = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, the_geom_entities_2D) }
            attrs_3D = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, the_geom_entities_3D) }
            mesh_interface_mock_1D = MagicMock(spec=MeshInterface)
            mesh_interface_mock_1D.configure_mock(**attrs_1D)
            mesh_interface_mock_2D = MagicMock(spec=MeshInterface)
            mesh_interface_mock_2D.configure_mock(**attrs_2D)
            mesh_interface_mock_3D = MagicMock(spec=MeshInterface)
            mesh_interface_mock_3D.configure_mock(**attrs_3D)

            meshes = [
                geometries_io.Mesh(mesh_interface_mock_1D, mesh_description_1D, smp_name_1D),
                geometries_io.Mesh(mesh_interface_mock_2D, mesh_description_2D, smp_name_2D),
                geometries_io.Mesh(mesh_interface_mock_3D, mesh_description_3D, smp_name_3D)
            ]
            geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

            def CheckMainModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id_1D))
                self.assertTrue(model_part_to_check.HasProperties(props_id_2D))
                self.assertTrue(model_part_to_check.HasProperties(props_id_3D))

                self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in the_nodes)

                    orig_node_coords = the_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                self.assertEqual(len(the_geom_entities_1D[geometry_name_1D])+len(the_geom_entities_2D[geometry_name_2D])+len(the_geom_entities_3D[geometry_name_3D]), model_part_to_check.NumberOfElements())
                for elem in model_part_to_check.Elements:
                    # TODO check everyhthing, now the order in which the entities are being created is deterministic
                    if len(elem.GetNodes()) == 2:
                        ref_props_id = props_id_1D
                    elif len(elem.GetNodes()) == 3:
                        ref_props_id = props_id_2D
                    elif len(elem.GetNodes()) == 4:
                        ref_props_id = props_id_3D
                    else:
                        raise Exception("Unknown number of nodes!")
                    self.assertEqual(elem.Properties.Id, ref_props_id)

            def CheckSubModelPart(model_part_to_check, geometries, props_id, id_offset=0):
                self.assertTrue(model_part_to_check.HasProperties(props_id))

                self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in the_nodes)

                    orig_node_coords = the_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                self.assertEqual(len(geometries), model_part_to_check.NumberOfElements())
                for elem in model_part_to_check.Elements:
                    # checking the connectivities
                    geom_id = elem.Id - id_offset
                    self.assertTrue(geom_id in geometries)
                    nodes_id_list = sorted([node.Id for node in elem.GetNodes()])
                    self.assertListEqual(sorted(geometries[geom_id]), nodes_id_list)
                    self.assertEqual(elem.Properties.Id, props_id)

            CheckMainModelPart(model_part)
            CheckSubModelPart(model_part.GetSubModelPart(smp_name_1D), the_geom_entities_1D[geometry_name_1D], props_id_1D)
            id_offset_2D = len(the_geom_entities_1D[geometry_name_1D])
            CheckSubModelPart(model_part.GetSubModelPart(smp_name_2D), the_geom_entities_2D[geometry_name_2D], props_id_2D, id_offset_2D)
            id_offset_3D = id_offset_2D + len(the_geom_entities_2D[geometry_name_2D])
            CheckSubModelPart(model_part.GetSubModelPart(smp_name_3D), the_geom_entities_3D[geometry_name_3D], props_id_3D, id_offset_3D)


        def test_add_conditions_from_one_mesh_to_main_model_part(self):
            self.__ExecuteTestAddConditionsFromOneMeshToModelPart("")

        def test_add_conditions_from_one_mesh_to_sub_model_part(self):
            self.__ExecuteTestAddConditionsFromOneMeshToModelPart("sub_mp_cond")

        def test_add_conditions_from_one_mesh_to_sub_sub_model_part(self):
            self.__ExecuteTestAddConditionsFromOneMeshToModelPart("subda3_mp.the_sub_sub_condition_model_part")

        def __ExecuteTestAddConditionsFromOneMeshToModelPart(self, model_part_name):
            model_part = self._CreateModelPart()

            geometry_name = "Line"
            condition_name = "LineCondition2D2N"
            props_id = 12

            mesh_description = { "conditions" : {geometry_name : {condition_name : props_id} } }

            the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            the_geom_entities = {geometry_name : {i+1 : [i+1, i+2] for i in range(14)}}

            attrs = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, the_geom_entities) }
            mesh_interface_mock = MagicMock(spec=MeshInterface)
            mesh_interface_mock.configure_mock(**attrs)

            meshes = [geometries_io.Mesh(mesh_interface_mock, mesh_description, model_part_name)]
            geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

            def CheckModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id))
                self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in the_nodes)

                    orig_node_coords = the_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                self.assertEqual(len(the_geom_entities[geometry_name]), model_part_to_check.NumberOfConditions())
                for elem in model_part_to_check.Conditions:
                    # checking the connectivities
                    self.assertTrue(elem.Id in the_geom_entities[geometry_name])
                    nodes_id_list = sorted([node.Id for node in elem.GetNodes()])
                    self.assertListEqual(sorted(the_geom_entities[geometry_name][elem.Id]), nodes_id_list)

            self.__RecursiveCheckModelParts(model_part, model_part_name, CheckModelPart)


        def test_add_conditions_from_multiple_meshes_to_main_model_part(self):
            self.__ExecuteTestAddConditionsFromMultipleMeshesToModelPart("")

        def test_add_conditions_from_multiple_meshes_to_sub_model_part(self):
            self.__ExecuteTestAddConditionsFromMultipleMeshesToModelPart("sub_mpss_conditions")

        def test_add_conditions_from_multiple_meshes_to_sub_sub_model_part(self):
            self.__ExecuteTestAddConditionsFromMultipleMeshesToModelPart("subdafq23_mp.the_sub_sub_elemaent_model_part")

        def __ExecuteTestAddConditionsFromMultipleMeshesToModelPart(self, model_part_name):
            model_part = self._CreateModelPart()

            geometry_name = "Line"
            condition_name = "LineCondition2D2N"
            props_id = 12

            mesh_description = { "conditions" : {geometry_name : {condition_name : props_id} } }

            nodes_mesh_1 = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            geometries_mesh_1 = {geometry_name : {i+1 : [i+1, i+2] for i in range(14)}}
            attrs_mesh_1 = { 'GetNodesAndGeometricalEntities.return_value': (nodes_mesh_1, geometries_mesh_1) }
            mesh_interface_mock_mesh_1 = MagicMock(spec=MeshInterface)
            mesh_interface_mock_mesh_1.configure_mock(**attrs_mesh_1)

            nodes_mesh_2 = {i+1 : [i*2,i+88.5, i-1] for i in range(33,39)}
            geometries_mesh_2 = {geometry_name : {i+1 : [i+1, i+2] for i in range(33,38)}}
            attrs_mesh_2 = { 'GetNodesAndGeometricalEntities.return_value': (nodes_mesh_2, geometries_mesh_2) }
            mesh_interface_mock_mesh_2 = MagicMock(spec=MeshInterface)
            mesh_interface_mock_mesh_2.configure_mock(**attrs_mesh_2)

            # this mesh is a subset of mesh 1, hence NO new entities should be created from this mesh!
            nodes_mesh_3 = {i+1 : [i+1,i*2,i+3.5] for i in range(5)}
            geometries_mesh_3 = {geometry_name : {i+1 : [i+1, i+2] for i in range(3)}}
            attrs_mesh_3 = { 'GetNodesAndGeometricalEntities.return_value': (nodes_mesh_3, geometries_mesh_3) }
            mesh_interface_mock_mesh_3 = MagicMock(spec=MeshInterface)
            mesh_interface_mock_mesh_3.configure_mock(**attrs_mesh_3)

            meshes = [
                geometries_io.Mesh(mesh_interface_mock_mesh_1, mesh_description, model_part_name),
                geometries_io.Mesh(mesh_interface_mock_mesh_2, mesh_description, model_part_name),
                geometries_io.Mesh(mesh_interface_mock_mesh_3, mesh_description, model_part_name)
            ]
            geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

            def CheckModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id))
                self.assertEqual(len(nodes_mesh_1)+len(nodes_mesh_2), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    if node.Id > 16:
                        ref_nodes = nodes_mesh_2
                    else:
                        ref_nodes = nodes_mesh_1

                    self.assertTrue(node.Id in ref_nodes)

                    orig_node_coords = ref_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                self.assertEqual(len(geometries_mesh_1[geometry_name])+len(geometries_mesh_2[geometry_name]), model_part_to_check.NumberOfConditions())
                for elem in model_part_to_check.Conditions:
                    # checking the connectivities
                    # Id offset is required because Conditions are renumbered!
                    if elem.Id > 14:
                        ref_geometries = geometries_mesh_2[geometry_name]
                        id_offset = 19
                    else:
                        ref_geometries = geometries_mesh_1[geometry_name]
                        id_offset = 0

                    self.assertTrue(elem.Id+id_offset in ref_geometries)
                    nodes_id_list = sorted([node.Id for node in elem.GetNodes()])
                    self.assertListEqual(sorted(ref_geometries[elem.Id+id_offset]), nodes_id_list)

            self.__RecursiveCheckModelParts(model_part, model_part_name, CheckModelPart)


        def test_add_to_existing_modelpart(self):
            # in the other tests the (sub-)modelparts to which the entities are being don't exist yet
            # in this test we make sure that it is possible to add entities to existing ModelParts
            main_model_part = self._CreateModelPart()
            sub_model_part = main_model_part.CreateSubModelPart("abc_sub")
            the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}

            attrs = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, {}) }
            mesh_interface_mock = MagicMock(spec=MeshInterface)
            mesh_interface_mock.configure_mock(**attrs)

            meshes = [geometries_io.Mesh(mesh_interface_mock, {}, sub_model_part.Name)]
            geometries_io.GeometriesIO.AddMeshes(main_model_part, meshes)

            def CheckModelPart(model_part_to_check):
                self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in the_nodes)

                    orig_node_coords = the_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

            self.__RecursiveCheckModelParts(main_model_part, sub_model_part.Name, CheckModelPart)

        def test_use_exsting_properties(self):
            # in the other tests the properties that are used for the creation of element/conditions
            # exist already. In this test the properties of the parent ModelPart are used
            main_model_part = self._CreateModelPart()
            sub_model_part = main_model_part.CreateSubModelPart("abc_sub")

            geometry_name = "Line"
            element_name = "Element2D2N"
            props_id = 12

            main_model_part.CreateNewProperties(props_id) # only exist in the main, but not yet in the submodelpart

            mesh_description = { "elements" : {geometry_name : {element_name : props_id} } }

            the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            the_geom_entities = {geometry_name : {i+1 : [i+1, i+2] for i in range(14)}}

            attrs = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, the_geom_entities) }
            mesh_interface_mock = MagicMock(spec=MeshInterface)
            mesh_interface_mock.configure_mock(**attrs)

            meshes = [geometries_io.Mesh(mesh_interface_mock, mesh_description, sub_model_part.Name)]
            geometries_io.GeometriesIO.AddMeshes(main_model_part, meshes)

            def CheckModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id))
                self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in the_nodes)

                    orig_node_coords = the_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                self.assertEqual(len(the_geom_entities[geometry_name]), model_part_to_check.NumberOfElements())
                for elem in model_part_to_check.Elements:
                    # checking the connectivities
                    self.assertTrue(elem.Id in the_geom_entities[geometry_name])
                    nodes_id_list = sorted([node.Id for node in elem.GetNodes()])
                    self.assertListEqual(sorted(the_geom_entities[geometry_name][elem.Id]), nodes_id_list)

            self.__RecursiveCheckModelParts(main_model_part, sub_model_part.Name, CheckModelPart)

        def test_add_entities_to_Root_and_SubModelPart(self):
            # in this test we check if adding the same entities to a main and submodelpart works
            # first we add the entities to the submodelpart, then to the parent modelpart
            # the created entities must be the same!
            main_model_part = self._CreateModelPart()
            sub_model_part = main_model_part.CreateSubModelPart("abc_sub")

            geometry_name = "Line"
            element_name = "Element2D2N"
            props_id = 3

            mesh_description = { "elements" : {geometry_name : {element_name : props_id} } }

            nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            geometries = {geometry_name : {i+1 : [i+1, i+2] for i in range(14)}}
            attrs = { 'GetNodesAndGeometricalEntities.return_value': (nodes, geometries) }

            mesh_interface_mock_sub_mp = MagicMock(spec=MeshInterface)
            mesh_interface_mock_sub_mp.configure_mock(**attrs)

            mesh_interface_mock_main_mp = MagicMock(spec=MeshInterface)
            mesh_interface_mock_main_mp.configure_mock(**attrs)

            meshes = [
                geometries_io.Mesh(mesh_interface_mock_sub_mp,  mesh_description, sub_model_part.Name),
                geometries_io.Mesh(mesh_interface_mock_main_mp, mesh_description, main_model_part.Name)
            ]
            geometries_io.GeometriesIO.AddMeshes(main_model_part, meshes)

            def CheckModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id))
                self.assertEqual(len(nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in nodes)

                    orig_node_coords = nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                self.assertEqual(len(geometries[geometry_name]), model_part_to_check.NumberOfElements())
                for elem in model_part_to_check.Elements:
                    # checking the connectivities
                    ref_geometries = geometries[geometry_name]

                    self.assertTrue(elem.Id in ref_geometries)
                    nodes_id_list = sorted([node.Id for node in elem.GetNodes()])
                    self.assertListEqual(sorted(ref_geometries[elem.Id]), nodes_id_list)

            self.__RecursiveCheckModelParts(main_model_part, sub_model_part.Name, CheckModelPart)

        def test_add_entities_to_different_SubModelPart(self):
            # in this test we check if adding the same entities to two sibling-submodelpart works
            # the entities are added one after the other, and the created entities must be the same!
            main_model_part = self._CreateModelPart()
            sub_model_part_1 = main_model_part.CreateSubModelPart("abc_sub")
            sub_model_part_2 = main_model_part.CreateSubModelPart("def_sub")

            geometry_name = "Line"
            element_name = "Element2D2N"
            props_id = 3

            mesh_description = { "elements" : {geometry_name : {element_name : props_id} } }

            nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            geometries = {geometry_name : {i+1 : [i+1, i+2] for i in range(14)}}
            attrs = { 'GetNodesAndGeometricalEntities.return_value': (nodes, geometries) }

            mesh_interface_mock_sub_mp_1 = MagicMock(spec=MeshInterface)
            mesh_interface_mock_sub_mp_1.configure_mock(**attrs)

            mesh_interface_mock_sub_mp_2 = MagicMock(spec=MeshInterface)
            mesh_interface_mock_sub_mp_2.configure_mock(**attrs)

            meshes = [
                geometries_io.Mesh(mesh_interface_mock_sub_mp_1, mesh_description, sub_model_part_1.Name),
                geometries_io.Mesh(mesh_interface_mock_sub_mp_2, mesh_description, sub_model_part_2.Name)
            ]
            geometries_io.GeometriesIO.AddMeshes(main_model_part, meshes)

            def CheckModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id))
                self.assertEqual(len(nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in nodes)

                    orig_node_coords = nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                self.assertEqual(len(geometries[geometry_name]), model_part_to_check.NumberOfElements())
                for elem in model_part_to_check.Elements:
                    # checking the connectivities
                    ref_geometries = geometries[geometry_name]

                    self.assertTrue(elem.Id in ref_geometries)
                    nodes_id_list = sorted([node.Id for node in elem.GetNodes()])
                    self.assertListEqual(sorted(ref_geometries[elem.Id]), nodes_id_list)

            self.__RecursiveCheckModelParts(main_model_part, sub_model_part_1.Name, CheckModelPart)
            self.__RecursiveCheckModelParts(main_model_part, sub_model_part_2.Name, CheckModelPart)

        def test_add_entities_different_properties_ids(self):
            # checking if an error is thrown if the same entities are added with different properties Ids
            main_model_part = self._CreateModelPart()
            sub_model_part_1 = main_model_part.CreateSubModelPart("abc_sub")
            sub_model_part_2 = main_model_part.CreateSubModelPart("def_sub")

            geometry_name = "Line"
            element_name = "Element2D2N"
            props_id = 3

            mesh_description = { "elements" : {geometry_name : {element_name : props_id} } }
            mesh_description_2 = { "elements" : {geometry_name : {element_name : props_id+2} } }

            nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            geometries = {geometry_name : {i+1 : [i+1, i+2] for i in range(14)}}
            attrs = { 'GetNodesAndGeometricalEntities.return_value': (nodes, geometries) }

            mesh_interface_mock_sub_mp_1 = MagicMock(spec=MeshInterface)
            mesh_interface_mock_sub_mp_1.configure_mock(**attrs)

            mesh_interface_mock_sub_mp_2 = MagicMock(spec=MeshInterface)
            mesh_interface_mock_sub_mp_2.configure_mock(**attrs)

            meshes = [
                geometries_io.Mesh(mesh_interface_mock_sub_mp_1, mesh_description, sub_model_part_1.Name),
                geometries_io.Mesh(mesh_interface_mock_sub_mp_2, mesh_description_2, sub_model_part_2.Name)
            ]

            # this should throw because the entities that are supposed to be added to smp_2 have a different properties-Id, which is not possible!
            with self.assertRaisesRegex(Exception, "Mismatch in properties Ids!\nTrying to use properties with Id 5 with an existing entity that has the properties with Id 3"):
                geometries_io.GeometriesIO.AddMeshes(main_model_part, meshes)

        def test_add_elements_and_conditions_to_same_model_part(self):
            model_part = self._CreateModelPart()
            smp_name = "smp_elemes_conds"

            geometry_name_1D = "Line"
            condition_name = "LineCondition2D2N"
            props_id_conditions = 12

            geometry_name_2D = "Triangle"
            element_name = "Element2D3N"
            props_id_elements = 77

            mesh_description = { "elements"   : {geometry_name_2D : {element_name : props_id_elements}},
                                 "conditions" : {geometry_name_1D : {condition_name : props_id_conditions}}}

            the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            geometries = {
                geometry_name_1D : {i+1 : [i+1, i+2] for i in range(12)},
                geometry_name_2D : {i+1 : [(i+1)%15+1, (i+3)%15+1, (i+4)%15+1] for i in range(25)}}

            attrs = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, geometries) }
            mesh_interface_mock = MagicMock(spec=MeshInterface)
            mesh_interface_mock.configure_mock(**attrs)

            meshes = [geometries_io.Mesh( mesh_interface_mock, mesh_description, smp_name)]
            geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

            def CheckModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id_elements))
                self.assertTrue(model_part_to_check.HasProperties(props_id_conditions))

                self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in the_nodes)

                    orig_node_coords = the_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                elem_geoms = geometries[geometry_name_2D]
                self.assertEqual(len(elem_geoms), model_part_to_check.NumberOfElements())
                for elem in model_part_to_check.Elements:
                    # checking the connectivities
                    self.assertTrue(elem.Id in elem_geoms)
                    nodes_id_list = sorted([node.Id for node in elem.GetNodes()])
                    self.assertListEqual(sorted(elem_geoms[elem.Id]), nodes_id_list)
                    self.assertEqual(elem.Properties.Id, props_id_elements)

                cond_geoms = geometries[geometry_name_1D]
                self.assertEqual(len(cond_geoms), model_part_to_check.NumberOfConditions())
                for cond in model_part_to_check.Conditions:
                    # checking the connectivities
                    self.assertTrue(cond.Id in cond_geoms)
                    nodes_id_list = sorted([node.Id for node in cond.GetNodes()])
                    self.assertListEqual(sorted(cond_geoms[cond.Id]), nodes_id_list)
                    self.assertEqual(cond.Properties.Id, props_id_conditions)

            self.__RecursiveCheckModelParts(model_part, smp_name, CheckModelPart)

        def test_add_elements_and_conditions_to_different_model_parts(self):
            model_part = self._CreateModelPart()

            smp_name_conds = "smp_line_conds"
            geometry_name_1D = "Line"
            condition_name = "LineCondition2D2N"
            props_id_conditions = 12

            smp_name_elems = "smp_with_elements"
            geometry_name_2D = "Triangle"
            element_name = "Element2D3N"
            props_id_elements = 77

            mesh_description_elems = {"elements"   : {geometry_name_2D : {element_name : props_id_elements}}}
            mesh_description_conds = {"conditions" : {geometry_name_1D : {condition_name : props_id_conditions}}}

            the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            geometries_1D = {geometry_name_1D : {i+1 : [i+1, i+2] for i in range(12)}}
            geometries_2D = {geometry_name_2D : {i+1 : [(i+1)%15+1, (i+3)%15+1, (i+4)%15+1] for i in range(25)}}

            attrs_1D = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, geometries_1D) }
            mesh_interface_mock_1D = MagicMock(spec=MeshInterface)
            mesh_interface_mock_1D.configure_mock(**attrs_1D)

            attrs_2D = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, geometries_2D) }
            mesh_interface_mock_2D = MagicMock(spec=MeshInterface)
            mesh_interface_mock_2D.configure_mock(**attrs_2D)

            meshes = [
                geometries_io.Mesh(mesh_interface_mock_1D, mesh_description_conds, smp_name_conds),
                geometries_io.Mesh(mesh_interface_mock_2D, mesh_description_elems, smp_name_elems)
            ]
            geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

            def CheckElementsModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id_elements))

                self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in the_nodes)

                    orig_node_coords = the_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                elem_geoms = geometries_2D[geometry_name_2D]
                self.assertEqual(len(elem_geoms), model_part_to_check.NumberOfElements())
                for elem in model_part_to_check.Elements:
                    # checking the connectivities
                    self.assertTrue(elem.Id in elem_geoms)
                    nodes_id_list = sorted([node.Id for node in elem.GetNodes()])
                    self.assertListEqual(sorted(elem_geoms[elem.Id]), nodes_id_list)
                    self.assertEqual(elem.Properties.Id, props_id_elements)

            def CheckConditionsModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id_conditions))

                self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in the_nodes)

                    orig_node_coords = the_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                cond_geoms = geometries_1D[geometry_name_1D]
                self.assertEqual(len(cond_geoms), model_part_to_check.NumberOfConditions())
                for cond in model_part_to_check.Conditions:
                    # checking the connectivities
                    self.assertTrue(cond.Id in cond_geoms)
                    nodes_id_list = sorted([node.Id for node in cond.GetNodes()])
                    self.assertListEqual(sorted(cond_geoms[cond.Id]), nodes_id_list)
                    self.assertEqual(cond.Properties.Id, props_id_conditions)

            def CheckMainModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id_elements))
                self.assertTrue(model_part_to_check.HasProperties(props_id_conditions))

                self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in the_nodes)

                    orig_node_coords = the_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                CheckElementsModelPart(model_part_to_check.GetSubModelPart(smp_name_elems))
                CheckConditionsModelPart(model_part_to_check.GetSubModelPart(smp_name_conds))

            CheckMainModelPart(model_part)
            CheckElementsModelPart(model_part.GetSubModelPart(smp_name_elems))
            CheckConditionsModelPart(model_part.GetSubModelPart(smp_name_conds))

        def test_add_elements_and_conditions_on_same_geometry(self):
            model_part = self._CreateModelPart()
            smp_name = "smp_elemes_conds"

            condition_name = "SurfaceCondition3D3N"
            props_id_conditions = 12

            geometry_name_2D = "Triangle"
            element_name = "Element2D3N"
            props_id_elements = 77

            mesh_description = { "elements"   : {geometry_name_2D : {element_name : props_id_elements}},
                                 "conditions" : {geometry_name_2D : {condition_name : props_id_conditions}}}

            the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            geometries = {geometry_name_2D : {i+1 : [(i+1)%15+1, (i+3)%15+1, (i+4)%15+1] for i in range(25)}}

            attrs = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, geometries) }
            mesh_interface_mock = MagicMock(spec=MeshInterface)
            mesh_interface_mock.configure_mock(**attrs)

            meshes = [geometries_io.Mesh(mesh_interface_mock, mesh_description, smp_name)]
            geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

            def CheckModelPart(model_part_to_check):
                self.assertTrue(model_part_to_check.HasProperties(props_id_elements))
                self.assertTrue(model_part_to_check.HasProperties(props_id_conditions))

                self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
                for node in model_part_to_check.Nodes:
                    self.assertTrue(node.Id in the_nodes)

                    orig_node_coords = the_nodes[node.Id]
                    self.assertAlmostEqual(orig_node_coords[0], node.X)
                    self.assertAlmostEqual(orig_node_coords[1], node.Y)
                    self.assertAlmostEqual(orig_node_coords[2], node.Z)

                elem_geoms = geometries[geometry_name_2D]
                self.assertEqual(len(elem_geoms), model_part_to_check.NumberOfElements())
                for elem in model_part_to_check.Elements:
                    # checking the connectivities
                    self.assertTrue(elem.Id in elem_geoms)
                    nodes_id_list = sorted([node.Id for node in elem.GetNodes()])
                    self.assertListEqual(sorted(elem_geoms[elem.Id]), nodes_id_list)
                    self.assertEqual(elem.Properties.Id, props_id_elements)

                cond_geoms = geometries[geometry_name_2D]
                self.assertEqual(len(cond_geoms), model_part_to_check.NumberOfConditions())
                for cond in model_part_to_check.Conditions:
                    # checking the connectivities
                    self.assertTrue(cond.Id in cond_geoms)
                    nodes_id_list = sorted([node.Id for node in cond.GetNodes()])
                    self.assertListEqual(sorted(cond_geoms[cond.Id]), nodes_id_list)
                    self.assertEqual(cond.Properties.Id, props_id_conditions)

            self.__RecursiveCheckModelParts(model_part, smp_name, CheckModelPart)

        def test_add_to_subsub_model_parts(self):
            model_part = py_model_part.ModelPart()

            smp_3D = "Parts_domain"
            geometry_name_3D = "Tetra"
            element_name_3D = "Element3D4N"
            props_id_3D = 4

            smp_2D = "surface"
            smp_2D_full_name = smp_3D + "." + smp_2D
            geometry_name_2D = "Triangle"
            element_name_2D = "Element3D3N"
            condition_name_2D = "SurfaceCondition3D3N"
            props_id_2D_elem = 11
            props_id_2D_cond = 16

            smp_1D = "edge_fixed"
            smp_1D_full_name = smp_3D + "." + smp_1D
            geometry_name_1D = "Edge"
            condition_name_1D = "LineCondition2D2N"
            props_id_1D = 22

            smp_0D = "corner_point"
            smp_0D_full_name = smp_1D_full_name + "." + smp_0D
            geometry_name_0D = "0D"
            condition_name_0D = "PointCondition2D1N"
            props_id_0D = 78

            mesh_description_3D = { "elements" : {geometry_name_3D : {element_name_3D : props_id_3D} } }
            mesh_description_2D = {
                "elements"   : {geometry_name_2D : {element_name_2D : props_id_2D_elem} },
                "conditions" : {geometry_name_2D : {condition_name_2D : props_id_2D_cond} }
            }
            mesh_description_1D = { "conditions" : {geometry_name_1D : {condition_name_1D : props_id_1D} } }
            mesh_description_0D = { "conditions" : {geometry_name_0D : {condition_name_0D : props_id_0D} } }

            nodes_3D = {i+1 : [i+1,i*2,i+3.5] for i in range(33)}
            geometries_3D = {geometry_name_3D : {i+1 : [(i+2)%33+1, (i+6)%33+1, (i+4)%33+1, (i+8)%33+1] for i in range(55)}}

            nodes_2D = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
            geometries_2D = {geometry_name_2D : {i+1 : [(i+1)%15+1, (i+3)%15+1, (i+4)%15+1] for i in range(25)}}

            nodes_1D = {i+1 : [i+18,i*20,i-23.5] for i in range(66, 88)}
            geometries_1D = {geometry_name_1D : {i+1 : [i+67, i+68] for i in range(12)}}

            geometries_0D = {geometry_name_0D : {i+1 : [i+72] for i in range(9)}}

            attrs_3D = { 'GetNodesAndGeometricalEntities.return_value': (nodes_3D, geometries_3D) }
            mesh_interface_mock_3D = MagicMock(spec=MeshInterface)
            mesh_interface_mock_3D.configure_mock(**attrs_3D)

            attrs_2D = { 'GetNodesAndGeometricalEntities.return_value': (nodes_2D, geometries_2D) }
            mesh_interface_mock_2D = MagicMock(spec=MeshInterface)
            mesh_interface_mock_2D.configure_mock(**attrs_2D)

            attrs_1D = { 'GetNodesAndGeometricalEntities.return_value': (nodes_1D, geometries_1D) }
            mesh_interface_mock_1D = MagicMock(spec=MeshInterface)
            mesh_interface_mock_1D.configure_mock(**attrs_1D)

            attrs_0D = { 'GetNodesAndGeometricalEntities.return_value': (nodes_1D, geometries_0D) }
            mesh_interface_mock_0D = MagicMock(spec=MeshInterface)
            mesh_interface_mock_0D.configure_mock(**attrs_0D)

            meshes = [
                geometries_io.Mesh(mesh_interface_mock_3D, mesh_description_3D, smp_3D),
                geometries_io.Mesh(mesh_interface_mock_2D, mesh_description_2D, smp_2D_full_name),
                geometries_io.Mesh(mesh_interface_mock_1D, mesh_description_1D, smp_1D_full_name),
                geometries_io.Mesh(mesh_interface_mock_0D, mesh_description_0D, smp_0D_full_name)
            ]
            geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

            def CheckProperties(model_part, list_props_ids):
                self.assertEqual(model_part.NumberOfProperties(), len(list_props_ids))
                for props_id in list_props_ids:
                    self.assertTrue(model_part.HasProperties(props_id))
                    self.assertTrue(model_part.RecursivelyHasProperties(props_id))

            def CheckSubModelParts(model_part, list_smp_names):
                self.assertEqual(model_part.NumberOfSubModelParts(), len(list_smp_names))
                for smp_name in list_smp_names:
                    self.assertTrue(model_part.HasSubModelPart(smp_name))


            # Checking MainModelPart
            CheckProperties(model_part, [props_id_3D, props_id_2D_elem, props_id_2D_cond, props_id_1D, props_id_0D])
            CheckSubModelParts(model_part, [smp_3D])
            self.assertEqual(55, model_part.NumberOfNodes())
            self.assertEqual(55+25, model_part.NumberOfElements())
            self.assertEqual(25+12+9, model_part.NumberOfConditions())

            # Checking 3D SubModelPart
            mp_3D = model_part.GetSubModelPart(smp_3D)
            CheckProperties(mp_3D, [props_id_3D, props_id_2D_elem, props_id_2D_cond, props_id_1D, props_id_0D])
            CheckSubModelParts(mp_3D, [smp_2D, smp_1D])
            self.assertEqual(55, mp_3D.NumberOfNodes())
            self.assertEqual(55+25, mp_3D.NumberOfElements())
            self.assertEqual(25+12+9, mp_3D.NumberOfConditions())

            # Checking 2D SubModelPart
            mp = mp_3D.GetSubModelPart(smp_2D) # SubModelPart of 3D Modelpart
            CheckProperties(mp, [props_id_2D_elem, props_id_2D_cond])
            CheckSubModelParts(mp, []) # has no SubModelParts
            self.assertEqual(15, mp.NumberOfNodes())
            self.assertEqual(25, mp.NumberOfElements())
            self.assertEqual(25, mp.NumberOfConditions())

            # Checking 1D SubModelPart
            mp = mp_3D.GetSubModelPart(smp_1D) # SubModelPart of 3D Modelpart
            CheckProperties(mp, [props_id_1D, props_id_0D])
            CheckSubModelParts(mp, [smp_0D])
            self.assertEqual(22, mp.NumberOfNodes())
            self.assertEqual(0, mp.NumberOfElements())
            self.assertEqual(12+9, mp.NumberOfConditions())

            # Checking 0D SubModelPart
            mp = mp.GetSubModelPart(smp_0D) # SubModelPart of 1D Modelpart
            CheckProperties(mp, [props_id_0D])
            CheckSubModelParts(mp, []) # has no SubModelParts
            self.assertEqual(22, mp.NumberOfNodes())
            self.assertEqual(0, mp.NumberOfElements())
            self.assertEqual(9, mp.NumberOfConditions())


        ### Auxiliar testing functions ###
        def __RecursiveCheckModelParts(self, model_part, model_part_name, check_fct_ptr):
            check_fct_ptr(model_part)

            sub_model_part_names = model_part_name.split(".")
            model_part_name = sub_model_part_names[0]

            if model_part_name != "":
                self.assertTrue(model_part.HasSubModelPart(model_part_name))
                model_part = model_part.GetSubModelPart(model_part_name)

                if len(sub_model_part_names) > 0:
                    self.__RecursiveCheckModelParts(model_part, ".".join(sub_model_part_names[1:]), check_fct_ptr)


@unittest.skipUnless(kratos_available, "Kratos not available")
class TestGeometriesIOWithMockMeshInterfaces_KratosModelPart(TestGeometriesIOWithMockMeshInterfaces.BaseTests):
    def _CreateModelPart(self, name="for_test"):
        self.model = KM.Model()
        return self.model.CreateModelPart(name)

class TestGeometriesIOWithMockMeshInterfaces_PyKratosModelPart(TestGeometriesIOWithMockMeshInterfaces.BaseTests):
    def _CreateModelPart(self, name="for_test"):
        return py_model_part.ModelPart(name)


class TestGeometriesIOWithSalome(SalomeTestCaseWithBox):
    # Note: the number of nodes & geometries are hardcoded and could theoretically change with different versions of salome
    def test_create_line_elements(self):
        model_part = py_model_part.ModelPart()

        geometry_name = "Edge"
        element_name = "Element2D2N"
        props_id = 12

        mesh_description = { "elements" : {geometry_name : {element_name : props_id} } }

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_tetra_e_1)
        mesh_interface = MeshInterface(existing_mesh_identifier)
        self.assertTrue(mesh_interface.CheckMeshIsValid())

        meshes = [geometries_io.Mesh(mesh_interface, mesh_description)]
        geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

        self.assertTrue(model_part.HasProperties(props_id))
        self.assertEqual(5, model_part.NumberOfNodes())
        for node in model_part.Nodes:
            self.assertAlmostEqual(200.0, node.X)
            self.assertAlmostEqual(200.0, node.Z)
        self.assertEqual(4, model_part.NumberOfElements())

    def test_create_hexa_elements(self):
        model_part = py_model_part.ModelPart()

        geometry_name = "Hexa"
        element_name = "Element3D8N"
        props_id = 4

        mesh_description = { "elements" : {geometry_name : {element_name : props_id} } }

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.mesh_hexa.GetMesh())
        mesh_interface = MeshInterface(existing_mesh_identifier)
        self.assertTrue(mesh_interface.CheckMeshIsValid())

        meshes = [geometries_io.Mesh(mesh_interface, mesh_description)]
        geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

        self.assertTrue(model_part.HasProperties(props_id))
        self.assertEqual(729, model_part.NumberOfNodes())
        self.assertEqual(512, model_part.NumberOfElements())

    def test_create_elements_and_conditions(self):
        model_part = py_model_part.ModelPart()

        smp_3D = "Parts_domain"
        geometry_name_3D = "Tetra"
        element_name_3D = "Element3D4N"
        props_id_3D = 4

        smp_2D = "surface"
        geometry_name_2D = "Triangle"
        element_name_2D = "Element3D3N"
        condition_name_2D = "SurfaceCondition3D3N"
        props_id_2D_elem = 11
        props_id_2D_cond = 16

        smp_1D = "edge_fixed"
        geometry_name_1D = "Edge"
        condition_name_1D = "LineCondition2D2N"
        props_id_1D = 22

        smp_0D = "corner_point" # this will be a SubSubModelPart of smp_1D
        geometry_name_0D = "0D"
        condition_name_0D = "PointCondition2D1N"
        props_id_0D = 78

        mesh_description_3D = { "elements" : {geometry_name_3D : {element_name_3D : props_id_3D} } }
        mesh_description_2D = {
            "elements"   : {geometry_name_2D : {element_name_2D : props_id_2D_elem} },
            "conditions" : {geometry_name_2D : {condition_name_2D : props_id_2D_cond} }
        }
        mesh_description_1D = { "conditions" : {geometry_name_1D : {condition_name_1D : props_id_1D} } }
        mesh_description_0D = { "conditions" : {geometry_name_0D : {condition_name_0D : props_id_0D} } }

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.mesh_tetra.GetMesh())
        mesh_interface = MeshInterface(existing_mesh_identifier)
        self.assertTrue(mesh_interface.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.group_tetra_0D_elements)
        mesh_interface_0D = MeshInterface(existing_mesh_identifier)
        self.assertTrue(mesh_interface_0D.CheckMeshIsValid())

        # Note: "mesh_interface" was created from the main-mesh, hence it contains all entities!
        # this means that all nodes are in all SubModelParts!
        meshes = [
            geometries_io.Mesh(mesh_interface, mesh_description_3D, smp_3D),
            geometries_io.Mesh(mesh_interface, mesh_description_2D, smp_2D),
            geometries_io.Mesh(mesh_interface, mesh_description_1D, smp_1D),
            geometries_io.Mesh(mesh_interface_0D, mesh_description_0D, smp_1D+"."+smp_0D) # just for fun using a subsubmodelpart and a different meshinterface
        ]
        geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

        def CheckProperties(model_part, list_props_ids):
            self.assertEqual(model_part.NumberOfProperties(), len(list_props_ids))
            for props_id in list_props_ids:
                self.assertTrue(model_part.HasProperties(props_id))
                self.assertTrue(model_part.RecursivelyHasProperties(props_id))

        def CheckSubModelParts(model_part, list_smp_names):
            self.assertEqual(model_part.NumberOfSubModelParts(), len(list_smp_names))
            for smp_name in list_smp_names:
                self.assertTrue(model_part.HasSubModelPart(smp_name))

        # Checking MainModelPart
        CheckProperties(model_part, [props_id_3D, props_id_2D_elem, props_id_2D_cond, props_id_1D, props_id_0D])
        CheckSubModelParts(model_part, [smp_3D, smp_2D, smp_1D])
        self.assertEqual(366, model_part.NumberOfNodes())
        self.assertEqual(1355+480, model_part.NumberOfElements())
        self.assertEqual(480+48+10, model_part.NumberOfConditions())

        # Checking 3D SubModelPart
        mp = model_part.GetSubModelPart(smp_3D)
        CheckProperties(mp, [props_id_3D])
        CheckSubModelParts(mp, []) # has no SubModelParts
        self.assertEqual(366, mp.NumberOfNodes())
        self.assertEqual(1355, mp.NumberOfElements())
        self.assertEqual(0, mp.NumberOfConditions())

        # Checking 2D SubModelPart
        mp = model_part.GetSubModelPart(smp_2D)
        CheckProperties(mp, [props_id_2D_elem, props_id_2D_cond])
        CheckSubModelParts(mp, []) # has no SubModelParts
        self.assertEqual(366, mp.NumberOfNodes())
        self.assertEqual(480, mp.NumberOfElements())
        self.assertEqual(480, mp.NumberOfConditions())

        # Checking 1D SubModelPart
        mp = model_part.GetSubModelPart(smp_1D)
        CheckProperties(mp, [props_id_1D, props_id_0D])
        CheckSubModelParts(mp, [smp_0D])
        self.assertEqual(366, mp.NumberOfNodes())
        self.assertEqual(0, mp.NumberOfElements())
        self.assertEqual(48+10, mp.NumberOfConditions()) # 48 edges + 10 0D

        # Checking 0D SubModelPart
        mp = mp.GetSubModelPart(smp_0D) # is a submodelpart of 1D
        CheckProperties(mp, [props_id_0D])
        CheckSubModelParts(mp, []) # has no SubModelParts
        self.assertEqual(10, mp.NumberOfNodes())
        self.assertEqual(0, mp.NumberOfElements())
        self.assertEqual(10, mp.NumberOfConditions())

    def test_add_from_different_meshes(self):
        # adding meshes from different main-meshes is not possible!
        model_part = py_model_part.ModelPart()

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_tetra_e_1)
        mesh_interface_tetra = MeshInterface(existing_mesh_identifier)
        self.assertTrue(mesh_interface_tetra.CheckMeshIsValid())

        existing_mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_hexa_e_1)
        mesh_interface_hexa = MeshInterface(existing_mesh_identifier)
        self.assertTrue(mesh_interface_hexa.CheckMeshIsValid())

        meshes = [
            geometries_io.Mesh(mesh_interface_tetra, None),
            geometries_io.Mesh(mesh_interface_hexa, None)
        ]

        with self.assertRaisesRegex(Exception, 'The meshes to be added to ModelPart "default" don\'t belong to the same main mesh!\nThis is necessary to ensure a consistent numbering.'):
            geometries_io.GeometriesIO.AddMeshes(model_part, meshes)


if __name__ == '__main__':
    unittest.main()
