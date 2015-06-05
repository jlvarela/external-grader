import logging
import settings
import client
import time
import signal
import sys

class Manager(object):
	"""
	Manager polling connection to Xqueue
	"""
	def __init__(self):
		super(Manager, self).__init__()
		# clientes Xqueue
		self.clients = []
		# logger
		self.log = logging.getLogger(__package__)
		self.poll_time = 10
		# credenciales http
		self.basic_http_auth = None

		# Senalizacion para finalizar las hebras (averiguar mejor sobre esto!!!)
		signal.signal(signal.SIGTERM, self.stop_clients)
		
	def configure(self, settings_file_path=None):
		"""
		configure this manager for multiple clients. The configuration
		is store in config_directory.
		"""

		self.log.info("configuring grader clients")
		# Obtenemos la informacion para los clientes
		settings.settings_file_path = settings_file_path
		# Agregamos tantos clientes como haya en settings
		for queue_name, config in settings.QUEUES.items():
			self.clients.append(client.Client(queue_name, config))

	def is_configured(self):
		"""
		ask if this manager is configure for multiple clients.
		"""
		return len(self.clients) > 0

	def run_clients(self):
		"""
		Run clients
		"""
		
		self.log.info("starting clients...")
		for client in self.clients:
			client.start()

	def stop_clients(self, *args):
		self.log.info("stopping grader clients")
		while self.clients:
			client = self.clients.pop()
			client.stop()
			client.join()
		self.log.info("manager done".format(client.queue_name))	
		sys.exit(0)

	def are_clients_alive(self):
		for client in self.clients:
			if not client.is_alive():
				return False
		return True

	def watch_clients(self):
		while True:
			try:
				if not self.are_clients_alive():
					self.log.warn("there are no clients alive. shutting down the manager")
					sys.exit(1)	
				time.sleep(self.poll_time)
			except KeyboardInterrupt:
				self.log.info("shutting down the manager NOW")
				self.stop_clients()

def get_argument_parser():
	# para los parametros de entrada
	# colocar todos los parametros de entrada necesarios para la ejecucion
	# de grader engine. Version OOP de getopt ;)
	import argparse
	program = "grade_engine"
	description = "A grader engine for grade student code from edX."
	# Creamos un parser para los argumentos
	parser = argparse.ArgumentParser(prog=program, description=description)
	# Agregamos las entradas necesarias para cada argumento requerido
	# parser.add_argument("mandatory_argument")
	parser.add_argument("-o", "--optional_argument", help="help text")
	return parser

def main(args=None):
	# Obtenemos los parametros de entrada
	parser = get_argument_parser()
	args = parser.parse_args(args)
	
	# Seteamos el logger

	# log del package
	# coloco package para evitar grade_engine.grade_engine
	log = logging.getLogger(__package__)
	log.setLevel(settings.GRADER_ENGINE_LOG_LEVEL)

	formatter = logging.Formatter(settings.DEFAULT_LOG_FORMAT, 
		                          settings.DEFAULT_TIME_LOG_FORMAT)
	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(formatter)
	log.addHandler(stream_handler)

	# jail code log (si esta disponible)
	jail_log = logging.getLogger("codejail")
	jail_log.addHandler(logging.StreamHandler())
	jail_log.setLevel(logging.DEBUG)
	
	# Procesamos los parametros
	# Creamos un objeto Manager para administrar las conexiones a Xqueue
	manager = Manager()
	manager.configure()
	if manager.is_configured():
		manager.run_clients()
		manager.watch_clients()
	return 0

# Solo se ejecutara el siguiente codigo si llamo a este modulo
# python grade_engine.py
if __name__=="__main__":
	main()