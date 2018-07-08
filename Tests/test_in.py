# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information.


import unittest

from iptest import run_test

class C:
    x = "Hello"
    def __contains__(self, y):
        return self.x == y;


class D:
    x = (1,2,3,4,5,6,7,8,9,10)
    def __getitem__(self, y):
        return self.x[y];

class InTest(unittest.TestCase):
    def test_basic(self):
        self.assertTrue('abc' in 'abcd')

    def test_class(self):
        h = "Hello"
        c = C()
        self.assertTrue(c.__contains__("Hello"))
        self.assertTrue(c.__contains__(h))
        self.assertTrue(not (c.__contains__('abc')))

        self.assertTrue(h in c)
        self.assertTrue("Hello" in c)

        d = D()
        self.assertTrue(1 in d)
        self.assertTrue(not(11 in d))

run_test(__name__)
