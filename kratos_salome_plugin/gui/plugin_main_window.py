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
from PyQt5.QtCore import Qt, QTimer
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

    def StatusBarInfo(self, message: str, msg_time:int=10) -> None:
        """show an info message in the statusbar
        input for time is in seconds
        """
        self.__StatusBarMessage(message, "green", msg_time)

    def StatusBarWarning(self, message: str, msg_time:int=10) -> None:
        """show a warning message in the statusbar
        input for time is in seconds
        """
        self.__StatusBarMessage(message, "yellow", msg_time)

    def __InitUI(self) -> None:
        """initialize the user interface from the "ui" file
        also set some settings that cannot be specified through the "ui" file
        """
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

    def __StatusBarMessage(self, message: str, color:int, msg_time: int) -> None:
        """compute the message time to fit the qt input and call the required functions
        msg_time in ms
        """
        msg_time = 2 * round(msg_time/2) * 1000 - 1000

        self.statusbar.showMessage(message, msg_time)
        self.__BlinkStatusBar(color, msg_time)

    def __BlinkStatusBar(self, color: str, msg_time: int) -> None:
        """blink the statusbar with a given color for given time
        Note that smaller blink_time will mess up the animation
        msg_time in ms
        maybe can be done better with QPropertyAnimation
        """
        blink_time = 1000 # [ms]
        num_blinks = int((msg_time+1000)/(blink_time*2))

        for i in range(num_blinks):
            delay_color = blink_time*i*2
            delay_base_color = blink_time*(i*2)+blink_time
            QTimer.singleShot(delay_color, lambda: self.statusbar.setStyleSheet(f"background-color: {color}"))
            QTimer.singleShot(delay_base_color, lambda: self.statusbar.setStyleSheet("background-color: white"))


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
