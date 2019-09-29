// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the Apache 2.0 License.
// See the LICENSE file in the project root for more information.


using System;
using System.IO;
using System.Text;
using IronPython.Runtime.Operations;
using Microsoft.Scripting;
using Microsoft.Scripting.Runtime;
using Microsoft.Scripting.Utils;

namespace IronPython.Runtime {
    internal sealed class OutputWriter : TextWriter {
        private readonly PythonContext _context;
        private readonly bool _isErrorOutput;

        public OutputWriter(PythonContext/*!*/ context, bool isErrorOutput) {
            Assert.NotNull(context);
            _context = context;
            _isErrorOutput = isErrorOutput;
        }

        public object Sink {
            get {
                return (_isErrorOutput) ? _context.SystemStandardError : _context.SystemStandardOut;
            }
        }

        public override Encoding Encoding {
            get {
                return (Sink is PythonFile file) ? file.Encoding : null;
            }
        }

        public override void Write(string value) {
            // the context arg is only used to get stdout if it's not passed in
            try {
                PythonOps.PrintWithDestNoNewline(DefaultContext.Default, Sink, value);
            } catch (Exception e) {
                PythonOps.PrintWithDest(DefaultContext.Default, _context.SystemStandardOut, _context.FormatException(e));
            }
        }

        public override void Write(char value) {
            Write(value.ToString());
        }

        public override void Write(char[] value) {
            Write(new string(value));
        }

        public override void Flush() {
            // avoid creating a site in the common case
            if (Sink is PythonFile pf) {
                pf.flush();
                return;
            }

            if (PythonOps.HasAttr(_context.SharedContext, Sink, "flush")) {
                PythonOps.Invoke(_context.SharedContext, Sink, "flush");
            }
        }
    }
}
