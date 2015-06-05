import sys
import StringIO

# debug flag for some message in stdout
DEBUG = True

# from http://stackoverflow.com/questions/6796492/python-temporarily-redirect-stdout-stderr
class RedirectStdStreams(object):
    def __init__(self, stdout=None, stderr=None):
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

def same_output(student_code, staff_code):
	# STUDENT
	# create file-like string to capture output
	_studentcode_out = StringIO.StringIO()
	_studentcode_err = StringIO.StringIO()
	try:
		# redirect stdout, stderr
		with RedirectStdStreams(stdout=_studentcode_out, stderr=_studentcode_err):
			# execute student code in unsafe-mode
			exec student_code
	except:
		if DEBUG:
			exc_info = sys.exc_info()
			print "[%s] student code error: \n %s" % (self.grader_name, exc_info[1])
		return False, exc_info
	
	# STAFF (correct code)
	_staffcode_out = StringIO.StringIO()
	_staffcode_err = StringIO.StringIO()
	try:
		# redirect stdout, stderr
		with RedirectStdStreams(stdout=_staffcode_out, stderr=_staffcode_err):
			# execute staff code in unsafe-mode
			exec staff_code
	except:
		if DEBUG:
			exc_info = sys.exc_info()
			print "[%s] staff code error: \n %s" % (self.grader_name, exc_info[1])
		return False, exc_info	

	# ask if both outputs are equals
	if _studentcode_out.getvalue() == _staffcode_out.getvalue():
		return True, None
	else:
		return False , None