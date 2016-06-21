import re
from collections import OrderedDict

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

def get_processing_state(current_state, current_token):
    """determine the current state of processing an SQL-string.
    return: state symbol.

    States:

        _    --    the base state wherein SQL tokens, commands, and math and
                   other operators occur. This is the initial processesing state
                   in which the machine starts off

        /*   --    block-comment state. In block-comments, no SQL actually
                   occurs, meaning special characters like quotes and semicolons
                   have no effect

        $$   --    extended-string state. In extended strings, all characters
                   are interpreted as string-data, meaning SQL-commands,
                   operators, etc. have no effect

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
            0: '_', '/*' : '/*', '--': '--', '$$': '$$',
            "'": "'", '"': '"', ';': ';'
        },
        "'": {0: "'", "'": "'2"},
        "'2":  {0: "_", "'": "'", ';': ';'},
        '"': {0: '"', '"': '"2'},
        '"2':  {0: '_', '"': '"', ';': ';'},
        '--':  {0: '--', '\n':'_'},
        '/*': {0: '/*', '*/':'_'},
        '$$':  {0: '$$', '$$': '_'},
    }
    # ^ Above, transitions[current_state][0] represents the transition to take
    # if no transition is explicitly defined for the passed-in character
    if current_state not in transitions:
        raise ValueError("Received an invalid state '{}'".format(current_state))
    if current_token in transitions[current_state]:
        return transitions[current_state][current_token]
    else:
        return transitions[current_state][0]

def get_token_gen(sql,tokens):
    """ return a generator that indicates each token in turn, and the identity
        of that token
        return: (token's integer position in string, token)
    """
    positionDict = {}
    search_position = 0
    for token in tokens:
        positionDict[token] = sql.find(token,search_position)
    while positionDict.values() != []:
        rval = sorted(positionDict.items(), key=lambda t: t[1])[0]
        if rval==-1:
            for key in positionDict.keys():
                if positionDict[key] == -1:
                    del positionDict[key]
            continue
        yield rval
        search_position = rval[1] + len(rval[0])

def split_sql(sql):
    """isolate complete SQL-statements from the passed-in string
       return: the SQL-statements from the passed-in string,
       separated into individual statements """
    if len(sql) == 0:
        raise ValueError("Input appears to be empty.")
    
    # first, find the locations of all potential tokens in the input
    tokens = ['$$','*/','/*',';',"'",'"','--',"\n"]

    # move through the tokens in order, appending SQL-chunks to current string
    previous_state = '_'
    current_state = '_'
    current_sql_expression = ''
    previous_position = 0
    for token, position in get_token_gen(sql,tokens):
        current_state = get_processing_state(current_state,token)
        # disard everything except for newlines if in line-comment state
        if current_state != '--' and previous_state != '--':
            current_sql_expression += sql[previous_position:position+len(token)]
        elif current_state == '--' and previous_state != '--':
        # if line-comment just started, add everything before it:
            current_sql_expression += sql[previous_position:position]
        elif token=="\n":
            current_sql_expression += token
##        print "Current token: {} new state: {}".format(repr(token),current_state)
        if current_state == ';':
            yield current_sql_expression
            current_sql_expression = ''
            current_state = '_'
            previous_state = '_'
        previous_position = position + len(token)
        previous_state = current_state
    current_sql_expression += sql[previous_position:].rstrip(';')
    if current_sql_expression.strip(' ;'):
    # unless only whitespace and semicolons left, return remaining characters
    # between last ; and EOF
        yield current_sql_expression + ';'
