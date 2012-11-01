import unittest
import tempfile
import os

from pgsanity import ecpg

class TestEcpg(unittest.TestCase):
    def setUp(self):
        self.file = tempfile.NamedTemporaryFile(delete=False, suffix=".pgc")

    def tearDown(self):
        self.file.close()
        os.remove(self.file.name)

    def test_simple_success(self):
        text = "EXEC SQL select a from b;"
        write_out(self.file, text)

        (success, msg) = ecpg.check_syntax(self.file.name)
        self.assertTrue(success)

    def test_simple_failure(self):
        text = "EXEC SQL garbage select a from b;"
        write_out(self.file, text)

        (success, msg) = ecpg.check_syntax(self.file.name)
        self.assertFalse(success)
        self.assertEqual('line 1: ERROR: unrecognized data type name "garbage"', msg)

    def test_parse_error_simple(self):
        error = '/tmp/tmpLBKZo5.pgc:1: ERROR: unrecognized data type name "garbage"'
        expected = 'line 1: ERROR: unrecognized data type name "garbage"'
        self.assertEqual(expected, ecpg.parse_error(error))

    def test_parse_error_comments(self):
        error = '/tmp/tmpLBKZo5.pgc:5: ERROR: syntax error at or near "//"'
        expected = 'line 5: ERROR: syntax error at or near "--"'
        self.assertEqual(expected, ecpg.parse_error(error))

def write_out(f, text):
    f.write(text)
    f.flush()
