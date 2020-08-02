#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

"""Base main window for the Plugin. Defines some basic functionalities"""

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
from kratos_salome_plugin.utilities import PathCheck


class BaseWindow(QMainWindow):
    def __init__(self, ui_form_path, parent=None):
        logger.debug('Creating BaseWindow')

        super().__init__()

        PathCheck(ui_form_path)
        self.__InitUI(ui_form_path)

        self.parent = parent
        # hide parent if existing
        if self.parent:
            self.parent.hide()

    def StatusBarInfo(self, message: str, msg_time: int=10) -> None:
        """show an info message in the statusbar
        input for time is in seconds
        """
        self.__StatusBarMessage(message, "green", msg_time)

    def StatusBarWarning(self, message: str, msg_time: int=10) -> None:
        """show a warning message in the statusbar
        input for time is in seconds
        """
        self.__StatusBarMessage(message, "yellow", msg_time)

    def keyPressEvent(self, event):
        # close if ESC or Ctrl+q is pressed
        if event.key() == Qt.Key_Escape or (event.key() == Qt.Key_Q and event.modifiers() == Qt.ControlModifier):
            self.close()
            event.accept()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """show the parent window again"""
        if self.parent:
            self.parent.show()

        super().closeEvent(event)

    def __InitUI(self, ui_form_path) -> None:
        """initialize the user interface from the "ui" file
        also set some settings that cannot be specified through the "ui" file
        """
        uic.loadUi(str(ui_form_path), self)

        # manual adaptations that can't be done with QtDesigner
        self.setWindowIcon(QIcon(GetAbsPathInPlugin("misc","kratos_logo.png")))

        self.statusbar.setStyleSheet("background-color: white")

        # prevent resize
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        self.setMinimumWidth(self.width())
        self.setMinimumHeight(self.height())

    def __StatusBarMessage(self, message: str, color: int, msg_time: int) -> None:
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
            QTimer.singleShot(delay_color, lambda: self.statusbar.setStyleSheet("background-color: {}".format(color)))
            QTimer.singleShot(delay_base_color, lambda: self.statusbar.setStyleSheet("background-color: white"))


# for testing / debugging
if __name__ == '__main__':
    import sys
    from pathlib import Path
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = BaseWindow(Path(GetAbsPathInPlugin("gui", "ui_forms", "plugin_main_window.ui")))
    win.show()
    # win.StatusBarWarning("Obacht")
    win.StatusBarInfo("hey")
    sys.exit(app.exec_())
