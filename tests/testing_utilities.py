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
sys.path.append(os.pardir) # required to be able to do "from plugin import xxx"
from plugin.utilities import utils

if utils.IsExecutedInSalome():
    # imports that have dependenices on salome, hence can only be imported if executed in salome
    import salome
    import plugin.utilities.salome_utilities as salome_utils

    # initialize salome, should be done only once
    salome.salome_init()
    # initializing salome also creats a study. Closing it right away since tests create new study for each test. This is much faster than re-launching salome for each test
    salome.myStudyManager.Close(salome.myStudy)


def GetTestsDir():
    return os.path.dirname(os.path.realpath(__file__))


@unittest.skipUnless(utils.IsExecutedInSalome(), "This test can only be executed in Salome")
class SalomeTestCase(unittest.TestCase):

    def setUp(self):
        num_open_studies = len(salome.myStudyManager.GetOpenStudies())
        if num_open_studies != 0:
            raise Exception("{} open studies exist!".format(num_open_studies))

        salome.createNewStudy()

        open_studies = salome.myStudyManager.GetOpenStudies()
        num_open_studies = len(open_studies)
        if num_open_studies > 1:
            raise Exception("Too many open studies: {}".format(num_open_studies))

        self.my_study = salome.myStudyManager.GetStudyByName(open_studies[0])


    def tearDown(self):
        open_studies = salome.myStudyManager.GetOpenStudies()
        num_open_studies = len(open_studies)
        if num_open_studies > 1:
            raise Exception("Too many open studies: {}".format(num_open_studies))

        current_study = salome.myStudyManager.GetStudyByName(open_studies[0])

        salome.myStudyManager.Close(current_study)

        num_open_studies = len(salome.myStudyManager.GetOpenStudies())
        if num_open_studies != 0:
            raise Exception("{} open studies exist!".format(num_open_studies))
