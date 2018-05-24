#! /usr/bin/env python

"""
Usage:

python -m test.regrtest [options] [test_name1 [test_name2 ...]]
python path/to/Lib/test/regrtest.py [options] [test_name1 [test_name2 ...]]


If no arguments or options are provided, finds all files matching
the pattern "test_*" in the Lib/test subdirectory and runs
them in alphabetical order (but see -M and -u, below, for exceptions).

For more rigorous testing, it is useful to use the following
command line:

python -E -tt -Wd -3 -m test.regrtest [options] [test_name1 ...]


Options:

-h/--help       -- print this text and exit

Verbosity

-v/--verbose    -- run tests in verbose mode with output to stdout
-w/--verbose2   -- re-run failed tests in verbose mode
-W/--verbose3   -- re-run failed tests in verbose mode immediately
-q/--quiet      -- no output unless one or more tests fail
-S/--slowest    -- print the slowest 10 tests
   --header     -- print header with interpreter info

Selecting tests

-r/--randomize  -- randomize test execution order (see below)
   --randseed   -- pass a random seed to reproduce a previous random run
-f/--fromfile   -- read names of tests to run from a file (see below)
-x/--exclude    -- arguments are tests to *exclude*
-s/--single     -- single step through a set of tests (see below)
-m/--match PAT  -- match test cases and methods with glob pattern PAT
--matchfile FILENAME -- filters tests using a text file, one pattern per line
-G/--failfast   -- fail as soon as a test fails (only with -v or -W)
-u/--use RES1,RES2,...
                -- specify which special resource intensive tests to run
-M/--memlimit LIMIT
                -- run very large memory-consuming tests

Special runs

-l/--findleaks  -- if GC is available detect tests that leak memory
-L/--runleaks   -- run the leaks(1) command just before exit
-R/--huntrleaks RUNCOUNTS
                -- search for reference leaks (needs debug build, v. slow)
-j/--multiprocess PROCESSES
                -- run PROCESSES processes at once
-T/--coverage   -- turn on code coverage tracing using the trace module
-D/--coverdir DIRECTORY
                -- Directory where coverage files are put
-N/--nocoverdir -- Put coverage files alongside modules
-t/--threshold THRESHOLD
                -- call gc.set_threshold(THRESHOLD)
-F/--forever    -- run the specified tests in a loop, until an error happens
-P/--pgo        -- enable Profile Guided Optimization training
--testdir       -- execute test files in the specified directory
                   (instead of the Python stdlib test suite)
--list-tests    -- only write the name of tests that will be run,
                   don't execute them
--list-cases    -- only write the name of test cases that will be run,
                   don't execute them
--fail-env-changed  -- if a test file alters the environment, mark the test
                       as failed


Additional Option Details:

-r randomizes test execution order. You can use --randseed=int to provide an
int seed value for the randomizer; this is useful for reproducing troublesome
test orders.

-s On the first invocation of regrtest using -s, the first test file found
or the first test file given on the command line is run, and the name of
the next test is recorded in a file named pynexttest.  If run from the
Python build directory, pynexttest is located in the 'build' subdirectory,
otherwise it is located in tempfile.gettempdir().  On subsequent runs,
the test in pynexttest is run, and the next test is written to pynexttest.
When the last test has been run, pynexttest is deleted.  In this way it
is possible to single step through the test files.  This is useful when
doing memory analysis on the Python interpreter, which process tends to
consume too many resources to run the full regression test non-stop.

-f reads the names of tests from the file given as f's argument, one
or more test names per line.  Whitespace is ignored.  Blank lines and
lines beginning with '#' are ignored.  This is especially useful for
whittling down failures involving interactions among tests.

-L causes the leaks(1) command to be run just before exit if it exists.
leaks(1) is available on Mac OS X and presumably on some other
FreeBSD-derived systems.

-R runs each test several times and examines sys.gettotalrefcount() to
see if the test appears to be leaking references.  The argument should
be of the form stab:run:fname where 'stab' is the number of times the
test is run to let gettotalrefcount settle down, 'run' is the number
of times further it is run and 'fname' is the name of the file the
reports are written to.  These parameters all have defaults (5, 4 and
"reflog.txt" respectively), and the minimal invocation is '-R :'.

-M runs tests that require an exorbitant amount of memory. These tests
typically try to ascertain containers keep working when containing more than
2 billion objects, which only works on 64-bit systems. There are also some
tests that try to exhaust the address space of the process, which only makes
sense on 32-bit systems with at least 2Gb of memory. The passed-in memlimit,
which is a string in the form of '2.5Gb', determines howmuch memory the
tests will limit themselves to (but they may go slightly over.) The number
shouldn't be more memory than the machine has (including swap memory). You
should also keep in mind that swap memory is generally much, much slower
than RAM, and setting memlimit to all available RAM or higher will heavily
tax the machine. On the other hand, it is no use running these tests with a
limit of less than 2.5Gb, and many require more than 20Gb. Tests that expect
to use more than memlimit memory will be skipped. The big-memory tests
generally run very, very long.

-u is used to specify which special resource intensive tests to run,
such as those requiring large file support or network connectivity.
The argument is a comma-separated list of words indicating the
resources to test.  Currently only the following are defined:

    all -       Enable all special resources.

    audio -     Tests that use the audio device.  (There are known
                cases of broken audio drivers that can crash Python or
                even the Linux kernel.)

    curses -    Tests that use curses and will modify the terminal's
                state and output modes.

    largefile - It is okay to run some test that may create huge
                files.  These tests can take a long time and may
                consume >2GB of disk space temporarily.

    network -   It is okay to run tests that use external network
                resource, e.g. testing SSL support for sockets.

    bsddb -     It is okay to run the bsddb testsuite, which takes
                a long time to complete.

    decimal -   Test the decimal module against a large suite that
                verifies compliance with standards.

    cpu -       Used for certain CPU-heavy tests.

    subprocess  Run all tests for the subprocess module.

    urlfetch -  It is okay to download files required on testing.

    gui -       Run tests that require a running GUI.

    xpickle -   Test pickle and cPickle against Python 2.4, 2.5 and 2.6 to
                test backwards compatibility. These tests take a long time
                to run.

To enable all resources except one, use '-uall,-<resource>'.  For
example, to run all the tests except for the bsddb tests, give the
option '-uall,-bsddb'.

--matchfile filters tests using a text file, one pattern per line.
Pattern examples:

- test method: test_stat_attributes
- test class: FileTests
- test identifier: test_os.FileTests.test_stat_attributes
"""

import StringIO
import datetime
import getopt
import json
import os
import random
import re
import shutil
import sys
import time
import traceback
import warnings
import unittest
import tempfile
import imp
import platform
import sysconfig


# Some times __path__ and __file__ are not absolute (e.g. while running from
# Lib/) and, if we change the CWD to run the tests in a temporary dir, some
# imports might fail.  This affects only the modules imported before os.chdir().
# These modules are searched first in sys.path[0] (so '' -- the CWD) and if
# they are found in the CWD their __file__ and __path__ will be relative (this
# happens before the chdir).  All the modules imported after the chdir, are
# not found in the CWD, and since the other paths in sys.path[1:] are absolute
# (site.py absolutize them), the __file__ and __path__ will be absolute too.
# Therefore it is necessary to absolutize manually the __file__ and __path__ of
# the packages to prevent later imports to fail when the CWD is different.
for module in sys.modules.itervalues():
    if hasattr(module, '__path__'):
        module.__path__ = [os.path.abspath(path) for path in module.__path__]
    if hasattr(module, '__file__'):
        module.__file__ = os.path.abspath(module.__file__)


# MacOSX (a.k.a. Darwin) has a default stack size that is too small
# for deeply recursive regular expressions.  We see this as crashes in
# the Python test suite when running test_re.py and test_sre.py.  The
# fix is to set the stack limit to 2048.
# This approach may also be useful for other Unixy platforms that
# suffer from small default stack limits.
if sys.platform == 'darwin':
    try:
        import resource
    except ImportError:
        pass
    else:
        soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
        newsoft = min(hard, max(soft, 1024*2048))
        resource.setrlimit(resource.RLIMIT_STACK, (newsoft, hard))

# Windows, Tkinter, and resetting the environment after each test don't
# mix well.  To alleviate test failures due to Tcl/Tk not being able to
# find its library, get the necessary environment massage done once early.
if sys.platform == 'win32':
    try:
        import FixTk
    except Exception:
        pass

# Test result constants.
PASSED = 1
FAILED = 0
ENV_CHANGED = -1
SKIPPED = -2
RESOURCE_DENIED = -3
INTERRUPTED = -4
CHILD_ERROR = -5   # error in a child process

# Minimum duration of a test to display its duration or to mention that
# the test is running in background
PROGRESS_MIN_TIME = 30.0   # seconds

# Display the running tests if nothing happened last N seconds
PROGRESS_UPDATE = 30.0   # seconds

from test import test_support

ALL_RESOURCES = ('audio', 'curses', 'largefile', 'network', 'bsddb',
                 'decimal', 'cpu', 'subprocess', 'urlfetch', 'gui',
                 'xpickle')

# Other resources excluded from --use=all:
#
# - extralagefile (ex: test_zipfile64): really too slow to be enabled
#   "by default"
RESOURCE_NAMES = ALL_RESOURCES + ('extralargefile',)

TEMPDIR = os.path.abspath(tempfile.gettempdir())


def usage(code, msg=''):
    print __doc__
    if msg: print msg
    sys.exit(code)


def format_duration(seconds):
    if seconds < 1.0:
        return '%.0f ms' % (seconds * 1e3)
    if seconds < 60.0:
        return '%.0f sec' % seconds

    minutes, seconds = divmod(seconds, 60.0)
    return '%.0f min %.0f sec' % (minutes, seconds)


_FORMAT_TEST_RESULT = {
    PASSED: '%s passed',
    FAILED: '%s failed',
    ENV_CHANGED: '%s failed (env changed)',
    SKIPPED: '%s skipped',
    RESOURCE_DENIED: '%s skipped (resource denied)',
    INTERRUPTED: '%s interrupted',
    CHILD_ERROR: '%s crashed',
}


def format_test_result(test_name, result):
    fmt = _FORMAT_TEST_RESULT.get(result, "%s")
    return fmt % test_name


def cpu_count():
    # first try os.sysconf() to prevent loading the big multiprocessing module
    try:
        return os.sysconf('SC_NPROCESSORS_ONLN')
    except (AttributeError, ValueError):
        pass

    # try multiprocessing.cpu_count()
    try:
        import multiprocessing
    except ImportError:
        pass
    else:
        return multiprocessing.cpu_count()

    return None


def unload_test_modules(save_modules):
    # Unload the newly imported modules (best effort finalization)
    for module in sys.modules.keys():
        if module not in save_modules and module.startswith("test."):
            test_support.unload(module)


def main(tests=None, testdir=None, verbose=0, quiet=False,
         exclude=False, single=False, randomize=False, fromfile=None,
         findleaks=False, use_resources=None, trace=False, coverdir='coverage',
         runleaks=False, huntrleaks=False, verbose2=False, print_slow=False,
         random_seed=None, use_mp=None, verbose3=False, forever=False,
         header=False, pgo=False, failfast=False, match_tests=None):
    """Execute a test suite.

    This also parses command-line options and modifies its behavior
    accordingly.

    tests -- a list of strings containing test names (optional)
    testdir -- the directory in which to look for tests (optional)

    Users other than the Python test suite will certainly want to
    specify testdir; if it's omitted, the directory containing the
    Python test suite is searched for.

    If the tests argument is omitted, the tests listed on the
    command-line will be used.  If that's empty, too, then all *.py
    files beginning with test_ will be used.

    The other default arguments (verbose, quiet, exclude,
    single, randomize, findleaks, use_resources, trace, coverdir,
    print_slow, and random_seed) allow programmers calling main()
    directly to set the values that would normally be set by flags
    on the command line.
    """
    regrtest_start_time = time.time()

    test_support.record_original_stdout(sys.stdout)
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hvqxsSrf:lu:t:TD:NLR:FwWM:j:PGm:',
            ['help', 'verbose', 'verbose2', 'verbose3', 'quiet',
             'exclude', 'single', 'slow', 'slowest', 'randomize', 'fromfile=',
             'findleaks',
             'use=', 'threshold=', 'trace', 'coverdir=', 'nocoverdir',
             'runleaks', 'huntrleaks=', 'memlimit=', 'randseed=',
             'multiprocess=', 'slaveargs=', 'forever', 'header', 'pgo',
             'failfast', 'match=', 'testdir=', 'list-tests', 'list-cases',
             'coverage', 'matchfile=', 'fail-env-changed'])
    except getopt.error, msg:
        usage(2, msg)

    # Defaults
    if random_seed is None:
        random_seed = random.randrange(10000000)
    if use_resources is None:
        use_resources = []
    slaveargs = None
    list_tests = False
    list_cases_opt = False
    fail_env_changed = False
    for o, a in opts:
        if o in ('-h', '--help'):
            usage(0)
        elif o in ('-v', '--verbose'):
            verbose += 1
        elif o in ('-w', '--verbose2'):
            verbose2 = True
        elif o in ('-W', '--verbose3'):
            verbose3 = True
        elif o in ('-G', '--failfast'):
            failfast = True
        elif o in ('-q', '--quiet'):
            quiet = True;
            verbose = 0
        elif o in ('-x', '--exclude'):
            exclude = True
        elif o in ('-s', '--single'):
            single = True
        elif o in ('-S', '--slow', '--slowest'):
            print_slow = True
        elif o in ('-r', '--randomize'):
            randomize = True
        elif o == '--randseed':
            random_seed = int(a)
        elif o in ('-f', '--fromfile'):
            fromfile = a
        elif o in ('-m', '--match'):
            if match_tests is None:
                match_tests = []
            match_tests.append(a)
        elif o == '--matchfile':
            if match_tests is None:
                match_tests = []
            filename = os.path.join(test_support.SAVEDCWD, a)
            with open(filename) as fp:
                for line in fp:
                    match_tests.append(line.strip())
        elif o in ('-l', '--findleaks'):
            findleaks = True
        elif o in ('-L', '--runleaks'):
            runleaks = True
        elif o in ('-t', '--threshold'):
            import gc
            gc.set_threshold(int(a))
        elif o in ('-T', '--coverage'):
            trace = True
        elif o in ('-D', '--coverdir'):
            coverdir = os.path.join(os.getcwd(), a)
        elif o in ('-N', '--nocoverdir'):
            coverdir = None
        elif o in ('-R', '--huntrleaks'):
            huntrleaks = a.split(':')
            if len(huntrleaks) not in (2, 3):
                print a, huntrleaks
                usage(2, '-R takes 2 or 3 colon-separated arguments')
            if not huntrleaks[0]:
                huntrleaks[0] = 5
            else:
                huntrleaks[0] = int(huntrleaks[0])
            if not huntrleaks[1]:
                huntrleaks[1] = 4
            else:
                huntrleaks[1] = int(huntrleaks[1])
            if len(huntrleaks) == 2 or not huntrleaks[2]:
                huntrleaks[2:] = ["reflog.txt"]
        elif o in ('-M', '--memlimit'):
            test_support.set_memlimit(a)
        elif o in ('-u', '--use'):
            u = [x.lower() for x in a.split(',')]
            for r in u:
                if r == 'all':
                    use_resources[:] = ALL_RESOURCES
                    continue
                remove = False
                if r[0] == '-':
                    remove = True
                    r = r[1:]
                if r not in RESOURCE_NAMES:
                    usage(1, 'Invalid -u/--use option: ' + a)
                if remove:
                    if r in use_resources:
                        use_resources.remove(r)
                elif r not in use_resources:
                    use_resources.append(r)
        elif o in ('-F', '--forever'):
            forever = True
        elif o in ('-j', '--multiprocess'):
            use_mp = int(a)
        elif o == '--header':
            header = True
        elif o == '--slaveargs':
            slaveargs = a
        elif o in ('-P', '--pgo'):
            pgo = True
        elif o == '--testdir':
            testdir = a
        elif o == '--list-tests':
            list_tests = True
        elif o == '--list-cases':
            list_cases_opt = True
        elif o == '--fail-env-changed':
            fail_env_changed = True
        else:
            print >>sys.stderr, ("No handler for option {}.  Please "
                "report this as a bug at http://bugs.python.org.").format(o)
            sys.exit(1)
    if single and fromfile:
        usage(2, "-s and -f don't go together!")
    if use_mp and trace:
        usage(2, "-T and -j don't go together!")
    if use_mp and findleaks:
        usage(2, "-l and -j don't go together!")
    if failfast and not (verbose or verbose3):
        usage("-G/--failfast needs either -v or -W")

    if testdir:
        testdir = os.path.abspath(testdir)

        # Prepend test directory to sys.path, so runtest() will be able
        # to locate tests
        sys.path.insert(0, testdir)

    # Make sure that '' and Lib/test/ are not in sys.path
    regrtest_dir = os.path.abspath(os.path.dirname(__file__))
    for path in ('', regrtest_dir):
        try:
            sys.path.remove(path)
        except ValueError:
            pass

    if slaveargs is not None:
        args, kwargs = json.loads(slaveargs)
        if kwargs['huntrleaks']:
            warm_caches()
        if testdir:
            kwargs['testdir'] = testdir
        try:
            result = runtest(*args, **kwargs)
        except BaseException, e:
            result = INTERRUPTED, e.__class__.__name__
        print   # Force a newline (just in case)
        print json.dumps(result)
        sys.exit(0)

    if huntrleaks:
        warm_caches()

    good = []
    bad = []
    skipped = []
    resource_denieds = []
    environment_changed = []
    interrupted = False

    if findleaks:
        try:
            import gc
        except ImportError:
            print 'No GC available, disabling findleaks.'
            findleaks = False
        else:
            # Uncomment the line below to report garbage that is not
            # freeable by reference counting alone.  By default only
            # garbage that is not collectable by the GC is reported.
            #gc.set_debug(gc.DEBUG_SAVEALL)
            found_garbage = []

    if single:
        filename = os.path.join(TEMPDIR, 'pynexttest')
        try:
            fp = open(filename, 'r')
            next_test = fp.read().strip()
            tests = [next_test]
            fp.close()
        except IOError:
            pass

    if fromfile:
        tests = []
        fp = open(os.path.join(test_support.SAVEDCWD, fromfile))
        for line in fp:
            guts = line.split() # assuming no test has whitespace in its name
            if guts and not guts[0].startswith('#'):
                tests.extend(guts)
        fp.close()

    # Strip .py extensions.
    removepy(args)
    removepy(tests)

    stdtests = STDTESTS[:]
    nottests = NOTTESTS.copy()
    if exclude:
        for arg in args:
            if arg in stdtests:
                stdtests.remove(arg)
            nottests.add(arg)
        args = []

    display_header = (verbose or header or not (quiet or single or tests or args)) and (not pgo)
    alltests = findtests(testdir, stdtests, nottests)
    selected = tests or args or alltests
    if single:
        selected = selected[:1]
        try:
            next_single_test = alltests[alltests.index(selected[0])+1]
        except IndexError:
            next_single_test = None

    if list_tests:
        for name in selected:
            print(name)
        sys.exit(0)

    if list_cases_opt:
        list_cases(testdir, selected, match_tests)
        sys.exit(0)

    if trace:
        import trace
        tracer = trace.Trace(trace=False, count=True)

    test_times = []
    test_support.use_resources = use_resources
    save_modules = set(sys.modules)

    def accumulate_result(test, result):
        ok, test_time = result
        if ok not in (CHILD_ERROR, INTERRUPTED):
            test_times.append((test_time, test))
        if ok == PASSED:
            good.append(test)
        elif ok in (FAILED, CHILD_ERROR):
            bad.append(test)
        elif ok == ENV_CHANGED:
            environment_changed.append(test)
        elif ok == SKIPPED:
            skipped.append(test)
        elif ok == RESOURCE_DENIED:
            skipped.append(test)
            resource_denieds.append(test)
        elif ok != INTERRUPTED:
            raise ValueError("invalid test result: %r" % ok)

    if forever:
        def test_forever(tests=list(selected)):
            while True:
                for test in tests:
                    yield test
                    if bad:
                        return
                    if fail_env_changed and environment_changed:
                        return
        tests = test_forever()
        test_count = ''
        test_count_width = 3
    else:
        tests = iter(selected)
        test_count = '/{}'.format(len(selected))
        test_count_width = len(test_count) - 1

    def display_progress(test_index, test):
        # "[ 51/405/1] test_tcl"
        line = "{1:{0}}{2}".format(test_count_width, test_index, test_count)
        if bad and not pgo:
            line = '{}/{}'.format(line, len(bad))
        line = '[{}]'.format(line)

        # add the system load prefix: "load avg: 1.80 "
        if hasattr(os, 'getloadavg'):
            load_avg_1min = os.getloadavg()[0]
            line = "load avg: {:.2f} {}".format(load_avg_1min, line)

        # add the timestamp prefix:  "0:01:05 "
        test_time = time.time() - regrtest_start_time
        test_time = datetime.timedelta(seconds=int(test_time))
        line = "%s %s" % (test_time, line)

        # add the test name
        line = "{} {}".format(line, test)

        print(line)
        sys.stdout.flush()

    # For a partial run, we do not need to clutter the output.
    if display_header:
        # Print basic platform information
        print "==", platform.python_implementation(), \
                    " ".join(sys.version.split())
        print "==  ", platform.platform(aliased=True), \
                      "%s-endian" % sys.byteorder
        print "==  ", os.getcwd()
        ncpu = cpu_count()
        if ncpu:
            print "== CPU count:", ncpu

    if randomize:
        random.seed(random_seed)
        print "Using random seed", random_seed
        random.shuffle(selected)

    if use_mp:
        try:
            from threading import Thread
        except ImportError:
            print "Multiprocess option requires thread support"
            sys.exit(2)
        from Queue import Queue, Empty
        from subprocess import Popen, PIPE
        debug_output_pat = re.compile(r"\[\d+ refs\]$")
        output = Queue()
        def tests_and_args():
            for test in tests:
                args_tuple = (
                    (test, verbose, quiet),
                    dict(huntrleaks=huntrleaks, use_resources=use_resources,
                         failfast=failfast,
                         match_tests=match_tests,
                         pgo=pgo)
                )
                yield (test, args_tuple)
        pending = tests_and_args()
        opt_args = test_support.args_from_interpreter_flags()
        base_cmd = [sys.executable] + opt_args + ['-m', 'test.regrtest']
        # required to spawn a new process with PGO flag on/off
        if pgo:
            base_cmd = base_cmd + ['--pgo']

        class MultiprocessThread(Thread):
            current_test = None
            start_time = None

            def runtest(self):
                try:
                    test, args_tuple = next(pending)
                except StopIteration:
                    output.put((None, None, None, None))
                    return True

                # -E is needed by some tests, e.g. test_import
                args = base_cmd + ['--slaveargs', json.dumps(args_tuple)]
                if testdir:
                    args.extend(('--testdir', testdir))
                try:
                    self.start_time = time.time()
                    self.current_test = test
                    popen = Popen(args,
                                  stdout=PIPE, stderr=PIPE,
                                  universal_newlines=True,
                                  close_fds=(os.name != 'nt'))
                    stdout, stderr = popen.communicate()
                    retcode = popen.wait()
                finally:
                    self.current_test = None

                # Strip last refcount output line if it exists, since it
                # comes from the shutdown of the interpreter in the subcommand.
                stderr = debug_output_pat.sub("", stderr)

                if retcode == 0:
                    stdout, _, result = stdout.strip().rpartition("\n")
                    if not result:
                        output.put((None, None, None, None))
                        return True

                    result = json.loads(result)
                else:
                    result = (CHILD_ERROR, "Exit code %s" % retcode)

                output.put((test, stdout.rstrip(), stderr.rstrip(), result))
                return False

            def run(self):
                try:
                    stop = False
                    while not stop:
                        stop = self.runtest()
                except BaseException:
                    output.put((None, None, None, None))
                    raise

        workers = [MultiprocessThread() for i in range(use_mp)]
        print("Run tests in parallel using %s child processes"
              % len(workers))
        for worker in workers:
            worker.start()

        def get_running(workers):
            running = []
            for worker in workers:
                current_test = worker.current_test
                if not current_test:
                    continue
                dt = time.time() - worker.start_time
                if dt >= PROGRESS_MIN_TIME:
                    running.append('%s (%.0f sec)' % (current_test, dt))
            return running

        finished = 0
        test_index = 1
        get_timeout = max(PROGRESS_UPDATE, PROGRESS_MIN_TIME)
        try:
            while finished < use_mp:
                try:
                    item = output.get(timeout=get_timeout)
                except Empty:
                    running = get_running(workers)
                    if running and not pgo:
                        print('running: %s' % ', '.join(running))
                    continue

                test, stdout, stderr, result = item
                if test is None:
                    finished += 1
                    continue
                accumulate_result(test, result)
                if not quiet:
                    ok, test_time = result
                    text = format_test_result(test, ok)
                    if (ok not in (CHILD_ERROR, INTERRUPTED)
                        and test_time >= PROGRESS_MIN_TIME
                        and not pgo):
                        text += ' (%.0f sec)' % test_time
                    running = get_running(workers)
                    if running and not pgo:
                        text += ' -- running: %s' % ', '.join(running)
                    display_progress(test_index, text)

                if stdout:
                    print stdout
                sys.stdout.flush()
                if stderr and not pgo:
                    print >>sys.stderr, stderr
                sys.stderr.flush()

                if result[0] == INTERRUPTED:
                    assert result[1] == 'KeyboardInterrupt'
                    raise KeyboardInterrupt   # What else?

                test_index += 1
        except KeyboardInterrupt:
            interrupted = True
            pending.close()
        for worker in workers:
            worker.join()
    else:
        print("Run tests sequentially")

        previous_test = None
        for test_index, test in enumerate(tests, 1):
            if not quiet:
                text = test
                if previous_test:
                    text = '%s -- %s' % (text, previous_test)
                display_progress(test_index, text)

            def local_runtest():
                result = runtest(test, verbose, quiet, huntrleaks, None, pgo,
                                 failfast=failfast,
                                 match_tests=match_tests,
                                 testdir=testdir)
                accumulate_result(test, result)
                return result

            start_time = time.time()
            if trace:
                # If we're tracing code coverage, then we don't exit with status
                # if on a false return value from main.
                ns = dict(locals())
                tracer.runctx('result = local_runtest()',
                              globals=globals(), locals=ns)
                result = ns['result']
            else:
                try:
                    result = local_runtest()
                    if verbose3 and result[0] == FAILED:
                        if not pgo:
                            print "Re-running test %r in verbose mode" % test
                        runtest(test, True, quiet, huntrleaks, None, pgo,
                                testdir=testdir)
                except KeyboardInterrupt:
                    interrupted = True
                    break
                except:
                    raise

            test_time = time.time() - start_time
            previous_test = format_test_result(test, result[0])
            if test_time >= PROGRESS_MIN_TIME:
                previous_test = "%s in %s" % (previous_test,
                                              format_duration(test_time))
            elif result[0] == PASSED:
                # be quiet: say nothing if the test passed shortly
                previous_test = None

            if findleaks:
                gc.collect()
                if gc.garbage:
                    print "Warning: test created", len(gc.garbage),
                    print "uncollectable object(s)."
                    # move the uncollectable objects somewhere so we don't see
                    # them again
                    found_garbage.extend(gc.garbage)
                    del gc.garbage[:]

            unload_test_modules(save_modules)

    if interrupted and not pgo:
        # print a newline after ^C
        print
        print "Test suite interrupted by signal SIGINT."
        omitted = set(selected) - set(good) - set(bad) - set(skipped)
        print count(len(omitted), "test"), "omitted:"
        printlist(omitted)
    if good and not quiet and not pgo:
        if not bad and not skipped and not interrupted and len(good) > 1:
            print "All",
        print count(len(good), "test"), "OK."
    if print_slow:
        test_times.sort(reverse=True)
        print "10 slowest tests:"
        for test_time, test in test_times[:10]:
            print("- %s: %.1fs" % (test, test_time))
    if bad and not pgo:
        print count(len(bad), "test"), "failed:"
        printlist(bad)
    if environment_changed and not pgo:
        print "{} altered the execution environment:".format(
            count(len(environment_changed), "test"))
        printlist(environment_changed)
    if skipped and not quiet and not pgo:
        print count(len(skipped), "test"), "skipped:"
        printlist(skipped)

        e = _ExpectedSkips()
        plat = sys.platform
        if e.isvalid():
            surprise = set(skipped) - e.getexpected() - set(resource_denieds)
            if surprise:
                print count(len(surprise), "skip"), \
                      "unexpected on", plat + ":"
                printlist(surprise)
            else:
                print "Those skips are all expected on", plat + "."
        else:
            print "Ask someone to teach regrtest.py about which tests are"
            print "expected to get skipped on", plat + "."

    if verbose2 and bad:
        print "Re-running failed tests in verbose mode"
        for test in bad[:]:
            print "Re-running test %r in verbose mode" % test
            sys.stdout.flush()
            try:
                test_support.verbose = True
                ok = runtest(test, True, quiet, huntrleaks, None, pgo,
                             testdir=testdir)
            except KeyboardInterrupt:
                # print a newline separate from the ^C
                print
                break
            else:
                if ok[0] in {PASSED, ENV_CHANGED, SKIPPED, RESOURCE_DENIED}:
                    bad.remove(test)
        else:
            if bad:
                print count(len(bad), "test"), "failed again:"
                printlist(bad)

    if single:
        if next_single_test:
            with open(filename, 'w') as fp:
                fp.write(next_single_test + '\n')
        else:
            os.unlink(filename)

    if trace:
        r = tracer.results()
        r.write_results(show_missing=True, summary=True, coverdir=coverdir)

    if runleaks:
        os.system("leaks %d" % os.getpid())

    print
    duration = time.time() - regrtest_start_time
    print("Total duration: %s" % format_duration(duration))

    if bad:
        result = "FAILURE"
    elif interrupted:
        result = "INTERRUPTED"
    elif fail_env_changed and environment_changed:
        result = "ENV CHANGED"
    else:
        result = "SUCCESS"
    print("Tests result: %s" % result)

    if bad:
        sys.exit(2)
    if interrupted:
        sys.exit(130)
    if fail_env_changed and environment_changed:
        sys.exit(3)
    sys.exit(0)


STDTESTS = [
    'test_grammar',
    'test_opcodes',
    'test_dict',
    'test_builtin',
    'test_exceptions',
    'test_types',
    'test_unittest',
    'test_doctest',
    'test_doctest2',
]

NOTTESTS = {
    'test_support',
    'test_future1',
    'test_future2',
}

def findtests(testdir=None, stdtests=STDTESTS, nottests=NOTTESTS):
    """Return a list of all applicable test modules."""
    testdir = findtestdir(testdir)
    names = os.listdir(testdir)
    tests = []
    others = set(stdtests) | nottests
    for name in names:
        modname, ext = os.path.splitext(name)
        if modname[:5] == "test_" and ext == ".py" and modname not in others:
            tests.append(modname)
    return stdtests + sorted(tests)

def runtest(test, verbose, quiet,
            huntrleaks=False, use_resources=None, pgo=False,
            failfast=False, match_tests=None, testdir=None):
    """Run a single test.

    test -- the name of the test
    verbose -- if true, print more messages
    quiet -- if true, don't print 'skipped' messages (probably redundant)
    test_times -- a list of (time, test_name) pairs
    huntrleaks -- run multiple times to test for leaks; requires a debug
                  build; a triple corresponding to -R's three arguments
    pgo -- if true, do not print unnecessary info when running the test
           for Profile Guided Optimization build

    Returns one of the test result constants:
        CHILD_ERROR      Child process crashed
        INTERRUPTED      KeyboardInterrupt when run under -j
        RESOURCE_DENIED  test skipped because resource denied
        SKIPPED          test skipped for some other reason
        ENV_CHANGED      test failed because it changed the execution environment
        FAILED           test failed
        PASSED           test passed
    """

    test_support.verbose = verbose  # Tell tests to be moderately quiet
    if use_resources is not None:
        test_support.use_resources = use_resources
    try:
        test_support.set_match_tests(match_tests)
        if failfast:
            test_support.failfast = True
        return runtest_inner(test, verbose, quiet, huntrleaks, pgo, testdir)
    finally:
        cleanup_test_droppings(test, verbose)


# Unit tests are supposed to leave the execution environment unchanged
# once they complete.  But sometimes tests have bugs, especially when
# tests fail, and the changes to environment go on to mess up other
# tests.  This can cause issues with buildbot stability, since tests
# are run in random order and so problems may appear to come and go.
# There are a few things we can save and restore to mitigate this, and
# the following context manager handles this task.

class saved_test_environment:
    """Save bits of the test environment and restore them at block exit.

        with saved_test_environment(testname, verbose, quiet):
            #stuff

    Unless quiet is True, a warning is printed to stderr if any of
    the saved items was changed by the test.  The attribute 'changed'
    is initially False, but is set to True if a change is detected.

    If verbose is more than 1, the before and after state of changed
    items is also printed.
    """

    changed = False

    def __init__(self, testname, verbose=0, quiet=False, pgo=False):
        self.testname = testname
        self.verbose = verbose
        self.quiet = quiet
        self.pgo = pgo

    # To add things to save and restore, add a name XXX to the resources list
    # and add corresponding get_XXX/restore_XXX functions.  get_XXX should
    # return the value to be saved and compared against a second call to the
    # get function when test execution completes.  restore_XXX should accept
    # the saved value and restore the resource using it.  It will be called if
    # and only if a change in the value is detected.
    #
    # Note: XXX will have any '.' replaced with '_' characters when determining
    # the corresponding method names.

    resources = ('sys.argv', 'cwd', 'sys.stdin', 'sys.stdout', 'sys.stderr',
                 'os.environ', 'sys.path', 'asyncore.socket_map',
                 'files',
                )

    def get_sys_argv(self):
        return id(sys.argv), sys.argv, sys.argv[:]
    def restore_sys_argv(self, saved_argv):
        sys.argv = saved_argv[1]
        sys.argv[:] = saved_argv[2]

    def get_cwd(self):
        return os.getcwd()
    def restore_cwd(self, saved_cwd):
        os.chdir(saved_cwd)

    def get_sys_stdout(self):
        return sys.stdout
    def restore_sys_stdout(self, saved_stdout):
        sys.stdout = saved_stdout

    def get_sys_stderr(self):
        return sys.stderr
    def restore_sys_stderr(self, saved_stderr):
        sys.stderr = saved_stderr

    def get_sys_stdin(self):
        return sys.stdin
    def restore_sys_stdin(self, saved_stdin):
        sys.stdin = saved_stdin

    def get_os_environ(self):
        return id(os.environ), os.environ, dict(os.environ)
    def restore_os_environ(self, saved_environ):
        os.environ = saved_environ[1]
        os.environ.clear()
        os.environ.update(saved_environ[2])

    def get_sys_path(self):
        return id(sys.path), sys.path, sys.path[:]
    def restore_sys_path(self, saved_path):
        sys.path = saved_path[1]
        sys.path[:] = saved_path[2]

    def get_asyncore_socket_map(self):
        asyncore = sys.modules.get('asyncore')
        # XXX Making a copy keeps objects alive until __exit__ gets called.
        return asyncore and asyncore.socket_map.copy() or {}
    def restore_asyncore_socket_map(self, saved_map):
        asyncore = sys.modules.get('asyncore')
        if asyncore is not None:
            asyncore.close_all(ignore_all=True)
            asyncore.socket_map.update(saved_map)

    def get_test_support_TESTFN(self):
        if os.path.isfile(test_support.TESTFN):
            result = 'f'
        elif os.path.isdir(test_support.TESTFN):
            result = 'd'
        else:
            result = None
        return result
    def restore_test_support_TESTFN(self, saved_value):
        if saved_value is None:
            if os.path.isfile(test_support.TESTFN):
                os.unlink(test_support.TESTFN)
            elif os.path.isdir(test_support.TESTFN):
                shutil.rmtree(test_support.TESTFN)

    def get_files(self):
        return sorted(fn + ('/' if os.path.isdir(fn) else '')
                      for fn in os.listdir(os.curdir))
    def restore_files(self, saved_value):
        fn = test_support.TESTFN
        if fn not in saved_value and (fn + '/') not in saved_value:
            if os.path.isfile(fn):
                test_support.unlink(fn)
            elif os.path.isdir(fn):
                test_support.rmtree(fn)

    def resource_info(self):
        for name in self.resources:
            method_suffix = name.replace('.', '_')
            get_name = 'get_' + method_suffix
            restore_name = 'restore_' + method_suffix
            yield name, getattr(self, get_name), getattr(self, restore_name)

    def __enter__(self):
        self.saved_values = dict((name, get()) for name, get, restore
                                                   in self.resource_info())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        saved_values = self.saved_values
        del self.saved_values
        for name, get, restore in self.resource_info():
            current = get()
            original = saved_values.pop(name)
            # Check for changes to the resource's value
            if current != original:
                self.changed = True
                restore(original)
                if not self.quiet and not self.pgo:
                    print >>sys.stderr, (
                          "Warning -- {} was modified by {}".format(
                                                 name, self.testname))
                    print >>sys.stderr, (
                          "  Before: {}\n  After:  {} ".format(
                                              original, current))
            # XXX (ncoghlan): for most resources (e.g. sys.path) identity
            # matters at least as much as value. For others (e.g. cwd),
            # identity is irrelevant. Should we add a mechanism to check
            # for substitution in the cases where it matters?
        return False


def post_test_cleanup():
    test_support.reap_children()

def runtest_inner(test, verbose, quiet, huntrleaks=False, pgo=False, testdir=None):
    test_support.unload(test)
    if verbose:
        capture_stdout = None
    else:
        capture_stdout = StringIO.StringIO()

    test_time = 0.0
    refleak = False  # True if the test leaked references.
    try:
        save_stdout = sys.stdout
        try:
            if capture_stdout:
                sys.stdout = capture_stdout
            abstest = get_abs_module(testdir, test)
            clear_caches()
            with saved_test_environment(test, verbose, quiet, pgo) as environment:
                start_time = time.time()
                the_package = __import__(abstest, globals(), locals(), [])
                if abstest.startswith('test.'):
                    the_module = getattr(the_package, test)
                else:
                    the_module = the_package
                # Old tests run to completion simply as a side-effect of
                # being imported.  For tests based on unittest or doctest,
                # explicitly invoke their test_main() function (if it exists).
                indirect_test = getattr(the_module, "test_main", None)
                if indirect_test is not None:
                    indirect_test()
                if huntrleaks:
                    refleak = dash_R(the_module, test, indirect_test,
                        huntrleaks)
                test_time = time.time() - start_time
            post_test_cleanup()
        finally:
            sys.stdout = save_stdout
    except test_support.ResourceDenied, msg:
        if not quiet and not pgo:
            print test, "skipped --", msg
            sys.stdout.flush()
        return RESOURCE_DENIED, test_time
    except unittest.SkipTest, msg:
        if not quiet and not pgo:
            print test, "skipped --", msg
            sys.stdout.flush()
        return SKIPPED, test_time
    except KeyboardInterrupt:
        raise
    except test_support.TestFailed, msg:
        if not pgo:
            print >>sys.stderr, "test", test, "failed --", msg
        sys.stderr.flush()
        return FAILED, test_time
    except:
        type, value = sys.exc_info()[:2]
        if not pgo:
            print >>sys.stderr, "test", test, "crashed --", str(type) + ":", value
        sys.stderr.flush()
        if verbose and not pgo:
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
        return FAILED, test_time
    else:
        if refleak:
            return FAILED, test_time
        if environment.changed:
            return ENV_CHANGED, test_time
        # Except in verbose mode, tests should not print anything
        if verbose or huntrleaks:
            return PASSED, test_time
        output = capture_stdout.getvalue()
        if not output:
            return PASSED, test_time
        print "test", test, "produced unexpected output:"
        print "*" * 70
        print output
        print "*" * 70
        sys.stdout.flush()
        return FAILED, test_time

def cleanup_test_droppings(testname, verbose):
    import stat
    import gc

    # First kill any dangling references to open files etc.
    gc.collect()

    # Try to clean up junk commonly left behind.  While tests shouldn't leave
    # any files or directories behind, when a test fails that can be tedious
    # for it to arrange.  The consequences can be especially nasty on Windows,
    # since if a test leaves a file open, it cannot be deleted by name (while
    # there's nothing we can do about that here either, we can display the
    # name of the offending test, which is a real help).
    for name in (test_support.TESTFN,
                 "db_home",
                ):
        if not os.path.exists(name):
            continue

        if os.path.isdir(name):
            kind, nuker = "directory", shutil.rmtree
        elif os.path.isfile(name):
            kind, nuker = "file", os.unlink
        else:
            raise SystemError("os.path says %r exists but is neither "
                              "directory nor file" % name)

        if verbose:
            print "%r left behind %s %r" % (testname, kind, name)
        try:
            # if we have chmod, fix possible permissions problems
            # that might prevent cleanup
            if (hasattr(os, 'chmod')):
                os.chmod(name, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            nuker(name)
        except Exception, msg:
            print >> sys.stderr, ("%r left behind %s %r and it couldn't be "
                "removed: %s" % (testname, kind, name, msg))

def dash_R(the_module, test, indirect_test, huntrleaks):
    """Run a test multiple times, looking for reference leaks.

    Returns:
        False if the test didn't leak references; True if we detected refleaks.
    """
    # This code is hackish and inelegant, but it seems to do the job.
    import copy_reg, _abcoll, _pyio

    if not hasattr(sys, 'gettotalrefcount'):
        raise Exception("Tracking reference leaks requires a debug build "
                        "of Python")

    # Save current values for dash_R_cleanup() to restore.
    fs = warnings.filters[:]
    ps = copy_reg.dispatch_table.copy()
    pic = sys.path_importer_cache.copy()
    try:
        import zipimport
    except ImportError:
        zdc = None # Run unmodified on platforms without zipimport support
    else:
        zdc = zipimport._zip_directory_cache.copy()
    abcs = {}
    modules = _abcoll, _pyio
    for abc in [getattr(mod, a) for mod in modules for a in mod.__all__]:
        # XXX isinstance(abc, ABCMeta) leads to infinite recursion
        if not hasattr(abc, '_abc_registry'):
            continue
        for obj in abc.__subclasses__() + [abc]:
            abcs[obj] = obj._abc_registry.copy()

    if indirect_test:
        def run_the_test():
            indirect_test()
    else:
        def run_the_test():
            imp.reload(the_module)

    deltas = []
    nwarmup, ntracked, fname = huntrleaks
    fname = os.path.join(test_support.SAVEDCWD, fname)
    repcount = nwarmup + ntracked
    print >> sys.stderr, "beginning", repcount, "repetitions"
    print >> sys.stderr, ("1234567890"*(repcount//10 + 1))[:repcount]
    dash_R_cleanup(fs, ps, pic, zdc, abcs)
    for i in range(repcount):
        rc_before = sys.gettotalrefcount()
        run_the_test()
        sys.stderr.write('.')
        dash_R_cleanup(fs, ps, pic, zdc, abcs)
        rc_after = sys.gettotalrefcount()
        if i >= nwarmup:
            deltas.append(rc_after - rc_before)
    print >> sys.stderr

    # bpo-30776: Try to ignore false positives:
    #
    #   [3, 0, 0]
    #   [0, 1, 0]
    #   [8, -8, 1]
    #
    # Expected leaks:
    #
    #   [5, 5, 6]
    #   [10, 1, 1]
    if all(delta >= 1 for delta in deltas):
        msg = '%s leaked %s references, sum=%s' % (test, deltas, sum(deltas))
        print >> sys.stderr, msg
        with open(fname, "a") as refrep:
            print >> refrep, msg
            refrep.flush()
        return True
    return False

def dash_R_cleanup(fs, ps, pic, zdc, abcs):
    import gc, copy_reg

    # Restore some original values.
    warnings.filters[:] = fs
    copy_reg.dispatch_table.clear()
    copy_reg.dispatch_table.update(ps)
    sys.path_importer_cache.clear()
    sys.path_importer_cache.update(pic)
    try:
        import zipimport
    except ImportError:
        pass # Run unmodified on platforms without zipimport support
    else:
        zipimport._zip_directory_cache.clear()
        zipimport._zip_directory_cache.update(zdc)

    # clear type cache
    sys._clear_type_cache()

    # Clear ABC registries, restoring previously saved ABC registries.
    for abc, registry in abcs.items():
        abc._abc_registry = registry.copy()
        abc._abc_cache.clear()
        abc._abc_negative_cache.clear()

    clear_caches()

def clear_caches():
    import gc

    # Clear the warnings registry, so they can be displayed again
    for mod in sys.modules.values():
        if hasattr(mod, '__warningregistry__'):
            del mod.__warningregistry__

    # Clear assorted module caches.
    # Don't worry about resetting the cache if the module is not loaded
    try:
        distutils_dir_util = sys.modules['distutils.dir_util']
    except KeyError:
        pass
    else:
        distutils_dir_util._path_created.clear()

    re.purge()

    try:
        _strptime = sys.modules['_strptime']
    except KeyError:
        pass
    else:
        _strptime._regex_cache.clear()

    try:
        urlparse = sys.modules['urlparse']
    except KeyError:
        pass
    else:
        urlparse.clear_cache()

    try:
        urllib = sys.modules['urllib']
    except KeyError:
        pass
    else:
        urllib.urlcleanup()

    try:
        urllib2 = sys.modules['urllib2']
    except KeyError:
        pass
    else:
        urllib2.install_opener(None)

    try:
        dircache = sys.modules['dircache']
    except KeyError:
        pass
    else:
        dircache.reset()

    try:
        linecache = sys.modules['linecache']
    except KeyError:
        pass
    else:
        linecache.clearcache()

    try:
        mimetypes = sys.modules['mimetypes']
    except KeyError:
        pass
    else:
        mimetypes._default_mime_types()

    try:
        filecmp = sys.modules['filecmp']
    except KeyError:
        pass
    else:
        filecmp._cache.clear()

    try:
        struct = sys.modules['struct']
    except KeyError:
        pass
    else:
        struct._clearcache()

    try:
        doctest = sys.modules['doctest']
    except KeyError:
        pass
    else:
        doctest.master = None

    try:
        ctypes = sys.modules['ctypes']
    except KeyError:
        pass
    else:
        ctypes._reset_cache()

    # Collect cyclic trash.
    gc.collect()

def warm_caches():
    """Create explicitly internal singletons which are created on demand
    to prevent false positive when hunting reference leaks."""
    # char cache
    for i in range(256):
        chr(i)
    # unicode cache
    for i in range(256):
        unichr(i)
    # int cache
    list(range(-5, 257))

def findtestdir(path=None):
    return path or os.path.dirname(__file__) or os.curdir

def removepy(names):
    if not names:
        return
    for idx, name in enumerate(names):
        basename, ext = os.path.splitext(name)
        if ext == '.py':
            names[idx] = basename

def count(n, word):
    if n == 1:
        return "%d %s" % (n, word)
    else:
        return "%d %ss" % (n, word)

def printlist(x, width=70, indent=4, file=None):
    """Print the elements of iterable x to stdout.

    Optional arg width (default 70) is the maximum line length.
    Optional arg indent (default 4) is the number of blanks with which to
    begin each line.
    """

    from textwrap import fill
    blanks = ' ' * indent
    # Print the sorted list: 'x' may be a '--random' list or a set()
    print >>file, fill(' '.join(str(elt) for elt in sorted(x)), width,
                       initial_indent=blanks, subsequent_indent=blanks)

def get_abs_module(testdir, test):
    if test.startswith('test.') or testdir:
        return test
    else:
        # Always import it from the test package
        return 'test.' + test

def _list_cases(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            _list_cases(test)
        elif isinstance(test, unittest.TestCase):
            if test_support.match_test(test):
                print(test.id())

def list_cases(testdir, selected, match_tests):
    test_support.verbose = False
    test_support.set_match_tests(match_tests)

    save_modules = set(sys.modules)
    skipped = []
    for test in selected:
        abstest = get_abs_module(testdir, test)
        try:
            suite = unittest.defaultTestLoader.loadTestsFromName(abstest)
            _list_cases(suite)
        except unittest.SkipTest:
            skipped.append(test)

        unload_test_modules(save_modules)

    if skipped:
        print >>sys.stderr
        print >>sys.stderr, count(len(skipped), "test"), "skipped:"
        printlist(skipped, file=sys.stderr)

# Map sys.platform to a string containing the basenames of tests
# expected to be skipped on that platform.
#
# Special cases:
#     test_pep277
#         The _ExpectedSkips constructor adds this to the set of expected
#         skips if not os.path.supports_unicode_filenames.
#     test_timeout
#         Controlled by test_timeout.skip_expected.  Requires the network
#         resource and a socket module.
#
# Tests that are expected to be skipped everywhere except on one platform
# are also handled separately.

_expectations = {
    'win32':
        """
        test__locale
        test_bsddb185
        test_bsddb3
        test_commands
        test_crypt
        test_curses
        test_dbm
        test_dl
        test_fcntl
        test_fork1
        test_epoll
        test_gdbm
        test_grp
        test_ioctl
        test_largefile
        test_kqueue
        test_mhlib
        test_openpty
        test_ossaudiodev
        test_pipes
        test_poll
        test_posix
        test_pty
        test_pwd
        test_resource
        test_signal
        test_spwd
        test_threadsignals
        test_timing
        test_wait3
        test_wait4
        """,
    'linux2':
        """
        test_bsddb185
        test_curses
        test_dl
        test_largefile
        test_kqueue
        test_ossaudiodev
        """,
    'unixware7':
        """
        test_bsddb
        test_bsddb185
        test_dl
        test_epoll
        test_largefile
        test_kqueue
        test_minidom
        test_openpty
        test_pyexpat
        test_sax
        test_sundry
        """,
    'openunix8':
        """
        test_bsddb
        test_bsddb185
        test_dl
        test_epoll
        test_largefile
        test_kqueue
        test_minidom
        test_openpty
        test_pyexpat
        test_sax
        test_sundry
        """,
    'sco_sv3':
        """
        test_asynchat
        test_bsddb
        test_bsddb185
        test_dl
        test_fork1
        test_epoll
        test_gettext
        test_largefile
        test_locale
        test_kqueue
        test_minidom
        test_openpty
        test_pyexpat
        test_queue
        test_sax
        test_sundry
        test_thread
        test_threaded_import
        test_threadedtempfile
        test_threading
        """,
    'riscos':
        """
        test_asynchat
        test_atexit
        test_bsddb
        test_bsddb185
        test_bsddb3
        test_commands
        test_crypt
        test_dbm
        test_dl
        test_fcntl
        test_fork1
        test_epoll
        test_gdbm
        test_grp
        test_largefile
        test_locale
        test_kqueue
        test_mmap
        test_openpty
        test_poll
        test_popen2
        test_pty
        test_pwd
        test_strop
        test_sundry
        test_thread
        test_threaded_import
        test_threadedtempfile
        test_threading
        test_timing
        """,
    'darwin':
        """
        test__locale
        test_bsddb
        test_bsddb3
        test_curses
        test_epoll
        test_gdb
        test_gdbm
        test_largefile
        test_locale
        test_kqueue
        test_minidom
        test_ossaudiodev
        test_poll
        """,
    'sunos5':
        """
        test_bsddb
        test_bsddb185
        test_curses
        test_dbm
        test_epoll
        test_kqueue
        test_gdbm
        test_gzip
        test_openpty
        test_zipfile
        test_zlib
        """,
    'hp-ux11':
        """
        test_bsddb
        test_bsddb185
        test_curses
        test_dl
        test_epoll
        test_gdbm
        test_gzip
        test_largefile
        test_locale
        test_kqueue
        test_minidom
        test_openpty
        test_pyexpat
        test_sax
        test_zipfile
        test_zlib
        """,
    'atheos':
        """
        test_bsddb185
        test_curses
        test_dl
        test_gdbm
        test_epoll
        test_largefile
        test_locale
        test_kqueue
        test_mhlib
        test_mmap
        test_poll
        test_popen2
        test_resource
        """,
    'cygwin':
        """
        test_bsddb185
        test_bsddb3
        test_curses
        test_dbm
        test_epoll
        test_ioctl
        test_kqueue
        test_largefile
        test_locale
        test_ossaudiodev
        test_socketserver
        """,
    'os2emx':
        """
        test_audioop
        test_bsddb185
        test_bsddb3
        test_commands
        test_curses
        test_dl
        test_epoll
        test_kqueue
        test_largefile
        test_mhlib
        test_mmap
        test_openpty
        test_ossaudiodev
        test_pty
        test_resource
        test_signal
        """,
    'freebsd4':
        """
        test_bsddb
        test_bsddb3
        test_epoll
        test_gdbm
        test_locale
        test_ossaudiodev
        test_pep277
        test_pty
        test_socketserver
        test_tcl
        test_tk
        test_ttk_guionly
        test_ttk_textonly
        test_timeout
        test_urllibnet
        test_multiprocessing
        """,
    'aix5':
        """
        test_bsddb
        test_bsddb185
        test_bsddb3
        test_bz2
        test_dl
        test_epoll
        test_gdbm
        test_gzip
        test_kqueue
        test_ossaudiodev
        test_tcl
        test_tk
        test_ttk_guionly
        test_ttk_textonly
        test_zipimport
        test_zlib
        """,
    'openbsd3':
        """
        test_ascii_formatd
        test_bsddb
        test_bsddb3
        test_ctypes
        test_dl
        test_epoll
        test_gdbm
        test_locale
        test_normalization
        test_ossaudiodev
        test_pep277
        test_tcl
        test_tk
        test_ttk_guionly
        test_ttk_textonly
        test_multiprocessing
        """,
    'netbsd3':
        """
        test_ascii_formatd
        test_bsddb
        test_bsddb185
        test_bsddb3
        test_ctypes
        test_curses
        test_dl
        test_epoll
        test_gdbm
        test_locale
        test_ossaudiodev
        test_pep277
        test_tcl
        test_tk
        test_ttk_guionly
        test_ttk_textonly
        test_multiprocessing
        """,
}
_expectations['freebsd5'] = _expectations['freebsd4']
_expectations['freebsd6'] = _expectations['freebsd4']
_expectations['freebsd7'] = _expectations['freebsd4']
_expectations['freebsd8'] = _expectations['freebsd4']

class _ExpectedSkips:
    def __init__(self):
        import os.path
        from test import test_timeout

        self.valid = False
        if sys.platform in _expectations:
            s = _expectations[sys.platform]
            self.expected = set(s.split())

            # expected to be skipped on every platform, even Linux
            self.expected.add('test_linuxaudiodev')

            if not os.path.supports_unicode_filenames:
                self.expected.add('test_pep277')

            if test_timeout.skip_expected:
                self.expected.add('test_timeout')

            if sys.maxint == 9223372036854775807L:
                self.expected.add('test_imageop')

            if sys.platform != "darwin":
                MAC_ONLY = ["test_macos", "test_macostools", "test_aepack",
                            "test_plistlib", "test_scriptpackages",
                            "test_applesingle"]
                for skip in MAC_ONLY:
                    self.expected.add(skip)
            elif len(u'\0'.encode('unicode-internal')) == 4:
                self.expected.add("test_macostools")


            if sys.platform != "win32":
                # test_sqlite is only reliable on Windows where the library
                # is distributed with Python
                WIN_ONLY = ["test_unicode_file", "test_winreg",
                            "test_winsound", "test_startfile",
                            "test_sqlite", "test_msilib"]
                for skip in WIN_ONLY:
                    self.expected.add(skip)

            if sys.platform != 'irix':
                IRIX_ONLY = ["test_imageop", "test_al", "test_cd", "test_cl",
                             "test_gl", "test_imgfile"]
                for skip in IRIX_ONLY:
                    self.expected.add(skip)

            if sys.platform != 'sunos5':
                self.expected.add('test_sunaudiodev')
                self.expected.add('test_nis')

            if not sys.py3kwarning:
                self.expected.add('test_py3kwarn')

            self.valid = True

    def isvalid(self):
        "Return true iff _ExpectedSkips knows about the current platform."
        return self.valid

    def getexpected(self):
        """Return set of test names we expect to skip on current platform.

        self.isvalid() must be true.
        """

        assert self.isvalid()
        return self.expected

def main_in_temp_cwd():
    """Run main() in a temporary working directory."""
    global TEMPDIR

    # When tests are run from the Python build directory, it is best practice
    # to keep the test files in a subfolder.  It eases the cleanup of leftover
    # files using command "make distclean".
    if sysconfig.is_python_build():
        TEMPDIR = os.path.join(sysconfig.get_config_var('srcdir'), 'build')
        TEMPDIR = os.path.abspath(TEMPDIR)
        if not os.path.exists(TEMPDIR):
            os.mkdir(TEMPDIR)

    # Define a writable temp dir that will be used as cwd while running
    # the tests. The name of the dir includes the pid to allow parallel
    # testing (see the -j option).
    TESTCWD = 'test_python_{}'.format(os.getpid())

    TESTCWD = os.path.join(TEMPDIR, TESTCWD)

    # Run the tests in a context manager that temporary changes the CWD to a
    # temporary and writable directory. If it's not possible to create or
    # change the CWD, the original CWD will be used. The original CWD is
    # available from test_support.SAVEDCWD.
    with test_support.temp_cwd(TESTCWD, quiet=True):
        main()

if __name__ == '__main__':
    # findtestdir() gets the dirname out of __file__, so we have to make it
    # absolute before changing the working directory.
    # For example __file__ may be relative when running trace or profile.
    # See issue #9323.
    global __file__
    __file__ = os.path.abspath(__file__)

    # sanity check
    assert __file__ == os.path.abspath(sys.argv[0])

    main_in_temp_cwd()
