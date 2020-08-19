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
from pathlib import Path
from typing import List
import logging
logger = logging.getLogger(__name__)

# qt imports
from PyQt5.QtCore import Qt

# plugin imports
from kratos_salome_plugin.utilities import GetAbsPathInPlugin
from kratos_salome_plugin.gui.base_window import BaseWindow
from kratos_salome_plugin.gui.group import Group
from kratos_salome_plugin.salome_utilities import GetSalomeObject, GetObjectName
from kratos_salome_plugin import salome_gui_utilities
from kratos_salome_plugin.salome_mesh_utilities import IsAnyMesh


class GroupsWindow(BaseWindow):
    def __init__(self, parent, model):
        super().__init__(Path(GetAbsPathInPlugin("gui", "ui_forms", "groups_window.ui")), parent)

        # this window should stay on top, it is much more convenient to select meshes then
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.model = model
        self.listView.setModel(self.model)

        self.__ConnectUI()

    def __ConnectUI(self) -> None:
        self.button_select_mesh.clicked.connect(self._SelectMesh)
        self.button_save_group.clicked.connect(self._SaveGroup)
        self.button_update_group.clicked.connect(self._UpdateGroup)
        self.button_clear_group.clicked.connect(self._ClearInputFields)
        self.button_show_groups.clicked.connect(self._ShowGroups)

        self.listView.doubleClicked.connect(self._EditGroup)

        self.lineEdit_group_name.textChanged.connect(self._EnableGroupButtons)
        self.lineEdit_mesh_identifier.textChanged.connect(self._EnableGroupButtons)
        self.lineEdit_entity_type.textChanged.connect(self._EnableGroupButtons)

    def _EnableGroupButtons(self):
        enable_save_group = False
        enable_update_group = False

        if self.lineEdit_mesh_identifier.text():
            if self.lineEdit_entity_type.text():
                group_name = self.lineEdit_group_name.text()
                if group_name:
                    if group_name in self.model.GetGroupNames():
                        enable_update_group = True
                    else:
                        enable_save_group = True

        self.button_save_group.setEnabled(enable_save_group)
        self.button_update_group.setEnabled(enable_update_group)

    def _SelectMesh(self) -> None:
        selection = salome_gui_utilities.GetAllSelected()

        # make sure only one mesh is selected
        if len(selection) != 1:
            self.StatusBarWarning("Please select one mesh!")
            return

        selection_identifier = selection[0]
        salome_object = GetSalomeObject(selection_identifier)

        # check if is mesh
        if not IsAnyMesh(salome_object):
            self.StatusBarWarning("Selection is not a mesh!")
            logger.debug("Selection is not a mesh; type: %s", type(salome_object))
            return

        # clear selection only after validating input
        salome_gui_utilities.ClearSelection()

        # if no name was given before, then use the mesh name
        if self.lineEdit_group_name.text():
            mesh_name = GetObjectName(selection_identifier)
            self.lineEdit_group_name.setText(mesh_name)

        self.lineEdit_mesh_identifier.setText(selection_identifier)

        self.lineEdit_entity_type.setText("Triangle") # TODO implement properly


    def _SaveGroup(self) -> None:
        group_name = self.lineEdit_group_name.text()

        self.model.AddGroup(group_name, self.lineEdit_mesh_identifier.text(), self.lineEdit_entity_type.text())

        # Trigger refresh.
        self.model.layoutChanged.emit()

        # Empty the input
        self._ClearInputFields()

    def _UpdateGroup(self) -> None:
        group_name = self.lineEdit_group_name.text()

        group = self.model.GetGroup(group_name)
        group.mesh_identifier = self.lineEdit_mesh_identifier.text()
        group.entity_type = self.lineEdit_entity_type.text()

        # Trigger refresh. (could be refactored to only use dataChanged since only maybe color changes)
        self.model.layoutChanged.emit()

        # Empty the input
        self._ClearInputFields()


    def _DeleteGroup(self) -> None:
        selected_groups = self.listView.selectedIndexes()
        if selected_groups:
            for selected_group in selected_groups:
                group_name = selected_group.data()
                self.model.DeleteGroup(group_name)

            # Trigger refresh.
            self.model.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            self.listView.clearSelection()

            self._EnableGroupButtons()
        else:
            print("selection was none")

    def _EditGroup(self) -> None:
        selected_groups = self.listView.selectedIndexes()
        if selected_groups:
            # only one is selected from double click
            group_name = selected_groups[0].data()

            group = self.model.GetGroup(group_name)

            self.lineEdit_group_name.setText(group.name)
            self.lineEdit_mesh_identifier.setText(group.mesh_identifier)
            self.lineEdit_entity_type.setText(group.entity_type)

        else:
            print("selection was none")

    def _ClearInputFields(self) -> None:
        self.lineEdit_group_name.setText("")
        self.lineEdit_mesh_identifier.setText("")
        self.lineEdit_entity_type.setText("")

    def _ShowGroups(self) -> None:
        mesh_indices = [group.mesh_identifier for group in self._GetSelectedGroups()]
        salome_gui_utilities.DisplayObjectsOnly(mesh_indices)

    def _GetSelectedGroups(self) -> List[Group]:
        return [self.model.GetGroup(index.data()) for index in self.listView.selectedIndexes()]


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self._DeleteGroup()
        else:
            super().keyPressEvent(event)


# for testing / debugging
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = GroupsWindow(None)
    win.show()
    # win.StatusBarWarning("Obacht")
    win.StatusBarInfo("hey")
    sys.exit(app.exec_())
