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
from PyQt5.QtCore import Qt, QAbstractListModel
from PyQt5.QtGui import QColor

# plugin imports
from kratos_salome_plugin.gui.group import Group


class GroupsModel(QAbstractListModel):
    """https://www.learnpyqt.com/courses/model-views/modelview-architecture/"""
    def __init__(self):
        super().__init__()
        self.__groups = []

    def GetGroupNames(self):
        return [group.name for group in self.__groups]

    def AddGroup(self, name, mesh_identifier, entity_type):
        if name in self.GetGroupNames():
            raise NameError('Group with name "{}" exists already!'.format(name))
        self.__groups.append(Group(name, mesh_identifier, entity_type))

    def GetGroup(self, name):
        if name not in self.GetGroupNames():
            raise IndexError('Group with name "{}" does not exist!'.format(name))

        for group in self.__groups:
            if group.name == name:
                return group

    def DeleteGroup(self, name):
        if name not in self.GetGroupNames():
            raise IndexError('Group with name "{}" does not exist!'.format(name))

        # TODO implement

    def rowCount(self, index):
        return len(self.__groups)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.__groups[index.row()].name

        if role == Qt.DecorationRole:
            return QColor(self.__groups[index.row()].GetStatusColor())

    def Serialize(self):
        serialized_obj = {}

        for group in self.__groups:
            serialized_obj[group.name] = [
                group.mesh_identifier,
                group.entity_type
            ]

        return serialized_obj

    def Deserialize(self, serialized_obj):
        self.__groups.clear()

        for group_name, group_vals in serialized_obj.items():
            self.__groups[group_name] = Group(group_name, *group_vals)

