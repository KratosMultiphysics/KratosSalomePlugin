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
    import SMESH
    from utilities import salome_utilities
    smesh = salome_utilities.GetSmesh()

class MeshGroup(object):
    def __init__(self, mesh_identifier):
        self.mesh_identifier = mesh_identifier
        self.__observers = []

        self.initial_mesh_name = "none" # might be needed in "MeshExists"
        if not self.MeshExists():
            raise Exception('Mesh with identifier "{}" does not exist!'.format(self.mesh_identifier))

        self.initial_mesh_name = self.GetMeshName()

        # TODO refactor that it only checks runtime (checks if object exists and is a mesh)
        if salome_utilities.IsMesh(salome_utilities.GetSalomeObject(self.mesh_identifier)):
            logger.debug('Mesh with identifier "{}" is a main Mesh'.format(self.mesh_identifier))
        elif salome_utilities.IsSubMesh(salome_utilities.GetSalomeObject(self.mesh_identifier)):
            logger.debug('Mesh with identifier "{}" is a sub Mesh'.format(self.mesh_identifier))
        else:
            obj_type = type(salome_utilities.GetSalomeObject(self.mesh_identifier))
            raise Exception('Object with identifier "{}" is not a mesh! Name: "{}" , Type: "{}"'.format(self.mesh_identifier, self.initial_mesh_name, obj_type))


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
            start_time = time.time()
            current_mesh = salome_utilities.GetSalomeObject(self.mesh_identifier)
            if salome_utilities.IsSubMesh(current_mesh):
                main_mesh = current_mesh.GetMesh()
            else:
                main_mesh = current_mesh

            nodes = {node_id : main_mesh.GetNodeXYZ(node_id) for node_id in current_mesh.GetNodesId()}
            print('Getting {0} Nodes from Mesh "{1}" took {2:.2f} [s]'.format(len(nodes), self.GetMeshName(), time.time()-start_time))
            logger.info('Getting {0} Nodes from Mesh "{1}" took {2:.2f} [s]'.format(len(nodes), self.GetMeshName(), time.time()-start_time))
            return nodes
        else:
            return {}

    def GetNodesAndGeometricalEntities(self, geometrical_entity_types=[]):
        # one function, since might be more efficient to get both at the same time if extracted through file
        if self.MeshExists():
            nodes = self.GetNodes()

            if SMESH.Entity_Node in geometrical_entity_types:
                geometrical_entity_types.remove(SMESH.Entity_Node)

            if len(geometrical_entity_types) == 0:
                return nodes, {}

            start_time = time.time()

            geom_entities = {}
            mesh_ref = salome_utilities.GetSalomeObject(self.mesh_identifier)

            entity_types_in_mesh = self.GetEntityTypesInMesh()
            for entity_type in geometrical_entity_types:
                if entity_type in entity_types_in_mesh:
                    if salome_utilities.IsSubMesh(mesh_ref):
                        main_mesh = smesh.Mesh(mesh_ref.GetFather())
                        sub_shape = mesh_ref.GetSubShape()
                        c1 = smesh.GetCriterion(SMESH.ALL, SMESH.FT_EntityType, '=', entity_type, BinaryOp=SMESH.FT_LogicalAND)
                        c2 = smesh.GetCriterion(SMESH.ALL, SMESH.FT_BelongToGeom, sub_shape)
                        entities_filter = smesh.GetFilterFromCriteria([c1,c2])
                    else:
                        entities_filter = smesh.GetFilter(SMESH.ALL, SMESH.FT_EntityType,'=', entity_type)
                        main_mesh = smesh.Mesh(mesh_ref)

                    entities_ids = main_mesh.GetIdsFromFilter(entities_filter)
                    geom_entities[entity_type] = {ent_id : main_mesh.GetElemNodes(ent_id) for ent_id in entities_ids}
                else:
                    logger.warning('Entity type "{}" not in Mesh "{}"!'.format(str(entity_type)[7:], self.GetMeshName()))
                    geom_entities[entity_type] = {}

            logger.info('Getting {0} Geometrical Entities from Mesh "{1}" took {2:.2f} [s]'.format(sum([len(ge) for ge in geom_entities.values()]), self.GetMeshName(), time.time()-start_time))

            return nodes, geom_entities

        else:
            return {}, {}

    def GetEntityTypesInMesh(self):
        if self.MeshExists():
            mesh = salome_utilities.GetSalomeObject(self.mesh_identifier)
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

