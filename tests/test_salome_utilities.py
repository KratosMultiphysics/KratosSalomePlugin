#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher
#

# python imports
import unittest, sys, os

# plugin imports
sys.path.append(os.pardir)
from plugin.utilities import utils

@unittest.skipUnless(utils.IsExecutedInSalome(), "Tests can only be executed in Salome")
class TestSalomeUtilities(unittest.TestCase):

    def test_sth(self):
        pass