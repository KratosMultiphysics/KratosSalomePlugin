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

# plugin imports
sys.path.append(os.pardir) # required to be able to do "from plugin import xxx"
from plugin.model_part import ModelPart as PyModelPart

# other imports
try:
    import KratosMultiphysics as KM
    kratos_available = True
except:
    kratos_available = False


class TestModelPart(object):
    """This set of tests makes sure that the python-version of the ModelPart
    behaves in the same way as the real ModelPart
    """

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
        smp_1.CreateSubModelPart("ssub_1")
        smp_1.CreateSubModelPart("ssub_2")

        self.assertEqual(smp_1.NumberOfSubModelParts(), 2)

        for smp in smp_1.SubModelParts:
            self.assertEqual(type(smp), type(self.model_part))
            self.assertTrue(smp.Name.startswith("ssub_"))

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
        self.assertEqual(self.model_part.NumberOfNodes(), 0)

        self.model_part.CreateNewNode(1, 1.00,0.00,0.00)

        self.assertEqual(self.model_part.NumberOfNodes(), 1)
        self.assertEqual(self.model_part.NumberOfNodes(), 1)

        #trying to create a node with Id 1 and coordinates which are different from the ones of the existing node 1. Error
        with self.assertRaises(RuntimeError):
            self.model_part.CreateNewNode(1, 0.00,0.00,0.00)

        #here i try to create a node with Id 1 but the coordinates coincide with the ones of the existing node. EXISTING NODE is returned and no error is thrown
        self.model_part.CreateNewNode(1, 1.00,0.00,0.00)
        self.assertEqual(self.model_part.NumberOfNodes(), 1)
        self.assertEqual(self.model_part.GetNode(1).Id, 1)
        self.assertAlmostEqual(self.model_part.GetNode(1).X, 1.00)

        self.assertEqual(len(self.model_part.Nodes), 1)

        self.model_part.CreateNewNode(2000, 2.00,0.00,0.00)

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

    # def test_add_node(self):
    #     sub1 = self.model_part.CreateSubModelPart("sub1")
    #     sub2 = self.model_part.CreateSubModelPart("sub2")

    #     model_part2 = self._CreateModelPart("Other")

    #     self.model_part.CreateNewNode(1,0.0,0.1,0.2)
    #     self.model_part.CreateNewNode(2,2.0,0.1,0.2)

    #     n1 = model_part2.CreateNewNode(1,1.0,1.1,0.2)
    #     n3 = model_part2.CreateNewNode(3,2.0,3.1,0.2)
    #     n4 = model_part2.CreateNewNode(4,2.0,3.1,10.2)

    #     #this should add node 3 to both sub1 and self.model_part, but not to sub2
    #     sub1.AddNode( n3, 0 )
    #     #self.assertTrue( n3.Id in sub1.Nodes )
    #     #self.assertTrue( n3.Id in self.model_part.Nodes )
    #     #self.assertFalse( n3.Id in sub2.Nodes )
    #     self.assertTrue( n3 in sub1.Nodes )
    #     self.assertTrue( n3 in self.model_part.Nodes )
    #     self.assertFalse( n3 in sub2.Nodes )


    #     ##next should throw an exception, since we try to add a node with Id1 which already exists
    #     with self.assertRaisesRegex(RuntimeError, "Error\: attempting to add pNewNode with Id \:1, unfortunately a \(different\) node with the same Id already exists\n"):
    #         sub2.AddNode( n1, 0 )

    #     #create two extra nodes in the model model_part2
    #     n5 = model_part2.CreateNewNode(5,2.0,3.1,0.2)
    #     n6 = model_part2.CreateNewNode(6,2.0,3.1,10.2)

    #     ### here we test adding a list of nodes at once
    #     #now add node 4 and 5 to the self.model_part by Id - here it fails since we did not yet add node 4
    #     with self.assertRaisesRegex(RuntimeError, "Error: while adding nodes to submodelpart, the node with Id 4 does not exist in the root model part"):
    #         sub1.AddNodes([4,5])

    #     self.model_part.AddNode( n4, 0 )
    #     self.model_part.AddNode( n5, 0 )

    #     sub1.AddNodes([4,5]) #now it works, since we already added the nodes
    #     self.assertTrue( n4.Id in sub1.Nodes )
    #     self.assertTrue( n5.Id in sub1.Nodes )
    #     self.assertFalse( n5.Id in sub2.Nodes )

    def test_model_part_elements(self):
        self.assertEqual(self.model_part.NumberOfElements(), 0)

        self.model_part.CreateNewNode(1, 0.00,0.00,0.00)
        self.model_part.CreateNewNode(2, 1.00,0.00,0.00)
        self.model_part.CreateNewNode(3, 1.00,1.00,0.00)
        self.model_part.CreateNewElement("Element2D3N", 1, [1,2,3], self.model_part.GetProperties()[1])

        self.assertEqual(self.model_part.NumberOfElements(), 1)

        #an error is thrown if i try to create an element with the same Id
        with self.assertRaises(RuntimeError):
            self.model_part.CreateNewElement("Element2D3N", 1, [1,2,3], self.model_part.GetProperties()[1])

        self.assertEqual(self.model_part.NumberOfElements(), 1)
        self.assertEqual(self.model_part.GetElement(1).Id, 1)
        self.assertEqual(len(self.model_part.Elements), 1)

        self.model_part.CreateNewElement("Element2D3N", 2000, [1,2,3], self.model_part.GetProperties()[1])

        self.assertEqual(self.model_part.NumberOfElements(), 2)
        self.assertEqual(self.model_part.GetElement(1).Id, 1)
        self.assertEqual(self.model_part.GetElement(2000).Id, 2000)

        self.model_part.CreateNewElement("Element2D3N", 2, [1,2,3], self.model_part.GetProperties()[1])

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
        inlets_model_part.CreateNewElement("Element2D3N", 3, [4,5,6], self.model_part.GetProperties()[1])

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
        inlet2_model_part.CreateNewElement("Element2D3N", 4, [7,8,9], self.model_part.GetProperties()[1])

        self.assertEqual(inlet2_model_part.NumberOfElements(), 1)
        self.assertEqual(inlet2_model_part.GetElement(4).Id, 4)
        self.assertEqual(inlets_model_part.NumberOfElements(), 2)
        self.assertEqual(inlets_model_part.GetElement(4).Id, 4)
        self.assertEqual(self.model_part.NumberOfElements(), 5)
        self.assertEqual(self.model_part.GetElement(4).Id, 4)

        inlets_model_part.CreateNewElement("Element2D3N", 5, [7,8,9], self.model_part.GetProperties()[1])
        inlets_model_part.CreateNewElement("Element2D3N", 6, [7,8,9], self.model_part.GetProperties()[1])
        inlet2_model_part.CreateNewElement("Element2D3N", 7, [7,8,9], self.model_part.GetProperties()[1])
        inlet2_model_part.CreateNewElement("Element2D3N", 8, [7,8,9], self.model_part.GetProperties()[1])

        self.assertEqual(inlet2_model_part.NumberOfElements(), 3)
        self.assertEqual(inlets_model_part.NumberOfElements(), 6)
        self.assertEqual(self.model_part.NumberOfElements(), 9)
        self.assertEqual(self.model_part.GetElement(4).Id, 4)

    def test_model_part_conditions(self):
        self.assertEqual(self.model_part.NumberOfConditions(), 0)

        self.model_part.CreateNewNode(1, 0.00,0.00,0.00)
        self.model_part.CreateNewNode(2, 1.00,0.00,0.00)
        self.model_part.CreateNewNode(3, 1.00,1.00,0.00)
        self.model_part.CreateNewCondition("SurfaceCondition3D3N", 1, [1,2,3], self.model_part.GetProperties()[1])

        self.assertEqual(self.model_part.NumberOfConditions(), 1)

        with self.assertRaises(RuntimeError):
            self.model_part.CreateNewCondition("SurfaceCondition3D3N", 1, [1,2,3], self.model_part.GetProperties()[1])

        self.assertEqual(self.model_part.NumberOfConditions(), 1)
        self.assertEqual(self.model_part.GetCondition(1).Id, 1)
        self.assertEqual(len(self.model_part.Conditions), 1)

        self.model_part.CreateNewCondition("Condition2D", 2000, [2,3], self.model_part.GetProperties()[1])

        self.assertEqual(self.model_part.NumberOfConditions(), 2)
        self.assertEqual(self.model_part.GetCondition(1).Id, 1)
        self.assertEqual(self.model_part.GetCondition(2000).Id, 2000)

        self.model_part.CreateNewCondition("SurfaceCondition3D3N", 2, [1,2,3], self.model_part.GetProperties()[1])

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
        inlets_model_part.CreateNewCondition("SurfaceCondition3D3N", 3, [4,5,6], self.model_part.GetProperties()[1])

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
        inlet2_model_part.CreateNewCondition("SurfaceCondition3D3N", 4, [7,8,9], self.model_part.GetProperties()[1])

        self.assertEqual(inlet2_model_part.NumberOfConditions(), 1)
        self.assertEqual(inlet2_model_part.GetCondition(4).Id, 4)
        self.assertEqual(inlets_model_part.NumberOfConditions(), 2)
        self.assertEqual(inlets_model_part.GetCondition(4).Id, 4)
        self.assertEqual(self.model_part.NumberOfConditions(), 5)
        self.assertEqual(self.model_part.GetCondition(4).Id, 4)

        inlets_model_part.CreateNewCondition("SurfaceCondition3D3N", 5, [7,8,9], self.model_part.GetProperties()[1])
        inlets_model_part.CreateNewCondition("SurfaceCondition3D3N", 6, [7,8,9], self.model_part.GetProperties()[1])
        inlet2_model_part.CreateNewCondition("SurfaceCondition3D3N", 7, [7,8,9], self.model_part.GetProperties()[1])
        inlet2_model_part.CreateNewCondition("SurfaceCondition3D3N", 8, [7,8,9], self.model_part.GetProperties()[1])

        self.assertEqual(inlet2_model_part.NumberOfConditions(), 3)
        self.assertEqual(inlets_model_part.NumberOfConditions(), 6)
        self.assertEqual(self.model_part.NumberOfConditions(), 9)
        self.assertEqual(self.model_part.GetCondition(4).Id, 4)

    def test_model_part_properties(self):
        current_model = KratosMultiphysics.Model()

        model_part= current_model.CreateModelPart("Main")

        self.assertEqual(model_part.NumberOfProperties(), 0)
        self.assertEqual(model_part.NumberOfProperties(0), 0)

        self.assertEqual(model_part.HasProperties(1), False)
        model_part.AddProperties(KratosMultiphysics.Properties(1))
        self.assertEqual(model_part.HasProperties(1), True)
        random_sub_model_part = model_part.CreateSubModelPart("RandomSubModelPart")
        self.assertEqual(random_sub_model_part.HasProperties(1), False)
        self.assertEqual(random_sub_model_part.RecursivelyHasProperties(1), True)

        self.assertEqual(model_part.NumberOfProperties(), 1)
        self.assertEqual(model_part.GetProperties()[1].Id, 1)
        self.assertEqual(model_part.GetProperties(0)[1].Id, 1)
        self.assertEqual(len(model_part.Properties), 1)

        model_part.AddProperties(KratosMultiphysics.Properties(2000))

        self.assertEqual(model_part.NumberOfProperties(), 2)
        self.assertEqual(model_part.GetProperties()[1].Id, 1)
        self.assertEqual(model_part.GetProperties()[2000].Id, 2000)

        model_part.AddProperties(KratosMultiphysics.Properties(2))

        self.assertEqual(model_part.NumberOfProperties(), 3)
        self.assertEqual(model_part.GetProperties()[1].Id, 1)
        self.assertEqual(model_part.GetProperties()[2].Id, 2)

        model_part.RemoveProperties(2000)

        self.assertEqual(model_part.NumberOfProperties(), 2)

        model_part.CreateSubModelPart("Inlets")
        model_part.CreateSubModelPart("Temp")
        model_part.CreateSubModelPart("Outlet")
        inlets_model_part = model_part.GetSubModelPart("Inlets")
        inlets_model_part.AddProperties(KratosMultiphysics.Properties(3))

        self.assertEqual(inlets_model_part.NumberOfProperties(), 1)
        self.assertEqual(inlets_model_part.GetProperties()[3].Id, 3)
        self.assertEqual(model_part.NumberOfProperties(), 3)
        self.assertEqual(model_part.GetProperties()[3].Id, 3)

        inlets_model_part.CreateSubModelPart("Inlet1")
        inlets_model_part.CreateSubModelPart("Inlet2")
        inlet2_model_part = inlets_model_part.GetSubModelPart("Inlet2")
        inlet2_model_part.AddProperties(KratosMultiphysics.Properties(4))

        self.assertEqual(inlet2_model_part.NumberOfProperties(), 1)
        self.assertEqual(inlet2_model_part.GetProperties()[4].Id, 4)
        self.assertEqual(inlets_model_part.NumberOfProperties(), 2)
        self.assertEqual(inlets_model_part.GetProperties()[4].Id, 4)
        self.assertEqual(model_part.NumberOfProperties(), 4)
        self.assertEqual(model_part.GetProperties()[4].Id, 4)

        inlets_model_part.AddProperties(KratosMultiphysics.Properties(5))
        inlets_model_part.AddProperties(KratosMultiphysics.Properties(6))
        inlet2_model_part.AddProperties(KratosMultiphysics.Properties(7))
        inlet2_model_part.AddProperties(KratosMultiphysics.Properties(8))

        self.assertEqual(inlet2_model_part.NumberOfProperties(), 3)
        self.assertEqual(inlets_model_part.NumberOfProperties(), 6)
        self.assertEqual(model_part.NumberOfProperties(), 8)
        self.assertEqual(model_part.GetProperties()[4].Id, 4)

        inlets_model_part.RemoveProperties(4)

        self.assertEqual(inlet2_model_part.NumberOfProperties(), 2)
        self.assertEqual(inlets_model_part.NumberOfProperties(), 5)
        self.assertEqual(model_part.NumberOfProperties(), 8) # the parent model part remains intact
        self.assertEqual(model_part.GetProperties()[4].Id, 4)

        inlets_model_part.RemovePropertiesFromAllLevels(4) # Remove from all levels will delete it from

        self.assertEqual(inlet2_model_part.NumberOfProperties(), 2)
        self.assertEqual(inlets_model_part.NumberOfProperties(), 5)
        self.assertEqual(model_part.NumberOfProperties(), 7)



@unittest.skipUnless(kratos_available, "Kratos not available")
class TestKratosModelPart(TestModelPart, unittest.TestCase):
    def _CreateModelPart(self, name="for_test"):
        self.model = KM.Model()
        return self.model.CreateModelPart(name)

class TestPyKratosModelPart(TestModelPart, unittest.TestCase):
    def _CreateModelPart(self, name="for_test"):
        return PyModelPart(name)

    def test_Comparison(self):
        # make sure the comparison is working fine, since this is used in other tests
        self.skipTest("This test is not yet implemented!")

if __name__ == '__main__':
    unittest.main()
