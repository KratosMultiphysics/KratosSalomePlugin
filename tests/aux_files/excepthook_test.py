"""auxiliary file to check if the exceptionhook is configured properly
used in test_logging.py
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

plugin_path = Path(__file__+"/../../..")
sys.path.append(str(plugin_path.resolve()))

with patch.dict(os.environ):
    # logs must be shown for the test to work!
    if 'KRATOS_SALOME_PLUGIN_DISABLE_LOGGING' in os.environ:
        del os.environ['KRATOS_SALOME_PLUGIN_DISABLE_LOGGING']
    if 'SALOMEPATH' in os.environ:
        del os.environ['SALOMEPATH']
    import kratos_salome_plugin

raise Exception("provocing error")

# this should not be executed as execution should stop after the first exception!
raise RuntimeError("This should not show up in the log!")
