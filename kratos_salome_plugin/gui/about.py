#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

"""The About MessageBox of the Plugin"""

# python imports
import logging
logger = logging.getLogger(__name__)

# plugin imports
from kratos_salome_plugin.version import GetVersionString

# qt imports
from PyQt5.QtWidgets import QMessageBox


def About(parent_window):
    """Show the About MessageBox of the Plugin"""
    logger.debug("show About MessageBox")
    title = "Kratos Multiphysics plugin for Salome preprocessor"
    msg   = "Interface that allows setup of a Kratos simulation with the help of the Salome preprocessor.\n"
    msg  += "Version: {}\n".format(GetVersionString())
    QMessageBox.information(parent_window, title, msg)
