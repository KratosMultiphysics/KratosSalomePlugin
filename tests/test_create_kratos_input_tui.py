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
from kratos_salome_plugin.utilities import IsExecutedInSalome

# tests imports
from testing_utilities import SalomeTestCaseWithBox, CompareMdpaWithReferenceFile

if IsExecutedInSalome():
    import create_kratos_input_tui
    from kratos_salome_plugin import salome_utilities


class TestSalomeMesh(SalomeTestCaseWithBox):
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


class TestCreateModelPart(SalomeTestCaseWithBox):
    def test_one_mesh(self):
        mesh_description_3D = { "elements" : {"Hexa" : {"MyFancyElement" : 0} } }

        meshes = [
            create_kratos_input_tui.SalomeMesh(self.mesh_hexa, mesh_description_3D, "domain")
        ]

        model_part = create_kratos_input_tui.CreateModelPart(meshes)

        self.assertEqual(model_part.NumberOfSubModelParts(), 1)
        self.assertEqual(model_part.NumberOfNodes(), 729)
        self.assertEqual(model_part.NumberOfElements(), 512)
        self.assertEqual(model_part.NumberOfConditions(), 0)
        self.assertEqual(model_part.NumberOfProperties(), 1)

        smp = model_part.GetSubModelPart("domain")
        self.assertEqual(smp.NumberOfSubModelParts(), 0)
        self.assertEqual(smp.NumberOfNodes(), 729)
        self.assertEqual(smp.NumberOfElements(), 512)
        self.assertEqual(smp.NumberOfConditions(), 0)
        self.assertEqual(smp.NumberOfProperties(), 1)

    def test_multiple_meshes(self):
        mesh_description_3D = {
            "elements" : {
                "Hexa" : {"MyFancyElement" : 1}
            },
            "conditions" : {
                "Hexa" : {"VolumeLoadCondition" : 0}
            }
        }
        mesh_description_1D = {
            "conditions" : {
                "Edge"   : {"LineSupportDisp" : 63, "LineSupportRot" : 7}
            }
        }
        mesh_description_0D = {
            "elements" : {
                "Ball"   : {"PointMassBall" : 4}
            }
        }

        meshes = [
            create_kratos_input_tui.SalomeMesh(self.mesh_hexa, mesh_description_3D, "domain"),
            create_kratos_input_tui.SalomeMesh(self.group_hexa_edges, mesh_description_1D, "supports"),
            create_kratos_input_tui.SalomeMesh(self.group_hexa_ball_elements, mesh_description_0D, "domain.point_masses")
        ]

        model_part = create_kratos_input_tui.CreateModelPart(meshes)

        self.assertEqual(model_part.NumberOfSubModelParts(), 2)
        self.assertEqual(model_part.NumberOfNodes(), 729)
        self.assertEqual(model_part.NumberOfElements(), 518)
        self.assertEqual(model_part.NumberOfConditions(), 704)
        self.assertEqual(model_part.NumberOfProperties(), 5)

        smp_domain = model_part.GetSubModelPart("domain")
        self.assertEqual(smp_domain.NumberOfNodes(), 729)
        self.assertEqual(smp_domain.NumberOfElements(), 518)
        self.assertEqual(smp_domain.NumberOfConditions(), 512)
        self.assertEqual(smp_domain.NumberOfSubModelParts(), 1)
        self.assertEqual(smp_domain.NumberOfProperties(), 3)

        smp_point_mass = smp_domain.GetSubModelPart("point_masses")
        self.assertEqual(smp_point_mass.NumberOfSubModelParts(), 0)
        self.assertEqual(smp_point_mass.NumberOfNodes(), 6)
        self.assertEqual(smp_point_mass.NumberOfElements(), 6)
        self.assertEqual(smp_point_mass.NumberOfConditions(), 0)
        self.assertEqual(smp_point_mass.NumberOfProperties(), 1)

        smp_supports = model_part.GetSubModelPart("supports")
        self.assertEqual(smp_supports.NumberOfSubModelParts(), 0)
        self.assertEqual(smp_supports.NumberOfNodes(), 92)
        self.assertEqual(smp_supports.NumberOfElements(), 0)
        self.assertEqual(smp_supports.NumberOfConditions(), 192)
        self.assertEqual(smp_supports.NumberOfProperties(), 2)


class TestCreateMdpaFile(SalomeTestCaseWithBox):
    def test_one_mesh(self):
        mesh_description_3D = { "elements" : {"Hexa" : {"MyFancyElement" : 0} } }

        meshes = [
            create_kratos_input_tui.SalomeMesh(self.mesh_hexa, mesh_description_3D, "domain")
        ]

        mdpa_file_name = "create_mdpa_one_mesh"
        create_kratos_input_tui.CreateMdpaFile(meshes, mdpa_file_name)

        CompareMdpaWithReferenceFile(mdpa_file_name, self)

    def test_multiple_meshes(self):
        mesh_description_3D = {
            "elements" : {
                "Hexa" : {"MyFancyElement" : 1}
            },
            "conditions" : {
                "Hexa" : {"VolumeLoadCondition" : 0}
            }
        }
        mesh_description_2D = {
            "conditions" : {
                "Quadrangle" : {"SideForce" : 23}
            }
        }
        mesh_description_1D = {
            "conditions" : {
                "Edge" : {"LineSupportDisp" : 63, "LineSupportRot" : 7}
            }
        }
        mesh_description_0D = {
            "elements" : {
                "Ball" : {"PointMassBall" : 4}
            }
        }

        meshes = [
            create_kratos_input_tui.SalomeMesh(self.mesh_hexa, mesh_description_3D, "domain"),
            create_kratos_input_tui.SalomeMesh(self.sub_mesh_hexa_f_1, mesh_description_2D, "side_faces"),
            create_kratos_input_tui.SalomeMesh(self.group_hexa_edges, mesh_description_1D, "supports"),
            create_kratos_input_tui.SalomeMesh(self.group_hexa_ball_elements, mesh_description_0D, "domain.point_masses")
        ]

        mdpa_file_name = "create_mdpa_multiple_meshes"
        create_kratos_input_tui.CreateMdpaFile(meshes, mdpa_file_name)

        CompareMdpaWithReferenceFile(mdpa_file_name, self)


if __name__ == '__main__':
    unittest.main()
