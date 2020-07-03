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
        self.main_window.actionNew.triggered.connect(self.__New)
        self.main_window.actionOpen.triggered.connect(self.__Open)
        self.main_window.actionSave.triggered.connect(self.__Save)
        self.main_window.actionSave_As.triggered.connect(self.__SaveAs)
        self.main_window.actionSettings.triggered.connect(self.__Settings)
        self.main_window.actionClose.triggered.connect(self.__Close)

        ### Kratos menu
        self.main_window.actionGroups.triggered.connect(self.__Groups)
        self.main_window.actionLoad_Application.triggered.connect(self.__LoadApplication)
        self.main_window.actionImport_MDPA.triggered.connect(self.__ImportMdpa)

        ### Help menu
        self.main_window.actionAbout.triggered.connect(lambda: ShowAbout(self.main_window))
        self.main_window.actionWebsite.triggered.connect(lambda: webbrowser.open("https://github.com/philbucher/KratosSalomePlugin"))

        ### Startup buttons
        self.main_window.pushButton_Open.clicked.connect(self.__Open)
        self.main_window.pushButton_Load_Application.clicked.connect(self.__LoadApplication)


    ### File menu
    def __New(self):
        ShowNotImplementedMessage()

    def __Open(self):
        ShowNotImplementedMessage()

    def __Save(self):
        ShowNotImplementedMessage()

    def __SaveAs(self):
        ShowNotImplementedMessage()

    def __Settings(self):
        ShowNotImplementedMessage()

    def __Close(self):
        self.main_window.close()

    ### Kratos menu
    def __Groups(self):
        ShowNotImplementedMessage()

    def __LoadApplication(self):
        ShowNotImplementedMessage()

    def __ImportMdpa(self):
        ShowNotImplementedMessage()


# for testing / debugging
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    contr = PluginController()
    contr.main_window.show()
    sys.exit(app.exec_())
