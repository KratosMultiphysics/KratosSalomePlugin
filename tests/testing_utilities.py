#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher
#

# this file contains helpers used in the tests

# python imports
import unittest, sys, os

# plugin imports
from plugin.utilities import utils

# salome imports
if utils.IsExecutedInSalome():
    import salome
    import plugin.utilities.salome_utilities as salome_utils

def GetTestsDir():
    return os.path.dirname(os.path.realpath(__file__))

@unittest.skipUnless(utils.IsExecutedInSalome(), "This test can only be executed in Salome")
class SalomeTestCase(unittest.TestCase):
    # TODO the salome testcase class should have a fct to create a new study in setUp (not setUpClass) and close it in tearDown.
    # This is probably the fastest/best way to run tests inside the salome environment

    def setUp(self):
        salome.salome_init() # is this always needed or only once? Or maybe call it with a study as argument?
        # if salome_utils.GetVersion() ...
        salome.createNewStudy()
        # create geompy and smesh here? => are version dependent

    def tearDown(self):
        salome.myStudyManager.Close() # scope might be different in different versions of salome!
        # also what abt connecting / disconnecting to a study?
