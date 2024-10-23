import cast_upgrade_1_6_22 # @UnusedImport
from cast.application import ApplicationLevelExtension, ReferenceFinder
import logging
from UtilityFunction import find_nested_loops # type: ignore
from UtilityFunction import find_string_concat_in_loops # type: ignore
from cast.analysers import Bookmark

class FunctionLoopsApplicationExtension(ApplicationLevelExtension):

    #initialization of variables
    nbFileScanned = 0
    nbViolationCallingFunctionInConditionLoop = 0
    nbViolationNestedLoops = 0
    nbViolationConcatStringInLoop = 0
    
    # one RF for multiples patterns (launched by SDK with an OR) - first pattern(s) for skipping the comments (match first)
    rfLoop = ReferenceFinder()
    #rfLoop.add_pattern('COMMENTEDline1'     , before='', element = "^\s*#.*$|#.*$", after='')
    #rfLoop.add_pattern('COMMENTEDline2'     , before='', element = "\s#", after='')
  
    rfLoop.add_pattern('whileCallingFunction', before='', element = "while\s+\w+\s*[<>=!]+\s*\w+\s*\(.*\)\s*:" , after='')
    rfLoop.add_pattern('forCallingFunction' , before='', element = "for\s+\w+\s+in\s+range\s*\(\s*\w+\s*\(.*\)\s*\)\s*:"  , after='')
    #rfLoop.add_pattern('concatStringInLoop1' , before='', element = "(for|while)\s*\(.*?\)\s*:\s*(\n|.)*?\b\w+\s*\+=\s*\".*?\"|\b\w+\s*\+=\s*\w+\s*\+.*"  , after='')
    #rfLoop.add_pattern('concatStringInLoop2' , before='', element = "(for|while)\s*\(.*\):\s*(.|\n)*?\n\s*.*\+=\s*[\"'].*[\"']"  , after='')
    #fLoop.add_pattern('concatStringInLoop3' , before='', element = "(for\s+\w+\s+in\s+.*:\s*|\bwhile\s+.*:\s*)[\w\[\]]+\s*\+=\s*\w+"  , after='')


    def scan_program(self, application, file):
        logging.debug("INIT scan_program : file id: >" +str(file.id))
        
        # search all patterns in current file
        try:
            references = [reference for reference in self.rfLoop.find_references_in_file(file)]
        except FileNotFoundError:
            logging.warning("Wrong file or file path, from Vn-1 or previous " + str(file))
        else:
            # for debugging and traversing the results
            
            for reference in references:
                logging.debug("**************Pattern In Progress: " + reference.pattern_name)
                logging.debug("DONE: reference found: >" +str(reference))
                if  reference.pattern_name in ['whileCallingFunction', 'forCallingFunction'] :
                    logging.info("GOTCHA ! Found " + reference.pattern_name + " - " + str(reference.value) + " - "+ str(file)) 
                    artifact, bookm  = my_find_most_specific_object(file,reference.bookmark.begin_line, 1)
                    # TODO : check if artifact is eligible for the property and aligned with QR scope
                    # TODO : or use Try Except block to protect the save_violation from 
                    # saving the violation
                    #Deve essere: CAST_Python_SourceCode, Method o Script (solo fino a versione 1.5.4...con la 1.6...non funziona con script)
                    #if str(artifact.get_type()).startswith("CAST_Python_Source") or str(artifact.get_type()).startswith("CAST_Python_Method"):
                    if str(artifact.get_type()).startswith("CAST_Python_"):
                        artifact.save_violation('Python_Loops_CustomMetrics.CIT_AvoidFunctionInLoopRule', reference.bookmark)
                        #file.save_violation('Python_Loops_CustomMetrics.CIT_AvoidFunctionInLoopRule', reference.bookmark)
                        self.nbViolationCallingFunctionInConditionLoop += 1
                        logging.debug("saving violation for artifact type >" +str(artifact.get_type())+ " - #: "+ str(self.nbViolationCallingFunctionInConditionLoop))
                
    def scan_file_for_nested_loop(self, application, file):
        logging.info("INIT scan_file for nested loop : file id: >" +str(file.id))
        
        # search all patterns in current file
        try:
           # cast.application.open_source_file(path, encoding=None) !!!!!!!!!!!!!!!!
            logging.info("scan file %s for Nested loops:"%(file.get_path()))
            # Apri il file in modalità lettura ('r') e leggi tutto il contenuto
            #pfile = application.open_source_file(file.get_path(), encoding=None) 
            #python_code = pfile.read()
            with open(file.get_path() , 'r') as pfile:
                python_code = pfile.read()

        except FileNotFoundError:
            logging.warning("Wrong file or file path, from Vn-1 or previous " + str(file))
        else: 
            nested_loops, tree = find_nested_loops(python_code, None)
            if nested_loops:
                logging.info("Nested loops found in file %s at:"%(file))
                for lineno, col_offset, loop_type in nested_loops:
                    logging.info("From Line %s:%s - %s loop" % (lineno, col_offset, loop_type))
                    artifact, bookm = my_find_most_specific_object(file,lineno, col_offset)
                    logging.info("Artifact: %s" %(artifact.get_type()))
                    if str(artifact.get_type()).startswith("CAST_Python_") or str(artifact.get_type()).startswith("sourceFile"):
                        artifact.save_violation('Python_Loops_CustomMetrics.CIT_AvoidNestedLoops', bookm)
                        self.nbViolationNestedLoops += 1
                        logging.info("saving nested loop violation for artifact type >" +str(artifact.get_type())+ " - #: "+ str(self.nbViolationNestedLoops))
            else:
                logging.info("Nested loops not found in file %s at:"%(file))
            logging.info("scan file %s for string concat in loops:"%(file.get_path()))
            stringconcat, tree = find_string_concat_in_loops(python_code, tree)  
            if stringconcat:
                logging.info("String concat in loop found in file %s at:"%(file))
                for lineno, col_offset in stringconcat:
                    logging.info("Strig concat riga: %s, colonna: %s" %(lineno, col_offset))
                    artifact, bookm = my_find_most_specific_object(file,lineno, col_offset)
                    logging.info("Artifact: %s" %(artifact.get_type()))
                    if str(artifact.get_type()).startswith("CAST_Python_") or str(artifact.get_type()).startswith("sourceFile"):
                            artifact.save_violation('Python_Loops_CustomMetrics.CIT_AvoidStringConcatInLoop', bookm)
                            self.nbViolationConcatStringInLoop += 1
                            logging.info("saving strig concat loop violation for artifact type >" +str(artifact.get_type())+ " - #: "+ str(self.nbViolationConcatStringInLoop))

              
    def end_application(self, application):
        logging.info("end_application: "+ application.get_name())

        #print(dir(application))

        #declare ownership for 1 property (this call also performs the required initialization cleaning)
        application.declare_property_ownership('Python_Loops_CustomMetrics.CIT_AvoidFunctionInLoopRule',['CAST_Python_Rule'])
        application.declare_property_ownership('Python_Loops_CustomMetrics.CIT_AvoidNestedLoops',['CAST_Python_Rule'])
        application.declare_property_ownership('Python_Loops_CustomMetrics.CIT_AvoidStringConcatInLoop',['CAST_Python_Rule'])
        
        logging.debug("Declaration done: "+ application.get_name())
        files = application.get_files() # list all files saved by JEE Analyzer 
        for o in files:     #looping through source files (path are in Deploy folder)
            logging.debug("file found: >" + str(o.get_path()))
            # check if file is analyzed source code, or if it generated (Unknown) : useful in case of Java ?
            if not o.get_path():
                continue
            # check if file is a Java program  -- useless test ?
            if not (o.get_path().endswith('.py')):
                continue
            #cast.analysers.log.debug("file found: >" + str(o.get_path()))
            #list_sub_object(o)
            
            logging.info("Scanning file for condition loop")
            self.scan_program(application, o) 
            logging.info("Scanning file for nested loop")
            self.scan_file_for_nested_loop(application, o)            
            self.nbFileScanned += 1
        
        # Final reporting in ApplicationPlugins.castlog
        logging.info("STATISTICS: Number of Python files scanned : " + str(self.nbFileScanned))
        logging.info("STATISTICS: Number of anti-pattern occurrences for function calling  in test condition  Loop patterns: " + str(self.nbViolationCallingFunctionInConditionLoop))
        logging.info("STATISTICS: Number of anti-pattern occurrences for concat string in loop patterns: " + str(self.nbViolationConcatStringInLoop))
        logging.info("STATISTICS: Number of anti-pattern occurrences for nested Loop patterns: " + str(self.nbViolationNestedLoops))


# sent by MRO - email Tuesday, March 3, 2020 5:35 PM, subject: RE: Java QR en end_application - Avoid loops with always true exit condition
def my_find_most_specific_object(_file, line, column):
    """
    Sometimes, some objects have the exact same position than the Java method, so we recode this.
    """
    result = _file
    result_position = None #_file.get_position() #None
    logging.debug("File: %s - %d - %d" % (_file, line, column))
    for sub_object in _file.load_objects():
        # @type sub_object:cast.application.Object
       # logging.debug("Sub_Object: " + str(sub_object))
        # under a java file we can have variable or executable
        #if not (sub_object.is_variable() or sub_object.is_executable()):
        #    return sub_object
            #continue  # AGR: go to next sub_object, skipping Spring MVC Operations for instance
        #logging.debug("Is Not Var or Exec" +str(sub_object))        
        for position in sub_object.get_positions():
            if position.contains_position(line, column) and (not result_position or result_position.contains(position)):
                result = sub_object
                result_position = position
                logging.debug(str(result))           
    return result, result_position

# sent by MRO - email Tuesday, March 3, 2020 5:35 PM, subject: RE: Java QR en end_application - Avoid loops with always true exit condition
def list_sub_object(_file):
    """
    Sometimes, some objects have the exact same position than the Java method, so we recode this.
    """
    logging.debug("listsubobject: " + str(_file)  + " - "+str(_file.get_type()))
    result = _file
    for sub_object in _file.load_objects():
        # @type sub_object:cast.application.Object
        logging.debug("Sub_Object: " + str(sub_object))
        
    return result

