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

from generate import generate

MaxTypes = 16

def gen_delegate_func(cw):
    for i in range(MaxTypes + 1):
        cw.write("case %(length)d: return typeof(Func<%(targs)s>).MakeGenericType(types);", length = i + 1, targs = "," * i)

def gen_delegate_action(cw):
    for i in range(MaxTypes):
        cw.write("case %(length)d: return typeof(Action<%(targs)s>).MakeGenericType(types);", length = i + 1, targs = "," * i)

def gen_max_delegate_arity(cw):
    cw.write('private const int MaximumArity = %d;' % (MaxTypes + 1))

def main():
    return generate(
        ("Delegate Action Types", gen_delegate_action),
        ("Delegate Func Types", gen_delegate_func),
        ("Maximum Delegate Arity", gen_max_delegate_arity),
# outer ring generators
        ("Delegate Microsoft Scripting Action Types", gen_delegate_action),
        ("Delegate Microsoft Scripting Scripting Func Types", gen_delegate_func),
    )

if __name__ == "__main__":
    main()
