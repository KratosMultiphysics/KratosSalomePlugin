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
from unittest.mock import MagicMock
from abc import ABCMeta, abstractmethod

# plugin imports
sys.path.append(os.pardir) # required to be able to do "from plugin import xxx"
sys.path.append(os.path.join(os.pardir, "plugin")) # required that the imports from the "plugin" folder work inside the py-modules of the plugin
import plugin.model_part as py_model_part
from plugin import geometries_io
from plugin.mesh_interface import MeshInterface

# other imports
try:
    import KratosMultiphysics as KM
    kratos_available = True
except:
    kratos_available = False


class TestGeometriesIOWithMockMeshInterfaces(object):
    """This TestCase contains basic tests for the GeometriesIO where the MeshInterface is substituted by a Mock object
    """
    class BaseTests(unittest.TestCase, metaclass=ABCMeta):
        @abstractmethod
        def _CreateModelPart(self, name):
            pass

        def test_AddMesh_nodes_from_one_mesh_to_main_model_part(self):
            self.__ExecuteTestAddNodesFromOneMeshToModelPart("")

        def test_AddMesh_nodes_from_one_mesh_to_sub_model_part(self):
            self.__ExecuteTestAddNodesFromOneMeshToModelPart("sub_mp")

        def test_AddMesh_nodes_from_one_mesh_to_sub_sub_model_part(self):
            self.__ExecuteTestAddNodesFromOneMeshToModelPart("subda3_mp.the_sub_sub_model_part")

        def __ExecuteTestAddNodesFromOneMeshToModelPart(self, model_part_name):
            model_part = self._CreateModelPart()
            the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}

            attrs = { 'GetNodesAndGeometricalEntities.return_value': (the_nodes, {}) }
            mesh_interface_mock = MagicMock(spec=MeshInterface)
            mesh_interface_mock.configure_mock(**attrs)

            meshes = [geometries_io.Mesh(model_part_name, mesh_interface_mock, {})]
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


        def test_AddMesh_nodes_from_multiple_meshes_to_main_model_part(self):
            self.__ExecuteTestAddNodesFromMultipleMeshesToModelPart("")

        def test_AddMesh_nodes_from_multiple_meshes_to_sub_model_part(self):
            self.__ExecuteTestAddNodesFromMultipleMeshesToModelPart("my_sub")

        def test_AddMesh_nodes_from_multiple_meshes_to_sub_sub_model_part(self):
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
                geometries_io.Mesh(model_part_name, mesh_interface_mock_mesh_1, {}),
                geometries_io.Mesh(model_part_name, mesh_interface_mock_mesh_2, {}),
                geometries_io.Mesh(model_part_name, mesh_interface_mock_mesh_3, {})
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


        def test_AddMesh_elements_from_one_mesh_to_main_model_part(self):
            self.__ExecuteTestAddElementsFromOneMeshToModelPart("")

        def test_AddMesh_elements_from_one_mesh_to_sub_model_part(self):
            self.__ExecuteTestAddElementsFromOneMeshToModelPart("sub_mp_el")

        def test_AddMesh_elements_from_one_mesh_to_sub_sub_model_part(self):
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

            meshes = [geometries_io.Mesh(model_part_name, mesh_interface_mock, mesh_description)]
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


        def test_AddMesh_elements_from_multiple_meshes_to_main_model_part(self):
            self.__ExecuteTestAddElementsFromMultipleMeshesToModelPart("")

        def test_AddMesh_elements_from_multiple_meshes_to_sub_model_part(self):
            self.__ExecuteTestAddElementsFromMultipleMeshesToModelPart("sub_mpss_el")

        def test_AddMesh_elements_from_multiple_meshes_to_sub_sub_model_part(self):
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
                geometries_io.Mesh(model_part_name, mesh_interface_mock_mesh_1, mesh_description),
                geometries_io.Mesh(model_part_name, mesh_interface_mock_mesh_2, mesh_description),
                geometries_io.Mesh(model_part_name, mesh_interface_mock_mesh_3, mesh_description)
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

                    self.assertTrue(elem.Id+id_offset in ref_geometries, msg=elem.Id+id_offset)
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

            meshes = [geometries_io.Mesh(sub_model_part.Name, mesh_interface_mock, {})]
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

            meshes = [geometries_io.Mesh(sub_model_part.Name, mesh_interface_mock, mesh_description)]
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
                geometries_io.Mesh(sub_model_part.Name,  mesh_interface_mock_sub_mp,  mesh_description),
                geometries_io.Mesh(main_model_part.Name, mesh_interface_mock_main_mp, mesh_description)
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
                geometries_io.Mesh(sub_model_part_1.Name, mesh_interface_mock_sub_mp_1, mesh_description),
                geometries_io.Mesh(sub_model_part_2.Name, mesh_interface_mock_sub_mp_2, mesh_description)
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
                geometries_io.Mesh(sub_model_part_1.Name, mesh_interface_mock_sub_mp_1, mesh_description),
                geometries_io.Mesh(sub_model_part_2.Name, mesh_interface_mock_sub_mp_2, mesh_description_2)
            ]
            # this should throw because the entities that are supposed to be added to smp_2 have a different properties-Id, which is not possible!

            with self.assertRaisesRegex(Exception, "Mismatch in properties Ids!\nTrying to use properties with Id 5 with an existing element that has the properties with Id 3"):
                geometries_io.GeometriesIO.AddMeshes(main_model_part, meshes)


        ### Auxiliar testing functions ###
        def __RecursiveCheckModelParts(self, model_part, model_part_name, check_fct_ptr):
            check_fct_ptr(model_part)

            sub_model_part_names = model_part_name.split(".")
            model_part_name = sub_model_part_names[0]

            if model_part_name != "":
                self.assertTrue(model_part.HasSubModelPart(model_part_name))
                model_part = model_part.GetSubModelPart(model_part_name)

                if len(sub_model_part_names) > 0:
                    model_part = self.__RecursiveCheckModelParts(model_part, ".".join(sub_model_part_names[1:]), check_fct_ptr)


@unittest.skipUnless(kratos_available, "Kratos not available")
class TestGeometriesIOWithMockMeshInterfaces_KratosModelPart(TestGeometriesIOWithMockMeshInterfaces.BaseTests):
    def _CreateModelPart(self, name="for_test"):
        self.model = KM.Model()
        return self.model.CreateModelPart(name)

class TestGeometriesIOWithMockMeshInterfaces_PyKratosModelPart(TestGeometriesIOWithMockMeshInterfaces.BaseTests):
    def _CreateModelPart(self, name="for_test"):
        return py_model_part.ModelPart(name)


if __name__ == '__main__':
    unittest.main()


# TODO:
# - Test for Conditions
# - Test with adding elements AND conditions
# - Test with using Salome instead of the Mock object to make sure the entire Toolchain works
