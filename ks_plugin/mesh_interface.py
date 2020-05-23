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
from .utilities.utils import IsExecutedInSalome
# note that this file is used a lot in the tests without salome, hence the import of salome-dependencies is done in a special way
if IsExecutedInSalome():
    import SMESH
    from .utilities import salome_utilities
    smesh = salome_utilities.GetSmesh()

class MeshInterface(object):
    def __init__(self, mesh_identifier):
        self.mesh_identifier = mesh_identifier
        self.__observers = []

    def AddObserver(self, observer):
        self.UpdateObservers()
        self.__observers.append(weakref.ref(observer))

    def GetObsevers(self):
        self.UpdateObservers()
        return self.__observers

    def UpdateObservers(self):
        self.__observers = [o for o in self.__observers if o() is not None] # TODO check this!, not sure if it works like this!

    def GetNodes(self):
        if self.CheckMeshIsValid():
            start_time = time.time()
            current_mesh = salome_utilities.GetSalomeObject(self.mesh_identifier)

            if salome_utilities.IsSubMeshProxy(current_mesh):
                def GetNodes(mesh):
                    return mesh.GetNodesId()
                main_mesh = current_mesh.GetMesh()
                get_nodes_fct_ptr = GetNodes

            elif salome_utilities.IsMeshGroup(current_mesh):
                def GetNodes(mesh):
                    return mesh.GetNodeIDs()
                main_mesh = current_mesh.GetMesh()
                get_nodes_fct_ptr = GetNodes

            else: # main mesh
                def GetNodes(mesh):
                    return mesh.GetNodesId()
                main_mesh = current_mesh
                get_nodes_fct_ptr = GetNodes

            use lambdas for GetNodes

            nodes = {node_id : main_mesh.GetNodeXYZ(node_id) for node_id in get_nodes_fct_ptr(current_mesh)}
            logger.info('Getting {0} Nodes from Mesh "{1}" took {2:.2f} [s]'.format(len(nodes), self.GetMeshName(), time.time()-start_time))
            return nodes
        else:
            return {}

    def GetNodesAndGeometricalEntities(self, geometrical_entity_types=[]):
        # one function, since might be more efficient to get both at the same time if extracted through file
        # TODO maybe return all geometries if list is empty? => but how to get only the nodes then...?
        if self.CheckMeshIsValid():
            nodes = self.GetNodes() # nodes are always needed

            geometrical_entity_types_salome = [salome_utilities.GetEntityType(entity) for entity in geometrical_entity_types if entity != "Node"] # nodes are treated separately

            if len(geometrical_entity_types_salome) == 0:
                return nodes, {}

            start_time = time.time()

            geom_entities = {}
            current_mesh = salome_utilities.GetSalomeObject(self.mesh_identifier)

            entity_types_in_mesh = self.GetEntityTypesInMesh()
            for entity_type in geometrical_entity_types_salome:
                entity_type_str = str(entity_type)[7:]
                if entity_type in entity_types_in_mesh:

                    if salome_utilities.IsSubMeshProxy(current_mesh):
                        main_mesh = smesh.Mesh(current_mesh.GetFather())
                        sub_shape = current_mesh.GetSubShape()
                        c1 = smesh.GetCriterion(SMESH.ALL, SMESH.FT_EntityType, '=', entity_type, BinaryOp=SMESH.FT_LogicalAND)
                        c2 = smesh.GetCriterion(SMESH.ALL, SMESH.FT_BelongToGeom, sub_shape)
                        entities_filter = smesh.GetFilterFromCriteria([c1,c2])
                        entities_ids = main_mesh.GetIdsFromFilter(entities_filter)

                    elif salome_utilities.IsMeshGroup(current_mesh):
                        main_mesh = current_mesh.GetMesh()
                        entities_ids = current_mesh.GetListOfID()

                    else: # main mesh
                        entities_filter = smesh.GetFilter(SMESH.ALL, SMESH.FT_EntityType,'=', entity_type)
                        main_mesh = smesh.Mesh(current_mesh)
                        entities_ids = main_mesh.GetIdsFromFilter(entities_filter)

                    geom_entities[entity_type_str] = {ent_id : main_mesh.GetElemNodes(ent_id) for ent_id in entities_ids}
                else:
                    logger.warning('Entity type "{}" not in Mesh "{}"!'.format(str(entity_type)[7:], self.GetMeshName()))
                    geom_entities[entity_type_str] = {}

            logger.info('Getting {0} Geometrical Entities from Mesh "{1}" took {2:.2f} [s]'.format(sum([len(ge) for ge in geom_entities.values()]), self.GetMeshName(), time.time()-start_time))

            return nodes, geom_entities

        else:
            return {}, {}

    def GetEntityTypesInMesh(self):
        # Note: EntityTypes != GeometryTypes in Salome, see the documentation of SMESH
        if self.CheckMeshIsValid():
            mesh = salome_utilities.GetSalomeObject(self.mesh_identifier)
            return [e for e, v in smesh.GetMeshInfo(mesh).items() if v > 0]
        else:
            return []

    def GetMeshInformation(self):
        if self.CheckMeshIsValid():
            mesh = salome_utilities.GetSalomeObject(self.mesh_identifier)
            # TODO probably has to be converted to string
            return {e : v for e, v in smesh.GetMeshInfo(mesh).items() if v > 0}
        else:
            return {}

    def GetNumberOfNodes(self):
        raise NotImplementedError

    def GetNumberOfGeometries(self, geometry_type):
        # return -1 if the requested type is not available
        raise NotImplementedError

    def CheckMeshIsValid(self):
        # check if object exists
        if not salome_utilities.ObjectExists(self.mesh_identifier):
            logger.critical('Mesh with identifier "{}" in MeshInterface does not exist'.format(self.mesh_identifier))
            return False

        # if the object is a mesh
        salome_object = salome_utilities.GetSalomeObject(self.mesh_identifier)
        if not salome_utilities.IsMeshProxy(salome_object) and not salome_utilities.IsSubMeshProxy(salome_object) and not salome_utilities.IsMeshGroup(salome_object):
            obj_type = type(salome_object)
            obj_name = salome_utilities.GetObjectName(self.mesh_identifier)
            logger.critical('Object with identifier "{}" is not a mesh! Name: "{}" , Type: "{}"'.format(self.mesh_identifier, obj_name, obj_type))
            return False

        return True

    def GetMeshName(self):
        if self.CheckMeshIsValid():
            return salome_utilities.GetObjectName(self.mesh_identifier)
        else:
            return ""

    def __GetMesh(self):
        if self.CheckMeshIsValid():
            return salome_utilities.GetSalomeObject(self.mesh_identifier)
        else:
            return None


    def PrintInfo(self, prefix_string=""):
        return prefix_string + "MeshInterface\n"

    def PrintData(self, prefix_string=""):
        string_buf  = "{}  Mesh identifier: {}\n".format(prefix_string, self.mesh_identifier)
        mesh_is_valid = self.CheckMeshIsValid()
        string_buf += "{}  Mesh is valid: {}\n".format(prefix_string, mesh_is_valid)
        if mesh_is_valid:
            string_buf += "{}  Mesh has the following entities:\n".format(prefix_string)
            mesh = salome_utilities.GetSalomeObject(self.mesh_identifier)
            for e, v in smesh.GetMeshInfo(mesh).items():
                if v > 0:
                    string_buf += "{}    {}: {}\n".format(prefix_string, str(e)[7:], v)

        return string_buf

    def __str__(self):
        string_buf = self.PrintInfo()
        string_buf += self.PrintData()
        return string_buf

