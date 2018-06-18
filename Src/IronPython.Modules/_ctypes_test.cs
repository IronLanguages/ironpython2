/* ****************************************************************************
 *
 * Copyright (c) Microsoft Corporation. 
 *
 * This source code is subject to terms and conditions of the Apache License, Version 2.0. A 
 * copy of the license can be found in the License.html file at the root of this distribution. If 
 * you cannot locate the  Apache License, Version 2.0, please send an email to 
 * dlr@microsoft.com. By using this source code in any fashion, you are agreeing to be bound 
 * by the terms of the Apache License, Version 2.0.
 *
 * You must not remove this notice, or any other, from this software.
 *
 *
 * ***************************************************************************/

#if FEATURE_CTYPES

using System;
using System.IO;

using IronPython.Runtime;

[assembly: PythonModule("_ctypes_test", typeof(IronPython.Modules.CTypesTest))]
namespace IronPython.Modules {
    public static class CTypesTest {

        private static string FindRoot() {
            // we start at the current directory and look up until we find the "Src" directory
            var current = System.Reflection.Assembly.GetExecutingAssembly().Location;
            var found = false;
            while (!found && !string.IsNullOrEmpty(current)) {
                var test = Path.Combine(current, "Src", "StdLib", "Lib");
                if (Directory.Exists(test)) {
                    return current;
                }

                current = Path.GetDirectoryName(current);
            }
            return string.Empty;
        }

        public static string __file__ = Path.Combine(FindRoot(), "Tests", string.Format("_ctypes_test_{0}{1}.pyd", Environment.OSVersion.Platform == PlatformID.Win32NT ? "win" : Environment.OSVersion.Platform == PlatformID.MacOSX ? "macOS" : "linux", Environment.Is64BitProcess ? 64 : 32));
    }
}
#endif