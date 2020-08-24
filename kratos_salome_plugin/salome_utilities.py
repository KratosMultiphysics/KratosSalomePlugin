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
NOTE: This file must NOT have dependencies on other files in the plugin!
"""

# python imports
from typing import List
import logging
logger = logging.getLogger(__name__)

# salome imports
import salome
import salome_version
import SalomePyQt
sgPyQt = SalomePyQt.SalomePyQt()

def GetVersionMajor() -> int:
    """returns the major version of Salome as int"""
    return salome_version.getVersions()[0]

def GetVersionMinor() -> int:
    """returns the minor version of Salome as int"""
    return salome_version.getVersions()[1]

def GetVersionPatch() -> int:
    """returns the patch version of Salome as int"""
    return salome_version.getVersions()[2]

def GetVersions() -> List[int]:
    """returns the versions of the plugin as a list of integers
    e.g. [9,4,0]
    """
    return salome_version.getVersions()

def GetVersionString() -> str:
    """returns the versions of the plugin as a string with versions separated by "."
    e.g. "9.4.0"
    """
    return salome_version.getVersion()

def HasDesktop() -> bool:
    """if Salome is executed with (aka GUI mode) or without Desktop (aka TUI mode)"""
    return salome.sg.hasDesktop()

def ExecutionMode() -> str:
    """mode in which Salome is executed, GUI or TUI"""
    return "GUI" if HasDesktop() else "TUI"

def GetSalomeObjectReference(object_identifier: str, log_if_not_existing: bool=True):
    obj_ref = salome.myStudy.FindObjectID(object_identifier)

    if obj_ref is None and log_if_not_existing:
        logger.critical('The object with identifier "{}" does not exist!'.format(object_identifier))

    return obj_ref

def GetSalomeObject(object_identifier: str):
    return GetSalomeObjectReference(object_identifier).GetObject()

def GetObjectName(object_identifier: str) -> str:
    return GetSalomeObjectReference(object_identifier).GetName()

def ObjectExists(object_identifier: str) -> bool:
    return (GetSalomeObjectReference(object_identifier, False) is not None)

def GetSalomeID(salome_object) -> str:
    return salome.ObjectToID(salome_object)
