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
This file defines the versioning of the plugin
It follows https://semver.org/
It also contains which versions of Salome the plugin has been tested with
NOTE: This file must NOT have dependencies on other files in the plugin!
"""

# versions of the plugin
__MAJOR = 1
__MINOR = 0
__PATCH = 0

def GetVersionMajor():
    """returns the major version of the plugin as int"""
    return __MAJOR

def GetVersionMinor():
    """returns the minor version of the plugin as int"""
    return __MINOR

def GetVersionPatch():
    """returns the patch version of the plugin as int"""
    return __PATCH

def GetVersions():
    """returns the versions of the plugin as a list of integers
    see salome_version.getVersion()
    """
    return [__MAJOR, __MINOR, __PATCH]

def GetVersionString():
    """returns the versions of the plugin as a string with versions separated by "."
    see salome_version.getVersions()
    """
    return "{}.{}.{}".format(__MAJOR, __MINOR, __PATCH)

# versions of salome with which the plugin was tested
TESTED_SALOME_VERSIONS = [
    [9,3,0],
    [9,4,0],
    [9,5,0]
]
