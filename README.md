IronPython
===
[![Linux/OSX Build Status](https://travis-ci.org/IronLanguages/ironpython2.svg?branch=master)](https://travis-ci.org/IronLanguages/ironpython2)
[![Windows Build status](https://ci.appveyor.com/api/projects/status/53h9jt1bym8wunh1?svg=true)](https://ci.appveyor.com/project/AlexEarl/ironpython2)
[![Gitter chat](https://badges.gitter.im/IronLanguages/ironpython.png)](https://gitter.im/IronLanguages/ironpython)

IronPython is an open-source implementation of the Python programming language which is tightly integrated with the .NET Framework. IronPython can use the .NET Framework and Python libraries, and other .NET languages can use Python code just as easily.

IronPython can be obtained at [http://ironpython.net/](http://ironpython.net/).

Comparison of IronPython vs. C# for 'Hello World'

c#:

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


Iron Python can also import DLL files compiled in other languages and use functions defined therein. For example:

```py
import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import *
```

# Documentation

Documentation can be found here: http://ironpython.net/documentation/dotnet/


## Additional information

Please see http://wiki.github.com/IronLanguages/main for information on:
- Setting up a development environment with easy access to utility scripts
- Building
- Running test

## Chat/Communication

Join our Gitter-Chat under: https://gitter.im/IronLanguages/ironpython
