#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher
#

# python imports
import sys
import subprocess

if __name__ == '__main__':
    verbosity = 0
    if len(sys.argv) == 3:
        salome_cmd  = str(sys.argv[1])
        script_name = str(sys.argv[2])
    elif len(sys.argv) == 4: # verbosity lvl was passed
        salome_cmd  = str(sys.argv[1])
        script_name = str(sys.argv[2])
        verbosity   = int(sys.argv[3])
    else:
        raise Exception("Wrong number of arguments!")

    sp = subprocess.Popen(salome_cmd + " --shutdown-servers=1 -t " + script_name, shell=True, stderr=subprocess.PIPE)
    _, process_stderr = sp.communicate()

    print("ERROR?", "ERROR:salomeContext:SystemExit 1 in method _runAppli" in process_stderr.decode('ascii'))
    print("return code:", sp.returncode != 0)
    # salome < 8.5 does not return the correct return code, hence also check for error message
    ret_code = sp.returncode != 0 or "ERROR:salomeContext:SystemExit 1 in method _runAppli" in process_stderr.decode('ascii')
    if ret_code:
        print(process_stderr.decode('ascii'))
    sys.exit(ret_code)