#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import argparse
import sys

from pgsanity import sqlprep
from pgsanity import ecpg

def get_config(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Check syntax of SQL for PostgreSQL')
    parser.add_argument('--add-semicolon', action='store_true')
    parser.add_argument('files', nargs='*', default=None)
    return parser.parse_args(argv)

def check_file(filename=None, show_filename=False, add_semicolon=False):
    """
    Check whether an input file is valid PostgreSQL. If no filename is
    passed, STDIN is checked.

    Returns a status code: 0 if the input is valid, 1 if invalid.
    """
    # either work with sys.stdin or open the file
    if filename is not None:
        with open(filename, "r") as filelike:
            sql_string = filelike.read()
    else:
        with sys.stdin as filelike:
            sql_string = sys.stdin.read()

    success, msg = check_string(sql_string, add_semicolon=add_semicolon)

    # report results
    result = 0
    if not success:
        # possibly show the filename with the error message
        prefix = ""
        if show_filename and filename is not None:
            prefix = filename + ": "
        print(prefix + msg)
        result = 1

    return result

def check_string(sql_string, add_semicolon=False):
    """
    Check whether a string is valid PostgreSQL. Returns a boolean
    indicating validity and a message from ecpg, which will be an
    empty string if the input was valid, or a description of the
    problem otherwise.
    """
    prepped_sql = sqlprep.prepare_sql(sql_string, add_semicolon=add_semicolon)
    success, msg = ecpg.check_syntax(prepped_sql)
    return success, msg

def check_files(files, add_semicolon=False):
    if files is None or len(files) == 0:
        return check_file(add_semicolon=add_semicolon)
    else:
        # show filenames if > 1 file was passed as a parameter
        show_filenames = (len(files) > 1)

        accumulator = 0
        for filename in files:
            accumulator |= check_file(filename, show_filenames, add_semicolon=add_semicolon)
        return accumulator

def main():
    config = get_config()
    return check_files(config.files, add_semicolon=config.add_semicolon)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
