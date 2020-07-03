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
from unittest.mock import MagicMock

# plugin imports
from kratos_salome_plugin.gui.plugin_main_window import PluginMainWindow

# tests imports
from testing_utilities import QtTestCase

# qt imports
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

class TestPluginMainWindow(QtTestCase):

    def test_Shortcuts(self):
        main_window = PluginMainWindow()
        mock_menubar_file_new = MagicMock(side_effect=lambda x:print("   >>> New"))
        mock_menubar_file_open = MagicMock()
        mock_menubar_file_save = MagicMock()
        mock_menubar_file_save_as = MagicMock()
        mock_menubar_file_close = MagicMock(side_effect=lambda x:print("   >>> HELLO"))
        mock_menubar_kratos_groups = MagicMock()

        main_window.actionNew.triggered.connect(mock_menubar_file_new)
        main_window.actionOpen.triggered.connect(mock_menubar_file_open)
        main_window.actionSave.triggered.connect(mock_menubar_file_save)
        main_window.actionSave_As.triggered.connect(mock_menubar_file_save_as)
        main_window.actionClose.triggered.connect(mock_menubar_file_close)
        main_window.actionGroups.triggered.connect(mock_menubar_kratos_groups)

        main_window.show()
        QTest.qWaitForWindowExposed(main_window)

        QTest.keyClick(main_window, Qt.Key_Escape)
        QTest.keyClicks(main_window, "q", Qt.ControlModifier)

        self.assertTrue(mock_menubar_file_close.called)
        self.assertEqual(mock_menubar_file_close.call_count, 2)


        # QTest.keyClicks(main_window, "Ctrl+N")
        QTest.keyClicks(main_window, "n", Qt.ControlModifier)
        self.assertEqual(mock_menubar_file_new.call_count, 1)


if __name__ == '__main__':
    unittest.main()
