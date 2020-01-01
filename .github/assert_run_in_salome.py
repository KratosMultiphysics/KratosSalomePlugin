# Check to make sure the detection for if a script is run inside salome or not is working
import os, sys

if len(sys.argv) == 2:
    salome_execution = bool(sys.argv[1])
else:
    raise Exception("Input whether or not this scipt is executed in Salome has to be given!")

# detect wheter or not the script is run inside of Salome
run_in_salome = ("SALOMEPATH" in os.environ)

print("This script is executed in Salome:", salome_execution)
print("Detection for running in Salome:",   run_in_salome)

sys.exit(int(not(salome_execution == run_in_salome))) # int(True) is 1 which means failure, hence have to invert