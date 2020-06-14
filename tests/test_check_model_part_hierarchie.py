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
from abc import ABCMeta, abstractmethod

# plugin imports
import kratos_salome_plugin.model_part as py_model_part

# tests imports
from testing_utilities import CheckIfKratosAvailable, CheckModelPartHierarchie, ModelPartForTests

# Kratos import
kratos_available = CheckIfKratosAvailable()
if kratos_available:
    import KratosMultiphysics as KM


class TestCheckModelPartHierarchie(object):
    class BaseTests(unittest.TestCase, metaclass=ABCMeta):
        @abstractmethod
        def _CreateModelPart(self, name): pass

        def setUp(self):
            self.model_part = self._CreateModelPart()

        def test_check_main_model_part_name(self):
            name_main_mp = "some_funny_name"
            self.model_part = self._CreateModelPart(name_main_mp)

            hierarchie = {name_main_mp : {}}

            CheckModelPartHierarchie(self.model_part, hierarchie, self)

        def test_check_sub_model_part_name(self):
            name_main_mp = "some_funny_name"
            self.model_part = self._CreateModelPart(name_main_mp)
            self.model_part.CreateSubModelPart("smp_1")
            self.model_part.CreateSubModelPart("smp_jui")

            hierarchie = {name_main_mp : {
                "sub_model_parts" : {
                    "smp_1" : {},
                    "smp_jui" : {}
                }
            }}

            hierarchie_wrong = {name_main_mp : {
                "sub_model_parts" : {
                    "smp_www" : {},
                    "smp_jui" : {}
                }
            }}

            CheckModelPartHierarchie(self.model_part, hierarchie, self)

            with self.assertRaisesRegex(AssertionError, 'ModelPart "some_funny_name" does not have SubModelPart with name "smp_www"'):
                CheckModelPartHierarchie(self.model_part, hierarchie_wrong, self)

        def test_check_sub_sub_model_part_name(self):
            name_main_mp = "some_funny_name"
            self.model_part = self._CreateModelPart(name_main_mp)
            smp_1 = self.model_part.CreateSubModelPart("smp_1")
            smp_1.CreateSubModelPart("smp_xxx")
            smp_1.CreateSubModelPart("smp_yyy")
            self.model_part.CreateSubModelPart("smp_jui")

            hierarchie = {name_main_mp : {
                "sub_model_parts" : {
                    "smp_1" : {
                        "sub_model_parts" : {
                            "smp_xxx" : {},
                            "smp_yyy" : {}
                }},
                    "smp_jui" : {}
                }
            }}

            hierarchie_wrong = {name_main_mp : {
                "sub_model_parts" : {
                    "smp_1" : {
                        "sub_model_parts" : {
                            "smp_xxx" : {},
                            "smp_zzz" : {}
                }},
                    "smp_jui" : {}
                }
            }}

            CheckModelPartHierarchie(self.model_part, hierarchie, self)

            with self.assertRaisesRegex(AssertionError, 'ModelPart "some_funny_name.smp_1" does not have SubModelPart with name "smp_zzz"'):
                CheckModelPartHierarchie(self.model_part, hierarchie_wrong, self)

        def test_check_num_nodes(self):
            name_main_mp = "some_funny_name"
            self.model_part = self._CreateModelPart(name_main_mp)
            ModelPartForTests.CreateNodes(self.model_part)

            hierarchie = {name_main_mp : {
                    "nodes" : 8
            }}

            hierarchie_wrong = {name_main_mp : {
                    "nodes" : 5
            }}

            CheckModelPartHierarchie(self.model_part, hierarchie, self)

            with self.assertRaisesRegex(AssertionError, 'ModelPart "some_funny_name" is expected to have 5 nodes but has 8'):
                CheckModelPartHierarchie(self.model_part, hierarchie_wrong, self)

        def test_check_nodes_elements_props(self):
            name_main_mp = "some_funny_name"
            self.model_part = self._CreateModelPart(name_main_mp)
            ModelPartForTests.CreateNodesAndLineElements(self.model_part)

            hierarchie = {name_main_mp : {
                "nodes" : 6,
                "elements" : 10,
                "properties" : 2
            }}

            hierarchie_wrong_elems = {name_main_mp : {
                "nodes" : 6,
                "elements" : 5,
                "properties" : 2
            }}


            hierarchie_wrong_props = {name_main_mp : {
                "nodes" : 6,
                "elements" : 10,
                "properties" : 1
            }}

            CheckModelPartHierarchie(self.model_part, hierarchie, self)

            with self.assertRaisesRegex(AssertionError, 'ModelPart "some_funny_name" is expected to have 5 elements but has 10'):
                CheckModelPartHierarchie(self.model_part, hierarchie_wrong_elems, self)

            with self.assertRaisesRegex(AssertionError, 'ModelPart "some_funny_name" is expected to have 1 properties but has 2'):
                CheckModelPartHierarchie(self.model_part, hierarchie_wrong_props, self)

        def test_check_nodes_elements_props_in_smp(self):
            name_main_mp = "some_funny_name"
            self.model_part = self._CreateModelPart(name_main_mp)
            smp = self.model_part.CreateSubModelPart("entities")
            ModelPartForTests.CreateNodesAndLineElements(smp)

            hierarchie = {name_main_mp : {
                "nodes" : 6,
                "elements" : 10,
                "properties" : 2,
                "sub_model_parts" : {
                    "entities" : {
                        "nodes" : 6,
                        "elements" : 10,
                        "properties" : 2
                    }
                }
            }}

            hierarchie_wrong_elems = {name_main_mp : {
                "nodes" : 6,
                "elements" : 10,
                "properties" : 2,
                "sub_model_parts" : {
                    "entities" : {
                        "nodes" : 6,
                        "elements" : 5,
                        "properties" : 2
                    }
                }
            }}


            hierarchie_wrong_props = {name_main_mp : {
                "nodes" : 6,
                "elements" : 10,
                "properties" : 2,
                "sub_model_parts" : {
                    "entities" : {
                        "nodes" : 6,
                        "elements" : 10,
                        "properties" : 1
                    }
                }
            }}

            CheckModelPartHierarchie(self.model_part, hierarchie, self)

            with self.assertRaisesRegex(AssertionError, 'ModelPart "some_funny_name.entities" is expected to have 5 elements but has 10'):
                CheckModelPartHierarchie(self.model_part, hierarchie_wrong_elems, self)

            with self.assertRaisesRegex(AssertionError, 'ModelPart "some_funny_name.entities" is expected to have 1 properties but has 2'):
                CheckModelPartHierarchie(self.model_part, hierarchie_wrong_props, self)

        def test_check_nodes_conditions(self):
            name_main_mp = "some_funny_name"
            self.model_part = self._CreateModelPart(name_main_mp)
            ModelPartForTests.CreateNodesAndTriangleConditions(self.model_part)

            hierarchie = {name_main_mp : {
                "nodes" : 6,
                "conditions" : 17,
                "properties" : 2
            }}

            hierarchie_wrong = {name_main_mp : {
                "nodes" : 6,
                "conditions" : 5,
                "properties" : 2
            }}

            CheckModelPartHierarchie(self.model_part, hierarchie, self)

            with self.assertRaisesRegex(AssertionError, 'ModelPart "some_funny_name" is expected to have 5 conditions but has 17'):
                CheckModelPartHierarchie(self.model_part, hierarchie_wrong, self)


@unittest.skipUnless(kratos_available, "Kratos not available")
class TestKratosModelPart(TestCheckModelPartHierarchie.BaseTests):
    def _CreateModelPart(self, name="for_test"):
        self.model = KM.Model()
        return self.model.CreateModelPart(name)

class TestPyKratosModelPart(TestCheckModelPartHierarchie.BaseTests):
    def _CreateModelPart(self, name="for_test"):
        return py_model_part.ModelPart(name)



if __name__ == '__main__':
    unittest.main()
