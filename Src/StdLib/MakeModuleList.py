# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information.


# Copies working standard library modules to the provided output directory
# Usage: ipy getModuleList.py <output directory>

#--Imports---------------------------------------------------------------------
import sys, os
import clr
import shutil

#List of predetermined directories and files which should not be included in
#the MSI
excludedDirectories = []
excludedFiles       = []

def find_root():
    test_dirs = ['Src', 'Build', 'Package', 'Tests', 'Util']
    root = os.getcwd()
    test = all([os.path.exists(os.path.join(root, x)) for x in test_dirs])
    while not test:
        root = os.path.dirname(root)
        test = all([os.path.exists(os.path.join(root, x)) for x in test_dirs])
    return root

root = find_root()
#Automatically determine what's currently not working under IronPython
sys.path.append(os.path.join(root, 'Tests', 'Tools'))
base_dir = os.path.abspath(os.path.join(root, 'Src', 'StdLib'))

import stdmodules
BROKEN_LIST = stdmodules.main(base_dir)

if len(BROKEN_LIST)<10:
    #If there are less than ten modules/directories listed in BROKEN_LIST
    #chances are good stdmodules is broken!
    exc_msg = "It's highly unlikely that only %d CPy standard modules are broken under IP!" % len(BROKEN_LIST)
    print exc_msg
    raise Exception(exc_msg)

#Specify Packages and Modules that should not be included here.
excludedDirectories += [
                        "/Lib/test",
                        "/Lib/idlelib",
                        "/Lib/lib-tk",
                        "/Lib/site-packages"
                        ]
excludedDirectories += [x for x in BROKEN_LIST if not x.endswith(".py")]

excludedFiles += [                  
                  #*.py modules IronPython has implemented in *.cs
                  "/Lib/copy_reg.py",
                  "/Lib/re.py",
                ]
excludedFiles += [x for x in BROKEN_LIST if x.endswith(".py") and not any(x.startswith(y) for y in excludedDirectories)]

excludedDirectoriesCase = [os.path.join(base_dir, x[1:]).replace('/', '\\') + '\\' for x in excludedDirectories]
excludedDirectories = [x.lower() for x in excludedDirectoriesCase]
excludedFilesCase = [os.path.join(base_dir, x[1:]).replace('/', '\\') for x in excludedFiles]
excludedFiles = [x.lower() for x in excludedFilesCase]

f = file('StdLib.pyproj')
content = ''.join(f.readlines())
header = '      <!-- Begin Generated Project Items -->'
    
footer = '      <!-- End Generated Project Items -->'
if header == -1 or footer == -1:
    print "no header or footer"
    sys.exit(1)

start = content.find(header)
end = content.find(footer)
f.close()
content_start = content[:start + len(header)] + '\n'
content_end = content[end:]
files = []

for excluded in excludedDirectoriesCase:
    files.append("      $(StdLibPath)\\{}**\\*;\n".format(excluded[len(base_dir) + 5:]))

for excluded in excludedFilesCase:
    files.append("      $(StdLibPath)\\{};\n".format(excluded[len(base_dir) + 5:]))

file_list = ''.join(files)
f = file('StdLib.pyproj', 'w')
f.write(content_start)
f.write(file_list)
f.write(content_end)
f.close()
