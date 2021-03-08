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
This file contains functions for interacting with the Salome Mesh
NOTE: This file must NOT have dependencies on other files in the plugin!
(except salome_utilities)
"""

# python imports
from typing import List, Dict, Any

# plugin imports
from . import salome_utilities

# salome imports
import SMESH
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New()


def IsMesh(obj: Any) -> bool:
    """returns whether an object is a Mesh"""
    return isinstance(obj, smeshBuilder.Mesh)

def IsMeshProxy(obj: Any) -> bool:
    """returns whether an object is a MeshProxy"""
    return isinstance(obj, smeshBuilder.meshProxy)

def IsSubMeshProxy(obj: Any) -> bool:
    """returns whether an object is a SubMeshProxy"""
    return isinstance(obj, smeshBuilder.submeshProxy)

def IsMeshGroup(obj: Any) -> bool:
    """returns whether an object is a MeshGroup
    checking against "SMESH._objref_SMESH_GroupBase" includes the other three derived classes
    - "SMESH._objref_SMESH_Group"
    - "SMESH._objref_SMESH_GroupOnGeom"
    - "SMESH._objref_SMESH_GroupOnFilter"
    """
    return isinstance(obj, SMESH._objref_SMESH_GroupBase)

def IsAnyMesh(obj: Any) -> bool:
    """returns whether an object is any Mesh"""
    return any([IsMesh(obj), IsMeshProxy(obj), IsSubMeshProxy(obj), IsMeshGroup(obj)])

def DoMeshesBelongToSameMainMesh(list_mesh_identifiers: List[str]) -> bool:
    """checks whether all meshes given a list of mesh identifiers belong to the same main mesh
    Throws if an mesh identifier does not belong to a mesh
    """
    main_mesh_identifiers = []
    for mesh_identifier in list_mesh_identifiers:
        mesh_obj = salome_utilities.GetSalomeObject(mesh_identifier)
        if IsMeshProxy(mesh_obj):
            main_mesh_identifiers.append(mesh_identifier)
        elif IsSubMeshProxy(mesh_obj) or IsMeshGroup(mesh_obj):
            main_mesh_identifiers.append(salome_utilities.GetSalomeID(mesh_obj.GetMesh()))
        else:
            obj_type = type(mesh_obj)
            obj_name = salome_utilities.GetObjectName(mesh_identifier)
            raise Exception('Object with identifier "{}" is not a mesh! Name: "{}" , Type: "{}"'.format(mesh_identifier, obj_name, obj_type))

    return len(set(main_mesh_identifiers)) <= 1 # also works for empty input

def EntityTypeToString(entity_type: SMESH.EntityType) -> str:
    """converts an entity type to a string
    e.g. Entity_Triangle (type: SMESH.EntityType) to "Triangle"
    see https://docs.salome-platform.org/latest/gui/SMESH/smesh_module.html#entitytype
    """
    return str(entity_type)[7:]

def EntityTypeFromString(name_entity_type: str) -> SMESH.EntityType:
    """converts an entity type name to an entity type
    e.g. "Triangle" to Entity_Triangle (type: SMESH.EntityType)
    see https://docs.salome-platform.org/latest/gui/SMESH/smesh_module.html#entitytype
    """
    # Note: EntityTypes != GeometryTypes in Salome, see the documentation of SMESH
    entity_types_dict = {EntityTypeToString(entity_type) : entity_type for entity_type in SMESH.EntityType._items} # all entities available in salome
    if name_entity_type not in entity_types_dict:
        err_msg  = 'The requested entity type "{}" is not available!\n'.format(name_entity_type)
        err_msg += 'Only the following entity types are available:\n'
        for e_t in sorted(entity_types_dict.keys()):
            err_msg += '    {}\n'.format(e_t)
        raise Exception(err_msg)
    return entity_types_dict[name_entity_type]

def GetEntityTypesInMesh(mesh_obj) -> List[str]:
    return [EntityTypeToString(e) for e, v in smesh.GetMeshInfo(mesh_obj).items() if v > 0]

def GetMeshInformation(mesh_obj) -> Dict[str, int]:
    return {EntityTypeToString(e) : v for e, v in smesh.GetMeshInfo(mesh).items() if v > 0}

def MeshHasEntitiesOfType(mesh_obj, entity_type: str) -> bool:
    return entity_type in GetEntityTypesInMesh(mesh_obj)

def GetSmesh():
    return smesh
