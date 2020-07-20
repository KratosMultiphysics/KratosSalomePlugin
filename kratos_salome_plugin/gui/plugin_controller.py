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
from pathlib import Path
import webbrowser
import logging
logger = logging.getLogger(__name__)

# plugin imports
from kratos_salome_plugin.exceptions import UserInputError
from kratos_salome_plugin.gui.plugin_main_window import PluginMainWindow
from kratos_salome_plugin.gui.about import ShowAbout
from kratos_salome_plugin.gui.project_manager import ProjectManager
from kratos_salome_plugin.gui.project_path_handler import ProjectPathHandler

def ShowNotImplementedMessage():
    from PyQt5.QtWidgets import QMessageBox
    QMessageBox.information(None, "Not implemented", "This is not yet implemented")

class PluginController(object):
    def __init__(self):
        logger.debug('Creating PluginController')
        self.main_window = PluginMainWindow()
        self.__InitializeMembers()

        self.__ConnectMainWindow()

    def ShowMainWindow(self):
        self.main_window.show()


    def __InitializeMembers(self) -> None:
        self._project_manager = ProjectManager()
        self._project_path_handler = ProjectPathHandler()
        self._previous_save_path = None


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
        # TODO check for unsaved changes
        self.__InitializeMembers()
        # self._project_manager.ResetProject()
        # completely reinitialize members
        # self._project_manager = ProjectManager()
        # self._project_path_handler = ProjectPathHandler()

    def _Open(self):
        # TODO check for unsaved changes
        try:
            path = self._project_path_handler.GetOpenPath(self.main_window) # check if dialog was aborted i.e. nothing is returned
        except UserInputError as e:
            print(e)
            return
        self._project_manager.OpenProject(path) # check if everything was ok

    def _Save(self):
        if self._previous_save_path:
            self._project_manager.SaveProject(path) # check if everything was ok
        else:
            self._SaveAs()

    def _SaveAs(self):
        """Save the project. The user is asked to provide a path for saving
        if the dialog for giving the path is aborted then nothing happens
        """
        logger.info("Saving project as ...")

        path = self._project_path_handler.GetSavePath(self.main_window)

        if path == Path("."): # this means the dialog was aborted, do nothing in this case
            logger.info("Saving was aborted")
            return

        save_successful = self._project_manager.SaveProject(path)

        if save_successful:
            self._previous_save_path = path # saving the path such that it can be reused
            logger.info('Saved project under "%s"', path)
        else:
            logger.critical('Failed to save project under "%s"!', path)


    def _Settings(self):
        raise Exception("Example of showing exception in messagebox")
        ShowNotImplementedMessage()

    def _Close(self):
        # TODO check for unsaved changes
        self.main_window.close()

    ### Kratos menu
    def _Groups(self):
        logger.critical("This is a critical messagbox example")
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
