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
from kratos_salome_plugin.gui.groups_window import GroupsWindow
from kratos_salome_plugin.gui.about import ShowAbout
import kratos_salome_plugin.gui.active_window as active_window
from kratos_salome_plugin.gui.project_manager import ProjectManager
from kratos_salome_plugin.gui.project_path_handler import ProjectPathHandler

def ShowNotImplementedMessage():
    from PyQt5.QtWidgets import QMessageBox
    QMessageBox.information(None, "Not implemented", "This is not yet implemented")


class PluginController:
    def __init__(self):
        logger.debug('Creating PluginController')
        self._main_window = PluginMainWindow()
        active_window.ACTIVE_WINDOW = self._main_window

        self.__InitializeMembers()

        self.__ConnectMainWindow()


    def __InitializeMembers(self) -> None:
        """completely reinitialize members to clean them"""
        self._project_manager = ProjectManager()
        self._project_path_handler = ProjectPathHandler()
        self._previous_save_path = None

    def __ConnectMainWindow(self) -> None:
        ### File menu
        self._main_window.actionNew.triggered.connect(self._New)
        self._main_window.actionOpen.triggered.connect(self._Open)
        self._main_window.actionSave.triggered.connect(self._Save)
        self._main_window.actionSave_As.triggered.connect(self._SaveAs)
        self._main_window.actionSettings.triggered.connect(self._Settings)
        self._main_window.actionClose.triggered.connect(self._Close)

        ### Kratos menu
        self._main_window.actionGroups.triggered.connect(self._Groups)
        self._main_window.actionImport_MDPA.triggered.connect(self._ImportMdpa)
        self._main_window.actionLaunch_Flowgraph.triggered.connect(self._LaunchFlowgraph)

        ### Help menu
        self._main_window.actionAbout.triggered.connect(lambda: ShowAbout(self._main_window))
        self._main_window.actionWebsite_Plugin.triggered.connect(lambda: webbrowser.open("https://github.com/KratosMultiphysics/KratosSalomePlugin"))
        self._main_window.actionWebsite_Kratos.triggered.connect(lambda: webbrowser.open("https://github.com/KratosMultiphysics/Kratos"))
        self._main_window.actionWebsite_Flowgraph.triggered.connect(lambda: webbrowser.open("https://github.com/KratosMultiphysics/Flowgraph"))

        ### Startup buttons
        self._main_window.pushButton_Open.clicked.connect(self._Open)


    ### File menu
    def _New(self) -> None:
        """Create new project. Salome study is untouched
        # TODO check for unsaved changes
        """
        self.__InitializeMembers()

    def _Open(self) -> None:
        """Open a project. User is asked for the path to the project folder
        # TODO check for unsaved changes
        """
        try:
            path = self._project_path_handler.GetOpenPath(self._main_window)
        except UserInputError as e:
            msg = "User input error while opening project: {}".format(e)
            logger.warning(msg)
            self._main_window.StatusBarWarning(msg)
            return

        if path == Path("."): # this means the dialog was aborted, do nothing in this case
            msg = "Opening was aborted"
            logger.info(msg)
            self._main_window.StatusBarWarning(msg)
            return

        open_successful = self._project_manager.OpenProject(path)

        if open_successful:
            msg = 'Successfully opened project from "{}"'.format(path)
            logger.info(msg)
            self._main_window.StatusBarInfo(msg)
        else:
            logger.critical('Failed to open project from "%s"!', path)

    def _Save(self) -> None:
        """Save the project. If it was saved before the same path is reused.
        Otherwise SaveAs is used and the user is asked to provide a path for saving
        """
        if self._previous_save_path:
            logger.info("Saving project with previous save path ...")
            self.__SaveProject(self._previous_save_path)
        else: # project was not previously saved
            self._SaveAs()

    def _SaveAs(self) -> None:
        """Save the project. The user is asked to provide a path for saving.
        If the dialog for giving the path is aborted then nothing happens
        """
        logger.info("Saving project as ...")

        path = self._project_path_handler.GetSavePath(self._main_window)

        if path == Path("."): # this means the dialog was aborted, do nothing in this case
            msg = "Saving was aborted"
            logger.info(msg)
            self._main_window.StatusBarWarning(msg)
            return

        save_successful = self.__SaveProject(path)
        if save_successful:
            self._previous_save_path = path # saving the path such that it can be reused


    def _Settings(self) -> None:
        raise Exception("Example of showing exception in messagebox")
        ShowNotImplementedMessage()

    def _Close(self) -> None:
        """Close the plugin window
        State is preserved!
        TODO check for unsaved changes(?)
        TODO if nothing else is implemented this can be moved to the PluginMainWindow
        """
        self._main_window.close()

    ### Kratos menu
    def _Groups(self) -> None:
        """open the groups window"""
        logger.debug("Opening Groups")
        _groups_widget = GroupsWindow(self._main_window, self._project_manager.groups_model)
        _groups_widget.show() # showing makes it the active window, hence no need to save it as member

    def _LaunchFlowgraph(self) -> None:
        ShowNotImplementedMessage()

    def _ImportMdpa(self) -> None:
        ShowNotImplementedMessage()

    def __SaveProject(self, path: Path) -> bool:
        """internal function for saving the project
        and issue the appropriate infos for the user
        returns if saving was successful
        """
        save_successful = self._project_manager.SaveProject(path)
        if save_successful:
            msg = 'Saved project under "{}"'.format(path)
            logger.info(msg)
            self._main_window.StatusBarInfo(msg)
        else:
            logger.critical('Failed to save project under "%s"!', path)
        return save_successful


# for testing / debugging
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    contr = PluginController()
    contr._main_window.show()
    sys.exit(app.exec_())
