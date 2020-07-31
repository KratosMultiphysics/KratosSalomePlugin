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
from unittest.mock import MagicMock, patch

# plugin imports
from kratos_salome_plugin.gui.plugin_main_window import PluginMainWindow

# tests imports
from testing_utilities import QtTestCase, skipUnlessPythonVersionIsAtLeast

# qt imports
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


class TestPluginMainWindowShortcuts(QtTestCase):
    """This test checks if the shortcuts are working correctly
    Useful reference: https://pytest-qt.readthedocs.io/en/1.3.0/
    testing shortcuts: https://stackoverflow.com/a/20751213
    NOTE: this test opens the PluginWindow
    set the environment variable "QT_QPA_PLATFORM" to "offscreen" to avoid this
    """

    @classmethod
    def setUpClass(cls):
        # doing this only once to save time (waiting for window to show takes time)
        # Mock objects are reset in "setUp"
        cls.main_window = PluginMainWindow()
        cls.mocks = {
            "file_new"      : MagicMock(),
            "file_open"     : MagicMock(),
            "file_save"     : MagicMock(),
            "file_save_as"  : MagicMock(),
            "file_close"    : MagicMock(),
            "kratos_groups" : MagicMock()
        }

        cls.main_window.actionNew.triggered.connect(cls.mocks["file_new"])
        cls.main_window.actionOpen.triggered.connect(cls.mocks["file_open"])
        cls.main_window.actionSave.triggered.connect(cls.mocks["file_save"])
        cls.main_window.actionSave_As.triggered.connect(cls.mocks["file_save_as"])
        cls.main_window.actionClose.triggered.connect(cls.mocks["file_close"])
        cls.main_window.actionGroups.triggered.connect(cls.mocks["kratos_groups"])

        # this is required for testing shortcuts
        # see https://stackoverflow.com/a/20751213
        cls.main_window.show()
        QTest.qWaitForWindowExposed(cls.main_window)

    def setUp(self):
        for mock in self.mocks.values():
            mock.reset_mock()


    def test_file_new(self):
        # Ctrl + n
        QTest.keyClicks(self.main_window, "n", Qt.ControlModifier)
        called_mock = "file_new"
        self.__CheckMockCalls(called_mock)

    def test_file_open(self):
        # Ctrl + o
        QTest.keyClicks(self.main_window, "o", Qt.ControlModifier)
        called_mock = "file_open"
        self.__CheckMockCalls(called_mock)

    def test_file_save(self):
        # Ctrl + s
        QTest.keyClicks(self.main_window, "s", Qt.ControlModifier)
        called_mock = "file_save"
        self.__CheckMockCalls(called_mock)

    def test_file_save_as(self):
        # Ctrl + Shift + s
        QTest.keyClicks(self.main_window, "s", Qt.ControlModifier|Qt.ShiftModifier)
        called_mock = "file_save_as"
        self.__CheckMockCalls(called_mock)

    def test_file_close(self):
        # Ctrl + q
        QTest.keyClicks(self.main_window, "q", Qt.ControlModifier)
        called_mock = "file_close"
        self.__CheckMockCalls(called_mock)

        # Esc
        QTest.keyClick(self.main_window, Qt.Key_Escape)
        called_mock = "file_close"
        self.__CheckMockCalls(called_mock,2)

    def test_kratos_groups(self):
        # Ctrl + g
        QTest.keyClicks(self.main_window, "g", Qt.ControlModifier)
        called_mock = "kratos_groups"
        self.__CheckMockCalls(called_mock)


    def __CheckMockCalls(self, called_mock, exp_call_count=1):
        # make sure that only the intended mock is called and not the other ones too
        # i.e. one shortcut should only trigger ONE operation
        self.assertEqual(self.mocks[called_mock].call_count, exp_call_count, msg='Mock "{}" was not called!'.format(called_mock))

        for mock_name in self.mocks:
            if mock_name == called_mock:
                continue
            self.assertFalse(self.mocks[mock_name].called, msg='Unexpected call for mock "{}": "{}"'.format(called_mock, mock_name))


class TestPluginMainWindowWindowStates(QtTestCase):
    """This test makes sure the window shows up again after being minimized"""
    def test_minimize(self):
        main_window = PluginMainWindow()
        self.assertTrue(main_window.isHidden())

        main_window.ShowOnTop()

        main_window.setWindowState(Qt.WindowMinimized)

        self.assertFalse(main_window.isActiveWindow())
        self.assertTrue(main_window.isMinimized())
        self.assertTrue(main_window.isVisible())
        self.assertFalse(main_window.isHidden())
        self.assertEqual(main_window.windowState(), Qt.WindowMinimized)

        main_window.ShowOnTop()

        # self.assertTrue(main_window.isActiveWindow()) # commented as doesn't work in the CI and in Linux, seems OS dependent
        self.assertFalse(main_window.isMinimized())
        self.assertTrue(main_window.isVisible())
        self.assertFalse(main_window.isHidden())
        self.assertEqual(main_window.windowState(), Qt.WindowNoState)

        main_window.close()

@skipUnlessPythonVersionIsAtLeast((3,6), 'Internally using f-strings')
class TestPluginMainWindowStatusBar(QtTestCase):
    def test_StatusBarInfo(self):
        main_window = PluginMainWindow()
        with patch.object(main_window, 'statusbar') as status_bar_patch:
            msg = "custom_message"
            main_window.StatusBarInfo(msg)
            self.assertEqual(status_bar_patch.showMessage.call_count, 1)
            self.assertEqual(len(status_bar_patch.showMessage.call_args[0]), 2)
            self.assertEqual(status_bar_patch.showMessage.call_args[0][0], msg)
            self.assertEqual(status_bar_patch.showMessage.call_args[0][1], 9000)

    def test_StatusBarWarning(self):
        main_window = PluginMainWindow()
        with patch.object(main_window, 'statusbar') as status_bar_patch:
            msg = "warn_message"
            main_window.StatusBarWarning(msg)
            self.assertEqual(status_bar_patch.showMessage.call_count, 1)
            self.assertEqual(len(status_bar_patch.showMessage.call_args[0]), 2)
            self.assertEqual(status_bar_patch.showMessage.call_args[0][0], msg)
            self.assertEqual(status_bar_patch.showMessage.call_args[0][1], 9000)


if __name__ == '__main__':
    unittest.main()
