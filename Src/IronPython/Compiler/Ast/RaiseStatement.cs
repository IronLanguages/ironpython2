// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the Apache 2.0 License.
// See the LICENSE file in the project root for more information.

using System;

using MSAst = System.Linq.Expressions;

using AstUtils = Microsoft.Scripting.Ast.Utils;

namespace IronPython.Compiler.Ast {
    using Ast = MSAst.Expression;

    public class RaiseStatement : Statement {
        private readonly Expression _type, _value, _traceback;
        private bool _inFinally;

        public RaiseStatement(Expression exceptionType, Expression exceptionValue, Expression traceBack) {
            _type = exceptionType;
            _value = exceptionValue;
            _traceback = traceBack;
        }

        [Obsolete("Type is obsolete due to direct inheritance from DLR Expression.  Use ExceptType instead")]
        public new Expression Type {
            get { return _type; }
        }

        public Expression ExceptType {
            get {
                return _type;
            }
        }

        public Expression Value {
            get { return _value; }
        }

        public Expression Traceback {
            get { return _traceback; }
        }

        public override MSAst.Expression Reduce() {
            MSAst.Expression raiseExpression;
            if (_type == null && _value == null && _traceback == null) {
                raiseExpression = Ast.Call(
                    AstMethods.MakeRethrownException,
                    Parent.LocalContext
                );
                
                if (!InFinally) {
                    raiseExpression = Ast.Block(
                        UpdateLineUpdated(true),
                        raiseExpression
                    );
                }
            } else {
                raiseExpression = Ast.Call(
                    AstMethods.MakeException,
                    Parent.LocalContext,
                    TransformOrConstantNull(_type, typeof(object)),
                    TransformOrConstantNull(_value, typeof(object)),
                    TransformOrConstantNull(_traceback, typeof(object))
                );
            }

            return GlobalParent.AddDebugInfo(
                Ast.Throw(raiseExpression),
                Span
            );
        }

        internal bool InFinally {
            get {
                return _inFinally;
            }
            set {
                _inFinally = value;
            }
        }

        public override void Walk(PythonWalker walker) {
            if (walker.Walk(this)) {
                _type?.Walk(walker);
                _value?.Walk(walker);
                _traceback?.Walk(walker);
            }
            walker.PostWalk(this);
        }
    }
}
