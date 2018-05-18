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
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.IO.Pipes;
using System.Runtime.InteropServices;

using Microsoft.Scripting.Runtime;

using IronPython.Runtime;
using IronPython.Runtime.Operations;

using System.Numerics;

[assembly: PythonModule("grp", typeof(IronPython.Modules.PythonGrp), PythonModuleAttribute.PlatformFamily.Unix)]
namespace IronPython.Modules {
    
    public static class PythonGrp {
        public const string __doc__ = @"Access to the Unix group database.
        
Group entries are reported as 4-tuples containing the following fields
from the group database, in order:

  gr_name   - name of the group
  gr_passwd - group password (encrypted); often empty
  gr_gid    - numeric ID of the group
  gr_mem    - list of members
  
The gid is an integer, name and password are strings.  (Note that most
users are not explicitly listed as members of the groups they are in
according to the password database.  Check both databases to get
complete membership information.)";

        [StructLayout(LayoutKind.Sequential)]
        private struct group {
            [MarshalAs(UnmanagedType.LPStr)]
            public string gr_name;
            [MarshalAs(UnmanagedType.LPStr)]
            public string gr_passwd;
            public int gr_gid;
            public IntPtr gr_mem;
        };

        [PythonType("struct_group")]
        [Documentation(@"grp.struct_group: Results from getgr*() routines.

This object may be accessed either as a tuple of
  (gr_name,gr_passwd,gr_gid,gr_mem)
or via the object attributes as named in the above tuple.
")]
        public class struct_group : PythonTuple {

            internal struct_group(string gr_name, string gr_passwd, int gr_gid, List gr_mem) :
                base(new object[] { gr_name, gr_passwd, gr_gid, gr_mem }) {
            }

            [Documentation("group name")]
            public string gr_name { 
                get {
                    return (string)_data[0];
                }
            }

            [Documentation("password")]
            public string gr_passwd { 
                get {
                    return (string)_data[1];
                }
            }

            [Documentation("group id")]
            public int gr_gid { 
                get {
                    return (int)_data[2];
                }
            }

            [Documentation("group members")]
            public List gr_mem { 
                get {
                    return (List)_data[3];
                }
            }

            public override string/*!*/ __repr__(CodeContext/*!*/ context) {
                return $"grp.struct_group(gr_name='{gr_name}', gr_passwd='{gr_passwd}', gr_gid={gr_gid}, gr_mem={gr_mem.__repr__(context)})";
            }
        }

        private static struct_group Make(IntPtr pwd) {
            group g = (group)Marshal.PtrToStructure(pwd, typeof(group));
            return new struct_group(g.gr_name, g.gr_passwd, g.gr_gid, new List(MarshalStringArray(g.gr_mem)));
        }

        private static IEnumerable<string> MarshalStringArray(IntPtr arrayPtr)
        {
            if (arrayPtr != IntPtr.Zero)
            {
                IntPtr ptr = Marshal.ReadIntPtr(arrayPtr);
                while (ptr != IntPtr.Zero)
                {
                    string key = Marshal.PtrToStringAnsi(ptr);
                    yield return key;
                    arrayPtr = new IntPtr(arrayPtr.ToInt64() + IntPtr.Size);
                    ptr = Marshal.ReadIntPtr(arrayPtr);
                }
            }
        }

        public static struct_group getgrgid(uint gid) {
            var grp = _getgrgid(gid);
            if(grp == IntPtr.Zero) {
                throw PythonOps.KeyError($"getgrgid(): gid not found: {gid}");
            }

            return Make(grp);
        }

        public static struct_group getgrnam(string name) {
            var grp = _getgrnam(name);
            if(grp == IntPtr.Zero) {
                throw PythonOps.KeyError($"getgrnam()): name not found: {name}");
            }

            return Make(grp);
        }

        public static List getgrall() {
            var res = new List();
            setgrent();
            IntPtr val = getgrent();
            while(val != IntPtr.Zero) {
                res.Add(Make(val));
                val = getgrent();
            }
            
            return res;
        }


        #region P/Invoke Declarations

        [DllImport("libc", EntryPoint="getgrgid", CallingConvention=CallingConvention.Cdecl)]
        private static extern IntPtr _getgrgid(uint uid);

        [DllImport("libc", EntryPoint="getgrnam", CallingConvention=CallingConvention.Cdecl)]
        private static extern IntPtr _getgrnam([MarshalAs(UnmanagedType.LPStr)] string name);

        [DllImport("libc", CallingConvention=CallingConvention.Cdecl)]
        private static extern void setgrent();

        [DllImport("libc", CallingConvention=CallingConvention.Cdecl)]
        private static extern IntPtr getgrent();

        #endregion

    }
}
#endif
