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
This file contains utility functions for GUI related functionalities
NOTE: This file must NOT have dependencies on other files in the plugin!
"""

# qt imports
from PyQt5.QtWidgets import QMessageBox


def CreateInformativeMessageBox(
    text,
    icon,
    informative_text="",
    detailed_text="",
    fct_ptr=None):
    """Shows a messagebox with the given input
    "fct_ptr" can be used to pass an additional
    function that can operate on the messagebox before it is shown.
    This is particularily helpful for testing
    """

    mbx_icon = getattr(QMessageBox, icon)

    mbx = QMessageBox()

    mbx.setWindowTitle("KratosMultiphysics")
    mbx.setText(text)
    mbx.setIcon(mbx_icon)

    # set buttons to work properly
    # see https://stackoverflow.com/a/32764190
    mbx.setStandardButtons(QMessageBox.Ok)
    mbx.setDefaultButton(QMessageBox.Ok)
    mbx.setEscapeButton(QMessageBox.Ok)

    # optional information
    if informative_text:
        mbx.setInformativeText(informative_text)
    if detailed_text:
        mbx.setDetailedText(detailed_text)

    # call the function pointer with the messagebox before executing it
    if fct_ptr:
        fct_ptr(mbx)

    mbx.exec()
