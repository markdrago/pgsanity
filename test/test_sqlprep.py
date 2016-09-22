import unittest

from pgsanity import sqlprep

class TestSqlPrep(unittest.TestCase):
    def test_split_sql_nothing_interesting(self):
        text = "abcd123"
        expected = ["abcd123;"]
        self.assertEqual(expected, list(sqlprep.split_sql(text)))

    def test_split_sql_trailing_semicolon(self):
        text = "abcd123;"
        expected = [text]
        self.assertEqual(expected, list(sqlprep.split_sql(text)))

    def test_split_sql_comment_between_statements(self):
        text = "select a from b;\n"
        text += "--comment here\n"
        text += "select a from b;"

        expected = ["select a from b;","\n\nselect a from b;"]
        self.assertEqual(expected, list(sqlprep.split_sql(text)))

    def test_split_sql_inline_comment(self):
        text = "select a from b; --comment here\n"
        text += "select a from b;"

        expected = ["select a from b;", " \nselect a from b;"]
        self.assertEqual(expected, list(sqlprep.split_sql(text)))

    def test_handles_first_column_comment_between_statements(self):
        text = "blah blah;\n"
        text += "--comment here\n"
        text += "blah blah;"

        expected = "EXEC SQL blah blah;"
        expected += "EXEC SQL \n\nblah blah;"

        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_handles_inline_comment_between_statements(self):
        text = "blah blah; --comment here\n"
        text += "blah blah;"

        expected = "EXEC SQL blah blah;"
        expected += "EXEC SQL  \nblah blah;"

        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_does_not_mangle_inline_comment_within_statement(self):
        text = "blah blah--comment here\n"
        text += "blah blah"

        expected = "EXEC SQL blah blah\n"
        expected += "blah blah;"

        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_does_not_mangle_first_column_comment_within_statement(self):
        text = "select a from b\n"
        text += "--comment here\n"
        text += "where c=3"

        expected = "select a from b\n"
        expected += "\n"
        expected += "where c=3;"
        expected = "EXEC SQL " + expected

        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_prepend_exec_sql_to_simple_statements(self):
        text = "create table control.myfavoritetable (id bigint);"
        expected = "EXEC SQL " + text
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_prepend_exec_sql_multiple_lines(self):
        text1 = "create table control.myfavoritetable (id bigint);"
        text2 = "\ncreate table control.myfavoritetable (id bigint);"
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

    def test_comment_start_found_within_comment_within_statement(self):
        text = "select a from b --comment in comment --here\nwhere c=1;"
        expected = "EXEC SQL select a from b \nwhere c=1;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_comment_start_found_within_comment_between_statements(self):
        text = "select a from b; --comment in comment --here\nselect c from d;"
        expected = "EXEC SQL select a from b;EXEC SQL  \nselect c from d;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_double_semicolon(self):
        text = "select a from b;;"
        expected = "EXEC SQL select a from b;EXEC SQL ;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_triple_semicolon(self):
        text = "select a from b;;;"
        expected = "EXEC SQL select a from b;EXEC SQL ;EXEC SQL ;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_semi_found_in_comment_at_end_of_line(self):
        text = "select a\nfrom b --semi in comment;\nwhere c=1;"
        expected = "EXEC SQL select a\nfrom b \nwhere c=1;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_handles_first_line_comment(self):
        text = "--comment on line 1\nselect a from b;"
        expected = "EXEC SQL \nselect a from b;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_handles_block_comment_on_last_line(self):
        text = "select a from b;\n/*\nselect c from d;\n*/"
        expected = "EXEC SQL select a from b;EXEC SQL \n/*\nselect c from d;\n*/;"
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

    def test_trailing_whitespace_after_semicolon(self):
        text = "select a from b; "
        expected = "EXEC SQL select a from b;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))

    def test_line_starts_with_semicolon(self):
        text = ";select a from b;"
        expected = "EXEC SQL ;EXEC SQL select a from b;"
        self.assertEqual(expected, sqlprep.prepare_sql(text))
