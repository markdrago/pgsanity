## PgSanity

PgSanity checks the syntax of Postgresql SQL files.

It does this by leveraging the ecpg command which is traditionally
used for preparing C files with embedded sql for compilation.
However, as part of that preparation, ecpg checks the embedded SQL
statements for syntax errors using the exact same parser that is
in PostgreSQL.

So the approach that PgSanity takes is to take a file that has a
list of bare SQL in it, make that file look like a C file with
embedded SQL, run it through ecpg and let ecpg report on the syntax
errors of the SQL.

[![Build Status](https://travis-ci.org/markdrago/pgsanity.svg?branch=master)](https://travis-ci.org/markdrago/pgsanity)

## Installation
### Dependencies
- Python >= 2.7
    - May work with Python 2.6 if you install argparse (sudo pip install argparse)
    - If you need support for Python < 2.6 let me know
- ecpg
    - ubuntu/debian: sudo apt-get install libecpg-dev
    - rhel/centos: sudo yum install postgresql-devel
    - arch: sudo pacman -S postgresql-libs

### Getting PgSanity
PgSanity is available in the Python Package Index, so you can install it with either easy_install or pip.  Here's [PgSanity's page on PyPI](http://pypi.python.org/pypi/pgsanity).
- sudo pip install pgsanity **or** sudo easy_install pgsanity
    - If you don't have pip you can get it on ubuntu/debian by running: sudo apt-get install python-pip

## Usage
PgSanity accepts filenames as parameters and it will report SQL syntax errors which exist in those files.  PgSanity will exit with a status code of 0 if the syntax of the SQL looks good and a 1 if any errors were found.
 
    $ pgsanity file_with_sql.sql
    $ echo $?
    0
    $ pgsanity good1.sql good2.sql bad.sql
    bad.sql: line 1: ERROR: syntax error at or near "bogus_token"
    $ echo $?
    1
 
Since pgsanity can handle multiple filenames as parameters it is very comfortable to use with find & xargs.

    $ find -name '*.sql' | xargs pgsanity
    ./sql/bad1.sql: line 59: ERROR: syntax error at or near ";"
    ./sql/bad2.sql: line 41: ERROR: syntax error at or near "insert"
    ./sql/bad3.sql: line 57: ERROR: syntax error at or near "update"

Additionally PgSanity will read SQL from stdin if it is not given any parameters.  This way it can be used interactively or by piping SQL through it.
 
    $ pgsanity
    select column1 alias2 asdf from table3
    line 1: ERROR: syntax error at or near "asdf"
    $ echo $?
    1
    $ echo "select mycol from mytable;" | pgsanity
    $ echo $?
    0

## Interpreting The Results
The error messages pretty much come directly from ecpg.  Something I have noticed while using pgsanity is that an error message on line X is probably more indicative of the statement right above X.  For example:

    $ echo "select a from b\ninsert into mytable values (1, 2, 3);" | pgsanity
    line 2: ERROR: syntax error at or near "into"

The real problem in that SQL is that there is no semicolon after the 'b' in the select statement.  However, the SQL can not be determined to be invalid until the word "into" is encountered in the insert statement.  When in doubt, look up to the previous statement.

Another common error message that can be a little weird to interpret is illustrated here:

    echo "select a from b" | pgsanity 
    line 2: ERROR: syntax error at or near ""

The 'at or near ""' bit is trying to say that we got to the end of the file and no semicolon was found.

## Reporting Problems
If you encounter any problems with PgSanity, especially any issues where it incorrectly states that invalid SQL is valid or vice versa, please report the issue on [PgSanity's github page](http://github.com/markdrago/pgsanity).  Thanks!
