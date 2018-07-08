# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information.


import copy_reg
import imp
import random
import sys
import unittest

from iptest import run_test

class testclass(object):
    pass

class myCustom2:
    pass

class CopyRegTest(unittest.TestCase):

    @unittest.expectedFailure
    def test_constructor_neg(self):
        'https://github.com/IronLanguages/main/issues/443'
        class KOld: pass
        
        self.assertRaises(TypeError, copy_reg.constructor, KOld)

 
    def test_constructor(self):
        #the argument can be callable
        copy_reg.constructor(testclass)
        
        #the argument can not be callable
        self.assertRaises(TypeError,copy_reg.constructor,0)
        self.assertRaises(TypeError,copy_reg.constructor,"Hello")
        self.assertRaises(TypeError,copy_reg.constructor,True)


    def test__newobj__(self):
        
        #the second argument is omitted
        result = None
        result = copy_reg.__newobj__(object)
        self.assertTrue(result != None,
            "The method __newobj__ did not return an object")
                        
        #the second argument is an int object
        result = None
        a = 1
        result = copy_reg.__newobj__(int,a)
        self.assertTrue(result != None,
            "The method __newobj__ did not return an object")
            
        #the method accept multiple arguments
        reseult = None
        class customtype(object):
            def __new__(cls,b,c,d):
                return object.__new__(cls)
            def __init__(self):
                pass
        c = True
        d = "argu"
        e = 3
        result = copy_reg.__newobj__(customtype,c,d,e)
        self.assertTrue(result != None,
            "The method __newobj__ did not return an object")


    #TODO: @skip("multiple_execute")
    def test_add_extension(self):
        global obj
        obj = object()

        #The module is system defined module:random
        copy_reg.add_extension(random,obj,100)

        #The module is a custom mudole or the module argument is not a type of module
        global mod
        mod = imp.new_module('module')
        sys.modules['argu1'] = mod
        import argu1
        copy_reg.add_extension(argu1,obj,1)

        module = True
        copy_reg.add_extension(module,obj,6)

        # the value is zero or less than zero
        module = "module"
        self.assertRaises(ValueError,copy_reg.add_extension,module,obj,0)
        self.assertRaises(ValueError,copy_reg.add_extension,module,object(),-987654)

        # the key is already registered with code
        self.assertRaises(ValueError,copy_reg.add_extension,argu1,object(),100)

        # the code is already in use for key
        self.assertRaises(ValueError,copy_reg.add_extension,random,obj,100009)

    #TODO: @skip("multiple_execute")
    def test_remove_extension(self):
        #delete extension
        copy_reg.remove_extension(random,obj,100)
        import argu1
        copy_reg.remove_extension(argu1,obj,1)
        module = True
        copy_reg.remove_extension(module,obj,6)

        #remove extension which has not been registed
        self.assertRaises(ValueError,copy_reg.remove_extension,random,obj,2)
        self.assertRaises(ValueError,copy_reg.remove_extension,random,object(),100)
        self.assertRaises(ValueError,copy_reg.remove_extension,argu1,obj,1)

        copy_reg.add_extension(argu1,obj,1)
        self.assertRaises(ValueError,copy_reg.remove_extension,argu1,obj,0)


    def test_extension_registry(self):
        #test getattr of the attribute and how the value of this attribute affects other method
        copy_reg.add_extension('a','b',123)
        key = copy_reg._inverted_registry[123]
        result = copy_reg._extension_registry
        code = result[key]
        self.assertTrue(code == 123,
                "The _extension_registry attribute did not return the correct value")
                
        copy_reg.add_extension('1','2',999)
        result = copy_reg._extension_registry
        code = result[('1','2')]
        self.assertTrue(code == 999,
                "The _extension_registry attribute did not return the correct value")
        
        #general test, try to set the attribute then to get it
        myvalue = 3885
        copy_reg._extension_registry["key"] = myvalue
        result = copy_reg._extension_registry["key"]
        self.assertTrue(result == myvalue,
            "The set or the get of the attribute failed")
    
    def test_inverted_registry(self):
        copy_reg.add_extension('obj1','obj2',64)
        #get
        result = copy_reg._inverted_registry[64]
        self.assertTrue(result == ('obj1','obj2'),
                "The _inverted_registry attribute did not return the correct value")
        
        #set
        value = ('newmodule','newobj')
        copy_reg._inverted_registry[10001] = value
        result = copy_reg._inverted_registry[10001]
        self.assertTrue(result == value,
                "The setattr of _inverted_registry attribute failed")


    def test_extension_cache(self):
        #set and get the attribute
        rand = random.Random()
        value = rand.getrandbits(8)
        copy_reg._extension_cache['cache1'] = value
        result = copy_reg._extension_cache['cache1']
        self.assertTrue(result == value,
            "The get and set of the attribute failed")
        
        value = rand.getrandbits(16)
        copy_reg._extension_cache['cache2'] = value
        result = copy_reg._extension_cache['cache2']
        self.assertTrue(result == value,
            "The get and set of the attribute failed")

        #change the value of the attribue
        value2 = rand.getrandbits(4)
        copy_reg._extension_cache['cache1'] = value2
        result = copy_reg._extension_cache['cache1']
        self.assertTrue(result == value2,
            "The get and set of the attribute failed")
        
        if not copy_reg._extension_cache.has_key('cache1') or  not copy_reg._extension_cache.has_key('cache2'):
            Fail("Set of the attribute failed")
            
        copy_reg.clear_extension_cache()
        if  copy_reg._extension_cache.has_key('cache1') or copy_reg._extension_cache.has_key('cache2'):
            Fail("The method clear_extension_cache did not work correctly ")

    def test_reconstructor(self):
        reconstructor_copy = copy_reg._reconstructor
        try:
            obj = copy_reg._reconstructor(object, object, None)   
            self.assertTrue(type(obj) is object)

            #set,get, the value is a random int
            rand = random.Random()
            value = rand.getrandbits(8)
            copy_reg._reconstructor = value
            result = copy_reg._reconstructor
            self.assertTrue(result == value,
                "set or get of the attribute failed!")
        
            #the value is a string
            value2 = "value2"
            copy_reg._reconstructor = value2
            result = copy_reg._reconstructor
            self.assertTrue(result == value2,
                "set or get of the attribute failed!")
        
            #the value is a custom type object
            value3 = testclass()
            copy_reg._reconstructor = value3
            result = copy_reg._reconstructor
            self.assertTrue(result == value3,
                "set or get of the attribute failed!")
        finally:               
            copy_reg._reconstructor = reconstructor_copy
   

    def test_pickle(self):
        def testfun():
            return testclass()
            
        # type is a custom type
        copy_reg.pickle(type(testclass), testfun)
        
        #type is a system type
        systype = type(random.Random())
        copy_reg.pickle(systype,random.Random.random)
        
        #function is not callable
        func = "hello"
        self.assertRaises(TypeError,copy_reg.pickle,testclass,func)
        func = 1
        self.assertRaises(TypeError,copy_reg.pickle,testclass,func)
        func = random.Random()
        self.assertRaises(TypeError,copy_reg.pickle,testclass,func)
    
    def test_dispatch_table(self):
        result = copy_reg.dispatch_table
        #CodePlex Work Item 8522
        #self.assertEqual(5,len(result))
        
        temp = {
                "abc":"abc123",
                "def":"def123",
                "ghi":"ghi123"
            }
        copy_reg.dispatch_table = temp
        self.assertEqual(temp,copy_reg.dispatch_table)
        
        temp = {
                1:"abc123",
                2:"def123",
                3:"ghi123"
            }
        copy_reg.dispatch_table = temp
        self.assertEqual(temp,copy_reg.dispatch_table)
        
        temp = {
                1:123,
                8:789,
                16:45465
            }
        copy_reg.dispatch_table = temp
        self.assertEqual(temp,copy_reg.dispatch_table)
        
        #set dispathc_table as empty
        temp ={}
        copy_reg.dispatch_table = temp
        self.assertEqual(temp,copy_reg.dispatch_table)

    def test_pickle_complex(self):
        #http://ironpython.codeplex.com/WorkItem/View.aspx?WorkItemId=21908
        #if not is_cli:
        self.assertEqual(copy_reg.pickle_complex(1), (complex, (1, 0)))
        
        #negative tests
        self.assertRaises(AttributeError,copy_reg.pickle_complex,"myargu")
        obj2 = myCustom2()
        self.assertRaises(AttributeError,copy_reg.pickle_complex,obj2)

run_test(__name__)
