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

# qt imports
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5 import uic

# plugin imports
from kratos_salome_plugin.utilities import GetAbsPathInPlugin
from kratos_salome_plugin.gui.base_main_window import BaseMainWindow


class PluginMainWindow(BaseMainWindow):
    def __init__(self):
        logger.debug('Creating PluginMainWindow')
        super().__init__(Path(GetAbsPathInPlugin("gui", "ui_forms", "plugin_main_window.ui")))

    def closeEvent(self, event):
        """prevent the window from closing, only hiding it"""
        event.ignore()
        self.hide()

# for testing / debugging
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ex = PluginMainWindow()
    ex.ShowOnTop()
    # ex.StatusBarWarning("Obacht")
    ex.StatusBarInfo("hey")
    sys.exit(app.exec_())
