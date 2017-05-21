using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using IronPython.Hosting;
using IronPython.Runtime;
using IronPython.Runtime.Exceptions;
using IronPythonTest.Util;
using Microsoft.Scripting;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Operations;

namespace IronPythonTest.Cases {
    class CaseExecuter {
        private static readonly String Executable = Path.Combine(Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location), "ipy.exe");

        private ScriptEngine defaultEngine;

        public static ScriptEngine CreateEngine(TestOptions options) {
            var engine = Python.CreateEngine(new Dictionary<string, object> {
                {"Debug", options.Debug },
                {"Frames", options.Frames || options.FullFrames },
                {"FullFrames", options.FullFrames },
                {"RecursionLimit", options.MaxRecursion },
                {"Tracing", options.Tracing }
            });

            engine.SetHostVariables(
                Path.GetDirectoryName(Executable),
                Executable,
                "");

            AddSearchPaths(engine);
            return engine;
        }

        private static void AddSearchPaths(ScriptEngine engine) {
            var paths = new List<string>(engine.GetSearchPaths());
            if(!paths.Any(x => x.ToLower().Contains("stdlib"))) {
                // we start at the current directory and look up until we find the "Src" directory
                var current = System.Reflection.Assembly.GetEntryAssembly().Location;
                var found = false;
                while(!found && !string.IsNullOrEmpty(current)) {
                    var test = Path.Combine(current, "Src", "StdLib", "Lib");
                    if(Directory.Exists(test)) {
                        paths.Add(test);
                        found = true;
                        break;
                    }

                    current = Path.GetDirectoryName(current);
                }
            }
            engine.SetSearchPaths(paths);
        }

        public CaseExecuter() {
            this.defaultEngine = Python.CreateEngine(new Dictionary<string, object> {
                {"Debug", false},
                {"Frames", true},
                {"FullFrames", true},
                {"RecursionLimit", 100}
            });

            this.defaultEngine.SetHostVariables(
                Path.GetDirectoryName(Executable),
                Executable,
                "");
            AddSearchPaths(this.defaultEngine);
        }

        public int RunTest(TestInfo testcase) {
            switch(testcase.Options.IsolationLevel) {
                case TestIsolationLevel.DEFAULT:
                    return GetScopeTest(testcase);

                case TestIsolationLevel.ENGINE:
                    return GetEngineTest(testcase);

                default:
                    throw new ArgumentException(String.Format("IsolationLevel {0} is not supported.", testcase.Options.IsolationLevel.ToString()), "testcase.IsolationLevel");
            }
        }

        public string FormatException(Exception ex) {
            return this.defaultEngine.GetService<ExceptionOperations>().FormatException(ex);
        }

        private int GetEngineTest(TestInfo testcase) {
            var engine = CreateEngine(testcase.Options);
            var source = engine.CreateScriptSourceFromString(
                testcase.Text, testcase.Path, SourceCodeKind.File);

            return GetResult(engine, source);
        }

        private int GetScopeTest(TestInfo testcase) {
            var source = this.defaultEngine.CreateScriptSourceFromString(
                testcase.Text, testcase.Path, SourceCodeKind.File);

            return GetResult(this.defaultEngine, source);
        }

        private int GetResult(ScriptEngine engine, ScriptSource source) {
            var scope = engine.CreateScope();
            engine.GetSysModule().SetVariable("argv", List.FromArrayNoCopy(new object[] { source.Path }));
            var compiledCode = source.Compile(new IronPython.Compiler.PythonCompilerOptions() { ModuleName = "__main__" });
            int res = 0;
            try {
                res = engine.Operations.ConvertTo<int>(compiledCode.Execute(scope) ?? 0);
            } catch(SystemExitException ex) {
                object otherCode;
                res = ex.GetExitCode(out otherCode);
            } catch(Exception ex) {
                bool throwIt = true;
                if(ex.Data.Contains("PythonException")) {
                    PythonExceptions.BaseException pyEx = ex.Data["PythonException"] as PythonExceptions.BaseException;
                    if(pyEx != null && PythonOps.GetPythonTypeName(pyEx).Contains("SkipTest")) {
                        throwIt = false;
                    }
                } 
                if(throwIt)
                    throw ex;
            }
            return res;
        }
    }
}
