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

        smp_1 = self.model_part.CreateSubModelPart("sub_1")
        self.assertEqual(smp_1.Name, self.model_part.GetSubModelPart("sub_1").Name)

        self.assertTrue(smp_1.IsSubModelPart())

        self.assertTrue(self.model_part.HasSubModelPart("sub_1"))
        self.assertFalse(self.model_part.HasSubModelPart("sub_2"))

        smp_2 = self.model_part.CreateSubModelPart("sub_2")
        self.assertTrue(self.model_part.HasSubModelPart("sub_2"))

        self.assertEqual(self.model_part.NumberOfSubModelParts(), 2)

        for smp in self.model_part.SubModelParts:
            self.assertEqual(type(smp), type(self.model_part))
            self.assertTrue(smp.Name.startswith("sub_"))

        with self.assertRaisesRegex(Exception, 'There is an already existing sub model part with name "sub_1" in model part: "for_test"'):
            self.model_part.CreateSubModelPart("sub_1")

    def test_SubSubModelParts(self):
        smp_1 = self.model_part.CreateSubModelPart("sub_1")
        sub_smp_1 = smp_1.CreateSubModelPart("ssub_1")
        sub_smp_2 = smp_1.CreateSubModelPart("ssub_2")

        self.assertEqual(smp_1.NumberOfSubModelParts(), 2)

        for smp in smp_1.SubModelParts:
            self.assertEqual(type(smp), type(self.model_part))
            self.assertTrue(smp.Name.startswith("ssub_"))


    def test_Nodes(self):
        self.skipTest("This test is not yet implemented!")

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
