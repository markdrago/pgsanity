import tempfile
import re

def prep_file(fdin):
    """prepare sql in a named file, return temp filename with prepared sql"""
    sqlin = fdin.read()
    clean_sql = prepare_sql(sqlin)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pgc") as dst:
        dst.write(clean_sql)
    return dst.name

def prepare_sql(sql):
    results = ""

    in_statement = False
    in_comment = False
    for (start, end, contents) in split_sql(sql):
        precontents = None
        start_str = None

        #decide where we are
        if not in_statement and not in_comment:
            #not currently in any block
            if start != "--" and len(contents.strip()) > 0:
                #not starting a comment and there is contents
                in_statement = True
                precontents = "EXEC SQL "

        if start == "--":
            in_comment = True
            if not in_statement:
                start_str = "//"

        start_str = start_str or start or ""
        precontents = precontents or ""
        results += start_str + precontents + contents

        if not in_comment and in_statement and end == ";":
            in_statement = False

        if in_comment and end == "\n":
            in_comment = False

    return results

def split_sql(sql):
    """generate hunks of SQL that are between the bookends
       return: tuple of beginning bookend, closing bookend, and contents
         note: beginning & end of string are returned as None"""
    bookends = ("\n", ";", "--")
    last_bookend_found = None
    start = 0

    while start <= len(sql):
        results = get_next_occurence(sql[start:], bookends)
        if results is None:
            yield (last_bookend_found, None, sql[start:])
            start = len(sql) + 1
        else:
            (index, bookend) = results
            end = start + index
            yield (last_bookend_found, bookend, sql[start:end])
            start = end + len(bookend)
            last_bookend_found = bookend

def get_next_occurence(haystack, needles):
    """find next occurence of one of the needles in the haystack
       return: tuple of (index, needle found)
           or: None if no needle was found"""
    min_index = None
    min_needle = None
    for needle in needles:
        index = haystack.find(needle)
        if index != -1:
            if min_index is None or index < min_index:
                min_index = index
                min_needle = needle
    if min_index is not None:
        return (min_index, min_needle)
    return None
