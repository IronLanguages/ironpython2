/* ****************************************************************************
 *
 * Copyright (c) Microsoft Corporation. 
 *
 * This source code is subject to terms and conditions of the Microsoft Public License. A 
 * copy of the license can be found in the License.html file at the root of this distribution. If 
 * you cannot locate the  Microsoft Public License, please send an email to 
 * ironpy@microsoft.com. By using this source code in any fashion, you are agreeing to be bound 
 * by the terms of the Microsoft Public License.
 *
 * You must not remove this notice, or any other, from this software.
 *
 *
 * ***********************************************************************/

#if FEATURE_NATIVE || NETCOREAPP2_0

using System;
using System.Collections;
using System.ComponentModel;
using System.IO;
using System.IO.Pipes;
using System.Runtime.InteropServices;

using Microsoft.Scripting.Runtime;

using IronPython.Runtime;
using IronPython.Runtime.Operations;

using System.Numerics;

[assembly: PythonModule("pwd", typeof(IronPython.Modules.PythonPwd), PythonModuleAttribute.PlatformFamily.Unix)]
namespace IronPython.Modules {
    
    public static class PythonPwd {
        public const string __doc__ = @"This module provides access to the Unix password database.
It is available on all Unix versions.

Password database entries are reported as 7-tuples containing the following
items from the password database (see `<pwd.h>'), in order:
pw_name, pw_passwd, pw_uid, pw_gid, pw_gecos, pw_dir, pw_shell.
The uid and gid items are integers, all others are strings. An
exception is raised if the entry asked for cannot be found.";

        [StructLayout(LayoutKind.Sequential)]
        private struct passwd_linux {
            [MarshalAs(UnmanagedType.LPStr)]
            public string pw_name;
            [MarshalAs(UnmanagedType.LPStr)]
            public string pw_passwd;
            public int pw_uid;
            public int pw_gid;
            [MarshalAs(UnmanagedType.LPStr)]
            public string pw_gecos;
            [MarshalAs(UnmanagedType.LPStr)]
            public string pw_dir;
            [MarshalAs(UnmanagedType.LPStr)]
            public string pw_shell;
        };

        [StructLayout(LayoutKind.Sequential)]
        private struct passwd_osx {
            [MarshalAs(UnmanagedType.LPStr)]
            public string pw_name;
            [MarshalAs(UnmanagedType.LPStr)]
            public string pw_passwd;
            public int pw_uid;
            public int pw_gid;
            public ulong pw_change;
            [MarshalAs(UnmanagedType.LPStr)]
            public string pw_class;
            [MarshalAs(UnmanagedType.LPStr)]
            public string pw_gecos;
            [MarshalAs(UnmanagedType.LPStr)]
            public string pw_dir;
            [MarshalAs(UnmanagedType.LPStr)]
            public string pw_shell;
            public ulong pw_expire;
        };

        [PythonType("struct_passwd")]
        [Documentation(@"pwd.struct_passwd: Results from getpw*() routines.

This object may be accessed either as a tuple of
  (pw_name,pw_passwd,pw_uid,pw_gid,pw_gecos,pw_dir,pw_shell)
or via the object attributes as named in the above tuple.")]
        public class struct_passwd : PythonTuple {

            private const int LENGTH = 7;

            internal struct_passwd(string pw_name, string pw_passwd, int pw_uid, int pw_gid, string pw_gecos, string pw_dir, string pw_shell) {
                this.pw_name = pw_name;
                this.pw_passwd = pw_passwd;
                this.pw_uid = pw_uid;
                this.pw_gid = pw_gid;
                this.pw_gecos = pw_gecos;
                this.pw_dir = pw_dir;
                this.pw_shell = pw_shell;
            }

            [Documentation("user name")]
            public string pw_name { get; }

            [Documentation("password")]
            public string pw_passwd { get; }

            [Documentation("user id")]
            public int pw_uid { get; }

            [Documentation("group id")]
            public int pw_gid { get; }

            [Documentation("real name")]
            public string pw_gecos { get; }

            [Documentation("home directory")]
            public string pw_dir { get; }

            [Documentation("shell program")]
            public string pw_shell { get; }

            public override int __len__() {
                return LENGTH;
            }

            private object[] AsArray() {
                return new object[] { pw_name, pw_passwd, pw_uid, pw_gid, pw_gecos, pw_dir, pw_shell };
            }

            public override object __getslice__(int start, int stop) {
                Slice.FixSliceArguments(LENGTH, ref start, ref stop);

                return MakeTuple(ArrayOps.GetSlice(AsArray(), start, stop));
            }

            public override object this[Slice slice] {
                get {
                    int start, stop, step;
                    slice.indices(LENGTH, out start, out stop, out step);

                    return MakeTuple(ArrayOps.GetSlice(AsArray(), start, stop, step));
                }
            }

            public override object this[int index] {
                get {
                    if(index > LENGTH || index < 0) {
                        throw PythonOps.IndexError("tuple index out of range");
                    }

                    return AsArray()[index];                    
                }
            }

            public override string/*!*/ __repr__(CodeContext/*!*/ context) {
                return $"pwd.struct_passwd(pw_name='{pw_name}', pw_passwd='{pw_passwd}', pw_uid={pw_uid}, pw_gid={pw_gid}, pw_gecos='{pw_gecos}', pw_dir='{pw_dir}', pw_shell='{pw_shell}')";
            }

            public override string ToString() {
                return __repr__(DefaultContext.Default);
            }

            public override IEnumerator __iter__() {
                return AsArray().GetEnumerator();
            }
        }

        private static struct_passwd Make(IntPtr pwd) {
            struct_passwd res = null;
            if(Environment.OSVersion.Platform == PlatformID.MacOSX) {
                passwd_osx p = (passwd_osx)Marshal.PtrToStructure(pwd, typeof(passwd_osx));
                res = new struct_passwd(p.pw_name, p.pw_passwd, p.pw_uid, p.pw_gid, p.pw_gecos, p.pw_dir, p.pw_shell);
            } else {                
                passwd_linux p = (passwd_linux)Marshal.PtrToStructure(pwd, typeof(passwd_linux));
                res = new struct_passwd(p.pw_name, p.pw_passwd, p.pw_uid, p.pw_gid, p.pw_gecos, p.pw_dir, p.pw_shell); 
            }

            return res;
        }

        [Documentation("Return the password database entry for the given numeric user ID.")]
        public static struct_passwd getpwuid(object uid) {
            if(uid is int id) {
                var pwd = _getpwuid(id);
                if(pwd == IntPtr.Zero) {
                    throw PythonOps.KeyError($"getpwuid(): uid not found: {id}");
                }

                return Make(pwd);                
            }

            if(uid is long || uid is BigInteger) {
                throw PythonOps.KeyError("getpwuid(): uid not found");
            }

            throw PythonOps.TypeError($"integer argument expected, got {PythonOps.GetPythonTypeName(uid)}");
        }

        [Documentation("Return the password database entry for the given user name.")]
        public static struct_passwd getpwnam(string name) {
            var pwd = _getpwnam(name);
            if(pwd == IntPtr.Zero) {
                throw PythonOps.KeyError($"getpwname(): name not found: {name}");
            }

            return Make(pwd);
        }

        [Documentation("Return a list of all available password database entries, in arbitrary order.")]
        public static List getpwall() {
            var res = new List();
            setpwent();
            IntPtr val = getpwent();
            while(val != IntPtr.Zero) {
                res.Add(Make(val));
                val = getpwent();
            }
            
            return res;
        }


        #region P/Invoke Declarations

        [DllImport("libc", EntryPoint="getpwuid", CallingConvention=CallingConvention.Cdecl)]
        private static extern IntPtr _getpwuid(int uid);

        [DllImport("libc", EntryPoint="getpwnam", CallingConvention=CallingConvention.Cdecl)]
        private static extern IntPtr _getpwnam([MarshalAs(UnmanagedType.LPStr)] string name);

        [DllImport("libc", CallingConvention=CallingConvention.Cdecl)]
        private static extern void setpwent();

        [DllImport("libc", CallingConvention=CallingConvention.Cdecl)]
        private static extern IntPtr getpwent();

        #endregion

    }
}
#endif
