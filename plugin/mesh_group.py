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
import time
import logging
logger = logging.getLogger(__name__)
logger.debug('loading module')

# plugin imports
from utilities.utils import IsExecutedInSalome
# note that this file is used a lot in the tests without salome, hence the import of salome-dependencies is done in a special way
if IsExecutedInSalome():
    import salome
    from salome.smesh import smeshBuilder
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
        if self.MeshExists():
            current_mesh = salome_utilities.GetSalomeObject(self.mesh_identifier)
            if salome_utilities.IsSubMesh(current_mesh):
                main_mesh = current_mesh.GetMesh()
            else:
                main_mesh = current_mesh
            start_time = time.time()
            nodes = {node_id : main_mesh.GetNodeXYZ(node_id) for node_id in current_mesh.GetNodesId()}
            logger.info('Getting {0} Nodes from Mesh "{1}" took {2:.2f} [s]'.format(len(nodes), self.GetMeshName(), time.time()-start_time))
            return nodes
        else:
            return {}

    def GetNodesAndGeometricalEntities(self, geometrical_entity_types=[]):
        # one function, since might be more efficient to get both at the same time if extracted through file

        # TODO issue a warning if sth is requested that does not exist in the mesh?

        if self.MeshExists():
            nodes = self.GetNodes()

            if len(geometrical_entity_types) == 0:
                return nodes, {}


            raise NotImplementedError
            start_time = time.time()

            logger.info('Getting {0} Geometrical Entities from Mesh "{1}" took {2:.2f} [s]'.format(len(nodes), self.GetMeshName(), time.time()-start_time))
            return nodes, {}
        else:
            return {}, {}

    def GetEntityTypesInMesh(self):
        if self.MeshExists():
            mesh = salome_utilities.GetSalomeObject(self.mesh_identifier)
            fct_args = []
            if salome_utilities.GetVersionMajor() < 9:
                fct_args.append(salome.myStudyManager.GetStudyByName(salome.myStudyManager.GetOpenStudies()[0]))
            smesh = smeshBuilder.New(*fct_args)
            print(smesh.GetMeshInfo(mesh))

            etytes = {e : v for e, v in smesh.GetMeshInfo(mesh).items() if v > 0}

            import SMESH

            print(type(SMESH.Entity_Tetra))

            for e in etytes:
                print("COMPARE_TYPE:", type(SMESH.Entity_Tetra) == type(e))
                the_filter = smesh.GetFilter(SMESH.ALL, SMESH.FT_EntityType,'=', e)
                ids_tri = smesh.Mesh(mesh).GetIdsFromFilter(the_filter)
                print(len(ids_tri))

            print("NUM",len(SMESH.EntityType._items))

            for e in sorted(SMESH.EntityType._items):
                print(e)


            return [e for e, v in smesh.GetMeshInfo(mesh).items() if v > 0]
        else:
            return []

    def MeshExists(self):
        mesh_exists = salome_utilities.ObjectExists(self.mesh_identifier)
        if not mesh_exists:
            logger.critical('Mesh with identifier "{}" in MeshGroup with initial name "{}" does not exist'.format(self.mesh_identifier, self.initial_mesh_name))
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

