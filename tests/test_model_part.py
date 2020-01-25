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
        pass
    def test_Nodes(self):
        pass
    def test_Elements(self):
        pass
    def test_Conditions(self):
        pass

@unittest.skipUnless(kratos_available, "Kratos not available")
class TestKratosModelPart(TestModelPart, unittest.TestCase):
    def _CreateModelPart(self):
        self.model = KM.Model()
        return self.model.CreateModelPart("for_test")

class TestPyKratosModelPart(TestModelPart, unittest.TestCase):
    def _CreateModelPart(self):
        return PyModelPart("dummy")

    def test_Comparison(self):
        # make sure the comparison is working fine, since this is used in other tests
        pass

if __name__ == '__main__':
    unittest.main()
