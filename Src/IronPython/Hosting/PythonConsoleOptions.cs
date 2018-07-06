// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the Apache 2.0 License.
// See the LICENSE file in the project root for more information.
#if FEATURE_FULL_CONSOLE
using System;
using Microsoft.Scripting.Hosting.Shell; 

namespace IronPython.Hosting {
    [CLSCompliant(true)]
    public /* TODO: sealed */ class PythonConsoleOptions : ConsoleOptions {

        private bool _ignoreEnvironmentVariables;
        private bool _skipImportSite;
        private bool _skipFistSourceLine;
        private string _runAsModule;
        private bool _basicConsole = false;

        public bool IgnoreEnvironmentVariables {
            get { return _ignoreEnvironmentVariables; }
            set { _ignoreEnvironmentVariables = value; }
        }

        public bool SkipImportSite {
            get { return _skipImportSite; }
            set { _skipImportSite = value; }
        }

        public string ModuleToRun {
            get { return _runAsModule; }
            set { _runAsModule = value; }
        }

        /// <summary>
        /// Skip the first line of the code to execute. This is useful for executing Unix scripts which
        /// have the command to execute specified in the first line.
        /// This only apply to the script code executed by the ScriptEngine APIs, but not for other script code 
        /// that happens to get called as a result of the execution.
        /// </summary>
        public bool SkipFirstSourceLine {
            get { return _skipFistSourceLine; }
            set { _skipFistSourceLine = value; }
        }

        public bool BasicConsole {
            get { return _basicConsole; }
            set { _basicConsole = value; }
        }
    }
}
#endif
