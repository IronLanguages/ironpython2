IronPython
===
IronPython is an open-source implementation of the Python programming language which is tightly integrated with the .NET Framework. IronPython can use the .NET Framework and Python libraries, and other .NET languages can use Python code just as easily.

IronPython can be obtained at [http://ironpython.net/](http://ironpython.net/).

| **What?** | **Where?** |
| --------: | :------------: |
| **Windows/Linux/macOS Builds** | [![Build status](https://dotnet.visualstudio.com/IronLanguages/_apis/build/status/ironpython2)](https://dotnet.visualstudio.com/IronLanguages/_build/latest?definitionId=42) |
| **Downloads** | [![NuGet](https://img.shields.io/nuget/v/IronPython.svg)](https://www.nuget.org/packages/IronPython/) [![Release](https://img.shields.io/github/release/IronLanguages/ironpython2.svg)](https://github.com/IronLanguages/ironpython2/releases/latest)|
| **Help** | [![Gitter chat](https://badges.gitter.im/IronLanguages/ironpython.svg)](https://gitter.im/IronLanguages/ironpython) [![StackExchange](https://img.shields.io/stackexchange/stackoverflow/t/ironpython.svg)](http://stackoverflow.com/questions/tagged/ironpython) |


Comparison of IronPython vs. C# for 'Hello World'

C#:

```cs
using System;
class Hello
{
    static void Main() 
    {
        Console.WriteLine("Hello World");
    }
}
```

IronPython:
```py
print "Hello World"
```
IronPython is a Dynamic Language that runs on the .NET DLR ([Dynamic Language Runtime](http://en.wikipedia.org/wiki/Dynamic_Language_Runtime)) in contrast with VB.NET and C# which are [static languages](http://en.wikipedia.org/wiki/Type_system).


IronPython can also import DLL files compiled in other languages and use functions defined therein. For example:

```py
import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import *
```

# Code of Conduct
This project has adopted the code of conduct defined by the Contributor Covenant to clarify expected behavior in our community.
For more information see the [.NET Foundation Code of Conduct](https://dotnetfoundation.org/code-of-conduct).

# Documentation

Documentation can be found here: http://ironpython.net/documentation/dotnet/


## Additional information

Please see http://wiki.github.com/IronLanguages/main for information on:
- Setting up a development environment with easy access to utility scripts
- [Building](Documentation/building.md)
- Running test

## Chat/Communication

Join our Gitter-Chat under: https://gitter.im/IronLanguages/ironpython
