This page documents various differences between IronPython and C Python.

* IRONPYTHONSTARTUP is used instead of PYTHONSTARTUP

* IRONPYTHONPATH is used instead of PYTHONPATH

* In C Python before version 3, strings are ascii and unicode is a special type.  From 3 onward strings are unicode and ascii strings use the b'string' form.  IronPython is otherwise python 2 but the strings are unicode by default to match the CTS string type and so string literals and string semantics in general is more like python 3 than python 2.

* Interaction with COM objects is handled by the CLR rather than a python library binding to the native COM dlls.