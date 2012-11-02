import unittest

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
