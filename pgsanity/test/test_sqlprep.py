import unittest

from pgsanity import sqlprep

class TestSqlPrep(unittest.TestCase):
    def test_handles_first_column_comment(self):
        text = "blah blah\n"
        text += "--comment here\n"
        text += "blah blah"

        expected = "blah blah\n"
        expected += "//comment here\n"
        expected += "blah blah"

        self.assertEqual(expected, sqlprep.handle_sql_comments(text))

    def test_handles_inline_comment(self):
        text = "blah blah--comment here\n"
        text += "blah blah"

        expected = "blah blah//comment here\n"
        expected += "blah blah"

        self.assertEqual(expected, sqlprep.handle_sql_comments(text))

    def test_prepend_exec_sql_to_simple_statements(self):
        text = "create table control.myfavoritetable (id bigint);"
        expected = "EXEC SQL " + text
        self.assertEqual(expected, sqlprep.add_exec_sql_statements(text))

    def test_prepend_exec_sql_multiple_lines(self):
        text1 = "create table control.myfavoritetable (id bigint);\n"
        text2 = "create table control.myfavoritetable (id bigint);"
        expected = "EXEC SQL " + text1 + "EXEC SQL " + text2
        self.assertEqual(expected, sqlprep.add_exec_sql_statements(text1 + text2))

    def test_line_has_sql_affirmative(self):
        self.assertTrue(sqlprep.line_has_sql("select a from b;"))

    def test_line_has_sql_entirely_comment(self):
        self.assertFalse(sqlprep.line_has_sql("--comment here"))

    def test_line_has_sql_entirely_whitespace(self):
        self.assertFalse(sqlprep.line_has_sql("  \t"))

    def test_line_has_sql_whitespace_before_comment(self):
        self.assertFalse(sqlprep.line_has_sql("  \t--comment here"))

    def test_line_has_sql_with_start_before_comment(self):
        self.assertTrue(sqlprep.line_has_sql("abcdef--comment here", 5))

    def test_line_has_sql_with_start_after_comment(self):
        self.assertFalse(sqlprep.line_has_sql("abcdef--comment here", 6))

    def test_prepend_exec_sql_wrapped_statement(self):
        text = "create table control.myfavoritetable (\n"
        text += "    id bigint\n"
        text += ");"
        expected = "EXEC SQL " + text
        self.assertEqual(expected, sqlprep.add_exec_sql_statements(text))

    def test_prepend_exec_sql_two_statements_one_line(self):
        text = "select a from b; select c from d;"
        expected = "EXEC SQL select a from b;EXEC SQL  select c from d;"
        self.assertEqual(expected, sqlprep.add_exec_sql_statements(text))

    def test_deal_with_inline_semicolons_simple(self):
        text = "before;after"
        expected = "before;EXEC SQL after"
        self.assertEqual(expected, sqlprep.deal_with_inline_semicolons(text))

    def test_deal_with_inline_semicolons_skip_ending_semicolon(self):
        text = "before;after;"
        expected = "before;EXEC SQL after;"
        self.assertEqual(expected, sqlprep.deal_with_inline_semicolons(text))

    def test_prepend_exec_sql_wrapped_statement_with_multiple_semis_on_last_line(self):
        text1 = "create table control.myfavoritetable (\n"
        text2 = "    id bigint\n"
        text3 = ");"
        text4 = "select a from b;"
        expected = "EXEC SQL " + text1 + text2 + text3 + "EXEC SQL " + text4
        self.assertEqual(expected, sqlprep.add_exec_sql_statements(text1 + text2 + text3 + text4))

    def test_prepend_exec_sql_wrapped_trailing_sql(self):
        text = "select a from b; select a\nfrom b;"
        expected = "EXEC SQL select a from b;EXEC SQL  select a\nfrom b;"
        self.assertEqual(expected, sqlprep.add_exec_sql_statements(text))

    def test_semi_found_in_comment_at_end_of_line(self):
        text = "select a\nfrom b --semi in comment;\nwhere c=1;"
        expected = "EXEC SQL select a\nfrom b --semi in comment;\nwhere c=1;"
        self.assertEqual(expected, sqlprep.add_exec_sql_statements(text))

    def test_handles_first_line_comment(self):
        text = "--comment on line 1\nselect a from b;"
        expected = "--comment on line 1\nEXEC SQL select a from b;"
        self.assertEqual(expected, sqlprep.add_exec_sql_statements(text))

#TODO:
#  semicolon followed by only whitespace / comments
#  multiple semicolons in a row (legal?)
#  line starts with semi and then has a statement
