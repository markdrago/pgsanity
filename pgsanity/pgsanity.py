#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
from chardet import detect
from codecs import BOM_UTF8
import argparse
import sys

from pgsanity import sqlprep
from pgsanity import ecpg

def get_config(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Check syntax of SQL for PostgreSQL')
    parser.add_argument('files', nargs='*', default=None)
    return parser.parse_args(argv)

def check_for_bom(starting_bytes):
    """ Check the first few bytes of a file to determine whether input
    contains a BOM-table or not.

    Returns a boolean indicating whether a BOM-table appears to be present.
    """
    minlen = len(BOM_UTF8)
    if len(starting_bytes) < minlen:
        raise ValueError("Starting bytes of file must be at least"
                         " {} bytes long to check for BOM.".format(minlen))
    encoding = detect(starting_bytes)["encoding"]
    is_utf8 = encoding in ["UTF-8","UTF-8-SIG"]
    return is_utf8 and starting_bytes.startswith(BOM_UTF8)
    # ^ The above is a tiny bit redundant given that 'UTF-8-SIG' simply means
    # "UTF-8 file with a BOM-table". However, older versions of chardet don't
    # support this, and will just detect 'UTF-8', leaving us to check for the
    # BOM ourselves as we do above. The extra check is not harmful on
    # systems that have a more recent chardet module.

def check_file(filename=None, show_filename=False):
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
    # check for BOM-table and discard if present
    nose = sql_string[0:len(BOM_UTF8)]
    bom_present = check_for_bom(nose)
    sql_string = sql_string[len(nose):] if bom_present else sql_string
    success, msg = check_string(sql_string.decode("utf-8"))
    # ^ The above call to decode() is safe for both ASCII and UTF-8 data.

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

def check_string(sql_string):
    """
    Check whether a string is valid PostgreSQL. Returns a boolean
    indicating validity and a message from ecpg, which will be an
    empty string if the input was valid, or a description of the
    problem otherwise.
    """
    prepped_sql = sqlprep.prepare_sql(sql_string)
    success, msg = ecpg.check_syntax(prepped_sql)
    return success, msg

def check_files(files):
    if files is None or len(files) == 0:
        return check_file()
    else:
        # show filenames if > 1 file was passed as a parameter
        show_filenames = (len(files) > 1)

        accumulator = 0
        for filename in files:
            accumulator |= check_file(filename, show_filenames)
        return accumulator

def main():
    config = get_config()
    return check_files(config.files)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
