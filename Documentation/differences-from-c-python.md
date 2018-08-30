This page documents various differences between IronPython and CPython.

* IRONPYTHONSTARTUP is used instead of PYTHONSTARTUP

* IRONPYTHONPATH is used instead of PYTHONPATH

* In CPython before version 3, strings are ASCII and Unicode is a special type. From 3 onward strings are Unicode and ASCII strings use the b'string' form. IronPython is otherwise Python 2 but the strings are Unicode by default to match the CTS string type and so string literals and string semantics in general are more like Python 3 than Python 2.

* Interaction with COM objects is handled by the CLR rather than a python library binding to the native COM dlls.
