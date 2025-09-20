import os
import re
import subprocess


def check_syntax(string):
    """Check syntax of a string of PostgreSQL-dialect SQL"""
    args = ["ecpg", "-o", "-", "-"]

    with open(os.devnull, "w") as devnull:
        try:
            proc = subprocess.Popen(
                args,
                shell=False,
                stdout=devnull,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            _, err = proc.communicate(string)
        except OSError as err:
            msg = "Unable to execute 'ecpg', you likely need to install it.'"
            raise OSError(msg) from err
        if proc.returncode == 0:
            return (True, "")
        else:
            return (False, parse_error(err))


def parse_error(error):
    error = re.sub(r"^[^:]+:", "line ", error, count=1)
    error = re.sub(r"\/\/", "--", error)
    return error.strip()
