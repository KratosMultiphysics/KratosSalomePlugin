
from PyQt5.QtWidgets import QMessageBox


def ShowInformativeMessageBox(
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

    mbx.exec()
