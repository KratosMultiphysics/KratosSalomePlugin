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
import logging
logger = logging.getLogger(__name__)

# plugin imports
from kratos_salome_plugin.utilities import GetAbsPathInPlugin
from kratos_salome_plugin.gui.base_window import BaseWindow


class GroupsWindow(BaseWindow):
    def __init__(self, parent, model):
        logger.debug('Creating GroupsWindow')
        super().__init__(Path(GetAbsPathInPlugin("gui", "ui_forms", "groups_window.ui")), parent)

        self.model = model
        self.listView.setModel(self.model)

        self.__ConnectUI()

    def __ConnectUI(self) -> None:
        self.button_save_group.clicked.connect(self._SaveGroup)
        self.listView.doubleClicked.connect(self._EditGroup)


    def _SaveGroup(self):
        print("Save Group")
        group_name = self.lineEdit_group_name.text()
        if group_name:
            self.model.AddGroup(group_name, "1:2:3:4", "Triangle")

            # Trigger refresh.
            self.model.layoutChanged.emit()
            # Empty the input
            self.lineEdit_group_name.setText("")

        else:
            print("empty group name!")
            # TODO show warning

    def _DeleteGroup(self):
        selected_groups = self.listView.selectedIndexes()
        if selected_groups:
            print(selected_groups)
            for selected_group in selected_groups:
                self.model.DeleteGroup(selected_group)

            # Trigger refresh.
            self.model.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            self.todoView.clearSelection()
        else:
            print("selection was none")

    def _EditGroup(self):
        print("Editing group...")
        selected_groups = self.listView.selectedIndexes()
        if selected_groups:
            # only one is selected from double click
            group_name = selected_groups[0].data()

            group = self.model.GetGroup(group_name)

            self.lineEdit_group_name.setText(group.name)

        else:
            print("selection was none")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            print("deleting")
            self._DeleteGroup()
        else:
            print("sth else...")




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
