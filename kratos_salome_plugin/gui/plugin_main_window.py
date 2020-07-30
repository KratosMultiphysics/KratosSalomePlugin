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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5 import uic

# plugin imports
from kratos_salome_plugin.utilities import GetAbsPathInPlugin


class PluginMainWindow(QMainWindow):
    def __init__(self):
        logger.debug('Creating PluginMainWindow')
        super().__init__()
        self.__InitUI()

    def ShowOnTop(self) -> None:
        """show and activate the window, works both if opened newly or minimized
        see https://kb.froglogic.com/squish/qt/howto/maximizing-minimizing-restoring-resizing-positioning-windows/
        """
        self.show()
        self.activateWindow()
        self.setWindowState(Qt.WindowNoState)

    def __InitUI(self) -> None:
        uic.loadUi(GetAbsPathInPlugin("gui","ui_forms","plugin_main_window.ui"), self)

        # manual adaptations that can't be done with QtDesigner
        self.setWindowIcon(QIcon(GetAbsPathInPlugin("misc","kratos_logo.png")))

        self.actionClose.setShortcuts(["Ctrl+Q", "Esc"])

        self.statusbar.setStyleSheet("background-color: white")

        # prevent resize
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        self.setMinimumWidth(self.width())
        self.setMinimumHeight(self.height())


# for testing / debugging
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ex = PluginMainWindow()
    ex.ShowOnTop()
    sys.exit(app.exec_())
