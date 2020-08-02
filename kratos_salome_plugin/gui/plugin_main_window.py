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


class PluginMainWindow(BaseWindow):
    def __init__(self):
        logger.debug('Creating PluginMainWindow')
        super().__init__(Path(GetAbsPathInPlugin("gui", "ui_forms", "plugin_main_window.ui")))

    def ShowOnTop(self) -> None:
        """show and activate the window, works both if opened newly or minimized
        see https://kb.froglogic.com/squish/qt/howto/maximizing-minimizing-restoring-resizing-positioning-windows/
        """
        self.show()
        self.activateWindow()
        self.setWindowState(Qt.WindowNoState)

    def closeEvent(self, event):
        """prevent the window from closing, only hiding it
        Note that this deliberately does not call the baseclass, as the event should be ignored
        """
        event.ignore()
        self.hide()


# for testing / debugging
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = PluginMainWindow()
    win.ShowOnTop()
    # win.StatusBarWarning("Obacht")
    win.StatusBarInfo("hey")
    sys.exit(app.exec_())
