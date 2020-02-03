#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# Check to make sure the detection for if a script is run inside salome or not is working
import os, sys

# plugin imports
sys.path.append(os.pardir) # required to be able to do "from plugin import xxx"
from plugin.utilities.utils import IsExecutedInSalome

if len(sys.argv) == 2:
    salome_execution = bool(int(sys.argv[1]))
else:
    raise Exception("Input whether or not this scipt is executed in Salome has to be given!")

# detect wheter or not the script is run inside of Salome
run_in_salome = IsExecutedInSalome()

print("This script is executed in Salome:", salome_execution)
print("Detection for running in Salome returned:",   run_in_salome)

sys.exit(int(not(salome_execution == run_in_salome))) # int(True) is 1 which means failure, hence have to invert