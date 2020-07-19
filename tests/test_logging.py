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
from unittest.mock import patch, call

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
    @unittest.skipUnless(initialize_testing_environment.PYQT_AVAILABLE, "This test checks if the logging works if pyqt is available")
    @patch('kratos_salome_plugin.plugin_logging.CreateInformativeMessageBox')
    def test_exception_logging_pyqt_available(self, create_msg_box_mock):
        self.assertTrue(hasattr(plugin_logging, 'CreateInformativeMessageBox'))

        with self.assertLogs(level="ERROR") as cm:
            try:
                1/0
            except ZeroDivisionError:
                plugin_logging._HandleUnhandledException(*exc_info())
                err_name = exc_info()[0].__name__
                err_value = str(exc_info()[1])

        with self.subTest("Testing exception logs"):
            self.__execute_test_exception_logging(err_name, err_value, cm)

        # in addition to checking if the exception loggin works also check if
        # showing the exception in the message box works
        with self.subTest("Testing exception message box"):
            self.assertEqual(create_msg_box_mock.call_count, 1)
            self.assertEqual(len(create_msg_box_mock.mock_calls), 2, msg="'exec' method not called!")
            self.assertEqual(call().exec(), create_msg_box_mock.mock_calls[1], msg="'exec' method not called properly!")
            msg_box_fct_args = create_msg_box_mock.call_args_list[0][0]
            self.assertEqual(len(msg_box_fct_args), 4)
            self.assertEqual(msg_box_fct_args[0], "An unhandled excepition occured!")
            self.assertEqual(msg_box_fct_args[1], "Critical")
            self.assertIn("Please report this problem under ", msg_box_fct_args[2])
            self.assertIn("Details of the error:\nType: {}\n\nMessage: {}\n\nTraceback:\n".format(err_name, err_value), msg_box_fct_args[3])

    def test_excepthook(self):
        """check if the exception hook is working properly
        see https://stackoverflow.com/a/46351418
        """
        proc = Popen([executable, str(Path('aux_files/excepthook_test.py'))], stdout=PIPE, stderr=PIPE, cwd=str(Path(__file__).parent))
        stdout, stderr = proc.communicate()
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(stdout, b'')
        self.assertIn(b'KRATOS SALOME PLUGIN : Unhandled exception', stderr)
        self.assertIn(b'Exception', stderr)
        self.assertIn(b'provocing error', stderr)


    def __execute_test_exception_logging(self, err_name, err_value, logger_cm):
        self.assertEqual(len(logger_cm.output), 1)
        self.assertIn('ERROR:KRATOS SALOME PLUGIN:Unhandled exception\nTraceback', logger_cm.output[0])
        self.assertIn(err_name, logger_cm.output[0])
        self.assertIn(err_value, logger_cm.output[0])


if __name__ == '__main__':
    unittest.main()
