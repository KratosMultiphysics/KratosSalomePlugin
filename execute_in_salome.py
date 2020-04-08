#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# python imports
import sys
import subprocess
import time, datetime

if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise Exception("Too few arguments, at least the salome-command and the py-script to be executed have to be given!")

    info_msg  = 'Executing salome with the following configuration:\n'
    info_msg += '    \x1b[1;1mSalome-command:\x1b[0m {}\n'.format(sys.argv[1])
    info_msg += '    \x1b[1;1mPython-script:\x1b[0m  {}\n'.format(sys.argv[2])
    info_msg += '    \x1b[1;1mArguments:\x1b[0m      {}\n'.format(sys.argv[3:])
    print(info_msg)

    start_time = time.time()

    sp = subprocess.Popen("{} --shutdown-servers=1 -t {} args:{}".format(sys.argv[1], sys.argv[2], ", ".join([str(arg) for arg in sys.argv[3:]])), shell=True, stderr=subprocess.PIPE)
    _, process_stderr = sp.communicate()

    if process_stderr:
        print(process_stderr.decode('ascii'))

    # salome < 8.5 does not return the correct return code, hence also check for error message
    ret_code = sp.returncode != 0 or "ERROR:salomeContext:SystemExit 1 in method _runAppli" in process_stderr.decode('ascii')

    info_msg  = '\x1b[1;1mExecution took: {}'.format((str(datetime.timedelta(seconds=time.time()-start_time))).split(".")[0])
    info_msg += ' and finished ' + ('\x1b[1;41mnot successful\x1b[0m' if ret_code else '\x1b[1;42msuccessful\x1b[0m')

    print(info_msg)

    sys.exit(ret_code)
