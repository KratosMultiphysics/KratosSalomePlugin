#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

"""
This file contains a wrapper for executing Salome in batch (aka without GUI) mode.
Features:
- passing command line arguments to Salome
- shut down all the Salome servers after the execution
- return the correct exit code (not working properly for older versions of Salome)

Rererences:
- https://stackoverflow.com/questions/13266480/running-salome-script-without-graphics
- https://www.salome-platform.org/forum/forum_10/680589823

NOTE: This file must NOT have dependencies on other files in the plugin!
TODO: Test/try to make this work also in Windows
"""

# python imports
import sys
import subprocess
import time, datetime

import locale
print(locale.getpreferredencoding())
print(locale.getdefaultlocale())

def Execute(salome_cmd, script_name, *args):
    info_msg  = 'Executing salome with the following configuration:\n'
    info_msg += '    \x1b[1;1mSalome-command:\x1b[0m {}\n'.format(salome_cmd)
    info_msg += '    \x1b[1;1mPython-script:\x1b[0m  {}\n'.format(script_name)
    info_msg += '    \x1b[1;1mArguments:\x1b[0m      {}\n'.format(args)
    print(info_msg)

    start_time = time.time()

    sp = subprocess.Popen("{} --shutdown-servers=1 -t {} args:{}".format(salome_cmd, script_name, ", ".join([str(arg) for arg in args])), shell=True, stderr=subprocess.PIPE)
    _, process_stderr = sp.communicate()

    import locale
    print(locale.getpreferredencoding())

    if process_stderr:
        print(process_stderr.decode(locale.getpreferredencoding()))

    # Salome < 8.5 does not return the correct return code, hence also check for error message
    ret_code = sp.returncode != 0 #or "ERROR:salomeContext:SystemExit 1 in method _runAppli" in process_stderr.decode('utf-8')

    info_msg  = '\x1b[1;1mExecution took: {}'.format((str(datetime.timedelta(seconds=time.time()-start_time))).split(".")[0])
    info_msg += ' and finished ' + ('\x1b[1;41mnot successful\x1b[0m' if ret_code else '\x1b[1;42msuccessful\x1b[0m')
    print(info_msg)

    return ret_code == 0 # 0 means successful execution


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise Exception("Too few arguments, at least the salome-command and the py-script to be executed have to be given!")

    salome_cmd = sys.argv[1]
    script_name = sys.argv[2]
    args = sys.argv[3:]

    successful_execution = Execute(salome_cmd, script_name, *args)

    sys.exit(not successful_execution) # 0 means exiting clean, but int(True) is 1, hence negating here
