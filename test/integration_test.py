
## Test at analysis level
import unittest
import cast.analysers.test

class TestIntegration(unittest.TestCase):
    
     def testRegisterPlugin(self):
        analysis = cast.analysers.test.UATestAnalysis('Python')
        #analysis.add_selection(r"C:\\AAWork\Software\\Sorgenti\\Est1\\Python\\com.castsoftware.python_extracwe\\tests\\samples")
        #analysis.add_selection(r"C:\\AAWork\Software\\Sorgenti\\i-nergy-main")
        analysis.add_selection(r"C:\\AAWork\\Software\\Sorgenti\\pythonsample\\samples\\test01")
         # add dependency to python extension
        analysis.add_dependency(r'C:\\ProgramData\\CAST\\CAST\\Extensions\\com.castsoftware.internal.platform.0.9.21')
        analysis.add_dependency(r'C:\\ProgramData\\CAST\\CAST\\Extensions\\com.castsoftware.html5.2.2.3-funcrel')
        analysis.add_dependency(r'C:\\ProgramData\\CAST\\CAST\\Extensions\\com.castsoftware.wbslinker.1.7.31')
        analysis.add_dependency(r'C:\\ProgramData\\CAST\\CAST\\Extensions\\com.castsoftware.python.1.5.4-funcrel')
        #analysis.add_dependency(r'C:\\ProgramData\\CAST\\CAST\\Extensions\\com.castsoftware.uc.python_extracwe.1.1.0-funcrel')
        print(analysis.test_directory)
        print(analysis.ua_language)
        print(analysis.plugin_name)
        print(analysis.plugin_path)
        print(analysis.flat_path)
        analysis.set_verbose(True)
        analysis.run()
        
        try:
            f = analysis.get_object_by_name('f1foo', 'CAST_Python_Method')
            print("Function: ", f)
            methods = analysis.get_objects_by_category('CAST_Python_Method')
            print("The total number of functions/methods: {}".format(len(methods)))
            modules = analysis.get_objects_by_category('CAST_Python_SourceCode')
            print("The total number of Modules: {}".format(len(modules)))
            #print(analysis.result)
            #self.assertTrue(f)
            #sourceFile

            #self.assertFalse(has_violation)
            # foo.py# with_violation.py
            module = analysis.get_object_by_name('file.py', 'sourceFile')
            # the presence of a violation is marked in a property with a non-zero number
            has_violation = module.get_value('CAST_Python_Rule.PREFIX_AvoidFunctionInLoopRule')
            print(has_violation)
            #self.assertTrue(has_violation)
            viols = analysis.get_objects_by_category("CAST_Python_Rule.PREFIX_AvoidFunctionInLoopRule")
            print(viols)
   
            #print(analysis.result)
            #analysis.get_violations(f,'CAST_Python_Rule.AvoidUsingInvalidObjectsInAll')
            print(analysis.get_objects_by_name("CAST_Python_Rule.PREFIX_AvoidFunctionInLoopRule"))
            print(analysis.get_violations(module))
        except Exception as err:
            print("Other error occurred: ", err)

   

if __name__ == "__main__":
    unittest.main()