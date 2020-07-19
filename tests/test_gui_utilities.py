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
from pathlib import Path
from sys import executable
from subprocess import Popen, PIPE
import locale

# plugin imports
from kratos_salome_plugin.gui import utilities

# tests imports
from testing_utilities import QtTestCase

# qt imports
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

"""for currently unknown reasons testing QMessageBox doesn't play nice with
the tests for QMainWinodw. Due to this they are currently being executed in a separate
process if run together with other tests
"""

if __name__ == '__main__':
    # test is run standalone
    class TestCreateInformativeMessageBox(QtTestCase):
        """TODO add a test where the close ( x ) button is pressed => figure out how to trigger"""
        def test_wrong_icon(self):
            wrong_name = "random_icon_non_existing"
            with self.assertRaisesRegex(AttributeError, "has no attribute '"+wrong_name):
                utilities.CreateInformativeMessageBox("my_text", wrong_name)

        def test_basics(self):
            my_text = "some_text that has nothing"

            def CheckFct(message_box):
                SingleShotOkKlick(message_box)
                self.assertEqual(message_box.text(), my_text)
                self.assertEqual(message_box.informativeText(), "")
                self.assertEqual(message_box.detailedText(), "")

            utilities.CreateInformativeMessageBox(my_text, "NoIcon", fct_ptr=CheckFct)

        def test_informative_text(self):
            my_text = "some_text that has a little bit"
            inform_text = "Here some more info is provided!"

            def CheckFct(message_box):
                SingleShotOkKlick(message_box)
                self.assertEqual(message_box.text(), my_text)
                self.assertEqual(message_box.informativeText(), inform_text)
                self.assertEqual(message_box.detailedText(), "")

            utilities.CreateInformativeMessageBox(my_text, "NoIcon", inform_text, fct_ptr=CheckFct)

        def test_detailed_text(self):
            my_text = "some_text that has a a lot!"
            inform_text = "Here some more info is kinda provided!"
            det_text = "This is some pretty detailed information\nEven more!!"

            def CheckFct(message_box):
                SingleShotOkKlick(message_box)
                self.assertEqual(message_box.text(), my_text)
                self.assertEqual(message_box.informativeText(), inform_text)
                self.assertEqual(message_box.detailedText(), det_text)

            utilities.CreateInformativeMessageBox(my_text, "NoIcon", inform_text, det_text, fct_ptr=CheckFct)

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
                    mbx = utilities.CreateInformativeMessageBox(*all_args, fct_ptr=SingleShotOkKlick) # args need to be passed then it blocks!

            # only pass detailed but not informative text
            with self.subTest(detailed_text=additional_args[2][1]):
                mbx = utilities.CreateInformativeMessageBox(*base_args, detailed_text=additional_args[2][1], fct_ptr=SingleShotOkKlick) # args need to be passed then it blocks!

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
                    utilities.CreateInformativeMessageBox(*all_args, fct_ptr=SingleShotEscape) # args need to be passed then it blocks!

            # only pass detailed but not informative text
            with self.subTest(detailed_text=additional_args[2][1]):
                mbx = utilities.CreateInformativeMessageBox(*base_args, detailed_text=additional_args[2][1], fct_ptr=SingleShotEscape) # args need to be passed then it blocks!


    def SingleShotOkKlick(message_box):
        """aux function to close messagebox"""
        close_delay = 0 # [ms]
        ok_btn = message_box.button(QMessageBox.Ok)
        QTimer.singleShot(close_delay, ok_btn.click)

    def SingleShotEscape(message_box):
        """aux function to close messagebox"""
        close_delay = 0 # [ms]
        QTimer.singleShot(close_delay, lambda: QTest.keyClick(message_box, Qt.Key_Escape))


    unittest.main()

else:
    # test is run with others
    class TestCreateInformativeMessageBoxInSubprocess(unittest.TestCase):
        def test_in_subprocess(self):
            def GetProcessOutput(proc_stdout, proc_stderr):
                msg  = "\nStdOut:\n"
                if proc_stdout:
                    msg += proc_stdout.decode(locale.getpreferredencoding())
                msg += "\nStdErr:\n"
                if proc_stderr:
                    msg += proc_stderr.decode(locale.getpreferredencoding())
                return msg

            proc = Popen([executable, str(Path(__file__))], stdout=PIPE, stderr=PIPE, cwd=str(Path(__file__).parent))
            stdout, stderr = proc.communicate()
            self.assertEqual(proc.returncode, 0, msg=GetProcessOutput(stdout, stderr))
