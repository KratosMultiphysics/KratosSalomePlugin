#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

"""
this file sets up the testing environment and should be the first import in every testing file
NOTE: This file must NOT have dependencies on other files in the plugin!
Especially since it initializes the salome environment during testing!
"""

# python imports
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.pardir) # needed to bring the plugin into the path, e.g. make "import kratos_salome_plugin" possible
os.environ["KRATOS_SALOME_PLUGIN_DISABLE_LOGGING"] = "1" # this disables all logging, see "kratos_salome_plugin.plugin_logging"

def __IsExecutedInSalome():
    """Function to check if the script is being executed inside Salome
    NOTE: This is a copy of kratos_salome_plugin.utilities : IsExecutedInSalome
    Reason is that this file cannot contain imports from the plugin because
    it initializes the environment for salome
    """
    return "SALOMEPATH" in os.environ

def __CheckIfKPyQtAvailable():
    if "PYQT_AVAILABLE" in os.environ:
        # this is intended to be used in the CI
        # there "try-except" might lead to an undiscovered failure
        return (os.environ["PYQT_AVAILABLE"] == "1")
    else:
        try:
            import PyQt5.QtCore
            import PyQt5.QtGui
            import PyQt5.QtTest
            return True
        except:
            return False


# variables to be used in testing
IS_EXECUTED_IN_SALOME = __IsExecutedInSalome()
PYQT_AVAILABLE = __CheckIfKPyQtAvailable()

# the plugin uses (non-standard) modules from Salome and PyQt
# if a module is not available, then mocking it to avoid having to
# check each time before importing it
# If a function from such a module is used it has to be patched
# Note that all modules that are used in the plugin have to be mocked
# see https://turlucode.com/mock-python-imports-in-unit-tests/

if IS_EXECUTED_IN_SALOME:
    # Check https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html for how to handle study
    import salome

    # initialize salome, should be done only once
    salome.salome_init()
else:
    sys.modules['salome'] = MagicMock()
    sys.modules['salome_version'] = MagicMock()
    sys.modules['GEOM'] = MagicMock()
    sys.modules['salome.geom'] = MagicMock()
    sys.modules['SMESH'] = MagicMock()
    sys.modules['salome.smesh'] = MagicMock()

if PYQT_AVAILABLE:
    from PyQt5.QtWidgets import QApplication
    py_qt_app = QApplication(sys.argv)
else:
    sys.modules['PyQt5'] = MagicMock()
    sys.modules['PyQt5.QtCore'] = MagicMock()
    sys.modules['PyQt5.QtGui'] = MagicMock()
    sys.modules['PyQt5.QtWidgets'] = MagicMock()
    sys.modules['PyQt5.QtTest'] = MagicMock()
