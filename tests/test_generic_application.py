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

# tests imports
import testing_utilities

class TestGenericApplicationWriteCalcFiles(unittest.TestCase):

    def setUp(self):
        self.folder_path = os.path.join(testing_utilities.GetTestsDir(), "dummy_testing_folder")
        if os.path.exists(self.folder_path):
            shutil.rmtree(self.folder_path) # clean leftovers in case they exist
        os.mkdir(self.folder_path)

    # def tearDown(self):
    #     shutil.rmtree(self.folder_path)

    def test_WriteCalculationFiles(self):
        app = GenericApplication()
        app.WriteCalculationFiles(self.folder_path)

        mdpa_file_name = os.path.join(self.folder_path, "case_name.mdpa")
        self.assertTrue(os.path.isfile(mdpa_file_name)) # TODO use real case name once supported

        self.assertEqual(1, len(os.listdir(self.folder_path))) # make sure only one file is written (the mdpa file). This can be different for other apps!

        ref_mdpa_file_name = os.path.join(testing_utilities.GetTestsDir(), "aux_test_files", "empty.mdpa")
        self.assertTrue(testing_utilities.CompareMdpaFiles(ref_mdpa_file_name, mdpa_file_name))


class TestGenericApplicationSerialize(unittest.TestCase):
    maxDiff = None # to display the entire comparison of "assertDictEqual"

    # global objects used in the tests
    serialized_obj_empty = {
        "mesh_identifiers"  : [],
        "mesh_descriptions" : {}
    }

    mesh_identifiers = sorted(["1:9:10", "2:56", "1"])

    serialized_obj_MeshGroups = {
        "mesh_identifiers"  : mesh_identifiers,
        "mesh_descriptions" : {}
    }

    serialized_obj_all = {
        "mesh_identifiers"  : mesh_identifiers,
        "mesh_descriptions" : {
            # the actual mesh-description does not matter, as it is serialized as whole dict, hence using dummy values
            "mesh_1"            : ["1:9:10", {"some_key1" : "some_4val"}],
            "mesh_3"            : ["1",      {"some_key2" : "some_3val", "other_key2" : "the_value"}],
            "the_sub_mesh"      : ["2:56",   {"elements" : "some_v8al"}],
            "the_sub_mesh_cond" : ["2:56",   {"conditions" : "some_v1al"}] # using the mesh-group multiple times!
        }
    }

    app_mesh_groups = {mesh_identifier : MeshGroup(mesh_identifier) for mesh_identifier in mesh_identifiers}

    app_mesh_descriptions = {
        # the actual mesh-description does not matter, as it is serialized as whole dict, hence using dummy values
        "mesh_1"            : (app_mesh_groups["1:9:10"], {"some_key1" : "some_4val"}),
        "mesh_3"            : (app_mesh_groups["1"],      {"some_key2" : "some_3val", "other_key2" : "the_value"}),
        "the_sub_mesh"      : (app_mesh_groups["2:56"],   {"elements" : "some_v8al"}),
        "the_sub_mesh_cond" : (app_mesh_groups["2:56"],   {"conditions" : "some_v1al"}) # using the mesh-group multiple times!
        }

    def test_Serialize_empty(self):
        self.__CheckSerialize({}, {}, TestGenericApplicationSerialize.serialized_obj_empty)

    def test_Serialize_MeshGroups(self):
        self.__CheckSerialize(TestGenericApplicationSerialize.app_mesh_groups, {}, TestGenericApplicationSerialize.serialized_obj_MeshGroups)

    def test_Serialize_all(self):
        self.__CheckSerialize(TestGenericApplicationSerialize.app_mesh_groups, TestGenericApplicationSerialize.app_mesh_descriptions, TestGenericApplicationSerialize.serialized_obj_all)

    def test_Deserialize_empty(self):
        self.__CheckDeserialize(TestGenericApplicationSerialize.serialized_obj_empty)

    def test_Deserialize_MeshGroups(self):
        self.__CheckDeserialize(TestGenericApplicationSerialize.serialized_obj_MeshGroups)

    def test_Deserialize_all(self):
        self.__CheckDeserialize(TestGenericApplicationSerialize.serialized_obj_all)

    def test_Serialize_Deserialize_empty(self):
        self.__CheckSerializeDeserialize({}, {}, TestGenericApplicationSerialize.serialized_obj_empty)

    def test_Serialize_Deserialize_MeshGroups(self):
        self.__CheckSerializeDeserialize(TestGenericApplicationSerialize.app_mesh_groups, {}, TestGenericApplicationSerialize.serialized_obj_MeshGroups)

    def test_Serialize_Deserialize_all(self):
        self.__CheckSerializeDeserialize(TestGenericApplicationSerialize.app_mesh_groups, TestGenericApplicationSerialize.app_mesh_descriptions, TestGenericApplicationSerialize.serialized_obj_all)

    # aux functions for tests
    def __CheckSerialize(self, app_mesh_groups, app_mesh_descriptions, serialized_obj):
        app = GenericApplication()

        # initialize app
        app.mesh_groups = app_mesh_groups
        app.mesh_descriptions = app_mesh_descriptions

        serialized_app = app.Serialize()

        # sorting is required otherwise the order can be random and the test fails
        # order does only matter for the test
        serialized_app["mesh_identifiers"] = sorted(serialized_app["mesh_identifiers"])
        self.assertDictEqual(serialized_obj, serialized_app)

    def __CheckDeserialize(self, serialized_obj):
        app = GenericApplication()
        app.Deserialize(serialized_obj)

        self.__CheckApp(app, serialized_obj)

    def __CheckSerializeDeserialize(self, app_mesh_groups, app_mesh_descriptions, serialized_obj):
        app = GenericApplication()

        # initialize app
        app.mesh_groups = app_mesh_groups
        app.mesh_descriptions = app_mesh_descriptions

        app2 = GenericApplication()
        app2.Deserialize(app.Serialize())

        self.__CheckApp(app, serialized_obj)

    def __CheckApp(self, app, serialized_obj):
        self.assertEqual(len(serialized_obj["mesh_identifiers"]), len(app.mesh_groups))
        self.assertListEqual(sorted(serialized_obj["mesh_identifiers"]), sorted(list(app.mesh_groups.keys())))
        for mesh_identifier, mesh_group in app.mesh_groups.items():
            self.assertEqual(mesh_identifier, mesh_group.mesh_identifier) # make sure the mesh-groups dict is correctly reconstructed

        self.assertEqual(len(serialized_obj["mesh_descriptions"]), len(app.mesh_descriptions))
        self.assertListEqual(sorted(list(serialized_obj["mesh_descriptions"].keys())), sorted(list(app.mesh_descriptions.keys())))
        for mesh_name in serialized_obj["mesh_descriptions"]:
            exp_res = serialized_obj["mesh_descriptions"][mesh_name]
            res = app.mesh_descriptions[mesh_name]
            self.assertEqual(exp_res[0], res[0].mesh_identifier)
            self.assertDictEqual(exp_res[1], res[1])


if __name__ == '__main__':
    unittest.main()
