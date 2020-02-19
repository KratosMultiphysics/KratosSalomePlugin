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
from plugin.model_part import ModelPart
from plugin.geometries_io import GeometriesIO

# TODO probably makes sense to set it up in the same way as the ModelPart test, here with and without salome
# without Salome a Mock could do the Job of MeshInterface to have simple and small tests
# will also be a good excercise for using Mocks
class TestGeometriesIO(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
