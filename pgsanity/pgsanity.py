#!/usr/bin/env python

from __future__ import print_function
import argparse
import sys
import os

import sqlprep
import ecpg

def get_config(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Check syntax of SQL for PostgreSQL')
    parser.add_argument('files', nargs='*', default=None)
    return parser.parse_args(argv)

def check_syntax(prepped_file):
    #check syntax
    (success, msg) = ecpg.check_syntax(prepped_file)

    #report results
    if success:
        return 0
    else:
        print(msg)
        return 1

def main():
    config = get_config()

    if config.files is None or len(config.files) == 0:
        #handle stdin
        prepped_file = sqlprep.prep_file(sys.stdin)
        result = check_syntax(prepped_file)
        os.remove(prepped_file)
        return result
    else:
        accumulator = 0
        for filename in config.files:
            fdin = open(filename, "r")
            prepped_file = sqlprep.prep_file(fdin)
            fdin.close()
            accumulator |= check_syntax(prepped_file)
            os.remove(prepped_file)
        return accumulator

if __name__ == '__main__':
    sys.exit(main())
