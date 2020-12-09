#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

"""
This file contains the MeshInterface
It interacts with the database of Salome to access the Mesh
"""

# python imports
import time
import logging
logger = logging.getLogger(__name__)

# plugin imports
from . import salome_utilities
from . import salome_mesh_utilities

# salome imports
import SMESH

smesh = salome_mesh_utilities.GetSmesh()


class MeshInterface:
    def __init__(self, mesh_identifier):
        self.mesh_identifier = mesh_identifier

    def GetNodes(self):
        if self.CheckMeshIsValid():
            start_time = time.time()
            current_mesh = salome_utilities.GetSalomeObject(self.mesh_identifier)

            if salome_mesh_utilities.IsSubMeshProxy(current_mesh):
                main_mesh = current_mesh.GetMesh()
                get_nodes_fct_ptr = lambda mesh : mesh.GetNodesId()

            elif salome_mesh_utilities.IsMeshGroup(current_mesh):
                main_mesh = current_mesh.GetMesh()
                get_nodes_fct_ptr = lambda mesh : mesh.GetNodeIDs()

            else: # MeshProxy
                main_mesh = current_mesh
                get_nodes_fct_ptr = lambda mesh : mesh.GetNodesId()

            nodes = {node_id : main_mesh.GetNodeXYZ(node_id) for node_id in sorted(get_nodes_fct_ptr(current_mesh))}
            logger.info('Getting {0} Nodes from Mesh "{1}" of type "{2}" took {3:.3} [s]'.format(len(nodes), self.GetMeshName(), self.GetMeshType(), time.time()-start_time))
            return nodes
        else:
            return {}

    def GetNodesAndGeometricalEntities(self, geometrical_entity_types=[]):
        # one function, since might be more efficient to get both at the same time if extracted through file
        # TODO maybe return all geometries if list is empty? => but how to get only the nodes then...?
        if self.CheckMeshIsValid():
            nodes = self.GetNodes() # nodes are always needed

            geometrical_entity_types_salome = [salome_mesh_utilities.EntityTypeFromString(entity) for entity in geometrical_entity_types if entity != "Node"] # nodes are treated separately

            if len(geometrical_entity_types_salome) == 0:
                return nodes, {}

            start_time = time.time()

            geom_entities = {}
            current_mesh = salome_utilities.GetSalomeObject(self.mesh_identifier)

            entity_types_in_mesh = self.GetEntityTypesInMesh()
            logged_entity_types_in_mesh = False
            for entity_type in geometrical_entity_types_salome:
                entity_type_str = salome_mesh_utilities.EntityTypeToString(entity_type)
                if entity_type in entity_types_in_mesh:

                    if salome_mesh_utilities.IsSubMeshProxy(current_mesh):
                        main_mesh = smesh.Mesh(current_mesh.GetFather())
                        sub_shape = current_mesh.GetSubShape()
                        c1 = smesh.GetCriterion(SMESH.ALL, SMESH.FT_EntityType, '=', entity_type, BinaryOp=SMESH.FT_LogicalAND)
                        c2 = smesh.GetCriterion(SMESH.ALL, SMESH.FT_BelongToGeom, sub_shape)
                        entities_filter = smesh.GetFilterFromCriteria([c1,c2])
                        entities_ids = main_mesh.GetIdsFromFilter(entities_filter)

                    elif salome_mesh_utilities.IsMeshGroup(current_mesh):
                        main_mesh = current_mesh.GetMesh()
                        entities_ids = current_mesh.GetListOfID()

                    else: # MeshProxy
                        entities_filter = smesh.GetFilter(SMESH.ALL, SMESH.FT_EntityType,'=', entity_type)
                        main_mesh = smesh.Mesh(current_mesh)
                        entities_ids = main_mesh.GetIdsFromFilter(entities_filter)

                    geom_entities[entity_type_str] = {ent_id : main_mesh.GetElemNodes(ent_id) for ent_id in sorted(entities_ids)}
                else:
                    geom_entities[entity_type_str] = {}

                    logger.warning('Entity type "{}" not in Mesh "{}"!'.format(salome_mesh_utilities.EntityTypeToString(entity_type), self.GetMeshName()))
                    if not logged_entity_types_in_mesh:
                        logged_entity_types_in_mesh = True
                        avail_entity_types_as_str = [salome_mesh_utilities.EntityTypeToString(e) for e in entity_types_in_mesh]
                        logger.info('The following entities are in this mesh: "{}"'.format('", "'.join(avail_entity_types_as_str)))

            logger.info('Getting {0} Geometrical Entities from Mesh "{1}" of type "{2}" took {3:.3f} [s]'.format(sum([len(ge) for ge in geom_entities.values()]), self.GetMeshName(), self.GetMeshType(), time.time()-start_time))

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
        if not salome_mesh_utilities.IsMeshProxy(salome_object) and not salome_mesh_utilities.IsSubMeshProxy(salome_object) and not salome_mesh_utilities.IsMeshGroup(salome_object):
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

    def GetMeshType(self):
        if self.CheckMeshIsValid():
            salome_object = salome_utilities.GetSalomeObject(self.mesh_identifier)
            if salome_mesh_utilities.IsSubMeshProxy(salome_object): return "SubMeshProxy"
            elif salome_mesh_utilities.IsMeshGroup(salome_object):  return "MeshGroup"
            else:                                                   return "MeshProxy"
        else:
            return ""

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

    @staticmethod
    def DoMeshesBelongToSameMainMesh(list_mesh_interfaces):
        """checks whether all meshes given a list of mesh interfaces belong to the same main mesh"""
        mesh_identifiers = []
        for mesh_interface in list_mesh_interfaces:
            if mesh_interface.CheckMeshIsValid():
                mesh_identifiers.append(mesh_interface.mesh_identifier)
            else:
                return False

        return salome_mesh_utilities.DoMeshesBelongToSameMainMesh(mesh_identifiers)
