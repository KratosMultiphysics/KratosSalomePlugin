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


def GetTestsDir():
    return os.path.dirname(os.path.realpath(__file__))


@unittest.skipUnless(utils.IsExecutedInSalome(), "This test can only be executed in Salome")
class SalomeTestCase(unittest.TestCase):

    def setUp(self):
        # initializing salome also creates a study.
        # closing and creating a new study (salome < 9) or clearing the study (salome >= 9)
        # in order to have a clean study for each test.
        # This is much faster than re-launching salome for each test
        # Note: The behavior is quite different between different versions of salome,
        # since from version 9 salome is single study, before multiple studies were possible!
        # This also requires different arguments for some functions

        if salome_utils.GetVersionMajor() < 9:
            self.__CloseOpenStudies()

            salome.createNewStudy()

            open_studies = salome.myStudyManager.GetOpenStudies()
            num_open_studies = len(open_studies)
            if num_open_studies != 1:
                raise Exception("Wrong number of open studies: {}".format(num_open_studies))

            self.study = salome.myStudyManager.GetStudyByName(open_studies[0])

        else:
            self.study = salome.myStudy
            self.study.Clear()
            # salome.salome_study_init()

    @classmethod
    def tearDownClass(cls):
        # make sure to clean leftovers, otherwise can cause errors at exit
        if salome_utils.GetVersionMajor() < 9:
            cls.__CloseOpenStudies()

    @classmethod
    def __CloseOpenStudies(cls):
        if salome_utils.GetVersionMajor() >= 9:
            raise Exception("This method can only be used with versions < 9!")

        for study_id in salome.myStudyManager.GetOpenStudies():
            salome.myStudyManager.Close(salome.myStudyManager.GetStudyByName(study_id))

        num_open_studies = len(salome.myStudyManager.GetOpenStudies())
        if num_open_studies != 0:
            raise Exception("{} open studies still exist!".format(num_open_studies))

