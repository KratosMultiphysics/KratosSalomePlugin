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
This file contains utility functions for interacting with Salome
it depends on salome and can only be imported if executed in Salome
NOTE: This file must NOT have dependencies on other files in the plugin!
"""

# python imports
import os
import logging
logger = logging.getLogger(__name__)

# salome imports
import salome
from salome.smesh import smeshBuilder
import salome_version
import SMESH

def GetVersionMajor():
    """returns the major version of Salome as int"""
    return salome_version.getVersions()[0]

def GetVersionMinor():
    """returns the minor version of Salome as int"""
    return salome_version.getVersions()[1]

def GetVersionPatch():
    """returns the patch version of Salome as int"""
    return salome_version.getVersions()[2]

def GetVersions():
    """returns the versions of the plugin as a list of integers
    e.g. [9,4,0]
    """
    return salome_version.getVersions()

def GetVersionString():
    """returns the versions of the plugin as a string with versions separated by "."
    e.g. "9.4.0"
    """
    return salome_version.getVersion()

def HasDesktop():
    """if Salome is executed with (aka GUI mode) or without Desktop (aka TUI mode)"""
    return salome.sg.hasDesktop()

def ExecutionMode():
    """mode in which Salome is executed, GUI or TUI"""
    return "GUI" if HasDesktop() else "TUI"

def GetSalomeObjectReference(object_identifier, log_if_not_existing=True):
    obj_ref = salome.myStudy.FindObjectID(object_identifier)

    if obj_ref is None and log_if_not_existing:
        logger.critical('The object with identifier "{}" does not exist!'.format(object_identifier))

    return obj_ref

def GetSalomeObject(object_identifier):
    return GetSalomeObjectReference(object_identifier).GetObject()

def GetObjectName(object_identifier):
    return GetSalomeObjectReference(object_identifier).GetName()

def ObjectExists(object_identifier):
    return (GetSalomeObjectReference(object_identifier, False) is not None)

def GetSalomeID(salome_object):
    return salome.ObjectToID(salome_object)

def IsMesh(obj):
    """returns whether an object is a Mesh"""
    return isinstance(obj, salome.smesh.smeshBuilder.Mesh)

def IsMeshProxy(obj):
    """returns whether an object is a MeshProxy"""
    return isinstance(obj, salome.smesh.smeshBuilder.meshProxy)

def IsSubMeshProxy(obj):
    """returns whether an object is a SubMeshProxy"""
    return isinstance(obj, salome.smesh.smeshBuilder.submeshProxy)

def IsMeshGroup(obj):
    """returns whether an object is a MeshGroup
    checking against "SMESH._objref_SMESH_GroupBase" includes the other three derived classes
    - "SMESH._objref_SMESH_Group"
    - "SMESH._objref_SMESH_GroupOnGeom"
    - "SMESH._objref_SMESH_GroupOnFilter"
    """
    return isinstance(obj, SMESH._objref_SMESH_GroupBase)

def IsAnyMesh(obj):
    """returns whether an object is any Mesh"""
    return any([IsMesh(obj), IsMeshProxy(obj), IsSubMeshProxy(obj), IsMeshGroup(obj)])

def DoMeshesBelongToSameMainMesh(list_mesh_identifiers):
    """checks whether all meshes given a list of mesh identifiers belong to the same main mesh
    Throws if an mesh identifier does not belong to a mesh
    """
    main_mesh_identifiers = []
    for mesh_identifier in list_mesh_identifiers:
        mesh_obj = GetSalomeObject(mesh_identifier)
        if IsMeshProxy(mesh_obj):
            main_mesh_identifiers.append(mesh_identifier)
        elif IsSubMeshProxy(mesh_obj) or IsMeshGroup(mesh_obj):
            main_mesh_identifiers.append(GetSalomeID(mesh_obj.GetMesh()))
        else:
            obj_type = type(mesh_obj)
            obj_name = GetObjectName(mesh_identifier)
            raise Exception('Object with identifier "{}" is not a mesh! Name: "{}" , Type: "{}"'.format(mesh_identifier, obj_name, obj_type))

    return len(set(main_mesh_identifiers)) <= 1 # also works for empty input

def EntityTypeToString(entity_type):
    """converts an entity type to a string
    e.g. Entity_Triangle (type: SMESH.EntityType) to "Triangle"
    see https://docs.salome-platform.org/latest/gui/SMESH/smesh_module.html#entitytype
    """
    return str(entity_type)[7:]

def EntityTypeFromString(name_entity_type):
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

def GetSmesh():
    return smeshBuilder.New()

def GetNumberOfObjectsInStudy():
    """Counts the number of objects in the study, for all components
    adapted from python script "salome_study" in KERNEL py-scripts
    """
    def GetNumberOfObjectsInComponent(SO):
        """Counts the number of objects in a component (e.g. GEOM, SMESH)"""
        num_objs_in_comp = 0
        it = salome.myStudy.NewChildIterator(SO)
        while it.More():
            CSO = it.Value()
            num_objs_in_comp += 1 + GetNumberOfObjectsInComponent(CSO)
            it.Next()
        return num_objs_in_comp

    # salome.myStudy.DumpStudy() # for debugging

    itcomp = salome.myStudy.NewComponentIterator()
    num_objs_in_study = 0
    while itcomp.More(): # loop components (e.g. GEOM, SMESH)
        SC = itcomp.Value()
        num_objs_in_study += 1 + GetNumberOfObjectsInComponent(SC)
        itcomp.Next()
    return num_objs_in_study

def StudyIsEmpty():
    return GetNumberOfObjectsInStudy() == 0

def IsStudyModified():
    """returns whether the study has unsaved modifications
    see https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html
    """
    return salome.myStudy.GetProperties().IsModified()

def SaveStudy(file_name):
    """saves the study as a single file, non-ascii
    returns whether saving the study was successful
    see https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html
    """
    if not file_name:
        raise NameError('"file_name" cannot be empty!')

    if not file_name.endswith(".hdf"):
        file_name += ".hdf"

    # create folder if necessary
    # required bcs otherwise Salome an crash if the folder to save the study in does not yet exist
    save_dir = os.path.split(file_name)[0]
    if not os.path.isdir(save_dir) and save_dir:
        os.makedirs(save_dir)

    save_successful = salome.myStudy.SaveAs(file_name, False, False) # args: use_multifile, use_acsii
    return save_successful

def OpenStudy(file_name):
    """opens a study
    returns whether opening the study was successful
    see https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html
    """
    if not file_name:
        raise NameError('"file_name" cannot be empty!')

    if not os.path.isfile(file_name):
        raise FileNotFoundError('File "{}" does not exist!'.format(file_name))

    if not file_name.endswith(".hdf"):
        logger.warning('Opening study from file without "*.hdf" extension: "{}"'.format(file_name))

    if IsStudyModified() and not StudyIsEmpty():
        logger.warning('Opening study when current study has unsaved changes')

    open_successful = salome.myStudy.Open(file_name)
    return open_successful

def ResetStudy():
    """resets the study, no objects are left afterwards
    see https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html
    """
    salome.myStudy.Clear()
    salome.myStudy.Init()
