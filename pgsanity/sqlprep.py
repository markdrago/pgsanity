import tempfile
import re

def prep_file(fdin):
    """prepare sql in a named file, return temp filename with prepared sql"""
    sqlin = fdin.read()
    clean_sql = get_clean_sql(sqlin)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pgc") as dst:
        dst.write(clean_sql)
    return dst.name

def get_clean_sql(sql):
    return handle_sql_comments(add_exec_sql_statements(sql))

def handle_sql_comments(sql):
    return re.sub(r'\-\-', '//', sql)

def add_exec_sql_statements(sql):
    result_lines = []
    waiting_for_semi = False
    for line in sql.split("\n"):
        if not line_has_sql(line):
            #line has no sql, just add it
            result_lines.append(line)
            continue

        if not waiting_for_semi:
            #line has sql, not waiting for semi, must be new statement
            result_lines.append("EXEC SQL " + deal_with_inline_semicolons(line))
            if not line_has_trailing_semicolon(line):
                waiting_for_semi = True
        else:
            #line has sql, waiting for semi
            if line_has_valid_semicolon(line):
               #waiting for semi and we found one
                waiting_for_semi = False

                #check for multiple statements per line
                line = deal_with_inline_semicolons(line)
                result_lines.append(line)
            else:
                 #waiting for semi and this line has none, just add
                result_lines.append(line)
    return "\n".join(result_lines)

def deal_with_inline_semicolons(line):
    start = 0
    while (line.find(";", start) > -1):
        post_semi = line.find(";", start) + 1
        if not line_has_sql(line, post_semi):
            break
        else:
            #drop an EXEC SQL in just after the semicolon
            line = line[start:post_semi] + "EXEC SQL " + line[post_semi:]
            start = post_semi
    return line

def line_has_trailing_semicolon(line):
    return line.rstrip().endswith(";")

def line_has_valid_semicolon(line):
    """return true if a semicolon is found before a comment starts"""
    if ";" in line:
        if "--" in line:
            return line.find(";") < line.find("--")
        else:
            return True
    else:
        return False

def line_has_sql(line, start=0):
    """return true if line is not entirely whitespace and/or comment
       start parameter specifies where to start checking the string"""
    clean = line[start:].strip()
    return len(clean) != 0 and not clean.startswith("--")
