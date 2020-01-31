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
import shutil

# plugin imports
sys.path.append(os.pardir) # required to be able to do "from plugin import xxx"
sys.path.append(os.path.join(os.pardir, "plugin")) # required that the imports from the "plugin" folder work inside the py-modules of the plugin
from plugin.mesh_group import MeshGroup
from utilities.utils import IsExecutedInSalome

# tests imports
import testing_utilities
import time

if IsExecutedInSalome():
    from plugin.utilities import salome_utilities
    import salome


# from development.utilities import PrintObjectInfo

class TestMeshGroupObservers(unittest.TestCase):
    def test_observers(self):
        pass


class TestMeshGroupMeshRelatedMethods(testing_utilities.SalomeTestCaseWithBox):

    def test_GetNodes(self):
        pass
        # mesh_group = MeshGroup(salome.ObjectToID(self.sub_mesh_tetra_f_1))
        # PrintObjectInfo("self.study", self.study)
        # import salome_study
        # print(salome_study.DumpStudy())
        # print(self.mesh_tetra.GetID)


        # start_time = time.time()
        # print(len(mesh_group.GetNodes()))
        # print("TIME TO GET NODES:", time.time() - start_time)

    def __GetMainMeshID(self):
        if salome_utilities.GetVersionMajor() >= 9:
            # return salome.ObjectToID(self.Mesh_1)
            return "0:1:2:3" # hard-coded because getting the ID does not work with older versions for some reason
        else:
            return "0:1:2:3" # hard-coded because getting the ID does not work with older versions for some reason

if __name__ == '__main__':
    unittest.main()
