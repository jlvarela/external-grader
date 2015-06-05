# CUIDADO CON EL MENSAJE EN HTML - ya esta solucionado con ET
# Construir una factoria para los graders
# Aun Exec y SameOutput corren en modo no seguro (instalar codeJail)
# Sera necesario la utilizacion de sintaxChecker (subconjunto permitido de Python) y codeJail (recursos de la maquina)
# Falta agregar un reloj
import util
import logging
import xml.etree.ElementTree as ET
#codejail provee un timer para la ejecucion a dos niveles (CPU, REALTIME)
from simple_timer import *
#aun probando sintaxchecker
from syntax_checker import SyntaxChecker as parser
#instalado en /usr/local/lib/python2.7/dist-packages/codejail-0.1-py2.7.egg
import codejail.jail_code
#import jailcode.jailcode.safe_exec

class BaseGrader(object):
	"""
	   Clase base para un Grader (calificador)
	"""
	def __init__(self, grader_name):
		self.grader_name = grader_name
		msg = "<p>not graded</p>"
		self.set_answer(msg)
		self.log = logging.getLogger("{0} [{1}]".format(__package__, grader_name))

	def grade(self, student_code, correct_code, score, test):
		self.log.critical("BaseGrader must not be implemented!")
		raise NotImplementedError()

	# Siempre responde, aunque ocurra un error en la forma de la respuesta.
	# Para este caso, se envia un mensaje de error.
	def get_answer(self):
		try:
			# testing malformed HTML message in answer
			# is it neccesary to test other parts in answer??
			ET.XML(self.grader_answer["msg"])
		except ET.ParseError as e:
			self.log.error("the HTML message is invalid\n {0}\nmessage: {1}".format(e.msg, self.grader_answer["msg"]))
			msg = "<p>grader error</p>"
			self.set_answer(False, 0, msg=msg)
			return self.grader_answer
			# make a better answer
			# print( "ERROR in {0} : {1}".format( ETree.ParseError.filename, ETree.ParseError.msg ) )
		return self.grader_answer	

	def set_answer(self, correct=False, score=0, msg="msg"):
		answer = {"correct": correct, 
				  "score":   score, 
				  "msg":     msg, 
				  "grader_id": self.grader_name}
		self.grader_answer = answer
	
class DummyGrader(BaseGrader):
	"""
	   DummyGrader permite retorna siempre correcto a cualquier ejercicio que
	   ingrese el estudiante.
	"""
	def __init__(self, grader_name):
		super(DummyGrader, self).__init__(grader_name)
	
	def grade(self, student_code="", staff_code="", score=1, test=""):
		msg = "<p>good job!</p>"
		self.set_answer(True, score, msg)
		return True

class UnsafeExecGrader(BaseGrader):
	"""
	   Este Grader ejecuta el codigo del estudiante, y siempre retorna exitoso.
	   CUIDADO: Para ejecutar exec, existen dos mecanismos de seguridad:
	     timer: limite maximo de ejecucion permitida.
	     parser: conjunto lexico y sintactico permitido.
	"""
	def __init__(self, grader_name):
		super(ExecGrader, self).__init__(grader_name)
	
	def grade(self, student_code, staff_code="", score=1, test=""):

		try:
			# setting a timer for a time slice
			# for instance is set to 2 seconds
			timer = SimpleTimer(2)
			timer.start()
			# checking if student's code is in python's allowed syntax
			# for now there is only one python's allowed syntax set
			parser().check(student_code)
			# executing the student's code
			exec student_code
			# cancel the timer
			timer.cancel()
			# setting answer
			msg = "<p>Buen trabajo!</p>"
			self.set_answer(True, score, msg)
			return True		
			
		except SyntaxError as e:
			timer.cancel()
			msg = "<p>Ocurrio un error lexico o sintactico en tu codigo. Revisalo en busca de errores.</p>"
			self.set_answer(False, 0, msg)
			return False
		except TimeOut as e:
			timer.cancel()
			msg = "<p>Se a alcanzado el <b>limite de tiempo permitido</b> para ejecion. Revisa el codigo en busca de posibles errores.</p>"
			self.set_answer(False, 0, msg)
			return False
		except:
			msg = "<p><b>Ocurrio un error inesperado</b>. Vuelve a cargar la pagina o intentalo mas tarde</p>"
			self.set_answer(False, 0, msg)
			return False
		finally:
			pass
		# 	#msg = "<p>Grader error</p>"
		# 	#self.set_answer(False, 0, msg)
		# 	# change to false
		# 	#return True

class SafeExecGrader(BaseGrader):
	"""  """
	def __init__(self, grader_name):
		super(SafeExecGrader, self).__init__(grader_name)

	def grade(self, student_code, staff_code="", score=1, test=""):
		# configuramos el entorno seguro para ejecucion
		#self.log.info("si hay logggggg")
		staff_code = """
def staff_code_calcularFactorial(n):
	contador = 1
	acumulador = 1
	while contador <= n:
		acumulador *= contador
		contador += 1
	return acumulador
		"""

		post_code = """
import random
from time import time
try:
	random.seed(int(time()))

	calcularFactorial(1000)

	for i in range(20):
		param = random.randint(1, 200)
		student_result = calcularFactorial(param)
		staff_result = staff_code_calcularFactorial(param)
		
		if student_result != staff_result:
			print 'ocurrio un error al ejecutar tu codigo. El resultado es incorrecto para el parametro formal n=', param
			break
except RuntimeError as e:
	print "ocurrio un error mientras se ejecutaba el codigo (puede ser que estes utilizando recursion?)"
"""

		student_code = staff_code + student_code + post_code

		codejail.jail_code.configure("python", "/edx/venvs/codejail-sandbox/bin/python", "sandbox")
		codejail.jail_code.set_limit("CPU", 3)
		codejail.jail_code.set_limit("REALTIME", 3)
		codejail.jail_code.set_limit("VMEM", 0)
		codejail.jail_code.set_limit("FSIZE", 0)
		out = codejail.jail_code.jail_code("python", student_code, slug="debug_mode")
		# print out.status
		# print out.stderr
		# print out.stdout
		
		if out.status == 0:
			if out.stdout != "":
				msg = "<p>" + out.stdout + "</p>"
				self.set_answer(False, score, msg)
				return False
			else:
				msg = "<p>Buen trabajo!</p>"
				self.set_answer(True, score, msg)
				return True		
		elif out.status != 0 and out.stderr == "":
			msg = "<p>Se a alcanzado el <b>limite de tiempo permitido</b> para ejecucion. Revisa el codigo en busca de posibles errores.</p>"
			self.set_answer(False, 0, msg)
			return False
		elif out.status != 0 and out.stderr != "":
			#msg = "<p>Ocurrio un <b>error durante la ejecucion de tu codigo</b>. Revisa posibles errores lexicos y/o sintacticos. {0}</p>".format(out.stderr)
			msg = "<p>Ocurrio un <b>error durante la ejecucion de tu codigo</b>. Revisa posibles errores lexicos y/o sintacticos.</p>"
			self.log.error(out.stderr)
			self.set_answer(False, 0, msg)
			return False
		else:
			msg = "<p><b>Ocurrio un error inesperado</b>. Vuelve a cargar la pagina o intentalo mas tarde</p>"
			self.set_answer(False, 0, msg)
			return False

# print 'comienza la ejecucion'
# grader = SafeExecGrader("SafeExecGrader")
# code = """
# print 'comienza la ejecucion'
# #import os
# #print os.getcwd()
# #os.chdir('/home/')
# #print os.getcwd()
# while True:pass
# """

# grader.grade(code)
# answer = grader.get_answer()
# print answer
