# -*- coding: utf-8 -*-
# from http://stackoverflow.com/questions/10661079/restricting-pythons-syntax-to-execute-user-code-safely-is-this-a-safe-approach
import ast # Abstract Syntax Tree (Python)

# Definir niviles seguros de ejecucion (por ejemplo, por cada clase en FCyP)
# Definir Excepciones

# Funciones matemáticas permitidas.
math_functions = set([
    #math library
    'acos', 'acosh', 'asin', 'asinh', 'atan', 'atan2', 'atanh',
    'ceil', 'copysign', 'cos', 'cosh', 'degrees', 'e', 'erf',
    'erfc', 'exp', 'expm1', 'fabs', 'factorial', 'floor', 'fmod',
    'frexp', 'fsum', 'gamma', 'hypot', 'isinf', 'isnan', 'ldexp',
    'lgamma', 'log', 'log10', 'log1p', 'modf', 'pi', 'pow', 'radians',
    'sin', 'sinh', 'sqrt', 'tan', 'tanh', 'trunc',
    #built-in
    'abs', 'max', 'min', 'range', 'xrange'
    #random?
    #others modules?
    ])

# Diccionario entre Nodos no permitidos y mensajes de error

# Funciones de String permitidas.
string_function = set([
    ])

# select anothers modules, but it is necesary the from-import & import
# Nodos sintácticos permitidos por defecto.
allowed_node_types = set([
    #Meta
    'Module', 'Assign', 'Expr', 'arguments', 'Params', 'Param',
    #Functions
    'FunctionDef', 'Return',
    # Strings
    'Print',
    #Control
    'For', 'If', 'Else', 'While',
    #Data
    'Store', 'Load', 'AugAssign', 'Subscript', 'Lt', 'LtE',
    #Datatypes
    'Num', 'Tuple', 'List', 'Str', 'Set',
    #Operations
    'BinOp', 'Add', 'Sub', 'Mult', 'Div', 'Mod', 'Compare',
    #Imports
    'ImportFrom', 'alias'
    ])

safe_names = set([
    'True', 'False', 'None'
    ])

class SyntaxChecker(ast.NodeVisitor):
    # Mensajes de error
    FUNCTION_CALL_ERROR = "No se permite el uso de funciones"
    DEF_FUNCTION_ERROR = "No se permite la definicion de funciones"
    FOR_ERROR = "No se pemite el uso de ciclos For-in"
    WHILE_ERROR = "No se permite el uso de ciclos While"
    TUPLE_ERROR = "No se permite el uso de estructuras complejas"
    LIST_ERROR = "No se permite el uso de listas"
    # ----------------------------------------#
    # Modos del parser sináctico
    CALCULATOR_MODE = 0
    FOR_MODE = 1
    WHILE_LISTS_MODE = 2
    DEF_FUNCTION_MODE = 3
    COMPLEX_STRUCTURES_MODE = 4
    FULL_MODE = 5
    # ----------------------------------------#
    def __init__(self, python_mode):
        self.mode = python_mode
        self.allowed_functions = list()
        if self.mode == SyntaxChecker.CALCULATOR_MODE:
            self.allowed_functions.append(math_functions)
    
    def check(self, syntax):
        tree = ast.parse(syntax)
        #print ast.dump(tree)
        self.visit(tree)

    def visit_Call(self, node):
        print self.allowed_functions
        print node.func.id in self.allowed_functions
        if not (node.func.id in self.allowed_functions):
            print node.func.id
            raise SyntaxError("No se permite el uso de la funcion: %s"%node.func.id)
        else:
            ast.NodeVisitor.generic_visit(self, node)
    def visit_Tuple(self, node):
        if not(self.mode == SyntaxChecker.COMPLEX_STRUCTURES_MODE or self.mode == SyntaxChecker.FULL_MODE):
            raise SyntaxError(SyntaxChecker.TUPLE_ERROR)
        return;
    
    def visit_Set(self, node):
        if not(self.mode == SyntaxChecker.COMPLEX_STRUCTURES_MODE or self.mode == SyntaxChecker.FULL_MODE):
            raise SyntaxError(SyntaxChecker.TUPLE_ERROR)
        return;

    def visit_List(self, node):
        if not(self.mode == SyntaxChecker.WHILE_LISTS_MODE or self.mode == SyntaxChecker.COMPLEX_STRUCTURES_MODE or self.mode == SyntaxChecker.FULL_MODE):
            raise SyntaxError(SyntaxChecker.LIST_ERROR)
        return;

    def visit_For(self,node):
        if not(self.mode == SyntaxChecker.FOR_MODE or self.mode == SyntaxChecker.COMPLEX_STRUCTURES_MODE or self.mode == SyntaxChecker.FULL_MODE):
            raise SyntaxError(SyntaxChecker.FOR_ERROR)
        return;
    
    def visit_While(self,node):
        if not(self.mode == SyntaxChecker.WHILE_LISTS_MODE or self.mode == SyntaxChecker.COMPLEX_STRUCTURES_MODE or self.mode == SyntaxChecker.FULL_MODE):
            raise SyntaxError(SyntaxChecker.WHILE_ERROR)
        return;

    def visit_Name(self, node):
        try:
            eval(node.id)
        except NameError:
            ast.NodeVisitor.generic_visit(self, node)
        else:
            if node.id not in safe_names and not(node.id in self.allowed_functions):
                raise SyntaxError("%s is a reserved name!"%node.id)
            else:
                ast.NodeVisitor.generic_visit(self, node)
    
    def visit_FunctionDef(self, node):
        if not(self.mode == SyntaxChecker.DEF_FUNCTION_MODE or self.mode == SyntaxChecker.COMPLEX_STRUCTURES_MODE or self.mode == SyntaxChecker.FULL_MODE):
            raise SyntaxError(SyntaxChecker.DEF_FUNCTION_ERROR)
        return;

    def generic_visit(self, node):
        if type(node).__name__ not in allowed_node_types:
            raise SyntaxError("%s is not allowed!"%type(node).__name__)
        else:
            ast.NodeVisitor.generic_visit(self, node)


"""
if __name__ == '__main__':
    x = SyntaxChecker()
    while True:
        try:
            x.check(raw_input())
        except Exception as e:
            print e
"""