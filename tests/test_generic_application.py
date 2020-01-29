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
import shutil

# plugin imports
sys.path.append(os.pardir) # required to be able to do "from plugin import xxx"
sys.path.append(os.path.join(os.pardir, "plugin")) # required that the imports from the "plugin" folder work inside the py-modules of the plugin
from plugin.applications.Generic.application import GenericApplication
from plugin.mesh_group import MeshGroup

class TestGenericApplication(unittest.TestCase):
    maxDiff = None

    def test_Serialize_empty(self):
        serialized_obj = {
            "mesh_identifiers"  : [],
            "mesh_descriptions" : {}
        }

        app = GenericApplication()
        self.assertDictEqual(serialized_obj, app.Serialize())

    def test_Serialize_MeshGroups(self):
        # sorting is required otherwise the order can be random and the test fails
        # order does only matter for the test
        mesh_identifiers = sorted(["1:9:10", "2:56", "1"])

        serialized_obj = {
            "mesh_identifiers"  : mesh_identifiers,
            "mesh_descriptions" : {}
        }

        app = GenericApplication()

        app.mesh_groups = {mesh_identifier : None for mesh_identifier in mesh_identifiers} # the actual MeshGroups are not used during the serialization, hence using None!

        serialized_app = app.Serialize()
        serialized_app["mesh_identifiers"] = sorted(serialized_app["mesh_identifiers"])
        self.assertDictEqual(serialized_obj, serialized_app)

    def test_Serialize_all(self):
        # sorting is required otherwise the order can be random and the test fails
        # order does only matter for the test
        mesh_identifiers = sorted(["1:9:10", "2:56", "1"])
        app = GenericApplication()

        app.mesh_groups = {mesh_identifier : MeshGroup(mesh_identifier) for mesh_identifier in mesh_identifiers} # using dummy mesh group for serialization of mesh-descriptions
        app.mesh_descriptions = {
            # the actual mesh-description does not matter, as it is serialized as whole dict, hence using dummy values
            "mesh_1"            : (app.mesh_groups["1:9:10"], {"some_key1" : "some_4val"}),
            "mesh_3"            : (app.mesh_groups["1"],      {"some_key2" : "some_3val", "other_key2" : "the_value"}),
            "the_sub_mesh"      : (app.mesh_groups["2:56"],   {"elements" : "some_v8al"}),
            "the_sub_mesh_cond" : (app.mesh_groups["2:56"],   {"conditions" : "some_v1al"}) # using the mesh-group multiple times!
        }

        serialized_obj = {
            "mesh_identifiers"  : mesh_identifiers,
            "mesh_descriptions" : {
                # the actual mesh-description does not matter, as it is serialized as whole dict, hence using dummy values
                "mesh_1"            : ["1:9:10", {"some_key1" : "some_4val"}],
                "mesh_3"            : ["1",      {"some_key2" : "some_3val", "other_key2" : "the_value"}],
                "the_sub_mesh"      : ["2:56",   {"elements" : "some_v8al"}],
                "the_sub_mesh_cond" : ["2:56",   {"conditions" : "some_v1al"}] # using the mesh-group multiple times!
            }
        }

        serialized_app = app.Serialize()
        serialized_app["mesh_identifiers"] = sorted(serialized_app["mesh_identifiers"])
        self.assertDictEqual(serialized_obj, serialized_app)

    def test_Deserialize_empty(self):
        serialized_obj = {
            "mesh_identifiers"  : [],
            "mesh_descriptions" : {}
        }

        app = GenericApplication()
        app.Deserialize(serialized_obj)

        self.assertEqual({}, app.mesh_groups)
        self.assertEqual({}, app.mesh_descriptions)

    def test_Deserialize_MeshGroups(self):
        serialized_obj = {
            "mesh_identifiers"  : ["1:9:10", "2:56", "1"],
            "mesh_descriptions" : {}
        }

        app = GenericApplication()
        app.Deserialize(serialized_obj)

        self.assertEqual(3, len(app.mesh_groups))
        self.assertListEqual(sorted(serialized_obj["mesh_identifiers"]), sorted(list(app.mesh_groups.keys())))
        for mesh_identifier, mesh_group in app.mesh_groups.items():
            self.assertEqual(mesh_identifier, mesh_group.mesh_identifier) # make sure the mesh-groups dict is correctly reconstructed

        self.assertEqual({}, app.mesh_descriptions)

    def test_Deserialize_all(self):
        serialized_obj = {
            "mesh_identifiers"  : ["1:9:10", "2:56", "1"],
            "mesh_descriptions" : {
                # the actual mesh-description does not matter, as it is serialized as whole dict, hence using dummy values
                "mesh_1"            : ["1:9:10", {"some_key1" : "some_4val"}],
                "mesh_3"            : ["1",      {"some_key2" : "some_3val", "other_key2" : "the_value"}],
                "the_sub_mesh"      : ["2:56",   {"elements" : "some_v8al"}],
                "the_sub_mesh_cond" : ["2:56",   {"conditions" : "some_v1al"}] # using the mesh-group multiple times!
            }
        }

        app = GenericApplication()
        app.Deserialize(serialized_obj)

        self.assertEqual(3, len(app.mesh_groups))
        self.assertListEqual(sorted(serialized_obj["mesh_identifiers"]), sorted(list(app.mesh_groups.keys())))
        for mesh_identifier, mesh_group in app.mesh_groups.items():
            self.assertEqual(mesh_identifier, mesh_group.mesh_identifier) # make sure the mesh-groups dict is correctly reconstructed

        self.assertEqual(4, len(app.mesh_descriptions))
        self.assertListEqual(sorted(list(serialized_obj["mesh_descriptions"].keys())), sorted(list(app.mesh_descriptions.keys())))
        for mesh_name in serialized_obj["mesh_descriptions"]:
            exp_res = serialized_obj["mesh_descriptions"][mesh_name]
            res = app.mesh_descriptions[mesh_name]
            self.assertEqual(exp_res[0], res[0].mesh_identifier)
            self.assertDictEqual(exp_res[1], res[1])

    def test_Serialize_Deserialize_empty(self):
        self.skipTest("This test is not yet implemented!")

    def test_Serialize_Deserialize_MeshGroups(self):
        self.skipTest("This test is not yet implemented!")

    def test_Serialize_Deserialize_all(self):
        self.skipTest("This test is not yet implemented!")

    def test_Deserialize_Serialize_empty(self):
        self.skipTest("This test is not yet implemented!")

    def test_Deserialize_Serialize_MeshGroups(self):
        self.skipTest("This test is not yet implemented!")

    def test_Deserialize_Serialize_all(self):
        self.skipTest("This test is not yet implemented!")


    def test_WriteCalculationFiles(self):
        self.skipTest("This test is not yet implemented!")


if __name__ == '__main__':
    unittest.main()
