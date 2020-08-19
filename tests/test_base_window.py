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
from kratos_salome_plugin.gui.base_window import BaseWindow
import kratos_salome_plugin.gui.active_window as active_window

# tests imports
from testing_utilities import QtTestCase, GetTestsPath

# qt imports
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

ui_file = GetTestsPath() / "aux_files" / "base_main_window_test.ui"


class TestBaseWindowShortcuts(QtTestCase):
    """This test checks if the shortcuts are working correctly
    Useful reference: https://pytest-qt.readthedocs.io/en/1.3.0/
    testing shortcuts: https://stackoverflow.com/a/20751213
    NOTE: this test opens the PluginWindow
    set the environment variable "QT_QPA_PLATFORM" to "offscreen" to avoid this
    """

    @classmethod
    def setUpClass(cls):
        # doing this only once to save time (waiting for window to show takes time)
        cls.window = BaseWindow(ui_file)

        # this is required for testing shortcuts
        # see https://stackoverflow.com/a/20751213
        cls.window.show()
        QTest.qWaitForWindowExposed(cls.window)

    def test_close_ctrl_q(self):
        # Ctrl + q
        with patch.object(self.window, 'close') as path_close_event:
            QTest.keyClicks(self.window, "q", Qt.ControlModifier)
            self.assertEqual(path_close_event.call_count, 1)

    def test_close_esc(self):
        # Esc
        with patch.object(self.window, 'close') as path_close_event:
            QTest.keyClick(self.window, Qt.Key_Escape)
            self.assertEqual(path_close_event.call_count, 1)


class TestBaseWindowWindowStates(QtTestCase):
    """This test makes sure the window shows up again after being minimized"""
    def test_minimize(self):
        window = BaseWindow(ui_file)
        self.assertTrue(window.isHidden())

        window.ShowOnTop()

        window.setWindowState(Qt.WindowMinimized)

        self.assertFalse(window.isActiveWindow())
        self.assertTrue(window.isMinimized())
        self.assertTrue(window.isVisible())
        self.assertFalse(window.isHidden())
        self.assertEqual(window.windowState(), Qt.WindowMinimized)

        window.ShowOnTop()

        # self.assertTrue(window.isActiveWindow()) # commented as doesn't work in the CI and in Linux, seems OS dependent
        self.assertFalse(window.isMinimized())
        self.assertTrue(window.isVisible())
        self.assertFalse(window.isHidden())
        self.assertEqual(window.windowState(), Qt.WindowNoState)

        window.close()


class TestBaseWindowStatusBar(QtTestCase):
    def test_StatusBarInfo(self):
        window = BaseWindow(ui_file)
        with patch.object(window, 'statusbar') as status_bar_patch:
            msg = "custom_message"
            window.StatusBarInfo(msg)
            self.assertEqual(status_bar_patch.showMessage.call_count, 1)
            self.assertEqual(len(status_bar_patch.showMessage.call_args[0]), 2)
            self.assertEqual(status_bar_patch.showMessage.call_args[0][0], msg)
            self.assertEqual(status_bar_patch.showMessage.call_args[0][1], 9000)

    def test_StatusBarWarning(self):
        window = BaseWindow(ui_file)
        with patch.object(window, 'statusbar') as status_bar_patch:
            msg = "warn_message"
            window.StatusBarWarning(msg)
            self.assertEqual(status_bar_patch.showMessage.call_count, 1)
            self.assertEqual(len(status_bar_patch.showMessage.call_args[0]), 2)
            self.assertEqual(status_bar_patch.showMessage.call_args[0][0], msg)
            self.assertEqual(status_bar_patch.showMessage.call_args[0][1], 9000)


class TestBaseWindowHideParent(QtTestCase):
    def test_hide_show_parent(self):
        parent_window = BaseWindow(ui_file)
        parent_window.show()
        self.assertTrue(parent_window.isVisible())

        window = BaseWindow(ui_file, parent_window)
        self.assertFalse(parent_window.isVisible())

        window.close()
        self.assertTrue(parent_window.isVisible())


class TestBaseWindowMinimize_ActiveWindow(QtTestCase):
    def setUp(self):
        # setting initial state
        active_window.ACTIVE_WINDOW = None

    def test_set_active_window(self):
        window = BaseWindow(ui_file)
        window.show()

        window.setWindowState(Qt.WindowMinimized)

        self.assertIs(active_window.ACTIVE_WINDOW, window)

    def test_set_active_window_parent(self):
        parent_window = BaseWindow(ui_file)
        parent_window.show()

        window = BaseWindow(ui_file, parent_window)

        window.show()

        self.assertIs(active_window.ACTIVE_WINDOW, window)

    def test_set_active_window_reset(self):
        parent_window = BaseWindow(ui_file)
        parent_window.show()

        window = BaseWindow(ui_file, parent_window)

        window.show()
        window.close()

        self.assertIs(active_window.ACTIVE_WINDOW, parent_window)


if __name__ == '__main__':
    unittest.main()
