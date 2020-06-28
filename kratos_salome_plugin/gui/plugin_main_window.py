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


class PluginMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.__InitUI()

    def __InitUI(self):
        uic.loadUi(GetAbsPathInPlugin("gui","ui_forms","plugin_main_window.ui"), self)
        self.setWindowIcon(QIcon(GetAbsPathInPlugin("misc","kratos_logo.png")))

        self.statusbar.setStyleSheet("background-color: white")


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ex = PluginMainWindow()
    ex.show()
    sys.exit(app.exec_())
