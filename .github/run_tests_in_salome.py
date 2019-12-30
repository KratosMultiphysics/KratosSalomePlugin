import os, sys, subprocess

command = "/root/salome_dir/salome -t"
script = "tests/run_all_tests.py"

process = subprocess.Popen([
    command,
    script,
    ], stdout=subprocess.PIPE)

process_stdout, process_stderr = process.communicate()

if process_stdout:
    print(process_stdout.decode('ascii'), file=sys.stdout)
if process_stderr:
    print(process_stderr.decode('ascii'), file=sys.stderr)

exitCode = int(process.returncode != 0)

# some versions of salome (e.g. 8.3 & 8.4) don't have correct return codes, hence checking for error in log
# check is only done if no error was detected before
if exitCode == 0 and "ERROR:salomeContext:SystemExit" in process_stdout:
    print("Detected failure in log")
    exitCode = 1
