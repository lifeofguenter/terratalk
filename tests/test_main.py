import os
import unittest

from click.testing import CliRunner

from terratalk import __main__


class TestMain(unittest.TestCase):

    def setUp(self) -> None:
        self.cwd = os.getcwd()
        os.chdir('tests')

    def tearDown(self) -> None:
        os.chdir(self.cwd)

    def test_comment_nothing(self):
        runner = CliRunner()
        result = runner.invoke(__main__.cli, ['comment', '-w', 'nothing'])
        self.assertEqual(result.output, '[terratalk] this plan does nothing\n')

    def test_output(self):
        runner = CliRunner()
        result = runner.invoke(__main__.cli, ['output', '-w', 'test'])
        self.assertEqual(result.output, '''
+  null_resource.foobar will be created

Plan: 1 to add, 0 to change, 0 to destroy.
'''.lstrip())
