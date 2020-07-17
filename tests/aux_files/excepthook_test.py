"""auxiliry file to check if the exceptionhook is configured properly
used in test_logging.py TestExceptionLogging.test_excepthook
"""

import os
import sys
from pathlib import Path

sys.path.append(Path(__file__).parent)

logging_disable_env_var = "KRATOS_SALOME_PLUGIN_DISABLE_LOGGING" # see "plugin_logging.py"

class LoggerEnvSetter(object):
    """Since here we explicitly test the logging, we have to enable it (temporarily)"""
    def __enter__(self):
        """enable logging (in case it was disabled)"""
        self.env_var_exists = logging_disable_env_var in os.environ
        if self.env_var_exists:
            self.orig_env_var_value = os.environ[logging_disable_env_var]
            os.environ[logging_disable_env_var] = "0"

    def __exit__(self, *exc_info):
        """disable logging (in case it was initially enabled)"""
        if self.env_var_exists:
            os.environ[logging_disable_env_var] = self.orig_env_var_value


with LoggerEnvSetter():
    import kratos_salome_plugin

raise Exception("provocing error")