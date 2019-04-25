import unittest
from test import test_support, test_genericpath
from test import test_support as support

import posixpath
import os
import sys
from posixpath import realpath, abspath, dirname, basename

try:
    import posix
except ImportError:
    posix = None

# An absolute path to a temporary filename for testing. We can't rely on TESTFN
# being an absolute path, so we need this.

ABSTFN = abspath(test_support.TESTFN)

def skip_if_ABSTFN_contains_backslash(test):
    """
    On Windows, posixpath.abspath still returns paths with backslashes
    instead of posix forward slashes. If this is the case, several tests
    fail, so skip them.
    """
    found_backslash = '\\' in ABSTFN
    msg = "ABSTFN is not a posix path - tests fail"
    return [test, unittest.skip(msg)(test)][found_backslash]

def safe_rmdir(dirname):
    try:
        os.rmdir(dirname)
    except OSError:
        pass

class PosixPathTest(unittest.TestCase):

    def setUp(self):
        self.tearDown()

    def tearDown(self):
        for suffix in ["", "1", "2"]:
            test_support.unlink(test_support.TESTFN + suffix)
            safe_rmdir(test_support.TESTFN + suffix)

    def test_join(self):
        self.assertEqual(posixpath.join("/foo", "bar", "/bar", "baz"), "/bar/baz")
        self.assertEqual(posixpath.join("/foo", "bar", "baz"), "/foo/bar/baz")
        self.assertEqual(posixpath.join("/foo/", "bar/", "baz/"), "/foo/bar/baz/")

    def test_split(self):
        self.assertEqual(posixpath.split("/foo/bar"), ("/foo", "bar"))
        self.assertEqual(posixpath.split("/"), ("/", ""))
        self.assertEqual(posixpath.split("foo"), ("", "foo"))
        self.assertEqual(posixpath.split("////foo"), ("////", "foo"))
        self.assertEqual(posixpath.split("//foo//bar"), ("//foo", "bar"))

    def splitextTest(self, path, filename, ext):
        self.assertEqual(posixpath.splitext(path), (filename, ext))
        self.assertEqual(posixpath.splitext("/" + path), ("/" + filename, ext))
        self.assertEqual(posixpath.splitext("abc/" + path), ("abc/" + filename, ext))
        self.assertEqual(posixpath.splitext("abc.def/" + path), ("abc.def/" + filename, ext))
        self.assertEqual(posixpath.splitext("/abc.def/" + path), ("/abc.def/" + filename, ext))
        self.assertEqual(posixpath.splitext(path + "/"), (filename + ext + "/", ""))

    def test_splitext(self):
        self.splitextTest("foo.bar", "foo", ".bar")
        self.splitextTest("foo.boo.bar", "foo.boo", ".bar")
        self.splitextTest("foo.boo.biff.bar", "foo.boo.biff", ".bar")
        self.splitextTest(".csh.rc", ".csh", ".rc")
        self.splitextTest("nodots", "nodots", "")
        self.splitextTest(".cshrc", ".cshrc", "")
        self.splitextTest("...manydots", "...manydots", "")
        self.splitextTest("...manydots.ext", "...manydots", ".ext")
        self.splitextTest(".", ".", "")
        self.splitextTest("..", "..", "")
        self.splitextTest("........", "........", "")
        self.splitextTest("", "", "")

    def test_isabs(self):
        self.assertIs(posixpath.isabs(""), False)
        self.assertIs(posixpath.isabs("/"), True)
        self.assertIs(posixpath.isabs("/foo"), True)
        self.assertIs(posixpath.isabs("/foo/bar"), True)
        self.assertIs(posixpath.isabs("foo/bar"), False)

    def test_basename(self):
        self.assertEqual(posixpath.basename("/foo/bar"), "bar")
        self.assertEqual(posixpath.basename("/"), "")
        self.assertEqual(posixpath.basename("foo"), "foo")
        self.assertEqual(posixpath.basename("////foo"), "foo")
        self.assertEqual(posixpath.basename("//foo//bar"), "bar")

    def test_dirname(self):
        self.assertEqual(posixpath.dirname("/foo/bar"), "/foo")
        self.assertEqual(posixpath.dirname("/"), "/")
        self.assertEqual(posixpath.dirname("foo"), "")
        self.assertEqual(posixpath.dirname("////foo"), "////")
        self.assertEqual(posixpath.dirname("//foo//bar"), "//foo")

    def test_islink(self):
        self.assertIs(posixpath.islink(test_support.TESTFN + "1"), False)
        f = open(test_support.TESTFN + "1", "wb")
        try:
            f.write("foo")
            f.close()
            self.assertIs(posixpath.islink(test_support.TESTFN + "1"), False)
            if hasattr(os, 'symlink'):
                os.symlink(test_support.TESTFN + "1", test_support.TESTFN + "2")
                self.assertIs(posixpath.islink(test_support.TESTFN + "2"), True)
                os.remove(test_support.TESTFN + "1")
                self.assertIs(posixpath.islink(test_support.TESTFN + "2"), True)
                self.assertIs(posixpath.exists(test_support.TESTFN + "2"), False)
                self.assertIs(posixpath.lexists(test_support.TESTFN + "2"), True)
        finally:
            if not f.close():
                f.close()

    def test_samefile(self):
        f = open(test_support.TESTFN + "1", "wb")
        try:
            f.write("foo")
            f.close()
            self.assertIs(
                posixpath.samefile(
                    test_support.TESTFN + "1",
                    test_support.TESTFN + "1"
                ),
                True
            )

            # If we don't have links, assume that os.stat doesn't return
            # reasonable inode information and thus, that samefile() doesn't
            # work.
            if hasattr(os, "symlink"):
                os.symlink(
                    test_support.TESTFN + "1",
                    test_support.TESTFN + "2"
                )
                self.assertIs(
                    posixpath.samefile(
                        test_support.TESTFN + "1",
                        test_support.TESTFN + "2"
                    ),
                    True
                )
                os.remove(test_support.TESTFN + "2")
                f = open(test_support.TESTFN + "2", "wb")
                f.write("bar")
                f.close()
                self.assertIs(
                    posixpath.samefile(
                        test_support.TESTFN + "1",
                        test_support.TESTFN + "2"
                    ),
                    False
                )
        finally:
            if not f.close():
                f.close()

    def test_samestat(self):
        f = open(test_support.TESTFN + "1", "wb")
        try:
            f.write("foo")
            f.close()
            self.assertIs(
                posixpath.samestat(
                    os.stat(test_support.TESTFN + "1"),
                    os.stat(test_support.TESTFN + "1")
                ),
                True
            )
            # If we don't have links, assume that os.stat() doesn't return
            # reasonable inode information and thus, that samestat() doesn't
            # work.
            if hasattr(os, "symlink"):
                os.symlink(test_support.TESTFN + "1", test_support.TESTFN + "2")
                self.assertIs(
                    posixpath.samestat(
                        os.stat(test_support.TESTFN + "1"),
                        os.stat(test_support.TESTFN + "2")
                    ),
                    True
                )
                os.remove(test_support.TESTFN + "2")
                f = open(test_support.TESTFN + "2", "wb")
                f.write("bar")
                f.close()
                self.assertIs(
                    posixpath.samestat(
                        os.stat(test_support.TESTFN + "1"),
                        os.stat(test_support.TESTFN + "2")
                    ),
                    False
                )
        finally:
            if not f.close():
                f.close()

    def test_ismount(self):
        self.assertIs(posixpath.ismount("/"), True)

    def test_ismount_non_existent(self):
        # Non-existent mountpoint.
        self.assertIs(posixpath.ismount(ABSTFN), False)
        try:
            os.mkdir(ABSTFN)
            self.assertIs(posixpath.ismount(ABSTFN), False)
        finally:
            safe_rmdir(ABSTFN)

    @unittest.skipUnless(hasattr(os, 'symlink'),
                         'Requires functional symlink implementation')
    def test_ismount_symlinks(self):
        # Symlinks are never mountpoints.
        try:
            os.symlink("/", ABSTFN)
            self.assertIs(posixpath.ismount(ABSTFN), False)
        finally:
            os.unlink(ABSTFN)

    @unittest.skipIf(posix is None, "Test requires posix module")
    def test_ismount_different_device(self):
        # Simulate the path being on a different device from its parent by
        # mocking out st_dev.
        save_lstat = os.lstat
        def fake_lstat(path):
            st_ino = 0
            st_dev = 0
            if path == ABSTFN:
                st_dev = 1
                st_ino = 1
            return posix.stat_result((0, st_ino, st_dev, 0, 0, 0, 0, 0, 0, 0))
        try:
            os.lstat = fake_lstat
            self.assertIs(posixpath.ismount(ABSTFN), True)
        finally:
            os.lstat = save_lstat

    @unittest.skipIf(posix is None, "Test requires posix module")
    def test_ismount_directory_not_readable(self):
        # issue #2466: Simulate ismount run on a directory that is not
        # readable, which used to return False.
        save_lstat = os.lstat
        def fake_lstat(path):
            st_ino = 0
            st_dev = 0
            if path.startswith(ABSTFN) and path != ABSTFN:
                # ismount tries to read something inside the ABSTFN directory;
                # simulate this being forbidden (no read permission).
                raise OSError("Fake [Errno 13] Permission denied")
            if path == ABSTFN:
                st_dev = 1
                st_ino = 1
            return posix.stat_result((0, st_ino, st_dev, 0, 0, 0, 0, 0, 0, 0))
        try:
            os.lstat = fake_lstat
            self.assertIs(posixpath.ismount(ABSTFN), True)
        finally:
            os.lstat = save_lstat

    def test_expanduser(self):
        self.assertEqual(posixpath.expanduser("foo"), "foo")

    def test_expanduser_home_envvar(self):
        with support.EnvironmentVarGuard() as env:
            env['HOME'] = '/home/victor'
            self.assertEqual(posixpath.expanduser("~"), "/home/victor")

            # expanduser() strips trailing slash
            env['HOME'] = '/home/victor/'
            self.assertEqual(posixpath.expanduser("~"), "/home/victor")

            for home in '/', '', '//', '///':
                env['HOME'] = home
                self.assertEqual(posixpath.expanduser("~"), "/")
                self.assertEqual(posixpath.expanduser("~/"), "/")
                self.assertEqual(posixpath.expanduser("~/foo"), "/foo")

    def test_expanduser_pwd(self):
        pwd = support.import_module('pwd')

        self.assertIsInstance(posixpath.expanduser("~/"), str)

        # if home directory == root directory, this test makes no sense
        if posixpath.expanduser("~") != '/':
            self.assertEqual(
                posixpath.expanduser("~") + "/",
                posixpath.expanduser("~/")
            )
        self.assertIsInstance(posixpath.expanduser("~root/"), str)
        self.assertIsInstance(posixpath.expanduser("~foo/"), str)

        with support.EnvironmentVarGuard() as env:
            # expanduser should fall back to using the password database
            del env['HOME']

            home = pwd.getpwuid(os.getuid()).pw_dir
            # $HOME can end with a trailing /, so strip it (see #17809)
            home = home.rstrip("/") or '/'
            self.assertEqual(posixpath.expanduser("~"), home)

            # bpo-10496: If the HOME environment variable is not set and the
            # user (current identifier or name in the path) doesn't exist in
            # the password database (pwd.getuid() or pwd.getpwnam() fail),
            # expanduser() must return the path unchanged.
            def raise_keyerror(*args):
                raise KeyError

            with support.swap_attr(pwd, 'getpwuid', raise_keyerror), \
                 support.swap_attr(pwd, 'getpwnam', raise_keyerror):
                for path in ('~', '~/.local', '~vstinner/'):
                    self.assertEqual(posixpath.expanduser(path), path)

    def test_normpath(self):
        self.assertEqual(posixpath.normpath(""), ".")
        self.assertEqual(posixpath.normpath("/"), "/")
        self.assertEqual(posixpath.normpath("//"), "//")
        self.assertEqual(posixpath.normpath("///"), "/")
        self.assertEqual(posixpath.normpath("///foo/.//bar//"), "/foo/bar")
        self.assertEqual(posixpath.normpath("///foo/.//bar//.//..//.//baz"), "/foo/baz")
        self.assertEqual(posixpath.normpath("///..//./foo/.//bar"), "/foo/bar")

    @skip_if_ABSTFN_contains_backslash
    def test_realpath_curdir(self):
        self.assertEqual(realpath('.'), os.getcwd())
        self.assertEqual(realpath('./.'), os.getcwd())
        self.assertEqual(realpath('/'.join(['.'] * 100)), os.getcwd())

    @skip_if_ABSTFN_contains_backslash
    def test_realpath_pardir(self):
        self.assertEqual(realpath('..'), dirname(os.getcwd()))
        self.assertEqual(realpath('../..'), dirname(dirname(os.getcwd())))
        self.assertEqual(realpath('/'.join(['..'] * 100)), '/')

    if hasattr(os, "symlink"):
        def test_realpath_basic(self):
            # Basic operation.
            try:
                os.symlink(ABSTFN+"1", ABSTFN)
                self.assertEqual(realpath(ABSTFN), ABSTFN+"1")
            finally:
                test_support.unlink(ABSTFN)

        def test_realpath_symlink_loops(self):
            # Bug #930024, return the path unchanged if we get into an infinite
            # symlink loop.
            try:
                os.symlink(ABSTFN, ABSTFN)
                self.assertEqual(realpath(ABSTFN), ABSTFN)

                os.symlink(ABSTFN+"1", ABSTFN+"2")
                os.symlink(ABSTFN+"2", ABSTFN+"1")
                self.assertEqual(realpath(ABSTFN+"1"), ABSTFN+"1")
                self.assertEqual(realpath(ABSTFN+"2"), ABSTFN+"2")

                self.assertEqual(realpath(ABSTFN+"1/x"), ABSTFN+"1/x")
                self.assertEqual(realpath(ABSTFN+"1/.."), dirname(ABSTFN))
                self.assertEqual(realpath(ABSTFN+"1/../x"), dirname(ABSTFN) + "/x")
                os.symlink(ABSTFN+"x", ABSTFN+"y")
                self.assertEqual(realpath(ABSTFN+"1/../" + basename(ABSTFN) + "y"),
                                ABSTFN + "y")
                self.assertEqual(realpath(ABSTFN+"1/../" + basename(ABSTFN) + "1"),
                                ABSTFN + "1")

                os.symlink(basename(ABSTFN) + "a/b", ABSTFN+"a")
                self.assertEqual(realpath(ABSTFN+"a"), ABSTFN+"a/b")

                os.symlink("../" + basename(dirname(ABSTFN)) + "/" +
                        basename(ABSTFN) + "c", ABSTFN+"c")
                self.assertEqual(realpath(ABSTFN+"c"), ABSTFN+"c")

                # Test using relative path as well.
                with support.change_cwd(dirname(ABSTFN)):
                    self.assertEqual(realpath(basename(ABSTFN)), ABSTFN)
            finally:
                test_support.unlink(ABSTFN)
                test_support.unlink(ABSTFN+"1")
                test_support.unlink(ABSTFN+"2")
                test_support.unlink(ABSTFN+"y")
                test_support.unlink(ABSTFN+"c")
                test_support.unlink(ABSTFN+"a")

        def test_realpath_repeated_indirect_symlinks(self):
            # Issue #6975.
            try:
                os.mkdir(ABSTFN)
                os.symlink('../' + basename(ABSTFN), ABSTFN + '/self')
                os.symlink('self/self/self', ABSTFN + '/link')
                self.assertEqual(realpath(ABSTFN + '/link'), ABSTFN)
            finally:
                test_support.unlink(ABSTFN + '/self')
                test_support.unlink(ABSTFN + '/link')
                safe_rmdir(ABSTFN)

        def test_realpath_deep_recursion(self):
            depth = 10
            try:
                os.mkdir(ABSTFN)
                for i in range(depth):
                    os.symlink('/'.join(['%d' % i] * 10), ABSTFN + '/%d' % (i + 1))
                os.symlink('.', ABSTFN + '/0')
                self.assertEqual(realpath(ABSTFN + '/%d' % depth), ABSTFN)

                # Test using relative path as well.
                with support.change_cwd(ABSTFN):
                    self.assertEqual(realpath('%d' % depth), ABSTFN)
            finally:
                for i in range(depth + 1):
                    test_support.unlink(ABSTFN + '/%d' % i)
                safe_rmdir(ABSTFN)

        def test_realpath_resolve_parents(self):
            # We also need to resolve any symlinks in the parents of a relative
            # path passed to realpath. E.g.: current working directory is
            # /usr/doc with 'doc' being a symlink to /usr/share/doc. We call
            # realpath("a"). This should return /usr/share/doc/a/.
            try:
                os.mkdir(ABSTFN)
                os.mkdir(ABSTFN + "/y")
                os.symlink(ABSTFN + "/y", ABSTFN + "/k")

                with support.change_cwd(ABSTFN + "/k"):
                    self.assertEqual(realpath("a"), ABSTFN + "/y/a")
            finally:
                test_support.unlink(ABSTFN + "/k")
                safe_rmdir(ABSTFN + "/y")
                safe_rmdir(ABSTFN)

        def test_realpath_resolve_before_normalizing(self):
            # Bug #990669: Symbolic links should be resolved before we
            # normalize the path. E.g.: if we have directories 'a', 'k' and 'y'
            # in the following hierarchy:
            # a/k/y
            #
            # and a symbolic link 'link-y' pointing to 'y' in directory 'a',
            # then realpath("link-y/..") should return 'k', not 'a'.
            try:
                os.mkdir(ABSTFN)
                os.mkdir(ABSTFN + "/k")
                os.mkdir(ABSTFN + "/k/y")
                os.symlink(ABSTFN + "/k/y", ABSTFN + "/link-y")

                # Absolute path.
                self.assertEqual(realpath(ABSTFN + "/link-y/.."), ABSTFN + "/k")
                # Relative path.
                with support.change_cwd(dirname(ABSTFN)):
                    self.assertEqual(realpath(basename(ABSTFN) + "/link-y/.."),
                                     ABSTFN + "/k")
            finally:
                test_support.unlink(ABSTFN + "/link-y")
                safe_rmdir(ABSTFN + "/k/y")
                safe_rmdir(ABSTFN + "/k")
                safe_rmdir(ABSTFN)

        def test_realpath_resolve_first(self):
            # Bug #1213894: The first component of the path, if not absolute,
            # must be resolved too.

            try:
                os.mkdir(ABSTFN)
                os.mkdir(ABSTFN + "/k")
                os.symlink(ABSTFN, ABSTFN + "link")
                with support.change_cwd(dirname(ABSTFN)):
                    base = basename(ABSTFN)
                    self.assertEqual(realpath(base + "link"), ABSTFN)
                    self.assertEqual(realpath(base + "link/k"), ABSTFN + "/k")
            finally:
                test_support.unlink(ABSTFN + "link")
                safe_rmdir(ABSTFN + "/k")
                safe_rmdir(ABSTFN)

    def test_relpath(self):
        (real_getcwd, os.getcwd) = (os.getcwd, lambda: r"/home/user/bar")
        try:
            curdir = os.path.split(os.getcwd())[-1]
            self.assertRaises(ValueError, posixpath.relpath, "")
            self.assertEqual(posixpath.relpath("a"), "a")
            self.assertEqual(posixpath.relpath(posixpath.abspath("a")), "a")
            self.assertEqual(posixpath.relpath("a/b"), "a/b")
            self.assertEqual(posixpath.relpath("../a/b"), "../a/b")
            self.assertEqual(posixpath.relpath("a", "../b"), "../"+curdir+"/a")
            self.assertEqual(posixpath.relpath("a/b", "../c"), "../"+curdir+"/a/b")
            self.assertEqual(posixpath.relpath("a", "b/c"), "../../a")
            self.assertEqual(posixpath.relpath("a", "a"), ".")
            self.assertEqual(posixpath.relpath("/foo/bar/bat", "/x/y/z"), '../../../foo/bar/bat')
            self.assertEqual(posixpath.relpath("/foo/bar/bat", "/foo/bar"), 'bat')
            self.assertEqual(posixpath.relpath("/foo/bar/bat", "/"), 'foo/bar/bat')
            self.assertEqual(posixpath.relpath("/", "/foo/bar/bat"), '../../..')
            self.assertEqual(posixpath.relpath("/foo/bar/bat", "/x"), '../foo/bar/bat')
            self.assertEqual(posixpath.relpath("/x", "/foo/bar/bat"), '../../../x')
            self.assertEqual(posixpath.relpath("/", "/"), '.')
            self.assertEqual(posixpath.relpath("/a", "/a"), '.')
            self.assertEqual(posixpath.relpath("/a/b", "/a/b"), '.')
        finally:
            os.getcwd = real_getcwd

    @unittest.skipUnless(test_support.FS_NONASCII, 'need test_support.FS_NONASCII')
    def test_expandvars_nonascii_word(self):
        encoding = sys.getfilesystemencoding()
        uwnonascii = test_support.FS_NONASCII
        swnonascii = uwnonascii.encode(encoding)
        if not swnonascii:
            self.skipTest('Needs non-ASCII word characters')
        with test_support.EnvironmentVarGuard() as env:
            env.clear()
            env[swnonascii] = 'baz' + swnonascii
            self.assertEqual(posixpath.expandvars(u'$%s bar' % uwnonascii),
                             u'baz%s bar' % uwnonascii)


class PosixCommonTest(test_genericpath.CommonTest):
    pathmodule = posixpath
    attributes = ['relpath', 'samefile', 'sameopenfile', 'samestat']


def test_main():
    test_support.run_unittest(PosixPathTest, PosixCommonTest)


if __name__=="__main__":
    test_main()
