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

# qt imports
from PyQt5.QtCore import QAbstractListModel

# plugin imports
from kratos_salome_plugin.gui.group import Group


class GroupsModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.__groups = {}

    def rowCount(self, index):
        return len(self.__groups)

    def Serialize(self):
        serialized_obj = {}

        for group in self.__groups.values():
            serialized_obj[group.name] = [
                group.mesh_identifier,
                group.entity_type
            ]

        return serialized_obj

    @staticmethod
    def Deserialize(serialized_obj):
        groups_manager = GroupsManager()

        for group_name, group_vals in serialized_obj.items():
            self.__groups[group_name] = Group(group_name, *group_vals)

        return groups_manager
