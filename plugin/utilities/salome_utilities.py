#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher
#

# This file must NOT have dependencies on other files in the plugin!
# it contains utility functions for interacting with Salome
# it depends on salome and can only be imported, if executed in Salome

# salome imports
import salome_version

def GetVersionMajor():
    return int(salome_version.getVersionMajor())

def GetVersionMinor():
    return int(salome_version.getVersionMinor())

def GetVersion():
    return (GetVersionMajor(), GetVersionMinor())