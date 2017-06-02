using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using IronPython.Hosting;
using IronPython.Runtime;
using IronPython.Runtime.Exceptions;
using IronPythonTest.Util;
using Microsoft.Scripting;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Operations;

namespace IronPythonTest.Cases {
    class CaseExecuter {
        private static readonly string Executable = Path.Combine(Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location), "ipy.exe");
        private static readonly string IRONPYTHONPATH = GetIronPythonPath();

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

        private static string FindRoot() {
            // we start at the current directory and look up until we find the "Src" directory
            var current = System.Reflection.Assembly.GetEntryAssembly().Location;
            var found = false;
            while (!found && !string.IsNullOrEmpty(current)) {
                var test = Path.Combine(current, "Src", "StdLib", "Lib");
                if (Directory.Exists(test)) {
                    return current;
                }

                current = Path.GetDirectoryName(current);
            }
            return string.Empty;
        }

        private static void AddSearchPaths(ScriptEngine engine) {
            var paths = new List<string>(engine.GetSearchPaths());
            if(!paths.Any(x => x.ToLower().Contains("stdlib"))) {
                var root = FindRoot();
                if(!string.IsNullOrEmpty(root)) {
                    paths.Insert(0, Path.Combine(root, "Src", "StdLib", "Lib"));
                }
            }
            engine.SetSearchPaths(paths);
        }

        public CaseExecuter() {
            this.defaultEngine = Python.CreateEngine(new Dictionary<string, object> {
                {"Debug", false},
                {"Frames", true},
                {"FullFrames", false},
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

                case TestIsolationLevel.PROCESS:
                    return GetProcessTest(testcase);

                default:
                    throw new ArgumentException(String.Format("IsolationLevel {0} is not supported.", testcase.Options.IsolationLevel.ToString()), "testcase.IsolationLevel");
            }
        }

        public string FormatException(Exception ex) {
            return this.defaultEngine.GetService<ExceptionOperations>().FormatException(ex);
        }

        private static string GetIronPythonPath() {
            var path = Path.Combine(FindRoot(), "Src", "StdLib", "Lib");
            if (Directory.Exists(path)) {
                return path;
            }
            return string.Empty;
        }

        private string ReplaceVariables(string input) {
            Regex variableRegex = new Regex(@"\${([^}]+)}", RegexOptions.Compiled);
            var replacements = new Dictionary<string, string>() {
                { "ROOT", FindRoot() }
            };

            var result = input;
            var match = variableRegex.Match(input);
            while (match.Success) {
                var variable = match.Groups[1].Value;
                if (replacements.ContainsKey(variable)) {
                    result = result.Replace(match.Groups[0].Value, replacements[variable]);
                }
                match = match.NextMatch();
            }

            return result;
        }

        private int GetEngineTest(TestInfo testcase) {
            var engine = CreateEngine(testcase.Options);
            var source = engine.CreateScriptSourceFromString(
                testcase.Text, testcase.Path, SourceCodeKind.File);

            return GetResult(engine, source);
        }        

        private int GetProcessTest(TestInfo testcase) {
            int exitCode = -1;
            using (Process proc = new Process()) {
                proc.StartInfo.FileName = Executable;
                proc.StartInfo.Arguments = string.Format("\"{0}\" {1}", testcase.Path, testcase.Options.Arguments);                
                if (!string.IsNullOrEmpty(IRONPYTHONPATH)) {
                    proc.StartInfo.EnvironmentVariables["IRONPYTHONPATH"] = IRONPYTHONPATH;
                }

                if (!string.IsNullOrEmpty(testcase.Options.WorkingDirectory)) {
                    proc.StartInfo.WorkingDirectory = ReplaceVariables(testcase.Options.WorkingDirectory);
                }
                proc.StartInfo.UseShellExecute = false;
                proc.Start();
                proc.WaitForExit();
                exitCode = proc.ExitCode;
            }
            return exitCode;
        }

        private int GetScopeTest(TestInfo testcase) {
            var source = this.defaultEngine.CreateScriptSourceFromString(
                testcase.Text, testcase.Path, SourceCodeKind.File);

            return GetResult(this.defaultEngine, source);
        }

        private int GetResult(ScriptEngine engine, ScriptSource source) {
            var path = Environment.GetEnvironmentVariable("IRONPYTHONPATH");
            if(string.IsNullOrEmpty(path)) {
                Environment.SetEnvironmentVariable("IRONPYTHONPATH", IRONPYTHONPATH);
            }
            var scope = engine.CreateScope();
            engine.GetSysModule().SetVariable("argv", List.FromArrayNoCopy(new object[] { source.Path }));
            var compiledCode = source.Compile(new IronPython.Compiler.PythonCompilerOptions() { ModuleName = "__main__" });
            int res = 0;
            try {
                res = engine.Operations.ConvertTo<int>(compiledCode.Execute(scope) ?? 0);
            } catch(SystemExitException ex) {
                object otherCode;
                res = ex.GetExitCode(out otherCode);
            }
            return res;
        }
    }
}
