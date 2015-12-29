# -*- coding: utf-8 -*-
import threading
# requiere instalar request.py (pip - easy_install)
import requests
import logging
import urlparse
import urls
import json
import time
import grader.grader as grader
import xmltodict

result_template = {
					"xqueue_header": None, 
	                "xqueue_body": 
	                      {
	                   		"msg": "No msg",
	                   		"correct": False,	
	                   		"score": 0,
	                   		"grader_id": "No grader_id"
	                   	  }
	              }

class Client(threading.Thread):
	"""
	Cliente que se conecta a un servidor Xqueue
	"""

	def __init__(self, queue_name, settings):
		super(Client, self).__init__()
		self.queue_name = queue_name
		self.server_url = settings["SERVER_URL"]
		self.django_auth = settings["DJANGO_AUTH"]
		self.basic_auth = (settings["BASIC_AUTH"]["username"], 
			               settings["BASIC_AUTH"]["password"])
		self.request_timeout = settings["REQUEST_TIMEOUT"]
		self.parser = XqueueParser()
		self.session = None
		self.is_running = False

		self.log = logging.getLogger("{0} [{1}]".format(__name__, queue_name))

	# client methods

	def login(self):
		"""
		logeo en el servidor Xqueue. 
		"""
		try:
			# obtenemos una sesion (logeo permanente)
			self.session = requests.session()
			# construimos la url para conectarnos
			login_url = urlparse.urljoin(self.server_url, urls.XQUEUE_LOG_IN)
			
			# procedemos a logearnos
			self.log.info("trying to login to xqueue at '{0}'".format(login_url))
			response = self.session.post(login_url, auth=self.basic_auth, data=self.django_auth)		
			# error con respecto a que la url termine en "/" ???
			if response == 500 and url.endswith("/"):
				response = self.session.post(login_url[:-1], auth=self.basic_auth, data=django_auth)
			status_code, content = self.parser.parse_reply(response.content)
			if status_code != 0:
				self.log.error("xqueue status code: {0}\n {1}".format(status_code, content))
				raise ClientError(content)

		except requests.exceptions.RequestException as e:
			self.log.error("it is not possible to login xqueue at '{0}'\n {1}".format(login_url, e))
			#self.session.close()
			raise ClientError(e)
		except XqueueParserError as e:
			self.log.exception("it is not possible to parse the xqueue response content to login\n {0}".format(e))
			#self.session.close()
			raise

	def get_submission(self):
		"""
		get the next student submission from queue_name
		"""
		queue_len_url = urlparse.urljoin(self.server_url, urls.XQUEUE_GET_QUEUELEN)
		queue_submission_url = urlparse.urljoin(self.server_url, urls.XQUEUE_GET_SUBMISSION)
		
		# cuidado al agragar threads, debe ser atomico.
		status_code, queue_len = self.http_get(queue_len_url, {"queue_name": self.queue_name})
		self.log.debug("retry to get a submission...")
		if status_code != 0:
			self.log.error("xqueue status code: {0}\n {1}".format(status_code, queue_len))
			raise ClientError(queue_len)
		if queue_len > 0:
			self.log.debug("pulling a submission")
			status_code, submission = self.http_get(queue_submission_url, {"queue_name": self.queue_name})
			if status_code != 0:
				self.log.error("xqueue status code: {0}\n {1}".format(status_code, submission))
				raise ClientError(submission)
			submission = self.parser.parse_submission(submission)
			print submission
			return submission

	def grade(self, submission):
		"""
		Grade de student's submission (student code)
		"""

		self.log.debug("gradding a submission...")
		g = grader.UnsafeExecGrader("SafeExecGrader")
		payload = submission.get_grader_payload()
		student_code = submission.get_student_response()
		staff_code = payload["answer_code"]
		python_mode = payload["python_mode"]
		#g.grade(submission.get_student_response())

		# Funciones/valores a evaluar. Deben estar separados por ";" por cada uno de los valores 
		# en el campo eval_function del payload
		evaluation_functions = payload["eval_function"].split(";")
		# Evaluando código del estudiante				
		g.grade(python_mode, student_code, staff_code, evaluation_functions)
		
		answer = result_template
		answer["xqueue_header"] = submission.header
		answer["xqueue_body"] = g.get_answer()
		return answer

	def put_result(self, answer):
		"""
		post answer for a student submission in a queue_name
		"""
		queue_answer_url = urlparse.urljoin(self.server_url, urls.XQUEUE_PUT_RESULT)
		self.log.debug("delivery the grade submission to xqueue")
		request = {
					"xqueue_header": json.dumps(answer["xqueue_header"]), 
					"xqueue_body": json.dumps(answer["xqueue_body"])
				  }
		
		status_code, content = self.http_post(queue_answer_url, request, self.request_timeout)
		if status_code != 0:
			self.log.error("xqueue status code: {0}\n {1}".format(status_code, content))
			raise ClientError(content)

	def http_post(self, url, data, timeout):
		
		try:
			r = self.session.post(url, auth=self.basic_auth, data=data, timeout=timeout, verify=False)
			if r.status_code == 500 and url.endswith("/"):
				r = self.session.post(url[:-1], auth=self.basic_auth, data=data, timeout=timeout, verify=False)
		except requests.exceptions.ConnectionError as e:
			raise ClientError(e)
		except requests.exceptions.Timeout as e:
			raise ClientError(e)
		if r.status_code != 200:
			raise ClientError("Error inesperado al tratar de conectar al servidor")
		if hasattr(r, "text"):
			response = r.text
		elif hasattr(r, "content"):
			response = r.content
		else:
			raise ClientError("Error al tratar de obtener el contenido de un post")
		return self.parser.parse_reply(response)

	def http_get(self, url, data=None):
		"""
		http get to a url
		"""
		if data == None:
			data = {}

		try:
			r = self.session.get(url, auth=self.basic_auth, params=data)
			if r.status_code == 500 and url.endswith("/"):
				r = self.session.get(url[:-1], auth=self.basic_auth, params=data)
		except requests.exceptions.ConnectionError as e:
			raise ClientError(e)
		if r.status_code != 200:
			raise ClientError("Error inesperado al tratar de conectar al servidor")
		if hasattr(r, "text"):
			response = r.text
		elif hasattr(r, "content"):
			response = r.content
		else:
			raise ClientError("Error al tratar de obtener el contenido de un get")
		return self.parser.parse_reply(response)

	# thread methods

	# metodo reescrito de la hebra.
	def run(self):
		"""
		Corre por siempre el cliente hasta que ocurre un error
		"""
		self.is_running = True
		try:
			self.login()
			while self.is_running:
				submission = self.get_submission()
				if submission:
					answer = self.grade(submission)
					self.put_result(answer)
				time.sleep(1)
		except ClientError as e:
			# hacer algo util
			#print "error!"
			#print e.msg
			self.stop()
		finally:
			pass
			#print "fin!"
	
	def stop(self):
		"""
		Finaliza la ejecucion de la hebra actual
		"""
		# revisar esto, ya que cerramos sesion mientras se procesa una solicitud.
		self.log.info("stopping...")
		self.session.close()
		self.is_running = False

class XqueueParser(object):
	"""
	docstring for XqueueParser
	"""
	def __init__(self):
		super(XqueueParser, self).__init__()
	
	# { 'return_code': 0 (success), 1 (fail)
	# 'content': Message from xqueue (string)
	def parse_reply(self, response):
		try:
			response = json.loads(response)
		except ValueError as e:
			raise XqueueParserError(e.message)
			
		if not response.has_key("return_code") or not response.has_key("content"):
			raise XqueueParserError("respuesta no tiene return_code y/o content")
			
			#response["return_code"] = "vaca"
		elif not response["return_code"] in [True, False]:
			raise XqueueParserError("return_code no tiene un valor valido")
			

		return response["return_code"], response["content"]

	def parse_submission(self, response):
		try:
		    response = json.loads(response)
		    
		    header = json.loads(response['xqueue_header'])
		    # header.update({'queue_name': queue_name})
		    body = json.loads(response['xqueue_body'])
		    files = json.loads(response['xqueue_files'])
		    
		    #student_info = json.loads(body['student_info'])
		    #body.update({'student_info': student_info})
		    
		    submission = Submission(header, files, body)
		except ValueError:
			raise XqueueParserError("Unexpected reply from server")
		
		return submission

class Submission(object):
	"""docstring for Submission"""
	def __init__(self, xqueue_header, xqueue_files, xqueue_body):
		super(Submission, self).__init__()
		self.header = xqueue_header
		self.files = xqueue_files
		self.body = xqueue_body		

	def get_student_response(self):
		if not self.body.has_key("student_response"):
			raise SubmissionError("Submission no contiene el campo student_response")
		return self.body["student_response"]

	def get_grader_payload(self):
		if not self.body.has_key("grader_payload"):
			raise SubmissionError("Submission no contiene el campo grader_payload")
		try:
			grader_payload = json.loads(self.body["grader_payload"])
		except ValueError as e:
			raise SubmissionError(e.message)
		return grader_payload

class ClientError(Exception):
	def __init__(self, msg):
		super(ClientError, self).__init__()
		self.msg = msg

	def __str__(self):
		return self.msg

class XqueueParserError(ClientError):
	def __init__(self, msg):
		super(XqueueParserError, self).__init__(msg)

class SubmissionError(ClientError):
	def __init__(self, msg):
		super(SubmissionError, self).__init__(msg)
		
class PayloadParser:
	# Delimitador for parsing payload code
	delimiter = "$_delimiter"
	
	# Constructor
	def __init__(self, payload):
		self.payload = payload

	# Setting payload into self
	def set_payload(self, payload):
		self.payload = payload

	# Getting payload from self
	def get_payload(self):
		return self.payload
	
	# Parsing payload JSON code from self content
	def parse_payload(self):
		fields = json.loads(self.payload)
		print "Payload tiene el campo answer_code: ",fields.has_key("answer_code")