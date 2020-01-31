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

# salome imports
import salome
import salome_version

def GetVersionMajor():
    return int(salome_version.getVersionMajor())

def GetVersionMinor():
    return int(salome_version.getVersionMinor())

def GetVersion():
    return (GetVersionMajor(), GetVersionMinor())

def GetSalomeObject(object_identifier):
    if not isinstance(object_identifier, str):
        raise TypeError("Input is not a string!")
    return salome.IDToObject(object_identifier)

def GetSalomeObjectReference(object_identifier):
    if not isinstance(object_identifier, str):
        raise TypeError("Input is not a string!")
    global salome_pluginsmanager
    return salome_pluginsmanager.salome.myStudy.FindObjectID(object_identifier)

def GetObjectName(object_identifier):
    return GetSalomeObjectReference(object_identifier).GetName()

def ObjectExists(object_identifier):
    return (GetSalomeObject(object_identifier).GetObject() != None)

def IsMesh(obj):
    return isinstance(obj, salome.smesh.smeshBuilder.meshProxy)

def IsSubMesh(obj):
    return isinstance(obj, salome.smesh.smeshBuilder.submeshProxy)
