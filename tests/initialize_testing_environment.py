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
from unittest.mock import MagicMock

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


class _ModuleMock(object):
    """This class is used for mocking unavailable modules
    It issues proper errors and does not hide them like MagicMock would do
    if a non-patched method is called
    """
    def __init__(self, module_name):
        self.module_name = module_name

    def __getattr__(self, method_name):
        def method(*args):
            err_msg = 'Tried to call "{}" on mocked module "{}"'.format(method_name, self.module_name)
            if args:
                err_msg += '\nArguments: ' + str(args)
            err_msg += '\nSince it is not available it has to be patched in order to be used in a test!'
            err_msg += '\nHint: use "unittest.mock.patch"'
            raise Exception(err_msg)
        return method

def _MockModule(module_name):
    sys.modules[module_name] = _ModuleMock(module_name)

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
    _MockModule('salome')
    _MockModule('salome_version')
    _MockModule('GEOM')
    _MockModule('salome.geom')
    _MockModule('SMESH')
    _MockModule('salome.smesh')
    _MockModule('salome.smesh.smeshBuilder')

if PYQT_AVAILABLE:
    from PyQt5.QtWidgets import QApplication
    py_qt_app = QApplication(sys.argv)
else:
    _MockModule('PyQt5')
    _MockModule('PyQt5.QtCore')
    _MockModule('PyQt5.QtGui')
    _MockModule('PyQt5.QtWidgets')
    _MockModule('PyQt5.QtTest')
