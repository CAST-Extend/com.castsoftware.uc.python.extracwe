from cast.analysers import log


class RuleAvoidConditionInLoop:
    #https://www.appmarq.com/public/efficiency,7204,Avoid-method-invocation-in-a-loop-termination-expression'''

    def __init__(self, module):
        self.__module = module
        #log.info("Statements {}".format(module.get_statements()))

    def start_Assignment(self, assig):
        
        # we can inspect the ast to decide
        # which nodes are convenient for analysis
        #log.info("Start assig Rule1050")
        #print_tree(assig)
        
        right = assig.get_right_expression()
        left = assig.get_left_expression()
        #log.info("LeftRight: "+left.get_type() + " - " + str(right) )
        #if not left.get_type() == 'Identifier':
        #    return
      
        varname = left.get_name()
        expression_type = str(right.get_type())
        #log.info("Varname: "+ varname + " - " + expression_type)
        # add violation to current module
        #module = self.get_module()
        #module.add_violation('CAST_Python_Rule.PREFIX_AvoidFunctionInLoopRule', assig)
        #log.info("Added violation to module {}".format(module.get_fullname()))

    def on_end(self):
        """optional callback function when analysis module is finished"""
        pass

    def get_module(self):
        return self.__module
    
    def start_MethodCall(self, ast):
        #log.info("[start_MethodCall] {}".format(ast.get_method()))
        # get the arguments
        arg0 = ast.get_argument(0, None)
       #log.info("Arguments: {}".format(arg0))
        method = ast.get_method()
        #log.info("Nome Metodo: {}".format(method.get_name()))

    #def end_MethodCall(self, ast):
        #log.info("[end_MethodCall] {}".format(ast.get_type()))
    
    #def start_Return(self, ast):
        #log.debug("[start_Return]")

    def start_ForBlock(self, ast):
        log.debug("[start_ForBlock]")
        #log.debug("[start_ForBlock] {}".format(ast.get_statements()))
        module = self.get_module()
        #module.add_violation('CAST_Python_Rule.PREFIX_AvoidFunctionInLoopRule', ast)
        #log.info("Added violation to module {}".format(module.get_fullname()))
        #print_tree(ast)

    
    def end_ForBlock(self, ast):
        log.debug("End ForBlock")
        #log.debug("[End ForBlock] {}".format(ast.get_statements()))

def print_tree(ast):
    """Utility for printing the ast in debug mode"""
    import sys
    from io import StringIO

    orig_stdout = sys.stdout
    s = StringIO()
    sys.stdout = s
    ast.print_tree()
    log.debug("printing ast ...\n{}".format(s.getvalue()))
    sys.stdout = orig_stdout