"""auxiliary file to check if the logging of critical messages
in MessageBoxes works when running in Salome
Has to be tested in a separate process bcs the logging is disabled in the test
and hence the messagebox is not created
used in test_logging.py
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import salome
salome.salome_init()

plugin_path = Path(__file__+"/../../..")
sys.path.append(str(plugin_path.resolve()))

with patch.dict(os.environ):
    # logs must be shown for the test to work!
    if 'KRATOS_SALOME_PLUGIN_DISABLE_LOGGING' in os.environ:
        del os.environ['KRATOS_SALOME_PLUGIN_DISABLE_LOGGING']
    import kratos_salome_plugin

# import logger after the plugin
import logging
logger = logging.getLogger(__file__)

with patch('kratos_salome_plugin.plugin_logging.CreateInformativeMessageBox') as create_msg_box_mock:
    logger.critical("This is a test message")

    assert create_msg_box_mock.call_count == 1

    # checking arguments
    msg_box_fct_args = create_msg_box_mock.call_args_list[0][0]

    assert len(msg_box_fct_args) == 4
    assert msg_box_fct_args[0] == "Critical event occurred!"
    assert msg_box_fct_args[1] == "Critical"
    assert "Please report this problem under " in msg_box_fct_args[2]
    assert msg_box_fct_args[3] == "This is a test message"
