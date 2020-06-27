#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# this file sets up the testing environment and should be the first import in every testing file

# python imports
import sys
import os
from unittest.mock import Mock

sys.path.append(os.pardir) # needed to bring the plugin into the path, e.g. make "import kratos_salome_plugin" possible
os.environ["KRATOS_SALOME_PLUGIN_DISABLE_LOGGING"] = "1" # this disables all logging, see "kratos_salome_plugin.plugin_logging"

# plugin imports
from kratos_salome_plugin.utilities import IsExecutedInSalome

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
IS_EXECUTED_IN_SALOME = IsExecutedInSalome()
PYQT_AVAILABLE = __CheckIfKPyQtAvailable()

# the plugin uses (non-standard) modules from Salome and PyQt
# if a module is not available, then mocking it to avoid having to
# check each time before importing it
# If a function from such a module is used it has to be patched
# Note that all modules that are used in the plugin have to be mocked

if IS_EXECUTED_IN_SALOME:
    # Check https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html for how to handle study
    import salome

    # initialize salome, should be done only once
    salome.salome_init()
else:
    sys.modules['salome'] = Mock()
    sys.modules['salome_version'] = Mock()
    sys.modules['GEOM'] = Mock()
    sys.modules['salome.geom'] = Mock()
    sys.modules['SMESH'] = Mock()
    sys.modules['salome.smesh'] = Mock()

if PYQT_AVAILABLE:
    from PyQt5.QtWidgets import QApplication
    py_qt_app = QApplication(sys.argv)
    sys.exit(py_qt_app.exec_())
else:
    sys.modules['PyQt5.QtCore'] = Mock()
    sys.modules['PyQt5.QtGui'] = Mock()
    sys.modules['PyQt5.QtTest'] = Mock()
