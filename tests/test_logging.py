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
from unittest.mock import patch, call, MagicMock
import logging

# plugin imports
from kratos_salome_plugin import IsExecutedInSalome
from kratos_salome_plugin import plugin_logging

# tests imports
from testing_utilities import QtTestCase

# qt imports
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


class TestLogging(unittest.TestCase):
    @patch('kratos_salome_plugin.plugin_logging.CreateInformativeMessageBox')
    def test_exceptions(self, create_msg_box_mock):
        """check if logging exceptions works properly"""
        self.assertTrue(hasattr(plugin_logging, 'CreateInformativeMessageBox'), msg="Import failed, seems like pyqt import wasn't working")

        with self.assertLogs(level="ERROR") as cm:
            try:
                1/0
            except ZeroDivisionError:
                plugin_logging._HandleUnhandledException(*exc_info())
                err_name = exc_info()[0].__name__
                err_value = str(exc_info()[1])

        with self.subTest("Testing exception logs"):
            self.assertEqual(len(cm.output), 1)
            self.assertIn('ERROR:KRATOS SALOME PLUGIN:Unhandled exception\nTraceback', cm.output[0])
            self.assertIn(err_name, cm.output[0])
            self.assertIn(err_value, cm.output[0])

        # in addition to checking if the exception loggin works also check if
        # showing the exception in the message box works
        with self.subTest("Testing exception message box"):
            # checking if function was called
            self.assertEqual(create_msg_box_mock.call_count, 1)

            # checking arguments
            msg_box_fct_args = create_msg_box_mock.call_args_list[0][0]
            self.assertEqual(len(msg_box_fct_args), 4)
            self.assertEqual(msg_box_fct_args[0], "An unhandled excepition occured!")
            self.assertEqual(msg_box_fct_args[1], "Critical")
            self.assertIn("Please report this problem under ", msg_box_fct_args[2])
            self.assertIn("Details of the error:\nType: {}\n\nMessage: {}\n\nTraceback:\n".format(err_name, err_value), msg_box_fct_args[3])

    @patch('kratos_salome_plugin.plugin_logging.CreateInformativeMessageBox')
    def test_MessageBoxLogHandler(self, create_msg_box_mock):
        handler = plugin_logging._MessageBoxLogHandler()
        record_mock = MagicMock(spec=logging.LogRecord)
        attrs = {'getMessage.return_value': "some message"}
        record_mock.configure_mock(**attrs)

        handler.emit(record_mock)

        self.assertEqual(create_msg_box_mock.call_count, 1)

        self.assertEqual(len(record_mock.mock_calls), 1)
        self.assertEqual(call.getMessage(), record_mock.mock_calls[0])

        msg_box_fct_args = create_msg_box_mock.call_args_list[0][0]

        self.assertEqual(len(msg_box_fct_args), 4)
        self.assertEqual(msg_box_fct_args[0], "Critical event occurred!")
        self.assertEqual(msg_box_fct_args[1], "Critical")
        self.assertIn("Please report this problem under ", msg_box_fct_args[2])
        self.assertEqual(msg_box_fct_args[3], "some message")

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

    @patch('kratos_salome_plugin.plugin_logging.CreateInformativeMessageBox')
    def test_show_critical_in_messagebox_in_salome(self, create_msg_box_mock):
        """test if critical logs are shown in message boxes when running in salome"""
        proc = Popen([executable, str(Path('aux_files/critical_in_msg_box_salome.py'))], stdout=PIPE, stderr=PIPE, cwd=str(Path(__file__).parent))
        stdout, stderr = proc.communicate()

        self.assertEqual(proc.returncode, 0)
        self.assertEqual(stdout, b'\n')
        self.assertIn(b'CRITICAL', stderr)
        self.assertIn(b'aux_files/critical_in_msg_box_salome.py', stderr)
        self.assertIn(b'This is a test message', stderr)


if __name__ == '__main__':
    unittest.main()
