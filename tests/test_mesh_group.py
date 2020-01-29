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

def PrintObjectInfo(label, obj, print_python_methods=False):
    sys.stdout.flush()
    print('\nPrinting information for object "{}" of type: {}'.format(label, type(obj)))

    print('Methods:')
    methods = [m for m in dir(obj) if not m.startswith('__') and callable(getattr(obj,m))]
    for method in sorted(methods):
        print('\t' + str(method))

    print('\nAttributes:')
    attributes = [a for a in dir(obj) if not a.startswith('__') and not callable(getattr(obj,a))]
    for attribute in sorted(attributes):
        print('\t' + str(attribute))

    if print_python_methods:
        print('\nPYTHON Methods:')
        methods = [m for m in dir(obj) if m.startswith('__') and callable(getattr(obj,m))]
        for method in sorted(methods):
            print('\t' + str(method))

        print('\nPYTHON Attributes:')
        attributes = [a for a in dir(obj) if a.startswith('__') and not callable(getattr(obj,a))]
        for attribute in sorted(attributes):
            print('\t' + str(attribute))

    sys.stdout.flush()

class TestMeshGroupObservers(unittest.TestCase):
    def test_observers(self):
        pass


class TestMeshGroupMeshRelatedMethods(testing_utilities.SalomeTestCase):

    def setUp(self):
        super(TestMeshGroupMeshRelatedMethods, self).setUp()

        # create geometry
        O = self.geompy.MakeVertex(0, 0, 0)
        OX = self.geompy.MakeVectorDXDYDZ(1, 0, 0)
        OY = self.geompy.MakeVectorDXDYDZ(0, 1, 0)
        OZ = self.geompy.MakeVectorDXDYDZ(0, 0, 1)
        Box_1 = self.geompy.MakeBoxDXDYDZ(200, 200, 200)
        [Face_1] = self.geompy.SubShapes(Box_1, [13])

        self.geompy.addToStudy( O, 'O' )
        self.geompy.addToStudy( OX, 'OX' )
        self.geompy.addToStudy( OY, 'OY' )
        self.geompy.addToStudy( OZ, 'OZ' )
        self.geompy.addToStudy( Box_1, 'Box_1' )
        self.geompy.addToStudyInFather( Box_1, Face_1, 'Face_1' )
        # print(salome.ObjectToID(Box_1))

        # PrintObjectInfo("Box_1", Box_1)
        # PrintObjectInfo("salome", salome)
        # PrintObjectInfo("self.study", self.study)

        # create mesh
        from salome.smesh import smeshBuilder
        self.Mesh_1 = self.smesh.Mesh(Box_1)
        Regular_1D = self.Mesh_1.Segment()
        Max_Size_1 = Regular_1D.MaxSize(2)
        MEFISTO_2D = self.Mesh_1.Triangle(algo=smeshBuilder.MEFISTO)
        NETGEN_3D = self.Mesh_1.Tetrahedron()
        start_time = time.time()
        self.assertTrue(self.Mesh_1.Compute())
        print("TIME TO Compute Mesh:", time.time() - start_time)
        Sub_mesh_1 = self.Mesh_1.GetSubMesh( Face_1, 'Sub-mesh_1' )

        ## Set names of Mesh objects
        self.smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
        self.smesh.SetName(NETGEN_3D.GetAlgorithm(), 'NETGEN 3D')
        self.smesh.SetName(MEFISTO_2D.GetAlgorithm(), 'MEFISTO_2D')
        self.smesh.SetName(Max_Size_1, 'Max Size_1')
        self.smesh.SetName(self.Mesh_1.GetMesh(), 'Mesh_1')
        self.smesh.SetName(Sub_mesh_1, 'Sub-mesh_1')

        # print(dir(salome))
        # print(dir(self.Mesh_1))
        # PrintObjectInfo("self.Mesh_1", self.Mesh_1)
        # PrintObjectInfo("self.Mesh_1.GetMesh()", self.Mesh_1.GetMesh())
        # PrintObjectInfo("self.Mesh_1.mesh", self.Mesh_1.mesh)
        # PrintObjectInfo("self.smesh", self.smesh)

        # print(salome.ObjectToID(Sub_mesh_1))
        # print(salome.ObjectToID(self.smesh.Mesh(self.Mesh_1)))


    def test_GetNodes(self):
        mesh_group = MeshGroup(self.__GetMainMeshID())


        start_time = time.time()
        print(len(mesh_group.GetNodes()))
        print("TIME TO GET NODES:", time.time() - start_time)

    def __GetMainMeshID(self):
        if salome_utilities.GetVersionMajor() >= 9:
            # return salome.ObjectToID(self.Mesh_1)
            return "0:1:2:3" # hard-coded because getting the ID does not work with older versions for some reason
        else:
            return "0:1:2:3" # hard-coded because getting the ID does not work with older versions for some reason

if __name__ == '__main__':
    unittest.main()
