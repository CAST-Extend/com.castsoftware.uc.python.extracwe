import ast

class NestedLoopDetector(ast.NodeVisitor):
    def __init__(self):
        self.nested_loops = []

    def visit_For(self, node):
        if self._has_nested_loop(node):
            self.nested_loops.append((node.lineno, node.col_offset, 'For'))
        self.generic_visit(node)

    def visit_While(self, node):
        if self._has_nested_loop(node):
            self.nested_loops.append((node.lineno, node.col_offset, 'While'))
        self.generic_visit(node)

    def _has_nested_loop(self, node):
        """ Check if the given node has a nested For or While loop in its body. """
        for child in node.body:
            if isinstance(child, (ast.For, ast.While)):
                return True
        return False

    def get_nested_loops(self):
        return self.nested_loops

def find_nested_loops(source_code, ast_tree):
    # Parse the source code into an AST
    try:
        tree = ast_tree
        if not ast_tree: 
            tree = ast.parse(source_code)

        # Create an instance of the NestedLoopDetector
        detector = NestedLoopDetector()
        detector.visit(tree)

        # Return the detected nested loops
        return detector.get_nested_loops(), tree
    except:
        pass

class StringConcatInLoopVisitor(ast.NodeVisitor):
    def __init__(self):
        self.concat_in_loops = []

    def visit_For(self, node):
        # Analizza il corpo del loop 'for'
        self._check_concat_in_loop(node)
        self.generic_visit(node)  # Continua a visitare nodi figli

    def visit_While(self, node):
        # Analizza il corpo del loop 'while'
        self._check_concat_in_loop(node)
        self.generic_visit(node)  # Continua a visitare nodi figli

    def _check_concat_in_loop(self, node):
        
        for stmt in node.body:
            """
            Verifica se ci sono concatenazioni inefficaci (+= con stringhe)
            all'interno del corpo del loop (for/while).
            """
            if isinstance(stmt, ast.AugAssign):  # Verifica se è un'assegnazione con +=
                if isinstance(stmt.op, ast.Add):  # Verifica se l'operatore è '+='
                    # Controlla se il valore a destra dell'assegnazione è una stringa o un'espressione di concatenazione
                    if isinstance(stmt.value, ast.Str) or self._is_string_concatenation(stmt.value):
                        self.concat_in_loops.append((stmt.lineno, stmt.col_offset))
            """
            Verifica se ci sono concatenazioni di stringhe nella funzione print 
            all'interno del corpo del loop.
            """            
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                # Verifica se la chiamata è a 'print'
                if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == 'print':
                    # Controlla se uno degli argomenti di print è una concatenazione di stringhe
                    print("Print:" + str(stmt.value.args))
                    for arg in stmt.value.args:
                        if self._is_string_concat2(arg):
                            self.concat_in_loops.append((stmt.lineno, stmt.col_offset))
    
    def _is_string_concatenation(self, value):
        """
        Controlla se un'espressione è una concatenazione di stringhe.
        """
        # Se è un'espressione BinOp (es: "str" + "altro_str"), verifica se le parti sono stringhe
        return isinstance(value, ast.BinOp) and isinstance(value.op, ast.Add) and (
            isinstance(value.left, ast.Str) or isinstance(value.right, ast.Str)
        )

    def _is_string_or_concat(self, node):
        """
        Verifica se un argomento di 'print' è una stringa o una concatenazione di stringhe.
        """
        # Verifica se è una stringa costante
        if isinstance(node, ast.Str) or isinstance(node, ast.Constant) and isinstance(node.value, str):
            return True
        
        # Verifica se è una concatenazione con '+'
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return (self._is_string_or_concat(node.left) or self._is_string_or_concat(node.right))
        
        return False
    def _is_string_concat2(self, node):
        """
        Verifica se un'espressione è una concatenazione di stringhe usando l'operatore '+'
        o una lista di espressioni concatenata con le virgole (che viene automaticamente
        gestita da print in Python 3).
        """
        print("Node:" + str(node))
        # Verifica se è un'operazione binaria con '+'
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return isinstance(node.left, ast.Str) or isinstance(node.right, ast.Str)
        # Verifica se ci sono più argomenti separati da virgole (usati come concatenazione)
        if isinstance(node, ast.Tuple):
            return any(isinstance(el, ast.Str) for el in node.elts)
        return False
        
def find_string_concat_in_loops(source_code, ast_tree):
    """
    Trova concatenazioni di stringhe inefficaci nei loop in un codice sorgente Python.
    :param source_code: Stringa contenente il codice sorgente Python.
    :return: Lista di tuple con le righe dei loop e delle concatenazioni inefficienti.
    """
    tree = ast_tree
    if not ast_tree: 
        tree = ast.parse(source_code)
    visitor = StringConcatInLoopVisitor()
    visitor.visit(tree)
    return visitor.concat_in_loops, tree
  

# Example usage
if __name__ == "__main__":
   
# Specifica il percorso del file
    file_path = "C:\\AAWork\\Software\\Sorgenti\\pythonsample\\samples\\test01\\file.py"

# Apri il file in modalità lettura ('r') e leggi tutto il contenuto
    with open(file_path, 'r') as file:
     python_code = file.read()

    nested_loops, tree = find_string_concat_in_loops(python_code, None)
    print(nested_loops)
    if nested_loops:
        print("Concat string in loops found at:")
        for lineno, col_offset in nested_loops:
            print("From Line %s:%s" % (lineno, col_offset))
    else:
        print("No nested loops found.")


