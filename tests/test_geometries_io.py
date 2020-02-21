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

# TODO probably makes sense to set it up in the same way as the ModelPart test, here with and without salome
# without Salome a Mock could do the Job of MeshInterface to have simple and small tests
# will also be a good excercise for using Mocks

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
                for i_node, node in enumerate(model_part_to_check.Nodes):
                    self.assertEqual(i_node+1, node.Id)
                    self.assertAlmostEqual(i_node+1, node.X)
                    self.assertAlmostEqual(i_node*2, node.Y)
                    self.assertAlmostEqual(i_node+3.5, node.Z)

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
                print("Checking", model_part_to_check.FullName())
                self.assertEqual(len(nodes_mesh_1) + len(nodes_mesh_2), model_part_to_check.NumberOfNodes())
                counter=0 # needed due to offsets in meshes (i.e. ranges start at 0)
                for i_node, node in enumerate(model_part_to_check.Nodes):
                    if i_node > 14:
                        self.assertEqual(i_node+10, node.Id) # there is a gap in the IDs
                        self.assertAlmostEqual(counter+3.5, node.X)
                        self.assertAlmostEqual(counter-13.22, node.Y)
                        self.assertAlmostEqual(counter*2, node.Z)
                        counter += 1
                    else:
                        self.assertEqual(i_node+1, node.Id)
                        self.assertAlmostEqual(i_node+1, node.X)
                        self.assertAlmostEqual(i_node*2, node.Y)
                        self.assertAlmostEqual(i_node+3.5, node.Z)

            self.__RecursiveCheckModelParts(model_part, model_part_name, CheckModelPart)


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







    # def test_AddMesh_only_nodes(self):
    #     mesh_description = {} # only adding the nodes, but not creating any elements or conditions

    #     the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}

    #     attrs = {
    #         'GetNodesAndGeometricalEntities.return_value': (the_nodes, {})
    #     }
    #     self.mesh_interface_mock.configure_mock(**attrs)

    #     mesh_name = "my_mesh"
    #     self.geom_io.AddMesh(mesh_name, self.mesh_interface_mock, mesh_description)

    #     self.assertTrue(self.model_part.HasSubModelPart(mesh_name)) # by default the mesh is added as a SubModelPart

    #     def CheckModelPart(model_part_to_check):
    #         self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
    #         for i_node, node in enumerate(model_part_to_check.Nodes):
    #             self.assertEqual(i_node+1, node.Id)
    #             self.assertAlmostEqual(i_node+1, node.X)
    #             self.assertAlmostEqual(i_node*2, node.Y)
    #             self.assertAlmostEqual(i_node+3.5, node.Z)

    #     # both ModelParts have to have the nodes (the nodes are added to the SubModelPart hence they should also be in the MainModelPart)
    #     CheckModelPart(self.model_part)
    #     CheckModelPart(self.model_part.GetSubModelPart(mesh_name))

    # def test_AddMesh_elements(self):
    #     entities_name = "Line"
    #     element_name = "SomeElement"
    #     props_id = 12
    #     self.model_part.CreateNewProperties(props_id) # creating it in the root

    #     mesh_description = {
    #         "elements" : {
    #             entities_name : {element_name : props_id}
    #         }
    #     }

    #     the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
    #     the_geom_entities = {entities_name : {i+1 : [i+1, i+2] for i in range(14)}}

    #     attrs = {
    #         'GetNodesAndGeometricalEntities.return_value': (the_nodes, the_geom_entities)
    #     }
    #     self.mesh_interface_mock.configure_mock(**attrs)

    #     mesh_name = "my_mesh"
    #     self.geom_io.AddMesh(mesh_name, self.mesh_interface_mock, mesh_description)

    #     self.assertTrue(self.model_part.HasSubModelPart(mesh_name)) # by default the mesh is added as a SubModelPart

    #     def CheckModelPart(model_part_to_check):
    #         self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
    #         for i_node, node in enumerate(model_part_to_check.Nodes):
    #             self.assertEqual(i_node+1, node.Id)
    #             self.assertAlmostEqual(i_node+1, node.X)
    #             self.assertAlmostEqual(i_node*2, node.Y)
    #             self.assertAlmostEqual(i_node+3.5, node.Z)

    #         self.assertEqual(len(the_geom_entities[entities_name]), model_part_to_check.NumberOfElements())
    #         for i_elem, elem in enumerate(model_part_to_check.Elements):
    #             self.assertEqual(i_elem+1, elem.Id)
    #             for i_node, node in enumerate(elem.nodes):
    #                 self.assertEqual(i_elem+1+i_node, node.Id)

    #     # both ModelParts have to have the nodes (the entities are added to the SubModelPart hence they should also be in the MainModelPart)
    #     CheckModelPart(self.model_part)
    #     CheckModelPart(self.model_part.GetSubModelPart(mesh_name))


if __name__ == '__main__':
    unittest.main()
