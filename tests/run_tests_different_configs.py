#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher
#

from __future__ import print_function

"""
This script is used to execute ALL tests (located in test_Plugin.py)
In multiple environments (e.g. python2, python3, salome)
"""
import subprocess, sys, os, time

### Auxiliary functions for testing ###
def RunTests(cmd_list, name, success_checker_fct):
    print(("Running tests with {}: ").format(name), end="")
    out_file_name = ("test_output_{}.txt").format(name)
    start_time = time.time()
    with open(out_file_name, "w") as out:
        sp = subprocess.Popen(cmd_list, stdout=out, stderr=out)
        sp.communicate()

    tests_successful = success_checker_fct(sp, out_file_name)

    if tests_successful:
        print(("\tOK\tin {} seconds").format(round(time.time() - start_time, 2)))
    else:
        print(("\tFAILED\tin {} seconds").format(round(time.time() - start_time, 2)))

    if verbosity == "2" or not tests_successful:
        for line in open(out_file_name).readlines():
            print(line, end="")

    if tests_successful:
        os.remove(out_file_name)

    return tests_successful

def SuccessCheckerPython(subproc, out_file_name):
    return not subproc.returncode

def SuccessCheckerSalome(subproc, out_file_name):
    return 'FAILED' not in open(out_file_name).read()

### running the tests in different environments ###
testing_file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_Plugin.py")

verbosity = "0"
if "-v" in sys.argv[1:] or "--verbose" in sys.argv[1:]:
    verbosity = "2"

all_tests_successful = True

all_tests_successful &= RunTests(["python2", testing_file_name, verbosity], "python2", SuccessCheckerPython)
if verbosity == "2":
    print("\n\n")

all_tests_successful &= RunTests(["python3", testing_file_name, verbosity], "python3", SuccessCheckerPython)
if verbosity == "2":
    print("\n\n")

all_tests_successful &= RunTests(["/bin/bash", "-i", "-c", "salome93 -t python " + testing_file_name + " args:"+verbosity], "salome", SuccessCheckerSalome)

sys.exit(not all_tests_successful) # inverting bcs 0 means everything is ok

#TODO maybe make the path-stuff for salome, aliases are not always available