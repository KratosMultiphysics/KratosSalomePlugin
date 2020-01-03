#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher
#

import subprocess, time

check this: https://stackoverflow.com/a/59041010 !!!

def ExecuteSalome(script_name, salome_cmd="salome", salome_arguments=[], print_output=True, print_timing=True):
    if print_timing:
        start_time = time.time()
    if not salome_script_name.endswith(".py"):
        salome_script_name += ".py"

    salome_cmd += " --shutdown-servers=1 -t"
    salome_args = "args:" + ", ".join([str(arg) for arg in salome_arguments])
    salome_exe =  " ".join([salome_cmd, salome_script_name, salome_args])

    out_file_name = 'salome_out_'+script_name
    err_file_name = 'salome_err_'+script_name

    open(out_file_name, 'w').close()
    open(err_file_name, 'w').close()

    with open(out_file_name, 'w') as salome_out, open(err_file_name, 'w') as salome_err:
        sp = subprocess.Popen(["/bin/bash", "-i", "-c", salome_exe], stdout=salome_out, stderr=salome_err)
        sp.communicate()

    if print_timing:
        exe_time = time.time() - start_time
        print('Executing SALOME with "' + salome_script_name + '" took ' + str(round(exe_time, 2)) + ' sec')

    with open(out_file_name, 'r') as out_file:
        out = out_file.readlines()
    with open(err_file_name, 'r') as err_file:
        err = out_file.readlines()

    return out, err, return_code
