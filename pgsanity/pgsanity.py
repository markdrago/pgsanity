#!/usr/bin/env python

from __future__ import print_function
import argparse
import tempfile
import sys
import os

import sqlprep
import ecpg

def get_config(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Check syntax of SQL for PostgreSQL')
    parser.add_argument('files', nargs='*', default=None)
    return parser.parse_args(argv)

def prep_file(filelike):
    """read in sql, prepare it, save prepped sql to temp file
       return: name of temp file which contains prepped sql"""
    raw_sql = filelike.read()
    prepped_sql = sqlprep.prepare_sql(raw_sql)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pgc") as dst:
        dst.write(prepped_sql)
    return dst.name

def check_file(filename=None, show_filename=False):
    #either work with sys.stdin or open the file
    filelike = sys.stdin
    if filename is not None:
        filelike = open(filename, "r")

    #prep the sql, store it in a temp file
    prepped_file = prep_file(filelike)
    filelike.close()

    #actually check the syntax of the prepped file
    (success, msg) = ecpg.check_syntax(prepped_file)

    #report results
    result = 0
    if not success:
        #possibly show the filename with the error message
        prefix = ""
        if show_filename and filename is not None:
            prefix = filename + ": "
        print(prefix + msg)
        result = 1

    #remove the temp file that contained the prepped sql
    os.remove(prepped_file)

    return result

def check_files(files):
    if files is None or len(files) == 0:
        return check_file()
    else:
        #show filenames if > 1 file was passed as a parameter
        show_filenames = (len(files) > 1)

        accumulator = 0
        for filename in files:
            accumulator |= check_file(filename, show_filenames)
        return accumulator

def main():
    config = get_config()
    return check_files(config.files)

if __name__ == '__main__':
    sys.exit(main())
