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
from sys import exc_info, executable
from subprocess import Popen, PIPE
from pathlib import Path
import unittest
from unittest.mock import patch

# plugin imports
from kratos_salome_plugin import plugin_logging

# tests imports
from testing_utilities import QtTestCase

# qt imports
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


class TestExceptionLogging(unittest.TestCase):

    @patch('kratos_salome_plugin.plugin_logging.CreateInformativeMessageBox')
    def _test_exception_logging(self, create_msg_box_mock):
        # assert sys.excepthook is uncaught_exception_handler
        # with your_preferred_output_capture_mechanism:
        with self.assertLogs(level="ERROR") as cm:
            try:
                1/0
            except ZeroDivisionError:
                plugin_logging._HandleUnhandledException(*exc_info())
                err_name = exc_info()[0].__name__
                err_value = str(exc_info()[1])

        with self.subTest("Testing exception logs"):
            self.assertEqual(len(cm.output), 1)
            self.assertIn('ERROR:root:Unhandled exception\nTraceback', cm.output[0])
            self.assertIn(err_name, cm.output[0])
            self.assertIn(err_value, cm.output[0])

        with self.subTest("Testing exception message box"):
            if initialize_testing_environment.PYQT_AVAILABLE:
                self.assertEqual(create_msg_box_mock.call_count, 1)
                msg_box_fct_args = create_msg_box_mock.call_args_list[0][0]
                self.assertEqual(msg_box_fct_args[0], "An unhandled excepition occured!")
                self.assertEqual(msg_box_fct_args[1], "Critical")
                self.assertIn("Please report this problem under ", msg_box_fct_args[2])
                self.assertIn("Details of the error:\nType: {}\n\nMessage: {}\n\nTraceback:\n".format(err_name, err_value), msg_box_fct_args[3])
            else:
                # this must not create a messagebox if qt is not available!
                self.assertEqual(create_msg_box_mock.call_count, 0)

    def test_excepthook(self):
        """check if the exception hook is working properly
        see https://stackoverflow.com/a/46351418
        """
        proc = Popen([executable, str(Path('aux_files/excepthook_test.py'))], stdout=PIPE, stderr=PIPE, cwd=str(Path(__file__).parent))
        stdout, stderr = proc.communicate()
        self.assertEqual(proc.returncode, 1)
        print(stdout)
        # self.assertEqual(stdout, b'')
        self.assertIn(b'root : Unhandled exception', stderr)
        self.assertIn(b'Exception', stderr)
        self.assertIn(b'provocing error', stderr)


if __name__ == '__main__':
    unittest.main()
