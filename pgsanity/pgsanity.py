#!/usr/bin/env python

from __future__ import print_function
import argparse
import sys
import os

import sqlprep
import ecpg

def main():
    #parse args
    parser = argparse.ArgumentParser(description='Check sanity of PostgreSQL SQL')
    parser.add_argument('file', nargs='?', default=None)
    args = parser.parse_args()

    #prep sql file for checking
    fdin = sys.stdin
    if args.file is not None:
        fdin = open(args.file, "r")
    prepped_file = sqlprep.prep_file(fdin)
    fdin.close()

    #check syntax
    (success, msg) = ecpg.check_syntax(prepped_file)
    os.remove(prepped_file)

    #report results
    if success:
        return 0
    else:
        print(msg)
        return 1

if __name__ == '__main__':
    sys.exit(main())
