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

# qt imports
from PyQt5.QtCore import Qt

# plugin imports
from kratos_salome_plugin.utilities import GetAbsPathInPlugin
from kratos_salome_plugin.gui.base_window import BaseWindow


class GroupsWindow(BaseWindow):
    def __init__(self, parent, model):
        super().__init__(Path(GetAbsPathInPlugin("gui", "ui_forms", "groups_window.ui")), parent)

        # this window should stay on top, it is much more convenient to select meshes then
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
