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
from kratos_salome_plugin.salome_utilities import ObjectExists, GetSalomeObject
from kratos_salome_plugin.salome_mesh_utilities import IsAnyMesh, MeshHasEntitiesOfType


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
            raise ValueError('Group with name "{}" does not exist!'.format(name))

        return self.__groups[self.__GetGroupIndex(name)]

    def DeleteGroup(self, name):
        if name not in self.GetGroupNames():
            raise ValueError('Group with name "{}" does not exist!'.format(name))

        del self.__groups[self.__GetGroupIndex(name)]

    def rowCount(self, index):
        return len(self.__groups)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.__groups[index.row()].name

        if role == Qt.DecorationRole:
            return QColor(*self._GetGroupStatusColor(self.__groups[index.row()]))

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
            self.__groups.append(Group(group_name, *group_vals))

    def __GetGroupIndex(self, group_name):
        """https://stackoverflow.com/a/47057419"""
        return next(i for i, x in enumerate(self.__groups) if x.name == group_name)

    def _GetGroupStatusColor(self, group):
        # first check if mesh exists
        if not ObjectExists(group.mesh_identifier):
            return (255, 0, 0) # red

        # next check if the object is a mesh
        salome_object = GetSalomeObject(group.mesh_identifier)
        if not IsAnyMesh(salome_object):
            return (255,140,0) # dark orange

        # next check if the requested entities still exist in the mesh
        if not MeshHasEntitiesOfType(salome_object, group.entity_type):
            return (255,255,0) # yellow

        # if everything is ok
        return (0, 200, 0) # green
