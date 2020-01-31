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
import weakref
import logging
logger = logging.getLogger(__name__)
logger.debug('loading module')

# plugin imports
from utilities.utils import IsExecutedInSalome
# note that this file is used a lot in the tests without salome, hence the import of salome-dependencies is done in a special way
if IsExecutedInSalome():
    from utilities import salome_utilities

class MeshGroup(object):
    def __init__(self, mesh_identifier):
        self.mesh_identifier = mesh_identifier
        self.__observers = []

        if not self.MeshExists():
            raise Exception('Mesh with identifier "{}" does not exist!'.format(self.mesh_identifier))

        self.initial_mesh_name = self.GetMeshName()

    def AddObserver(self, observer):
        self.UpdateObservers()
        self.__observers.append(weakref.ref(observer))

    def GetObsevers(self):
        self.UpdateObservers()
        return self.__observers

    def UpdateObservers(self):
        self.__observers = [o for o in self.__observers if o() is not None] # TODO check this!, not sure if it works like this!

    def GetNodes(self):
        # if self.MeshExists():
            mesh = salome_utilities.GetSalomeObject(self.mesh_identifier)
            return {node_id : mesh.GetNodeXYZ(node_id) for node_id in mesh.GetNodesId()}
        # else:
            # return {}

    def GetNodesAndGeometricalEntities(self, geometrical_entity_types):
        # TODO issue a warning if sth is requested that does not exist in the mesh?
        pass

    def GetEntityTypesInMesh(self):
        return []

    def MeshExists(self):
        mesh_exists = salome_utilities.ObjectExists(self.mesh_identifier)
        if not mesh_exists:
            logger.info('Mesh with identifier "{}" in MeshGroup does not exist'.format(self.mesh_identifier))
        return mesh_exists

    def GetMeshName(self):
        if self.MeshExists():
            return salome_utilities.GetObjectName(self.mesh_identifier)
        else:
            return ""

    def __GetMesh(self):
        if self.MeshExists():
            return salome_utilities.GetSalomeObject(self.mesh_identifier)
        else:
            return None

