// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the Apache 2.0 License.
// See the LICENSE file in the project root for more information.

using MSAst = System.Linq.Expressions;

using System;

namespace IronPython.Compiler.Ast {
    using Ast = MSAst.Expression;
    using AstUtils = Microsoft.Scripting.Ast.Utils;

    public class BackQuoteExpression : Expression {
        private readonly Expression _expression;

        public BackQuoteExpression(Expression expression) {
            _expression = expression;
        }

        public Expression Expression {
            get { return _expression; }
        }

        public override MSAst.Expression Reduce() {
            return Ast.Call(
                AstMethods.Repr,
                Parent.LocalContext,
                AstUtils.Convert(_expression, typeof(object))
            );                                  
        }

        public override void Walk(PythonWalker walker) {
            if (walker.Walk(this)) {
                _expression?.Walk(walker);
            }
            walker.PostWalk(this);
        }
    }
}
