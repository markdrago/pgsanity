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

def remove_bom_if_exists(sql_string):
    """ Take the entire SQL-payload of a file (or stream) and strip the BOM-table
    if one was detected, returning it along with the detected encoding.

    sql_string   --   string-representation of incoming character-data. Value
                      should be passed RAW, meaning BEFORE regular decoding take
                      place. Otherwise, BOM-detection may fail. 

    Returns a BOM-free SQL-payload.
    """
    encoding = detect(sql_string[:10000])["encoding"] # HACK
    is_utf8 = encoding in ["UTF-8","UTF-8-SIG"] # *
    bom_present = is_utf8 and sql_string.startswith(BOM_UTF8) # *
    sql_string = sql_string[len(BOM_UTF8):] if bom_present else sql_string
    return sql_string, encoding
    # * The marked lines above are a tiny bit redundant given that 'UTF-8-SIG'
    # simply means "UTF-8 file with a BOM-table". However, older versions of
    # chardet don't support this, and will just detect 'UTF-8', leaving us to
    # check for the BOM ourselves as we do above. The extra check is not
    # harmful on systems that have a more recent chardet module.

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
    sql_string, encoding = remove_bom_if_exists(sql_string)
    success, msg = check_string(sql_string.decode(encoding))

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
