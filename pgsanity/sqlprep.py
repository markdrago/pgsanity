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

    current_state   --    see 'States' further down in this dcostring

    current_token   --    any character or character-pair which can prompt one
                          or more transitions in SQL-state (quote-marks,
                          comment-starting symbols, etc.)
                          NOTE: For both double-quote and single-quote
                          characters, the passed-in token should consist of the
                          initial quote character, plus the character which
                          immediately follows it, because it is not possible
                          to determine the next state without it.

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
            "'": "'", '"': '"', ';': ';', "''": "'2", '""': '"2'
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
    elif current_token[0] in transitions[current_state]:
    # if we have a double-quote + peek character or a single-quote + char,
    # transition using that
        temp_state = transitions[current_state][current_token[0]]
        return get_processing_state(temp_state,current_token[1]) # recurse
    else:
        return transitions[current_state][0]

def get_token_gen(sql,tokens):
    """ return a generator that indicates the position of each token in turn,
        and the identity of that token
        return: (token's integer position in string, token)
    """
    peek_tokens = ["'",'"']
    positionDict = {}
    search_position = 0
    for token in tokens:
        positionDict[token] = sql.find(token,search_position)    
    while positionDict.values() != []:
        si = sorted(positionDict.items(), key=lambda t: t[1])
##        print "Sorted tokens: {}".format(si)
        rval = si[0]
        find_next = rval[0]
        if rval[1]==-1:
##            print "Deleting... {}".format(rval[0])
            del positionDict[rval[0]]
            continue
        elif rval[0] in peek_tokens and rval[1]+1 < len(sql):
            find_next = rval[0]
            rval = (rval[0]+sql[rval[1]+1],rval[1])
        yield rval
        # if possible, replace the token just returned and advance the cursor
        search_position = rval[1] + len(rval[0])
        positionDict[find_next] = sql.find(find_next,search_position)
##        print "Found next {} at {}".format(find_next,positionDict[find_next])

def split_sql(sql):
    """isolate complete SQL-statements from the passed-in string
       return: the SQL-statements from the passed-in string,
       separated into individual statements """
    if len(sql) == 0:
        raise ValueError("Input appears to be empty.")

##    print "\nSTRING:\n"
##    print sql
##    print "\n:STRING"
##    print ""
    
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
##        print "Current token: {}".format(repr(token))
##        print "New state from token: ( {} )".format(current_state)
##        print "Current position: {}".format(position)
##        print "String so far: {}".format(repr(current_sql_expression))
##        print "---"
        if current_state == ';':
##            print "YIELDING: {}".format(repr(current_sql_expression))
            yield current_sql_expression
##            print "\n"
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
