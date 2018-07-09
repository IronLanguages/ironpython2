# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information.


##
## Test the cStringIO module
##

import cStringIO
import unittest

from iptest import run_test

text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

class CStringIOTest(unittest.TestCase):

    def call_close(self, i):
        self.assertEqual(i.closed, False)
        i.close()
        self.assertEqual(i.closed, True)
        i.close()
        self.assertEqual(i.closed, True)
        i.close()
        self.assertEqual(i.closed, True)
        

    def call_isatty(self, i):
        self.assertEqual(i.isatty(), False)


    def call_read(self, i):
        self.assertEqual(i.read(), text)
        self.assertEqual(i.read(), "")
        self.assertEqual(i.read(), "")
        i.close()
        i.close()
        self.assertRaises(ValueError, i.read)
    
    def call_readline(self, i):
        self.assertEqual(i.readline(), "Line 1\n")
        self.assertEqual(i.readline(), "Line 2\n")
        self.assertEqual(i.readline(), "Line 3\n")
        self.assertEqual(i.readline(), "Line 4\n")
        self.assertEqual(i.readline(), "Line 5")
        self.assertEqual(i.readline(), "")
        i.close()
        self.assertRaises(ValueError, i.readline)

    def call_readline_n(self, i):
        self.assertEqual(i.readline(50), "Line 1\n")
        self.assertEqual(i.readline(0), "")
        self.assertEqual(i.readline(1), "L")
        self.assertEqual(i.readline(9), "ine 2\n")
        self.assertEqual(i.readline(50), "Line 3\n")
        self.assertEqual(i.readline(6), "Line 4")
        self.assertEqual(i.readline(50), "\n")
        self.assertEqual(i.readline(50), "Line 5")
        i.close()
        self.assertRaises(ValueError, i.readline)

    def call_readlines(self, i):
        self.assertEqual(i.readlines(), ["Line 1\n", "Line 2\n", "Line 3\n", "Line 4\n", "Line 5"])
        self.assertEqual(i.readlines(), [])
        i.close()
        self.assertRaises(ValueError, i.readlines)

    def call_readlines_n(self, i):
        self.assertEqual(i.readlines(10), ["Line 1\n", "Line 2\n"])
        self.assertEqual(i.readlines(50), ["Line 3\n", "Line 4\n", "Line 5"])
        self.assertEqual(i.readlines(50), [])
        i.close()
        self.assertRaises(ValueError, i.readlines)

    def call_getvalue(self, i):
        self.assertEqual(i.getvalue(), text)
        self.assertEqual(i.read(6), "Line 1")
        self.assertEqual(i.getvalue(True), "Line 1")
        self.assertEqual(i.getvalue(), text)
        i.close()
        self.assertRaises(ValueError, i.getvalue)
    
    def call_next(self, i):
        self.assertEqual(i.__iter__(), i)
        self.assertEqual(i.next(), "Line 1\n")
        self.assertEqual(i.next(), "Line 2\n")
        self.assertEqual([l for l in i], ["Line 3\n", "Line 4\n", "Line 5"])
        i.close()
        self.assertRaises(ValueError, i.readlines)
    
    

    def call_reset(self, i):
        self.assertEqual(i.read(0), "")
        self.assertEqual(i.read(4), "Line")
        self.assertEqual(i.readline(), " 1\n")
        i.reset()
        self.assertEqual(i.read(4), "Line")
        self.assertEqual(i.readline(), " 1\n")
        i.reset()
        self.assertEqual(i.read(37),text)
        i.reset()
        self.assertEqual(i.read(38),text)
        i.close()
        self.assertRaises(ValueError, i.read, 5)
        self.assertRaises(ValueError, i.readline)

    def call_seek_tell(self, i):
        self.assertEqual(i.read(4), "Line")
        self.assertEqual(i.tell(), 4)
        i.seek(10)
        self.assertEqual(i.tell(), 10)
        self.assertEqual(i.read(3), "e 2")
        i.seek(15, 0)
        self.assertEqual(i.tell(), 15)
        self.assertEqual(i.read(5), "ine 3")
        i.seek(3, 1)
        self.assertEqual(i.read(4), "ne 4")
        i.seek(-5, 2)
        self.assertEqual(i.tell(), len(text) - 5)
        self.assertEqual(i.read(), "ine 5")
        i.seek(1000)
        self.assertEqual(i.tell(), 1000)
        self.assertEqual(i.read(), "")
        i.seek(2000, 0)
        self.assertEqual(i.tell(), 2000)
        self.assertEqual(i.read(), "")
        i.seek(400, 1)
        self.assertEqual(i.tell(), 2400)
        self.assertEqual(i.read(), "")
        i.seek(100, 2)
        self.assertEqual(i.tell(), len(text) + 100)
        self.assertEqual(i.read(), "")
        i.close()
        self.assertRaises(ValueError, i.tell)
        self.assertRaises(ValueError, i.seek, 0)
        self.assertRaises(ValueError, i.seek, 0, 2)
    
    def call_truncate(self, i):
        self.assertEqual(i.read(6), "Line 1")
        i.truncate(20)
        self.assertEqual(i.tell(), 20)
        self.assertEqual(i.getvalue(), "Line 1\nLine 2\nLine 3")
        i.truncate(30)
        self.assertEqual(i.tell(), 20)
        self.assertEqual(i.getvalue(), "Line 1\nLine 2\nLine 3")
        i.reset()
        self.assertEqual(i.tell(), 0)
        self.assertEqual(i.read(6), "Line 1")
        i.truncate()
        self.assertEqual(i.getvalue(), "Line 1")
        i.close()
        self.assertRaises(ValueError, i.truncate)
        self.assertRaises(ValueError, i.truncate, 10)

    def call_write(self, o):
        self.assertEqual(o.getvalue(), text)
        o.write("Data")
        o.write(buffer(' 1'))
        self.assertRaises(TypeError, o.write, None)
        self.assertEqual(o.read(7), "\nLine 2")
        self.assertEqual(o.getvalue(), "Data 1\nLine 2\nLine 3\nLine 4\nLine 5")
        o.close()
        self.assertRaises(ValueError, o.write, "Hello")

    def call_writelines(self, o):
        self.assertEqual(o.getvalue(), text)
        o.writelines(["Data 1", "Data 2"])
        self.assertEqual(o.read(8), "2\nLine 3")
        self.assertEqual(o.getvalue(), "Data 1Data 22\nLine 3\nLine 4\nLine 5")
        self.assertRaises(TypeError, o.writelines, [buffer('foo')])
        self.assertRaises(TypeError, o.writelines, [None])
        o.close()
        self.assertRaises(ValueError, o.writelines, "Hello")
        self.assertRaises(ValueError, o.writelines, ['foo', buffer('foo')])
        self.assertRaises(TypeError, o.writelines, [buffer('foo')])

    def call_softspace(self, o):
        o.write("Hello")
        o.write("Hi")
        o.softspace = 1
        self.assertEqual(o.softspace, 1)
        self.assertEqual(o.getvalue(), "HelloHiLine 2\nLine 3\nLine 4\nLine 5")

    def call_flush(self, i):
        i.flush()
        self.assertEqual(i,i)

    def init_StringI(self):
        return cStringIO.StringIO(text)

    def init_StringO(self):
        o = cStringIO.StringIO()
        o.write(text)
        o.reset()
        return o

    def init_emptyStringI(self):
        return cStringIO.StringIO("")
    
    def test_empty(self):
        i = self.init_emptyStringI()
        
        # test closed
        self.assertEqual(i.closed,False)
        i.close()
        self.assertEqual(i.closed,True)
        
        
        #test read
        i = self.init_emptyStringI()
        self.assertEqual(i.read(),"")
        i.close()
        self.assertRaises(ValueError, i.read)
        i.close()
        self.assertRaises(ValueError, i.read, 2)
        
        #test readline
        i = self.init_emptyStringI()
        self.assertEqual(i.readline(),"")
        i.close()
        self.assertRaises(ValueError, i.readline)
        
        i = self.init_emptyStringI()
        self.assertEqual(i.readline(0),"")
        i.close()
        self.assertRaises(ValueError, i.readline)
        
        #test readlines
        i = self.init_emptyStringI()
        self.assertEqual(i.readlines(),[])
        
        i = self.init_emptyStringI()
        self.assertEqual(i.readlines(0),[])
        
        #test getvalue
        i = self.init_emptyStringI()
        self.assertEqual(i.getvalue(),"")
        self.assertEqual(i.getvalue(True),"")
        i.close()
        self.assertRaises(ValueError, i.getvalue)
        
        #test iter
        i = self.init_emptyStringI()
        self.assertEqual(i.__iter__(), i)
        
        #test reset
        i = self.init_emptyStringI()
        self.assertEqual(i.read(0), "")
        i.reset()
        self.assertEqual(i.read(1), "")
        i.reset()
        self.assertEqual(i.readline(), "")
        i.close()
        self.assertRaises(ValueError, i.read, 2)
        self.assertRaises(ValueError, i.readline)
        
        #test seek,tell,read
        i = self.init_emptyStringI()
        self.assertEqual(i.read(0), "")
        self.assertEqual(i.tell(), 0)
        self.assertEqual(i.read(1), "")
        self.assertEqual(i.tell(), 0)
        i.seek(2)
        self.assertEqual(i.tell(), 2)
        self.assertEqual(i.read(),"")
        i.close()
        self.assertRaises(ValueError, i.tell)
        self.assertRaises(ValueError, i.seek, 0)
        self.assertRaises(ValueError, i.seek, 0, 2)
        
        #test truncate
        i = self.init_emptyStringI()
        i.truncate(0)
        self.assertEqual(i.tell(), 0)
        i.truncate(1)
        self.assertEqual(i.tell(), 0)
        i.close()
        self.assertRaises(ValueError, i.truncate)
    
    def test_cp8567(self):
        for x in ["", "1", "12", "12345", 
                    #u"123", #CodePlex 19220
                    ]:
            for i in [5, 6, 7, 2**8, 100, 2**16-1, 2**16, 2**16, 2**31-2, 2**31-1]:
                cio = cStringIO.StringIO(x)
                cio.truncate(i)
                self.assertEqual(cio.tell(), len(x))
                cio.close()
    
    
    
    def test_i_o(self):
        for t in [  self.call_close,
                    self.call_isatty,
                    self.call_read,
                    self.call_readline,
                    self.call_readline_n,
                    self.call_readlines,
                    self.call_readlines_n,
                    self.call_getvalue,
                    self.call_next,
                    self.call_reset,
                    self.call_seek_tell,
                    self.call_truncate,
                    self.call_flush ]:
            i = self.init_StringI()
            t(i)
            
            o= self.init_StringO()
            t(o)

    def test_o(self):
        for t in [  self.call_write,
                    self.call_writelines,
                    self.call_softspace ]:
            o = self.init_StringO()
            t(o)

    def test_cp22017(self):
        m = cStringIO.StringIO()
        m.seek(2)
        m.write("hello!")
        self.assertEqual(m.getvalue(), '\x00\x00hello!')
        m.seek(2)
        self.assertEqual(m.getvalue(), '\x00\x00hello!')

run_test(__name__)
