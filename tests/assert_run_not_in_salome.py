# Check to make sure the detection for if a script is run inside salome or not is working
import os, sys

run_in_salome = ("SALOMEPATH" in os.environ)
print("Running in Salome:", run_in_salome)
exit_code = int(not run_in_salome) # exit code of 0 means successful, but int(True) is 1, hence have to invert
sys.exit(exit_code)