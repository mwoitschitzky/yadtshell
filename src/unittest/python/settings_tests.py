import yadtshell
import unittest
from mock import patch, MagicMock
from StringIO import StringIO


class SettingsTests(unittest.TestCase):

    def setUp(self):
        self.open_patcher = patch('yadtshell.settings.open', create=True)
        self.mock_open = self.open_patcher.start()

        self.getcwd_patcher = patch('yadtshell.settings.os.getcwd')
        self.getcwd = self.getcwd_patcher.start()

        self.getcwd.return_value = '/foo/bar/foobaz42'

    def tearDown(self):
        self.open_patcher.stop()
        self.getcwd_patcher.stop()

    def test_should_load_target_file(self):
        content = """
hosts:
    - foobar
"""
        self.mock_open.return_value = MagicMock(
            spec=file, wraps=StringIO(content))

        result = yadtshell.settings.load_target_file("useless_name")
        expect = dict(name='foobaz42',
                      hosts=['foobar'])
        self.assertEqual(result, expect)

    def test_should_load_meta_target_file(self):
        content = """
hosts:
    - foobar01
includes:
    - sub-target
"""
        subcontent = """
hosts:
    - foobar42
"""

        def my_open(filename):
            if filename == 'root-target':
                return MagicMock(spec=file, wraps=StringIO(content))
            return MagicMock(spec=file, wraps=StringIO(subcontent))

        self.mock_open.side_effect = my_open

        result = yadtshell.settings.load_target_file('root-target')
        expect = dict(name='foobaz42',
                      hosts=['foobar01', 'foobar42'],
                      includes=['sub-target'])
        self.assertEqual(result, expect)

    def test_should_load_recursed_meta_target_files(self):
        content = """
hosts:
    - foobar01
includes:
    - sub-target
"""
        subcontent = """
hosts:
    - foobar42
includes:
    - sub-sub-target
"""
        subsubcontent = """
hosts:
    - foobar4242
"""

        def my_open(filename):
            if filename == 'root-target':
                return MagicMock(spec=file, wraps=StringIO(content))
            if filename == 'sub-target':
                return MagicMock(spec=file, wraps=StringIO(subcontent))

            return MagicMock(spec=file, wraps=StringIO(subsubcontent))

        self.mock_open.side_effect = my_open

        result = yadtshell.settings.load_target_file('root-target')
        expect = dict(name='foobaz42',
                      hosts=['foobar01', 'foobar42', 'foobar4242'],
                      includes=['sub-target'])
        self.assertEqual(result, expect)

    def test_should_load_recursed_meta_target_files_once(self):
        content = """
hosts:
    - foobar01
includes:
    - sub-target
"""
        subcontent = """
hosts:
    - foobar42
includes:
    - root-target
"""

        def my_open(filename):
            if filename == 'root-target':
                return MagicMock(spec=file, wraps=StringIO(content))
            return MagicMock(spec=file, wraps=StringIO(subcontent))

        self.mock_open.side_effect = my_open

        result = yadtshell.settings.load_target_file('root-target')
        expect = dict(name='foobaz42',
                      hosts=['foobar01', 'foobar42'],
                      includes=['sub-target'])
        self.assertEqual(result, expect)

    def test_should_add_hosts_only_once(self):
        content = """
hosts:
    - foobar01
includes:
    - sub-target
"""
        subcontent = """
hosts:
    - foobar42
    - foobar01
"""

        def my_open(filename):
            if filename == 'root-target':
                return MagicMock(spec=file, wraps=StringIO(content))
            return MagicMock(spec=file, wraps=StringIO(subcontent))

        self.mock_open.side_effect = my_open

        result = yadtshell.settings.load_target_file('root-target')
        expect = dict(name='foobaz42',
                      hosts=['foobar01', 'foobar42'],
                      includes=['sub-target'])
        self.assertEqual(result, expect)

    def test_should_add_hosts_only_once_other_format(self):
        content = """
hosts:
    - foobar01
includes:
    - sub-target
"""
        subcontent = """
hosts:
    - foobar42 foobar23
    - foobar01
"""

        def my_open(filename):
            if filename == 'root-target':
                return MagicMock(spec=file, wraps=StringIO(content))
            return MagicMock(spec=file, wraps=StringIO(subcontent))

        self.mock_open.side_effect = my_open

        result = yadtshell.settings.load_target_file('root-target')
        expect = dict(name='foobaz42',
                      hosts=['foobar01', 'foobar42 foobar23'],
                      includes=['sub-target'])
        self.assertEqual(result, expect)

    def test_should_cope_with_targets_only_containing_includes(self):
        content = """
includes:
    -   sub-target
"""
        subcontent = """
hosts:
    - foobar01
    - foobar42
"""

        def my_open(filename):
            if filename == 'root-target':
                return MagicMock(spec=file, wraps=StringIO(content))
            return MagicMock(spec=file, wraps=StringIO(subcontent))

        self.mock_open.side_effect = my_open

        result = yadtshell.settings.load_target_file('root-target')
        expect = dict(name='foobaz42',
                      hosts=['foobar01', 'foobar42'],
                      includes=['sub-target'])
        self.assertEqual(result, expect)