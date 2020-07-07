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

# tests imports
import testing_utilities

# salome imports
import salome
import GEOM
import SMESH


class TestSalomeUtilities(testing_utilities.SalomeTestCaseWithBox):
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
            self.assertTrue(salome_utilities.ObjectExists(obj_id[1]))
            self.assertEqual(obj_id[0], type(salome_utilities.GetSalomeObject(obj_id[1])))

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
            self.assertEqual(obj_id[0], salome_utilities.GetSalomeID(obj_id[1]))

    def test_GetObjectName(self):
        identifier = salome_utilities.GetSalomeID(self.box)
        self.assertEqual(salome_utilities.GetObjectName(identifier), self.name_main_box)

        identifier = salome_utilities.GetSalomeID(self.mesh_tetra.GetMesh())
        self.assertEqual(salome_utilities.GetObjectName(identifier), self.name_main_mesh_tetra)

        identifier = salome_utilities.GetSalomeID(self.sub_mesh_hexa_g_2)
        self.assertEqual(salome_utilities.GetObjectName(identifier), self.name_mesh_group)

    def test_ObjectExists(self):
        identifier = salome_utilities.GetSalomeID(self.box)
        self.assertTrue(salome_utilities.ObjectExists(identifier))

        identifier = salome_utilities.GetSalomeID(self.mesh_tetra.GetMesh())
        self.assertTrue(salome_utilities.ObjectExists(identifier))

        identifier = salome_utilities.GetSalomeID(self.sub_mesh_hexa_g_2)
        self.assertTrue(salome_utilities.ObjectExists(identifier))

        self.assertFalse(salome_utilities.ObjectExists("0:1:2:4:10:2:1:1:4:7:8")) # random identifier, should not exist
        self.assertFalse(salome_utilities.ObjectExists("0:15555")) # random identifier, should not exist


if __name__ == '__main__':
    unittest.main()
