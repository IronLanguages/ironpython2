// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the Apache 2.0 License.
// See the LICENSE file in the project root for more information.


using System;
using System.Reflection;

#if FEATURE_REFEMIT

namespace Microsoft.Scripting.Generation {
    internal class ParameterInfoWrapper {
        private readonly ParameterInfo parameterInfo;
        private readonly Type parameterType;
        private readonly string name;

        public ParameterInfoWrapper(ParameterInfo parameterInfo) {
            this.parameterInfo = parameterInfo;
        }

        public ParameterInfoWrapper(Type parameterType, string name = null) {
            this.parameterType = parameterType;
            this.name = name;
        }

        public Type ParameterType {
            get {
                if (parameterInfo != null)
                    return parameterInfo.ParameterType;
                return parameterType;
            }
        }

        public string Name {
            get {
                if (parameterInfo != null)
                    return parameterInfo.Name;
                return name;
            }
        }

        public ParameterAttributes Attributes {
            get {
                if (parameterInfo != null)
                    return parameterInfo.Attributes;
                return default(ParameterAttributes);
            }
        }
    }
}

#endif
