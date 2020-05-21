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

# version of the plugin, see https://semver.org/
__MAJOR = 1
__MINOR = 0
__PATCH = 0

def GetVersionMajor():
    return __MAJOR

def GetVersionMinor():
    return __MINOR

def GetVersionPatch():
    return __PATCH

def GetVersions():
    # see salome_version.getVersion()
    return [__MAJOR, __MINOR, __PATCH]

def GetVersionString():
    # see salome_version.getVersions()
    return f"__MAJOR.__MINOR.__PATCH"

# versions of salome with which the plugin was tested
TESTED_SALOME_VERSIONS = [
    [9,3,0],
    [9,4,0]
]
