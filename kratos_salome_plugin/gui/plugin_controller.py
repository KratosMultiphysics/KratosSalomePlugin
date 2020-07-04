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
Loosely follows MVC / PAC pattern
https://www.tutorialspoint.com/software_architecture_design/interaction_oriented_architecture.htm
"""

# python imports
import os
import webbrowser
import logging
logger = logging.getLogger(__name__)

# plugin imports
from kratos_salome_plugin.gui.plugin_main_window import PluginMainWindow
from kratos_salome_plugin.gui.about import ShowAbout

def ShowNotImplementedMessage():
    from PyQt5.QtWidgets import QMessageBox
    QMessageBox.information(None, "Not implemented", "This is not yet implemented")

class PluginController(object):
    def __init__(self):
        logger.debug('Creating PluginController')
        self.main_window = PluginMainWindow()

        self.__ConnectMainWindow()

    def ShowMainWindow(self):
        self.main_window.show()


    def __ConnectMainWindow(self):
        ### File menu
        self.main_window.actionNew.triggered.connect(self._New)
        self.main_window.actionOpen.triggered.connect(self._Open)
        self.main_window.actionSave.triggered.connect(self._Save)
        self.main_window.actionSave_As.triggered.connect(self._SaveAs)
        self.main_window.actionSettings.triggered.connect(self._Settings)
        self.main_window.actionClose.triggered.connect(self._Close)

        ### Kratos menu
        self.main_window.actionGroups.triggered.connect(self._Groups)
        self.main_window.actionLoad_Application.triggered.connect(self._LoadApplication)
        self.main_window.actionImport_MDPA.triggered.connect(self._ImportMdpa)

        ### Help menu
        self.main_window.actionAbout.triggered.connect(lambda: ShowAbout(self.main_window))
        self.main_window.actionWebsite.triggered.connect(lambda: webbrowser.open("https://github.com/philbucher/KratosSalomePlugin"))

        ### Startup buttons
        self.main_window.pushButton_Open.clicked.connect(self._Open)
        self.main_window.pushButton_Load_Application.clicked.connect(self._LoadApplication)


    ### File menu
    def _New(self):
        ShowNotImplementedMessage()

    def _Open(self):
        ShowNotImplementedMessage()

    def _Save(self):
        ShowNotImplementedMessage()

    def _SaveAs(self):
        ShowNotImplementedMessage()

    def _Settings(self):
        ShowNotImplementedMessage()

    def _Close(self):
        self.main_window.close()

    ### Kratos menu
    def _Groups(self):
        ShowNotImplementedMessage()

    def _LoadApplication(self):
        ShowNotImplementedMessage()

    def _ImportMdpa(self):
        ShowNotImplementedMessage()


# for testing / debugging
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    contr = PluginController()
    contr.main_window.show()
    sys.exit(app.exec_())
