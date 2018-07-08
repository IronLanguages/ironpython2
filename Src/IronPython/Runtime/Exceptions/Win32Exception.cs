// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the Apache 2.0 License.
// See the LICENSE file in the project root for more information.
#if !FEATURE_WIN32EXCEPTION

using System;

namespace IronPython.Runtime.Exceptions {
    // exits for better compatibility w/ Silverlight where this exception isn't available.

    [Serializable]
    public class Win32Exception : Exception {
        public Win32Exception() : base() { }
        public Win32Exception(string msg) : base(msg) { }
        public Win32Exception(string message, Exception innerException)
            : base(message, innerException) {
        }

        public int ErrorCode {
            get {
                return 0;
            }
        }

        public int NativeErrorCode {
            get {
                return 0;
            }
        }
    }
}

#endif
