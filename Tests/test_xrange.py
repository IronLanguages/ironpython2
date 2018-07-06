# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information.


##
## Test range and xrange
##
## * sbs_builtin\test_xrange covers many xrange corner cases
##

import unittest

from iptest import run_test

class XRangeTest(unittest.TestCase):

    def test_range(self):
        self.assertTrue(range(10) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertTrue(range(0) == [])
        self.assertTrue(range(-10) == [])

        self.assertTrue(range(3,10) == [3, 4, 5, 6, 7, 8, 9])
        self.assertTrue(range(10,3) == [])
        self.assertTrue(range(-3,-10) == [])
        self.assertTrue(range(-10,-3) == [-10, -9, -8, -7, -6, -5, -4])

        self.assertTrue(range(3,20,2) == [3, 5, 7, 9, 11, 13, 15, 17, 19])
        self.assertTrue(range(3,20,-2) == [])
        self.assertTrue(range(20,3,2) == [])
        self.assertTrue(range(20,3,-2) == [20, 18, 16, 14, 12, 10, 8, 6, 4])
        self.assertTrue(range(-3,-20,2) == [])
        self.assertTrue(range(-3,-20,-2) == [-3, -5, -7, -9, -11, -13, -15, -17, -19])
        self.assertTrue(range(-20,-3, 2) == [-20, -18, -16, -14, -12, -10, -8, -6, -4])
        self.assertTrue(range(-20,-3,-2) == [])

    def _xrange_eqv_range(self, r, o):
        self.assertTrue(len(r) == len(o))
        for i in range(len(r)):
            self.assertTrue(r[i]==o[i])
            if (1 - i) == len(r):
                self.assertRaises(IndexError, lambda: r[1-i])
                self.assertRaises(IndexError, lambda: o[1-i])
            else:
                self.assertTrue(r[1-i] == o[1-i])

    def test_xrange_based_on_range(self):
        for x in (10, -1, 0, 1, -10):
            self._xrange_eqv_range(xrange(x), range(x))

        for x in (3, -3, 10, -10):
            for y in (3, -3, 10, -10):
                self._xrange_eqv_range(xrange(x, y), range(x, y))

        for x in (3, -3, 20, -20):
            for y in (3, -3, 20, -20):
                for z in (2, -2):
                    self._xrange_eqv_range(xrange(x, y, z), range(x, y, z))

        for x in (7, -7):
            for y in (20, 21, 22, 23, -20, -21, -22, -23):
                for z in (4, -4):
                    self._xrange_eqv_range(xrange(x, y, z), range(x, y, z))

    def test_xrange_corner_cases(self):
        import sys
        x = xrange(0, sys.maxint, sys.maxint-1)
        self.assertEqual(x[0], 0)
        self.assertEqual(x[1], sys.maxint-1)

    def test_xrange_coverage(self):
        ## ToString
        self.assertEqual(str(xrange(0, 3, 1)), "xrange(3)")
        self.assertEqual(str(xrange(1, 3, 1)), "xrange(1, 3)")
        self.assertEqual(str(xrange(0, 5, 2)), "xrange(0, 6, 2)")

        ## Long
        self.assertEqual([x for x in xrange(5L)], range(5))
        self.assertEqual([x for x in xrange(10L, 15L)], range(10, 15))
        self.assertEqual([x for x in xrange(10L, 15L, 2)], range(10, 15,2 ))
    
        ## Ops
        self.assertRaises(TypeError, lambda: xrange(4) + 4)
        self.assertRaises(TypeError, lambda: xrange(4) * 4)
        self.assertRaises(TypeError, lambda: xrange(4)[:2])
        self.assertRaises(TypeError, lambda: xrange(4)[1:2:3])


run_test(__name__)
