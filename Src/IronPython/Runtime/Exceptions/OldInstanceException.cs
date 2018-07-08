// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the Apache 2.0 License.
// See the LICENSE file in the project root for more information.

using System;
using System.Runtime.Serialization;
using IronPython.Runtime.Types;

namespace IronPython.Runtime.Exceptions {
    [Serializable]
    class OldInstanceException : Exception, IPythonException {
        private OldInstance _instance;

        public OldInstanceException(OldInstance instance) {
            _instance = instance;
        }
        public OldInstanceException(string msg) : base(msg) { }
        public OldInstanceException(string message, Exception innerException)
            : base(message, innerException) {
        }
#if FEATURE_SERIALIZATION
        protected OldInstanceException(SerializationInfo info, StreamingContext context) : base(info, context) { }
#endif

        public OldInstance Instance {
            get {
                return _instance;
            }
        }

        #region IPythonException Members

        public object ToPythonException() {
            return _instance;
        }

        #endregion
    }
}
