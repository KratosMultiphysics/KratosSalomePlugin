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
from kratos_salome_plugin import salome_utilities
from kratos_salome_plugin import salome_mesh_utilities

# tests imports
import testing_utilities

# salome imports
import salome
import GEOM
import SMESH


class TestSalomeMeshUtilities(testing_utilities.SalomeTestCaseWithBox):
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
            self.assertTrue(salome_mesh_utilities.IsMesh(mesh))

        for not_mesh in not_meshes:
            self.assertFalse(salome_mesh_utilities.IsMesh(not_mesh))


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
            self.assertTrue(salome_mesh_utilities.IsMeshProxy(mesh))

        for not_mesh in not_meshes:
            self.assertFalse(salome_mesh_utilities.IsMeshProxy(not_mesh))

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
            self.assertTrue(salome_mesh_utilities.IsSubMeshProxy(sub_mesh))

        for not_sub_mesh in not_sub_meshes:
            self.assertFalse(salome_mesh_utilities.IsSubMeshProxy(not_sub_mesh))

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
            self.assertTrue(salome_mesh_utilities.IsMeshGroup(mesh_group))

        for not_mesh_group in not_mesh_groups:
            self.assertFalse(salome_mesh_utilities.IsMeshGroup(not_mesh_group))

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
            self.assertTrue(salome_mesh_utilities.IsAnyMesh(mesh_group))

        for not_mesh_group in not_mesh_groups:
            self.assertFalse(salome_mesh_utilities.IsAnyMesh(not_mesh_group))

    def test_DoMeshesBelongToSameMainMesh(self):
        self.assertTrue(salome_mesh_utilities.DoMeshesBelongToSameMainMesh([])) # empty input should return True

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

        mesh_identifiers_same_main_mesh = [salome_utilities.GetSalomeID(mesh) for mesh in meshes_same_main_mesh]
        mesh_identifiers_not_same_main_mesh = [salome_utilities.GetSalomeID(mesh) for mesh in meshes_not_same_main_mesh]
        identifiers_not_meshes = [salome_utilities.GetSalomeID(mesh) for mesh in meshes_not_meshes]

        self.assertTrue(salome_mesh_utilities.DoMeshesBelongToSameMainMesh(mesh_identifiers_same_main_mesh))
        self.assertFalse(salome_mesh_utilities.DoMeshesBelongToSameMainMesh(mesh_identifiers_not_same_main_mesh))

        with self.assertRaisesRegex(Exception, 'Object with identifier "0:1:1:1" is not a mesh! Name: "main_box" , Type:'):
            salome_mesh_utilities.DoMeshesBelongToSameMainMesh(identifiers_not_meshes)

    def test_EntityTypeToString(self):
        self.assertEqual("Tetra", salome_mesh_utilities.EntityTypeToString(SMESH.Entity_Tetra))
        self.assertEqual("Quadrangle", salome_mesh_utilities.EntityTypeToString(SMESH.Entity_Quadrangle))

    def test_EntityTypeFromString(self):
        self.assertEqual(SMESH.Entity_Tetra, salome_mesh_utilities.EntityTypeFromString("Tetra"))
        self.assertEqual(SMESH.Entity_Quadrangle, salome_mesh_utilities.EntityTypeFromString("Quadrangle"))

        with self.assertRaisesRegex(Exception, 'The requested entity type "WeirdGeometry" is not available!\nOnly the following entity types are available:\n'):
            salome_mesh_utilities.EntityTypeFromString("WeirdGeometry")


if __name__ == '__main__':
    unittest.main()
