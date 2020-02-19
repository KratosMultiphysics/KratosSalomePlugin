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
            'GetNodes.return_value': the_nodes,
            'GetNodesAndGeometricalEntities.return_value': (the_nodes, {})
        }
        self.mesh_interface_mock.configure_mock(**attrs)

        mesh_name = "my_mesh"
        self.geom_io.AddMesh(mesh_name, self.mesh_interface_mock, mesh_description)

        self.assertTrue(self.model_part.HasSubModelPart(mesh_name)) # by default the mesh is added as a SubModelPart
        self.assertEqual(len(the_nodes), self.model_part.NumberOfNodes())
        for i_node, node in enumerate(self.model_part.Nodes):
            self.assertEqual(i_node+1, node.Id)
            self.assertAlmostEqual(i_node+1, node.X)
            self.assertAlmostEqual(i_node*2, node.Y)
            self.assertAlmostEqual(i_node+3.5, node.Z)

    def test_AddMesh_elements(self):
        raise NotImplementedError
        mesh_description = {} # only adding the nodes, but not creating any elements or conditions

        the_nodes = {i+1 : [i+1,i*2,i+3.5] for i in range(15)}

        attrs = {
            'GetNodes.return_value': the_nodes,
            'GetNodesAndGeometricalEntities.return_value': (the_nodes, {})
        }
        self.mesh_interface_mock.configure_mock(**attrs)
        self.geom_io.AddMesh("my_mesh", self.mesh_interface_mock, mesh_description)

        self.assertEqual(len(the_nodes), self.model_part.NumberOfNodes())
        for i_node, node in enumerate(self.model_part.Nodes):
            self.assertEqual(i_node+1, node.Id)
            self.assertAlmostEqual(i_node+1, node.X)
            self.assertAlmostEqual(i_node*2, node.Y)
            self.assertAlmostEqual(i_node+3.5, node.Z)


if __name__ == '__main__':
    unittest.main()
