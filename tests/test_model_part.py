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
from abc import ABCMeta, abstractmethod

# plugin imports
sys.path.append(os.pardir) # required to be able to do "from plugin import xxx"
import plugin.model_part as py_model_part

# other imports
try:
    import KratosMultiphysics as KM
    kratos_available = True
except:
    kratos_available = False


"""This set of tests makes sure that the python-version of the ModelPart
behaves in the same way as the real ModelPart
"""

class TestModelPart(object):
    class BaseTests(unittest.TestCase, metaclass=ABCMeta):
        @abstractmethod
        def _CreateModelPart(self, name):
            pass

        def setUp(self):
            self.model_part = self._CreateModelPart()

        def test_SubModelParts(self):
            self.assertFalse(self.model_part.IsSubModelPart())
            self.assertEqual(self.model_part.NumberOfSubModelParts(), 0)

            smp_1 = self.model_part.CreateSubModelPart("sub_1")
            self.assertEqual(smp_1.Name, self.model_part.GetSubModelPart("sub_1").Name)

            self.assertTrue(smp_1.IsSubModelPart())

            self.assertTrue(self.model_part.HasSubModelPart("sub_1"))
            self.assertFalse(self.model_part.HasSubModelPart("sub_2"))

            smp_2 = self.model_part.CreateSubModelPart("sub_2")
            self.assertTrue(smp_2.IsSubModelPart())
            self.assertTrue(self.model_part.HasSubModelPart("sub_2"))

            self.assertEqual(self.model_part.NumberOfSubModelParts(), 2)

            for smp in self.model_part.SubModelParts:
                self.assertEqual(type(smp), type(self.model_part))
                self.assertTrue(smp.Name.startswith("sub_"))

            with self.assertRaisesRegex(Exception, 'There is an already existing sub model part with name "sub_1" in model part: "for_test"'):
                self.model_part.CreateSubModelPart("sub_1")

        def test_SubSubModelParts(self):
            smp_1 = self.model_part.CreateSubModelPart("sub_1")
            ssub_1 = smp_1.CreateSubModelPart("ssub_1")
            ssub_2 = smp_1.CreateSubModelPart("ssub_2")

            self.assertEqual(smp_1.NumberOfSubModelParts(), 2)

            for smp in smp_1.SubModelParts:
                self.assertEqual(type(smp), type(self.model_part))
                self.assertTrue(smp.Name.startswith("ssub_"))

            self.assertEqual(self.model_part.Name, ssub_1.GetRootModelPart().Name)
            self.assertEqual(self.model_part.Name, ssub_2.GetRootModelPart().Name)
            self.assertEqual(smp_1.Name, ssub_1.GetParentModelPart().Name)
            self.assertEqual(smp_1.Name, ssub_2.GetParentModelPart().Name)

        def test_model_part_iterators(self):
            sub1 = self.model_part.CreateSubModelPart("sub1")
            sub2 = self.model_part.CreateSubModelPart("sub2")

            subsub1 = sub1.CreateSubModelPart("subsub1")

            names = set(["sub1","sub2"])

            counter = 0

            for subpart in self.model_part.SubModelParts:
                part_name = subpart.Name
                if part_name in names:
                    counter+=1

                if(subpart.Name == "sub1"):
                    for subsubpart in subpart.SubModelParts:
                        self.assertEqual(subsubpart.Name,"subsub1")
            self.assertEqual(counter, 2)

        def test_model_part_nodes(self):
            self.assertEqual(self.model_part.NumberOfNodes(), 0)

            self.model_part.CreateNewNode(1, 1.00,0.00,0.00)

            for node in self.model_part.Nodes:
                self.assertEqual(1, node.Id)

            self.assertEqual(self.model_part.NumberOfNodes(), 1)

            #trying to create a node with Id 1 and coordinates which are different from the ones of the existing node 1. Error
            with self.assertRaisesRegex(RuntimeError, "already exists in the root model part"):
                self.model_part.CreateNewNode(1, 0.00,0.00,0.00)

            #here i try to create a node with Id 1 but the coordinates coincide with the ones of the existing node. EXISTING NODE is returned and no error is thrown
            self.model_part.CreateNewNode(1, 1.00,0.00,0.00)
            self.assertEqual(self.model_part.NumberOfNodes(), 1)
            self.assertEqual(self.model_part.GetNode(1).Id, 1)
            self.assertAlmostEqual(self.model_part.GetNode(1).X, 1.00)

            self.assertEqual(len(self.model_part.Nodes), 1)

            self.model_part.CreateNewNode(2000, 2.00,0.00,0.00)

            for node_id, node in zip([1,2000], self.model_part.Nodes):
                self.assertEqual(node_id, node.Id) # this works bcs the container is ordered!

            self.assertEqual(self.model_part.NumberOfNodes(), 2)
            self.assertEqual(self.model_part.GetNode(1).Id, 1)
            self.assertEqual(self.model_part.GetNode(2000).Id, 2000)
            self.assertAlmostEqual(self.model_part.GetNode(2000).X, 2.00)

            self.model_part.CreateNewNode(2, 2.00,0.00,0.00)

            self.assertEqual(self.model_part.NumberOfNodes(), 3)
            self.assertEqual(self.model_part.GetNode(1).Id, 1)
            self.assertEqual(self.model_part.GetNode(2).Id, 2)
            self.assertAlmostEqual(self.model_part.GetNode(1).X, 1.00) #here the coordinates are still  the same as the original node
            self.assertAlmostEqual(self.model_part.GetNode(2).X, 2.00)

            self.assertEqual(self.model_part.NumberOfNodes(), 3)

            self.model_part.CreateSubModelPart("Inlets")
            self.model_part.CreateSubModelPart("Temp")
            self.model_part.CreateSubModelPart("Outlet")
            inlets_model_part = self.model_part.GetSubModelPart("Inlets")
            inlets_model_part.CreateNewNode(3, 3.00,0.00,0.00)

            self.assertEqual(inlets_model_part.NumberOfNodes(), 1)
            self.assertEqual(inlets_model_part.GetNode(3).Id, 3)
            self.assertAlmostEqual(inlets_model_part.GetNode(3).X, 3.00)
            self.assertEqual(self.model_part.NumberOfNodes(), 4)
            self.assertEqual(self.model_part.GetNode(3).Id, 3)
            self.assertAlmostEqual(self.model_part.GetNode(3).X, 3.00)

            inlets_model_part.CreateSubModelPart("Inlet1")
            inlets_model_part.CreateSubModelPart("Inlet2")
            inlet2_model_part = inlets_model_part.GetSubModelPart("Inlet2")
            inlet2_model_part.CreateNewNode(4, 4.00,0.00,0.00)

            self.assertEqual(inlet2_model_part.NumberOfNodes(), 1)
            self.assertEqual(inlet2_model_part.GetNode(4).Id, 4)
            self.assertAlmostEqual(inlet2_model_part.GetNode(4).X, 4.00)
            self.assertEqual(inlets_model_part.NumberOfNodes(), 2)
            self.assertEqual(inlets_model_part.GetNode(4).Id, 4)
            self.assertAlmostEqual(inlets_model_part.GetNode(4).X, 4.00)
            self.assertEqual(self.model_part.NumberOfNodes(), 5)
            self.assertEqual(self.model_part.GetNode(4).Id, 4)

            inlets_model_part.CreateNewNode(5, 5.00,0.00,0.00)
            inlets_model_part.CreateNewNode(6, 6.00,0.00,0.00)
            inlet2_model_part.CreateNewNode(7, 7.00,0.00,0.00)
            inlet2_model_part.CreateNewNode(8, 8.00,0.00,0.00)

            self.assertEqual(inlet2_model_part.NumberOfNodes(), 3)
            self.assertEqual(inlets_model_part.NumberOfNodes(), 6)
            self.assertEqual(self.model_part.NumberOfNodes(), 9)
            self.assertEqual(self.model_part.GetNode(4).Id, 4)

            self.model_part.CreateNewNode(15, 1.00,5.00,8.00)
            self.assertAlmostEqual(self.model_part.GetNode(15).X, 1.00)
            self.assertAlmostEqual(self.model_part.GetNode(15).Y, 5.00)
            self.assertAlmostEqual(self.model_part.GetNode(15).Z, 8.00)

        def test_model_part_elements(self):
            self.assertEqual(self.model_part.NumberOfElements(), 0)

            self.model_part.CreateNewProperties(1)
            self.model_part.CreateNewNode(1, 0.00,0.00,0.00)
            self.model_part.CreateNewNode(2, 1.00,0.00,0.00)
            self.model_part.CreateNewNode(3, 1.00,1.00,0.00)
            self.model_part.CreateNewElement("Element2D3N", 1, [1,2,3], self.model_part.Properties[1])

            for elem in self.model_part.Elements:
                self.assertEqual(1, elem.Id)

            self.assertEqual(self.model_part.NumberOfElements(), 1)

            #an error is thrown if i try to create an element with the same Id
            with self.assertRaisesRegex(RuntimeError, 'trying to construct an element with ID 1 however an element with the same Id already exists'):
                self.model_part.CreateNewElement("Element2D3N", 1, [1,2,3], self.model_part.Properties[1])

            self.assertEqual(self.model_part.NumberOfElements(), 1)
            self.assertEqual(self.model_part.GetElement(1).Id, 1)
            self.assertEqual(len(self.model_part.Elements), 1)

            self.model_part.CreateNewElement("Element2D3N", 2000, [1,2,3], self.model_part.Properties[1])

            for elem_id, elem in zip([1,2000], self.model_part.Elements):
                self.assertEqual(elem_id, elem.Id) # this works bcs the container is ordered!

            self.assertEqual(self.model_part.NumberOfElements(), 2)
            self.assertEqual(self.model_part.GetElement(1).Id, 1)
            self.assertEqual(self.model_part.GetElement(2000).Id, 2000)

            self.model_part.CreateNewElement("Element2D3N", 2, [1,2,3], self.model_part.Properties[1])

            self.assertEqual(self.model_part.NumberOfElements(), 3)
            self.assertEqual(self.model_part.GetElement(1).Id, 1)
            self.assertEqual(self.model_part.GetElement(2).Id, 2)

            self.assertEqual(self.model_part.NumberOfElements(), 3)

            self.model_part.CreateSubModelPart("Inlets")
            self.model_part.CreateSubModelPart("Temp")
            self.model_part.CreateSubModelPart("Outlet")
            inlets_model_part = self.model_part.GetSubModelPart("Inlets")
            inlets_model_part.CreateNewNode(4, 0.00,0.00,0.00)
            inlets_model_part.CreateNewNode(5, 1.00,0.00,0.00)
            inlets_model_part.CreateNewNode(6, 1.00,1.00,0.00)
            inlets_model_part.CreateNewElement("Element2D3N", 3, [4,5,6], self.model_part.Properties[1])

            self.assertEqual(inlets_model_part.NumberOfElements(), 1)
            self.assertEqual(inlets_model_part.GetElement(3).Id, 3)
            self.assertEqual(self.model_part.NumberOfElements(), 4)
            self.assertEqual(self.model_part.GetElement(3).Id, 3)

            inlets_model_part.CreateSubModelPart("Inlet1")
            inlets_model_part.CreateSubModelPart("Inlet2")
            inlet2_model_part = inlets_model_part.GetSubModelPart("Inlet2")
            inlet2_model_part.CreateNewNode(7, 0.00,0.00,0.00)
            inlet2_model_part.CreateNewNode(8, 1.00,0.00,0.00)
            inlet2_model_part.CreateNewNode(9, 1.00,1.00,0.00)
            inlet2_model_part.CreateNewElement("Element2D3N", 4, [7,8,9], self.model_part.Properties[1])

            self.assertEqual(inlet2_model_part.NumberOfElements(), 1)
            self.assertEqual(inlet2_model_part.GetElement(4).Id, 4)
            self.assertEqual(inlets_model_part.NumberOfElements(), 2)
            self.assertEqual(inlets_model_part.GetElement(4).Id, 4)
            self.assertEqual(self.model_part.NumberOfElements(), 5)
            self.assertEqual(self.model_part.GetElement(4).Id, 4)

            inlets_model_part.CreateNewElement("Element2D3N", 5, [7,8,9], self.model_part.Properties[1])
            inlets_model_part.CreateNewElement("Element2D3N", 6, [7,8,9], self.model_part.Properties[1])
            inlet2_model_part.CreateNewElement("Element2D3N", 7, [7,8,9], self.model_part.Properties[1])
            inlet2_model_part.CreateNewElement("Element2D3N", 8, [7,8,9], self.model_part.Properties[1])

            self.assertEqual(inlet2_model_part.NumberOfElements(), 3)
            self.assertEqual(inlets_model_part.NumberOfElements(), 6)
            self.assertEqual(self.model_part.NumberOfElements(), 9)
            self.assertEqual(self.model_part.GetElement(4).Id, 4)

        def test_model_part_conditions(self):
            self.assertEqual(self.model_part.NumberOfConditions(), 0)

            self.model_part.CreateNewProperties(1)
            self.model_part.CreateNewNode(1, 0.00,0.00,0.00)
            self.model_part.CreateNewNode(2, 1.00,0.00,0.00)
            self.model_part.CreateNewNode(3, 1.00,1.00,0.00)
            self.model_part.CreateNewCondition("SurfaceCondition3D3N", 1, [1,2,3], self.model_part.Properties[1])

            for cond in self.model_part.Conditions:
                self.assertEqual(1, cond.Id)

            self.assertEqual(self.model_part.NumberOfConditions(), 1)

            with self.assertRaisesRegex(RuntimeError, 'trying to construct a condition with ID 1 however a condition with the same Id already exists'):
                self.model_part.CreateNewCondition("SurfaceCondition3D3N", 1, [1,2,3], self.model_part.Properties[1])

            self.assertEqual(self.model_part.NumberOfConditions(), 1)
            self.assertEqual(self.model_part.GetCondition(1).Id, 1)
            self.assertEqual(len(self.model_part.Conditions), 1)

            self.model_part.CreateNewCondition("Condition2D", 2000, [2,3], self.model_part.Properties[1])

            for cond_id, cond in zip([1,2000], self.model_part.Conditions):
                self.assertEqual(cond_id, cond.Id) # this works bcs the container is ordered!

            self.assertEqual(self.model_part.NumberOfConditions(), 2)
            self.assertEqual(self.model_part.GetCondition(1).Id, 1)
            self.assertEqual(self.model_part.GetCondition(2000).Id, 2000)

            self.model_part.CreateNewCondition("SurfaceCondition3D3N", 2, [1,2,3], self.model_part.Properties[1])

            self.assertEqual(self.model_part.NumberOfConditions(), 3)
            self.assertEqual(self.model_part.GetCondition(1).Id, 1)
            self.assertEqual(self.model_part.GetCondition(2).Id, 2)

            self.assertEqual(self.model_part.NumberOfConditions(), 3)

            self.model_part.CreateSubModelPart("Inlets")
            self.model_part.CreateSubModelPart("Temp")
            self.model_part.CreateSubModelPart("Outlet")
            inlets_model_part = self.model_part.GetSubModelPart("Inlets")
            inlets_model_part.CreateNewNode(4, 0.00,0.00,0.00)
            inlets_model_part.CreateNewNode(5, 1.00,0.00,0.00)
            inlets_model_part.CreateNewNode(6, 1.00,1.00,0.00)
            inlets_model_part.CreateNewCondition("SurfaceCondition3D3N", 3, [4,5,6], self.model_part.Properties[1])

            self.assertEqual(inlets_model_part.NumberOfConditions(), 1)
            self.assertEqual(inlets_model_part.GetCondition(3).Id, 3)
            self.assertEqual(self.model_part.NumberOfConditions(), 4)
            self.assertEqual(self.model_part.GetCondition(3).Id, 3)

            inlets_model_part.CreateSubModelPart("Inlet1")
            inlets_model_part.CreateSubModelPart("Inlet2")
            inlet2_model_part = inlets_model_part.GetSubModelPart("Inlet2")
            inlet2_model_part.CreateNewNode(7, 0.00,0.00,0.00)
            inlet2_model_part.CreateNewNode(8, 1.00,0.00,0.00)
            inlet2_model_part.CreateNewNode(9, 1.00,1.00,0.00)
            inlet2_model_part.CreateNewCondition("SurfaceCondition3D3N", 4, [7,8,9], self.model_part.Properties[1])

            self.assertEqual(inlet2_model_part.NumberOfConditions(), 1)
            self.assertEqual(inlet2_model_part.GetCondition(4).Id, 4)
            self.assertEqual(inlets_model_part.NumberOfConditions(), 2)
            self.assertEqual(inlets_model_part.GetCondition(4).Id, 4)
            self.assertEqual(self.model_part.NumberOfConditions(), 5)
            self.assertEqual(self.model_part.GetCondition(4).Id, 4)

            inlets_model_part.CreateNewCondition("SurfaceCondition3D3N", 5, [7,8,9], self.model_part.Properties[1])
            inlets_model_part.CreateNewCondition("SurfaceCondition3D3N", 6, [7,8,9], self.model_part.Properties[1])
            inlet2_model_part.CreateNewCondition("SurfaceCondition3D3N", 7, [7,8,9], self.model_part.Properties[1])
            inlet2_model_part.CreateNewCondition("SurfaceCondition3D3N", 8, [7,8,9], self.model_part.Properties[1])

            self.assertEqual(inlet2_model_part.NumberOfConditions(), 3)
            self.assertEqual(inlets_model_part.NumberOfConditions(), 6)
            self.assertEqual(self.model_part.NumberOfConditions(), 9)
            self.assertEqual(self.model_part.GetCondition(4).Id, 4)

        def test_model_part_properties(self):
            self.assertEqual(self.model_part.NumberOfProperties(), 0)

            self.model_part.CreateNewProperties(1)

            self.assertEqual(self.model_part.NumberOfProperties(), 1)
            self.assertEqual(self.model_part.Properties[1].Id, 1)
            self.assertEqual(len(self.model_part.Properties), 1)

            self.model_part.CreateNewProperties(2000)

            self.assertEqual(self.model_part.NumberOfProperties(), 2)
            self.assertEqual(self.model_part.Properties[1].Id, 1)
            self.assertEqual(self.model_part.Properties[2000].Id, 2000)

            self.model_part.CreateNewProperties(2)

            with self.assertRaisesRegex(Exception, "Property #2 already existing"):
                self.model_part.CreateNewProperties(2)

            self.assertEqual(self.model_part.NumberOfProperties(), 3)
            self.assertEqual(self.model_part.Properties[1].Id, 1)
            self.assertEqual(self.model_part.Properties[2].Id, 2)

            self.assertEqual(self.model_part.NumberOfProperties(), 3)

            self.model_part.CreateSubModelPart("Inlets")
            self.model_part.CreateSubModelPart("Temp")
            self.model_part.CreateSubModelPart("Outlet")
            inlets_model_part = self.model_part.GetSubModelPart("Inlets")
            inlets_model_part.CreateNewProperties(3)

            self.assertEqual(inlets_model_part.NumberOfProperties(), 1)
            self.assertEqual(inlets_model_part.Properties[3].Id, 3)
            self.assertEqual(self.model_part.NumberOfProperties(), 4)
            self.assertEqual(self.model_part.Properties[3].Id, 3)

            inlets_model_part.CreateSubModelPart("Inlet1")
            inlets_model_part.CreateSubModelPart("Inlet2")
            inlet2_model_part = inlets_model_part.GetSubModelPart("Inlet2")
            inlet2_model_part.CreateNewProperties(4)

            self.assertEqual(inlet2_model_part.NumberOfProperties(), 1)
            self.assertEqual(inlet2_model_part.Properties[4].Id, 4)
            self.assertEqual(inlets_model_part.NumberOfProperties(), 2)
            self.assertEqual(inlets_model_part.Properties[4].Id, 4)
            self.assertEqual(self.model_part.NumberOfProperties(), 5)
            self.assertEqual(self.model_part.Properties[4].Id, 4)

            inlets_model_part.CreateNewProperties(5)
            inlets_model_part.CreateNewProperties(6)
            inlet2_model_part.CreateNewProperties(7)
            inlet2_model_part.CreateNewProperties(8)

            self.assertEqual(inlet2_model_part.NumberOfProperties(), 3)
            self.assertEqual(inlets_model_part.NumberOfProperties(), 6)
            self.assertEqual(self.model_part.NumberOfProperties(), 9)
            self.assertEqual(self.model_part.Properties[4].Id, 4)


@unittest.skipUnless(kratos_available, "Kratos not available")
class TestKratosModelPart(TestModelPart.BaseTests):
    def _CreateModelPart(self, name="for_test"):
        self.model = KM.Model()
        return self.model.CreateModelPart(name)

class TestPyKratosModelPart(TestModelPart.BaseTests):
    def _CreateModelPart(self, name="for_test"):
        return py_model_part.ModelPart(name)

    def test_properties_additional(self):
        with self.assertRaisesRegex(Exception, "Properties index not found: 212"):
            self.model_part.GetProperties(212)

    def test_Comparison(self):
        # make sure the comparison is working fine, since this is used in other tests
        self.skipTest("This test is not yet implemented!")


class TestDataValueContainer(object):
    '''Interface matches the one of Kratos
    However the tests cannot be executed with Kratos, since it requires the use of Variables
    '''
    class BaseTests(unittest.TestCase, metaclass=ABCMeta):
        '''wrapping in an extra class to avoid discovery of the base-test
        see https://stackoverflow.com/a/25695512
        '''
        maxDiff = None # to display all the diff
        @abstractmethod
        def _CreateDataValueContainer(self):
            pass

        def test_Has(self):
            dvc = self._CreateDataValueContainer()
            self.assertFalse(dvc.Has("abs"))
            self.assertFalse(dvc.Has("sthing"))

            dvc.SetValue("My_value", 15)
            self.assertTrue(dvc.Has("My_value"))

        def test_SetValue(self):
            dvc = self._CreateDataValueContainer()
            self.assertFalse(dvc.Has("Mx_value"))
            val = 15
            dvc.SetValue("Mx_value", val)
            self.assertTrue(dvc.Has("Mx_value"))

            self.assertEqual(dvc.GetValue("Mx_value"), val)

        def test_GetValue(self):
            dvc = self._CreateDataValueContainer()
            self.assertFalse(dvc.Has("Mz_value"))
            # this is different from Kratos, Kratos would silently allocate a non-existing variable!
            with self.assertRaisesRegex(KeyError, 'Variable "Mz_value" not found!'):
                dvc.GetValue("Mz_value")

            val = 15
            dvc.SetValue("Mz_value", val)
            self.assertTrue(dvc.Has("Mz_value"))

            self.assertEqual(dvc.GetValue("Mz_value"), val)

        def test_HasData(self):
            dvc = self._CreateDataValueContainer()

            self.assertFalse(dvc.HasData())
            dvc.SetValue("ff", 1.5)
            self.assertTrue(dvc.HasData())

        def test_GetData(self):
            dvc = self._CreateDataValueContainer()

            self.assertEqual({}, dvc.GetData())

            all_data = {
                "val_abc" : [1,3,6],
                "the_val2" : 15,
                "aassdd" : -193
            }
            for k,v in all_data.items():
                dvc.SetValue(k, v)

            self.assertDictEqual(all_data, dvc.GetData())

# The expected definitions are here to make the handling of the
# multiline-stings easier (no need to deal with indentation)
data_value_container_str = '''DataValueContainer
  aassdd : -193
  the_val2 : 15
  val_abc : [1, 3, 6]
'''

node_str = '''Node #1
  Coordinates: [1.0, 2.0, 3.0]
'''

node_with_data_str = '''Node #1
  Coordinates: [1.0, 2.0, 3.0]
  Nodal Data:
    DISP : -13.55
    VAL : 4.667
'''

geom_obj_str = '''GeometricalObject #1
  Name: myCondition
  Nodes:
    Node #1
      Coordinates: [1.0, 2.0, 3.0]
      Nodal Data:
        CvT : -13.55
    Node #2
      Coordinates: [11.0, -3.0, 5.0]
  Properties:
    Properties #1
      DENSITY : 7850
      YOUNGS_MOD : 5000000000.0
'''

geom_obj_with_data_str = '''GeometricalObject #1
  Name: myCondition
  Nodes:
    Node #1
      Coordinates: [1.0, 2.0, 3.0]
      Nodal Data:
        CvT : -13.55
    Node #2
      Coordinates: [11.0, -3.0, 5.0]
  Properties:
    Properties #1
      DENSITY : 7850
      YOUNGS_MOD : 5000000000.0
  GeometricalObject Data:
    DISP : -13.55
    VAL : 4.667
'''

props_str = '''Properties #1
  DISP : -13.55
  VAL : 4.667
'''

pointer_vector_set_str = '''PointerVectorSet:
  0 : 0
  1 : 1
  2 : 4
  3 : 9
  4 : 16
'''

pointer_vector_set_with_nodes_str = '''PointerVectorSet:
  1 : Node #1
  Coordinates: [0.5, -0.1, 0]

  2 : Node #2
  Coordinates: [1.5, 0.9, 1]

  3 : Node #3
  Coordinates: [2.5, 1.9, 4]

  4 : Node #4
  Coordinates: [3.5, 2.9, 9]

  5 : Node #5
  Coordinates: [4.5, 3.9, 16]

'''


class TestPyKratosDataValueContainer(TestDataValueContainer.BaseTests):
    def _CreateDataValueContainer(self):
        return py_model_part.DataValueContainer()

    def test_printing(self):
        dvc = self._CreateDataValueContainer()
        all_data = {
            "val_abc" : [1,3,6],
            "the_val2" : 15,
            "aassdd" : -193
        }
        for k,v in all_data.items():
            dvc.SetValue(k, v)

        self.assertMultiLineEqual(str(dvc), data_value_container_str)


class TestPyKratosNode(TestDataValueContainer.BaseTests):
    '''Node derives from DataValueContainer, hence also checking this interface
    '''
    def _CreateDataValueContainer(self):
        return py_model_part.Node(1, 1.0, 2.0, 3.0)

    def test_Node_basics(self):
        coords = [1.0, -99.41, 435.6]
        node_id = 56
        node = py_model_part.Node(node_id, coords[0], coords[1], coords[2])

        self.assertEqual(node_id, node.Id)

        self.assertAlmostEqual(coords[0], node.X)
        self.assertAlmostEqual(coords[1], node.Y)
        self.assertAlmostEqual(coords[2], node.Z)

        for i in range(3):
            self.assertAlmostEqual(coords[i], node.Coordinates()[i])

    def test_printing(self):
        node = self._CreateDataValueContainer()
        self.assertMultiLineEqual(str(node), node_str)

        node.SetValue("VAL", 4.667)
        node.SetValue("DISP", -13.55)
        self.assertMultiLineEqual(str(node), node_with_data_str)


class TestPyKratosGeometricalObject(TestDataValueContainer.BaseTests):
    '''GeometricalObject derives from DataValueContainer, hence also checking this interface
    '''
    def _CreateDataValueContainer(self):
        node_1 = py_model_part.Node(1, 1.0, 2.0, 3.0)
        node_1.SetValue("CvT", -13.55)
        node_2 = py_model_part.Node(2, 11.0, -3.0, 5.0)
        props = py_model_part.Properties(1)
        props.SetValue("YOUNGS_MOD", 5E9)
        props.SetValue("DENSITY", 7850)
        return py_model_part.GeometricalObject(1, [node_1, node_2], "myCondition", props)

    def test_GeometricalObject_basics(self):
        geom_obj_name = "myElement5"
        geom_obj_nodes = [1,3,77] # node Ids, serving as replacement for actual "Node"s
        geom_obj_id = 88
        geom_obj_props = py_model_part.Properties(2)

        geom_obj = py_model_part.GeometricalObject(geom_obj_id, geom_obj_nodes, geom_obj_name, geom_obj_props)

        self.assertEqual(geom_obj_id, geom_obj.Id)
        self.assertEqual(geom_obj_name, geom_obj.name)
        self.assertListEqual(geom_obj_nodes, geom_obj.nodes)
        self.assertEqual(geom_obj_props.Id, geom_obj.properties.Id)

    def test_printing(self):
        geom_obj = self._CreateDataValueContainer()
        self.assertMultiLineEqual(str(geom_obj), geom_obj_str)

        geom_obj.SetValue("VAL", 4.667)
        geom_obj.SetValue("DISP", -13.55)
        self.assertMultiLineEqual(str(geom_obj), geom_obj_with_data_str)


class TestPyKratosProperties(TestDataValueContainer.BaseTests):
    '''Properties derives from DataValueContainer, hence also checking this interface
    '''
    def _CreateDataValueContainer(self):
        return py_model_part.Properties(1)

    def test_Properties_basics(self):
        props_id = 369

        props = py_model_part.Properties(props_id)

        self.assertEqual(props_id, props.Id)

    def test_printing(self):
        props = self._CreateDataValueContainer()
        props.SetValue("VAL", 4.667)
        props.SetValue("DISP", -13.55)
        self.assertMultiLineEqual(str(props), props_str)


class TestPyKratosModelPartMissingMethods(TestDataValueContainer.BaseTests):
    '''ModelPart derives from DataValueContainer, hence also checking this interface
    '''
    def _CreateDataValueContainer(self):
        return py_model_part.ModelPart()

    def test_printing(self):
        model_part = self._CreateDataValueContainer()
        print(model_part)
        self.assertMultiLineEqual(str(model_part), model_part_str)

class TestPointerVectorSet(unittest.TestCase):
    def test_printing(self):
        pvs = py_model_part.ModelPart.PointerVectorSet()
        # adding some entities
        for i in range(5):
            pvs[i] = i**2

        self.assertMultiLineEqual(str(pvs), pointer_vector_set_str)

    def test_printing_with_nodes(self):
        pvs = py_model_part.ModelPart.PointerVectorSet()
        # adding some entities
        for i in range(5):
            pvs[i+1] = py_model_part.Node(i+1, i+0.5, i-0.1, i*i)

        self.assertMultiLineEqual(str(pvs), pointer_vector_set_with_nodes_str)


if __name__ == '__main__':
    unittest.main()
