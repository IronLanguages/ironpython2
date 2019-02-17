// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the Apache 2.0 License.
// See the LICENSE file in the project root for more information.

using MSAst = System.Linq.Expressions;

using System;
using System.Reflection;
using Microsoft.Scripting.Utils;

namespace IronPython.Compiler.Ast {
    using Ast = MSAst.Expression;
    using AstUtils = Microsoft.Scripting.Ast.Utils;

    public class ReturnStatement : Statement {
        private readonly Expression _expression;        

        public ReturnStatement(Expression expression) {
            _expression = expression;
        }

        public Expression Expression {
            get { return _expression; }
        }

        public override MSAst.Expression Reduce() {
            if (Parent.IsGeneratorMethod) {
                if (_expression != null) {
                    // Statements can't return null, so return a rethrow. 
                    // Callers should detecet the ag.AddError and avoid trying to execute the tree, 
                    // but if they accidentally do, use Throw instead of empty so that
                    // we'll get an exception.
                    return Ast.Throw(
                        Ast.New(
                            typeof(InvalidOperationException).GetConstructor(ReflectionUtils.EmptyTypes)
                        )
                    );
                }

                return GlobalParent.AddDebugInfo(AstUtils.YieldBreak(GeneratorLabel), Span);
            }

            return GlobalParent.AddDebugInfo(
                Ast.Return(
                    FunctionDefinition._returnLabel,
                    TransformOrConstantNull(_expression, typeof(object))
                ),
                Span
            );
        }

        public override void Walk(PythonWalker walker) {
            if (walker.Walk(this)) {
                _expression?.Walk(walker);
            }
            walker.PostWalk(this);
        }

        internal override bool CanThrow {
            get {
                if (_expression == null) {
                    return false;
                }

                return _expression.CanThrow;
            }
        }
    }
}
