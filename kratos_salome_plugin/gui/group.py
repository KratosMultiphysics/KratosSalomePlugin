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
"""

# python imports
import logging
logger = logging.getLogger(__name__)

# for showing group: https://docs.salome-platform.org/latest/gui/GUI/text_user_interface.html

class Group:
    def __init__(self, name, mesh_identifier, entity_type):
        self.name = name
        self.mesh_identifier = mesh_identifier
        self.entity_type = entity_type
