#Test at application level

import unittest
from cast.application.test import run
from cast.application import create_postgres_engine, Server
import sys
import os
# Aggiungi il percorso della directory superiore al percorso di ricerca
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(sys.path)
# Ora puoi importare il modulo
from application_extension import FunctionLoopsApplicationExtension

class Test(unittest.TestCase):


    def testName(self):
        print("starting test....")
        my_engine=create_postgres_engine(port=2284)
        run(kb_name='pythonext_local', application_name='PythonExt',engine=my_engine) 
        server = Server(my_engine)# 8.3.5 !!
        #cb = server.get_schema('pythonext_test_local')
        cb = server.get_schema('pythonext_local')
        print(cb.get_applications())
        application = cb.get_application('PythonExt')
        print('Fine')
        '''
        #Non serve chiamare esplicitamente, viene già chiamata prima
        print("Instancing extension....")
        extension = FunctionLoopsApplicationExtension()   # get an instance of my class
        print("end application call....")
        extension.end_application(application)  # run this extension point, just 1 of the class' methods
        '''
                
if __name__ == "__main__":
    unittest.main()



