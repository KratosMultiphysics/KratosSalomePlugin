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
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5 import uic

# plugin imports
from kratos_salome_plugin.utilities import GetAbsPathInPlugin


class GroupsWidget(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        if self.parent:
            self.parent.hide()

        self.__InitUI()

    def __InitUI(self) -> None:
        """initialize the user interface from the "ui" file
        also set some settings that cannot be specified through the "ui" file
        """
        uic.loadUi(GetAbsPathInPlugin("gui","ui_forms","groups_widget.ui"), self)

        # manual adaptations that can't be done with QtDesigner
        self.setWindowIcon(QIcon(GetAbsPathInPlugin("misc","kratos_logo.png")))

        # self.actionClose.setShortcuts(["Ctrl+Q", "Esc"])

        self.statusbar.setStyleSheet("background-color: white")

        # prevent resize
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        self.setMinimumWidth(self.width())
        self.setMinimumHeight(self.height())

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
    ex = GroupsWidget(None)
    ex.show()
    sys.exit(app.exec_())
