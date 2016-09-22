import unittest
import tempfile
import os

from pgsanity import pgsanity

class TestPgSanity(unittest.TestCase):
    def test_args_parsed_one_filename(self):
        args = ["myfile.sql"]
        config = pgsanity.get_config(args)
        self.assertEqual(args, config.files)
        self.assertEqual(False, config.add_semicolon)

    def test_args_parsed_multiple_filenames(self):
        args = ["myfile.sql", "myotherfile.sql"]
        config = pgsanity.get_config(args)
        self.assertEqual(args, config.files)
        self.assertEqual(False, config.add_semicolon)

    def test_args_parsed_add_semicolon(self):
        args = ["--add-semicolon", "myfile.sql"]
        config = pgsanity.get_config(args)
        self.assertEqual(["myfile.sql"], config.files)
        self.assertEqual(True, config.add_semicolon)

    def test_check_valid_string(self):
        text = "select a from b;"
        (success, msg) = pgsanity.check_string(text)
        self.assertTrue(success)

    def test_check_invalid_string(self):
        text = "garbage select a from b;"
        (success, msg) = pgsanity.check_string(text)
        self.assertFalse(success)
        self.assertEqual('line 1: ERROR: unrecognized data type name "garbage"', msg)


class TestPgSanityFiles(unittest.TestCase):
    def setUp(self):
        self.file = tempfile.NamedTemporaryFile(delete=False, suffix=".pgc")

    def tearDown(self):
        self.file.close()
        os.remove(self.file.name)

    def test_check_valid_file(self):
        text = "select a from b;"
        write_out(self.file, text.encode('utf-8'))
        status_code = pgsanity.check_file(self.file.name)
        self.assertEqual(status_code, 0)

    def test_check_invalid_file(self):
        text = "garbage select a from b;"
        write_out(self.file, text.encode('utf-8'))
        status_code = pgsanity.check_file(self.file.name)
        self.assertNotEqual(status_code, 0)

    def _write_missing_semi(self):
        text = "select a from b"
        write_out(self.file, text.encode('utf-8'))

    def test_check_missing_semi(self):
        self._write_missing_semi()
        status_code = pgsanity.check_file(self.file.name)
        self.assertNotEqual(status_code, 0)

    def test_check_missing_semi_ok(self):
        self._write_missing_semi()
        status_code = pgsanity.check_file(self.file.name, add_semicolon=True)
        self.assertEqual(status_code, 0)


def write_out(f, text):
    f.write(text)
    f.flush()
