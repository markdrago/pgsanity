#!/bin/sh

#E302 = 2 newlines before functions & classes
find . -name '*.py' -exec pep8 --ignore=E302 --max-line-length=120 {} \;
