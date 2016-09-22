import unittest
import tempfile
import os
from codecs import BOM_UTF8

from pgsanity import pgsanity

class TestPgSanity(unittest.TestCase):
    def test_args_parsed_one_filename(self):
        args = ["myfile.sql"]
        config = pgsanity.get_config(args)
        self.assertEqual(args, config.files)

    def test_args_parsed_multiple_filenames(self):
        args = ["myfile.sql", "myotherfile.sql"]
        config = pgsanity.get_config(args)
        self.assertEqual(args, config.files)

    def test_check_valid_string(self):
        text = "select a from b;"
        (success, msg) = pgsanity.check_string(text)
        self.assertTrue(success)

    def test_check_invalid_string(self):
        text = "garbage select a from b;"
        (success, msg) = pgsanity.check_string(text)
        self.assertFalse(success)
        self.assertEqual('line 1: ERROR: unrecognized data type name "garbage"', msg)

    def test_check_invalid_string_2(self):
        text = "SELECT '\n"
        text += "-- this is not really a comment' AS c;\n"
        text += "SELECT '\n"
        text += "-- neither is this' AS c spam;"

        (success,msg) = pgsanity.check_string(text)
        self.assertFalse(success)
        self.assertEqual('line 4: ERROR: syntax error at or near "spam"', msg)

    def test_bom_gets_stripped(self):
        bomless = "SELECT 'pining for the fjords';".encode('utf-8')
        bomful = BOM_UTF8 + bomless
        self.assertEqual(pgsanity.remove_bom_if_exists(bomful), bomless)

    def test_bom_removal_idempotence(self):
        bomless = "SELET current_setting('parrot.status);".encode('utf-8')
        self.assertEqual(bomless, pgsanity.remove_bom_if_exists(bomless))


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


def write_out(f, text):
    f.write(text)
    f.flush()
