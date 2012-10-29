import subprocess
import re
import os

def check_syntax(filename):
    args = ["ecpg", "-o", "-", filename]

    with open(os.devnull, "w") as devnull:
        proc = subprocess.Popen(args, shell=False,
                                stdout=devnull,
                                stderr=subprocess.PIPE)
        proc.wait()
        if proc.returncode == 0:
            return (True, "")
        else:
            err = proc.stderr.readline()
            return (False, parse_error(err))

def parse_error(error):
    error = re.sub(r'^[^:]+:', 'line ', error, count=1)
    error = re.sub(r'\/\/', '--', error)
    return error.strip()
