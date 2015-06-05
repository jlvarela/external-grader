# https://docs.python.org/2/library/signal.html#signal.alarm
import signal, os

class SimpleTimer(object):
	"""
	   Timer permite definir una ventana de tiempo. Al finalizar esta
	   tiempo se genera una excepcion
	"""
	def __init__(self, interval):
		super(SimpleTimer, self).__init__()
		# El tipo de 
		signal.signal(signal.SIGALRM, self.handler)
		self.interval = interval

	# No tengo muy claro que es signum
	def handler(self, signum, interval):
		#print "signal handler called with signal ", signum
		raise TimeOut(self.interval)

	def start(self):
		signal.alarm(self.interval)

	def cancel(self):
		signal.alarm(0)

class TimeOut(Exception):
	""" ------ """
	def __init__(self, interval):
		self.interval = interval

	def __str__(self):
		return "reach the time limit ({:d}s)".format(self.interval)

"""
t = SimpleTimer(1)
t.start()
while(True):pass
t.cancel()
"""

"""
from threading import Timer as threading_timer

class SimpleTimer(object):
	
	   #Timer permite definir una ventana de tiempo. Al finalizar esta
	   #tiempo se genera una excepcion
	
	def __init__(self, interval):
		super(SimpleTimer, self).__init__()
		self.timer = threading_timer(interval, self.event)
		self.interval = interval

	def event(self):
		raise TimeOut(self.interval)

	def start(self):
		self.timer.start()

	def cancel(self):
		self.timer.cancel()

class TimeOut(Exception):
	
	def __init__(self, interval):
		self.interval = interval

	def __str__(self):
		return "reach the time limit ({:.2f}s)".format(self.interval)
"""