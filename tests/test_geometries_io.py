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

# plugin imports
sys.path.append(os.pardir) # required to be able to do "from plugin import xxx"
sys.path.append(os.path.join(os.pardir, "plugin")) # required that the imports from the "plugin" folder work inside the py-modules of the plugin
from plugin.model_part import ModelPart
from plugin.geometries_io import GeometriesIO
from plugin.mesh_interface import MeshInterface

# TODO probably makes sense to set it up in the same way as the ModelPart test, here with and without salome
# without Salome a Mock could do the Job of MeshInterface to have simple and small tests
# will also be a good excercise for using Mocks

class TestGeometriesIO(unittest.TestCase):
    """This TestCase contains basic tests for the GeometriesIO where the MeshInterface is substituted by a Mock object
    """
    def setUp(self):
        self.model_part = ModelPart()
        self.geom_io = GeometriesIO(self.model_part)
        self.mesh_interface_mock = MagicMock(spec=MeshInterface)

    def test_AddMesh_only_nodes(self):
        mesh_description = {} # only adding the nodes, but not creating any elements or conditions

        the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}

        attrs = {
            'GetNodesAndGeometricalEntities.return_value': (the_nodes, {})
        }
        self.mesh_interface_mock.configure_mock(**attrs)

        mesh_name = "my_mesh"
        self.geom_io.AddMesh(mesh_name, self.mesh_interface_mock, mesh_description)

        self.assertTrue(self.model_part.HasSubModelPart(mesh_name)) # by default the mesh is added as a SubModelPart

        def CheckModelPart(model_part_to_check):
            self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
            for i_node, node in enumerate(model_part_to_check.Nodes):
                self.assertEqual(i_node+1, node.Id)
                self.assertAlmostEqual(i_node+1, node.X)
                self.assertAlmostEqual(i_node*2, node.Y)
                self.assertAlmostEqual(i_node+3.5, node.Z)

        # both ModelParts have to have the nodes (the nodes are added to the SubModelPart hence they should also be in the MainModelPart)
        CheckModelPart(self.model_part)
        CheckModelPart(self.model_part.GetSubModelPart(mesh_name))

    def test_AddMesh_elements(self):
        mesh_description = {
            "elements" : {
                "Line" : ["SomeElement"]
            }
        }

        the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}
        the_geom_entities = {"Line" : {i+1 : [i+1, i+2] for i in range(14)}}

        attrs = {
            'GetNodesAndGeometricalEntities.return_value': (the_nodes, the_geom_entities)
        }
        self.mesh_interface_mock.configure_mock(**attrs)

        mesh_name = "my_mesh"
        self.geom_io.AddMesh(mesh_name, self.mesh_interface_mock, mesh_description)

        self.assertTrue(self.model_part.HasSubModelPart(mesh_name)) # by default the mesh is added as a SubModelPart

        def CheckModelPart(model_part_to_check):
            self.assertEqual(len(the_nodes), model_part_to_check.NumberOfNodes())
            for i_node, node in enumerate(model_part_to_check.Nodes):
                self.assertEqual(i_node+1, node.Id)
                self.assertAlmostEqual(i_node+1, node.X)
                self.assertAlmostEqual(i_node*2, node.Y)
                self.assertAlmostEqual(i_node+3.5, node.Z)

            self.assertEqual(len(the_geom_entities["Line"]), model_part_to_check.NumberOfElements())
            for i_elem, elem in enumerate(model_part_to_check.Elements):
                self.assertEqual(i_elem+1, elem.Id)
                for i_node, node in enumerate(elem.nodes):
                    self.assertEqual(i_elem+1+i_node, node.Id)

        # both ModelParts have to have the nodes (the entities are added to the SubModelPart hence they should also be in the MainModelPart)
        CheckModelPart(self.model_part)
        CheckModelPart(self.model_part.GetSubModelPart(mesh_name))


if __name__ == '__main__':
    unittest.main()
