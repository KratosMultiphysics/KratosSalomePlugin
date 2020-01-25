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
        if (sys.version_info < (3, 2)):
            self.assertRaisesRegex = self.assertRaisesRegexp

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

    def test_Nodes(self):
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

    def test_Elements(self):
        self.skipTest("This test is not yet implemented!")

    def test_Conditions(self):
        self.skipTest("This test is not yet implemented!")

@unittest.skipUnless(kratos_available, "Kratos not available")
class TestKratosModelPart(TestModelPart, unittest.TestCase):
    def _CreateModelPart(self):
        self.model = KM.Model()
        return self.model.CreateModelPart("for_test")

class TestPyKratosModelPart(TestModelPart, unittest.TestCase):
    def _CreateModelPart(self):
        return PyModelPart("for_test")

    def test_Comparison(self):
        # make sure the comparison is working fine, since this is used in other tests
        self.skipTest("This test is not yet implemented!")

if __name__ == '__main__':
    unittest.main()
