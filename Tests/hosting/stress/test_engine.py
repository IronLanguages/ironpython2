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

'''
Testing IronPython Engine under a few stressful scenarios
'''

import os
import sys
import unittest

from iptest import IronPythonTestCase, is_cli, is_netstandard, run_test, skipUnlessIronPython

def gen_testcase(name):
    def test(self):
        getattr(self.engine, name)()
    return test

multipleexecskips = [ "ScenarioXGC" ]

@skipUnlessIronPython()
class EngineStressTest(IronPythonTestCase):
    def setUp(self):
        super(EngineStressTest, self).setUp()
        self.load_iron_python_test()
        self.engine = IronPythonTest.Stress.Engine()

if is_cli:
    import clr
    if not is_netstandard:
        clr.AddReference("System.Core")

    clr.AddReference("Microsoft.Scripting")
    clr.AddReference("Microsoft.Dynamic")
    clr.AddReference("IronPython")
    clr.AddReferenceToFileAndPath(os.path.join(sys.prefix, "IronPythonTest.exe"))

    import IronPythonTest
    engine = IronPythonTest.Stress.Engine()

    for s in dir(engine):
        print 's = %s' % s
        if s.startswith("Scenario"):
            test_name = "test_Engine_%s" % s
            test = gen_testcase(s)
            if s in multipleexecskips:
                # TODO: add the multipleexec decorator
                pass
            setattr(EngineStressTest, test_name, test)


run_test(__name__)



