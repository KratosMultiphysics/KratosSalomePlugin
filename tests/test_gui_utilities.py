#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# set up testing environment (before anything else)
import initialize_testing_environment

# python imports
import unittest

# plugin imports
from kratos_salome_plugin.gui import utilities

# tests imports
from testing_utilities import QtTestCase

# qt imports
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


class TestCreateInformativeMessageBox(QtTestCase):
    """TODO add a test where the close ( x ) button is pressed => figure out how to trigger"""
    def test_wrong_icon(self):
        wrong_name = "random_icon_non_existing"
        with self.assertRaisesRegex(AttributeError, "has no attribute '"+wrong_name):
            utilities.CreateInformativeMessageBox("my_text", wrong_name)

    def test_basics(self):
        my_text = "some_text that has nothing"

        mbx = utilities.CreateInformativeMessageBox(my_text, "NoIcon")

        self.assertEqual(mbx.text(), my_text)
        self.assertEqual(mbx.informativeText(), "")
        self.assertEqual(mbx.detailedText(), "")

    def test_informative_text(self):
        my_text = "some_text that has a little bit"
        inform_text = "Here some more info is provided!"

        mbx = utilities.CreateInformativeMessageBox(my_text, "NoIcon", inform_text)

        self.assertEqual(mbx.text(), my_text)
        self.assertEqual(mbx.informativeText(), inform_text)
        self.assertEqual(mbx.detailedText(), "")

    def test_detailed_text(self):
        my_text = "some_text that has a a lot!"
        inform_text = "Here some more info is kinda provided!"
        det_text = "This is some pretty detailed information\nEven more!!"

        mbx = utilities.CreateInformativeMessageBox(my_text, "NoIcon", inform_text, det_text)

        self.assertEqual(mbx.text(), my_text)
        self.assertEqual(mbx.informativeText(), inform_text)
        self.assertEqual(mbx.detailedText(), det_text)

    def test_ok_key(self):
        base_args = ["some text", "NoIcon"] # those are always needed
        additional_args = [
            [],
            ["inform_Text"],
            ["inform_Text", "detailed_text"]
        ]

        for args in additional_args:
            all_args = base_args+args
            with self.subTest(all_args=all_args):
                mbx = utilities.CreateInformativeMessageBox(*all_args) # args need to be passed then it blocks!
                close_delay = 0 # [ms]
                ok_btn = mbx.button(QMessageBox.Ok)
                QTimer.singleShot(close_delay, ok_btn.click)
                mbx.exec() # this must return due to the singleShot!

    def test_escape(self):
        base_args = ["some text", "NoIcon"] # those are always needed
        additional_args = [
            [],
            ["inform_Text"],
            ["inform_Text", "detailed_text"]
        ]

        for args in additional_args:
            all_args = base_args+args
            with self.subTest(all_args=all_args):
                mbx = utilities.CreateInformativeMessageBox(*all_args) # args need to be passed then it blocks!
                close_delay = 0 # [ms]
                QTimer.singleShot(close_delay, lambda: QTest.keyClick(mbx, Qt.Key_Escape))
                mbx.exec() # this must return due to the singleShot!


if __name__ == '__main__':
    unittest.main()
