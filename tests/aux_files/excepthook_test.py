"""auxiliry file to check if the exceptionhook is configured properly
used in test_logging.py TestExceptionLogging.test_excepthook
"""

import kratos_salome_plugin

raise Exception("provocing error")