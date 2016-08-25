import unittest

from pgsanity import sqlprep

class TestSqlPrep(unittest.TestCase):
    def test_split_sql_nothing_interesting(self):
        text = "abcd123"
        expected = [(None, None, "abcd123")]
        self.assertEqual(expected, list(sqlprep.split_sql(text)))

    def test_split_sql_trailing_semicolon(self):
        text = "abcd123;"
        expected = [(None, ";", "abcd123"), (";", None, '')]
        self.assertEqual(expected, list(sqlprep.split_sql(text)))

    def test_split_sql_comment_between_statements(self):
        text = "select a from b;\n"
        text += "--comment here\n"
        text += "select a from b;"

        expected = [(None, ";", "select a from b"),
                    (";", "\n", ''),
                    ("\n", "--", ''),
                    ("--", "\n", 'comment here'),
                    ("\n", ";", 'select a from b'),
                    (";", None, '')]
        self.assertEqual(expected, list(sqlprep.split_sql(text)))

    def test_split_sql_inline_comment(self):
        text = "select a from b; --comment here\n"
        text += "select a from b;"

        expected = [(None, ";", "select a from b"),
                    (";", "--", ' '),
                    ("--", "\n", 'comment here'),
                    ("\n", ";", 'select a from b'),
                    (";", None, '')]
        self.assertEqual(expected, list(sqlprep.split_sql(text)))

    def test_handles_first_column_comment_between_statements(self):
        text = "blah blah;\n"
        text += "--comment here\n"
        text += "blah blah;"

        expected = "EXEC SQL blah blah;\n"
        expected += "//comment here\n"
        expected += "EXEC SQL blah blah;"

        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_handles_inline_comment_between_statements(self):
        text = "blah blah; --comment here\n"
        text += "blah blah;"

        expected = "EXEC SQL blah blah; //comment here\n"
        expected += "EXEC SQL blah blah;"

        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_does_not_mangle_inline_comment_within_statement(self):
        text = "blah blah--comment here\n"
        text += "blah blah"

        expected = "EXEC SQL " + text

        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_does_not_mangle_first_column_comment_within_statement(self):
        text = "select a from b\n"
        text += "--comment here\n"
        text += "where c=3"

        expected = "EXEC SQL " + text

        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_prepend_exec_sql_to_simple_statements(self):
        text = "create table control.myfavoritetable (id bigint);"
        expected = "EXEC SQL " + text
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_prepend_exec_sql_multiple_lines(self):
        text1 = "create table control.myfavoritetable (id bigint);\n"
        text2 = "create table control.myfavoritetable (id bigint);"
        expected = "EXEC SQL " + text1 + "EXEC SQL " + text2
        self.assertEqual(expected, sqlprep.prepare_sql(text1 + text2))

    def test_prepend_exec_sql_wrapped_statement(self):
        text = "create table control.myfavoritetable (\n"
        text += "    id bigint\n"
        text += ");"
        expected = "EXEC SQL " + text
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_prepend_exec_sql_two_statements_one_line(self):
        text = "select a from b; select c from d;"
        expected = "EXEC SQL select a from b;EXEC SQL  select c from d;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_prepend_exec_sql_wrapped_statement_with_multiple_semis_on_last_line(self):
        text1 = "create table control.myfavoritetable (\n"
        text2 = "    id bigint\n"
        text3 = ");"
        text4 = "select a from b;"
        expected = "EXEC SQL " + text1 + text2 + text3 + "EXEC SQL " + text4
        self.assertEqual(expected, sqlprep.prepare_sql(text1 + text2 + text3 + text4))

    def test_prepend_exec_sql_wrapped_trailing_sql(self):
        text = "select a from b; select a\nfrom b;"
        expected = "EXEC SQL select a from b;EXEC SQL  select a\nfrom b;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_no_append_semi(self):
        text = "select a from b"
        expected = 'EXEC SQL ' + text
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_append_semi(self):
        text = "select a from b"
        expected = 'EXEC SQL ' + text + ';'
        self.assertEqual(expected, sqlprep.prepare_sql(text, add_semicolon=True))

    def test_append_semi_once(self):
        text = "select a from b;"
        expected = 'EXEC SQL ' + text
        self.assertEqual(expected, sqlprep.prepare_sql(text, add_semicolon=True))

    def test_append_semi_line_comment(self):
        text = "select a from b\n-- looks done!"
        expected = 'EXEC SQL ' + text + "\n;"
        self.assertEqual(expected, sqlprep.prepare_sql(text, add_semicolon=True))

    def test_append_semi_line_comment(self):
        text = "select a from b\n/* looks done!\n*"
        expected = 'EXEC SQL ' + text
        self.assertEqual(expected, sqlprep.prepare_sql(text, add_semicolon=True))

    def test_comment_start_found_within_comment_within_statement(self):
        text = "select a from b --comment in comment --here\nwhere c=1;"
        expected = "EXEC SQL select a from b --comment in comment --here\nwhere c=1;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_comment_start_found_within_comment_between_statements(self):
        text = "select a from b; --comment in comment --here\nselect c from d;"
        expected = "EXEC SQL select a from b; //comment in comment //here\nEXEC SQL select c from d;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_double_semicolon(self):
        text = "select a from b;;"
        expected = "EXEC SQL select a from b;;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_semi_found_in_comment_at_end_of_line(self):
        text = "select a\nfrom b --semi in comment;\nwhere c=1;"
        expected = "EXEC SQL select a\nfrom b --semi in comment;\nwhere c=1;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_handles_first_line_comment(self):
        text = "--comment on line 1\nselect a from b;"
        expected = "//comment on line 1\nEXEC SQL select a from b;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_handles_block_comment_on_last_line(self):
        text = "select a from b;\n/*\nselect c from d;\n*/"
        expected = "EXEC SQL select a from b;\n/*\nselect c from d;\n*/"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_semi_found_in_block_comment(self):
        text = "select a\n/*\n;\n*/from b;"
        expected = "EXEC SQL " + text
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_line_comment_in_block_comment_is_undisturbed(self):
        text = "select a\n/*\n--hey\n*/\nfrom b;"
        expected = "EXEC SQL " + text
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_opening_two_block_comments_only_requries_one_close(self):
        text = "select a\n/*\n/*\ncomment\n*/from b;select c from d;"
        expected = "EXEC SQL select a\n/*\n/*\ncomment\n*/from b;EXEC SQL select c from d;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

#  TODO:
#  semicolon followed by only whitespace / comments
#  multiple semicolons in a row (legal?)
#  line starts with semi and then has a statement
