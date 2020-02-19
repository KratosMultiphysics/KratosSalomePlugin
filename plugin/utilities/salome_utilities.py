#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# This file must NOT have dependencies on other files in the plugin!
# it contains utility functions for interacting with Salome
# it depends on salome and can only be imported, if executed in Salome

# python imports
import logging
logger = logging.getLogger(__name__)
logger.debug('loading module')

# salome imports
import salome
from salome.smesh import smeshBuilder
import salome_version
import SMESH

def GetVersionMajor() -> int:
    return int(salome_version.getVersionMajor())

def GetVersionMinor() -> int:
    return int(salome_version.getVersionMinor())

def GetVersion():
    return (GetVersionMajor(), GetVersionMinor())

def GetSalomeObjectReference(object_identifier: str, log_if_not_existing: bool=True):
    obj_ref = salome.myStudy.FindObjectID(object_identifier)

    if obj_ref is None and log_if_not_existing:
        logger.critical('The object with identifier "{}" does not exist!'.format(object_identifier))

    return obj_ref

def GetSalomeObject(object_identifier : str):
    return GetSalomeObjectReference(object_identifier).GetObject()

def GetObjectName(object_identifier : str) -> str:
    return GetSalomeObjectReference(object_identifier).GetName()

def ObjectExists(object_identifier : str) -> bool:
    return (GetSalomeObjectReference(object_identifier, False) is not None)

def GetSalomeID(salome_object) -> str:
    return salome.ObjectToID(salome_object)

def IsMesh(obj) -> bool:
    return isinstance(obj, salome.smesh.smeshBuilder.meshProxy)

def IsSubMesh(obj) -> bool:
    return isinstance(obj, salome.smesh.smeshBuilder.submeshProxy)

def IsMeshGroup(obj) -> bool:
    # checking against "SMESH._objref_SMESH_GroupBase" includes the other three derived classes
    # - "SMESH._objref_SMESH_Group"
    # - "SMESH._objref_SMESH_GroupOnGeom"
    # - "SMESH._objref_SMESH_GroupOnFilter"
    return isinstance(obj, SMESH._objref_SMESH_GroupBase)

def GetEntityType(name_entity_type : str):
    entity_types_dict = {str(entity_type)[7:] : entity_type for entity_type in SMESH.EntityType._items} # all entities avalable in salome
    return entity_types_dict[name_entity_type]

def GetSmesh():
    return smeshBuilder.New()
