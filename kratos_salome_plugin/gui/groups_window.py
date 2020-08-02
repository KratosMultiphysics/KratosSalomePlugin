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
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIcon, QKeyEvent
from PyQt5 import uic

# plugin imports
from kratos_salome_plugin.utilities import GetAbsPathInPlugin
from kratos_salome_plugin.gui.group import Group
from kratos_salome_plugin.gui.groups_model import GroupsModel


class GroupsWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        if self.parent:
            self.parent.hide()

        self.__InitUI()
        self.__ConnectUI()

        self.model = GroupsModel()
        self.listView.setModel(self.model)

    def __InitUI(self) -> None:
        """initialize the user interface from the "ui" file
        also set some settings that cannot be specified through the "ui" file
        """
        uic.loadUi(GetAbsPathInPlugin("gui","ui_forms","groups_window.ui"), self)

        # manual adaptations that can't be done with QtDesigner
        self.setWindowIcon(QIcon(GetAbsPathInPlugin("misc","kratos_logo.png")))

        # self.actionClose.setShortcuts(["Ctrl+Q", "Esc"])

        self.statusbar.setStyleSheet("background-color: white")

        # prevent resize
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        self.setMinimumWidth(self.width())
        self.setMinimumHeight(self.height())

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

    def closeEvent(self, event):
        print("event")
        event.accept()
        if self.parent:
            self.parent.show()
        # reply = QtGui.QMessageBox.question(self, 'Message',
        #     "Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        # if reply == QtGui.QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()



# for testing / debugging
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ex = GroupsWindow(None)
    ex.show()
    sys.exit(app.exec_())
