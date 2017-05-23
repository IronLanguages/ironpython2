import unittest

from .test_env import *

class IronPythonTestCase(unittest.TestCase):

    def _force_gc(self):
        if is_cpython:
            import gc
            gc.collect()
        else:
            import System
            for i in xrange(100):
                System.GC.Collect()
            System.GC.WaitForPendingFinalizers()

    pass