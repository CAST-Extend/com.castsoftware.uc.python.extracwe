'''
PYTHON Analyser Level Extension operations
    Author:        SOL
    date:          16/09/2024
    description:   Encompasses all customizations at analysis level.
    Log:
        16/09/2024:  First release
'''
#https://cast-projects.github.io/Extension-SDK/doc/application_level.html
#https://github.com/CAST-projects/Extension-SDK/tree/master/samples/analyzer_level/python/python.quality_rule

import cast_upgrade_1_6_22 # @UnusedImport

from cast.analysers.ua import Extension
from cast.analysers import log
from cast import analysers
from cast import Event
#from cast import quality_rules
#from quality_rules import ExternalQualityRules
from interpreters1 import RuleAvoidConditionInLoop
from utility import loggingInfo, loggingError
from utility import EXTENSION_VER, EXTENSION_DATE, LANG_FINGERPRINT
from utility import EXTENSION_DEBUG
from cast.application import open_source_file
from cast.analysers import CustomObject
from cast.analysers import Bookmark
import re
import uuid

class MyPythonExtension(Extension):
    def __init__(self):
        super(MyPythonExtension, self).__init__()
        self.extensions = ['.py', '.jy', '.yml', '.yaml'] 

    def start_analysis(self):
        log.info('Start Analysis event....................')
        # retreive the pathes of the analysed csproj
        #projects = options.get_source_projects()
        #print(projects)
        # resistant (for unit tests)
        
        #log.debug("Broadcast external rule manager ..")
        #self.broadcast('add_quality_rules', externalQualityRules)
        #log.debug(".. done")
        log.info('END Start Analysis event....................')
        
     
    def end_analysis(self):
        log.info("End analysis...............")
        
    
    def start_file(self, file):
        log.info("Start file event################")
        log.info("File: "+file.get_path())
    
    def end_file(self, file):
        log.info("End file event####################")
        Extension.end_file(self, file)
                
        log.info(file)
        
    def start_object(object):
        log.info("Start Object event")
        log.info("Start Object: "+object.get_fullname())
        log.info("Start Object: "+object.get_name())
        

    @Event('com.castsoftware.python', 'add_quality_rules')
    def add_quality_rules(self, externalQualityRules):
        log.info("add quality rule event")
        
        def add_rule(interpreter):
            """Add interpreter and current plugin for proper logging"""
            externalQualityRules.add_interpreter(interpreter, self.get_plugin())
            log.info("Added rule interpreter: {}".format(interpreter.__name__))

        # Add rule interpreters
        #add_rule(SimpleInfoPrint)
        #add_rule(RuleAllContainingOnlyStrings)
        add_rule(RuleAvoidConditionInLoop)

        
    @Event('com.castsoftware.python', 'finished_rule_analysis')
    def on_finished_rule_analysis(self):
        """
        Here one can perform post quality-rule analysis processing.
        Interpreter class attributes can be used to collect data
        from different analyzed modules.
        """
        log.info("[on_finished_rule_analysis]")