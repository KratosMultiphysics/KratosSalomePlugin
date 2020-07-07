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
import os
import shutil
import unittest

# plugin imports
import kratos_salome_plugin.salome_utilities as salome_utils

# tests imports
import testing_utilities

# salome imports
import salome
import GEOM
import SMESH


class TestSalomeUtilities(testing_utilities.SalomeTestCaseWithBox):
    def test_IsMesh(self):
        meshes = [
            self.mesh_tetra
        ]

        not_meshes = [
            self.mesh_tetra.GetMesh(),
            self.sub_mesh_tetra_f_1,
            self.sub_mesh_tetra_g_1,
            self.box,
            self.face_1,
            self.group_faces,
            self.group_tetra_0D_elements,
            self.group_hexa_ball_elements,
            self.group_tetra_f1_nodes,
            self.group_tetra_f1_faces,
            self.group_hexa_edges
        ]

        for mesh in meshes:
            self.assertTrue(salome_utils.IsMesh(mesh))

        for not_mesh in not_meshes:
            self.assertFalse(salome_utils.IsMesh(not_mesh))


    def test_IsMeshProxy(self):
        meshes = [
            self.mesh_tetra.GetMesh()
        ]

        not_meshes = [
            self.mesh_tetra,
            self.sub_mesh_tetra_f_1,
            self.sub_mesh_tetra_g_1,
            self.box,
            self.face_1,
            self.group_faces,
            self.group_tetra_0D_elements,
            self.group_hexa_ball_elements,
            self.group_tetra_f1_nodes,
            self.group_tetra_f1_faces,
            self.group_hexa_edges
        ]

        for mesh in meshes:
            self.assertTrue(salome_utils.IsMeshProxy(mesh))

        for not_mesh in not_meshes:
            self.assertFalse(salome_utils.IsMeshProxy(not_mesh))

    def test_IsSubMeshProxy(self):
        sub_meshes = [
            self.sub_mesh_tetra_f_1,
            self.sub_mesh_tetra_g_1
        ]

        not_sub_meshes = [
            self.mesh_tetra,
            self.mesh_tetra.GetMesh(),
            self.box,
            self.face_1,
            self.group_faces,
            self.group_tetra_0D_elements,
            self.group_hexa_ball_elements,
            self.group_tetra_f1_nodes,
            self.group_tetra_f1_faces,
            self.group_hexa_edges
        ]

        for sub_mesh in sub_meshes:
            self.assertTrue(salome_utils.IsSubMeshProxy(sub_mesh))

        for not_sub_mesh in not_sub_meshes:
            self.assertFalse(salome_utils.IsSubMeshProxy(not_sub_mesh))

    def test_IsMeshGroup(self):
        mesh_groups = [
            self.group_tetra_0D_elements, # type "SMESH._objref_SMESH_Group"
            self.group_hexa_ball_elements, # type "SMESH._objref_SMESH_Group"
            self.group_tetra_f1_nodes, # type "SMESH._objref_SMESH_GroupOnGeom"
            self.group_tetra_f1_faces, # type "SMESH._objref_SMESH_GroupOnGeom"
            self.group_hexa_edges # "SMESH._objref_SMESH_GroupOnFilter"
        ]

        not_mesh_groups = [
            self.sub_mesh_tetra_f_1,
            self.sub_mesh_tetra_g_1,
            self.mesh_tetra,
            self.mesh_tetra.GetMesh(),
            self.box,
            self.face_1,
            self.group_faces
        ]

        for mesh_group in mesh_groups:
            self.assertTrue(salome_utils.IsMeshGroup(mesh_group))

        for not_mesh_group in not_mesh_groups:
            self.assertFalse(salome_utils.IsMeshGroup(not_mesh_group))

    def test_IsAnyMesh(self):
        mesh_groups = [
            self.group_tetra_0D_elements,
            self.group_hexa_ball_elements,
            self.group_tetra_f1_nodes,
            self.group_tetra_f1_faces,
            self.group_hexa_edges,
            self.sub_mesh_tetra_f_1,
            self.sub_mesh_tetra_g_1,
            self.mesh_tetra,
            self.mesh_tetra.GetMesh()
        ]

        not_mesh_groups = [
            self.box,
            self.face_1,
            self.group_faces
        ]

        for mesh_group in mesh_groups:
            self.assertTrue(salome_utils.IsAnyMesh(mesh_group))

        for not_mesh_group in not_mesh_groups:
            self.assertFalse(salome_utils.IsAnyMesh(not_mesh_group))

    def test_DoMeshesBelongToSameMainMesh(self):
        self.assertTrue(salome_utils.DoMeshesBelongToSameMainMesh([])) # empty input should return True

        meshes_same_main_mesh = [
            self.mesh_tetra.GetMesh(),
            self.sub_mesh_tetra_f_1,
            self.sub_mesh_tetra_g_1,
            self.sub_mesh_tetra_e_2,
            self.group_tetra_f1_faces,
            self.group_tetra_0D_elements
        ]

        meshes_not_same_main_mesh = [
            self.mesh_hexa.GetMesh(),
            self.sub_mesh_tetra_f_1,
            self.sub_mesh_tetra_g_1,
            self.sub_mesh_tetra_e_2,
            self.group_tetra_f1_faces,
            self.group_tetra_0D_elements
        ]

        meshes_not_meshes = [
            self.mesh_hexa.GetMesh(),
            self.box
        ]

        mesh_identifiers_same_main_mesh = [salome_utils.GetSalomeID(mesh) for mesh in meshes_same_main_mesh]
        mesh_identifiers_not_same_main_mesh = [salome_utils.GetSalomeID(mesh) for mesh in meshes_not_same_main_mesh]
        identifiers_not_meshes = [salome_utils.GetSalomeID(mesh) for mesh in meshes_not_meshes]

        self.assertTrue(salome_utils.DoMeshesBelongToSameMainMesh(mesh_identifiers_same_main_mesh))
        self.assertFalse(salome_utils.DoMeshesBelongToSameMainMesh(mesh_identifiers_not_same_main_mesh))

        with self.assertRaisesRegex(Exception, 'Object with identifier "0:1:1:1" is not a mesh! Name: "main_box" , Type:'):
            salome_utils.DoMeshesBelongToSameMainMesh(identifiers_not_meshes)

    def test_GetSalomeObject(self):
        object_id_list = [
            (salome.smesh.smeshBuilder.meshProxy, "0:1:2:3"),
            (salome.smesh.smeshBuilder.submeshProxy, "0:1:2:3:7:1"),
            (salome.smesh.smeshBuilder.submeshProxy, "0:1:2:3:10:1"),
            (GEOM._objref_GEOM_Object, "0:1:1:1"),
            (GEOM._objref_GEOM_Object, "0:1:1:1:1"),
            (GEOM._objref_GEOM_Object, "0:1:1:1:5")
        ]

        for obj_id in object_id_list:
            self.assertTrue(salome_utils.ObjectExists(obj_id[1]))
            self.assertEqual(obj_id[0], type(salome_utils.GetSalomeObject(obj_id[1])))

    def test_GetSalomeID(self):
        # this test might fail if salome orders the ids differently in different versions
        # it should not, since the order in which the objects are added is always the same
        object_id_list = [
            ("0:1:2:3", self.mesh_tetra.GetMesh()),
            ("0:1:2:3:7:1", self.sub_mesh_tetra_f_1),
            ("0:1:2:3:10:1", self.sub_mesh_tetra_g_1),
            ("0:1:1:1", self.box),
            ("0:1:1:1:1", self.face_1),
            ("0:1:1:1:5", self.group_faces)
        ]

        for obj_id in object_id_list:
            self.assertEqual(obj_id[0], salome_utils.GetSalomeID(obj_id[1]))

    def test_GetObjectName(self):
        identifier = salome_utils.GetSalomeID(self.box)
        self.assertEqual(salome_utils.GetObjectName(identifier), self.name_main_box)

        identifier = salome_utils.GetSalomeID(self.mesh_tetra.GetMesh())
        self.assertEqual(salome_utils.GetObjectName(identifier), self.name_main_mesh_tetra)

        identifier = salome_utils.GetSalomeID(self.sub_mesh_hexa_g_2)
        self.assertEqual(salome_utils.GetObjectName(identifier), self.name_mesh_group)

    def test_ObjectExists(self):
        identifier = salome_utils.GetSalomeID(self.box)
        self.assertTrue(salome_utils.ObjectExists(identifier))

        identifier = salome_utils.GetSalomeID(self.mesh_tetra.GetMesh())
        self.assertTrue(salome_utils.ObjectExists(identifier))

        identifier = salome_utils.GetSalomeID(self.sub_mesh_hexa_g_2)
        self.assertTrue(salome_utils.ObjectExists(identifier))

        self.assertFalse(salome_utils.ObjectExists("0:1:2:4:10:2:1:1:4:7:8")) # random identifier, should not exist
        self.assertFalse(salome_utils.ObjectExists("0:15555")) # random identifier, should not exist

    def test_EntityTypeToString(self):
        self.assertEqual("Tetra", salome_utils.EntityTypeToString(SMESH.Entity_Tetra))
        self.assertEqual("Quadrangle", salome_utils.EntityTypeToString(SMESH.Entity_Quadrangle))

    def test_EntityTypeFromString(self):
        self.assertEqual(SMESH.Entity_Tetra, salome_utils.EntityTypeFromString("Tetra"))
        self.assertEqual(SMESH.Entity_Quadrangle, salome_utils.EntityTypeFromString("Quadrangle"))

        with self.assertRaisesRegex(Exception, 'The requested entity type "WeirdGeometry" is not available!\nOnly the following entity types are available:\n'):
            salome_utils.EntityTypeFromString("WeirdGeometry")


if __name__ == '__main__':
    unittest.main()
