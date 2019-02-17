// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the Apache 2.0 License.
// See the LICENSE file in the project root for more information.

using MSAst = System.Linq.Expressions;

using System;

namespace IronPython.Compiler.Ast {
    using Ast = MSAst.Expression;

    public class SliceExpression : Expression {
        private readonly Expression _sliceStart;
        private readonly Expression _sliceStop;
        private readonly Expression _sliceStep;
        private readonly bool _stepProvided;

        public SliceExpression(Expression start, Expression stop, Expression step, bool stepProvided) {
            _sliceStart = start;
            _sliceStop = stop;
            _sliceStep = step;
            _stepProvided = stepProvided;
        }

        public Expression SliceStart {
            get { return _sliceStart; }
        }

        public Expression SliceStop {
            get { return _sliceStop; }
        }

        public Expression SliceStep {
            get { return _sliceStep; }
        }

        /// <summary>
        /// True if the user provided a step parameter (either providing an explicit parameter
        /// or providing an empty step parameter) false if only start and stop were provided.
        /// </summary>
        public bool StepProvided {
            get {
                return _stepProvided;
            }
        }

        public override MSAst.Expression Reduce() {
            return Ast.Call(
                AstMethods.MakeSlice,                                    // method
                TransformOrConstantNull(_sliceStart, typeof(object)),    // parameters
                TransformOrConstantNull(_sliceStop, typeof(object)),
                TransformOrConstantNull(_sliceStep, typeof(object))
            );
        }

        public override void Walk(PythonWalker walker) {
            if (walker.Walk(this)) {
                _sliceStart?.Walk(walker);
                _sliceStop?.Walk(walker);
                _sliceStep?.Walk(walker);
            }
            walker.PostWalk(this);
        }
    }
}
