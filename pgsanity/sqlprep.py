import re
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

def prepare_sql(sql):
    results = StringIO()

    for current_sql_expression in split_sql(sql):
        assert(current_sql_expression[-1] == ';')
        results.write("EXEC SQL " + current_sql_expression)

    response = results.getvalue()
    results.close()
    return response

def get_processing_state(current_state, current_char):
    """determine the current state of processing an SQL-string.
    return: state symbol.

    States:

        _    --    the base state wherein SQL tokens, commands, and math and
                   other operators occur. This is the initial processesing state
                   in which the machine starts off

        /*p  --    block-comment pre-entry state. Identical to the "_" state
                   except that '*' initiates entry of a block comment

        /*   --    block-comment state. In block-comments, no SQL actually
                   occurs, meaning special characters like quotes and semicolons
                   have no effect

        /*2  --    block-comment pre-exit state. Identical to the "/*" state
                   except that '/' causes the current block-comment to be closed

        $$p  --    extended-string pre-entry state. Identical to the base state
                   except that '$' initiates entry of an extended string

        $$   --    extended-string state. In extended strings, all characters
                   are interpreted as string-data, meaning SQL-commands,
                   operators, etc. have no effect

        $$2  --    extended-string pre-exit state. Identical to the extended-
                   string state except that '$' causes the current extended-
                   string to be closed

        --p  --    line-comment pre-entry state. identical to the base state,
                   except that '-' initiates a line-comment

        --   --    line-comment state. All characters are ignored and not
                   treated as SQL except for '\n', which is the only character
                   that prompts a transition out of this state

        ;    --    the final state which indicates a single, complete
                   SQL-statement has just been completed

        '    --    single-quote state. In this state, no characters are treated
                   as SQL. The only transition away is "'" followed by any
                   character other than "'"

        '2   --    single-quote pre-exit state. Identical to the single-quote
                   state except that encountering a character other than "'"
                   causes the current single-quoted string to be closed

        "    --    double-quote state. Similar in nature to the single-quote
                   state, except that possible transition away is intiated
                   by '"' instead of "'".

        "2   --    double-quote pre-exit state. Similar in nature to the single-
                   quote pre-exit state except that '"' prompts a return back to
                   the stable double-quote state, rather than "'"
    """
    transitions = {
        '_': {
            0: '_', '/' : '/*p', '-': '--p', '$': '$$p',
            "'": "'", '"': '"', ';': ';'
        },
        "'": {0: "'", "'": "'2"},
        '"': {0: '"', '"': '"2'},
        '--p': {0: '_', '-': '--', ';': ';'},
        '/*p': {0: '_', '*': '/*', ';': ';'},
        '$$p': {0: '_', '$': '$$', ';': ';'},
        '--':  {0: '--', '\n':'_'},
        '/*': {0: '/*', '*':'/*2'},
        '/*2': {0: '/*', '/':'_'},
        '$$':  {0: '$$', '$': '$$2'},
        '$$2': {0: '$$', '$': '_'},
        "'2":  {0: "_", "'": "'", ';': ';'},
        '"2':  {0: '_', '"': '"', ';': ';'}
    }
    # ^ Above, transitions[current_state][0] represents the transition to take
    # if no transition is explicitly defined for the passed-in symbol
    if current_state not in transitions:
        raise ValueError("Received an invalid state '{}'".format(current_state))
    if current_char in transitions[current_state]:
        return transitions[current_state][current_char]
    else:
        return transitions[current_state][0]

def split_sql(sql):
    """isolate complete SQL-statements from the passed-in string
       return: the SQL-statements from the passed-in string,
       separated into individual statements """
    if len(sql) == 0:
        raise ValueError("Input appears to be empty.")
    previous_state = '_'
    current_state = '_'
    current_sql_expression = ''
    for c in sql:
        previous_state = current_state
        current_state = get_processing_state(current_state,c)
        # disard everything except for newlines if in line-comment state
        current_sql_expression += c if ( current_state != '--'
                                         or c == "\n" ) else ''
##        print "Current char: {} new state: {}".format(repr(c),current_state)
        if current_state == ';':
            yield current_sql_expression
            current_sql_expression = ''
            current_state = '_'
        elif ( previous_state == '--p' and current_state == '--' ):
        # if previous character was the start of a line-comment token, discard
            current_sql_expression = current_sql_expression[:-1]
    if current_sql_expression and not re.match("[\s;]*",current_sql_expression):
    # unless only whitespace and semicolons left, return remaining characters
    # between last ; and EOF
        yield current_sql_expression + ';'

def get_next_occurence(haystack, offset, needles):
    """find next occurence of one of the needles in the haystack
       return: tuple of (index, needle found)
           or: None if no needle was found"""
    # make map of first char to full needle (only works if all needles
    # have different first characters)
    firstcharmap = dict([(n[0], n) for n in needles])
    firstchars = firstcharmap.keys()
    while offset < len(haystack):
        if haystack[offset] in firstchars:
            possible_needle = firstcharmap[haystack[offset]]
            if haystack[offset:offset + len(possible_needle)] == possible_needle:
                return (offset, possible_needle)
        offset += 1
    return None
