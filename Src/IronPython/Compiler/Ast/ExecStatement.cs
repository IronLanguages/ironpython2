// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the Apache 2.0 License.
// See the LICENSE file in the project root for more information.

using MSAst = System.Linq.Expressions;

using System.Diagnostics;
using Microsoft.Scripting;
using IronPython.Runtime;
using AstUtils = Microsoft.Scripting.Ast.Utils;

namespace IronPython.Compiler.Ast {
    using Ast = MSAst.Expression;

    public class ExecStatement : Statement {
        private readonly Expression _code, _locals, _globals;

        public ExecStatement(Expression code, Expression locals, Expression globals) {
            _code = code;
            _locals = locals;
            _globals = globals;
        }

        public Expression Code {
            get { return _code; }
        }

        public Expression Locals {
            get { return _locals; }
        }

        public Expression Globals {
            get { return _globals; }
        }

        public bool NeedsLocalsDictionary() {
            return _globals == null && _locals == null;
        }

        public override MSAst.Expression Reduce() {
            MSAst.MethodCallExpression call;

            if (_locals == null && _globals == null) {
                // exec code
                call = Ast.Call(
                    AstMethods.UnqualifiedExec,
                    Parent.LocalContext,
                    AstUtils.Convert(_code, typeof(object))
                );
            } else {
                // exec code in globals [ , locals ]
                // We must have globals now (locals is last and may be absent)
                Debug.Assert(_globals != null);
                call = Ast.Call(
                    AstMethods.QualifiedExec,
                    Parent.LocalContext,
                    AstUtils.Convert(_code, typeof(object)),
                    TransformAndDynamicConvert(_globals, typeof(PythonDictionary)),
                    TransformOrConstantNull(_locals, typeof(object))
                );
            }

            return GlobalParent.AddDebugInfo(call, Span);
        }

        public override void Walk(PythonWalker walker) {
            if (walker.Walk(this)) {
                _code?.Walk(walker);
                _locals?.Walk(walker);
                _globals?.Walk(walker);
            }
            walker.PostWalk(this);
        }
    }
}
