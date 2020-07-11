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
The ProjectPathHandler is used for interacting with the user for
getting paths for opening and saving projects
"""

# python imports
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

# qt imports
from PyQt5.QtWidgets import QFileDialog


class ProjectPathHandler(object):
    """TODO: using native dialogs or not?"""
    def __init__(self):
        # using home directory as start
        self.last_path = Path.home()

    def GetOpenPath(self, parent_window=None) -> Path:
        """Getting path for opening project
        TODO: opening only folders with ".ksp" extension (like filtering for filenames)
        """
        path = Path(QFileDialog.getExistingDirectory(
            parent_window,
            'Select a KSP project folder (*.ksp)',
            self.last_path,
            QFileDialog.ShowDirsOnly))

        if path == "":
            # dialog was aborted
            return ""

        if path.suffix != ".ksp":
            print(path)
            raise Exception('Invalid project folder selected, must end with ".ksp"!')

        self.last_path = path.parent

        logger.debug("Opening project path: %s", path)

        return path

    def GetSavePath(self, parent_window=None) -> Path:
        """Getting path for saving project"""
        path = Path(QFileDialog.getSaveFileName(parent_window, "Save KSP project", self.last_path)[0])

        if path == "":
            # dialog was aborted
            return ""

        path = path.with_suffix(".ksp")

        self.last_path = path.parent

        logger.debug("Saving project path: %s", path)

        return path
