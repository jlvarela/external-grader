""" 
Pruebas de analisis del AST de un programa escrito en Python
para agregar niveles de Python a el External Grader (proyecto PID)
"""

import ast
import symtable
import sys

tree = ast.parse(sys.stdin.read())

# Podemos usar la funncion visit_FunctionDef (solo sera invocada si encuentra una definicion de funcion)

# usamos la clase que recorre el arbol. Para ello definimos que se hace al visitar los nodos del arbol
class FuncLister(ast.NodeVisitor):
	# Lo que hacemos cuando visitamos la definicion de una funcion
	# Las funciones visit_(name) pueden usar cualquier nombre de nodo para hacer algo cuando encuentran un nodo en particular
	# en este caso, definicion de funciones. Para saber que nombre usar, hay que ver la gramatica de Python.
	def visit_FunctionDef(self, node):
		# sencillamente mostramos el nombre de la funcion por pantalla (podemos, por ejemplo, arrojar error sintactico)
		print(node.name)
		raise SyntaxError("No debes definir funciones")
		self.generic_visit(node)

	# Otra visita a otro tipo de nodo
	def visit_For(self, node):
		raise SyntaxError("No debes utilizar ciclos for-in")

# recorremos el arbol
fc = FuncLister()
fc.visit(tree)