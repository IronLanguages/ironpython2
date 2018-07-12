using System;

using IronPython.Runtime.Operations;

namespace IronPython.Runtime {
    public class PlatformsAttribute : Attribute {
        public enum PlatformFamily {
            Windows,
            Unix
        }

        public static readonly PlatformID[] WindowsFamily = { PlatformID.Win32NT, PlatformID.Win32S, PlatformID.Win32Windows, PlatformID.WinCE, PlatformID.Xbox };
        public static readonly PlatformID[] UnixFamily = { PlatformID.MacOSX, PlatformID.Unix };

        public PlatformID[] ValidPlatforms { get; protected set; }

        public bool IsPlatformValid => ValidPlatforms == null || ValidPlatforms.Length == 0 || Array.IndexOf(ValidPlatforms, Environment.OSVersion.Platform) >= 0;

        protected void SetValidPlatforms(PlatformFamily validPlatformFamily) {
            switch (validPlatformFamily) {
                case PlatformFamily.Unix:
                    ValidPlatforms = UnixFamily;
                    break;
                default:
                    ValidPlatforms = WindowsFamily;
                    break;
            }
        }
    }
}