#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# qt imports
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

def CreateInformativeMessageBox(
    text,
    icon,
    informative_text="",
    detailed_text=""):

    mbx = QMessageBox()

    mbx.setWindowTitle("KratosMultiphysics")
    mbx.setText(text)
    mbx.setIcon(getattr(QMessageBox, icon))

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

    return mbx

# for testing / debugging
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    CreateInformativeMessageBox("some_text", "Information", "sss", "ddddd").exec()
    print("after")

    sys.exit(app.exec_())
