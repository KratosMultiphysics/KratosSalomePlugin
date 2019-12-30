import unittest
import sys, os

if __name__ == '__main__':
    verbosity = 0
    if len(sys.argv) == 2: # verbosity lvl was passed
        verbosity = int(sys.argv[1])
    loader = unittest.TestLoader()
    tests = loader.discover(os.path.dirname(__file__)) # automatically discover all tests in this directory
    testRunner = unittest.runner.TextTestRunner(verbosity=verbosity)
    result = testRunner.run(tests).wasSuccessful()
    sys.exit(not result) # retuning inverse bcs for sys.exit 1 aka true means error