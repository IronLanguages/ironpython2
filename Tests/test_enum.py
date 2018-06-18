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

import clr
clr.AddReference('IronPython')
from IronPython.Compiler.Ast import Arg

Arg(None)

import sys

from iptest import IronPythonTestCase, is_cli, run_test, skipUnlessIronPython

if is_cli:
    from System import *

class Enum34Test(IronPythonTestCase):
    """check that CLR Enum have simular behavior to Python 3.4 enum"""
    def setUp(self):
        super(Enum34Test, self).setUp()
        self.load_iron_python_test()
    
    @skipUnlessIronPython()
    def test_constructor(self):
        """check that enum could be constructed from numeric values"""
        from IronPythonTest import DaysInt, DaysShort, DaysLong, DaysSByte, DaysByte, DaysUShort, DaysUInt, DaysULong
        
        enum_types = [DaysInt, DaysShort, DaysLong, DaysSByte, DaysByte, DaysUShort, DaysUInt, DaysULong]
        # days go from 0x01 to 0x40
        # we add 0x80 as a check for undefined enum member
        enum_values = list(range(0, 0x80))

        for EnumType in enum_types:
            for value in enum_values:
                day = EnumType(value)
                self.assertEqual(int(day), value)
                
            self.assertTrue(EnumType.Mon < EnumType.Tue)
            
            self.assertEqual(EnumType(1), EnumType.Mon)
            self.assertEqual(EnumType(6), EnumType.Tue | EnumType.Wed)
            self.assertEqual(EnumType(96), EnumType.Weekend)

run_test(__name__)
