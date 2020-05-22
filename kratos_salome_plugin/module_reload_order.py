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

"""A list containing the order in which the python modules should be reloaded when the plugin is (re-)opened
The order has to be specified because of dependencies
"""
MODULE_RELOAD_ORDER = [
    "module_reload_order",
    "version",
    "utilities",
    "salome_dependent.salome_utilities",
    "mesh_interface",
    "model_part",
    "geometries_io",
    "write_mdpa",
    "plugin_logging",
    "base_application",
    "applications.Generic.application",
    "applications.StructuralMechanics.application"
]
