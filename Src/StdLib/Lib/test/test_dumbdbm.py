"""Test script for the dumbdbm module
   Original by Roger E. Masse
"""

import os
import stat
import unittest
import dumbdbm
from test import test_support

_fname = test_support.TESTFN

def _delete_files():
    for ext in [".dir", ".dat", ".bak"]:
        try:
            os.unlink(_fname + ext)
        except OSError:
            pass

class DumbDBMTestCase(unittest.TestCase):
    _dict = {'0': '',
             'a': 'Python:',
             'b': 'Programming',
             'c': 'the',
             'd': 'way',
             'f': 'Guido',
             'g': 'intended'
             }

    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)

    def test_dumbdbm_creation(self):
        f = dumbdbm.open(_fname, 'c')
        self.assertEqual(f.keys(), [])
        for key in self._dict:
            f[key] = self._dict[key]
        self.read_helper(f)
        f.close()

    @unittest.skipUnless(hasattr(os, 'chmod'), 'os.chmod not available')
    @unittest.skipUnless(hasattr(os, 'umask'), 'os.umask not available')
    def test_dumbdbm_creation_mode(self):
        try:
            old_umask = os.umask(0002)
            f = dumbdbm.open(_fname, 'c', 0637)
            f.close()
        finally:
            os.umask(old_umask)

        expected_mode = 0635
        if os.name != 'posix':
            # Windows only supports setting the read-only attribute.
            # This shouldn't fail, but doesn't work like Unix either.
            expected_mode = 0666

        import stat
        st = os.stat(_fname + '.dat')
        self.assertEqual(stat.S_IMODE(st.st_mode), expected_mode)
        st = os.stat(_fname + '.dir')
        self.assertEqual(stat.S_IMODE(st.st_mode), expected_mode)

    def test_close_twice(self):
        f = dumbdbm.open(_fname)
        f['a'] = 'b'
        self.assertEqual(f['a'], 'b')
        f.close()
        f.close()

    def test_dumbdbm_modification(self):
        self.init_db()
        f = dumbdbm.open(_fname, 'w')
        self._dict['g'] = f['g'] = "indented"
        self.read_helper(f)
        f.close()

    def test_dumbdbm_read(self):
        self.init_db()
        f = dumbdbm.open(_fname, 'r')
        self.read_helper(f)
        f.close()

    def test_dumbdbm_keys(self):
        self.init_db()
        f = dumbdbm.open(_fname)
        keys = self.keys_helper(f)
        f.close()

    def test_write_write_read(self):
        # test for bug #482460
        f = dumbdbm.open(_fname)
        f['1'] = 'hello'
        f['1'] = 'hello2'
        f.close()
        f = dumbdbm.open(_fname)
        self.assertEqual(f['1'], 'hello2')
        f.close()

    def test_line_endings(self):
        # test for bug #1172763: dumbdbm would die if the line endings
        # weren't what was expected.
        f = dumbdbm.open(_fname)
        f['1'] = 'hello'
        f['2'] = 'hello2'
        f.close()

        # Mangle the file by adding \r before each newline
        data = open(_fname + '.dir').read()
        data = data.replace('\n', '\r\n')
        open(_fname + '.dir', 'wb').write(data)

        f = dumbdbm.open(_fname)
        self.assertEqual(f['1'], 'hello')
        self.assertEqual(f['2'], 'hello2')


    def read_helper(self, f):
        keys = self.keys_helper(f)
        for key in self._dict:
            self.assertEqual(self._dict[key], f[key])

    def init_db(self):
        f = dumbdbm.open(_fname, 'w')
        for k in self._dict:
            f[k] = self._dict[k]
        f.close()

    def keys_helper(self, f):
        keys = f.keys()
        keys.sort()
        dkeys = self._dict.keys()
        dkeys.sort()
        self.assertEqual(keys, dkeys)
        return keys

    # Perform randomized operations.  This doesn't make assumptions about
    # what *might* fail.
    def test_random(self):
        import random
        d = {}  # mirror the database
        for dummy in range(5):
            f = dumbdbm.open(_fname)
            for dummy in range(100):
                k = random.choice('abcdefghijklm')
                if random.random() < 0.2:
                    if k in d:
                        del d[k]
                        del f[k]
                else:
                    v = random.choice('abc') * random.randrange(10000)
                    d[k] = v
                    f[k] = v
                    self.assertEqual(f[k], v)
            f.close()

            f = dumbdbm.open(_fname)
            expected = d.items()
            expected.sort()
            got = f.items()
            got.sort()
            self.assertEqual(expected, got)
            f.close()

    def test_eval(self):
        with open(_fname + '.dir', 'w') as stream:
            stream.write("str(__import__('sys').stdout.write('Hacked!')), 0\n")
        with test_support.captured_stdout() as stdout:
            with self.assertRaises(ValueError):
                dumbdbm.open(_fname).close()
            self.assertEqual(stdout.getvalue(), '')

    @unittest.skipUnless(hasattr(os, 'chmod'), 'test needs os.chmod()')
    def test_readonly_files(self):
        dir = _fname
        os.mkdir(dir)
        try:
            fname = os.path.join(dir, 'db')
            f = dumbdbm.open(fname, 'n')
            self.assertEqual(list(f.keys()), [])
            for key in self._dict:
                f[key] = self._dict[key]
            f.close()
            os.chmod(fname + ".dir", stat.S_IRUSR)
            os.chmod(fname + ".dat", stat.S_IRUSR)
            os.chmod(dir, stat.S_IRUSR|stat.S_IXUSR)
            f = dumbdbm.open(fname, 'r')
            self.assertEqual(sorted(f.keys()), sorted(self._dict))
            f.close()  # don't write
        finally:
            test_support.rmtree(dir)

    def tearDown(self):
        _delete_files()

    def setUp(self):
        _delete_files()

def test_main():
    try:
        test_support.run_unittest(DumbDBMTestCase)
    finally:
        _delete_files()

if __name__ == "__main__":
    test_main()
