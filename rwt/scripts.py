import sys
import tokenize


def run(cmdline):
	"""
	Execute the script as if it had been invoked naturally.
	"""
	namespace = dict()
	filename = cmdline[0]
	namespace['__file__'] = filename
	namespace['__name__'] = '__main__'
	sys.argv[:] = cmdline

	open_ = getattr(tokenize, 'open', open)
	script = open_(filename).read()
	norm_script = script.replace('\\r\\n', '\\n')
	code = compile(norm_script, filename, 'exec')
	exec(code, namespace)
