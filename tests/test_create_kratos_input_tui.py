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
from ks_plugin.utilities.utils import IsExecutedInSalome

# tests imports
import testing_utilities

if IsExecutedInSalome():
    import create_kratos_input_tui
    from ks_plugin.utilities import salome_utilities


class TestSalomeMesh(testing_utilities.SalomeTestCaseWithBox):
    def test_mesh_identifier(self):
        mesh_identifier = salome_utilities.GetSalomeID(self.mesh_hexa.GetMesh())

        # this is not the real format, only a dummy for testing
        mesh_description= {
            "elements" : "abc",
            "conditions" : ["ddd"]
        }

        sal_mesh = create_kratos_input_tui.SalomeMesh(mesh_identifier, mesh_description, "my_model_part_name")

        self.assertEqual(sal_mesh.mesh_interface.mesh_identifier, mesh_identifier)
        self.assertDictEqual(sal_mesh.mesh_description, mesh_description)
        self.assertEqual(sal_mesh.model_part_name, "my_model_part_name")

    def test_mesh_proxy(self):
        mesh_identifier = salome_utilities.GetSalomeID(self.mesh_hexa.GetMesh())

        sal_mesh = create_kratos_input_tui.SalomeMesh(self.mesh_hexa.GetMesh(), {}, "sccffome_mp")

        self.assertEqual(sal_mesh.mesh_interface.mesh_identifier, mesh_identifier)
        self.assertEqual(sal_mesh.mesh_description, {})
        self.assertEqual(sal_mesh.model_part_name, "sccffome_mp")

    def test_sub_mesh_proxy(self):
        mesh_identifier = salome_utilities.GetSalomeID(self.sub_mesh_tetra_e_1)

        sal_mesh = create_kratos_input_tui.SalomeMesh(self.sub_mesh_tetra_e_1, {})

        self.assertEqual(sal_mesh.mesh_interface.mesh_identifier, mesh_identifier)
        self.assertEqual(sal_mesh.mesh_description, {})
        self.assertEqual(sal_mesh.model_part_name, "")

    def test_mesh_group(self):
        mesh_identifier = salome_utilities.GetSalomeID(self.group_tetra_0D_elements)

        sal_mesh = create_kratos_input_tui.SalomeMesh(self.group_tetra_0D_elements, {}, "htars.abc")

        self.assertEqual(sal_mesh.mesh_interface.mesh_identifier, mesh_identifier)
        self.assertEqual(sal_mesh.mesh_description, {})
        self.assertEqual(sal_mesh.model_part_name, "htars.abc")

    def test_mesh(self):
        mesh_identifier = salome_utilities.GetSalomeID(self.mesh_hexa.GetMesh())

        sal_mesh = create_kratos_input_tui.SalomeMesh(self.mesh_hexa, {}, "some_mp")

        self.assertEqual(sal_mesh.mesh_interface.mesh_identifier, mesh_identifier)
        self.assertEqual(sal_mesh.mesh_description, {})
        self.assertEqual(sal_mesh.model_part_name, "some_mp")

    def test_unpermitted_object(self):
        with self.assertRaisesRegex(Exception, 'Type of argument "salome_mesh" not permitted: '):
            create_kratos_input_tui.SalomeMesh(self.box, {})


class TestCreateModelPart(testing_utilities.SalomeTestCaseWithBox):
    def test_one_mesh(self):
        pass

    def test_multiple_meshes(self):
        pass


class TestCreateMdpaFile(testing_utilities.SalomeTestCaseWithBox):
    def test_one_mesh(self):
        pass

    def test_multiple_meshes(self):
        pass


if __name__ == '__main__':
    unittest.main()
