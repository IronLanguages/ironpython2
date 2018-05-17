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

using Mono.Unix.Native;

[assembly: PythonModule("spwd", typeof(IronPython.Modules.PythonSpwd), PythonModuleAttribute.PlatformFamily.Unix)]
namespace IronPython.Modules {
    
    public static class PythonSpwd {
        public const string __doc__ = @"This module provides access to the Unix shadow password database.
It is available on various Unix versions.

Shadow password database entries are reported as 9-tuples of type struct_spwd,
containing the following items from the password database (see `<shadow.h>'):
sp_namp, sp_pwdp, sp_lstchg, sp_min, sp_max, sp_warn, sp_inact, sp_expire, sp_flag.
The sp_namp and sp_pwdp are strings, the rest are integers.
An exception is raised if the entry asked for cannot be found.
You have to be root to be able to use this module.";

        [StructLayout(LayoutKind.Sequential)]
        private struct spwd {
            [MarshalAs(UnmanagedType.LPStr)]
            public string sp_namp;
            [MarshalAs(UnmanagedType.LPStr)]
            public string sp_pwdp;
            public int sp_lstchg;
            public int sp_min;
            public int sp_max;
            public int sp_warn;
            public int sp_inact;
            public int sp_expire;
            public int sp_flag;
        };        

        [PythonType("struct_spwd")]
        [Documentation(@"spwd.struct_spwd: Results from getsp*() routines.

This object may be accessed either as a 9-tuple of
  (sp_namp,sp_pwdp,sp_lstchg,sp_min,sp_max,sp_warn,sp_inact,sp_expire,sp_flag)
or via the object attributes as named in the above tuple.")]
        public class struct_spwd : PythonTuple {

            private const int LENGTH = 9;

            internal struct_spwd(string sp_nam, string sp_pwd, int sp_lstchg, int sp_min, int sp_max, int sp_warn, int sp_inact, int sp_expire, int sp_flag) {
                this.sp_nam = sp_nam;
                this.sp_pwd = sp_pwd;
                this.sp_lstchg = sp_lstchg;
                this.sp_min = sp_min;
                this.sp_max = sp_max;
                this.sp_warn = sp_warn;
                this.sp_inact = sp_inact;
                this.sp_expire = sp_expire;
                this.sp_flag = sp_flag;
            }

            [Documentation("login name")]
            public string sp_nam { get; }

            [Documentation("encrypted password")]
            public string sp_pwd { get; }

            [Documentation("date of last change")]
            public int sp_lstchg { get; }

            [Documentation("min #days between changes")]
            public int sp_min { get; }

            [Documentation("max #days between changes")]
            public int sp_max { get; }

            [Documentation("#days before pw expires to warn user about it")]
            public int sp_warn { get; }

            [Documentation("#days after pw expires until account is disabled")]
            public int sp_inact { get; }

            [Documentation("#days since 1970-01-01 when account expires")]
            public int sp_expire { get; }

            [Documentation("reserved")]
            public int sp_flag { get; }

            public override int __len__() {
                return LENGTH;
            }

            private object[] AsArray() {
                return new object[] { sp_nam, sp_pwd, sp_lstchg, sp_min, sp_max, sp_warn, sp_inact, sp_expire, sp_flag };
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
                return $"spwd.struct_spwd(sp_name='{sp_nam}', sp_pwd='{sp_pwd}', sp_lstchg={sp_lstchg}, sp_min={sp_min}, sp_max={sp_max}, sp_warn={sp_warn}, sp_inact={sp_inact}, sp_expire={sp_expire}, sp_flag={sp_flag})";
            }

            public override string ToString() {
                return __repr__(DefaultContext.Default);
            }

            public override IEnumerator __iter__() {
                return AsArray().GetEnumerator();
            }
        }

        private static struct_spwd Make(IntPtr pwd) {
            spwd p = (spwd)Marshal.PtrToStructure(pwd, typeof(spwd));
            return new struct_spwd(p.sp_namp, p.sp_pwdp, p.sp_lstchg, p.sp_min, p.sp_max, p.sp_warn, p.sp_inact, p.sp_expire, p.sp_flag);
        }

        [Documentation("Return the shadow password database entry for the given user name.")]
        public static struct_spwd getspnam(string name) {
            var pwd = _getspnam(name);
            if(pwd == IntPtr.Zero) {
                throw PythonOps.KeyError($"getspnam(): name not found");
            }

            return Make(pwd);
        }

        [Documentation("Return a list of all available shadow password database entries, in arbitrary order.")]
        public static List getspall() {
            var res = new List();
            setspent();
            IntPtr val = getspent();
            while(val != IntPtr.Zero) {
                res.Add(Make(val));
                val = getspent();
            }
            
            return res;
        }


        #region P/Invoke Declarations

        [DllImport("libc", EntryPoint="getspnam", CallingConvention=CallingConvention.Cdecl)]
        private static extern IntPtr _getspnam([MarshalAs(UnmanagedType.LPStr)] string name);

        [DllImport("libc", CallingConvention=CallingConvention.Cdecl)]
        private static extern void setspent();

        [DllImport("libc", CallingConvention=CallingConvention.Cdecl)]
        private static extern IntPtr getspent();

        #endregion

    }
}
#endif
