// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the Apache 2.0 License.
// See the LICENSE file in the project root for more information.

using System;
using System.Reflection;

using Microsoft.Scripting;
using Microsoft.Scripting.Interpreter;
using Microsoft.Scripting.Runtime;

using IronPython.Runtime.Binding;
using IronPython.Runtime.Operations;
using IronPython.Runtime.Types;

using MSAst = System.Linq.Expressions;

using AstUtils = Microsoft.Scripting.Ast.Utils;

namespace IronPython.Compiler.Ast {
    using Ast = MSAst.Expression;

    public class ConstantExpression : Expression, IInstructionProvider {
        private readonly object _value;

        public ConstantExpression(object value) {
            _value = value;
        }

        internal static ConstantExpression MakeUnicode(string value) {
            return new ConstantExpression(new UnicodeWrapper(value));
        }

        public object Value {
            get {
                UnicodeWrapper wrapper;
                if ((wrapper = _value as UnicodeWrapper) != null) {
                    return wrapper.Value;
                }
                
                return _value; 
            }
        }

        internal bool IsUnicodeString {
            get {
                return _value is UnicodeWrapper;
            }
        }

        private static readonly MSAst.Expression EllipsisExpr = Ast.Property(null, typeof(PythonOps).GetProperty(nameof(PythonOps.Ellipsis)));
        private static readonly MSAst.Expression TrueExpr = Ast.Field(null, typeof(ScriptingRuntimeHelpers).GetField("True"));
        private static readonly MSAst.Expression FalseExpr = Ast.Field(null, typeof(ScriptingRuntimeHelpers).GetField("False"));
        public override MSAst.Expression Reduce() {
            UnicodeWrapper wrapper;
            if (_value == Ellipsis.Value) {
                return EllipsisExpr;
            } else if (_value is bool) {
                if ((bool)_value) {
                    return TrueExpr;
                } else {
                    return FalseExpr;
                }
            } else if ((wrapper = _value as UnicodeWrapper) != null) {
                return GlobalParent.Constant(wrapper.Value);
            }

            return GlobalParent.Constant(_value);
        }

        internal override ConstantExpression ConstantFold() {
            return this;
        }

        public override Type Type {
            get {
                return GlobalParent.CompilationMode.GetConstantType(Value);
            }
        }

        internal override string CheckAssign() {
            if (_value == null) {
                return "cannot assign to None";
            }

            return base.CheckAssign();
        }

        public override void Walk(PythonWalker walker) {
            if (walker.Walk(this)) {
            }
            walker.PostWalk(this);
        }

        public override string NodeName => _value == null ? "None" : "literal";

        internal override bool CanThrow {
            get {
                return false;
            }
        }

        internal override object GetConstantValue() {
            return Value;
        }

        internal override bool IsConstant {
            get {
                return true;
            }
        }

        class UnicodeWrapper {
            public readonly object Value;

            public UnicodeWrapper(string value) {
                Value = value;
            }
        }

        #region IInstructionProvider Members

        void IInstructionProvider.AddInstructions(LightCompiler compiler) {
            if (_value is bool) {
                compiler.Instructions.EmitLoad((bool)_value);
            } else if (_value is UnicodeWrapper) {
                compiler.Instructions.EmitLoad(((UnicodeWrapper)_value).Value);
            } else {
                compiler.Instructions.EmitLoad(_value);
            }
        }

        #endregion
    }
}
