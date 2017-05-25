#####################################################################################
#
#  Copyright (c) Microsoft Corporation. All rights reserved.
#
# This source code is subject to terms and conditions of the Apache License, Version 2.0. A
# copy of the license can be found in the License.html file at the root of this distribution. If
# you cannot locate the  Apache License, Version 2.0, please send an email to
# ironpy@microsoft.com. By using this source code in any fashion, you are agreeing to be bound
# by the terms of the Apache License, Version 2.0.
#
# You must not remove this notice, or any other, from this software.
#
#
#####################################################################################

#
# test assert
#

import unittest

class AssertTest(unittest.TestCase):

    def test_positive(self):
        try:
            assert True
        except AssertionError, e:
            raise "Should have been no exception!"

        try:
            assert True, 'this should always pass'
        except AssertionError, e:
            raise "Should have been no exception!"
            
    def test_negative(self):
        ok = False
        try:
            assert False
        except AssertionError, e:
            ok = True
            self.assertEqual(str(e), "")
        self.assertTrue(ok)
        
        ok = False
        try:
            assert False
        except AssertionError, e:
            ok = True
            self.assertEqual(str(e), "")
        self.assertTrue(ok)
        
        ok = False
        try:
            assert False, 'this should never pass'
        except AssertionError, e:
            ok = True
            self.assertEqual(str(e), "this should never pass")
        self.assertTrue(ok)
        
        ok = False
        try:
            assert None, 'this should never pass'
        except AssertionError, e:
            ok = True
            self.assertEqual(str(e), "this should never pass")
        self.assertTrue(ok)
            
    def test_doesnt_fail_on_curly(self):
        """Ensures that asserting a string with a curly brace doesn't choke up the
        string formatter."""

        ok = False
        try:
            assert False, '}'
        except AssertionError:
            ok = True
        self.assertTrue(ok)
  
  
#--Main------------------------------------------------------------------------
# if is_cli and '-O' in System.Environment.GetCommandLineArgs():
#     from iptest.process_util import *
#     self.assertEqual(0, launch_ironpython_changing_extensions(__file__, remove=["-O"]))
# else:
#     run_test(__name__)

if __name__ == '__main__':
    from test import test_support
    test_support.run_unittest(__name__)

