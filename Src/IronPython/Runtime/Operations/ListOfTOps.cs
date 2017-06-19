/* ****************************************************************************
 *
 * Copyright (c) Microsoft Corporation. 
 *
 * This source code is subject to terms and conditions of the Apache License, Version 2.0. A 
 * copy of the license can be found in the License.html file at the root of this distribution. If 
 * you cannot locate the  Apache License, Version 2.0, please send an email to 
 * dlr@microsoft.com. By using this source code in any fashion, you are agreeing to be bound 
 * by the terms of the Apache License, Version 2.0.
 *
 * You must not remove this notice, or any other, from this software.
 *
 *
 * ***************************************************************************/

using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;

using Microsoft.Scripting.Runtime;

using IronPython.Runtime.Types;

namespace IronPython.Runtime.Operations {
    public static class ListOfTOps<T> {
        public static string __repr__(CodeContext/*!*/ context, List<T> self) {
            List<object> infinite = PythonOps.GetAndCheckInfinite(self);
            if (infinite == null) {
                return "[...]";
            }

            int index = infinite.Count;
            infinite.Add(self);
            try {
                StringBuilder res = new StringBuilder();
                res.Append("List[");
                res.Append(DynamicHelpers.GetPythonTypeFromType(typeof(T)).Name);
                res.Append("](");
                if (self.Count > 0) {
                    res.Append("[");
                    string comma = "";
                    foreach (T obj in self) {
                        res.Append(comma);
                        res.Append(PythonOps.Repr(context, obj));
                        comma = ", ";
                    }
                    res.Append("]");
                }

                res.Append(")");
                return res.ToString();
            } finally {
                System.Diagnostics.Debug.Assert(index == infinite.Count - 1);
                infinite.RemoveAt(index);
            }
        }

        #region Python __ methods

        public static bool __contains__(List<T> l, T item) {
            return l.Contains(item);
        }

        public static string __format__(CodeContext/*!*/ context, List<T> self, [BytesConversion]string formatSpec) {
            return ObjectOps.__format__(context, self, formatSpec);
        }

        public static int __len__(List<T> l) {
            return l.Count;
        }

        [SpecialName]
        public static T GetItem(List<T> l, int index) {
            return l[PythonOps.FixIndex(index, l.Count)];
        }

        [SpecialName]
        public static T GetItem(List<T> l, object index) {
            return GetItem(l, Converter.ConvertToIndex(index));
        }

        [SpecialName]
        public static List<T> GetItem(List<T> l, Slice slice) {
            if (slice == null) throw PythonOps.TypeError("string indices must be slices or integers");
            int start, stop, step;
            slice.indices(l.Count, out start, out stop, out step);
            if (step == 1) {
                return stop > start ? l.Skip(start).Take(stop - start).ToList() : new List<T>();
            } else {
                int index = 0;
                List<T> newData = null;
                if (step > 0) {
                    if (start > stop) return new List<T>();

                    int icnt = (stop - start + step - 1) / step;
                    newData = new List<T>(icnt);
                    for (int i = start; i < stop; i += step) {
                        newData[index++] = l[i];
                    }
                } else {
                    if (start < stop) return new List<T>();

                    int icnt = (stop - start + step + 1) / step;
                    newData = new List<T>(icnt);
                    for (int i = start; i > stop; i += step) {
                        newData[index++] = l[i];
                    }
                }
                return newData;
            }
        }

        public static List<T> __getslice__(List<T> self, int x, int y) {
            Slice.FixSliceArguments(self.Count, ref x, ref y);
            if (x >= y) return new List<T>();

            return self.Skip(x).Take(y - x).ToList();
        }


        #endregion
    }
}
