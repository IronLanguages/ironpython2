
import unittest
from decimal import *

from iptest import is_cli

@unittest.skipUnless(is_cli, 'IronPython specific test case')
class DecimalTest(unittest.TestCase):
    def test_explicit_from_System_Decimal(self):
        import System

        #int
        self.assertEqual(str(Decimal(System.Decimal.Parse('45'))), '45')

        #float
        self.assertEqual(str(Decimal(System.Decimal.Parse('45.34'))), '45.34')

if __name__ == '__main__':
    from test import test_support
    test_support.run_unittest(__name__)
