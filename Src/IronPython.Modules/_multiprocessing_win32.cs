using IronPython.Runtime;
using Microsoft.Win32.SafeHandles;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

[assembly: PythonModule("_multiprocessing_win32", typeof(IronPython.Modules.MultiProcessingWin32))]
namespace IronPython.Modules {
    public static class MultiProcessingWin32 {
        public const int WAIT_OBJECT_0 = 0;
        public const int WAIT_ABANDONED_0 = 0x80;
        public const int WAIT_TIMEOUT = 0x102;
        public const int INFINITE = -1;

        public const int ERROR_IO_PENDING = 997;
        public const int ERROR_MORE_DATA = 0xEA;
        public const int ERROR_BROKEN_PIPE = 0x6D;

        [return: MarshalAs(UnmanagedType.Bool)]
        [DllImport("kernel32.dll", SetLastError = true, EntryPoint = "CloseHandle")]
        public static extern bool CloseHandle(IntPtr hObject);

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern int WriteFile(SafeFileHandle handle, byte[] bytes, int numBytesToWrite, out int numBytesWritten, IntPtr mustBeZero);

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern int ReadFile(SafeFileHandle handle, byte[] bytes, int numBytesToRead, out int numBytesRead, IntPtr mustBeZero);

        [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
        public static extern int WaitForMultipleObjects(uint handle, IntPtr[] handles, bool waitAll, uint milliseconds);

        [DllImport("kernel32.dll")]
        public static extern void ExitProcess(uint uExitCode);
    }

}
